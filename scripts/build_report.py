"""Build the final assignment .docx from a JSON spec.

Usage:
    py build_report.py spec.json

See ../examples/spec_example.json for the spec format and SKILL.md for rules.
"""
import json
import os
import re
import sys

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor
from PIL import Image, ImageOps

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BODY_FONT = "Times New Roman"
COVER_FONT = "Times New Roman"
BLACK = RGBColor(0, 0, 0)
PAGE_TEXT_WIDTH = 6.7   # inches usable between margins
MARKUP = re.compile(r"(\*\*.+?\*\*|`.+?`)")


# ---------- small helpers ----------
def set_font(run, name, size=None, bold=None, italic=None, color=BLACK):
    run.font.name = name
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    for attr in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rfonts.set(qn(attr), name)
    if size:
        run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold
    if italic is not None:
        run.italic = italic
    if color is not None:
        run.font.color.rgb = color


def add_marked_text(par, text, font=BODY_FONT, size=12):
    """Supports **bold** and `code` inside text."""
    for part in MARKUP.split(text):
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            set_font(par.add_run(part[2:-2]), font, size, bold=True)
        elif part.startswith("`") and part.endswith("`"):
            set_font(par.add_run(part[1:-1]), "Consolas", size - 1)
        else:
            set_font(par.add_run(part), font, size)


def para(doc_or_cell, text="", align=None, space_before=0, space_after=6,
         keep_next=False, line=1.15):
    p = doc_or_cell.add_paragraph()
    pf = p.paragraph_format
    pf.space_before, pf.space_after, pf.line_spacing = Pt(space_before), Pt(space_after), line
    pf.keep_with_next = keep_next
    if align is not None:
        p.alignment = align
    if text:
        add_marked_text(p, text)
    return p


def label(doc, text, size=12, space_before=8, space_after=3):
    p = para(doc, space_before=space_before, space_after=space_after, keep_next=True)
    set_font(p.add_run(text), BODY_FONT, size, bold=True)
    return p


def bullet(doc, text):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.15
    add_marked_text(p, text)
    return p


def page_break(doc):
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


def add_page_number_footer(section):
    section.different_first_page_header_footer = True
    p = section.footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    set_font(run, BODY_FONT, 9, color=RGBColor(0x59, 0x59, 0x59))
    for kind, text in (("begin", None), (None, "PAGE"), ("end", None)):
        if kind:
            el = OxmlElement("w:fldChar")
            el.set(qn("w:fldCharType"), kind)
        else:
            el = OxmlElement("w:instrText")
            el.set(qn("xml:space"), "preserve")
            el.text = text
        run._r.append(el)


def set_table_borders(table, color="BFBFBF", size=4):
    tblPr = table._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), str(size))
        el.set(qn("w:color"), color)
        borders.append(el)
    tblPr.append(borders)


def framed_copy(path, tmp_dir):
    """Add a thin grey frame around a screenshot so it looks tidy on white paper."""
    img = Image.open(path).convert("RGB")
    img = ImageOps.expand(img, border=3, fill=(0, 0, 0))
    os.makedirs(tmp_dir, exist_ok=True)
    out = os.path.join(tmp_dir, "f_" + os.path.basename(path))
    img.save(out)
    return out, img.size


# ---------- sections ----------
def build_cover(doc, meta):
    logo = meta["logo"]
    if not os.path.exists(logo):
        sys.exit(f"Logo not found: {logo}\nSave the college logo there (see SKILL.md).")
    p = para(doc, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=18)
    p.add_run().add_picture(logo, width=Inches(2.4))

    for text in (meta["department"], meta["institute"]):
        p = para(doc, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=10, space_after=10)
        set_font(p.add_run(text), COVER_FONT, 16, bold=True)

    rows = [
        ("Submitted By:", meta["student_name"]),
        ("Submitted To:", meta["teacher"]),
        ("Semester:", meta["semester"]),
        ("Session:", meta["session"]),
        ("Subject:", meta["subject"]),
        ("Roll no:", meta["roll_no"]),
        ("Date of submission:", meta["date"]),
    ]
    first = True
    for k, v in rows:
        p = para(doc, align=WD_ALIGN_PARAGRAPH.CENTER,
                 space_before=46 if first else 0, space_after=9)
        first = False
        set_font(p.add_run(k + " "), COVER_FONT, 12, bold=True)
        set_font(p.add_run(v), COVER_FONT, 12)


def build_intro(doc, spec):
    p = para(doc, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=12)
    set_font(p.add_run(spec["meta"]["report_title"]), BODY_FONT, 16, bold=True)

    if spec.get("experiment_name"):
        label(doc, "Experiment name:")
        para(doc, spec["experiment_name"], space_after=8)
    if spec.get("objective"):
        label(doc, "Objective:")
        para(doc, spec["objective"], space_after=8)
    if spec.get("theory"):
        label(doc, "Theory:")
        theory = spec["theory"]
        if isinstance(theory, str):
            para(doc, theory)
        else:
            for item in theory:
                bullet(doc, item)
    if spec.get("conclusion"):
        label(doc, "Conclusion:", space_before=14)
        para(doc, spec["conclusion"])


def add_image_par(doc, path, width_in, tmp_dir, space_after=4):
    out, (w, h) = framed_copy(path, tmp_dir)
    p = para(doc, align=WD_ALIGN_PARAGRAPH.LEFT, space_after=space_after, line=1.0)
    p.paragraph_format.keep_with_next = False
    p.add_run().add_picture(out, width=Inches(width_in))
    return p


def add_placeholder(container, text="[Paste output screenshot here]"):
    p = container.add_paragraph() if hasattr(container, "add_paragraph") else container
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_font(p.add_run(text), BODY_FONT, 10, italic=True, color=RGBColor(0x80, 0x80, 0x80))


def normalise_outputs(items):
    out = []
    for it in items or []:
        if it is None or it == "PLACEHOLDER":
            out.append({"image": None, "caption": None, "width": None})
        elif isinstance(it, str):
            out.append({"image": it, "caption": None, "width": None})
        else:
            out.append({"image": it.get("image"), "caption": it.get("caption"),
                        "width": it.get("width"), "placeholder": it.get("placeholder")})
    return out


def add_caption(doc, text):
    c = para(doc, align=WD_ALIGN_PARAGRAPH.LEFT, space_after=8)
    add_marked_text(c, text, size=9)


def add_single_output(doc, o, tmp_dir):
    if o["image"]:
        w, h = Image.open(o["image"]).size
        width = o["width"] or PAGE_TEXT_WIDTH  # full text width (6.7 in)
        add_image_par(doc, o["image"], width, tmp_dir)
        if o["caption"]:
            add_caption(doc, o["caption"])
    else:
        ph = o.get("placeholder") or "[Paste output screenshot here]"
        add_placeholder(doc, text=ph)
        if o.get("caption"):
            add_caption(doc, o["caption"])


def add_output_table(doc, outs, cols, tmp_dir):
    rows = -(-len(outs) // cols)
    table = doc.add_table(rows=rows, cols=cols)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table)
    cell_w = (PAGE_TEXT_WIDTH / cols) - 0.15
    for i, o in enumerate(outs):
        cell = table.cell(i // cols, i % cols)
        cp = cell.paragraphs[0]
        cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cp.paragraph_format.space_after = Pt(2)
        if o["image"]:
            out, _ = framed_copy(o["image"], tmp_dir)
            cp.add_run().add_picture(out, width=Inches(o["width"] or cell_w))
        else:
            add_placeholder(cp)
        if o["caption"]:
            c = cell.add_paragraph()
            c.alignment = WD_ALIGN_PARAGRAPH.CENTER
            add_marked_text(c, o["caption"], size=9)
    para(doc, space_after=4)


def build_outputs(doc, task, tmp_dir):
    raw = task.get("outputs") or []
    if not raw:
        return
    if task.get("output_new_page"):
        page_break(doc)
    label(doc, "Output:", space_before=14, space_after=6)
    outs = normalise_outputs(raw)
    layout = task.get("output_layout", "stack")  # default MUST be stack
    if layout == "table":
        cols = task.get("output_columns") or 2
        add_output_table(doc, outs, cols, tmp_dir)
        return
    # Default stack: all output screenshots full width, stacked vertically
    for o in outs:
        add_single_output(doc, o, tmp_dir)


def add_data_table(doc, tbl):
    if tbl.get("new_page"):
        doc.add_page_break()
    if tbl.get("title"):
        label(doc, tbl["title"], space_before=8, space_after=3)
    headers = tbl.get("headers", [])
    rows = tbl.get("rows", [])
    cols = len(headers)
    table = doc.add_table(rows=len(rows) + 1, cols=cols)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table, color="BFBFBF", size=4)

    trPr0 = table.rows[0]._tr.get_or_add_trPr()
    trPr0.append(OxmlElement("w:tblHeader"))

    for row in table.rows:
        rPr = row._tr.get_or_add_trPr()
        rPr.append(OxmlElement("w:cantSplit"))

    col_widths = tbl.get("col_widths")
    if col_widths and len(col_widths) == cols:
        table.autofit = False
        for row in table.rows:
            for idx, w in enumerate(col_widths):
                row.cells[idx].width = Inches(w)

    for i, h in enumerate(headers):
        c = table.rows[0].cells[i]
        c.text = ""
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.0
        set_font(p.add_run(h), BODY_FONT, 10, bold=True)
    for r_idx, row in enumerate(rows):
        for c_idx, val in enumerate(row):
            c = table.rows[r_idx + 1].cells[c_idx]
            c.text = ""
            p = c.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(1.5)
            p.paragraph_format.space_after = Pt(1.5)
            p.paragraph_format.line_spacing = 1.0
            set_font(p.add_run(str(val)), BODY_FONT, 9.5)
    para(doc, space_after=4)


def build_task(doc, n, task, tmp_dir, new_page=False):
    q_text = task["question"].strip()
    m = re.match(r"^((?:lab\s+)?(?:question|task|exercise|activity)\s*\d*)\s*[:.]\s*(.*)", q_text, re.I | re.S)
    if m:
        q_text = m.group(2).strip()
    raw_title = task.get("title", f"Question {n}")
    prefix = raw_title.strip()

    hp = para(doc, space_before=6 if n == 1 else 16, space_after=4, keep_next=True)
    hp.paragraph_format.page_break_before = new_page
    set_font(hp.add_run(prefix), BODY_FONT, 16, bold=True)          # heading at 16pt, bold
    if q_text:
        qp = para(doc, space_before=0, space_after=8, keep_next=True)
        set_font(qp.add_run(q_text), BODY_FONT, 12, bold=False)     # normal question text at 12pt

    if task.get("answer"):
        for item in task["answer"]:
            if item.startswith("- "):
                bullet(doc, item[2:])
            else:
                para(doc, item)
    if task.get("code"):
        label(doc, "Code:", space_before=8, space_after=4)
        code_list = task["code"]
        dpi = float(task.get("code_dpi", 210.0))
        for idx, path in enumerate(code_list):
            img_w, _ = Image.open(path).size
            code_w = task.get("code_width") or (min(img_w / dpi, PAGE_TEXT_WIDTH) if task.get("code_dpi") else PAGE_TEXT_WIDTH)
            after_space = 10 if idx == len(code_list) - 1 else 2
            add_image_par(doc, path, code_w, tmp_dir, space_after=after_space)
    build_outputs(doc, task, tmp_dir)
    if task.get("table"):
        tables = task["table"] if isinstance(task["table"], list) else [task["table"]]
        for tbl in tables:
            add_data_table(doc, tbl)
    if task.get("after"):
        for item in task["after"]:
            if isinstance(item, dict) and "headers" in item:
                add_data_table(doc, item)
            elif isinstance(item, str):
                if item.startswith("- "):
                    bullet(doc, item[2:])
                elif item.startswith("## "):
                    label(doc, item[3:])
                else:
                    para(doc, item)


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    spec_path = os.path.abspath(sys.argv[1])
    base = os.path.dirname(spec_path)
    spec = json.load(open(spec_path, encoding="utf-8-sig"))

    cfg_path = os.path.join(SKILL_DIR, "config", "student.json")
    meta = json.load(open(cfg_path, encoding="utf-8"))
    cfg_dir = os.path.dirname(cfg_path)
    meta["logo"] = os.path.normpath(os.path.join(cfg_dir, meta["logo"]))
    meta.update(spec["meta"])
    if not os.path.isabs(meta["logo"]):
        meta["logo"] = os.path.normpath(os.path.join(base, meta["logo"]))
    spec["meta"] = meta

    # make image paths relative to the spec file
    def fix(p):
        return p if (p is None or os.path.isabs(p)) else os.path.normpath(os.path.join(base, p))

    def fix_item(o):
        if isinstance(o, list):
            return [fix_item(x) for x in o]
        if isinstance(o, str):
            return o if o == "PLACEHOLDER" else fix(o)
        if isinstance(o, dict):
            return {**o, "image": fix(o.get("image"))}
        return o

    for t in spec.get("tasks", []):
        t["code"] = [fix(p) for p in t.get("code", [])]
        t["outputs"] = [fix_item(o) for o in t.get("outputs", []) or []]

    doc = Document()
    sec = doc.sections[0]
    sec.left_margin = sec.right_margin = Inches(0.9)
    sec.top_margin = sec.bottom_margin = Inches(1)
    normal = doc.styles["Normal"]
    normal.font.name = BODY_FONT
    normal.font.size = Pt(12)
    normal.element.rPr.rFonts.set(qn("w:eastAsia"), BODY_FONT)
    doc.styles["List Bullet"].font.name = BODY_FONT
    doc.styles["List Bullet"].font.size = Pt(12)

    add_page_number_footer(sec)
    # black border around every page
    pg = OxmlElement("w:pgBorders")
    pg.set(qn("w:offsetFrom"), "page")
    for edge in ("top", "left", "bottom", "right"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "8")
        el.set(qn("w:space"), "24")
        el.set(qn("w:color"), "000000")
        pg.append(el)
    sec._sectPr.find(qn("w:pgMar")).addnext(pg)
    tmp_dir = os.path.join(base, "_build_tmp")

    build_cover(doc, meta)
    page_break(doc)
    build_intro(doc, spec)
    tasks = spec.get("tasks", [])
    if tasks:
        hp = para(doc, space_before=0, space_after=10, keep_next=True)
        hp.paragraph_format.page_break_before = True
        set_font(hp.add_run(spec.get("tasks_heading", "Lab Tasks")), BODY_FONT, 16, bold=True)
    for i, task in enumerate(tasks, start=1):
        new_page = bool(task.get("new_page", False)) if i > 1 else False
        build_task(doc, task.get("number", i), task, tmp_dir, new_page=new_page)

    out = spec.get("output_file", "assignment.docx")
    out = out if os.path.isabs(out) else os.path.join(base, out)
    doc.save(out)
    print("Saved:", out)


if __name__ == "__main__":
    main()


