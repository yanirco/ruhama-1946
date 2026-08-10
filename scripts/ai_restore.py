#!/usr/bin/env python3
"""AI restoration pass on Replicate (Real-ESRGAN + face enhance).

Input is the tone-corrected crop at NATIVE resolution (no algorithmic upscale),
so the model does the enlarging - stacking Lanczos then ESRGAN just smears detail.

The API token is read from the environment. It is never written to disk.
"""
import cv2, numpy as np, os, glob, sys, json, time, base64, urllib.request, urllib.error
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from restore2 import clarify, ROT, PHOTOS

TOKEN = os.environ['REPLICATE_API_TOKEN']
TIGHT = '/sessions/happy-zealous-feynman/mnt/outputs/01b_tight/'
PRE   = '/sessions/happy-zealous-feynman/mnt/outputs/06_pre_ai/'
OUT   = '/sessions/happy-zealous-feynman/mnt/outputs/07_ai/'
MODEL_VERSION = 'nightmareai/real-esrgan'
VERSION_ID = 'b3ef194191d13140337468c916c2c5b96dd0cb06dffc032a022a31807f6a5ea8'


def api(url, data=None, method=None, raw=False):
    req = urllib.request.Request(url, method=method)
    req.add_header('Authorization', 'Bearer ' + TOKEN)
    if data is not None and not raw:
        req.add_header('Content-Type', 'application/json')
        data = json.dumps(data).encode()
    with urllib.request.urlopen(req, data, timeout=180) as r:
        return json.loads(r.read().decode())


def upload(path):
    """Replicate Files API - multipart upload, returns a served URL."""
    boundary = '----ruhama' + str(int(time.time() * 1000))
    body = b''
    body += ('--%s\r\nContent-Disposition: form-data; name="content"; filename="%s"\r\n'
             'Content-Type: image/jpeg\r\n\r\n' % (boundary, os.path.basename(path))).encode()
    body += open(path, 'rb').read()
    body += ('\r\n--%s--\r\n' % boundary).encode()
    req = urllib.request.Request('https://api.replicate.com/v1/files', method='POST')
    req.add_header('Authorization', 'Bearer ' + TOKEN)
    req.add_header('Content-Type', 'multipart/form-data; boundary=' + boundary)
    with urllib.request.urlopen(req, body, timeout=300) as r:
        return json.loads(r.read().decode())['urls']['get']


def run(image_url, scale=2, face=True):
    p = api('https://api.replicate.com/v1/predictions', {
        'version': VERSION_ID,
        'input': {'image': image_url, 'scale': scale, 'face_enhance': face},
    })
    pid = p['id']
    for _ in range(150):
        time.sleep(4)
        s = api('https://api.replicate.com/v1/predictions/' + pid)
        if s['status'] == 'succeeded':
            return s['output']
        if s['status'] in ('failed', 'canceled'):
            raise RuntimeError(s.get('error') or s['status'])
    raise TimeoutError('prediction timed out')


def main():
    os.makedirs(PRE, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    only = [int(a) for a in sys.argv[1:] if a.isdigit()]
    ids = only or PHOTOS
    for i in ids:
        dst = f'{OUT}ruhama_1946_{i:02d}_ai.jpg'
        if os.path.exists(dst):
            print(f'{i:02d} already done'); continue
        src = f'{TIGHT}{i:02d}.jpg'
        # tone/clean at native resolution, correct rotation, then let the model enlarge
        g = clarify(cv2.imread(src), scale=1)
        if i in ROT:
            g = np.rot90(g, -ROT[i] // 90).copy()
        # the GPU tops out near 2.1 MP once face_enhance is on
        MAXPX = 1_200_000
        if g.shape[0] * g.shape[1] > MAXPX:
            f = (MAXPX / (g.shape[0] * g.shape[1])) ** 0.5
            g = cv2.resize(g, None, fx=f, fy=f, interpolation=cv2.INTER_AREA)
        # GFPGAN inside real-esrgan needs 3 channels, not single-channel grey
        g3 = cv2.cvtColor(g, cv2.COLOR_GRAY2BGR) if g.ndim == 2 else g
        pre = f'{PRE}{i:02d}.jpg'
        cv2.imwrite(pre, g3, [cv2.IMWRITE_JPEG_QUALITY, 95])
        try:
            url = upload(pre)
            for attempt in range(3):          # the GPU is shared; OOM is transient
                try:
                    out_url = run(url); break
                except RuntimeError as e:
                    if 'out of memory' not in str(e) or attempt == 2: raise
                    time.sleep(20)
            urllib.request.urlretrieve(out_url, dst)
            h, w = cv2.imread(dst).shape[:2]
            print(f'{i:02d} ok  {g3.shape[1]}x{g3.shape[0]} -> {w}x{h}')
        except Exception as e:
            print(f'{i:02d} FAILED: {type(e).__name__} {e}')


if __name__ == '__main__':
    main()
