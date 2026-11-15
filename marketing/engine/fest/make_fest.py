"""Festival photo reels (Chhath, Jagaddhatri): real Wikimedia Commons photos with cinematic camera moves, light effects,
film grain and bold titles; music and ambience instead of a synthetic narrator.

    python3 make_fest.py chhath|jag [preview]"""
import functools
import math
import random
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "anim"))
from brand import DEVA, FPS, GOLD, H, IVORY, LABEL, NIGHT, W, ease, tracked  # noqa: E402

AUDIO = Path("/home/user/Durga-Puja-2026/app/audio")
XF = 0.45
rnd = random.Random(3)


@functools.lru_cache(maxsize=64)
def load(name):
    return Image.open(HERE / "hi" / f"{name}.jpg").convert("RGB")


def crop(im, cx, cy, z):
    """A 9:16 window of 1/z the photo's height, centred on (cx, cy) as fractions."""
    h = min(im.height / z, im.width * H / W / z)
    w = h * W / H
    x0 = min(max(cx * im.width - w / 2, 0), im.width - w)
    y0 = min(max(cy * im.height - h / 2, 0), im.height - h)
    return im.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + w, y0 + h)), (x0, y0, w, h)


def to_screen(win, im, fx, fy):
    x0, y0, w, h = win
    return (fx * im.width - x0) / w * W, (fy * im.height - y0) / h * H


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


EMBERS = [(rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(40, 120), rnd.uniform(0, 6.28), rnd.uniform(0.3, 1)) for _ in range(55)]


def embers(im, t, k=1.0, color=(255, 190, 110)):
    sp = glow(7, color)
    for x, y, v, ph, b in EMBERS:
        put(im, sp, x + 25 * math.sin(t * 0.9 + ph), (y - v * t) % (H + 60) - 30, k * b * (0.5 + 0.5 * math.sin(t * 4 + ph)))


def sun(im, x, y, t, k=1.0):
    put(im, glow(320, (255, 170, 90), 110), x, y, k * (0.85 + 0.1 * math.sin(t * 1.5)))
    put(im, glow(90, (255, 235, 190), 230), x, y, k)
    lay = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(lay)
    for i in range(14):
        a = t * 0.08 + i * math.pi / 7
        d.polygon([(x, y), (x + 1700 * math.cos(a - .04), y + 1700 * math.sin(a - .04)),
                   (x + 1700 * math.cos(a + .04), y + 1700 * math.sin(a + .04))], fill=int(26 * k))
    im.paste(Image.new("RGBA", (W, H), (255, 214, 150, 255)), (0, 0), lay.filter(ImageFilter.GaussianBlur(20)))


def flicker(im, pts, t, r=70):
    for i, (x, y) in enumerate(pts):
        f = 0.65 + 0.2 * math.sin(t * 13 + i * 2.1) + 0.15 * math.sin(t * 21.7 + i)
        put(im, glow(r, (255, 160, 70), 170), x, y, f)


GRAIN = [Image.effect_noise((W // 2, H // 2), 40).convert("L").resize((W, H)) for _ in range(4)]


def finish(im, t, warm=0.06):
    """Grade, grain and vignette: the film look."""
    rgb = ImageEnhance.Contrast(im.convert("RGB")).enhance(1.06)
    rgb = Image.blend(rgb, Image.new("RGB", (W, H), (255, 170, 90)), warm)
    out = rgb.convert("RGBA")
    g = GRAIN[int(t * FPS) % 4]
    out.paste(Image.new("RGBA", (W, H), (128, 128, 128, 255)), (0, 0), g.point(lambda v: int(abs(v - 128) * 0.16)))
    return out


def _vig():
    v = Image.new("L", (W, H), 0)
    ImageDraw.Draw(v).ellipse([-W * 0.35, -H * 0.15, W * 1.35, H * 1.15], fill=255)
    return Image.eval(v.filter(ImageFilter.GaussianBlur(220)), lambda p: 255 - p)


VIG = _vig()


def shade(start=1150, span=520, peak=230):
    g = Image.new("L", (1, H))
    for y in range(H):
        g.putpixel((0, y), int(peak * ease((y - start) / span)))
    return g.resize((W, H))


SHADE = shade()
TOP = SHADE.transpose(Image.FLIP_TOP_BOTTOM)


def words(im, big, small, t, t_in, size=150, y=1340, top=False):
    a = ease((t - t_in) / 0.45)
    if a <= 0:
        return
    if top:
        y = 230
    im.paste(Image.new("RGBA", (W, H), NIGHT + (255,)), (0, 0), (TOP if top else SHADE).point(lambda v: int(v * a)))
    d = ImageDraw.Draw(im)
    f = DEVA(size)
    lift = int(26 * (1 - a))
    tw = d.textlength(big, font=f)
    if tw > W - 120:  # long phrases step down so they always fit
        f = DEVA(int(size * (W - 120) / tw))
        tw = d.textlength(big, font=f)
    col = tuple(int(c * a + NIGHT[i] * (1 - a)) for i, c in enumerate(GOLD))
    d.text(((W - tw) / 2, y + lift), big, font=f, fill=col)
    if small:
        sf = LABEL(29)
        sw = sum(d.textlength(ch, font=sf) for ch in small) + 4 * (len(small) - 1)
        if sw > W - 100:
            sf = LABEL(int(29 * (W - 100) / sw))
        tracked(d, y + f.size + 70 + lift, small, sf, tuple(int(c * a + NIGHT[i] * (1 - a)) for i, c in enumerate(IVORY)), 4)


# ---- the two reels --------------------------------------------------------------------------------------------
# shot: (photo, (cx, cy, zoom) start, end, effect, big, small, seconds)
REELS = {
    "chhath": {
        "music": [("story_flute.mp3", 0.5, 0.0), ("shankh.mp3", 0.6, 0.2)],
        "warm": 0.08,
        "end": "जय छठी मैया",
        "end_small": "SANDHYA ARGHYA · SUNDAY 15 NOV",
        "shots": [
            ("chhath_18", (0.42, 0.6, 1.25), (0.38, 0.68, 1.55), ("sun", 0.28, 0.33), "36 घंटे", "WITHOUT A SINGLE SIP OF WATER", 3.6, "top"),
            ("chhath_4", (0.35, 0.5, 1.0), (0.55, 0.5, 1.0), None, "छठ महापर्व", "FOUR DAYS OF FAITH · 13–16 NOV", 3.4),
            ("chhath_1", (0.6, 0.55, 1.15), (0.68, 0.5, 1.4), None, "अर्घ्य", "KNEE-DEEP IN THE RIVER, TO THE SUN", 3.4),
            ("chhath_23", (0.5, 0.45, 1.1), (0.5, 0.55, 1.45), None, "ठेकुआ, फल, सूप", "EVERY OFFERING MADE BY HAND", 3.2),
            ("chhath_27", (0.25, 0.55, 1.0), (0.7, 0.55, 1.0), ("sun", 0.92, 0.05), "डूबते सूरज को प्रणाम", "THE SETTING SUN IS WORSHIPPED TOO", 3.6),
            ("chhath_17", (0.5, 0.5, 1.1), (0.5, 0.48, 1.45), ("diyas",), "रात भर दीये", "THEN A WHOLE NIGHT OF WAITING", 3.4),
            ("chhath_40", (0.5, 0.45, 1.05), (0.5, 0.42, 1.35), ("embers",), "उगता सूरज", "AT SUNRISE, THE FAST ENDS", 3.4),
            ("chhath_37", (0.35, 0.5, 1.0), (0.6, 0.45, 1.05), ("embers",), None, None, 4.8),
        ],
    },
    "jag": {
        "music": [("dhak.mp3", 0.75, 18.0), ("shankh.mp3", 0.55, 0.2)],
        "warm": 0.05,
        "end": "जय माँ जगद्धात्री",
        "end_small": "NAVAMI · WEDNESDAY 18 NOV",
        "shots": [
            ("jag_42", (0.42, 0.55, 1.05), (0.4, 0.45, 1.35), ("embers",), "जगद्धात्री", "SHE WHO HOLDS THE WORLD", 3.6),
            ("jag_4", (0.5, 0.35, 1.25), (0.5, 0.55, 1.05), ("embers",), "सिंह पर सवार", "A FORM OF DURGA, ON A LION OVER AN ELEPHANT", 3.6),
            ("jag_2", (0.42, 0.55, 1.0), (0.6, 0.55, 1.15), None, "चंदननगर", "THE CITY OF LIGHT · 16–19 NOV", 3.4),
            ("jag_3", (0.3, 0.55, 1.0), (0.55, 0.55, 1.2), ("embers",), "रोशनी का शहर", "ITS LIGHT ARTISTS ARE FAMOUS ACROSS INDIA", 3.4),
            ("jag_5", (0.5, 0.45, 1.0), (0.5, 0.4, 1.3), None, "18वीं सदी से", "CELEBRATED SINCE THE 18TH CENTURY", 3.4),
            ("jag_0", (0.5, 0.35, 1.3), (0.5, 0.5, 1.05), ("embers",), None, None, 4.8),
        ],
    },
}


def make_shot(reel, shot, last):
    photo, a, b, fx, big, small, dur = shot[:7]
    top = len(shot) > 7 and shot[7] == "top"
    im0 = load(photo)

    def frame(t):
        k = ease(t / dur)
        cam = tuple(a[i] + (b[i] - a[i]) * k for i in range(3))
        im, win = crop(im0, *cam)
        im = im.convert("RGBA")
        if fx and fx[0] == "sun":
            sx, sy = to_screen(win, im0, fx[1], fx[2])
            sun(im, sx, sy, t)
        elif fx and fx[0] == "diyas":
            pts = [to_screen(win, im0, x, y) for x, y in [(0.3, 0.18), (0.62, 0.15), (0.78, 0.35), (0.2, 0.45), (0.85, 0.6),
                                                          (0.25, 0.75), (0.55, 0.82), (0.7, 0.85)]]
            flicker(im, pts, t)
            embers(im, t, 0.5)
        elif fx and fx[0] == "embers":
            embers(im, t, 0.8)
        im = finish(im, t, REELS[reel]["warm"])
        im.paste(Image.new("RGBA", (W, H), (0, 0, 0, 255)), (0, 0), VIG.point(lambda v: int(v * 0.55)))
        if last:
            words(im, REELS[reel]["end"], REELS[reel]["end_small"], t, 0.5, size=130)
            ah = ease((t - 1.6) / 0.6)
            if ah > 0:
                tracked(ImageDraw.Draw(im), 1800, "@pujoparikramaguide", LABEL(24), tuple(int(c * ah) for c in GOLD), 2)
        elif big:
            words(im, big, small, t, 0.25, top=top)
        return im
    return frame, dur


def render(reel, preview=False):
    spec = REELS[reel]
    out = HERE / f"out_{reel}"
    out.mkdir(exist_ok=True)
    shots = [make_shot(reel, s, i == len(spec["shots"]) - 1) for i, s in enumerate(spec["shots"])]
    if preview:
        tiles = []
        for fn, d in shots:
            tiles += [fn(d * f).convert("RGB").resize((180, 320)) for f in (0.3, 0.9)]
        sheet = Image.new("RGB", (180 * len(shots), 640))
        for i, m in enumerate(tiles):
            sheet.paste(m, ((i // 2) * 180, (i % 2) * 320))
        sheet.save(out / "preview.jpg", quality=88)
        return
    parts = []
    for i, (fn, d) in enumerate(shots):
        fr = out / f"s{i}"
        fr.mkdir(exist_ok=True)
        n = int(d * FPS)
        for k in range(n):
            fn(k / FPS).convert("RGB").save(fr / f"{k:04d}.jpg", quality=92)
        clip = out / f"s{i}.mp4"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", str(FPS), "-i", str(fr / "%04d.jpg"), "-c:v", "libx264",
                        "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", str(clip)], check=True)
        parts.append((clip, n / FPS))
    inputs, chain, last, t = [], [], "0:v", parts[0][1]
    for c, _ in parts:
        inputs += ["-i", str(c)]
    for k in range(1, len(parts)):
        chain.append(f"[{last}][{k}:v]xfade=transition=fade:duration={XF}:offset={t - XF:.2f}[v{k}]")
        last, t = f"v{k}", t + parts[k][1] - XF
    n = len(parts)
    labels = []
    for j, (fname, vol, seek) in enumerate(spec["music"]):
        inputs += ["-ss", str(seek), "-i", str(AUDIO / fname)]
        chain.append(f"[{n + j}:a]volume={vol},afade=t=in:d=0.8,afade=t=out:st={t - 2.5:.2f}:d=2.5[m{j}]")
        labels.append(f"[m{j}]")
    chain.append("".join(labels) + f"amix=inputs={len(labels)}:duration=longest:normalize=0,alimiter=limit=0.8:level=false,volume=-1.5dB[a]")
    subprocess.run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", ";".join(chain), "-map", f"[{last}]", "-map", "[a]",
                    "-t", f"{t:.2f}", "-c:v", "libx264", "-preset", "slow", "-crf", "21", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(out / f"{reel}.mp4")], check=True)
    print("ok", reel, round(t, 2))


if __name__ == "__main__":
    render(sys.argv[1], preview="preview" in sys.argv)
