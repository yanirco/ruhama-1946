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
from html.parser import HTMLParser

API = 'https://api.elevenlabs.io/v1'
KEY = os.environ.get('ELEVENLABS_API_KEY', '')
SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO = os.path.join(SITE, 'audio')
SAMPLE = os.environ.get('VOICE_SAMPLE', '')
VOICE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.voice_id')
NARRATOR_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             '.voice_id_narrator')
NARRATOR_FILE_EN = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                '.voice_id_narrator_en')

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


def voice_id(lang=None):
    """--narrator uses the designed voices (design_voice.py), which belong to no
    real person. Default stays the owner's own cloned voice.

    Hebrew and English get *separate* designed voices. A voice described for
    Hebrew has no basis on which to choose an English accent, and the first one
    picked South Asian - so the English narrator names the accent explicitly.
    """
    if '--narrator' not in sys.argv:
        f = VOICE_FILE
    elif lang == 'en' and os.path.exists(NARRATOR_FILE_EN):
        f = NARRATOR_FILE_EN
    else:
        f = NARRATOR_FILE
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


class _Narratable(HTMLParser):
    """Walk a section and collect the text a listener should actually hear.

    Two bugs lived in the regex version this replaces, and both were silent -
    the audio simply came out short and nobody could tell what was missing
    without comparing against the page.

    1. It cut the section at the copyright box. That box sits in the *middle*
       of Part 3, so more than half of "Six days" was never narrated at all.
       The box is skipped now; the text after it is not.
    2. It only matched <p>, <li> and <h3>. Part 2's substance is a <div
       class="tl"> timeline - 1911 to 1944, the four abandonments - and none
       of it was in the audio. Hence a 39-second Part 2 that reads as
       truncated, because it was.

    Block elements are whitelisted; housekeeping (the play button, the voice
    credit, video captions, the licence box) is skipped subtree and all.
    """
    BLOCK = {'p', 'li', 'h3', 'h4', 'blockquote', 'figcaption', 'div'}
    SKIP_CLASS = {'audionote', 'vidcap', 'listen', 'box warn', 'dur', 'bar'}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out, self.buf, self.depth, self.skip = [], [], 0, 0

    def _classes(self, attrs):
        return dict(attrs).get('class', '')

    def handle_starttag(self, tag, attrs):
        cls = self._classes(attrs)
        if self.skip:
            self.skip += 1
            return
        if tag in ('button', 'script', 'style', 'svg', 'cite'):
            self.skip = 1
            return
        if any(c and c in cls for c in self.SKIP_CLASS):
            self.skip = 1
            return
        if tag in self.BLOCK:
            self._flush()
            self.depth += 1

    def handle_endtag(self, tag):
        if self.skip:
            self.skip -= 1
            return
        if tag in self.BLOCK:
            self._flush()
            self.depth = max(0, self.depth - 1)

    def handle_data(self, data):
        if not self.skip and data.strip():
            self.buf.append(data)

    def _flush(self):
        t = re.sub(r'\s+', ' ', ' '.join(self.buf)).strip()
        self.buf = []
        # 25 chars filters out stray labels; a real sentence always clears it
        if len(t) > 25:
            # the middle dot and the en-dash are both read aloud otherwise
            t = t.replace('·', '.').replace('–', ' – ')
            self.out.append(t if t.endswith(('.', '?', '!', ':', '"')) else t + '.')

    def close(self):
        super().close()
        self._flush()
        return self.out


def segments():
    """Pull the narratable text out of index.html, in document order."""
    html = open(os.path.join(SITE, 'index.html'), encoding='utf-8').read()

    def plain(fragment):
        t = re.sub(r'<[^>]+>', ' ', fragment)
        t = (t.replace('&nbsp;', ' ').replace('&amp;', 'and')
               .replace('&quot;', '"').replace('&#39;', "'").replace('·', '.'))
        return re.sub(r'\s+', ' ', t).strip()

    out = []
    for lang in ('he', 'en'):
        body = re.search(r'<article id="%s".*?</article>' % lang, html, re.S).group(0)
        for i, part in enumerate(re.split(r'<h2>', body)[1:], 1):
            head = plain(part.split('</h2>')[0])
            rest = part.split('</h2>', 1)[1] if '</h2>' in part else ''
            # drop the licence box itself, but keep everything around it
            rest = re.sub(r'<div class="box warn".*?</div>\s*</div>', '', rest, flags=re.S)
            rest = re.sub(r'<div class="box warn".*?</div>', '', rest, flags=re.S)
            p = _Narratable()
            p.feed(rest)
            chunks = p.close()
            text = re.sub(r'\s+', ' ', (head + '. ' + ' '.join(chunks)).strip())
            if len(text) > 120:
                out.append({'lang': lang, 'n': i, 'title': head, 'text': text})
    return out


def main():
    if not KEY:
        sys.exit('set ELEVENLABS_API_KEY')
    os.makedirs(AUDIO, exist_ok=True)
    if '--clone' in sys.argv:
        clone(); return
    index = []
    for s in segments():
        vid = voice_id(s['lang'])
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
