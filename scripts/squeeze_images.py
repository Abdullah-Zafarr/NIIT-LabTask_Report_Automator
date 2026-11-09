"""Squeeze images slightly (max 12%) in height when that lets them stay on the previous page.

Usage:
    py -u squeeze_images.py report.docx [max_percent]
    py squeeze_images.py report.docx --max-percent 15

Uses Microsoft Word (COM). Edits the file in place. Never shrinks more than max_percent.
"""

import argparse
import os
import sys

try:
    import win32com.client
except ImportError:
    sys.exit("Missing pywin32 dependency. Install via: py -m pip install pywin32")


def page(doc, pos):
    return doc.Range(pos, pos).Information(3)  # wdActiveEndPageNumber


def main():
    parser = argparse.ArgumentParser(
        description="Squeeze inline image heights slightly in Word to eliminate awkward page breaks."
    )
    parser.add_argument("docx", help="Path to input Word (.docx) document")
    parser.add_argument(
        "max_percent_pos",
        nargs="?",
        type=float,
        default=None,
        help="Maximum shrink percentage (positional shorthand, default: 12.0)",
    )
    parser.add_argument(
        "--max-percent",
        "-m",
        type=float,
        default=12.0,
        help="Maximum shrink percentage (default: 12.0)",
    )
    args = parser.parse_args()

    max_pct = args.max_percent_pos if args.max_percent_pos is not None else args.max_percent
    path = os.path.abspath(args.docx)
    if not os.path.isfile(path):
        sys.exit(f"Word document not found: {path}")

    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    doc = word.Documents.Open(path)
    changed = 0
    try:
        n = doc.InlineShapes.Count
        for i in range(1, n + 1):
            shp = doc.InlineShapes(i)
            start = shp.Range.Start
            par = doc.Range(start, start).Paragraphs(1)
            if par.Range.Information(12):          # inside a table: skip
                continue
            prev = par.Previous(1)
            if prev is None:
                continue
            prev_pos = prev.Range.End - 1
            if page(doc, start) <= page(doc, prev_pos):
                continue                           # already on the previous page
            h0 = shp.Height
            shp.LockAspectRatio = False
            ok = False
            pct = 2.0
            while pct <= max_pct:
                shp.Height = h0 * (1 - pct / 100)
                if page(doc, start) <= page(doc, prev_pos):
                    ok = True
                    break
                pct += 2.0
            if ok:
                changed += 1
                print("image", i, "squeezed", int(pct), "%", flush=True)
            else:
                shp.Height = h0
        doc.Save()
    finally:
        doc.Close()
        word.Quit()
    print("squeezed", changed, "images", flush=True)


if __name__ == "__main__":
    main()
