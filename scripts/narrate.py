#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Narrate the article in the project owner's own cloned voice (ElevenLabs).

Scope, deliberately: this narrates ONLY the article text, which is ours and
CC BY-SA. It does not narrate Alterman's column - that needs an ACUM licence
regardless of whose voice reads it.

  export ELEVENLABS_API_KEY=...
  python3 scripts/narrate.py --clone   # once: build the voice from the sample
  python3 scripts/narrate.py           # render every segment, both languages

Voice sample must be the speaker's own recording. Cloning anyone else's voice
without their consent is not something this script is for.
"""
import os, sys, json, re, time, urllib.request, urllib.error

API = 'https://api.elevenlabs.io/v1'
KEY = os.environ.get('ELEVENLABS_API_KEY', '')
SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO = os.path.join(SITE, 'audio')
SAMPLE = os.environ.get('VOICE_SAMPLE', '')
VOICE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.voice_id')
NARRATOR_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             '.voice_id_narrator')

# eleven_v3 is the ONLY model that supports Hebrew (74 languages).
# multilingual_v2 covers 29 and Hebrew is not among them - it approximates
# Hebrew letters with a foreign phoneme set, which comes out as gibberish.
MODEL = 'eleven_v3'
SETTINGS = {
    'stability': 0.45,        # a little variation - this is storytelling, not IVR
    'similarity_boost': 0.85,
    'style': 0.35,
    'use_speaker_boost': True,
}


def req(path, data=None, method=None, headers=None, raw_body=None, ctype=None):
    url = API + path
    h = {'xi-api-key': KEY}
    if headers:
        h.update(headers)
    body = raw_body
    if data is not None:
        body = json.dumps(data).encode()
        h['Content-Type'] = 'application/json'
    if ctype:
        h['Content-Type'] = ctype
    r = urllib.request.Request(url, data=body, headers=h, method=method)
    with urllib.request.urlopen(r, timeout=300) as resp:
        raw = resp.read()
        if resp.headers.get('Content-Type', '').startswith('audio'):
            return raw
        return json.loads(raw.decode())


def clone():
    """Instant voice clone from the owner's own recording."""
    if not SAMPLE or not os.path.exists(SAMPLE):
        sys.exit('set VOICE_SAMPLE to your own voice recording (mp3/wav)')
    b = '----ruhamavoice'
    parts = []
    parts.append(('--%s\r\nContent-Disposition: form-data; name="name"\r\n\r\n'
                  'Ruhama narrator (owner)\r\n' % b).encode())
    parts.append(('--%s\r\nContent-Disposition: form-data; name="description"\r\n\r\n'
                  'Narration for ruhama1946.site. Cloned from the project owner\'s own '
                  'recording, with their consent.\r\n' % b).encode())
    parts.append(('--%s\r\nContent-Disposition: form-data; name="files"; filename="%s"\r\n'
                  'Content-Type: audio/mpeg\r\n\r\n' % (b, os.path.basename(SAMPLE))).encode())
    parts.append(open(SAMPLE, 'rb').read())
    parts.append(('\r\n--%s--\r\n' % b).encode())
    out = req('/voices/add', raw_body=b''.join(parts),
              ctype='multipart/form-data; boundary=' + b, method='POST')
    vid = out['voice_id']
    open(VOICE_FILE, 'w').write(vid)
    print('cloned. voice_id =', vid)
    return vid


def voice_id():
    """--narrator uses the designed voice (design_voice.py), which belongs to no
    real person. Default stays the owner's own cloned voice."""
    f = NARRATOR_FILE if '--narrator' in sys.argv else VOICE_FILE
    if os.path.exists(f):
        return open(f).read().strip()
    sys.exit('no voice yet - run design_voice.py, or narrate.py --clone')


def chunks_of(text, limit=700):
    """Split on sentence ends. eleven_v3 is slow, and one long request is far
    more likely to time out than three short ones."""
    parts, cur = [], ''
    for sent in re.split(r'(?<=[.!?:])\s+', text):
        if len(cur) + len(sent) + 1 > limit and cur:
            parts.append(cur.strip()); cur = sent
        else:
            cur += ' ' + sent
    if cur.strip():
        parts.append(cur.strip())
    return parts


def tts(text, vid, out_path, lang):
    """Render in chunks and concatenate - mp3 frames join cleanly end to end."""
    blobs = []
    for c in chunks_of(text):
        for attempt in range(4):
            try:
                blobs.append(req('/text-to-speech/' + vid,
                                 data={'text': c, 'model_id': MODEL,
                                       'voice_settings': SETTINGS},
                                 method='POST', headers={'Accept': 'audio/mpeg'}))
                break
            except Exception:
                if attempt == 3:
                    raise
                time.sleep(6)
    audio = b''.join(blobs)
    open(out_path, 'wb').write(audio)
    return len(audio)


def segments():
    """Pull the narratable text out of index.html, in document order.

    The first version only took <p> tags, so bulleted lists vanished - the
    narration jumped from "two restrictions" straight past the restrictions
    themselves, which is why it sounded like nonsense. This walks paragraphs,
    list items and pull-quotes in the order they appear, and always puts a
    space where a tag was so words never fuse together.
    """
    html = open(os.path.join(SITE, 'index.html'), encoding='utf-8').read()

    def plain(fragment):
        t = re.sub(r'<[^>]+>', ' ', fragment)      # space, not empty
        t = (t.replace('&nbsp;', ' ').replace('&amp;', 'and')
               .replace('&quot;', '"').replace('&#39;', "'")
               .replace('·', '.'))                  # the middle dot is read aloud otherwise
        return re.sub(r'\s+', ' ', t).strip()

    out = []
    for lang in ('he', 'en'):
        m = re.search(r'<article id="%s".*?</article>' % lang, html, re.S)
        body = m.group(0)
        for i, part in enumerate(re.split(r'<h2>', body)[1:], 1):
            head = plain(part.split('</h2>')[0])
            rest = part.split('</h2>', 1)[1] if '</h2>' in part else ''
            # stop before the licence box: it is site housekeeping, not narration
            rest = re.split(r'<div class="box warn"', rest)[0]
            chunks = []
            for m2 in re.finditer(r'<(p|li|h3)(?: class="[^"]*")?>(.*?)</\1>', rest, re.S):
                if 'class="audionote"' in m2.group(0):
                    continue
                t = plain(m2.group(2))
                if len(t) > 25:
                    chunks.append(t if t.endswith(('.', '?', '!', ':')) else t + '.')
            text = (head + '. ' + ' '.join(chunks)).strip()
            text = re.sub(r'\s+', ' ', text)
            if len(text) > 120:
                out.append({'lang': lang, 'n': i, 'title': head, 'text': text[:2600]})
    return out


def main():
    if not KEY:
        sys.exit('set ELEVENLABS_API_KEY')
    os.makedirs(AUDIO, exist_ok=True)
    if '--clone' in sys.argv:
        clone(); return
    vid = voice_id()
    index = []
    for s in segments():
        name = f"{s['lang']}_part{s['n']}.mp3"
        path = os.path.join(AUDIO, name)
        if not os.path.exists(path):
            n = tts(s['text'], vid, path, s['lang'])
            print(f"{name:18s} {len(s['text']):5d} chars -> {n/1024:.0f} KB")
            time.sleep(1)
        else:
            print(f'{name:18s} exists')
        index.append({'lang': s['lang'], 'part': s['n'],
                      'title': s['title'], 'file': 'audio/' + name})
    json.dump(index, open(os.path.join(SITE, 'audio-index.json'), 'w'),
              ensure_ascii=False, indent=1)
    print('wrote audio-index.json —', len(index), 'segments')


if __name__ == '__main__':
    main()
