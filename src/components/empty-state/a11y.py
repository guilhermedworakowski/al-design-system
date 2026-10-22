"""
Accessibility QA for the Empty state.

Validation by RENDERED COMBINATION: theme x page background (bg-canvas,
bg-surface - usage rule 5). The content sits on the box (bg-surface-raised),
not on the page; only the box edge touches the page. Not interactive itself:
the button brings its own states.

What is measured:
  1. Text (4.5:1, WCAG 1.4.3): title and description on the box. No Link
     inside (rule 18): Figma has none, and the Link Default would fall to
     3.2:1 on surface-raised in dark.
  2. Graphics (3:1, WCAG 1.4.11): the icon on the box (decorative, measured
     anyway); the box border on the page is `region-border`, declared in
     tokens.py.

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
ES = json.load(open(comp_out('empty-state', 'tokens.json')))

SEM = FOUND['color']['semantic']
RES = ES['resolved']
THEMES = ('light', 'dark')
UNDER = ('bg-canvas', 'bg-surface')


def sem(name, theme):
    return SEM[name][0 if theme == 'light' else 1]


def tok(role, theme):
    return RES[f'empty-state-{role}'][theme]


def row(theme, under, what, ratio, floor, exc=None):
    ratio = round(ratio, 2)
    return {'theme': theme, 'under': under, 'what': what, 'ratio': ratio, 'min': floor,
            'pass': ratio >= floor, 'exception': exc if ratio < floor else None}


def run():
    rows = []
    for theme in THEMES:
        box = tok('bg', theme)
        for under in UNDER:
            page = sem(under, theme)
            rows.append(row(theme, under, 'box border', cr(tok('border', theme), page), 3.0,
                            'region-border'))
            rows.append(row(theme, under, 'title', cr(tok('title', theme), box), 4.5))
            rows.append(row(theme, under, 'description', cr(tok('description', theme), box), 4.5))
            rows.append(row(theme, under, 'icon', cr(tok('icon', theme), box), 3.0))

    fails = [x for x in rows if not x['pass'] and not x['exception']]
    excs = [x for x in rows if not x['pass'] and x['exception']]

    print('=' * 78)
    print('EMPTY STATE - ACCESSIBILITY QA (rendered combinations)')
    print('=' * 78)
    for x in rows:
        mark = 'ok ' if x['pass'] else ('exc' if x['exception'] else 'FAIL')
        print(f'  {mark}  {x["theme"]:<5} {x["under"]:<11} {x["what"]:<14} '
              f'{x["ratio"]:>5}:1  (min {x["min"]})' + (f'  {x["exception"]}' if x['exception'] else ''))
    print('-' * 78)
    print(f'{len(rows)} combinations  |  pass: {len(rows) - len(fails) - len(excs)}  |  '
          f'declared exceptions: {len(excs)}  |  fail: {len(fails)}')

    out = {'component': 'Empty state', 'rows': rows,
           'summary': {'total': len(rows), 'fail': len(fails), 'exceptions': len(excs)}}
    os.makedirs(os.path.dirname(comp_out('empty-state', 'a11y.json')), exist_ok=True)
    json.dump(out, open(comp_out('empty-state', 'a11y.json'), 'w'), indent=2, ensure_ascii=False)

    if fails:
        print(f'{len(fails)} COMBINATION(S) FAIL THE ACCESSIBILITY GATE')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(run())
