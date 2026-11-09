"""Extract all embedded images and media from a Word (.docx) document.

Usage:
    py extract_docx_media.py document.docx [--out-dir media]
"""

import argparse
import os
import sys
import zipfile


def extract_docx_media(docx_path, out_dir):
    if not os.path.isfile(docx_path):
        sys.exit(f"Word document not found: {docx_path}")

    os.makedirs(out_dir, exist_ok=True)
    count = 0

    with zipfile.ZipFile(docx_path, "r") as z:
        for name in z.namelist():
            if name.startswith("word/media/"):
                fname = os.path.basename(name)
                if not fname:
                    continue
                target = os.path.join(out_dir, fname)
                with open(target, "wb") as f:
                    f.write(z.read(name))
                count += 1
                info = z.getinfo(name)
                print(f"  [+] Extracted: {fname} ({info.file_size:,} bytes)")

    return count


def main():
    parser = argparse.ArgumentParser(description="Extract embedded images/media from a Word (.docx) document.")
    parser.add_argument("docx", help="Path to input Word (.docx) document")
    parser.add_argument("--out-dir", "-o", default=None, help="Directory to save extracted media (default: <docx_stem>_media)")
    args = parser.parse_args()

    docx_path = os.path.abspath(args.docx)
    stem = os.path.splitext(os.path.basename(docx_path))[0]
    out_dir = os.path.abspath(args.out_dir if args.out_dir else f"{stem}_media")

    print(f"Extracting media from '{os.path.basename(docx_path)}' to '{out_dir}'...")
    total = extract_docx_media(docx_path, out_dir)
    print(f"\nDone. Extracted {total} media file(s).")


if __name__ == "__main__":
    main()
