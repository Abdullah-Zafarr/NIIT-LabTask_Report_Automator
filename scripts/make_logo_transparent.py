"""Remove the outer white background from a logo (keeps white inside the logo).

Usage:
    py make_logo_transparent.py <input.png> <output.png> [--threshold 235]

Only white that touches the image edge is removed, so white letters/shapes
inside the logo stay. Edges are softened and the picture is cropped tight.
"""
import argparse

import numpy as np
from PIL import Image
from scipy import ndimage


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--threshold", type=int, default=235)
    args = ap.parse_args()

    img = Image.open(args.src).convert("RGBA")
    rgb = np.array(img)[:, :, :3].astype(int)
    near_white = rgb.min(axis=2) >= args.threshold
    labels, _ = ndimage.label(near_white)
    edge_labels = set(labels[0, :]) | set(labels[-1, :]) | set(labels[:, 0]) | set(labels[:, -1])
    edge_labels.discard(0)
    outside = np.isin(labels, list(edge_labels))
    outside = ndimage.binary_dilation(outside, iterations=1)   # eat the pale fringe

    alpha = np.where(outside, 0, 255).astype(float)
    alpha = ndimage.gaussian_filter(alpha, 0.8)                 # soft edge
    arr = np.array(img)
    arr[:, :, 3] = alpha.clip(0, 255).astype(np.uint8)
    out = Image.fromarray(arr)
    out = out.crop(out.getbbox())
    out.save(args.dst)
    print("saved", args.dst, out.size)


if __name__ == "__main__":
    main()
