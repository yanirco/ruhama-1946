#!/usr/bin/env python3
"""Restore the historical B&W prints cropped out of the Ruhama exhibition board.

Pipeline: illumination flatten -> auto-levels -> CLAHE -> denoise -> dust removal
-> unsharp -> 2x upscale.  Optional AI colorisation (Zhang et al. 2016, OpenCV DNN).
Nothing is invented in the greyscale masters; colour versions are clearly labelled.
"""
import cv2, numpy as np, os, glob, sys

IN = '/sessions/happy-zealous-feynman/mnt/outputs/01b_tight/'
# clockwise rotation (degrees) inferred from image content; flagged in the catalogue
ROT = {14:90, 18:270, 20:90, 23:90, 29:270, 33:90, 34:270, 39:90, 42:90, 43:90, 44:90, 47:90}
OUT_BW = '/sessions/happy-zealous-feynman/mnt/outputs/02_restored_bw/'
OUT_COL = '/sessions/happy-zealous-feynman/mnt/outputs/03_colorized/'
MODEL = '/tmp/colorz/'

PHOTOS = [8, 11, 12, 13, 14, 16, 18, 19, 20, 21, 23, 26, 27, 28, 29, 31,
          33, 34, 35, 36, 37, 39, 42, 43, 44, 45, 47]


def flatten(g):
    """Remove the smooth lighting gradient from photographing a print on a board."""
    bg = cv2.GaussianBlur(g.astype(np.float32), (0, 0), max(g.shape) / 12.0)
    out = g.astype(np.float32) / np.maximum(bg, 1) * float(bg.mean())
    return np.clip(out, 0, 255).astype(np.uint8)


def autolevel(g, lo=0.5, hi=99.5):
    a, b = np.percentile(g, [lo, hi])
    if b - a < 10:
        return g
    return np.clip((g.astype(np.float32) - a) * 255.0 / (b - a), 0, 255).astype(np.uint8)


def dust(g, thr=26):
    """Inpaint small bright/dark specks that differ sharply from a median-filtered copy."""
    med = cv2.medianBlur(g, 5)
    d = cv2.absdiff(g, med)
    mask = (d > thr).astype(np.uint8) * 255
    n, lab, stats, _ = cv2.connectedComponentsWithStats(mask, 8)
    keep = np.zeros_like(mask)
    lim = max(9, int(g.size * 2e-5))
    for i in range(1, n):
        if stats[i, cv2.CC_STAT_AREA] <= lim:
            keep[lab == i] = 255
    if keep.sum() == 0:
        return g, 0
    keep = cv2.dilate(keep, np.ones((3, 3), np.uint8), 1)
    return cv2.inpaint(g, keep, 3, cv2.INPAINT_TELEA), int((keep > 0).sum())


def unsharp(g, amt=0.55, r=1.6):
    b = cv2.GaussianBlur(g, (0, 0), r)
    return cv2.addWeighted(g, 1 + amt, b, -amt, 0)


def restore(path):
    img = cv2.imread(path)
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    g = flatten(g)
    g = autolevel(g)
    g = cv2.fastNlMeansDenoising(g, None, 7, 7, 21)
    g = cv2.createCLAHE(clipLimit=1.8, tileGridSize=(8, 8)).apply(g)
    g, npx = dust(g)
    g = unsharp(g)
    g = cv2.resize(g, None, fx=2, fy=2, interpolation=cv2.INTER_LANCZOS4)
    return g, npx


_net = None


def colorize(gray):
    global _net
    if _net is None:
        _net = cv2.dnn.readNetFromCaffe(MODEL + 'colorization_deploy_v2.prototxt',
                                        MODEL + 'colorization_release_v2.caffemodel')
        pts = np.load(MODEL + 'pts_in_hull.npy').transpose().reshape(2, 313, 1, 1)
        _net.getLayer(_net.getLayerId('class8_ab')).blobs = [pts.astype(np.float32)]
        _net.getLayer(_net.getLayerId('conv8_313_rh')).blobs = [np.full([1, 313], 2.606, np.float32)]
    h, w = gray.shape
    rgb = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR).astype(np.float32) / 255.
    lab = cv2.cvtColor(rgb, cv2.COLOR_BGR2LAB)
    L = cv2.resize(lab[:, :, 0], (224, 224)) - 50
    _net.setInput(cv2.dnn.blobFromImage(L))
    ab = _net.forward()[0].transpose((1, 2, 0))
    ab = cv2.resize(ab, (w, h))
    out = np.concatenate((lab[:, :, 0][:, :, None], ab), axis=2)
    out = np.clip(cv2.cvtColor(out, cv2.COLOR_LAB2BGR), 0, 1)
    return (out * 255).astype(np.uint8)


def main():
    os.makedirs(OUT_BW, exist_ok=True)
    os.makedirs(OUT_COL, exist_ok=True)
    do_color = '--color' in sys.argv
    for f in sorted(glob.glob(IN + '*.jpg')):
        i = int(os.path.basename(f).split('.')[0])
        if i not in PHOTOS:
            continue
        g, npx = restore(f)
        if i in ROT:
            g = np.rot90(g, -ROT[i] // 90).copy()
        name = f'ruhama_1946_{i:02d}'
        cv2.imwrite(OUT_BW + name + '_bw.jpg', g, [cv2.IMWRITE_JPEG_QUALITY, 95])
        cv2.imwrite(OUT_BW + name + '_bw.png', g)
        print(f'{i:02d} {g.shape[1]}x{g.shape[0]} dust_px={npx}')
        if do_color:
            small = cv2.resize(g, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
            c = colorize(small)
            c = cv2.resize(c, (g.shape[1], g.shape[0]), interpolation=cv2.INTER_LANCZOS4)
            # keep the restored luminance, take only the model's chroma
            lab = cv2.cvtColor(c, cv2.COLOR_BGR2LAB).astype(np.float32)
            lab[:, :, 0] = g
            # damp the model's chroma: 1946 prints colourised at full saturation
            # look lurid and misleading, a restrained tint reads as plausible
            for ch in (1, 2):
                lab[:, :, ch] = np.clip(128 + (lab[:, :, ch] - 128) * 0.40, 108, 148)
            c = cv2.cvtColor(lab.astype(np.uint8), cv2.COLOR_LAB2BGR)
            cv2.imwrite(OUT_COL + name + '_colorized.jpg', c, [cv2.IMWRITE_JPEG_QUALITY, 94])


if __name__ == '__main__':
    main()
