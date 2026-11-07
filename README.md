# NIIT Lab Task & Report Automator

[![Python 3.14+](https://img.shields.io/badge/Python-3.14%2B-blue.svg)](https://www.python.org/)
[![Document Format](https://img.shields.io/badge/Output-Word%20(.docx)-2b579a.svg)](https://github.com/Abdullah-Zafarr/NIIT-LabTask_Report_Automator)
[![Format Standard](https://img.shields.io/badge/University-NIIT%20Compliant-darkred.svg)](https://github.com/Abdullah-Zafarr/NIIT-LabTask_Report_Automator)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An end-to-end automation engine built for NASTP Institute of Information Technology (NIIT) coursework. It solves lab tasks, captures live terminal and browser outputs, slices syntax-highlighted code into readable chunks, and compiles standardized `.docx` university lab reports.

---

## Key Features

- **Automated Task Execution**: Compiles and executes C, C++, Python, and JavaScript scripts while echoing interactive inputs into clean console images.
- **Headless Browser Capture**: Uses headless Chromium/Edge to render HTML, CSS, JavaScript, and Bootstrap pages in desktop (1280px) and phone (440px) viewports with auto-trimmed whitespace.
- **Readable Code Chunking**: Slices source code into numbered, syntax-highlighted dark-mode blocks (~12 lines each) stretched to the full page text width (6.5–6.7 in).
- **Strict NIIT Document Formatting**:
  - Exact university cover page with institutional logo and metadata hierarchy.
  - Times New Roman typography throughout (16 pt bold black headings, 12 pt body text).
  - Page-bordered layout with framed code and output figures.
  - Zero Word default styles (no blue headings).
- **COM-Based Image Squeezer**: Adjusts image heights via Microsoft Word COM automation (up to 12% vertical squeeze) to prevent single-figure trailing page overflows.
- **Fast Page Preview**: Converts rendered `.docx` pages into PNG previews via PyMuPDF for quick visual inspection before submission.

---

## Project Structure

```text
.
├── assets/
│   ├── logo.png             # Official university transparent logo
│   └── README.md            # Asset guidance and notes
├── config/
│   └── student.json         # Fixed student metadata (name, roll no, department, etc.)
├── examples/
│   ├── spec_example.json    # Sample assignment specification
│   └── demo/
│       └── task1.cpp        # Sample task solution
├── scripts/
│   ├── _common.py           # Shared path and configuration helpers
│   ├── build_report.py      # Core Word (.docx) report generation engine
│   ├── code_to_images.py    # Syntax-highlighted code chunk renderer
│   ├── make_logo_transparent.py # Logo alpha channel processor
│   ├── preview_docx.py      # DOCX to PNG page inspection renderer
│   ├── run_program.py       # Code execution runner and console grabber
│   ├── screenshot_web.py    # Headless browser web page renderer
│   ├── squeeze_images.py    # Word COM-based image height optimizer
│   └── terminal_to_image.py # Terminal output snapshot renderer
├── SKILL.md                 # Agent orchestration instruction set
└── README.md                # Project documentation
```

---

## Prerequisites

- **OS**: Windows 10 / 11 (required for MS Word COM automation)
- **Python**: Python 3.14+ (or Python 3.10+ with the following packages)
- **Microsoft Word**: Installed desktop version (for `.docx` squeezing and final rendering)

### Python Dependencies

```powershell
pip install python-docx Pillow pygments pymupdf
```

---

## Configuration

### 1. Student Metadata (`config/student.json`)

Set your default academic credentials once. The build engine injects these into every cover page:

```json
{
  "student_name": "Abdullah Zafar",
  "roll_no": "F2025CS014",
  "department": "Department of Computer Science",
  "institute": "NASTP Institute of Information Technology",
  "semester": "III",
  "session": "Fall – 2025 to 2029",
  "logo": "../assets/logo.png"
}
```

### 2. Assignment Specification (`spec.json`)

Each assignment uses a declarative JSON specification describing the experiment metadata, theory, and tasks:

```json
{
  "output_file": "Lab_Report_04.docx",
  "meta": {
    "report_title": "Lab Report 04",
    "teacher": "Mam Unaiza",
    "subject": "Data Structures & Algorithms",
    "date": "19-10-2026"
  },
  "experiment_name": "Even and Odd Numbers and Loops in C++",
  "objective": "To implement and analyze control structures and iterative logic in C++.",
  "theory": [
    "**Function:** A reusable subprogram designed to perform a distinct computation.",
    "**Iteration:** Repeating statements until a termination condition evaluates to false."
  ],
  "conclusion": "The program executed as expected across all test cases.",
  "tasks": [
    {
      "question": "Write a C++ program that checks if a number is even or odd.",
      "code": ["code/q1_code_01.png", "code/q1_code_02.png"],
      "outputs": ["out/q1_out.png"],
      "output_layout": "stack"
    }
  ]
}
```

---

## Step-by-Step Workflow

### Step 1: Write Task Solutions

Place source code in your assignment workspace (e.g. `src/q1.cpp`, `src/index.html`).

### Step 2: Render Syntax-Highlighted Code Images

Split code into readable, framed blocks:

```powershell
py scripts/code_to_images.py src/q1.cpp --out-dir build/code --prefix q1_code
```

Supports C, C++, HTML, CSS, JavaScript, Python, Java, SQL, and EMU8086 Assembly (`.asm`).

### Step 3: Capture Verified Execution Outputs

**For CLI Programs (C++, C, Python):**
```powershell
py scripts/run_program.py src/q1.cpp --out build/out/q1_out1.png --input 5 --input 10
```

**For Web Pages (HTML, CSS, Bootstrap):**
```powershell
# Desktop viewport
py scripts/screenshot_web.py src/task1.html --out build/out/q1_desktop.png --width 1280 --height 800

# Mobile viewport (phone frame)
py scripts/screenshot_web.py src/task1.html --out build/out/q1_mobile.png --mobile 440
```

### Step 4: Compile the University Report

Generate the `.docx` report with cover page, headings, borders, and structured tasks:

```powershell
py scripts/build_report.py build/spec.json
```

### Step 5: Optimize Image Sizing (Squeeze)

Eliminate trailing single-image page breaks automatically:

```powershell
py -u scripts/squeeze_images.py build/Lab_Report_04.docx
```

### Step 6: Visual Inspection Preview

Convert the document pages to high-resolution PNG images for rapid verification:

```powershell
py scripts/preview_docx.py build/Lab_Report_04.docx --out-dir build/preview
```

---

## Script Reference

| Script | Purpose |
|---|---|
| `build_report.py` | Compiles `.docx` document from `spec.json` and `student.json`. |
| `code_to_images.py` | Generates numbered, syntax-highlighted code images. |
| `run_program.py` | Compiles and executes native binaries, capturing console output. |
| `screenshot_web.py` | Renders HTML files inside headless Chromium/Edge browsers. |
| `terminal_to_image.py` | Renders arbitrary terminal text into styled console images. |
| `squeeze_images.py` | Connects to MS Word COM API to eliminate minor image overflows. |
| `preview_docx.py` | Exports `.docx` pages as raster images for instant validation. |
| `make_logo_transparent.py` | Converts opaque background images into transparent PNG assets. |
| `_common.py` | Core constants, font definitions, and path resolvers. |

---

## Academic Integrity & Standards

This toolkit guarantees compliance with departmental submission guidelines:
- **No Side-by-Side Images**: All screenshots stack vertically at full document width (6.5 in) with descriptive captions.
- **Real Output Only**: Code runs live during build time; no fabricated console outputs.
- **Neutral Heading Palette**: Strictly black `#000000` text across all structural headings.

---

## Author

**Abdullah Zafar**  
NASTP Institute of Information Technology (NIIT)  
Department of Computer Science  
GitHub: [@Abdullah-Zafarr](https://github.com/Abdullah-Zafarr)
