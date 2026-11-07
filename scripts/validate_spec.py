"""Pre-flight validator for lab assignment specification files.

Verifies schema validity, checks for required metadata, and confirms
that referenced code and output images exist on disk before compilation.
"""

import argparse
import json
import os
import sys

REQUIRED_META_KEYS = ["report_title", "teacher", "subject", "date"]


def validate_spec(spec_path):
    """Validate a specification JSON file against lab report rules."""
    errors = []
    warnings = []

    if not os.path.isfile(spec_path):
        return [f"Specification file not found: {spec_path}"], []

    try:
        with open(spec_path, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        return [f"Malformed JSON in {spec_path}: {exc}"], []

    spec_dir = os.path.dirname(os.path.abspath(spec_path))

    # Top-level required keys
    if "output_file" not in data or not str(data["output_file"]).strip():
        errors.append("Missing or empty 'output_file' key.")
    elif not str(data["output_file"]).lower().endswith(".docx"):
        warnings.append("Property 'output_file' should end with '.docx'.")

    if "meta" not in data or not isinstance(data["meta"], dict):
        errors.append("Missing or invalid 'meta' dictionary.")
    else:
        meta = data["meta"]
        for key in REQUIRED_META_KEYS:
            if key not in meta or not str(meta[key]).strip():
                errors.append(f"Missing or empty meta field: 'meta.{key}'")

    tasks = data.get("tasks")
    if not isinstance(tasks, list) or len(tasks) == 0:
        errors.append("'tasks' must be a non-empty list.")
    else:
        for idx, task in enumerate(tasks, start=1):
            if not isinstance(task, dict):
                errors.append(f"Task #{idx} must be a dictionary object.")
                continue

            q = task.get("question")
            if not q or not str(q).strip():
                errors.append(f"Task #{idx} has missing or empty 'question' text.")

            has_code = bool(task.get("code"))
            has_outputs = bool(task.get("outputs"))
            has_answer = bool(task.get("answer"))

            if not (has_code or has_outputs or has_answer):
                errors.append(f"Task #{idx} has no 'code', 'outputs', or 'answer' defined.")

            # Check code image files
            for c_path in task.get("code", []):
                full_c = os.path.normpath(os.path.join(spec_dir, c_path))
                if not os.path.isfile(full_c):
                    errors.append(f"Task #{idx}: code image not found -> {c_path}")

            # Check output image files
            for out_entry in task.get("outputs", []):
                if out_entry is None:
                    continue  # Null placeholder allowed
                rel_path = out_entry.get("image") if isinstance(out_entry, dict) else out_entry
                if rel_path:
                    full_o = os.path.normpath(os.path.join(spec_dir, rel_path))
                    if not os.path.isfile(full_o):
                        errors.append(f"Task #{idx}: output image not found -> {rel_path}")

    return errors, warnings


def main():
    parser = argparse.ArgumentParser(description="Validate assignment spec.json before build.")
    parser.add_argument("spec", help="Path to specification JSON file")
    args = parser.parse_args()

    errors, warnings = validate_spec(args.spec)

    for w in warnings:
        print(f"[WARN] {w}")

    if errors:
        print(f"\n[FAIL] Validation failed with {len(errors)} error(s):")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    print(f"[OK] Specification '{args.spec}' is valid.")
    sys.exit(0)


if __name__ == "__main__":
    main()
