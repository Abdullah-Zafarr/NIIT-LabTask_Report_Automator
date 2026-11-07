"""Screenshot an HTML page with headless Edge/Chrome (real browser output).

Usage:
    py screenshot_web.py <page.html | http-url> --out shot.png
                         [--width 1280] [--height 800] [--wait 3000]

Tip: for long pages, run once with a bigger --height, or several times with
different widths (e.g. 1280 for desktop, 420 for mobile) to show responsiveness.
"""
import argparse
import os
import pathlib
import subprocess
import sys

BROWSERS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("page")
    ap.add_argument("--out", required=True)
    ap.add_argument("--width", type=int, default=1280)
    ap.add_argument("--height", type=int, default=800)
    ap.add_argument("--wait", type=int, default=3000, help="ms to let CDN files/JS load")
    ap.add_argument("--mobile", type=int, default=0, metavar="PX",
                    help="show the page inside a phone-width frame (e.g. 400). Headless "
                         "browsers cannot go below ~500px wide, so a frame is used instead")
    ap.add_argument("--no-trim", action="store_true", help="keep empty white space at the bottom")
    args = ap.parse_args()

    browser = next((b for b in BROWSERS if os.path.exists(b)), None)
    if not browser:
        sys.exit("No Edge/Chrome found.")
    if args.page.startswith("http"):
        url = args.page
    elif "?" in args.page:
        fpart, qpart = args.page.split("?", 1)
        url = pathlib.Path(os.path.abspath(fpart)).as_uri() + "?" + qpart
    else:
        url = pathlib.Path(os.path.abspath(args.page)).as_uri()
    out = os.path.abspath(args.out)
    wrapper = None
    if args.mobile:
        wrapper = out + ".frame.html"
        with open(wrapper, "w", encoding="utf-8") as f:
            f.write(f'<body style="margin:0;background:#fff"><iframe src="{url}" '
                    f'style="width:{args.mobile}px;height:{args.height}px;border:0;'
                    f'display:block;margin:0 auto"></iframe></body>')
        url = pathlib.Path(wrapper).as_uri()
        args.width = max(args.width, args.mobile + 4)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    profile = os.path.join(os.environ.get("TEMP", "."), "lab_shot_profile")
    cmd = [browser, "--headless=new", "--disable-gpu", "--hide-scrollbars",
           f"--user-data-dir={profile}", f"--screenshot={out}",
           f"--window-size={args.width},{args.height}",
           f"--virtual-time-budget={args.wait}", url]
    subprocess.run(cmd, capture_output=True, timeout=90)
    if not os.path.exists(out):
        sys.exit("Screenshot failed.")
    if wrapper:
        os.remove(wrapper)
        from PIL import Image
        img = Image.open(out)
        left = (img.width - args.mobile) // 2
        img.crop((left, 0, left + args.mobile, img.height)).save(out)
    if not args.no_trim:
        from PIL import Image, ImageChops
        img = Image.open(out).convert("RGB")
        bg = img.getpixel((img.width - 1, img.height - 1))   # page background colour
        diff = ImageChops.difference(img, Image.new("RGB", img.size, bg))
        box = diff.getbbox()
        if box:
            img.crop((0, 0, img.width, min(img.height, box[3] + 24))).save(out)
    print(out)


if __name__ == "__main__":
    main()
