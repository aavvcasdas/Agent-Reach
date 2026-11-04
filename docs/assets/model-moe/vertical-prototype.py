"""Minimal, self-contained 9:16 (1080x1920) deterministic video renderer.

No Chromium, no video-generation model: Pillow draws every frame, ffmpeg encodes.
Used as the feasibility prototype referenced by docs/model-moe.md.

    pip install pillow imageio-ffmpeg
    python vertical-prototype.py --out out_demo.mp4

Properties that matter for this genre:
  * every frame is a pure function of `t` (deterministic; same input -> same file)
  * character + cards + typing text + disclaimer mark, all drawn from data
  * ~30x realtime on a laptop CPU (236 frames in ~6.5 s in the sandbox)

The character below is a plain placeholder drawn from shapes, NOT anyone's artwork.
Swap `draw_chibi()` for your own transparent PNG (the sprite chain in
`PC2005-cloud/dsh-pet` produces exactly that: normalised, transparent, feet on a
fixed floor line) and nothing else in this file has to change.
"""
from __future__ import annotations

import argparse
import math
import subprocess
import time
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1080, 1920, 30
INK = (243, 248, 255)
DIM = (176, 199, 226)
ACCENT = (255, 138, 92)
AQUA = (98, 227, 207)
BG_TOP, BG_BOT = (8, 22, 40), (11, 38, 62)
HAIR, HAIR_DARK, SKIN, DRESS = (92, 122, 214), (58, 82, 160), (252, 226, 210), (196, 214, 246)


def ease(x: float) -> float:
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def find_font() -> Path | None:
    """Any CJK font works; pass --font to point at your own."""
    for p in (
        Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
        Path("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"),
        Path("/System/Library/Fonts/PingFang.ttc"),
        Path("C:/Windows/Fonts/msyh.ttc"),
    ):
        if p.exists():
            return p
    return None


def build_bg() -> Image.Image:
    img = Image.new("RGB", (W, H), BG_BOT)
    d = ImageDraw.Draw(img, "RGBA")
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(lerp(BG_TOP[i], BG_BOT[i], t)) for i in range(3)))
    # porthole with a few fish
    cx, cy, r = 812, 430, 190
    d.ellipse([cx - r - 26, cy - r - 26, cx + r + 26, cy + r + 26], fill=(24, 54, 82, 255))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(36, 92, 128, 255))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(120, 190, 225, 180), width=6)
    for fx, fy, fs, col in ((cx - 70, cy - 40, 26, (168, 232, 240)), (cx + 40, cy + 30, 18, (208, 240, 235)),
                            (cx - 10, cy + 80, 14, (150, 216, 232))):
        d.ellipse([fx - fs, fy - fs * 0.62, fx + fs, fy + fs * 0.62], fill=col + (205,))
        d.polygon([(fx + fs, fy), (fx + fs * 1.6, fy - fs * 0.4), (fx + fs * 1.6, fy + fs * 0.4)], fill=col + (205,))
    for bx, by, br in ((150, 300, 9), (196, 232, 6), (118, 210, 4), (250, 356, 5)):
        d.ellipse([bx - br, by - br, bx + br, by + br], outline=(160, 226, 244, 140), width=2)
    # shelf + books
    d.rectangle([700, 760, 1050, 778], fill=(58, 44, 62, 255))
    d.rectangle([700, 778, 1050, 792], fill=(40, 30, 44, 255))
    for bx, bh, col in ((730, 96, (188, 84, 84)), (782, 78, (86, 150, 168)), (828, 104, (214, 168, 92))):
        d.rectangle([bx, 778 - bh, bx + 40, 776], fill=col)
    # desk + mat
    d.rectangle([0, 1392, W, 1440], fill=(74, 52, 44, 255))
    d.rectangle([0, 1440, W, H], fill=(44, 30, 28, 255))
    d.line([(0, 1392), (W, 1392)], fill=(132, 96, 76, 255), width=4)
    d.ellipse([120, 1596, 960, 1760], fill=(18, 58, 78, 255))
    d.ellipse([160, 1620, 920, 1740], fill=(26, 76, 100, 255))
    # vignette
    vg = Image.new("L", (W, H), 0)
    ImageDraw.Draw(vg).ellipse([-260, -180, W + 260, H + 260], fill=255)
    vg = vg.filter(ImageFilter.GaussianBlur(160))
    return Image.composite(img, Image.new("RGB", (W, H), (2, 8, 16)), vg)


def draw_chibi(size: int = 760, mouth_open: bool = False) -> Image.Image:
    """Placeholder whale-girl chibi. Replace with your own transparent PNG."""
    s = 4  # supersample, then downscale for smooth edges
    im = Image.new("RGBA", (size * s, size * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im, "RGBA")
    S = size * s
    u = S / 100.0

    def r(x, y, w, h, fill, **kw):
        kw.setdefault("radius", int(min(w, h) * 0.45))
        d.rounded_rectangle([x * u, y * u, (x + w) * u, (y + h) * u], fill=fill, **kw)

    # tail
    d.polygon([(66 * u, 78 * u), (96 * u, 62 * u), (92 * u, 84 * u), (97 * u, 92 * u), (66 * u, 88 * u)],
              fill=HAIR_DARK)
    # legs
    r(38, 80, 11, 18, SKIN)
    r(52, 80, 11, 18, SKIN)
    r(34, 95, 18, 5, (250, 250, 255))
    r(50, 95, 18, 5, (250, 250, 255))
    # dress
    r(28, 52, 45, 32, DRESS)
    d.polygon([(28 * u, 80 * u), (73 * u, 80 * u), (70 * u, 86 * u), (31 * u, 86 * u)], fill=(176, 198, 238))
    # hair back
    d.ellipse([20 * u, 14 * u, 80 * u, 66 * u], fill=HAIR_DARK)
    # head
    d.ellipse([28 * u, 18 * u, 72 * u, 58 * u], fill=SKIN)
    # fringe
    d.pieslice([27 * u, 14 * u, 73 * u, 52 * u], 180, 360, fill=HAIR)
    # fin ears
    d.polygon([(22 * u, 26 * u), (8 * u, 16 * u), (16 * u, 36 * u)], fill=HAIR)
    d.polygon([(78 * u, 26 * u), (92 * u, 16 * u), (84 * u, 36 * u)], fill=HAIR)
    # eyes
    for ex in (40, 60):
        d.ellipse([(ex - 5) * u, 36 * u, (ex + 5) * u, 46 * u], fill=(28, 40, 78))
        d.ellipse([(ex - 4) * u, 37 * u, (ex + 1) * u, 42 * u], fill=(255, 255, 255))
    # blush + mouth
    d.ellipse([32 * u, 46 * u, 38 * u, 50 * u], fill=(246, 168, 168, 190))
    d.ellipse([62 * u, 46 * u, 68 * u, 50 * u], fill=(246, 168, 168, 190))
    if mouth_open:
        d.ellipse([47 * u, 48 * u, 53 * u, 55 * u], fill=(150, 60, 70))
    else:
        d.arc([46 * u, 47 * u, 54 * u, 54 * u], 20, 160, fill=(150, 60, 70), width=int(2.4 * u))
    return im.resize((size, size), Image.LANCZOS)


def tint_panel(size, col=(14, 38, 62), alpha=228, radius=34):
    p = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(p)
    d.rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], radius=radius, fill=col + (alpha,),
                        outline=(96, 156, 198, 200), width=3)
    return p


def render(out: Path, font_path: Path | None) -> None:
    t0 = time.time()
    bg = build_bg()
    sprite_idle = draw_chibi()
    sprite_talk = draw_chibi(mouth_open=True)
    f_title = ImageFont.truetype(str(font_path), 76) if font_path else ImageFont.load_default()
    f_line = ImageFont.truetype(str(font_path), 62) if font_path else ImageFont.load_default()
    f_small = ImageFont.truetype(str(font_path), 44) if font_path else ImageFont.load_default()
    f_chip = ImageFont.truetype(str(font_path), 38) if font_path else ImageFont.load_default()

    lines = ["本鲸只在自己评论区吃饭。", "不刷屏，不串门。", "今晚的米缸，还是空的。"]
    intro, per_line = 1.4, 1.9
    total = intro + per_line * len(lines) + 0.8
    n_frames = int(total * FPS)

    import imageio_ffmpeg  # ships a static ffmpeg binary

    cmd = [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-an",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-pix_fmt", "yuv420p", str(out)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    panel = tint_panel((940, 300))
    nameplate = tint_panel((320, 74), col=(10, 28, 48), alpha=210, radius=22)

    for i in range(n_frames):
        t = i / FPS
        frame = bg.convert("RGBA")
        d = ImageDraw.Draw(frame, "RGBA")

        chip_t = ease(t / 0.5)
        d.rounded_rectangle([56, 60, 56 + 300 * chip_t, 130], radius=18, fill=ACCENT + (int(235 * chip_t),))
        if font_path:
            d.text((80, 74), "鲸鱼娘在营业", font=f_chip, fill=(20, 30, 44))

        title = "本鲸只回自己家的评论"
        if font_path:
            d.text((56, 190), title[: int(len(title) * ease((t - 0.2) / 0.9))], font=f_title, fill=INK)

        drop = ease(t / 0.7)
        bob = int(math.sin(t * 3.1) * 8)
        talking = t > intro
        hop = int(abs(math.sin(t * 11)) * 10) if talking and int(t * 11) % 2 == 0 else 0
        spr = sprite_talk if talking else sprite_idle
        px = 130
        py = 1440 - spr.height + int(lerp(-260, 0, drop)) + bob - hop
        d.ellipse([px + 40, 1768, px + spr.width - 40, 1800], fill=(4, 18, 30, 150))
        frame.alpha_composite(spr, (px, py))

        frame.alpha_composite(nameplate, (px - 10, py - 96))
        if font_path:
            d.text((px + 14, py - 80), "本鲸 · 深海住户", font=f_chip, fill=AQUA)

        slide = ease((t - 0.5) / 0.6)
        cy = int(lerp(1700, 1360, slide))
        frame.alpha_composite(panel, (66, cy))
        idx = min(len(lines) - 1, max(0, int((t - intro) / per_line)))
        lt = ((t - intro) - idx * per_line) / per_line if t > intro else 0.0
        shown = int(len(lines[idx]) * ease(lt * 1.7))
        if font_path:
            for k in range(idx + 1):
                txt = lines[k] if k < idx else lines[idx][:shown]
                d.text((104, cy + 34 + k * 84), txt, font=f_line, fill=DIM if k < idx else INK)
            d.text((70, 1832), "非官方同人 · AI生成 · 剧情演绎", font=f_small, fill=(150, 176, 204))

        proc.stdin.write(frame.convert("RGB").tobytes())

    proc.stdin.close()
    proc.wait()
    print(f"{n_frames} frames, {total:.1f}s of video, rendered in {time.time() - t0:.1f}s -> {out}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="out_demo.mp4", type=Path)
    ap.add_argument("--font", default=None, help="path to a CJK .ttf/.ttc (Noto Sans SC, PingFang, MSYH…)")
    a = ap.parse_args()
    font = Path(a.font) if a.font else find_font()
    if not font:
        print("warning: no CJK font found, text will be blank; pass --font")
    render(a.out, font)


if __name__ == "__main__":
    main()
