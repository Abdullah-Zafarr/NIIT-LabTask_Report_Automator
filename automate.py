#!/usr/bin/env python3
"""Unified CLI orchestrator for NIIT Lab Task & Report Automator.

Provides a single command-line interface to validate specifications,
slice code into numbered blocks, build formatted .docx reports,
optimize image heights via COM, and render inspection previews.
"""

import argparse
import os
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")


def run_cmd(cmd):
    """Run a Python script via current interpreter, relaying output."""
    res = subprocess.run([sys.executable] + cmd)
    return res.returncode == 0


def cmd_validate(args):
    """Run specification validation."""
    validator = os.path.join(SCRIPTS_DIR, "validate_spec.py")
    return 0 if run_cmd([validator, args.spec]) else 1


def cmd_build(args):
    """Build Word report, with optional squeeze and preview steps."""
    builder = os.path.join(SCRIPTS_DIR, "build_report.py")
    print(f"--> Building report from '{args.spec}'...")
    if not run_cmd([builder, args.spec]):
        print("[ERROR] Build failed.")
        return 1

    # Extract output file path if possible
    import json
    try:
        with open(args.spec, "r", encoding="utf-8-sig") as f:
            spec_data = json.load(f)
        spec_dir = os.path.dirname(os.path.abspath(args.spec))
        docx_path = os.path.join(spec_dir, spec_data.get("output_file", "output.docx"))
    except Exception:
        docx_path = None

    if args.squeeze and docx_path and os.path.isfile(docx_path):
        print(f"\n--> Running Word COM image squeezer on '{docx_path}'...")
        squeezer = os.path.join(SCRIPTS_DIR, "squeeze_images.py")
        run_cmd(["-u", squeezer, docx_path])

    if args.preview and docx_path and os.path.isfile(docx_path):
        print(f"\n--> Generating page previews for '{docx_path}'...")
        previewer = os.path.join(SCRIPTS_DIR, "preview_docx.py")
        preview_dir = os.path.join(os.path.dirname(docx_path), "preview")
        run_cmd([previewer, docx_path, "--out-dir", preview_dir])

    print("\n[OK] Pipeline completed successfully.")
    return 0


def cmd_code(args):
    """Slice source code file into highlighted images."""
    slicer = os.path.join(SCRIPTS_DIR, "code_to_images.py")
    cmd = [slicer, args.file, "--out-dir", args.out_dir]
    if args.prefix:
        cmd.extend(["--prefix", args.prefix])
    if args.lines:
        cmd.extend(["--lines", str(args.lines)])
    if args.lang:
        cmd.extend(["--lang", args.lang])
    return 0 if run_cmd(cmd) else 1


def main():
    parser = argparse.ArgumentParser(
        prog="automate.py",
        description="NIIT Lab Task & Report Automator CLI",
    )
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    # validate
    p_val = subparsers.add_parser("validate", help="Validate a spec.json file")
    p_val.add_argument("spec", help="Path to specification JSON file")
    p_val.set_defaults(func=cmd_validate)

    # build
    p_bld = subparsers.add_parser("build", help="Build Word (.docx) report from spec.json")
    p_bld.add_argument("spec", help="Path to specification JSON file")
    p_bld.add_argument("--squeeze", action="store_true", help="Run image height squeezer via Word COM")
    p_bld.add_argument("--preview", action="store_true", help="Generate PNG page previews")
    p_bld.set_defaults(func=cmd_build)

    # code
    p_code = subparsers.add_parser("code", help="Slice code into syntax-highlighted images")
    p_code.add_argument("file", help="Path to source code file")
    p_code.add_argument("--out-dir", default="build/code", help="Output directory for generated images")
    p_code.add_argument("--prefix", help="Image filename prefix")
    p_code.add_argument("--lines", type=int, default=12, help="Lines per image chunk")
    p_code.add_argument("--lang", help="Override Pygments lexer language")
    p_code.set_defaults(func=cmd_code)

    args = parser.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
