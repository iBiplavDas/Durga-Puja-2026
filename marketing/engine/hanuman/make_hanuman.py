"""Why did Hanuman forget his strength? Storybook reel: Canva 3D frames animated in layers, Hindi narration.
Reuses the kit in ../anim/make_anim.py (camera, layers, light, clouds, titles, edit)."""
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "anim"))
import make_anim as K  # noqa: E402
from brand import GOLD, H, LABEL, W, ease, tracked  # noqa: E402

F = HERE / "frames"


def load(k):
    full = Image.open(F / f"{k}_full.png").convert("RGBA")
    fg = Image.open(F / f"{k}_fg.png").convert("RGBA") if (F / f"{k}_fg.png").exists() else None
    bg = Image.open(F / f"{k}_bg.jpg").convert("RGBA") if (F / f"{k}_bg.jpg").exists() else None
    return full, fg, bg


K.FR = {k: load(k) for k in ("h1", "h2", "h3", "h4", "h5", "h6")}
K.VO = HERE.parent / "vo" / "hanuman"
K.OUT = HERE / "out"
crop, layered, lerp, put, glow, motes, rays, rush, title, to_screen = (
    K.crop, K.layered, K.lerp, K.put, K.glow, K.motes, K.rays, K.rush, K.title, K.to_screen)


def moved(k, cam, dx, dy, tilt=0.0):
    """A compact figure (a flyer against the sky) travelling further across its world."""
    full, fg, bg = K.FR[k]
    im = crop(bg, *cam)
    f = crop(fg, *cam)
    if tilt:
        f = f.rotate(tilt, Image.BICUBIC, center=(W / 2, H / 2))
    im.alpha_composite(f, (int(dx), int(dy)))
    return im


def fade_strength(im, k):
    """His strength drains away: colour and warmth fade, edges darken."""
    rgb = ImageEnhance.Color(im.convert("RGB")).enhance(1 - 0.75 * k)
    rgb = ImageEnhance.Brightness(rgb).enhance(1 - 0.25 * k)
    out = rgb.convert("RGBA")
    out.alpha_composite(Image.new("RGBA", (W, H), (20, 26, 60, int(70 * k))))
    return out


# ---- shots (positions in frame pixels, 1080 x 1920) ------------------------------------------------------------
def s1(t, d):  # hook: he forgot his own strength
    cam = lerp((560, 960, 1.0), (680, 820, 1.25), ease(t / d))
    im = layered("h1", cam, breathe=0.006 * math.sin(t * 2), anchor=(560, 1900))
    motes(im, t, 0.6)
    title(im, "अपनी ताकत भूल गए?", "WHY HANUMAN FORGOT HIS POWER", t, 0.4, size=104)
    return im


def s2(t, d):  # baby Hanuman leaps for the sun
    k = ease(t / d)
    cam = (560, 900 - 60 * k, 1.05)
    im = moved("h2", cam, 70 * k, -90 * k + 8 * math.sin(t * 3), tilt=-4 * k)
    sx, sy = to_screen(*cam, 961, 288)
    rays(im, t, sx, sy, 0.9)
    put(im, glow(140, (255, 220, 140), 200), sx, sy, 0.7 + 0.2 * math.sin(t * 2))
    motes(im, t, 0.6)
    return im


def s3(t, d):  # the sages' curse: he forgets
    k = ease((t - 1.0) / (d - 1.5))
    im = crop(K.FR["h2"][0], *lerp((520, 700, 1.4), (513, 520, 1.9), ease(t / d)))
    return fade_strength(im, k)


def s4(t, d):  # years later: the endless ocean
    cam = lerp((540, 1100, 1.0), (900, 700, 1.35), ease(t / d))
    im = crop(K.FR["h3"][0], *cam)
    lx, ly = to_screen(*cam, 945, 561)
    put(im, glow(80, (255, 220, 150), 150), lx, ly, 0.5 + 0.2 * math.sin(t * 2))
    motes(im, t, 0.3)
    return im


def s5(t, d):  # Jambavan reminds him
    cam = lerp((300, 700, 1.6), (640, 760, 1.5), ease((t - 0.8) / (d - 1.2)))
    im = layered("h1", cam, breathe=0.006 * math.sin(t * 2), anchor=(560, 1900))
    hx, hy = to_screen(*cam, 673, 609)
    put(im, glow(120, (255, 214, 140), 140), hx, hy, ease((t - d * 0.6) / 1.2) * 0.7)
    motes(im, t, 0.5)
    return im


def s6(t, d):  # he remembers, grows, and leaps
    a, b = d * 0.3, d * 0.62
    if t < a:  # the aura rises
        im = crop(K.FR["h4"][0], *lerp((593, 700, 1.25), (593, 600, 1.45), ease(t / a)))
        put(im, glow(260, (255, 210, 120), 170), 593 * 1, 900, 0.3 + 0.6 * ease(t / a))
        motes(im, t, 1.0)
        return im
    if t < b:  # mountain-tall: tilt up from the army to his face
        k = ease((t - a) / (b - a))
        im = layered("h5", (560, 1400 - 700 * k, 1.35 - 0.3 * k), breathe=0.008 * math.sin(t * 2.5), anchor=(560, 1700))
        rush(im, t, 0.25)
        return im
    k = (t - b) / (d - b)  # the leap across the ocean to Lanka
    im = moved("h6", (540 + 40 * k, 960, 1.08), -60 + 120 * k, 14 * math.sin(t * 2.4), tilt=2 * math.sin(t * 1.8))
    rush(im, t, 1.0)
    return im


def s7(t, d):  # the lesson
    cam = lerp((620, 900, 1.35), (560, 960, 1.0), ease(t / d))
    im = layered("h1", cam, breathe=0.006 * math.sin(t * 2), anchor=(560, 1900))
    put(im, glow(200, (255, 214, 140), 120), 560, 900, 0.5)
    motes(im, t, 0.9)
    return im


def s8(t, d):  # the send
    im = moved("h6", (560, 940, 1.1), 20 * math.sin(t * 0.8), 14 * math.sin(t * 2.4), tilt=2 * math.sin(t * 1.8))
    rush(im, t, 0.6)
    title(im, "उसे याद दिलाइए", "SEND THIS TO THAT FRIEND", t, 0.4, size=112)
    a = ease((t - (d - 2.6)) / 0.6)
    if a > 0:
        tracked(ImageDraw.Draw(im), 1800, "@pujoparikramaguide", LABEL(24), K.fade(GOLD, a), 2)
    return im


K.SHOTS = [("s1", "l1", s1, 0.6), ("s2", "l2", s2, 0), ("s3", "l3", s3, 0.2), ("s4", "l4", s4, 0), ("s5", "l5", s5, 0),
           ("s6", "l6", s6, 0.8), ("s7", "l7", s7, 0), ("s8", "l8", s8, 3.0)]  # the last shot holds for the end card

if __name__ == "__main__":
    if "preview" in sys.argv:
        K.preview()
        print("preview")
    else:
        t = K.render(set(sys.argv[1:]))
        (K.OUT / "ganesha_kartikeya_animated.mp4").rename(K.OUT / "hanuman_strength.mp4")
        print("ok", round(t, 2))
