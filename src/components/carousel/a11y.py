"""
Accessibility QA for the Carousel.

Validation by RENDERED COMBINATION: theme x page background (bg-canvas,
bg-surface, bg-surface-raised). The component has no fill of its own, so the
dots, the slides and the arrows always touch the page.

What is measured:
  1. Indicators (3:1, WCAG 1.4.11): each dot against the page.
  2. Arrows (the Icon Button Secondary sm, unchanged): the chevron, the
     border and the focus ring against the page - the Secondary fill is
     transparent. The Icon Button's gate already measures them; repeated here
     on every page background the Carousel can sit on.
  3. Declared exceptions (tokens.py), not new findings:
       dot-shape      current dot against the other dots - the 24px pill
                      carries the state and the dots are aria-hidden (rule 22);
       slide-content  the empty slide against the page - content, not a
                      control; the content draws its own edge (rule 24, D1=a).

Disabled arrows are exempt (WCAG 1.4.3) and not measured.

Run: python3 a11y.py
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'tools'))
from paths import TOKENS_JSON, comp_out  # noqa: E402
from contrast import cr  # noqa: E402
FOUND = json.load(open(TOKENS_JSON))
CAR = json.load(open(comp_out('carousel', 'tokens.json')))['resolved']
IB = json.load(open(comp_out('icon-button', 'tokens.json')))['resolved']

SEM = FOUND['color']['semantic']
THEMES = ('light', 'dark')
UNDER = ('bg-canvas', 'bg-surface', 'bg-surface-raised')


def sem(name, theme):
    return SEM[name][0 if theme == 'light' else 1]


def run():
    rows = []

    def add(theme, under, what, fg, bg, floor, exc=None):
        r = round(cr(fg, bg), 2)
        rows.append({'theme': theme, 'under': under, 'what': what, 'ratio': r,
                     'min': floor, 'exception': exc if r < floor else None})

    for theme in THEMES:
        dot = CAR['carousel-dot'][theme]
        cur = CAR['carousel-dot-current'][theme]
        for under in UNDER:
            bg = sem(under, theme)
            add(theme, under, 'dot', dot, bg, 3.0)
            add(theme, under, 'current dot', cur, bg, 3.0)
            add(theme, under, 'current vs dot', cur, dot, 3.0, 'dot-shape')
            add(theme, under, 'empty slide', CAR['carousel-slide-bg'][theme], bg, 3.0, 'slide-content')
            add(theme, under, 'arrow border', IB['icon-button-secondary-border'][theme], bg, 3.0)
            # the ring is a box-shadow: a bg-canvas gap, then the ring color;
            # the ring's outer edge is what touches the page
            ring = re.findall(r'#[0-9A-Fa-f]{6}', IB['icon-button-secondary-ring'][theme])[-1]
            add(theme, under, 'arrow focus ring', ring, bg, 3.0)
            # the Secondary fill is transparent: the chevron sits on the page
            add(theme, under, 'chevron', IB['icon-button-secondary-ink'][theme], bg, 3.0)

    for x in rows:
        x['pass'] = x['ratio'] >= x['min']
    fails = [x for x in rows if not x['pass'] and not x['exception']]
    excs = [x for x in rows if not x['pass'] and x['exception']]

    print('=' * 74)
    print('CAROUSEL - ACCESSIBILITY QA (rendered combinations)')
    print('=' * 74)
    for x in rows:
        mark = 'ok ' if x['pass'] else ('exc' if x['exception'] else 'FAIL')
        print(f'  {mark}  {x["theme"]:<5} {x["under"]:<17} {x["what"]:<18} '
              f'{x["ratio"]:>5}:1  (min {x["min"]})')
    print('-' * 74)
    print(f'{len(rows)} combinations  |  pass: {len(rows) - len(fails) - len(excs)}  |  '
          f'declared exceptions: {len(excs)}  |  fail: {len(fails)}')

    out = {'component': 'Carousel', 'rows': rows,
           'summary': {'total': len(rows), 'fail': len(fails), 'exceptions': len(excs)}}
    os.makedirs(os.path.dirname(comp_out('carousel', 'a11y.json')), exist_ok=True)
    json.dump(out, open(comp_out('carousel', 'a11y.json'), 'w'), indent=2, ensure_ascii=False)

    if fails:
        print(f'{len(fails)} COMBINATION(S) FAIL THE ACCESSIBILITY GATE')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(run())
