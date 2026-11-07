"""Render plain text as a console-window screenshot (for program output).

Usage:
    py terminal_to_image.py --text-file out.txt --out out.png [--title "Output"]
    (or pipe text on stdin)
"""
import argparse
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(__file__))
from _common import mono_font, expand_tabs  # noqa: E402

FONT_SIZE = 24
PAD = 22
TITLE_H = 54
BG = (12, 12, 12)
FG = (204, 204, 204)
TITLE_BG = (32, 32, 32)
BORDER = (110, 110, 110)


def render(text, title="Output", min_cols=60, min_rows=6, max_cols=100):
    font = mono_font(FONT_SIZE)
    char_w = font.getlength("M")
    line_h = int(FONT_SIZE * 1.4)
    lines = []
    for raw in expand_tabs(text.replace("\r\n", "\n")).rstrip("\n").split("\n"):
        while len(raw) > max_cols:
            lines.append(raw[:max_cols])
            raw = raw[max_cols:]
        lines.append(raw)
    cols = max(min_cols, min(max(len(l) for l in lines), max_cols))
    rows = max(min_rows, len(lines))
    w = int(PAD * 2 + cols * char_w)
    h = TITLE_H + PAD * 2 + rows * line_h
    img = Image.new("RGB", (w, h), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, w, TITLE_H], fill=TITLE_BG)
    d.text((PAD, TITLE_H // 2 - FONT_SIZE // 2 - 2), title, font=font, fill=(235, 235, 235))
    d.text((w - PAD - char_w * 8, TITLE_H // 2 - FONT_SIZE // 2 - 2), "_  []  X", font=font, fill=(200, 200, 200))
    y = TITLE_H + PAD
    for line in lines:
        d.text((PAD, y), line, font=font, fill=FG)
        y += line_h
    d.rectangle([0, 0, w - 1, h - 1], outline=BORDER, width=3)
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--text-file")
    ap.add_argument("--out", required=True)
    ap.add_argument("--title", default="Output")
    args = ap.parse_args()
    text = open(args.text_file, encoding="utf-8", errors="replace").read() if args.text_file else sys.stdin.read()
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    render(text, args.title).save(args.out)
    print(os.path.abspath(args.out))


if __name__ == "__main__":
    main()
