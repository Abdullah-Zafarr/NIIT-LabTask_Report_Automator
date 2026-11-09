"""Render PDF pages as high-resolution images.

Usage:
    py render_pdf_pages.py document.pdf [--out-dir preview] [--dpi 150]
    py render_pdf_pages.py document.pdf --pages 1-3,5 --prefix slide_
"""

import argparse
import os
import sys

try:
    import fitz  # PyMuPDF
except ImportError:
    sys.exit("Missing pymupdf dependency. Install via: py -m pip install pymupdf")


def parse_page_selection(spec, total_pages):
    """Parse comma-separated page numbers and ranges (1-based), returning 0-based indices."""
    if not spec or spec.strip().lower() in ("all", "*"):
        return list(range(total_pages))

    selected = set()
    parts = [p.strip() for p in spec.split(",") if p.strip()]

    for part in parts:
        if "-" in part:
            bounds = part.split("-", 1)
            try:
                start = int(bounds[0])
                end = int(bounds[1])
            except ValueError:
                sys.exit(f"Invalid page range: '{part}'")
            if start > end:
                start, end = end, start
            for p in range(start, end + 1):
                if 1 <= p <= total_pages:
                    selected.add(p - 1)
        else:
            try:
                p = int(part)
                if 1 <= p <= total_pages:
                    selected.add(p - 1)
            except ValueError:
                sys.exit(f"Invalid page number: '{part}'")

    return sorted(list(selected))


def main():
    parser = argparse.ArgumentParser(description="Render pages of a PDF document as images.")
    parser.add_argument("pdf", help="Path to input PDF file")
    parser.add_argument("--out-dir", "-o", default=None, help="Directory to save rendered images (default: <pdf_name>_pages)")
    parser.add_argument("--dpi", type=int, default=150, help="Rendering resolution DPI (default: 150)")
    parser.add_argument("--prefix", default="page_", help="Prefix for output image files (default: 'page_')")
    parser.add_argument("--pages", default="all", help="Pages to render, e.g. '1,3,5-7' or 'all' (default: all)")
    parser.add_argument("--ext", default="png", choices=["png", "jpg", "jpeg"], help="Image format (default: png)")
    args = parser.parse_args()

    pdf_path = os.path.abspath(args.pdf)
    if not os.path.isfile(pdf_path):
        sys.exit(f"PDF file not found: {pdf_path}")

    stem = os.path.splitext(os.path.basename(pdf_path))[0]
    out_dir = os.path.abspath(args.out_dir if args.out_dir else f"{stem}_pages")
    os.makedirs(out_dir, exist_ok=True)

    try:
        doc = fitz.open(pdf_path)
    except Exception as exc:
        sys.exit(f"Failed to open PDF '{pdf_path}': {exc}")

    total = len(doc)
    page_indices = parse_page_selection(args.pages, total)

    if not page_indices:
        sys.exit(f"No valid pages selected (document has {total} pages).")

    print(f"Rendering {len(page_indices)} of {total} pages from '{os.path.basename(pdf_path)}' to '{out_dir}'...")

    saved_files = []
    for idx in page_indices:
        page = doc[idx]
        pix = page.get_pixmap(dpi=args.dpi)
        filename = f"{args.prefix}{idx + 1:02d}.{args.ext}"
        target = os.path.join(out_dir, filename)
        pix.save(target)
        saved_files.append(target)
        print(f"  [+] Page {idx + 1} -> {filename} ({pix.width}x{pix.height})")

    doc.close()
    print(f"\nDone. Successfully saved {len(saved_files)} image(s) in {out_dir}")


if __name__ == "__main__":
    main()
