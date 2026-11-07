"""Squeeze images slightly (max 12%) in height when that lets them stay on the previous page.
Usage: py -u squeeze_images.py report.docx [max_percent]
Uses Word (COM). Edits the file in place. Never shrinks more than max_percent."""
import sys, os, win32com.client


def page(doc, pos):
    return doc.Range(pos, pos).Information(3)  # wdActiveEndPageNumber


def main():
    path = os.path.abspath(sys.argv[1])
    max_pct = float(sys.argv[2]) if len(sys.argv) > 2 else 12.0
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


main()
