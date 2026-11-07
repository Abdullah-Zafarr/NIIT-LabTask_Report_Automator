"""Preview a .docx as page images (needs Microsoft Word + pymupdf).

Usage:
    py preview_docx.py report.docx [--out-dir preview] [--dpi 80]

Install once if missing:  py -m pip install pymupdf
Look at the PNGs to check layout (cover page, page breaks, image sizes).
"""
import argparse
import os

import fitz  # pymupdf
import win32com.client


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("docx")
    ap.add_argument("--out-dir", default="preview")
    ap.add_argument("--dpi", type=int, default=80)
    args = ap.parse_args()

    docx = os.path.abspath(args.docx)
    out_dir = os.path.abspath(args.out_dir)
    os.makedirs(out_dir, exist_ok=True)
    pdf = os.path.join(out_dir, "preview.pdf")

    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    try:
        doc = word.Documents.Open(docx, ReadOnly=True)
        doc.ExportAsFixedFormat(pdf, 17)   # 17 = PDF
        doc.Close(False)
    finally:
        word.Quit()

    pages = fitz.open(pdf)
    for i, page in enumerate(pages, start=1):
        page.get_pixmap(dpi=args.dpi).save(os.path.join(out_dir, f"page_{i}.png"))
    print(f"{len(pages)} pages -> {out_dir}")


if __name__ == "__main__":
    main()
