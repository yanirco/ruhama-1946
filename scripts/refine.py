#!/usr/bin/env python3
"""Second pass: inside each loose crop, isolate the print itself and straighten it.

The mounting board is a large, near-uniform colour; the print is everything that is
NOT that colour.  We measure the board colour from the frame edges, build a distance
mask, take the largest component and fit a rotated rectangle to it.
"""
import cv2, numpy as np, os, glob, sys

IN = '/sessions/happy-zealous-feynman/mnt/outputs/01_cropped/'
OUT = '/sessions/happy-zealous-feynman/mnt/outputs/01b_tight/'


def board_color(img, frac=0.06):
    h, w = img.shape[:2]
    b = max(4, int(min(h, w) * frac))
    edge = np.concatenate([img[:b].reshape(-1, 3), img[-b:].reshape(-1, 3),
                           img[:, :b].reshape(-1, 3), img[:, -b:].reshape(-1, 3)])
    return np.median(edge, axis=0)


def tight(img):
    h, w = img.shape[:2]
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
    bc = cv2.cvtColor(np.uint8([[board_color(img)]]), cv2.COLOR_BGR2LAB)[0, 0].astype(np.float32)
    d = np.linalg.norm(lab - bc, axis=2)
    d = cv2.GaussianBlur(d, (0, 0), 3)
    thr = max(14.0, float(np.percentile(d, 55)))
    m = (d > thr).astype(np.uint8) * 255
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((13, 13), np.uint8), 3)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((7, 7), np.uint8), 2)
    n, lab2, st, _ = cv2.connectedComponentsWithStats(m, 8)
    if n < 2:
        return None
    i = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
    if st[i, cv2.CC_STAT_AREA] < 0.15 * h * w:
        return None
    comp = (lab2 == i).astype(np.uint8) * 255
    comp = cv2.morphologyEx(comp, cv2.MORPH_CLOSE, np.ones((25, 25), np.uint8), 2)
    cs, _ = cv2.findContours(comp, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    c = max(cs, key=cv2.contourArea)
    rect = cv2.minAreaRect(c)
    (cx, cy), (rw, rh), ang = rect
    if rw < 0.25 * w and rh < 0.25 * h:
        return None
    # normalise angle to the smallest rotation
    if rw < rh:
        rw, rh = rh, rw
        ang += 90
    while ang > 45:
        ang -= 90
    while ang < -45:
        ang += 90
    M = cv2.getRotationMatrix2D((cx, cy), ang, 1.0)
    rot = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    # after rotation the rect is axis aligned around (cx, cy)
    if abs(ang) > 44:
        rw, rh = rh, rw
    pad = 0.985
    x0 = int(max(0, cx - rw * pad / 2)); x1 = int(min(w, cx + rw * pad / 2))
    y0 = int(max(0, cy - rh * pad / 2)); y1 = int(min(h, cy + rh * pad / 2))
    if x1 - x0 < 60 or y1 - y0 < 60:
        return None
    return rot[y0:y1, x0:x1]


def main():
    os.makedirs(OUT, exist_ok=True)
    ok = 0
    for f in sorted(glob.glob(IN + '*.jpg')):
        img = cv2.imread(f)
        t = tight(img)
        name = os.path.basename(f)
        if t is None:
            cv2.imwrite(OUT + name, img)
            print('keep', name)
            continue
        cv2.imwrite(OUT + name, t, [cv2.IMWRITE_JPEG_QUALITY, 96])
        ok += 1
    print('tightened', ok)


if __name__ == '__main__':
    main()
