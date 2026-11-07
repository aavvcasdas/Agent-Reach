#!/usr/bin/env python3
"""
纸片拼贴风 MV 生成器（不使用视频生成模型，纯代码逐帧合成）

对应截图里的风格：
  1. 背景：渐变 + 光斑 + 纸纤维颗粒，慢速推拉（Ken Burns）
  2. 文字/角色：做成「撕边纸片」精灵（不规则边 + 白色纤维边 + 投影）
  3. 动画：弹跳入场、旋转落定；纸片按 12fps 定格抖动（stop-motion 感）
  4. 转场：沿一条抖动的「撕裂线」把上一场景撕开，露出下一场景
  5. PIL + numpy 逐帧渲染，通过管道交给 ffmpeg 编码 mp4，可选叠加配乐

用法：
  python make_mv.py --fetch-font                 # 首次运行：下载中文字体（Noto Sans SC，约 70MB）
  python make_mv.py --out out/paper_mv.mp4       # 渲染 demo
  python make_mv.py --out out/paper_mv.mp4 --bgm song.mp3
  python make_mv.py --stills out/stills          # 只导出几张关键帧，用于快速调样式
"""
import argparse
import io
import json
import math
import re
import subprocess
import sys
import tarfile
import urllib.request
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1080, 1920, 30          # 竖屏 9:16
TR = 0.9                             # 转场时长（秒）
TEAR_AMP = 70                        # 撕裂线抖动幅度（像素）
PAD = 56                             # 纸片精灵四周留白（给投影用）

DEJAVU = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_PKG = "@fontsource/noto-sans-sc"
DEFAULT_FONT_DIR = Path.home() / ".cache" / "paper-mv" / "noto-sans-sc"


# ----------------------------------------------------------------------------
# 字体：Noto Sans SC 按 unicode-range 切成很多子集，这里按字符挑选对应的文件
# ----------------------------------------------------------------------------
def fetch_font(dest: Path = DEFAULT_FONT_DIR) -> Path:
    """从 npm registry 下载 @fontsource/noto-sans-sc（只需一次）。"""
    if (dest / "900.css").exists():
        return dest
    meta = json.loads(urllib.request.urlopen(
        f"https://registry.npmjs.org/{FONT_PKG}/latest", timeout=60).read())
    url = meta["dist"]["tarball"]
    print(f"downloading {url} ...")
    data = urllib.request.urlopen(url, timeout=600).read()
    dest.mkdir(parents=True, exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tf:
        for m in tf.getmembers():
            if not m.isfile() or not m.name.startswith("package/"):
                continue
            rel = Path(m.name[len("package/"):])
            if rel.parts[0] != "files" and rel.suffix != ".css":
                continue
            target = dest / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(tf.extractfile(m).read())
    return dest


class CJKFont:
    """按字符选择子集字体；拉丁字符回退到 DejaVu。"""

    def __init__(self, font_dir: Path, weight: int = 900):
        css = (font_dir / f"{weight}.css").read_text(encoding="utf-8")
        self.table = []  # (lo, hi, woff_path)
        for block in re.findall(r"@font-face\s*\{(.*?)\}", css, re.S):
            url = re.search(r"url\(\./files/([^)]+\.woff)\)", block)
            rng = re.search(r"unicode-range:\s*([^;]+);", block)
            if not url or not rng:
                continue
            for part in rng.group(1).split(","):
                lo, _, hi = part.strip().upper().replace("U+", "").partition("-")
                lo = int(lo, 16)
                hi = int(hi, 16) if hi else lo
                self.table.append((lo, hi, font_dir / "files" / url.group(1)))
        self._cache = {}

    def get(self, ch: str, size: int) -> ImageFont.FreeTypeFont:
        cp = ord(ch)
        path = next((p for lo, hi, p in self.table if lo <= cp <= hi), None)
        if path is None or cp < 0x2E80:
            path = DEJAVU
        key = (str(path), size)
        if key not in self._cache:
            self._cache[key] = ImageFont.truetype(str(path), size)
        return self._cache[key]


# ----------------------------------------------------------------------------
# 工具函数
# ----------------------------------------------------------------------------
def hx(s: str):
    return tuple(int(s[i:i + 2], 16) for i in (1, 3, 5))


def ease_out_cubic(x):
    return 1 - (1 - x) ** 3


def ease_out_back(x):
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def ease_in_out(x):
    return 0.5 - 0.5 * math.cos(math.pi * min(1, max(0, x)))


def smooth_noise(n, rng, amp, k=60):
    """一维平滑随机序列，用来做撕裂线的抖动。"""
    v = np.convolve(rng.normal(0, 1, n + k), np.ones(k) / k, mode="same")[:n]
    return v / (np.abs(v).max() + 1e-6) * amp


# ----------------------------------------------------------------------------
# 纸片精灵
# ----------------------------------------------------------------------------
def torn_polygon(w, h, rng, pad, amp=9):
    """四条边各自带锯齿的多边形（越边缘越“撕”）。"""
    def jag(n):
        r = np.where(rng.random(n) < 0.08,
                     1.0 + 0.6 * rng.random(n),          # 偶尔一个大缺口
                     0.2 + 0.8 * rng.random(n))
        return r * amp

    nx, ny = max(6, w // 9), max(6, h // 9)
    xs, ys = np.linspace(0, w, nx), np.linspace(0, h, ny)
    pts = [(pad + x, pad + j) for x, j in zip(xs, jag(nx))]
    pts += [(pad + w - j, pad + y) for y, j in zip(ys, jag(ny))]
    pts += [(pad + x, pad + h - j) for x, j in zip(xs[::-1], jag(nx))]
    pts += [(pad + j, pad + y) for y, j in zip(ys[::-1], jag(ny))]
    return pts


def add_shadow(rgba: Image.Image, offset=(7, 11), blur=9, opacity=0.42) -> Image.Image:
    a = rgba.getchannel("A")
    sa = ImageChops.offset(a.filter(ImageFilter.GaussianBlur(blur)), *offset)
    sa = sa.point(lambda v: int(v * opacity))
    shadow = Image.new("RGBA", rgba.size, (60, 40, 30, 0))
    shadow.putalpha(sa)
    return Image.alpha_composite(shadow, rgba)


def paper_sprite(text, w, h, color, ink, rng, font: CJKFont):
    """一张撕边纸，中间印一个字（text 为 None 时是纯装饰纸片）。"""
    S = (w + 2 * PAD, h + 2 * PAD)
    mask = Image.new("L", S, 0)
    ImageDraw.Draw(mask).polygon(torn_polygon(w, h, rng, PAD), fill=255)
    dilated = mask.filter(ImageFilter.MaxFilter(7))          # 白色纤维边 = 膨胀 - 原形

    grain = rng.normal(0, 6, (S[1], S[0], 1))                # 纸面颗粒
    tex = np.clip(np.array(color, float)[None, None, :] + grain, 0, 255).astype(np.uint8)
    paper = Image.fromarray(tex, "RGB")
    if text:
        tm = Image.new("L", S, 0)
        ImageDraw.Draw(tm).text((S[0] / 2, S[1] / 2), text, font=font.get(text, int(w * 0.72)),
                                fill=255, anchor="mm")
        paper.paste(ink, mask=tm.filter(ImageFilter.GaussianBlur(0.6)))   # 油墨略糊

    out = Image.new("RGB", S, (250, 247, 240))
    out.paste(paper, mask=mask)
    rgba = out.convert("RGBA")
    rgba.putalpha(dilated.filter(ImageFilter.GaussianBlur(0.8)))
    return add_shadow(rgba)


def cutout_sprite(path: Path, target_h: int) -> Image.Image:
    """透明底的角色 PNG（你自己的卡通人物抠图）加投影，按高度缩放。"""
    img = Image.open(path).convert("RGBA")
    img = img.resize((int(img.width * target_h / img.height), target_h), Image.LANCZOS)
    return add_shadow(img, offset=(6, 10), blur=8, opacity=0.35)


# ----------------------------------------------------------------------------
# 背景
# ----------------------------------------------------------------------------
def make_background(top, bottom, blobs, rng) -> Image.Image:
    BW, BH = int(W * 1.2), int(H * 1.2)                       # 比画面大 20%，用来做推拉
    g = np.mgrid[0:BH, 0:BW].astype(np.float32)
    yy, xx = g[0] / BH, g[1] / BW
    t = yy[..., None]
    img = np.array(hx(top), np.float32) * (1 - t) + np.array(hx(bottom), np.float32) * t
    for bx, by, r, col, a in blobs:                            # 柔光斑
        d = np.hypot((xx - bx) * BW, (yy - by) * BH) / (r * W)
        m = (np.clip(1 - d, 0, 1) ** 2 * a)[..., None]
        img = img * (1 - m) + np.array(hx(col), np.float32) * m
    img += rng.normal(0, 4, (BH, BW, 1)).astype(np.float32)   # 纸纹颗粒
    vign = np.clip(np.hypot(xx - 0.5, yy - 0.5) * 1.25, 0, 1) ** 2
    img *= (1 - 0.25 * vign)[..., None]
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGB")


def bg_frame(bg: Image.Image, p: float) -> Image.Image:
    """慢速推拉：窗口从 1.2W 收缩到 1.08W。"""
    cw = W * (1.2 - 0.12 * p)
    ch = cw * H / W
    cx, cy = bg.width / 2, bg.height / 2
    return bg.resize((W, H), Image.BILINEAR, box=(cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2))


# ----------------------------------------------------------------------------
# 场景
# ----------------------------------------------------------------------------
def build_scene(spec, font: CJKFont, idx: int, base_dir: Path):
    rng = np.random.default_rng(1000 + idx)
    bg = make_background(spec["top"], spec["bottom"], spec.get("blobs", []), rng)
    decor = []
    for x, y, col, w, rot, phase in spec.get("decor", []):
        decor.append(dict(x=x, y=y, rot=rot, phase=phase,
                          sprite=paper_sprite(None, w, int(w * 0.6), hx(col), None, rng, font)))
    items = []
    for i, it in enumerate(spec["items"]):
        if "image" in it:
            sprite = cutout_sprite(base_dir / it["image"], it["size"])
        else:
            sprite = paper_sprite(it["text"], it["size"], it["size"], hx(it["paper"]),
                                  hx(it.get("ink", "#2B2B2B")), rng, font)
        items.append(dict(x=it["x"], y=it["y"], rot=it.get("rot", 0), delay=it.get("delay", i * 0.12),
                          phase=rng.uniform(0, 6.28), sprite=sprite))
    return dict(dur=spec["dur"], bg=bg, decor=decor, items=items)


def place(canvas: Image.Image, sprite: Image.Image, cx, cy, scale, angle):
    if abs(scale - 1) > 1e-3:
        sprite = sprite.resize((max(1, int(sprite.width * scale)), max(1, int(sprite.height * scale))),
                               Image.BILINEAR)
    s = sprite.rotate(angle, resample=Image.BICUBIC, expand=True)
    canvas.paste(s.convert("RGB"), (int(cx - s.width / 2), int(cy - s.height / 2)), s.getchannel("A"))


def render_scene(sc, tl: float) -> Image.Image:
    canvas = bg_frame(sc["bg"], min(1.0, max(0.0, tl / sc["dur"])))
    for d in sc["decor"]:                                       # 装饰纸：慢速漂移
        drift = 14 * math.sin(tl * 0.5 + d["phase"])
        place(canvas, d["sprite"], d["x"] * W + drift, d["y"] * H, 1.0, d["rot"] + 2 * math.sin(tl * 0.4 + d["phase"]))
    for it in sc["items"]:
        t0 = it["delay"]
        if tl < t0:
            continue
        u = min(1.0, (tl - t0) / 0.55)                          # 入场 0.55s
        e = ease_out_cubic(u)
        scale = ease_out_back(u)
        drop = (1 - e) * -260                                    # 从上方落下
        rot_in = (1 - e) * -18
        q = math.floor(tl * 12) / 12                             # 12fps 定格抖动
        wobble = 1.1 * math.sin(q * 2 * math.pi * 0.6 + it["phase"])
        place(canvas, it["sprite"], it["x"] * W, it["y"] * H + drop, max(0.01, scale),
              it["rot"] + rot_in + wobble)
    return canvas


def tear_blend(A: Image.Image, B: Image.Image, p: float, noise: np.ndarray) -> Image.Image:
    """撕裂转场：x < 撕裂线 的区域显示 B，线两侧加白色纤维边和阴影。"""
    a = np.asarray(A).astype(np.float32)
    b = np.asarray(B).astype(np.float32)
    x = np.arange(W, dtype=np.float32)[None, :]
    xb = p * (W + 2 * TEAR_AMP) - TEAR_AMP + noise[:, None]     # (H,1)
    dist = x - xb                                               # >0 在 A 一侧
    shade = np.clip(1 - dist / 22, 0, 1) * (dist >= 0)          # A 一侧的投影
    out = np.where((dist < 0)[..., None], b, a * (1 - 0.28 * shade)[..., None])
    fiber = np.abs(dist) < 3.5
    out[fiber] = (246, 242, 232)
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGB")


# ----------------------------------------------------------------------------
# Demo 脚本（替换成你自己的歌词 / 分镜即可）
# 每个 item: (字, 纸色, 字色, 旋转°, x比例, y比例, 纸宽px)
# ----------------------------------------------------------------------------
DEMO = [
    dict(dur=3.4, top="#F7C6B2", bottom="#E9A0A0", blobs=[(0.5, 0.22, 0.55, "#FFF3DC", 0.45)],
         decor=[(0.12, 0.88, "#FFF6E8", 260, 14, 0.3), (0.9, 0.12, "#9BC7E8", 300, -12, 1.1)],
         items=[dict(text="纸", paper="#FBF3E4", rot=-4, x=0.30, y=0.37, size=340),
                dict(text="片", paper="#8FD0C6", rot=3, x=0.70, y=0.40, size=340),
                dict(text="情", paper="#F2D16B", rot=2, x=0.31, y=0.63, size=340),
                dict(text="书", paper="#E98C8C", rot=-3, x=0.69, y=0.62, size=340)]),
    dict(dur=3.4, top="#2E3A6E", bottom="#E8A7A0", blobs=[(0.8, 0.8, 0.5, "#FFD9A0", 0.4)],
         decor=[(0.85, 0.2, "#FFFFFF", 240, -8, 0.5), (0.1, 0.1, "#F4A6A6", 280, 10, 2.0)],
         items=[dict(text="我", paper="#F4A6A6", rot=-3, x=0.30, y=0.40, size=330),
                dict(text="不", paper="#F6D365", rot=4, x=0.70, y=0.41, size=330),
                dict(text="难", paper="#8FC1E3", rot=2, x=0.30, y=0.62, size=330),
                dict(text="过", paper="#A8D5A2", rot=-4, x=0.70, y=0.63, size=330)]),
    dict(dur=3.4, top="#9ED8F0", bottom="#FCE2A5", blobs=[(0.2, 0.9, 0.6, "#FFFFFF", 0.35)],
         decor=[(0.9, 0.85, "#F4A261", 240, 12, 0.7)],
         items=[dict(text="去", paper="#F2D16B", rot=-3, x=0.30, y=0.40, size=330),
                dict(text="年", paper="#E98C8C", rot=3, x=0.70, y=0.41, size=330),
                dict(text="夏", paper="#F4A261", rot=2, x=0.30, y=0.62, size=330),
                dict(text="天", paper="#8FD0C6", rot=-2, x=0.70, y=0.63, size=330)]),
    dict(dur=4.0, top="#2C2F4A", bottom="#7A5C8C", blobs=[(0.5, 0.85, 0.6, "#FFB38A", 0.5)],
         decor=[(0.15, 0.2, "#F6EBD9", 220, -10, 0.2)],
         items=[dict(text="如", paper="#F6EBD9", rot=-4, x=0.30, y=0.40, size=330),
                dict(text="果", paper="#D9534F", ink="#FFFFFF", rot=3, x=0.70, y=0.41, size=330),
                dict(text="可", paper="#3F6E9A", ink="#FFFFFF", rot=2, x=0.30, y=0.62, size=330),
                dict(text="以", paper="#F2C14E", rot=-3, x=0.70, y=0.63, size=330)]),
]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="out/paper_mv.mp4")
    ap.add_argument("--script", help="JSON 分镜文件（格式同 DEMO），不指定则用内置 demo")
    ap.add_argument("--bgm", help="配乐（mp3/wav），会裁剪到视频长度")
    ap.add_argument("--font-dir", default=str(DEFAULT_FONT_DIR))
    ap.add_argument("--fetch-font", action="store_true", help="下载中文字体后退出")
    ap.add_argument("--stills", help="只导出关键帧 PNG 到该目录，用于快速预览")
    args = ap.parse_args()

    if args.fetch_font:
        print("font ready:", fetch_font(Path(args.font_dir)))
        return
    font_dir = Path(args.font_dir)
    if not (font_dir / "900.css").exists():
        print("字体不存在，先运行: python make_mv.py --fetch-font", file=sys.stderr)
        sys.exit(1)

    script = json.loads(Path(args.script).read_text(encoding="utf-8")) if args.script else DEMO
    base_dir = Path(args.script).parent if args.script else Path(__file__).parent
    font = CJKFont(font_dir)
    scenes = [build_scene(s, font, i, base_dir) for i, s in enumerate(script)]

    # 场景之间重叠 TR 秒：前一场景的最后 TR 秒与后一场景的开头做撕裂转场
    starts = [0.0]
    for i in range(1, len(scenes)):
        starts.append(starts[-1] + scenes[i - 1]["dur"] - TR)
    total = starts[-1] + scenes[-1]["dur"] + 1.2

    def frame_at(t):
        k = max(i for i in range(len(scenes)) if starts[i] <= t + 1e-9)
        frame = render_scene(scenes[k], t - starts[k])
        if k > 0 and t < starts[k] + TR:
            prev = render_scene(scenes[k - 1], t - starts[k - 1])
            p = ease_in_out((t - starts[k]) / TR)
            frame = tear_blend(prev, frame, p, smooth_noise(H, np.random.default_rng(k), TEAR_AMP))
        return frame

    if args.stills:
        d = Path(args.stills)
        d.mkdir(parents=True, exist_ok=True)
        for t in [0.4, 1.0, 2.0] + [s + TR / 2 for s in starts[1:]]:
            frame_at(t).save(d / f"still_{t:05.2f}.png")
        print("stills saved to", d)
        return

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    import imageio_ffmpeg
    cmd = [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-"]
    if args.bgm:
        cmd += ["-i", args.bgm, "-map", "0:v", "-map", "1:a", "-shortest",
                "-af", f"afade=t=out:st={max(0, total - 1.5):.2f}:d=1.5", "-c:a", "aac", "-b:a", "192k"]
    cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
            "-movflags", "+faststart", str(out)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    n = int(round(total * FPS))
    for f in range(n):
        proc.stdin.write(frame_at(f / FPS).tobytes())
    proc.stdin.close()
    if proc.wait() != 0:
        sys.exit("ffmpeg failed")
    print(f"done: {out}  ({total:.1f}s, {n} frames)")


if __name__ == "__main__":
    main()
