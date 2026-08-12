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
    # --- second batch: the people, and the thing the whole siege was about ---
    'slik': {
        'file': 'sketch_slik.jpg',
        'he': 'סליק — מחבוא נשק',
        'en': 'A slik — a hidden arms cache',
        'prompt': (
            'Cutaway view of a concealed cavity beneath a stone floor, a lifted '
            'flagstone leaning aside, rifles and ammunition boxes wrapped in '
            'cloth packed into the void below. A single figure kneeling at the '
            'edge, seen from behind, lamplight from one side.'
        ),
    },
    'moving': {
        'file': 'sketch_moving_the_weapons.jpg',
        'he': 'מוציאים את הנשק אל מחוץ לגדר',
        'en': 'Moving the weapons outside the perimeter',
        'prompt': (
            'Night. A line of figures carrying long wrapped bundles and wooden '
            'crates away from a small settlement, out through a wire fence into '
            'open fields, bent low. Seen from behind and at a distance. Urgency '
            'and silence. Moonlight only.'
        ),
    },
    'palmach': {
        'file': 'sketch_palmach_training.jpg',
        'he': 'אימון פלמ"ח בוואדיות',
        'en': 'Palmach training in the wadis',
        'prompt': (
            'A dozen young people in work clothes training in a dry riverbed '
            'between eroded banks, some lying prone, some crouching, an '
            'instructor gesturing. Seen from above and behind, faces not '
            'visible. Harsh midday light, deep shadow in the gully.'
        ),
    },
    'cordon': {
        'file': 'sketch_the_cordon.jpg',
        'he': 'טבעת הסגר נסגרת, 28 באוגוסט 1946',
        'en': 'The cordon closes, 28 August 1946',
        'prompt': (
            'A ring of soldiers and military vehicles surrounding a small '
            'settlement of low buildings, seen from a distance and slightly '
            'above, dust rising from the track. The settlement small at the '
            'centre, the ring complete around it.'
        ),
    },
    'search': {
        'file': 'sketch_the_search.jpg',
        'he': 'שוברים את הרצפה',
        'en': 'Breaking the floor',
        'prompt': (
            'Inside a bare room, two soldiers levering up floor tiles with '
            'crowbars, rubble and broken paving heaped to one side, a slit '
            'mattress against the wall, an overturned cupboard. Figures seen '
            'from behind. Hard light from a single window.'
        ),
    },
    # --- third batch: enough frames to keep a wall presentation moving ---
    'mandate': {'file': 'sketch_mandate_office.jpg', 'he': 'שלטון המנדט', 'en': 'The Mandate administration',
        'prompt': 'A colonial government office building with a flagpole, sentry box '
                  'and a parked staff car, seen from the street. Two small figures on '
                  'the steps. Nineteen-forties.'},
    'checkpoint': {'file': 'sketch_checkpoint.jpg', 'he': 'מחסום על הדרך', 'en': 'A checkpoint on the road',
        'prompt': 'A road barrier across a dirt road with a sandbagged post beside it, '
                  'a lorry waiting, two soldiers standing. Open country beyond. Seen '
                  'from behind the waiting lorry.'},
    'ship': {'file': 'sketch_immigrant_ship.jpg', 'he': 'ספינת מעפילים', 'en': 'An immigrant ship',
        'prompt': 'A crowded small steamer low in the water off a dark coastline at '
                  'night, people packed on deck as tiny shapes, a searchlight beam '
                  'sweeping the water from a patrol vessel.'},
    'map': {'file': 'sketch_negev_map.jpg', 'he': 'מפת הנגב', 'en': 'A map of the Negev',
        'prompt': 'A hand-drawn survey map of an arid southern region, contour lines, '
                  'wadis, a few marked points, dividers and a pencil lying across it. '
                  'No lettering, no place names, no writing of any kind.'},
    'society': {'file': 'sketch_moscow_society.jpg', 'he': 'אגודת "שארית ישראל", מוסקבה', 'en': 'The She\'erit Yisrael society, Moscow',
        'prompt': 'A meeting in a plain room around a long table, a dozen people in '
                  'early twentieth century European dress, papers spread out, a lamp. '
                  'Seen from the back of the room, faces not visible.'},
    'jamama': {'file': 'sketch_neighbouring_village.jpg', 'he': 'הכפר השכן, ג\'מאמה', 'en': 'The neighbouring village of Jamama',
        'prompt': 'A small village of low mud-brick houses on a rise, camels and goats '
                  'in the foreground, a well, palm trees. Everyday quiet. Seen from a '
                  'distance across open ground.'},
    'firsthouse': {'file': 'sketch_first_building.jpg', 'he': 'הבית הראשון', 'en': 'The first building',
        'prompt': 'A single-storey stone building half constructed, scaffolding of '
                  'rough timber, stacked blocks, a mortar board, three workers on the '
                  'wall. Empty land all around.'},
    'watercart': {'file': 'sketch_water_cart.jpg', 'he': 'עגלת המים', 'en': 'The water cart',
        'prompt': 'A horse-drawn cart carrying a large water barrel along a rutted '
                  'track, a driver walking beside the horse. Dust, low hills, hard '
                  'sunlight.'},
    'hut': {'file': 'sketch_raising_a_hut.jpg', 'he': 'מקימים צריף', 'en': 'Raising a hut',
        'prompt': 'A group hauling on ropes to raise the timber frame of a long hut, '
                  'others steadying the posts, planks stacked nearby. Seen from a low '
                  'angle. Cooperative effort.'},
    'loudspeaker': {'file': 'sketch_loudspeaker.jpg', 'he': 'הכרזה ברמקול', 'en': 'The announcement',
        'prompt': 'A military vehicle with a large horn loudspeaker mounted on its '
                  'roof, parked at the edge of a settlement, a few figures standing '
                  'still at a distance listening.'},
    'assembly': {'file': 'sketch_assembled_in_the_yard.jpg', 'he': 'מכונסים בחצר', 'en': 'Assembled in the yard',
        'prompt': 'Forty or fifty people sitting and standing together in an open '
                  'farmyard, guarded at the edges by a few soldiers with rifles. Seen '
                  'from above and behind. Long wait, midday heat.'},
    'trenches': {'file': 'sketch_trenches_along_the_walls.jpg', 'he': 'תעלות לאורך הקירות', 'en': 'Trenches along the walls',
        'prompt': 'Soldiers digging a long trench hard against the outside wall of a '
                  'building, spoil heaped along it, picks and shovels, more trenches '
                  'already dug further along.'},
    'stores': {'file': 'sketch_the_food_stores.jpg', 'he': 'מחסני המזון', 'en': 'The food stores',
        'prompt': 'A storeroom with sacks split open and their contents spilled across '
                  'the floor, tins scattered, shelves swept bare, a single figure '
                  'standing in the doorway looking in.'},
    'hay': {'file': 'sketch_the_hay_burning.jpg', 'he': 'החציר בוער', 'en': 'The hay burning',
        'prompt': 'A large haystack burning in a field, thick smoke drifting sideways, '
                  'small figures standing well back watching. Dusk.'},
    'dogsearch': {'file': 'sketch_dogs_in_the_room.jpg', 'he': 'הכלבים בחדרים', 'en': 'The dogs in the rooms',
        'prompt': 'A tracker dog on a lead nosing at a slit mattress inside a wrecked '
                  'room, its handler behind it, bedding and stuffing across the floor.'},
    'radio': {'file': 'sketch_the_radio.jpg', 'he': 'ליד המקלט', 'en': 'At the radio set',
        'prompt': 'Several people gathered close around a valve radio set on a table '
                  'in a plain room, leaning in to listen, one hand on the tuning dial. '
                  'Lamplight. Faces turned away.'},
    'crockery': {'file': 'sketch_the_dining_hall.jpg', 'he': 'חדר האוכל', 'en': 'The dining hall',
        'prompt': 'The interior of a communal dining hall wrecked, long tables '
                  'overturned, an enormous heap of broken plates and cups swept '
                  'together in the middle of the floor.'},
    'rebuild': {'file': 'sketch_rebuilding.jpg', 'he': 'בונים מחדש', 'en': 'Rebuilding',
        'prompt': 'People relaying a broken floor and re-glazing a window frame, '
                  'mortar board and trowel, fresh timber, rubble cleared into neat '
                  'piles. Ordinary work resuming.'},
    'hospital': {'file': 'sketch_field_hospital.jpg', 'he': 'בית חולים שדה', 'en': 'A field hospital',
        'prompt': 'A large canvas tent pitched beside low buildings, crates of '
                  'supplies stacked outside, a stretcher leaning against a pole, two '
                  'figures carrying a box in.'},
    'airstrip': {'file': 'sketch_airstrip.jpg', 'he': 'מנחת בשדה', 'en': 'A landing strip',
        'prompt': 'A rough landing strip scraped across open country, a small light '
                  'aircraft standing at one end, oil drums marking the edge, flat '
                  'empty horizon.'},
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
