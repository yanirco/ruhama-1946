#!/usr/bin/env python3
"""Detect the mounted print / panel inside each board photo and perspective-crop it."""
import cv2, numpy as np, glob, os, json, sys

SRC = '/sessions/happy-zealous-feynman/mnt/ruhama80britishWea[ponSearch/'
OUT = '/sessions/happy-zealous-feynman/mnt/outputs/01_cropped/'
os.makedirs(OUT, exist_ok=True)


def order_pts(p):
    p = p.reshape(4, 2).astype(np.float32)
    s = p.sum(1); d = np.diff(p, axis=1).ravel()
    return np.array([p[np.argmin(s)], p[np.argmin(d)], p[np.argmax(s)], p[np.argmax(d)]], np.float32)


def quad_score(q, area_img):
    a = cv2.contourArea(q)
    if a < 0.06 * area_img or a > 0.96 * area_img:
        return -1
    if not cv2.isContourConvex(q.astype(np.int32)):
        return -1
    o = order_pts(q)
    w1 = np.linalg.norm(o[1] - o[0]); w2 = np.linalg.norm(o[2] - o[3])
    h1 = np.linalg.norm(o[3] - o[0]); h2 = np.linalg.norm(o[2] - o[1])
    if min(w1, w2, h1, h2) < 40:
        return -1
    # penalise wildly inconsistent opposite sides (bad perspective fit)
    if max(w1, w2) / max(min(w1, w2), 1) > 1.6 or max(h1, h2) / max(min(h1, h2), 1) > 1.6:
        return -1
    ar = max(w1, w2) / max(min(h1, h2), 1)
    if ar > 4.5 or ar < 0.22:
        return -1
    return a


def candidates_from_mask(mask, area_img):
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8), iterations=2)
    cs, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    out = []
    for c in sorted(cs, key=cv2.contourArea, reverse=True)[:8]:
        for eps in (0.02, 0.03, 0.045, 0.06):
            ap = cv2.approxPolyDP(c, eps * cv2.arcLength(c, True), True)
            if len(ap) == 4:
                s = quad_score(ap, area_img)
                if s > 0:
                    out.append((s, order_pts(ap)))
                break
        else:
            r = cv2.minAreaRect(c)
            box = cv2.boxPoints(r).astype(np.float32)
            s = quad_score(box.reshape(4, 1, 2), area_img)
            if s > 0:
                out.append((s * 0.85, order_pts(box)))
    return out


def detect(img):
    h, w = img.shape[:2]
    sc = 900 / max(h, w)
    small = cv2.resize(img, None, fx=sc, fy=sc, interpolation=cv2.INTER_AREA)
    hsv = cv2.cvtColor(small, cv2.COLOR_BGR2HSV)
    S, V = hsv[:, :, 1], hsv[:, :, 2]
    area = small.shape[0] * small.shape[1]
    cands = []

    # 1) red mount border -> outer quad of the red frame
    red = ((hsv[:, :, 0] < 12) | (hsv[:, :, 0] > 168)) & (S > 70) & (V > 70)
    red = (red.astype(np.uint8)) * 255
    if red.sum() / 255 > 0.004 * area:
        rr = cv2.dilate(red, np.ones((15, 15), np.uint8), 1)
        cands += [(s * 1.25, q) for s, q in candidates_from_mask(rr, area)]

    # 2) low-saturation bright region (the photographic print / white paper)
    m2 = ((S < 55) & (V > 60)).astype(np.uint8) * 255
    cands += candidates_from_mask(m2, area)

    # 3) edge based
    g = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
    g = cv2.bilateralFilter(g, 9, 60, 60)
    e = cv2.Canny(g, 30, 90)
    e = cv2.dilate(e, np.ones((5, 5), np.uint8), 2)
    cands += [(s * 0.9, q) for s, q in candidates_from_mask(e, area)]

    if not cands:
        return None
    best = max(cands, key=lambda t: t[0])[1] / sc
    return best


def warp(img, q):
    o = q
    W = int(max(np.linalg.norm(o[1] - o[0]), np.linalg.norm(o[2] - o[3])))
    H = int(max(np.linalg.norm(o[3] - o[0]), np.linalg.norm(o[2] - o[1])))
    dst = np.array([[0, 0], [W, 0], [W, H], [0, H]], np.float32)
    M = cv2.getPerspectiveTransform(o, dst)
    return cv2.warpPerspective(img, M, (W, H), flags=cv2.INTER_CUBIC)


def main():
    files = sorted(glob.glob(SRC + '*.jpeg'))
    rec = []
    for i, f in enumerate(files, 1):
        img = cv2.imread(f)
        q = detect(img)
        name = f'{i:02d}.jpg'
        if q is None:
            cv2.imwrite(OUT + name, img)
            rec.append({'id': i, 'src': os.path.basename(f), 'detected': False})
            continue
        c = warp(img, q)
        # trim 1.5% border (mount edge)
        hh, ww = c.shape[:2]
        m = int(min(hh, ww) * 0.015)
        c = c[m:hh - m, m:ww - m]
        cv2.imwrite(OUT + name, c, [cv2.IMWRITE_JPEG_QUALITY, 96])
        rec.append({'id': i, 'src': os.path.basename(f), 'detected': True,
                    'size': [c.shape[1], c.shape[0]]})
    json.dump(rec, open('/sessions/happy-zealous-feynman/mnt/outputs/crop_log.json', 'w'), indent=1)
    print('done', len(rec), 'detected', sum(r['detected'] for r in rec))


if __name__ == '__main__':
    main()
