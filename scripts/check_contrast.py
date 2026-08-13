#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Find text colours that break in dark mode.

The dark theme works by swapping CSS variables. Any rule that sets a colour as
a literal hex value is invisible to that swap, so a near-black paragraph stays
near-black on a near-black page. That is exactly what happened to p.lead and
blockquote - the most prominent text on the article - and nothing flagged it
until someone looked at the page.

    python3 scripts/check_contrast.py

Exit code 1 if any dark literal colour is not overridden in theme.css.
"""
import io, os, re, sys

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = ('index.html', 'gallery.html', 'slides.html', 'timeline.html', '404.html')


def luminance(hexs):
    h = hexs.lstrip('#')
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def main():
    theme = io.open(os.path.join(SITE, 'theme.css'), encoding='utf-8').read()
    problems = []
    for f in PAGES:
        path = os.path.join(SITE, f)
        if not os.path.exists(path):
            continue
        s = io.open(path, encoding='utf-8').read()
        for css in re.findall(r'<style>(.*?)</style>', s, re.S):
            for m in re.finditer(r'([^{}]+)\{([^{}]*)\}', css):
                sel, decls = m.group(1).strip().replace('\n', ' '), m.group(2)
                for cm in re.finditer(r'(?<!-)\bcolor:\s*(#[0-9a-fA-F]{3,6})', decls):
                    c = cm.group(1)
                    if luminance(c) >= 110:
                        continue
                    # is this selector overridden for dark mode?
                    key = sel.split(',')[0].strip()
                    if key and key in theme:
                        continue
                    problems.append((f, sel[:56], c, round(luminance(c))))

    for f, sel, c, L in problems:
        print('  DARK-ON-DARK  %-14s %-56s %s (lum %d)' % (f, sel, c, L))
    if not problems:
        print('  no unhandled dark text colours')
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
