# Six Days at Ruhama, 1946 · שישה ימים ברוחמה

In late August 1946 the British Army cordoned Kibbutz Ruhama and neighbouring Kibbutz Dorot in the western Negev and searched them for weapons for six days. Around two thousand troops of the 6th Airborne Division broke the floors, dug trenches along the walls, slit every mattress, mixed chemical fertiliser into the food stores and burned the hay. They found nothing — the caches had been moved outside the perimeter before the troops arrived. Six weeks later, Ruhama was a launch point for the eleven settlements founded across the Negev in a single night.

This is the story, in Hebrew and English, with the kibbutz archive's own photographs digitally restored.

**Live site:** https://ruhama1946.site

---

## What's in here

| Path | What it is |
|---|---|
| `index.html` | The article. Six parts, Hebrew and English, `?lang=en` for English. This is the site. |
| `gallery.html` | **The full archive** — all 47 board images, filterable (photographs / people / captions / orientation-uncertain), with a lightbox and bilingual captions. |
| `slides.html` | The same story as a slide sequence, at 16:9 and 9:16. Served at `/story`. |
| `timeline.html` | Historical timeline plus the production Gantt. Served at `/timeline`. |
| `images/` | 56 restored photographs and panels, web-sized. |
| `scripts/` | The Python that did the restoration. Re-runnable on better scans. |
| `catalogue.csv` | All 47 board photographs catalogued: transcription, translation, subject, confidence. |
| `research-brief.md` | The research behind the article, with open questions and sources. |
| `content-plan.md` | The bilingual publishing plan for the 80th anniversary. |
| `render.yaml` | Render blueprint: static site, cache headers, pretty URLs. |
| `NOTICE.md` | **Read this.** The photographs are the archive's property and are not licensed for reuse. |

## How the photographs were made

They started as 47 phone photographs of an exhibition board in the kibbutz archive — photographs of photographs, shot under room light at an angle. The pipeline:

1. **`crop_detect.py`** — finds the mounted print inside each board photo and perspective-corrects it.
2. **`refine.py`** — measures the board colour from the frame edges, isolates the print, straightens it.
3. **`restore.py`** — lighting flatten, auto-levels, denoise, dust inpainting, 2× upscale. Optional colourisation (Zhang et al. 2016 via OpenCV DNN) with chroma damped to 40%.
4. **`restore2.py`** — the clarity pass that produced the images on the site. Separates the image into a large-scale lighting layer and a small-scale detail layer, flattens only the first, boosts only the second, and sharpens edges without amplifying flat grain.
5. **`people.py`** — cuts each human figure out and re-restores it at 3–4× from the source crop, so detail is never lost twice.
6. **`ai_restore.py`** — the final pass, and the one that produced the images on the site. Tone-corrects each crop at *native* resolution (stacking Lanczos and then a neural upscaler just smears detail), then sends it to **Real-ESRGAN with face enhancement** on Replicate. Two hard-won details: input is capped at 1.2 MP because the shared GPU OOMs above that once face enhancement is on, and the image is written as 3-channel because GFPGAN rejects single-channel grey.

```bash
pip install opencv-python numpy pillow
python3 scripts/crop_detect.py && python3 scripts/refine.py && python3 scripts/restore2.py

export REPLICATE_API_TOKEN=...        # yours — never commit it
python3 scripts/ai_restore.py         # all 27, or specific ids: ... 27 34
```

Nothing was invented. No detail was painted in. Where orientation was inferred rather than known, the catalogue says so.

## Deploying

Static site, no build step.

```bash
git clone https://github.com/<you>/ruhama-1946.git
cd ruhama-1946
python3 -m http.server 8000   # then open http://localhost:8000
```

On Render: **New → Static Site → connect this repo**. Publish directory `.`, build command empty. `render.yaml` handles headers and routes.

## Known unknowns

Sources disagree on whether the siege began **28 August 1946 and ran six days** or **25 August and ran seven**. The site currently says 28 August. The *Mishmar* clipping on the board is headed "day five of the siege" — a clean scan of its date line settles it. Corrections welcome as issues.

We also do not know the names of the four people who appear in the photographs. If you recognise any of them, please open an issue. That is the single most valuable contribution anyone can make to this repository.

## Credits

Photographs: **Kibbutz Ruhama Archive**, 1946. Digitally restored 2026.
Historical background: [Yad Ya'ari / Yad Tabenkin](https://www.kibbutz-story.com/post/ruhama) · [Sha'ar HaNegev Regional Council](https://www.sng.org.il/רוחמה/) · [Haganah Museum](http://www.hahagana.org.il/sites/sitepage/?itemId=48424)

Code MIT · text CC BY-SA 4.0 · photographs © the archive, all rights reserved. See [`NOTICE.md`](NOTICE.md).
