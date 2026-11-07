---
name: lab-assignment
description: >-
  Creates a complete university lab report / assignment as a Word (.docx) file
  in the user's fixed format: cover page with college logo, Lab Report heading,
  Experiment name, Objective, Theory, Conclusion, then each task as Question /
  Code / Output with small readable code screenshots and real output
  screenshots. Use when the user gives a lab manual or assignment (C++, HTML,
  CSS, JS, Bootstrap, EMU8086 assembly, or non-code) and wants the finished
  report.
---

# Lab Assignment Skill

Produces one `.docx` per assignment. Always follow this skill exactly; the user
has strict format rules.

All commands use `py` (Python 3.14 with python-docx, Pillow, Pygments).
**Do not use `python`** â€” on this machine it points to a different install
without these packages. Script folder: `.agents/skills/lab-assignment/scripts/`
(called `$S` below).

## Hard rules (never break)

1. **Cover page is always the same layout** (logo, department, institute, then 7 centered
   lines). Built by `build_report.py`; never hand-make it.
2. **No blue anywhere in headings.** All headings are black, bold. Never use Word
   `Heading` styles (they are blue).
3. **Writing style:** simple English, short sentences, minimal, no jargon. If a technical
   word is needed, explain it in plain words the first time. No fluffy filler.
4. **Code screenshots are many small images**, never one big one (about 12 lines each,
   with line numbers).
5. **Outputs are real**: run the code / open the page and screenshot the real result.
   Never invent output. If it cannot be run (e.g. EMU8086), leave a placeholder
   (`null` in `outputs`) and tell the user which screenshots they must paste.
6. Final deliverable is **.docx only** (no PDF unless asked).
7. **Borders:** every page has a thin black page border, and every code/output image has a black frame (built in by `build_report.py`).
8. **Wide images (CRITICAL - NEVER MAKE SMALL SCREENSHOTS):** Both code and output
   screenshots must stretch to the full page text width (6.5 to 6.7 in; margins are 0.9 in).
   **NEVER put output screenshots side-by-side in a table.** Side-by-side tables shrink
   images down to 2-3 inches, making browser UI, text, forms, and terminal runs completely
   unseeable and illegible. All output screenshots MUST be stacked vertically one below
   another (`output_layout: stack`), with each screenshot displayed at full width (6.5 to 6.7 in)
   and its descriptive caption placed directly underneath it. `code_dpi` in a task brings back
   natural (small) size, so avoid it.
9. **Squeeze rule:** if an image sits on a new page only because it is a little too tall for the previous page, shorten it vertically so it fits there. Only when the cut is small (max 12%, smallest cut that works). If it needs more than that, leave it full size. Done by `squeeze_images.py` after the build.
10. **Font and typography:** Always use **Times New Roman** throughout the entire document (cover page, headings, body text, lists). Keep all **headings at 16 pt (bold, black)** and all **normal text at 12 pt**. Heading and text must never be the same size.

## Report structure

Page 1 – Cover. Page 2 – report heading block. Next page – tasks.

```
Lab Report NN                (centered, bold, black, 16 pt, Times New Roman)
Experiment name:   <one line> (12 pt bold label, 12 pt text)
Objective:         <1-2 simple sentences> (12 pt)
Theory:            <3-6 short bullets, each starts with a **bold term**> (12 pt)
Conclusion:        <3-4 simple sentences: what was done, what result, what learned> (12 pt)

(new page)
Lab Tasks                    (bold, black heading, 16 pt, Times New Roman)
Lab Task N                   (bold, black heading, 16 pt)
<question text from manual (12 pt, not bold)>

Code:                        (12 pt, bold)
<small code screenshots, stacked>

Output:                      (12 pt, bold)
<screenshot(s)>
```

- Order is **Objective, then Theory** (as in the user's sample).
- Name for the heading comes from the manual: "Lab Report 04", "Assignment 2", etc.
  (`meta.report_title`).
- Theory should only cover what the tasks use. Plain words, e.g. "A loop repeats code
  many times" rather than "iterative control structure".
- Conclusion is written **after** the outputs are verified, and must match the real
  results.
- Non-code assignments: use `answer` (list of paragraphs; items starting with `- ` become
  bullets) instead of `code`/`outputs`. Omit `objective`/`theory`/`conclusion` or
  `experiment_name` if the manual does not call for them.

## Workflow

### 1. Read the manual and collect details
The user always supplies the lab manual (docx/pdf). From it get: course/subject name,
instructor name (**keep the title exactly as written, e.g. "Mam Unaiza", "Sir Ali",
"Dr. Sara"; if no title is given, ask**), lab/assignment number, experiment title,
tasks/questions.
Fixed details (student name, roll no, department, institute, semester, session) live in
`config/student.json` â€” do not ask for them again. Update that file only if the user
says they changed (e.g. new semester).
**Date of submission:** use the date the user gives; if none, ask. Format `DD-MM-YYYY`.
`assets/logo.png` is the college logo with a transparent background (already done). If a new logo is given, run `scripts/make_logo_transparent.py` on it first.

### 2. Do the tasks
Write each solution in its own source file in a working folder (e.g.
`<assignment>/src/q1.cpp`). Keep code simple, student-level, with short plain comments.
Read `.docx` manuals with python-docx.

### 3. Make code screenshots (small pieces)
```
py $S\code_to_images.py src\q1.cpp --out-dir build\code --prefix q1_code
```
Prints the image paths in order. Dark theme, line numbers continue across pieces. Use
`--lines 10` for wide/dense code, `--lang` to force a language. Supports C++, HTML, CSS,
JS, EMU8086 (`.asm`, uses nasm colours), Python, SQL, Java.

### 4. Make output screenshots (real)
- **C++ / C / Python / JS** â€“ compile + run, typing the inputs in order:
  ```
  py $S\run_program.py src\q1.cpp --out build\out\q1_out1.png --input 5 --input 10
  ```
  Run once per important test case (e.g. normal case, edge case). Inputs are echoed so it
  looks like a real console. Check the printed text is correct before using it.
- **HTML / CSS / JS / Bootstrap** â€“ real browser (headless Edge/Chrome):
  ```
  py $S\screenshot_web.py src\task1.html --out build\out\q1_desktop.png --width 1280 --height 800
  ```
  For responsive pages also take a phone view with `--mobile 440` (headless browsers cannot go narrower than ~500px, so this shows the page in a phone-width frame). Empty space at the bottom is trimmed automatically. For an opened hamburger menu, screenshot a temp copy with `show` added to the `collapse navbar-collapse` class. Make `--height`
  tall enough to show the whole page. Open the PNG and check it looks right (CDN files
  need internet). For interaction (click, dropdown open) use the browser tools instead and
  save the screenshot.
- **EMU8086** â€“ cannot be run here. Write and carefully hand-check the code, use
  `null` placeholders in `outputs`, and tell the user to paste the emulator screenshots.
  Only draw a simulated screen if the user explicitly asks.

### 5. Build the spec and the docx
Copy `examples/spec_example.json` and edit it. Keys:

| Key | Meaning |
|---|---|
| `output_file` | name of the .docx, e.g. `Lab_Report_04.docx` |
| `meta.report_title` | "Lab Report 04" |
| `meta.teacher`, `meta.subject`, `meta.date` | per course (cover page) |
| `meta.*` | any fixed field from student.json can be overridden |
| `experiment_name`, `objective`, `theory[]`, `conclusion` | text; `**bold**` and `` `code` `` allowed |
| `tasks[].question` | question text (builder adds "Question N:") |
| `tasks[].title` | optional, e.g. "Task 1" instead of "Question 1" |
| `tasks[].code[]` | image paths from step 3 |
| `tasks[].outputs[]` | image paths, `null` = placeholder, or `{"image":..,"caption":..,"width":inches}` |
| `tasks[].output_layout` | `stack` (default and required for all screenshots). Stacks every screenshot vertically at full width (6.5 to 6.7 in) with caption directly below |
| `tasks[].answer[]` | paragraphs for non-code questions |

Image paths are relative to the spec file. **Output layout rule:** ALL output screenshots
MUST be full width (6.5 to 6.7 in), stacked vertically (`output_layout: "stack"`). Never use
side-by-side tables for screenshots, even when a task has multiple test cases (e.g. initial,
interaction, error, success); stack each one full size so text and controls remain crisp
and clearly readable.

```
py $S\build_report.py build\spec.json
```

### 5b. Squeeze images (always run after building)
```
py -u $S\squeeze_images.py <file>.docx
```
Uses Word. Edits the docx in place; prints which images were shortened and by how much (max 12%). Close other Word windows first. It can take about a minute.

### 6. Check the result
```
py $S\preview_docx.py <file>.docx --out-dir build\preview
```
(needs Word + `py -m pip install pymupdf`). View the page PNGs and verify: cover looks
right and has the correct teacher/subject/date, no blue, no tiny unreadable images, no
big empty gaps, outputs match the conclusion. Fix and rebuild if needed. Delete scratch
folders (`_build_tmp`, `preview`) before handing over, and tell the user the final file
path plus any placeholders they must fill.

## Files
- `config/student.json` â€“ fixed student details
- `assets/logo.png` â€“ college logo (user supplies)
- `scripts/` â€“ `code_to_images.py`, `terminal_to_image.py`, `run_program.py`,
  `screenshot_web.py`, `build_report.py`, `squeeze_images.py`, `preview_docx.py`
- `examples/spec_example.json`, `examples/demo/task1.cpp` â€“ sample input

