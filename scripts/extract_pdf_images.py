"""Extract embedded raster images from a PDF file.

Usage:
    py extract_pdf_images.py document.pdf [--out-dir extracted_images]
    py extract_pdf_images.py document.pdf --min-width 100 --min-height 100
"""

import argparse
import os
import sys

try:
    import fitz  # PyMuPDF
except ImportError:
    sys.exit("Missing pymupdf dependency. Install via: py -m pip install pymupdf")


def extract_images(pdf_path, out_dir, min_w=20, min_h=20, prefix="p"):
    doc = fitz.open(pdf_path)
    os.makedirs(out_dir, exist_ok=True)

    extracted_count = 0
    total_pages = len(doc)
    seen_xrefs = set()

    for page_idx in range(total_pages):
        page = doc[page_idx]
        image_list = page.get_images(full=True)

        for img_idx, img_info in enumerate(image_list, start=1):
            xref = img_info[0]
            if xref in seen_xrefs:
                continue
            seen_xrefs.add(xref)

            base_img = doc.extract_image(xref)
            width = base_img["width"]
            height = base_img["height"]

            if width < min_w or height < min_h:
                continue

            ext = base_img["ext"]
            filename = f"{prefix}{page_idx + 1}_img{img_idx}.{ext}"
            target_path = os.path.join(out_dir, filename)

            with open(target_path, "wb") as f:
                f.write(base_img["image"])

            extracted_count += 1
            print(f"  [+] Page {page_idx + 1} -> {filename} ({width}x{height}, {ext})")

    doc.close()
    return extracted_count


def main():
    parser = argparse.ArgumentParser(description="Extract embedded images from a PDF file.")
    parser.add_argument("pdf", help="Path to input PDF file")
    parser.add_argument("--out-dir", "-o", default=None, help="Directory to save extracted images (default: <pdf_stem>_images)")
    parser.add_argument("--min-width", type=int, default=20, help="Minimum image width to extract (default: 20)")
    parser.add_argument("--min-height", type=int, default=20, help="Minimum image height to extract (default: 20)")
    parser.add_argument("--prefix", default="p", help="Prefix for extracted image files (default: 'p')")
    args = parser.parse_args()

    pdf_path = os.path.abspath(args.pdf)
    if not os.path.isfile(pdf_path):
        sys.exit(f"PDF file not found: {pdf_path}")

    stem = os.path.splitext(os.path.basename(pdf_path))[0]
    out_dir = os.path.abspath(args.out_dir if args.out_dir else f"{stem}_images")

    print(f"Extracting images from '{os.path.basename(pdf_path)}' to '{out_dir}'...")
    count = extract_images(pdf_path, out_dir, args.min_width, args.min_height, args.prefix)
    print(f"\nDone. Extracted {count} image(s).")


if __name__ == "__main__":
    main()
