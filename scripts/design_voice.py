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
OUT_FILE_EN = os.path.join(HERE, '.voice_id_narrator_en')
PREVIEW_DIR = '/tmp/voice_previews'

# Deliberately describes a *type*, not a person. No names, no "sounds like".
DESCRIPTION = (
    'An elderly Israeli man in his eighties, speaking Hebrew. Warm, weathered, '
    'slightly gravelly baritone. Unhurried - he leaves space between sentences. '
    'The cadence of someone reading a text aloud with care rather than '
    'delivering the news. Reflective, plain, no theatrical emphasis.'
)

# A voice designed for Hebrew does not automatically speak good English. The
# first Hebrew narrator, asked to read English, came out sounding South Asian -
# the model had no reason to infer *which* accent to carry over, so it picked
# one. The English narrator therefore has to name the accent explicitly, and
# name the things that make it recognisably Israeli rather than generic.
DESCRIPTION_EN = (
    'An elderly Israeli man in his eighties speaking English as a second '
    'language, with a clear Hebrew accent - the accent of someone born in '
    'Tel Aviv who learned English later. A guttural, back-of-the-throat R. '
    'Short pure vowels with no diphthong glide. Crisp unaspirated T and P. '
    'The stress falls late in the word. Warm, weathered, slightly gravelly '
    'baritone, unhurried, reading a text aloud with care. '
    'Not British, not American, not Indian, not Arabic, not Russian, '
    'not German - specifically Israeli Hebrew.'
)

# English preview text, from our own article. Chosen because it carries the
# consonants where a wrong accent shows up first: the R in "British", the
# W/V distinction in "weapons", the TH in "they" and "nothing".
PREVIEW_TEXT_EN = (
    'In late August 1946 the British Army surrounded Kibbutz Ruhama in the '
    'western Negev and searched it for weapons for six days. They broke the '
    'floors, dug trenches along the walls, and slit every mattress. They '
    'found nothing. The weapons had been moved outside the perimeter before '
    'the soldiers arrived.'
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


def previews(en=False):
    os.makedirs(PREVIEW_DIR, exist_ok=True)
    tag = 'en' if en else 'he'
    out = req('/text-to-voice/create-previews', {
        'voice_description': DESCRIPTION_EN if en else DESCRIPTION,
        'text': PREVIEW_TEXT_EN if en else PREVIEW_TEXT,
        'model_id': 'eleven_multilingual_ttv_v2',
    })
    for i, p in enumerate(out['previews'], 1):
        path = os.path.join(PREVIEW_DIR, f'{tag}_candidate_{i}.mp3')
        open(path, 'wb').write(base64.b64decode(p['audio_base_64']))
        print(f"{i}  {p['generated_voice_id']}  ->  {path}")
    print('\nlisten, then: python3 scripts/design_voice.py --keep <id>' +
          (' --en' if en else ''))


def keep(gid, en=False):
    out = req('/text-to-voice/create-voice-from-preview', {
        'voice_name': 'Ruhama archival narrator, English (synthesised)' if en
                      else 'Ruhama archival narrator (synthesised)',
        'voice_description': DESCRIPTION_EN if en else DESCRIPTION,
        'generated_voice_id': gid,
    })
    open(OUT_FILE_EN if en else OUT_FILE, 'w').write(out['voice_id'])
    print('saved narrator voice_id =', out['voice_id'])


def main():
    if not KEY:
        sys.exit('set ELEVENLABS_API_KEY')
    en = '--en' in sys.argv
    if '--previews' in sys.argv:
        previews(en)
    elif '--keep' in sys.argv:
        keep(sys.argv[sys.argv.index('--keep') + 1], en)
    else:
        sys.exit(__doc__)


if __name__ == '__main__':
    main()
