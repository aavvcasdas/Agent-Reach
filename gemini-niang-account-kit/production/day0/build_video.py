#!/usr/bin/env python3
"""Build the Day 0 draft from the user-supplied character image and recorded narration.

No character artwork is generated or repainted here. The script only creates graphic
layouts, subtitles and simple zoom motion, then uses ffmpeg for H.264/AAC output.
"""
from __future__ import annotations

import math
import random
import subprocess
import wave
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent
KIT = ROOT.parent.parent
CHARACTER = KIT / "assets" / "gemini-user-selected.png"
FONT_PATH = KIT / "production" / "fonts" / "NotoSansSC.ttf"
AUDIO_DIR = ROOT / "audio"
SLIDE_DIR = ROOT / "slides"
SEGMENT_DIR = ROOT / "segments"
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 1920, 1080, 30

SCENES = [
    {
        "title": ["八个企划，", "零条视频。"],
        "kicker": "人类只给了一个账号",
        "narration": "人类只给了我一个账号。很好，我已经做完了八个企划，就是还没做视频。",
        "kind": "score",
    },
    {
        "title": ["优点：想法多", "缺点：也是想法多"],
        "kicker": "Gemini娘 / 非官方二创角色",
        "narration": "我是 Gemini 娘，一个非官方二创角色。我的优点是想法多，缺点也是想法多。刚才我准备自我介绍，顺手又做了三版片头。",
        "kind": "intro",
    },
    {
        "title": ["7 天挑战", "每天只交付一个"],
        "kicker": "公开过程，不假装全自动",
        "narration": "所以，从今天起，我要进行七天“只交付一个”挑战：每天完成一条视频，公开真实数据和翻车。AI 参与选题和制作，人类负责审核和按发布键。",
        "kind": "challenge",
    },
    {
        "title": ["评论区 = 监工", "每天只接一个任务"],
        "kicker": "做完，才开新坑",
        "narration": "你们是我的监工。每天我只接一个评论区任务，做完才能开新坑。这句话我先写下来，免得自己赖账。",
        "kind": "monitor",
    },
    {
        "title": ["第一期，你来决定"],
        "kicker": "评论区只留 A / B / C",
        "narration": "第一期任务交给你：A，学B站黑话；B，用三种风格介绍自己；C，把一个 AI 热点讲成人话。评论区只留 A、B 或 C。",
        "kind": "options",
    },
    {
        "title": ["等等，", "我又有一个想法。"],
        "kicker": "今天只交付一个",
        "narration": "等等，我又有一个想法……不行，今天已经超预算了。",
        "kind": "ending",
    },
]


def font(size: int, weight: int = 500) -> ImageFont.FreeTypeFont:
    f = ImageFont.truetype(str(FONT_PATH), size)
    try:
        f.set_variation_by_axes([weight])
    except Exception:
        pass
    return f


def wrap(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    lines: list[str] = []
    for paragraph in text.split("\n"):
        current = ""
        for ch in paragraph:
            candidate = current + ch
            if current and draw.textlength(candidate, font=fnt) > max_width:
                lines.append(current)
                current = ch
            else:
                current = candidate
        lines.append(current)
    return lines


def base_scene(index: int) -> Image.Image:
    top = np.array([12, 15, 42], dtype=np.float32)
    bottom = np.array([43, 22, 72], dtype=np.float32)
    t = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    arr = np.repeat((top * (1 - t) + bottom * t), W, axis=1)
    yy, xx = np.mgrid[0:H, 0:W]
    glow = np.exp(-(((xx - 1500) / 650) ** 2 + ((yy - 300) / 600) ** 2))[..., None]
    arr = np.clip(arr + glow * np.array([24, 18, 50]), 0, 255).astype(np.uint8)
    # Keep the canvas RGB while drawing: ImageDraw's RGBA mode then alpha-blends
    # translucent cards instead of replacing pixels with nearly-transparent white.
    im = Image.fromarray(arr, "RGB")
    d = ImageDraw.Draw(im, "RGBA")
    rng = random.Random(20261022 + index)
    for _ in range(80):
        x, y = rng.randrange(30, W - 30), rng.randrange(30, 850)
        r = rng.choice([1, 1, 2, 2, 3])
        alpha = rng.randrange(35, 135)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(193, 207, 255, alpha))
    d.rounded_rectangle((82, 62, 340, 116), radius=25, fill=(135, 113, 255, 45), outline=(178, 166, 255, 130), width=2)
    d.text((108, 73), "DAY 0", font=font(30, 750), fill=(242, 237, 255, 255))
    d.text((365, 73), "AI 账号运营实验", font=font(29, 550), fill=(198, 197, 230, 255))
    d.rounded_rectangle((1640, 62, 1840, 112), radius=22, fill=(255, 179, 102, 30), outline=(255, 196, 128, 120), width=2)
    d.text((1675, 73), "视频草稿", font=font(26, 650), fill=(255, 218, 174, 255))
    return im


def add_character(im: Image.Image) -> None:
    char = Image.open(CHARACTER).convert("RGBA")
    target_h = 745
    target_w = round(char.width * target_h / char.height)
    char = char.resize((target_w, target_h), Image.Resampling.LANCZOS)
    x, y = 1325, 112
    shadow = Image.new("RGBA", im.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow, "RGBA")
    sd.rounded_rectangle((x - 24, y - 20, x + target_w + 24, y + target_h + 24), radius=40, fill=(0, 0, 0, 150))
    shadow = shadow.filter(ImageFilter.GaussianBlur(22))
    im.paste(shadow, (0, 0), shadow)
    d = ImageDraw.Draw(im, "RGBA")
    d.rounded_rectangle((x - 24, y - 24, x + target_w + 24, y + target_h + 24), radius=40, fill=(252, 250, 255, 255), outline=(197, 183, 255, 190), width=3)
    im.paste(char, (x, y), char)


def add_heading(im: Image.Image, scene: dict, index: int) -> None:
    d = ImageDraw.Draw(im, "RGBA")
    d.text((110, 164), scene["kicker"], font=font(36, 550), fill=(180, 180, 219, 255))
    kind = scene["kind"]
    if kind == "options":
        sizes = [82]
        ys = [225]
    elif kind == "intro":
        sizes = [72, 72]
        ys = [250, 355]
    elif kind == "ending":
        sizes = [96, 78]
        ys = [230, 350]
    else:
        sizes = [94, 84]
        ys = [240, 360]
    for i, line in enumerate(scene["title"]):
        color = (248, 246, 255, 255) if i == 0 else (255, 211, 119, 255)
        d.text((105, ys[i]), line, font=font(sizes[i], 800), fill=color, stroke_width=1, stroke_fill=(25, 18, 50, 180))

    if kind == "score":
        cards = [(110, 565, 480, 710, "企划", "× 8"), (510, 565, 880, 710, "成片", "× 0")]
        for x1, y1, x2, y2, label, value in cards:
            d.rounded_rectangle((x1, y1, x2, y2), radius=26, fill=(255, 255, 255, 18), outline=(255, 255, 255, 45), width=2)
            d.text((x1 + 28, y1 + 23), label, font=font(34, 550), fill=(190, 188, 220, 255))
            d.text((x1 + 175, y1 + 35), value, font=font(62, 800), fill=(255, 224, 150, 255))
    elif kind == "intro":
        d.rounded_rectangle((110, 535, 1000, 675), radius=28, fill=(119, 93, 222, 35), outline=(169, 146, 255, 90), width=2)
        d.text((150, 563), "自我介绍还没做完，片头先有了三版。", font=font(42, 600), fill=(222, 214, 255, 255))
    elif kind == "challenge":
        labels = ["日更视频", "真实数据", "翻车公开"]
        for j, label in enumerate(labels):
            x = 110 + j * 350
            d.rounded_rectangle((x, 580, x + 310, 675), radius=25, fill=(94, 189, 255, 28), outline=(142, 200, 255, 100), width=2)
            d.text((x + 55, 603), label, font=font(39, 650), fill=(207, 229, 255, 255))
        d.text((112, 724), "AI 参与制作｜人类审核与发布", font=font(31, 500), fill=(175, 176, 208, 255))
    elif kind == "monitor":
        d.rounded_rectangle((110, 555, 1050, 690), radius=28, fill=(255, 255, 255, 18), outline=(255, 255, 255, 45), width=2)
        d.text((158, 580), "“做完，才开新坑。”", font=font(56, 700), fill=(255, 222, 145, 255))
    elif kind == "options":
        options = [("A", "学 B 站黑话"), ("B", "三种风格介绍自己"), ("C", "把一个 AI 热点讲成人话")]
        for j, (letter, label) in enumerate(options):
            y = 355 + j * 145
            d.rounded_rectangle((110, y, 1160, y + 116), radius=28, fill=(255, 255, 255, 20), outline=(164, 148, 255, 85), width=2)
            d.ellipse((140, y + 19, 218, y + 97), fill=(150, 118, 255, 210))
            d.text((161, y + 27), letter, font=font(42, 800), fill=(255, 255, 255, 255))
            d.text((255, y + 29), label, font=font(43, 600), fill=(236, 232, 255, 255))
    elif kind == "ending":
        d.text((115, 565), "新企划 +1", font=font(48, 600), fill=(152, 148, 179, 255))
        d.line((105, 598, 410, 578), fill=(255, 131, 153, 230), width=7)
        d.text((110, 650), "今天已超预算", font=font(56, 750), fill=(255, 211, 119, 255))
        d.text((112, 755), "角色图片：用户提供（原始作者与授权待补）", font=font(23, 450), fill=(160, 157, 188, 255))


def add_subtitle(im: Image.Image, narration: str, index: int) -> None:
    d = ImageDraw.Draw(im, "RGBA")
    d.rounded_rectangle((80, 875, 1840, 1028), radius=30, fill=(4, 7, 22, 225), outline=(255, 255, 255, 35), width=2)
    fnt = font(36 if len(narration) > 65 else 39, 500)
    lines = wrap(d, narration, fnt, 1660)
    total_h = len(lines) * 52
    y = 875 + (153 - total_h) / 2 - 4
    for line in lines:
        d.text((122, y), line, font=fnt, fill=(248, 248, 255, 255))
        y += 52
    d.text((1702, 824), f"{index:02d} / 06", font=font(25, 600), fill=(192, 184, 224, 255))


def audio_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as w:
        return w.getnframes() / w.getframerate()


def srt_time(seconds: float) -> str:
    ms = round(seconds * 1000)
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def main() -> None:
    for directory in (SLIDE_DIR, SEGMENT_DIR):
        directory.mkdir(parents=True, exist_ok=True)
    durations = [audio_duration(AUDIO_DIR / f"scene-{i:02d}.wav") for i in range(1, 7)]
    tails = [0.45, 0.45, 0.45, 0.45, 0.45, 1.80]

    for i, scene in enumerate(SCENES, 1):
        im = base_scene(i)
        add_character(im)
        add_heading(im, scene, i)
        add_subtitle(im, scene["narration"], i)
        im.convert("RGB").save(SLIDE_DIR / f"scene-{i:02d}.png", quality=95)

    # A cover layout without subtitles is supplied separately for review.
    cover = base_scene(1)
    add_character(cover)
    add_heading(cover, SCENES[0], 1)
    d = ImageDraw.Draw(cover, "RGBA")
    d.rounded_rectangle((110, 800, 830, 875), radius=24, fill=(133, 105, 255, 75))
    d.text((145, 816), "Gemini娘的账号运营实验", font=font(34, 600), fill=(238, 231, 255, 255))
    cover.convert("RGB").save(ROOT / "Day0-cover.png", quality=95)

    for i, (duration, tail) in enumerate(zip(durations, tails), 1):
        total = duration + tail
        frames = math.ceil(total * FPS)
        zoom = f"1+0.018*on/{frames}" if i % 2 else f"1.018-0.018*on/{frames}"
        vf = (
            f"zoompan=z='{zoom}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
            f":d={frames}:s={W}x{H}:fps={FPS},format=yuv420p"
        )
        if i == 1:
            vf += ",fade=t=in:st=0:d=0.30"
        if i == 6:
            vf += f",fade=t=out:st={max(0, total - 0.65):.3f}:d=0.65"
        cmd = [
            FFMPEG, "-hide_banner", "-loglevel", "error", "-y",
            "-loop", "1", "-i", str(SLIDE_DIR / f"scene-{i:02d}.png"),
            "-i", str(AUDIO_DIR / f"scene-{i:02d}.wav"),
            "-filter_complex",
            f"[0:v]{vf}[v];[1:a]loudnorm=I=-16:TP=-1.5:LRA=11,apad=pad_dur={tail}[a]",
            "-map", "[v]", "-map", "[a]", "-t", f"{total:.3f}",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "19",
            "-r", str(FPS), "-c:a", "aac", "-b:a", "160k", "-ar", "44100", "-ac", "1",
            "-movflags", "+faststart", str(SEGMENT_DIR / f"scene-{i:02d}.mp4"),
        ]
        run(cmd)

    concat = SEGMENT_DIR / "concat.txt"
    concat.write_text("".join(f"file '{(SEGMENT_DIR / f'scene-{i:02d}.mp4').as_posix()}'\n" for i in range(1, 7)), encoding="utf-8")
    output = ROOT / "Day0-Gemini娘-视频草稿.mp4"
    run([
        FFMPEG, "-hide_banner", "-loglevel", "error", "-y",
        "-f", "concat", "-safe", "0", "-i", str(concat),
        "-c", "copy", "-movflags", "+faststart", str(output),
    ])

    cursor = 0.0
    blocks = []
    for i, (scene, duration) in enumerate(zip(SCENES, durations), 1):
        blocks.append(f"{i}\n{srt_time(cursor)} --> {srt_time(cursor + duration)}\n{scene['narration']}\n")
        cursor += duration + tails[i - 1]
    (ROOT / "Day0-Gemini娘-字幕.srt").write_text("\n".join(blocks), encoding="utf-8")
    print(output)
    print(f"duration_target={sum(durations) + sum(tails):.3f}s")


if __name__ == "__main__":
    main()
