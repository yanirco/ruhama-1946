#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Design a narrator voice that belongs to no one (ElevenLabs Voice Design).

Why this exists: we wanted an older, weathered Hebrew narrator with the gravity
of someone reading aloud rather than reporting. The obvious shortcut - cloning a
known poet's voice off a documentary - is not ours to take: he died in 2018 and
consent sits with his family. Voice Design generates a voice from a written
description instead. No real person's recording goes in, so no one's identity
comes out. The site labels it as synthesised, the same way it labels the
colourised photographs.

  export ELEVENLABS_API_KEY=...
  python3 scripts/design_voice.py --previews   # render 3 candidates to /tmp
  python3 scripts/design_voice.py --keep <generated_voice_id>

The chosen voice id is written to scripts/.voice_id_narrator, which narrate.py
reads with --narrator.
"""
import os, sys, json, base64, urllib.request

API = 'https://api.elevenlabs.io/v1'
KEY = os.environ.get('ELEVENLABS_API_KEY', '')
HERE = os.path.dirname(os.path.abspath(__file__))
OUT_FILE = os.path.join(HERE, '.voice_id_narrator')
PREVIEW_DIR = '/tmp/voice_previews'

# Deliberately describes a *type*, not a person. No names, no "sounds like".
DESCRIPTION = (
    'An elderly Israeli man in his eighties, speaking Hebrew. Warm, weathered, '
    'slightly gravelly baritone. Unhurried - he leaves space between sentences. '
    'The cadence of someone reading a text aloud with care rather than '
    'delivering the news. Reflective, plain, no theatrical emphasis.'
)

# Hebrew preview text, from our own article - it is the language that actually
# needs testing, and English previews tell you nothing about Hebrew phonemes.
PREVIEW_TEXT = (
    'בסוף אוגוסט 1946 הקיפו כוחות בריטיים את קיבוץ רוחמה שבנגב המערבי '
    'וחיפשו בו נשק במשך שישה ימים. הם שברו את הרצפות, חפרו לאורך הקירות, '
    'קרעו כל מזרן. הם לא מצאו דבר. הנשק הוצא מן המקום עוד לפני שהגיעו '
    'החיילים, והוסתר מחוץ לגדר.'
)


def req(path, data=None, method='POST'):
    body = json.dumps(data).encode() if data is not None else None
    r = urllib.request.Request(API + path, data=body, method=method,
                               headers={'xi-api-key': KEY,
                                        'Content-Type': 'application/json'})
    with urllib.request.urlopen(r, timeout=300) as resp:
        return json.loads(resp.read().decode())


def previews():
    os.makedirs(PREVIEW_DIR, exist_ok=True)
    out = req('/text-to-voice/create-previews', {
        'voice_description': DESCRIPTION,
        'text': PREVIEW_TEXT,
        'model_id': 'eleven_multilingual_ttv_v2',
    })
    for i, p in enumerate(out['previews'], 1):
        path = os.path.join(PREVIEW_DIR, f'candidate_{i}.mp3')
        open(path, 'wb').write(base64.b64decode(p['audio_base_64']))
        print(f"{i}  {p['generated_voice_id']}  ->  {path}")
    print('\nlisten, then: python3 scripts/design_voice.py --keep <id>')


def keep(gid):
    out = req('/text-to-voice/create-voice-from-preview', {
        'voice_name': 'Ruhama archival narrator (synthesised)',
        'voice_description': DESCRIPTION,
        'generated_voice_id': gid,
    })
    open(OUT_FILE, 'w').write(out['voice_id'])
    print('saved narrator voice_id =', out['voice_id'])


def main():
    if not KEY:
        sys.exit('set ELEVENLABS_API_KEY')
    if '--previews' in sys.argv:
        previews()
    elif '--keep' in sys.argv:
        keep(sys.argv[sys.argv.index('--keep') + 1])
    else:
        sys.exit(__doc__)


if __name__ == '__main__':
    main()
