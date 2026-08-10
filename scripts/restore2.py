#!/usr/bin/env python3
"""Restoration v2 - built for clarity rather than for smoothness.

v1 denoised hard and then sharpened, which cost real detail. v2 keeps the grain,
separates the image into a large-scale (lighting) and small-scale (detail) layer,
flattens only the first and boosts only the second.
"""
import cv2, numpy as np, os, glob, sys

IN = '/sessions/happy-zealous-feynman/mnt/outputs/01b_tight/'
OUT = '/sessions/happy-zealous-feynman/mnt/outputs/04_clear/'
ROT = {14: 90, 18: 270, 20: 90, 23: 90, 29: 270, 33: 90, 34: 270,
       39: 90, 42: 90, 43: 90, 44: 90, 47: 90}
PHOTOS = [8, 11, 12, 13, 14, 16, 18, 19, 20, 21, 23, 26, 27, 28, 29, 31,
          33, 34, 35, 36, 37, 39, 42, 43, 44, 45, 47]


def flatten(g, div=10.0):
    bg = cv2.GaussianBlur(g.astype(np.float32), (0, 0), max(g.shape) / div)
    out = g.astype(np.float32) / np.maximum(bg, 1) * float(bg.mean())
    return np.clip(out, 0, 255).astype(np.uint8)


def levels(g, lo=0.4, hi=99.6, gamma=1.0):
    a, b = np.percentile(g, [lo, hi])
    if b - a < 8:
        return g
    x = np.clip((g.astype(np.float32) - a) / (b - a), 0, 1)
    if gamma != 1.0:
        x = x ** gamma
    return (x * 255).astype(np.uint8)


def local_contrast(g, radius, amount):
    """Large-radius unsharp = local contrast / 'clarity', not edge sharpening."""
    b = cv2.GaussianBlur(g.astype(np.float32), (0, 0), radius)
    out = g.astype(np.float32) + (g.astype(np.float32) - b) * amount
    return np.clip(out, 0, 255).astype(np.uint8)


def edge_sharpen(g, radius=1.1, amount=0.9, threshold=3):
    """Unsharp that leaves flat areas alone, so grain is not amplified into mush."""
    b = cv2.GaussianBlur(g.astype(np.float32), (0, 0), radius)
    hi = g.astype(np.float32) - b
    mask = (np.abs(hi) > threshold).astype(np.float32)
    mask = cv2.GaussianBlur(mask, (0, 0), 1.0)
    return np.clip(g.astype(np.float32) + hi * amount * mask, 0, 255).astype(np.uint8)


def despeck(g, thr=30):
    med = cv2.medianBlur(g, 5)
    d = cv2.absdiff(g, med)
    m = (d > thr).astype(np.uint8) * 255
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
    keep = np.zeros_like(m)
    lim = max(6, int(g.size * 8e-6))
    for i in range(1, n):
        if st[i, cv2.CC_STAT_AREA] <= lim:
            keep[lab == i] = 255
    if keep.sum() == 0:
        return g
    return cv2.inpaint(g, cv2.dilate(keep, np.ones((3, 3), np.uint8), 1), 3, cv2.INPAINT_TELEA)


def clarify(img, scale=2, strong=False):
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if img.ndim == 3 else img
    g = flatten(g)
    g = levels(g, 0.4, 99.6, 0.96)
    # gentle edge-preserving smoothing instead of heavy NLM
    g = cv2.bilateralFilter(g, 7, 26, 7)
    g = despeck(g)
    g = local_contrast(g, radius=max(g.shape) / 26.0, amount=0.42 if not strong else 0.58)
    g = cv2.createCLAHE(clipLimit=1.25, tileGridSize=(10, 10)).apply(g)
    if scale != 1:
        g = cv2.resize(g, None, fx=scale, fy=scale, interpolation=cv2.INTER_LANCZOS4)
    g = edge_sharpen(g, radius=1.05 * (scale / 2 + .5), amount=1.0 if strong else 0.8, threshold=3)
    g = levels(g, 0.15, 99.85)
    return g


def main():
    os.makedirs(OUT, exist_ok=True)
    for f in sorted(glob.glob(IN + '*.jpg')):
        i = int(os.path.basename(f).split('.')[0])
        if i not in PHOTOS:
            continue
        g = clarify(cv2.imread(f))
        if i in ROT:
            g = np.rot90(g, -ROT[i] // 90).copy()
        cv2.imwrite(f'{OUT}ruhama_1946_{i:02d}_clear.jpg', g, [cv2.IMWRITE_JPEG_QUALITY, 95])
        print(f'{i:02d} {g.shape[1]}x{g.shape[0]}')


if __name__ == '__main__':
    main()
