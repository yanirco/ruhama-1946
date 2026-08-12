#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Report which narration files no longer match the article text.

Twice now the audio has quietly drifted from the page - once because the
extractor was dropping half a section, once because I edited the article after
rendering. Both were invisible: the file existed, played fine, and simply was
not what the page said. This makes the drift visible.

    python3 scripts/check_audio_sync.py

Writes scripts/.narration_hashes on a clean run, and compares against it after.
Exit code 1 if anything is stale, so it can gate a deploy.
"""
import os, sys, json, hashlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import narrate

HASHES = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.narration_hashes')


def digest(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]


def main():
    old = json.load(open(HASHES)) if os.path.exists(HASHES) else {}
    new, stale = {}, []
    for s in narrate.segments():
        key = f"{s['lang']}_part{s['n']}"
        new[key] = digest(s['text'])
        audio = os.path.join(narrate.AUDIO, key + '.mp3')
        if not os.path.exists(audio):
            stale.append((key, 'no audio file'))
        elif key in old and old[key] != new[key]:
            stale.append((key, 'text changed since render'))
        elif key not in old:
            stale.append((key, 'never recorded - run again to baseline'))

    for key, why in stale:
        print(f'  STALE  {key:12s} {why}')
    if not stale:
        print('  all 12 segments match the article')

    if '--write' in sys.argv or not old:
        json.dump(new, open(HASHES, 'w'), indent=1)
        print('baseline written to scripts/.narration_hashes')

    return 1 if stale and old else 0


if __name__ == '__main__':
    sys.exit(main())
