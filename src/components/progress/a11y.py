"""
Accessibility QA for the Progress.

Validation by RENDERED COMBINATION: each type, in each theme, on each
background a progress is allowed on (bg-canvas, bg-surface, bg-surface-raised -
usage rule 10). The component has no fill of its own, so the text and the bar
always touch the page background.

What is measured:
  - the label and the meta text against the background (4.5:1, WCAG 1.4.3);
  - the fill against the background (3:1, WCAG 1.4.11);
  - the fill against the track (3:1) - below it is the declared exception
    `fill-on-track` (tokens.py), paid by usage rule 22, not a new finding.

The track against the background is not measured: it only hints at capacity.
The bar takes no focus, so there is no ring to measure.

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
PROG = json.load(open(comp_out('progress', 'tokens.json')))

SEM = FOUND['color']['semantic']
RES = PROG['resolved']
THEMES = ('light', 'dark')
UNDER = ('bg-canvas', 'bg-surface', 'bg-surface-raised')
EXCEPTION = 'fill-on-track'

# (type, the text roles it renders)
TYPES = (
    ('label', ('label-text', 'meta-text')),
    ('steps', ('meta-text',)),
    ('thin',  ()),
)


def sem(name, theme):
    return SEM[name][0 if theme == 'light' else 1]


def run():
    rows = []
    for theme in THEMES:
        fill = RES['progress-fill-bg'][theme]
        track = RES['progress-track-bg'][theme]
        for under in UNDER:
            bg = sem(under, theme)
            for kind, texts in TYPES:
                for role in texts:
                    r = round(cr(RES[f'progress-{role}'][theme], bg), 2)
                    rows.append({'theme': theme, 'under': under, 'what': f'{kind} {role}',
                                 'ratio': r, 'min': 4.5, 'exception': None})
                r = round(cr(fill, bg), 2)
                rows.append({'theme': theme, 'under': under, 'what': f'{kind} fill',
                             'ratio': r, 'min': 3.0, 'exception': None})
                r = round(cr(fill, track), 2)
                rows.append({'theme': theme, 'under': under, 'what': f'{kind} fill on track',
                             'ratio': r, 'min': 3.0,
                             'exception': EXCEPTION if r < 3.0 else None})

    for x in rows:
        x['pass'] = x['ratio'] >= x['min']
    fails = [x for x in rows if not x['pass'] and not x['exception']]
    excs = [x for x in rows if not x['pass'] and x['exception']]

    print('=' * 74)
    print('PROGRESS - ACCESSIBILITY QA (rendered combinations)')
    print('=' * 74)
    for x in rows:
        mark = 'ok ' if x['pass'] else ('exc' if x['exception'] else 'FAIL')
        print(f'  {mark}  {x["theme"]:<5} {x["under"]:<17} {x["what"]:<22} '
              f'{x["ratio"]:>5}:1  (min {x["min"]})')
    print('-' * 74)
    print(f'{len(rows)} combinations  |  pass: {len(rows) - len(fails) - len(excs)}  |  '
          f'declared exceptions: {len(excs)}  |  fail: {len(fails)}')

    out = {'component': 'Progress', 'rows': rows,
           'summary': {'total': len(rows), 'fail': len(fails), 'exceptions': len(excs)}}
    os.makedirs(os.path.dirname(comp_out('progress', 'a11y.json')), exist_ok=True)
    json.dump(out, open(comp_out('progress', 'a11y.json'), 'w'), indent=2, ensure_ascii=False)

    if fails:
        print(f'{len(fails)} COMBINATION(S) FAIL THE ACCESSIBILITY GATE')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(run())
