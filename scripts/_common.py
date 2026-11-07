"""Shared helpers for the lab-assignment skill scripts."""
import os
from PIL import ImageFont

_FONT_CANDIDATES = [
    r"C:\Windows\Fonts\consola.ttf",
    r"C:\Windows\Fonts\CascadiaMono.ttf",
    r"C:\Windows\Fonts\cour.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/System/Library/Fonts/Menlo.ttc",
]


def mono_font(size):
    """Return a monospace font (Consolas first), falling back to Pillow's default."""
    for path in _FONT_CANDIDATES:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def expand_tabs(text, width=4):
    return text.replace("\t", " " * width)
