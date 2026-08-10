#!/usr/bin/env python3
"""Cut every human figure out of the Ruhama board photographs and enlarge it.

The board is a record of wrecked property, so people are rare - these are all of them.
Each crop is re-restored at 4x from the tight crop rather than upscaled from the
already-processed file, so no detail is lost twice.
"""
import cv2, numpy as np, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from restore2 import clarify, ROT

IN = '/sessions/happy-zealous-feynman/mnt/outputs/01b_tight/'
OUT = '/sessions/happy-zealous-feynman/mnt/outputs/05_people/'

# key: output name -> (source id, crop as fractions of the ROTATED clear image)
CROPS = {
 'p1_woman_at_the_sign':      (27, (0.56, 0.04, 0.95, 0.94)),
 'p2_the_warning_sign':       (27, (0.04, 0.10, 0.68, 0.78)),
 'p3_woman_in_the_kitchen':   (34, (0.00, 0.00, 0.46, 0.34)),
 'p4_second_figure_kitchen':  (34, (0.78, 0.02, 1.00, 0.34)),
 'p5_carrying_it_out':        (28, (0.28, 0.38, 1.00, 1.00)),
 'p6_hands_and_the_basket':   (28, (0.55, 0.60, 1.00, 1.00)),
 'p7_man_in_the_yard':        (45, (0.10, 0.18, 0.36, 0.78)),
 'p8_the_yard_around_him':    (45, (0.05, 0.10, 0.60, 0.95)),
 'p9_blackboard_graffiti':    (29, (0.05, 0.10, 0.95, 0.80)),
}


def main():
    os.makedirs(OUT, exist_ok=True)
    cache = {}
    for name, (sid, r) in CROPS.items():
        if sid not in cache:
            img = cv2.imread(f'{IN}{sid:02d}.jpg')
            g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            if sid in ROT:
                g = np.rot90(g, -ROT[sid] // 90).copy()
            cache[sid] = g
        g = cache[sid]
        H, W = g.shape
        x0, y0, x1, y1 = int(r[0] * W), int(r[1] * H), int(r[2] * W), int(r[3] * H)
        crop = g[y0:y1, x0:x1]
        # enlarge more for smaller crops, capped so we never invent resolution
        scale = 4 if max(crop.shape) < 900 else 3
        out = clarify(crop, scale=scale, strong=True)
        cv2.imwrite(f'{OUT}{name}.jpg', out, [cv2.IMWRITE_JPEG_QUALITY, 96])
        print(f'{name:28s} src {sid:02d}  {out.shape[1]}x{out.shape[0]}')


if __name__ == '__main__':
    main()
