# Contributing to NIIT Lab Task & Report Automator

We welcome contributions from NIIT students, faculty, and developers. Follow these guidelines to submit improvements, fix formatting issues, or add language support.

---

## Areas for Contribution

1. **New Language Syntax Support**: Add Pygments lexers or style overrides to `scripts/code_to_images.py`.
2. **Course Templates**: Expand `examples/` with course-specific task examples (e.g. Operating Systems, Computer Networks, Database Systems).
3. **Execution Environments**: Add support for compilers or simulators (e.g. GCC, Clang, NASM, Node.js).
4. **Layout & Typography Refinements**: Optimize `.docx` table borders, margin formulas, or image scaling in `scripts/build_report.py`.

---

## Development Workflow

### 1. Setup Local Environment

Fork the repository, clone your fork, and install dependencies:

```powershell
git clone https://github.com/<your-username>/NIIT-LabTask_Report_Automator.git
cd NIIT-LabTask_Report_Automator
pip install -r requirements.txt
```

### 2. Verify Pre-Existing Scripts

Before making changes, verify that the CLI runs cleanly:

```powershell
py automate.py --help
py scripts/validate_spec.py examples/spec_example.json
```

### 3. Making Changes

- Keep pull requests focused on a single feature or bugfix.
- Follow Python PEP 8 style conventions (4-space indentation, clear variable names).
- Never commit personal credentials, student roll numbers, or submission dates into template files.

### 4. Testing Your Changes

Run a test compilation to verify `.docx` generation:

```powershell
py automate.py validate examples/spec_example.json
```

### 5. Submitting a Pull Request

1. Create a feature branch: `git checkout -b feature/new-language-support`
2. Commit your changes with concise, descriptive commit messages.
3. Push to your branch and open a Pull Request against `main`.

---

## Code of Conduct

Maintain respectful, collaborative communication. All academic integrity rules of NASTP Institute of Information Technology apply.
