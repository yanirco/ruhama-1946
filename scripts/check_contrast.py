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


def inverted_surfaces():
    """Find rules that use the palette the OTHER way round.

    The hero and the footer are dark plates even in the light theme: a dark
    background with --paper as the *text* colour. A dark theme that swaps
    --paper to near-black turns their text invisible. A colour audit that only
    looks at literal hex values cannot see this, because the values are
    variables and look perfectly correct.
    """
    theme = io.open(os.path.join(SITE, 'theme.css'), encoding='utf-8').read()
    out = []
    for f in PAGES:
        path = os.path.join(SITE, f)
        if not os.path.exists(path):
            continue
        s = io.open(path, encoding='utf-8').read()
        if 'theme.css' not in s:
            continue                      # page opts out of theming entirely
        for css in re.findall(r'<style>(.*?)</style>', s, re.S):
            for m in re.finditer(r'([^{}]+)\{([^{}]*)\}', css):
                sel, decls = m.group(1).strip().replace('\n', ' '), m.group(2)
                d = decls.replace(' ', '')
                if 'color:var(--paper)' not in d:
                    continue
                # A MATCHED PAIR IS SAFE. background:var(--ink) with
                # color:var(--paper) flips as a unit: in dark mode --ink becomes
                # light and --paper becomes dark, so the contrast survives. The
                # dangerous case is --paper text over a background that does NOT
                # flip with it - var(--dark), or a literal colour.
                if 'background:var(--ink)' in d:
                    continue
                key = sel.split(',')[0].strip()
                if key and key in theme:
                    continue
                out.append((f, sel[:56]))
    return out


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

    inv = inverted_surfaces()
    for f, sel in inv:
        print('  INVERTED      %-14s %-56s uses --paper as TEXT' % (f, sel))

    if not problems and not inv:
        print('  no unhandled dark text colours, no unhandled inverted surfaces')
    return 1 if (problems or inv) else 0


if __name__ == '__main__':
    sys.exit(main())
