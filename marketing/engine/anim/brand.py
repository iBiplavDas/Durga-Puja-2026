"""The page's look: night indigo, ivory and muted gold; Devanagari titles, spaced-capital labels."""
from pathlib import Path

from PIL import ImageFont

FONTS = Path("/tmp/reel-work/fonts")
W, H, FPS = 1080, 1920, 30
NIGHT, INDIGO = (14, 18, 40), (30, 36, 74)
IVORY, GOLD, MUTED = (244, 236, 220), (204, 168, 98), (168, 164, 186)

DEVA = lambda s: ImageFont.truetype(str(FONTS / "TiroDevanagariSanskrit-Regular.ttf"), s)
LABEL = lambda s: ImageFont.truetype(str(FONTS / "Poppins-Medium.ttf"), s)


def ease(t):
    t = min(1, max(0, t))
    return t * t * (3 - 2 * t)


def tracked(d, y, text, f, fill, spacing=5, x=None):
    w = sum(d.textlength(ch, font=f) for ch in text) + spacing * (len(text) - 1)
    x = (W - w) / 2 if x is None else x
    for ch in text:
        d.text((x, y), ch, font=f, fill=fill)
        x += d.textlength(ch, font=f) + spacing
