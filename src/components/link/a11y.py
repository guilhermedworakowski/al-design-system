"""
Accessibility QA for the Link.

Validation by RENDERED COMBINATION: each state, in each theme, on each
background a link is allowed on (bg-canvas and bg-surface - usage rule 21).
The Link has no fill, so the text always touches the page background.

What is measured:
  - text against the background (4.5:1, WCAG 1.4.3);
  - the outer ring against the background around it (3:1, WCAG 1.4.11);
  - the focused text against the ring's inner halo, which is canvas-colored
    even on the surface (4.5:1).

The default below 4.5:1 is the declared brand exception (tokens.py,
`default-below-aa`) - not a new finding.

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
LINK = json.load(open(comp_out('link', 'tokens.json')))

SEM = FOUND['color']['semantic']
RES = LINK['resolved']
THEMES = ('light', 'dark')
UNDER = ('bg-canvas', 'bg-surface')
STATES = ('default', 'hover', 'focus')
EXCEPTION = 'default-below-aa'


def sem(name, theme):
    return SEM[name][0 if theme == 'light' else 1]


def ring(theme):
    """(inner halo, outer ring) colors from the composite focus shadow."""
    inner, outer = re.findall(r'#[0-9A-Fa-f]{6}', RES['link-ring'][theme])
    return inner, outer


def run():
    rows = []
    for theme in THEMES:
        for under in UNDER:
            bg = sem(under, theme)
            for state in STATES:
                ink = RES[f'link-text-{state}'][theme]
                r = round(cr(ink, bg), 2)
                rows.append({'theme': theme, 'under': under, 'what': f'text {state}',
                             'ratio': r, 'min': 4.5,
                             'exception': EXCEPTION if state == 'default' and r < 4.5 else None})
            inner, outer = ring(theme)
            r = round(cr(outer, bg), 2)
            rows.append({'theme': theme, 'under': under, 'what': 'focus ring',
                         'ratio': r, 'min': 3.0, 'exception': None})
            r = round(cr(RES['link-text-focus'][theme], inner), 2)
            rows.append({'theme': theme, 'under': under, 'what': 'focus text on halo',
                         'ratio': r, 'min': 4.5, 'exception': None})

    for x in rows:
        x['pass'] = x['ratio'] >= x['min']
    fails = [x for x in rows if not x['pass'] and not x['exception']]
    excs = [x for x in rows if not x['pass'] and x['exception']]

    print('=' * 74)
    print('LINK - ACCESSIBILITY QA (rendered combinations)')
    print('=' * 74)
    for x in rows:
        mark = 'ok ' if x['pass'] else ('exc' if x['exception'] else 'FAIL')
        print(f'  {mark}  {x["theme"]:<5} {x["under"]:<10} {x["what"]:<20} '
              f'{x["ratio"]:>5}:1  (min {x["min"]})')
    print('-' * 74)
    print(f'{len(rows)} combinations  |  pass: {len(rows) - len(fails) - len(excs)}  |  '
          f'declared exceptions: {len(excs)}  |  fail: {len(fails)}')

    out = {'component': 'Link', 'rows': rows,
           'summary': {'total': len(rows), 'fail': len(fails), 'exceptions': len(excs)}}
    os.makedirs(os.path.dirname(comp_out('link', 'a11y.json')), exist_ok=True)
    json.dump(out, open(comp_out('link', 'a11y.json'), 'w'), indent=2, ensure_ascii=False)

    if fails:
        print(f'{len(fails)} COMBINATION(S) FAIL THE ACCESSIBILITY GATE')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(run())
