#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Write the image catalogue for the Ruhama 1946 exhibition board photographs."""
import csv, os

B = '/sessions/happy-zealous-feynman/mnt/ruhama80britishWea[ponSearch/ruhama-80/'

SRC = {}
import glob
for i, f in enumerate(sorted(glob.glob('/sessions/happy-zealous-feynman/mnt/ruhama80britishWea[ponSearch/*.jpeg')), 1):
    SRC[i] = os.path.basename(f)

# id: (type, hebrew, english, subject, confidence, notes)
D = {
1: ('caption', '"...כדי לגלות את נשק המגן תצטרכו לחרוש את כל אדמות ארץ ישראל" (פרופ\' חיים ויצמן)',
    '"...to find the defence weapons you would have to plough every acre of the Land of Israel" (Prof. Chaim Weizmann)',
    'Opening quotation panel of the exhibition', 'high', 'Attributed on the board to Weizmann; wording not yet traced to a published source.'),
2: ('clipping-headline', '"מעשה רוחמה ודורות – התגרות" / שביתת חירום בעיתונים המצולמים – מעשי ההרס בשני הישובים נמשכים',
    '"The Ruhama and Dorot affair - a provocation" / the destruction in both settlements continues',
    'Hebrew press headline strip', 'medium', 'Sub-headline partly illegible at this resolution.'),
3: ('caption', '3 יחידות צבא אנגליה – הדיביזיה השישית המוטסת, המכונה בארץ "הכלניות" – שהשתתפו במצור על הקיבוץ. [68 | 941 | 67]',
    'Three British Army units - the 6th Airborne Division, known locally as "the Anemones" - took part in the siege of the kibbutz. [unit numbers 68, 941, 67]',
    'Order of battle panel with three unit insignia drawn as triangles', 'high', '"Anemones" = red berets. The three numbers are drawn inside triangular formation signs.'),
4: ('clipping-headline', 'חיל כבד שם מצור על המשקים רוחמה ודורות / רשמית: הפעולות מכוונות לחיפוש נשק',
    'Heavy force lays siege to the farms Ruhama and Dorot / Officially: the operations are aimed at searching for arms',
    'Front-page headline', 'high', ''),
5: ('board-overview', 'גזרי עיתונים: "משמר" / "דבר" / "הדאר" (?) + כרטיס: רדיו ירושלים, 28.8.1946 + "הדים: ...רוחמה ודורות בנגב השומם נשלט בידי צבא בריטי מצויד בנשק רב – משוריינים, מוקשים וכו\'"',
    'Newspaper clippings plus a card citing Radio Jerusalem, 28.8.1946, and an "Echoes" card: "...Ruhama and Dorot in the desolate Negev are controlled by a British army equipped with heavy weapons - armour, mines and so on"',
    'Cluster of press clippings on the board', 'medium', 'KEY DATE EVIDENCE: the Radio Jerusalem card is dated 28.8.1946. Masthead identifications are provisional.'),
6: ('title', 'רוחמה במצור', 'Ruhama Under Siege', 'Exhibition title board (detail)', 'high', ''),
7: ('caption', 'אנחנו: "...למה הרסתם תנור האפיה? האין יודעים הקצינים כי אי אפשר להסתיר נשק בתנור מוסק?"',
    'Us: "...why did you destroy the baking oven? Do the officers not know that you cannot hide weapons in a lit oven?"',
    'Voice-of-the-members caption card', 'high', 'One of a series of blue cards giving the kibbutz members\' own reactions.'),
8: ('photo', '', '', 'Wrecked interior: torn bedding and papers, broken furniture, roof beams pulled down', 'high', ''),
9: ('clipping-headline', '...מה ודורות – התגרות" / ...צומתם. – מעשי ההרס בשני הישובים נמשכים',
    '"...[Ruha]ma and Dorot - a provocation" / the destruction in both settlements continues',
    'Headline strip (same story as #2)', 'medium', ''),
10: ('clipping', '"החפושים – הזמנה להרוס את רוחמה בפעם השלישית" / מרת גולדה מאירסון במסיבה עם עתונאי־חוץ',
     '"The searches - an invitation to destroy Ruhama for the third time" / Mrs Golda Meyerson at a press conference with foreign journalists',
     'Report of a Jewish Agency press conference', 'high', 'Golda Meyerson (later Meir) was acting head of the Jewish Agency political department after the Black Saturday arrests. Strong, checkable anchor.'),
11: ('photo', '', '', 'Overturned wooden bed frame / cupboard in a ransacked room', 'high', ''),
12: ('photo', '', '', 'Outdoor structure levered off its foundations; the ground dug out beneath it', 'high', 'One of the clearest prints in the set.'),
13: ('photo', '', '', 'Floor and brick wall broken open, rubble heaped below a standing beam', 'high', 'Matches the accounts of floors being smashed and trenches dug along the walls.'),
14: ('photo', '', '', 'Wrecked machinery / stove beside a corrugated wall', 'medium', 'Orientation inferred, not certain.'),
15: ('clipping', '"משק צעיר, בן שנתיים בנגב נהרס תוך שעות..." / "עמל שנים נהרס תוך שעות" – פניה בה מתארגנת החקלאית הבינלאומית (תל־אביב)',
     '"A young farm, two years old in the Negev, destroyed within hours..." / "Years of labour destroyed within hours" - an appeal to the international agricultural body',
     'Caption card plus clipping about the appeal to international agricultural organisations', 'medium', 'Body text partly legible; mentions a 5-day operation and c. 2,000 soldiers.'),
16: ('photo', '', '', 'Storeroom or workshop with contents strewn across the floor', 'high', ''),
17: ('title', 'רוחמה במצור / חיפוש נשק תש"ו-1946', 'Ruhama Under Siege / Weapons Search 5706-1946', 'Exhibition title board', 'high', 'The Hebrew year on the board reads תש"ו (5706). Late August 1946 falls in Elul 5706.'),
18: ('photo', '', '', 'Concrete floor broken up; graffiti chalked on the surface', 'medium', 'Orientation inferred. A heart and Latin letters are visible.'),
19: ('photo', '', '', 'Interior with windows, furniture overturned, bedding and paper across the floor', 'high', ''),
20: ('photo', '', '', 'Dark interior / doorway of a damaged building', 'low', 'Print is under-exposed; orientation inferred.'),
21: ('photo', '', '', 'Room stripped bare, mattresses slit open, table and chairs upturned', 'high', ''),
22: ('caption', '[חלקי] ...שלושה ואחרים... [כרטיס כחול]', '[partial] blue caption card, text cut off in the photograph',
     'Caption card, partly out of frame', 'low', 'Needs rephotographing.'),
23: ('photo', '', '', 'Exterior of a kibbutz building with the ground dug up along its wall', 'medium', 'Orientation inferred.'),
24: ('caption', 'צריף הקומונה ותכולתה הושחתה. ערימת בגדים מזוהמים, מכונות התפירה, ציוד, כלים, נוצות, חיתולי ילדים – הרכוש המועט שהיה לנו אינו יותר לשימוש.',
     'The commune hut and its contents were ruined. A heap of soiled clothes, the sewing machines, equipment, utensils, feathers, babies\' nappies - the little property we had is no longer usable.',
     'Caption card, members\' account of the commune hut', 'high', 'One of the most quotable lines on the whole board.'),
25: ('clipping', 'המעש (בטאון לח"י): "מפאריס-לונדון עד רוחמה"',
     'HaMa\'as (organ of Lehi): "From Paris-London to Ruhama"',
     'Underground press clipping', 'medium', 'Shows the search was also used politically by the Revisionist underground.'),
26: ('photo', '', '', 'Slit mattresses and scattered bedding in a dark interior', 'high', ''),
27: ('photo', 'שלט: "התבואה תבוא / ...מיד אחת נפתח באש" + כיתוב בערבית',
     'Sign (partly legible) with Arabic text below; a young woman stands beside it',
     'A woman beside a British warning sign posted at the settlement', 'medium',
     'The most human, most publishable image in the set. Sign text needs a clean scan; the Arabic line is a warning to open fire.'),
28: ('photo', '', '', 'A member carrying a slit mattress out of a wrecked room', 'high', ''),
29: ('photo', 'YEHUDI SWINE', 'YEHUDI SWINE', 'Antisemitic graffiti chalked on a blackboard by searching soldiers', 'high',
     'Documentary evidence of the conduct of the search; use with an explanatory caption, never as a standalone shock image.'),
30: ('caption', '...תקו החיים בקיבוץ... בחדר האוכל... [מט]בח הרוס, הצי[וד]... "ברנר" נעקר מה[מקום]',
     '[partial] "...life in the kibbutz was cut off... in the dining hall... the kitchen destroyed, the equipment... the \'Brener\' [burner/pump] torn out"',
     'Caption card on the dining hall and kitchen', 'medium', 'Text runs off the edge of the photograph.'),
31: ('photo', '', '', 'A heavy beam or lintel thrown down across dug-up ground', 'high', ''),
32: ('clipping', 'משמר: "הרס והתעללות ביישובים הנצורים – יום חמישי למצור ולחיפושים ברוחמה ודורות" / הקצין וילסון: "רוחמה, מרכז נשק הגדול אחרי יגור"',
     'Mishmar: "Destruction and abuse in the besieged settlements - fifth day of the siege and searches at Ruhama and Dorot" / Officer Wilson: "Ruhama, the largest arms centre after Yagur"',
     'Mishmar front page, day five of the siege', 'high',
     'CRITICAL: dates the siege to at least five days and names the British officer. Mishmar was the Hashomer Hatzair daily, later Al HaMishmar.'),
33: ('photo', '', '', 'Trench dug along a building line, debris and timber piled in it', 'medium', 'Orientation inferred.'),
34: ('photo', '', '', 'A woman at a table in a wrecked kitchen or dining hall, salvaging utensils', 'high', 'Strong human-scale image; good series opener or closer.'),
35: ('photo', '', '', 'Store shelves emptied, linen and bedding thrown into a heap', 'high', ''),
36: ('photo', '', '', 'A mattress cut open, its stuffing pulled out - the standard search technique', 'high', ''),
37: ('photo', '', '', 'Dark interior, floor broken open near a window', 'medium', ''),
38: ('clipping', 'משמר: "הרס והתעללות ביישובים הנצורים – יום חמישי למצור ולחיפושים ברוחמה ודורות. חמסו מבארות בריחות, מחסני אספקה ובמים, ובכל משק רכוש הועלה באש – גילו נשק מגן – החיפושים נמשכים" / הקצין וילסון: "רוחמה, מרכז נשק הגדול אחרי יגור"',
     'Mishmar: "Destruction and abuse in the besieged settlements - fifth day of the siege and searches at Ruhama and Dorot" / Officer Wilson: "Ruhama, the largest arms centre after Yagur"',
     'Mishmar front page (fuller frame of #32)', 'medium', 'Sub-deck transcription is provisional - needs a flatbed scan.'),
39: ('photo', '', '', 'Long interior, probably the cowshed or a barn, wrecked along its whole length', 'medium', 'Orientation inferred.'),
40: ('caption', '...מתבנים הועלו באש. האספקה... בעלי חיים עורבבו... זבל כימי... הגרעינים טופ[לו]',
     '[partial] "...haystacks were set alight. The food stores... the livestock scattered... chemical fertiliser [mixed in]... the seed grain spoiled"',
     'Caption card on damage to the farm', 'medium', 'Card runs off the edge of the photograph; this is the agricultural-damage panel.'),
41: ('clipping', 'משמר: "הרס והתעללות ביישובים הנצורים" / הקצין וילסון: "רוחמה, מרכז נשק הגדול אחרי יגור"',
     'Mishmar front page (third framing)', 'Mishmar front page', 'high', 'Duplicate framing of #32/#38 - useful for stitching a clean composite.'),
42: ('photo', '', '', 'A timber hut with its cladding torn off', 'medium', 'Orientation inferred.'),
43: ('photo', '', '', 'Open Negev landscape with a wrecked cart or implement', 'medium', 'Orientation inferred.'),
44: ('photo', '', '', 'Two prints mounted together: smashed office furniture and scattered ring-binders / files',
     'high', 'The lower frame shows the kibbutz office files thrown on the floor - the archive documenting its own ransacking.'),
45: ('photo', '', '', 'The yard: wrecked equipment, timber and machinery heaped after the search', 'high',
     'Widest, best-exposed print in the set. Natural hero image for the 16:9 page.'),
46: ('clipping', '"הנגב זועק תרגז ארץ!" מאת אליהו בוצני(?) / כותרת כחולה: "ענפי החקלאות נפגעו הראשונים" / "למה נבחרו דורות ורוחמה?"',
     '"The Negev cries out, let the country rage!" / blue card: "The farming branches were hit first" / "Why were Dorot and Ruhama chosen?"',
     'Opinion piece plus caption cards', 'medium', 'Author name uncertain at this resolution.'),
47: ('photo', '', '', 'A vast heap of smashed crockery - the kibbutz dining-hall dishes', 'high',
     'Visually the most arresting single frame. Orientation inferred.'),
}

rows = []
for i in range(1, 48):
    t, he, en, subj, conf, note = D[i]
    bw = f'images/bw/ruhama_1946_{i:02d}_bw.jpg' if os.path.exists(B + f'images/bw/ruhama_1946_{i:02d}_bw.jpg') else ''
    col = f'images/color/ruhama_1946_{i:02d}_colorized.jpg' if os.path.exists(B + f'images/color/ruhama_1946_{i:02d}_colorized.jpg') else ''
    rows.append({
        'id': f'RUH-{i:02d}', 'source_file': SRC.get(i, ''), 'type': t,
        'hebrew_text': he, 'english_translation': en, 'subject': subj,
        'restored_bw': bw, 'colorized': col,
        'transcription_confidence': conf, 'notes': note,
    })

with open(B + '02-image-catalogue.csv', 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)
print('wrote', len(rows), 'rows')
print('photos', sum(1 for r in rows if r['type'] == 'photo'))
