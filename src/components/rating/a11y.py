"""
Accessibility QA for the Rating.

Validation by RENDERED COMBINATION: theme x page background (bg-canvas,
bg-surface, bg-surface-raised). The stars have no box of their own at rest,
so the glyph always touches the page.

What is measured:
  1. Text (4.5:1, WCAG 1.4.3): the legend against the page.
  2. Indicators (3:1, WCAG 1.4.11): the on star and the off outline against
     the page; the focus ring against the page.
  3. Declared exception (tokens.py), not a new finding:
       star-preview-on-brand  the hover preview against a checked star -
                              transient, the checked radio carries the value
                              (usage rule 10).

Read-only paints the same tokens as Default. Disabled is exempt (WCAG 1.4.3)
and not measured.

Run: python3 a11y.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'tools'))
from paths import TOKENS_JSON, comp_out  # noqa: E402
from contrast import cr  # noqa: E402
FOUND = json.load(open(TOKENS_JSON))
RAT = json.load(open(comp_out('rating', 'tokens.json')))

SEM = FOUND['color']['semantic']
RES = RAT['resolved']
THEMES = ('light', 'dark')
UNDER = ('bg-canvas', 'bg-surface', 'bg-surface-raised')

# (what, token, min)
MEASURES = (
    ('label',    'rating-label-text', 4.5),
    ('star on',  'rating-star-on',    3.0),
    ('star off', 'rating-star-off',   3.0),
)


def sem(name, theme):
    return SEM[name][0 if theme == 'light' else 1]


def run():
    rows = []
    for theme in THEMES:
        ring = sem('shadow-focus-default', theme)
        for under in UNDER:
            bg = sem(under, theme)
            for what, tok, floor in MEASURES:
                r = round(cr(RES[tok][theme], bg), 2)
                rows.append({'theme': theme, 'under': under, 'what': what,
                             'ratio': r, 'min': floor, 'exception': None})
            r = round(cr(ring, bg), 2)
            rows.append({'theme': theme, 'under': under, 'what': 'focus ring',
                         'ratio': r, 'min': 3.0, 'exception': None})
            r = round(cr(RES['rating-star-preview'][theme], RES['rating-star-on'][theme]), 2)
            rows.append({'theme': theme, 'under': under, 'what': 'preview on star',
                         'ratio': r, 'min': 3.0,
                         'exception': 'star-preview-on-brand' if r < 3.0 else None})

    for x in rows:
        x['pass'] = x['ratio'] >= x['min']
    fails = [x for x in rows if not x['pass'] and not x['exception']]
    excs = [x for x in rows if not x['pass'] and x['exception']]

    print('=' * 74)
    print('RATING - ACCESSIBILITY QA (rendered combinations)')
    print('=' * 74)
    for x in rows:
        mark = 'ok ' if x['pass'] else ('exc' if x['exception'] else 'FAIL')
        print(f'  {mark}  {x["theme"]:<5} {x["under"]:<17} {x["what"]:<16} '
              f'{x["ratio"]:>5}:1  (min {x["min"]})')
    print('-' * 74)
    print(f'{len(rows)} combinations  |  pass: {len(rows) - len(fails) - len(excs)}  |  '
          f'declared exceptions: {len(excs)}  |  fail: {len(fails)}')

    out = {'component': 'Rating', 'rows': rows,
           'summary': {'total': len(rows), 'fail': len(fails), 'exceptions': len(excs)}}
    os.makedirs(os.path.dirname(comp_out('rating', 'a11y.json')), exist_ok=True)
    json.dump(out, open(comp_out('rating', 'a11y.json'), 'w'), indent=2, ensure_ascii=False)

    if fails:
        print(f'{len(fails)} COMBINATION(S) FAIL THE ACCESSIBILITY GATE')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(run())
