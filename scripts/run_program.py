"""Compile + run a program for real, feed it inputs, and make an output screenshot.

Usage:
    py run_program.py <source.cpp|.c|.py|.js> --out out.png
                      [--input "5" --input "10" ...] [--title "Output"]
                      [--text-out out.txt] [--timeout 10]

Inputs are typed in one at a time whenever the program stops and waits, and
they are echoed in the transcript, so the picture looks like a real session.
"""
import argparse
import os
import queue
import subprocess
import sys
import tempfile
import threading
import time

sys.path.insert(0, os.path.dirname(__file__))
from terminal_to_image import render  # noqa: E402


def build_command(src, workdir):
    ext = os.path.splitext(src)[1].lower()
    if ext in (".cpp", ".cc", ".c"):
        exe = os.path.join(workdir, "prog.exe")
        compiler = "g++" if ext != ".c" else "gcc"
        flags = ["-std=c++17"] if ext != ".c" else []
        r = subprocess.run([compiler, *flags, src, "-o", exe], capture_output=True, text=True)
        if r.returncode != 0:
            sys.exit("COMPILE ERROR:\n" + r.stderr)
        return [exe]
    if ext == ".py":
        return ["py", src]
    if ext == ".js":
        return ["node", src]
    sys.exit(f"Unsupported file type: {ext}")


def run(cmd, inputs, timeout, idle=0.5):
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, bufsize=0)
    q = queue.Queue()

    def reader():
        while True:
            data = proc.stdout.read(1024)
            if not data:
                q.put(None)
                return
            q.put(data)

    threading.Thread(target=reader, daemon=True).start()
    transcript, remaining = "", list(inputs)
    deadline = time.time() + timeout
    finished = False
    while time.time() < deadline:
        try:
            chunk = q.get(timeout=idle)
        except queue.Empty:
            # program is waiting -> type the next input
            if remaining and proc.poll() is None:
                line = remaining.pop(0)
                transcript += line + "\n"
                try:
                    proc.stdin.write((line + "\n").encode())
                    proc.stdin.flush()
                except OSError:
                    pass
                continue
            if proc.poll() is not None:
                continue
            break  # waiting for input we do not have
        if chunk is None:
            finished = True
            break
        transcript += chunk.decode("utf-8", errors="replace").replace("\r\n", "\n")
    if not finished:
        proc.kill()
        transcript += "\n[stopped: program was still waiting for input or running]"
    return transcript


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("--out", required=True)
    ap.add_argument("--input", action="append", default=[])
    ap.add_argument("--title", default="Output")
    ap.add_argument("--text-out")
    ap.add_argument("--timeout", type=float, default=15)
    args = ap.parse_args()

    with tempfile.TemporaryDirectory() as tmp:
        cmd = build_command(os.path.abspath(args.source), tmp)
        text = run(cmd, args.input, args.timeout)

    if args.text_out:
        open(args.text_out, "w", encoding="utf-8").write(text)
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    render(text if text.strip() else "(no output)", args.title).save(args.out)
    print(text)
    print("->", os.path.abspath(args.out))


if __name__ == "__main__":
    main()
