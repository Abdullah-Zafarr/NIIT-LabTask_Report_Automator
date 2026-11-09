"""Inspect paragraphs, font formatting, tables, and images in a Word (.docx) document.

Usage:
    py inspect_docx.py document.docx
    py inspect_docx.py document.docx --tables-only
    py inspect_docx.py document.docx --paragraphs-only
"""

import argparse
import os
import sys

try:
    import docx
except ImportError:
    sys.exit("Missing python-docx dependency. Install via: py -m pip install python-docx")


def inspect(docx_path, show_paragraphs=True, show_tables=True):
    doc = docx.Document(docx_path)

    if show_paragraphs:
        print("=== PARAGRAPHS ===")
        printed_count = 0
        for i, p in enumerate(doc.paragraphs):
            runs_info = " | ".join(
                [f"'{r.text}' (b={r.bold}, size={r.font.size.pt if r.font.size else 'default'})" for r in p.runs if r.text]
            )
            imgs = [r for r in p.runs if "drawing" in getattr(r._r, "xml", "")]
            img_str = f" [IMAGES: {len(imgs)}]" if imgs else ""
            if p.text.strip() or imgs:
                print(f"P{i:02d}: '{p.text}'{img_str}")
                if runs_info and len(p.runs) > 1:
                    print(f"     Runs: {runs_info}")
                printed_count += 1
        print(f"Total non-empty paragraphs: {printed_count} (out of {len(doc.paragraphs)})")

    if show_tables:
        print("\n=== TABLES ===")
        print(f"Total tables: {len(doc.tables)}")
        for t_idx, table in enumerate(doc.tables):
            print(f"\n--- Table {t_idx + 1} ({len(table.rows)} rows x {len(table.columns)} cols) ---")
            for r_idx, row in enumerate(table.rows):
                row_cells = []
                for cell in row.cells:
                    cell_imgs = [r for p in cell.paragraphs for r in p.runs if "drawing" in getattr(r._r, "xml", "")]
                    img_note = f" (+{len(cell_imgs)} img)" if cell_imgs else ""
                    row_cells.append(cell.text.strip().replace("\n", " ") + img_note)
                print(f"  Row {r_idx + 1}: {' | '.join(row_cells)}")


def main():
    parser = argparse.ArgumentParser(description="Inspect paragraphs, runs, tables, and images in a Word document.")
    parser.add_argument("docx", help="Path to input Word (.docx) document")
    parser.add_argument("--paragraphs-only", action="store_true", help="Only show paragraphs")
    parser.add_argument("--tables-only", action="store_true", help="Only show tables")
    args = parser.parse_args()

    docx_path = os.path.abspath(args.docx)
    if not os.path.isfile(docx_path):
        sys.exit(f"Word document not found: {docx_path}")

    show_p = not args.tables_only
    show_t = not args.paragraphs_only
    inspect(docx_path, show_paragraphs=show_p, show_tables=show_t)


if __name__ == "__main__":
    main()
