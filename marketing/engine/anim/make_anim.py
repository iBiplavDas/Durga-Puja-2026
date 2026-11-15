"""Ganesha and Kartikeya's race as a moving storybook: AI-made 3D frames (Canva), animated in layers, Hindi narration.

Each frame is split into a character layer and a filled-in background, so the characters breathe, bob and fly
against their world while the camera moves; light, clouds, wind and glows sit on top."""
import functools
import json
import math
import random
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).parent))
from brand import DEVA, FPS, GOLD, H, IVORY, LABEL, NIGHT, W, ease, tracked

HERE = Path(__file__).parent
F = HERE / "frames"
VO = HERE.parent / "vo" / "race"
OUT = HERE / "out"
FLUTE = "/home/user/Durga-Puja-2026/app/audio/story_flute.mp3"
rnd = random.Random(5)


def load(k):
    full = Image.open(F / f"{k}_full.png" if (F / f"{k}_full.png").exists() else F / f"{k}.png").convert("RGBA")
    full = full.resize((W, H), Image.LANCZOS)
    fg = Image.open(F / f"{k}_fg.png").convert("RGBA") if (F / f"{k}_fg.png").exists() else None
    bg = Image.open(F / f"{k}_bg.jpg").convert("RGBA") if (F / f"{k}_bg.jpg").exists() else None
    return full, fg, bg


FR = {k: load(k) for k in ("f1", "f2", "f3", "f4", "f5", "f6")}


# ---- camera and layers ----------------------------------------------------------------------------------------
def crop(im, cx, cy, z):
    """A window of 1/z the frame, centred on (cx, cy) in frame pixels, scaled back to full size."""
    w, h = W / z, H / z
    x0 = min(max(cx - w / 2, 0), W - w)
    y0 = min(max(cy - h / 2, 0), H - h)
    return im.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + w, y0 + h))


def to_screen(cx, cy, z, px, py):
    w, h = W / z, H / z
    x0 = min(max(cx - w / 2, 0), W - w)
    y0 = min(max(cy - h / 2, 0), H - h)
    return (px - x0) * z, (py - y0) * z


def layered(k, cam, dx=0, dy=0, breathe=0.0, tilt=0.0, anchor=None):
    """Background through the camera, then the characters on top, nudged (dx, dy), breathing and tilting a little."""
    full, fg, bg = FR[k]
    if fg is None:
        return crop(full, *cam)
    im = crop(bg, *cam)
    f = crop(fg, *cam)
    if breathe or tilt:
        ax, ay = anchor or (W / 2, H)
        s = 1 + breathe
        f2 = f.resize((W, int(H * s)), Image.BICUBIC)
        if tilt:
            f2 = f2.rotate(tilt, Image.BICUBIC, center=(ax, ay * s))
        f = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        f.alpha_composite(f2, (0, int(ay - ay * s)))
    im.alpha_composite(f, (int(dx), int(dy)))
    return im


def lerp(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(len(a)))


# ---- light, air and gold --------------------------------------------------------------------------------------
@functools.lru_cache(maxsize=256)
def glow(r, color, peak=255):
    s = Image.new("RGBA", (r * 4, r * 4), color + (0,))
    a = Image.new("L", s.size, 0)
    ImageDraw.Draw(a).ellipse([r * 1.5, r * 1.5, r * 2.5, r * 2.5], fill=peak)
    s.putalpha(a.filter(ImageFilter.GaussianBlur(r * 0.6)))
    return s


def put(im, sprite, x, y, a=1.0):
    if a <= 0:
        return
    if a < 1:
        sprite = sprite.copy()
        sprite.putalpha(sprite.getchannel("A").point(lambda v: int(v * a)))
    im.alpha_composite(sprite, (int(x - sprite.width / 2), int(y - sprite.height / 2)))


DOT = glow(9, (255, 232, 180))
MOTES = [(rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(20, 70), rnd.uniform(0, 6.28), rnd.uniform(0.3, 0.9))
         for _ in range(40)]


def motes(im, t, k=1.0):
    for x, y, v, ph, b in MOTES:
        put(im, DOT, x + 16 * math.sin(t * 0.7 + ph), (y - v * t) % (H + 60) - 30, k * b * (0.6 + 0.4 * math.sin(t * 3 + ph)))


def rays(im, t, x, y, k=1.0):
    """Soft light rays from a point, slowly turning."""
    lay = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(lay)
    for i in range(12):
        a = t * 0.15 + i * math.pi / 6
        d.polygon([(x, y), (x + 1600 * math.cos(a - 0.05), y + 1600 * math.sin(a - 0.05)),
                   (x + 1600 * math.cos(a + 0.05), y + 1600 * math.sin(a + 0.05))], fill=int(38 * k))
    im.paste(Image.new("RGBA", (W, H), (255, 228, 160, 255)), (0, 0), lay.filter(ImageFilter.GaussianBlur(18)))


def _cloud(seed, r):
    g = random.Random(seed)
    a = Image.new("L", (r * 4, r * 2), 0)
    d = ImageDraw.Draw(a)
    for _ in range(10):
        rr = g.uniform(r * 0.35, r * 0.8)
        x, y = g.uniform(r * 0.8, r * 3.2), g.uniform(r * 0.6, r * 1.4)
        d.ellipse([x - rr, y - rr * 0.7, x + rr, y + rr * 0.7], fill=int(g.uniform(150, 230)))
    s = Image.new("RGBA", a.size, (255, 255, 255, 0))
    s.putalpha(a.filter(ImageFilter.GaussianBlur(r * 0.25)))
    return s


CLOUDS = [_cloud(i, rnd.choice((120, 160, 220))) for i in range(6)]
FLY = [(rnd.uniform(0, 1), rnd.uniform(100, H - 100), rnd.uniform(0.8, 1.6), rnd.randrange(6)) for _ in range(9)]
STREAKS = [(rnd.uniform(0, 1), rnd.uniform(60, H - 60), rnd.uniform(140, 340)) for _ in range(30)]


def rush(im, t, k=1.0):
    """Clouds and wind racing past right to left: speed."""
    d = ImageDraw.Draw(im)
    for off, y, ln in STREAKS:
        x = W + 400 - ((off * 3000 + t * 2600) % (W + 800))
        d.line([x, y, x + ln, y], fill=(255, 250, 235, int(120 * k)), width=3)
    for off, y, sp, c in FLY:
        x = W + 500 - ((off * 4000 + t * 1500 * sp) % (W + 1000))
        put(im, CLOUDS[c], x, y, 0.55 * k)


def ring(im, centre, rx, ry, upto, alpha=1.0):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    pts = [(centre[0] + rx * math.cos(a), centre[1] + ry * math.sin(a))
           for a in [math.pi / 2 + i * 0.04 for i in range(int(upto / 0.04) + 1)]]
    for p0, p1 in zip(pts, pts[1:]):
        d.line([p0, p1], fill=(255, 214, 120, int(235 * alpha)), width=10)
    im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(4)))
    im.alpha_composite(lay)


def sparkle_burst(im, x, y, t, k=1.0):
    g = random.Random(9)
    for i in range(28):
        a, v = g.uniform(0, 6.28), g.uniform(120, 420)
        r = v * ease(t / 1.2)
        put(im, glow(8, (255, 230, 150)), x + r * math.cos(a), y + r * math.sin(a), k * (1 - ease((t - 0.6) / 1.2)))


# ---- words ----------------------------------------------------------------------------------------------------
def _shade(start, span, peak):
    g = Image.new("L", (1, H))
    for y in range(H):
        g.putpixel((0, y), int(peak * ease((y - start) / span)))
    return g.resize((W, H))


SHADE, DEEP = _shade(1300, 480, 190), _shade(1100, 420, 235)


def fade(c, a):
    return tuple(int(v * a + NIGHT[i] * (1 - a)) for i, v in enumerate(c))


def title(im, big, small, t, t_in, y=1390, size=140):
    a = ease((t - t_in) / 0.6)
    if a <= 0:
        return
    im.paste(Image.new("RGBA", (W, H), NIGHT + (255,)), (0, 0), DEEP.point(lambda v: int(v * a)))
    d = ImageDraw.Draw(im)
    f = DEVA(size)
    d.text(((W - d.textlength(big, font=f)) / 2, y), big, font=f, fill=fade(GOLD, a))
    if small:
        tracked(d, y + size + 90, small, LABEL(30), fade(IVORY, a), 7)


def label(im, text, t, t_in, y=1660):
    a = ease((t - t_in) / 0.5)
    if a <= 0:
        return
    im.paste(Image.new("RGBA", (W, H), NIGHT + (255,)), (0, 0), SHADE.point(lambda v: int(v * a)))
    tracked(ImageDraw.Draw(im), y, text, LABEL(30), fade(GOLD, a), 6)


# ---- shots (positions are in frame pixels, 1080 x 1920) -------------------------------------------------------
def s1(t, d):  # One fruit, two brothers
    cam = lerp((540, 960, 1.0), (540, 900, 1.12), ease(t / d))
    im = layered("f1", cam, dy=-6 * math.sin(t * 1.3), breathe=0.006 * math.sin(t * 2.2), anchor=(540, 1700))
    mx, my = to_screen(*cam, 529, 880)
    put(im, glow(70, (255, 215, 110), 200), mx, my + 10 * math.sin(t * 2), 0.8 + 0.2 * math.sin(t * 3))
    motes(im, t, 0.7)
    title(im, "एक फल", "ONE FRUIT  ·  TWO BROTHERS", t, 0.5)
    return im


def s2(t, d):  # Narada brings the fruit of knowledge
    cam = lerp((540, 980, 1.0), (528, 1150, 1.45), ease(t / d))
    im = crop(FR["f2"][0], *cam)
    mx, my = to_screen(*cam, 528, 1280)
    rays(im, t, mx, my, ease((t - 2) / 2))
    put(im, glow(90, (255, 215, 110), 210), mx, my, 0.6 + 0.3 * math.sin(t * 3))
    motes(im, t, 0.8)
    return im


def s3(t, d):  # Shiva and Parvati set the challenge
    cam = lerp((540, 900, 1.05), (560, 820, 1.2), ease(t / d))
    im = layered("f3", cam, dx=8 * math.sin(t * 0.8), breathe=0.005 * math.sin(t * 2), anchor=(540, 1920))
    mx, my = to_screen(*cam, 672, 1232)
    put(im, glow(70, (255, 215, 110), 200), mx, my, 0.7 + 0.25 * math.sin(t * 3))
    motes(im, t, 0.6)
    return im


def flight(k, t, d):
    cam = lerp((560, 960, 1.08), (520, 960, 1.08), t / d)
    shake = (4 * math.sin(t * 13), 3 * math.sin(t * 11))
    im = layered(k, (cam[0] + shake[0], cam[1] + shake[1], cam[2]), dx=10 * math.sin(t * 1.7),
                 dy=20 * math.sin(t * 2.3), tilt=2.5 * math.sin(t * 1.9), anchor=(540, 1100))
    rush(im, t)
    return im


def s4(t, d):  # Kartikeya flies: mountains, then the sea
    half = d * 0.5
    if t < half - 0.3:
        return flight("f4", t, d)
    if t > half + 0.3:
        return flight("f5", t, d)
    return Image.blend(flight("f4", t, d), flight("f5", t, d), (t - half + 0.3) / 0.6)


def s5(t, d):  # Ganesha looks at his mouse, then at his parents
    k = t / d
    if k < 0.6:
        cam = lerp((880, 1344, 2.2), (448, 820, 1.7), ease(k / 0.6))
        return crop(FR["f6"][0], *cam)
    im = layered("f3", (540, 960, 1.0), breathe=0.005 * math.sin(t * 2), anchor=(540, 1920))
    return im


def s6(t, d):  # three slow circles around them
    cam = (540, 1000, 1.0)
    im = layered("f3", cam, breathe=0.005 * math.sin(t * 2), anchor=(540, 1920))
    im.alpha_composite(Image.new("RGBA", (W, H), NIGHT + (40,)))
    a = 3 * 2 * math.pi * ease((t - 0.3) / (d - 1.0))
    centre, rx, ry = (560, 1350), 470, 150
    ring(im, centre, rx, ry, a)
    x, y = centre[0] + rx * math.cos(a + math.pi / 2), centre[1] + ry * math.sin(a + math.pi / 2)
    put(im, glow(40, (255, 236, 180)), x, y)
    motes(im, t, 0.5)
    return im


def s7(t, d):  # "You are my world"
    im = crop(FR["f6"][0], *lerp((448, 780, 1.9), (448, 790, 2.15), ease(t / d)))
    title(im, "आप ही मेरी दुनिया", "YOU ARE MY WORLD", t, 0.3, size=104)
    return im


def s8(t, d):  # the fruit goes to Ganesha
    cam = lerp((420, 900, 1.6), (360, 920, 1.75), ease(t / d))
    im = layered("f1", cam, breathe=0.006 * math.sin(t * 2.2), anchor=(300, 1700))
    mx, my = to_screen(*cam, 529, 880)
    put(im, glow(90, (255, 215, 110), 230), mx, my, 0.9)
    sparkle_burst(im, mx, my, t - 0.4)
    motes(im, t, 0.8)
    return im


def s9(t, d):  # Kartikeya leaves for the south: Murugan of Palani
    # the whole view pulls back and drifts as he flies off south, clouds closing in
    k = ease(t / d)
    im = crop(FR["f5"][0], 560 - 40 * k, 960 + 20 * math.sin(t * 2.3), 1.35 - 0.35 * k)
    rush(im, t, 0.4 + 0.5 * k)
    label(im, "MURUGAN  ·  PALANI", t, d * 0.5)
    return im


def s10(t, d):  # look closer
    im = crop(FR["f6"][0], *lerp((540, 960, 1.0), (448, 820, 1.9), ease(t / d)))
    motes(im, t, 0.5)
    return im


def s11(t, d):  # the family; look closer
    cam = lerp((528, 1100, 1.35), (540, 960, 1.0), ease(t / (d - 2)))
    im = crop(FR["f2"][0], *cam)
    mx, my = to_screen(*cam, 528, 1280)
    put(im, glow(90, (255, 215, 110), 200), mx, my, 0.7 + 0.2 * math.sin(t * 3))
    motes(im, t, 0.9)
    title(im, "पास देखिए", "LOOK CLOSER", t, d - 3.2, size=120)
    a = ease((t - (d - 2.6)) / 0.6)
    if a > 0:
        tracked(ImageDraw.Draw(im), 1800, "@pujoparikramaguide", LABEL(24), fade(GOLD, a), 2)
    return im


SHOTS = [("s1", "l1", s1, 0.8), ("s2", "l2", s2, 0), ("s3", "l3", s3, 0), ("s4", "l4", s4, 0.4), ("s5", "l5", s5, 0),
         ("s6", "l6", s6, 1.2), ("s7", "l7", s7, 0.5), ("s8", "l8", s8, 0.6), ("s9", "l9", s9, 0), ("s10", "l10", s10, 0),
         ("s11", "l11", s11, 0)]
XF, LEAD, TAIL, END = 0.5, 0.35, 0.75, 3.0


def durations():
    dur = json.load(open(VO / "durations.json"))
    return [(n, line, fn, int((dur[line] + LEAD + TAIL + extra + (END if n == "s11" else 0)) * FPS) / FPS)
            for n, line, fn, extra in SHOTS]


def preview():
    tiles = []
    for name, line, fn, d in durations():
        tiles += [fn(d * f, d).convert("RGB").resize((180, 320)) for f in (0.3, 0.85)]
    sheet = Image.new("RGB", (180 * len(SHOTS), 640))
    for i, m in enumerate(tiles):
        sheet.paste(m, ((i // 2) * 180, (i % 2) * 320))
    OUT.mkdir(exist_ok=True)
    sheet.save(OUT / "preview.jpg", quality=88)


def render(only=()):
    OUT.mkdir(exist_ok=True)
    parts, starts, t0 = [], [], 0.0
    for name, line, fn, d in durations():
        starts.append((line, t0 + LEAD))
        out = OUT / f"{name}.mp4"
        if not only or name in only:
            frames = OUT / name
            frames.mkdir(exist_ok=True)
            for k in range(int(d * FPS)):
                fn(k / FPS, d).convert("RGB").save(frames / f"{k:04d}.jpg", quality=92)
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", str(FPS), "-i", str(frames / "%04d.jpg"),
                            "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", str(out)], check=True)
        parts.append((out, d))
        t0 += d - XF
    inputs, chain, last, t = [], [], "0:v", parts[0][1]
    for c, _ in parts:
        inputs += ["-i", str(c)]
    for k in range(1, len(parts)):
        chain.append(f"[{last}][{k}:v]xfade=transition=fade:duration={XF}:offset={t - XF:.2f}[v{k}]")
        last, t = f"v{k}", t + parts[k][1] - XF
    n = len(parts)
    for i, (line, st) in enumerate(starts):
        inputs += ["-i", str(VO / f"{line}.wav")]
        chain.append(f"[{n + i}:a]adelay={int(st * 1000)}|{int(st * 1000)},volume=1.25[vo{i}]")
    inputs += ["-i", FLUTE]
    chain.append(f"[{n + len(starts)}:a]volume=0.22,afade=t=in:d=2,afade=t=out:st={t - 3:.2f}:d=3[bg]")
    chain.append("".join(f"[vo{i}]" for i in range(len(starts))) +
                 f"[bg]amix=inputs={len(starts) + 1}:duration=longest:normalize=0,alimiter=limit=0.8:level=false,volume=-1.5dB[a]")
    subprocess.run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", ";".join(chain), "-map", f"[{last}]",
                    "-map", "[a]", "-t", f"{t:.2f}", "-c:v", "libx264", "-preset", "slow", "-crf", "22",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart",
                    str(OUT / "ganesha_kartikeya_animated.mp4")], check=True)
    return t


if __name__ == "__main__":
    if "preview" in sys.argv:
        preview()
        print("preview")
    else:
        print("ok", round(render(set(sys.argv[1:])), 2))
