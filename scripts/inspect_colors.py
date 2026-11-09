"""Inspect pixel colors, dimensions, and background tone of images.

Usage:
    py inspect_colors.py <image_path_or_dir> [more_paths ...]
    py inspect_colors.py ./assets --sample-offset 5
    py inspect_colors.py preview/*.png --json
"""

import argparse
import glob
import json
import os
import sys

import numpy as np
from PIL import Image


def inspect_image(path, sample_offset=5):
    """Analyze dimensions, corner colors, and average color of an image."""
    try:
        with Image.open(path) as raw:
            im = raw.convert("RGBA" if "A" in raw.getbands() else "RGB")
            width, height = im.size
            mode = im.mode
            arr = np.array(im)
    except Exception as exc:
        return {"file": path, "error": str(exc)}

    ox = min(sample_offset, max(0, width - 1))
    oy = min(sample_offset, max(0, height - 1))

    # Corner sampling
    top_left = arr[oy, ox, :3].tolist()
    top_right = arr[oy, width - 1 - ox, :3].tolist()
    bottom_left = arr[height - 1 - oy, ox, :3].tolist()
    bottom_right = arr[height - 1 - oy, width - 1 - ox, :3].tolist()

    rgb = arr[:, :, :3]
    mean_rgb = [round(float(c), 1) for c in rgb.mean(axis=(0, 1))]
    brightness = round(float(0.299 * mean_rgb[0] + 0.587 * mean_rgb[1] + 0.114 * mean_rgb[2]), 1)

    has_alpha = mode == "RGBA"
    transparent_pixels = 0
    if has_alpha:
        transparent_pixels = int(np.sum(arr[:, :, 3] < 128))

    return {
        "file": os.path.normpath(path),
        "size": [width, height],
        "mode": mode,
        "corners": {
            "top_left": top_left,
            "top_right": top_right,
            "bottom_left": bottom_left,
            "bottom_right": bottom_right,
        },
        "mean_rgb": mean_rgb,
        "brightness": brightness,
        "is_dark": brightness < 128,
        "transparent_pixels": transparent_pixels if has_alpha else None,
    }


def resolve_inputs(targets):
    """Resolve file paths, directories, and glob patterns."""
    found = []
    valid_exts = {".png", ".jpg", ".jpeg", ".bmp", ".webp", ".gif", ".tiff"}

    for target in targets:
        # Check if target is glob pattern or direct path
        matched = glob.glob(target)
        if not matched and os.path.exists(target):
            matched = [target]

        for p in matched:
            if os.path.isdir(p):
                for root, _, files in os.walk(p):
                    for f in files:
                        if os.path.splitext(f)[1].lower() in valid_exts:
                            found.append(os.path.join(root, f))
            elif os.path.isfile(p):
                found.append(p)

    return sorted(list(dict.fromkeys(found)))


def main():
    parser = argparse.ArgumentParser(
        description="Inspect image dimensions, corner colors, and background brightness."
    )
    parser.add_argument("targets", nargs="+", help="Image files, folders, or glob patterns to inspect")
    parser.add_argument("--sample-offset", type=int, default=5, help="Pixel offset from edges when sampling corners (default: 5)")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    args = parser.parse_args()

    paths = resolve_inputs(args.targets)
    if not paths:
        sys.exit("No matching image files found.")

    results = [inspect_image(p, args.sample_offset) for p in paths]

    if args.json:
        print(json.dumps(results, indent=2))
        return

    print(f"Inspected {len(results)} image(s):\n")
    for r in results:
        if "error" in r:
            print(f"[ERROR] {r['file']}: {r['error']}")
            continue

        w, h = r["size"]
        tl = r["corners"]["top_left"]
        mean = r["mean_rgb"]
        tone = "DARK" if r["is_dark"] else "LIGHT"
        alpha_info = f", transparent_px={r['transparent_pixels']}" if r["transparent_pixels"] is not None else ""
        print(f"- {r['file']}")
        print(f"    Dimensions: {w}x{h} ({r['mode']}){alpha_info}")
        print(f"    Top-Left:   RGB{tuple(tl)}")
        print(f"    Mean RGB:   RGB{tuple(mean)} (brightness {r['brightness']} -> {tone})")


if __name__ == "__main__":
    main()
