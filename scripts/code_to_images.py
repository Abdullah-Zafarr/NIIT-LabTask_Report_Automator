"""Turn a source file into several small, readable, syntax-highlighted PNGs.

Usage:
    py code_to_images.py <source-file> --out-dir <dir> [--prefix q1_code]
                         [--lines 12] [--lang cpp] [--max-cols 80]

Prints a JSON list of the image paths (in reading order).
Every chunk has the same width, and line numbers continue across chunks.
"""
import argparse
import json
import os
import sys

from PIL import Image, ImageDraw
from pygments import lex
from pygments.lexers import get_lexer_by_name, get_lexer_for_filename
from pygments.styles import get_style_by_name
from pygments.util import ClassNotFound

sys.path.insert(0, os.path.dirname(__file__))
from _common import mono_font, expand_tabs  # noqa: E402

EXT_LANG = {
    ".cpp": "cpp", ".cc": "cpp", ".c": "c", ".h": "c", ".hpp": "cpp",
    ".html": "html", ".htm": "html", ".css": "css", ".js": "javascript",
    ".asm": "nasm", ".py": "python", ".java": "java", ".sql": "sql",
}

FONT_SIZE = 24          # drawn large; Word scales it down, so text stays sharp
PAD = 26
BORDER = 3
BORDER_COLOR = (90, 90, 90)
GUTTER_COLOR = "#6e7681"


def get_lexer(path, lang):
    if lang:
        return get_lexer_by_name(lang)
    ext = os.path.splitext(path)[1].lower()
    if ext in EXT_LANG:
        return get_lexer_by_name(EXT_LANG[ext])
    try:
        return get_lexer_for_filename(path)
    except ClassNotFound:
        return get_lexer_by_name("text")


def colored_lines(code, lexer, style):
    """Return a list of lines; each line is a list of (char, colour)."""
    token_colors = {}
    lines = [[]]
    for ttype, value in lex(code, lexer):
        if ttype not in token_colors:
            t, color = ttype, None
            while t is not None and color is None:
                try:
                    color = style.style_for_token(t).get("color")
                except KeyError:
                    color = None
                t = t.parent
            token_colors[ttype] = "#" + color if color else "#f8f8f2"
        color = token_colors[ttype]
        for ch in value:
            if ch == "\n":
                lines.append([])
            elif ch != "\r":
                lines[-1].append((ch, color))
    if lines and not lines[-1]:
        lines.pop()          # trailing newline
    return lines


def brace_depths(raw_lines):
    depth, out = 0, [0]
    for line in raw_lines:
        depth += line.count("{") - line.count("}")
        out.append(max(depth, 0))
    return out


def split_chunks(raw_lines, size):
    """Split into chunks of ~size lines, preferring natural break points."""
    n = len(raw_lines)
    depths = brace_depths(raw_lines)
    chunks, i = [], 0
    while i < n:
        if n - i <= size + 3:
            chunks.append((i, n))
            break
        chosen = i + size
        for j in range(min(i + size + 2, n - 1), i + size // 2, -1):
            blank_here = raw_lines[j - 1].strip() == ""
            blank_next = raw_lines[j].strip() == ""
            if blank_here or blank_next or depths[j] == 0:
                chosen = j
                break
        chunks.append((i, chosen))
        i = chosen
    return chunks


def render_chunk(lines, start_no, total_lines, cols, bg, fg_font, wrap_cols):
    font = fg_font
    char_w = font.getlength("M")
    line_h = int(FONT_SIZE * 1.5)
    digits = len(str(total_lines))
    gutter_w = int(char_w * (digits + 2))

    # strip blank lines at both ends of the chunk (numbers are kept for the rest)
    first, last = 0, len(lines)
    while first < last and not lines[first]:
        first += 1
    while last > first and not lines[last - 1]:
        last -= 1
    lines, start_no = lines[first:last], start_no + first

    rows = []   # (line_number or None, [(char, colour)])
    for k, line in enumerate(lines):
        pieces = [line[p:p + wrap_cols] for p in range(0, max(len(line), 1), wrap_cols)] or [[]]
        for idx, piece in enumerate(pieces):
            rows.append((start_no + k if idx == 0 else None, piece))

    width = int(PAD * 2 + gutter_w + cols * char_w) + BORDER * 2
    height = PAD * 2 + line_h * len(rows) + BORDER * 2
    img = Image.new("RGB", (width, height), bg)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, width - 1, height - 1], outline=BORDER_COLOR, width=BORDER)

    y = PAD + BORDER
    for num, row in rows:
        if num is not None:
            label = str(num).rjust(digits)
            d.text((PAD + BORDER, y), label, font=font, fill=GUTTER_COLOR)
        x = PAD + BORDER + gutter_w
        for ch, color in row:
            if ch != " ":
                d.text((x, y), ch, font=font, fill=color)
            x += char_w
        y += line_h
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--prefix", default="code")
    ap.add_argument("--lines", type=int, default=12, help="target lines per image")
    ap.add_argument("--lang", default=None)
    ap.add_argument("--max-cols", type=int, default=80, help="wrap lines longer than this")
    ap.add_argument("--style", default="monokai")
    args = ap.parse_args()

    with open(args.source, encoding="utf-8", errors="replace") as f:
        code = expand_tabs(f.read()).rstrip("\n")

    os.makedirs(args.out_dir, exist_ok=True)
    lexer = get_lexer(args.source, args.lang)
    style = get_style_by_name(args.style)
    bg = style.background_color or "#272822"
    lines = colored_lines(code, lexer, style)
    raw = code.split("\n")
    cols = max(36, min(max(len(r) for r in raw), args.max_cols))
    font = mono_font(FONT_SIZE)

    paths = []
    for n, (a, b) in enumerate(split_chunks(raw, args.lines), start=1):
        img = render_chunk(lines[a:b], a + 1, len(raw), cols, bg, font, args.max_cols)
        path = os.path.abspath(os.path.join(args.out_dir, f"{args.prefix}_{n:02d}.png"))
        img.save(path)
        paths.append(path)
    print(json.dumps(paths, indent=2))


if __name__ == "__main__":
    main()
