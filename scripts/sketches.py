#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate ink-sketch illustrations for the background the camera never covered.

Nobody photographed the 1912 founding, the well being dug in 1913, or the night
descent to the land in 1944. The article describes them in words and shows
nothing. These sketches fill that gap.

THE RULES THIS SCRIPT ENFORCES, and why each one exists:

1. NEVER PHOTOREALISTIC. Every prompt is locked to pen-and-ink with visible
   hatching on cream paper. A photoreal AI image sitting next to a real 1946
   archive photograph would corrupt the whole site - a reader could not tell
   which was evidence. A drawing announces itself as a drawing from across the
   room. That is the entire point.

2. NO FACES, NO NAMED PEOPLE. Figures are small, distant, backs turned or in
   silhouette. We are not inventing portraits of real settlers, and we are
   certainly not inventing faces for the four unidentified people in the
   archive photographs. Those four get found by a person who recognises them,
   not by a model that guesses.

3. THEY LIVE SOMEWHERE ELSE. Output goes to images/sketches/, never
   images/ or images/ai/. The gallery of archive material does not include
   them. Every caption says so. NOTICE.md records them separately.

4. NOTHING IS RECONSTRUCTED FROM A PHOTOGRAPH. Each sketch illustrates an
   event described in a written source, not a scene we have a picture of. If
   we have a photograph, we use the photograph.

    export REPLICATE_API_TOKEN=...
    python3 scripts/sketches.py            # all of them
    python3 scripts/sketches.py 1912 1944  # only these keys
"""
import os, sys, json, time, urllib.request

TOKEN = os.environ.get('REPLICATE_API_TOKEN', '')
SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(SITE, 'images', 'sketches')
MODEL = 'black-forest-labs/flux-1.1-pro'

# The style lock. Appended to every prompt, never varied - consistency across
# the set is what makes them read as one illustrator's hand rather than as
# assorted AI output.
STYLE = (
    'Black ink pen drawing with grey wash on cream paper. Loose confident '
    'linework, visible cross-hatching, visible pencil under-drawing, unfinished '
    'edges fading into the paper. Monochrome, no colour. Reportage sketchbook '
    'study. Figures are small, distant and anonymous - no facial features, no '
    'portraits. Clearly a hand drawing, absolutely not a photograph, not '
    'photorealistic, no photographic grain, no lens blur. '
    # The model likes to sign its work with an invented name. A fake signature
    # implies a human artist who does not exist - on a history site that is a
    # false claim of authorship, so it is forbidden explicitly.
    'No signature, no artist name, no monogram, no watermark, no caption, '
    'no lettering or text of any kind anywhere in the image, clean empty '
    'margins.'
)

SKETCHES = {
    '1912': {
        'file': 'sketch_1912_founding.jpg',
        'he': 'חוות רוחמה נוסדת, 1912',
        'en': 'The founding of the Ruhama farm, 1912',
        'prompt': (
            'A small group of settlers with loaded carts arriving on empty '
            'semi-desert land, low bare hills to the horizon, a few tents and '
            'the beginnings of a stone building. Early twentieth century dress. '
            'Wide open emptiness dominating the frame, the people very small.'
        ),
    },
    '1913': {
        'file': 'sketch_1913_the_well.jpg',
        'he': 'חופרים את הבאר, 1913',
        'en': 'Digging the well, 1913',
        'prompt': (
            'Men digging a deep well by hand in dry ground, a timber winding '
            'frame over the shaft with a rope and bucket, spoil heaped around '
            'the mouth, a horse-drawn cart to one side. Semi-desert landscape.'
        ),
    },
    '1917': {
        'file': 'sketch_1917_expulsion.jpg',
        'he': 'המלחמה מגיעה, 1917',
        'en': 'The war reaches the farm, 1917',
        'prompt': (
            'An abandoned farmstead in semi-desert, roofless walls, a broken '
            'gate, a column of people walking away from it into the distance '
            'carrying bundles. Empty sky. Sense of departure, not violence.'
        ),
    },
    '1936': {
        'file': 'sketch_1936_orchards.jpg',
        'he': 'הפרדסים נעקרים, 1936',
        'en': 'The orchards uprooted, 1936',
        'prompt': (
            'Rows of young fruit trees torn out of the ground and lying on '
            'their sides, roots exposed, an empty field beyond, a ruined '
            'single-storey building in the background. No people.'
        ),
    },
    '1943': {
        'file': 'sketch_1943_return.jpg',
        'he': 'חוזרים לבאר, דצמבר 1943',
        'en': 'Back to the well, December 1943',
        'prompt': (
            'A small group clearing the mouth of a long-disused well, timber '
            'huts half built behind them, tools and planks on the ground, '
            'low hills. Winter light, long shadows.'
        ),
    },
    '1944': {
        'file': 'sketch_1944_night_landing.jpg',
        'he': 'עלייה לקרקע בלילה, 29 במרץ 1944',
        'en': 'Going up to the land by night, 29 March 1944',
        'prompt': (
            'Night scene. Trucks with hooded headlamps on an unmade dirt track '
            'crossing open country, figures unloading timber by lamplight, a '
            'half-raised wooden structure. Dark sky, moonlight, deep shadow. '
            'Secrecy and haste.'
        ),
    },
    '1946dogs': {
        'file': 'sketch_1946_tracker_dogs.jpg',
        'he': 'כלבי הגישוש, אוגוסט 1946',
        'en': 'The tracker dogs, August 1946',
        'prompt': (
            'Two large tracker dogs on leads held by soldiers, seen from behind '
            'and at a distance, crossing a farmyard. The soldiers are silhouettes. '
            'Emphasis on the dogs and the empty yard around them.'
        ),
    },
    '1946eleven': {
        'file': 'sketch_1946_eleven_points.jpg',
        'he': 'אחת עשרה נקודות, אוקטובר 1946',
        'en': 'Eleven points in one night, October 1946',
        'prompt': (
            'Night. A convoy of trucks strung out across open desert country '
            'under stars, tiny watchtower silhouettes rising on the horizon in '
            'several places at once. Vast landscape, minute human activity.'
        ),
    },
}


def api(url, data=None, method=None):
    req = urllib.request.Request(url, method=method)
    req.add_header('Authorization', 'Bearer ' + TOKEN)
    if data is not None:
        req.add_header('Content-Type', 'application/json')
        data = json.dumps(data).encode()
    with urllib.request.urlopen(req, data, timeout=120) as r:
        return json.loads(r.read().decode())


def generate(key, spec):
    dest = os.path.join(OUT, spec['file'])
    if os.path.exists(dest):
        print(f'  = {spec["file"]} (already here)')
        return
    p = api('https://api.replicate.com/v1/models/%s/predictions' % MODEL, {
        'input': {
            'prompt': spec['prompt'] + ' ' + STYLE,
            'aspect_ratio': '3:2',
            'output_format': 'jpg',
            'output_quality': 92,
            'safety_tolerance': 2,
            'prompt_upsampling': False,   # keep our style lock exactly as written
        },
    })
    pid = p['id']
    for _ in range(90):
        time.sleep(4)
        s = api('https://api.replicate.com/v1/predictions/' + pid)
        if s['status'] == 'succeeded':
            url = s['output'][0] if isinstance(s['output'], list) else s['output']
            urllib.request.urlretrieve(url, dest)
            kb = os.path.getsize(dest) // 1024
            print(f'  + {spec["file"]:38s} {kb:5d} KB')
            return
        if s['status'] in ('failed', 'canceled'):
            raise RuntimeError(f'{key}: {s.get("error")}')
    raise TimeoutError(key)


def main():
    if not TOKEN:
        sys.exit('set REPLICATE_API_TOKEN')
    os.makedirs(OUT, exist_ok=True)
    keys = [a for a in sys.argv[1:] if a in SKETCHES] or list(SKETCHES)
    for k in keys:
        try:
            generate(k, SKETCHES[k])
        except Exception as e:
            print(f'  ! {k} failed: {type(e).__name__} {e}')
    json.dump({k: {'file': v['file'], 'he': v['he'], 'en': v['en']}
               for k, v in SKETCHES.items()},
              open(os.path.join(OUT, 'index.json'), 'w'),
              ensure_ascii=False, indent=1)
    print(f'\n{len(keys)} sketches -> images/sketches/')
    print('These are drawings, not photographs. Caption them as such everywhere.')


if __name__ == '__main__':
    main()
