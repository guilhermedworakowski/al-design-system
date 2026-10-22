"""
Accessibility QA for the Pagination.

Validation by RENDERED COMBINATION: theme x page background (bg-canvas,
bg-surface - never surface-raised, usage rule 8) x page item (current or not)
x state (rest, hover, pressed, focus). Previous, Next, Load more and the rows
Select are measured by their own components' gates.

What is measured:
  1. Text (4.5:1, WCAG 1.4.3): the page number against the background it
     really sits on - the item's fill when it has one, the page otherwise.
     The ellipsis and the range text against the page.
  2. Indicators (3:1, WCAG 1.4.11): the current page's fill against the page,
     and the focus ring against the page and against the bg-canvas gap.
     The tonal rest fill is `tonal-selection` (the brand label carries the
     current page, rule 19); the dark pressed fill on bg-surface is
     `pressed-on-dark-surface`; white on the dark brand hover is
     `brand-on-dark-hover`. All three are declared in tokens.py.

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
PAG = json.load(open(comp_out('pagination', 'tokens.json')))

SEM = FOUND['color']['semantic']
RES = PAG['resolved']
THEMES = ('light', 'dark')
UNDER = ('bg-canvas', 'bg-surface')
STATES = ('rest', 'hover', 'pressed', 'focus')

# (current?, state) -> (fill token or None, label token)
ITEM = {
    (False, 'rest'):    (None,                   'item-label'),
    (False, 'hover'):   ('item-bg-hover',        'item-label'),
    (False, 'pressed'): ('item-bg-active',       'item-label'),
    (False, 'focus'):   (None,                   'item-label'),
    (True,  'rest'):    ('current-bg',           'current-label'),
    (True,  'hover'):   ('current-bg-hover',     'current-label-hover'),
    (True,  'pressed'): ('current-bg-active',    'current-label-hover'),
    (True,  'focus'):   ('current-bg',           'current-label'),
}


def sem(name, theme):
    return SEM[name][0 if theme == 'light' else 1]


def tok(role, theme):
    return RES[f'pagination-{role}'][theme]


def row(theme, under, what, ratio, floor, exc=None):
    ratio = round(ratio, 2)
    return {'theme': theme, 'under': under, 'what': what, 'ratio': ratio, 'min': floor,
            'pass': ratio >= floor, 'exception': exc if ratio < floor else None}


def run():
    rows = []
    for theme in THEMES:
        ring = sem('shadow-focus-default', theme)
        gap = sem('bg-canvas', theme)
        for under in UNDER:
            page = sem(under, theme)
            for (cur, state), (fill, label) in ITEM.items():
                name = f'{"current" if cur else "page"} {state}'
                bg = tok(fill, theme) if fill else page
                exc = 'brand-on-dark-hover' if (cur and state == 'hover') else None
                rows.append(row(theme, under, f'{name} label', cr(tok(label, theme), bg), 4.5, exc))
                if cur:
                    exc = ('tonal-selection' if state in ('rest', 'focus')
                           else 'pressed-on-dark-surface' if state == 'pressed' else None)
                    rows.append(row(theme, under, f'{name} fill', cr(bg, page), 3.0, exc))
                if state == 'focus':
                    rows.append(row(theme, under, f'{name} ring',
                                    min(cr(ring, page), cr(ring, gap)), 3.0))
            rows.append(row(theme, under, 'ellipsis', cr(tok('ellipsis', theme), page), 4.5))
            rows.append(row(theme, under, 'range text', cr(tok('range-text', theme), page), 4.5))

    fails = [x for x in rows if not x['pass'] and not x['exception']]
    excs = [x for x in rows if not x['pass'] and x['exception']]

    print('=' * 74)
    print('PAGINATION - ACCESSIBILITY QA (rendered combinations)')
    print('=' * 74)
    for x in rows:
        mark = 'ok ' if x['pass'] else ('exc' if x['exception'] else 'FAIL')
        print(f'  {mark}  {x["theme"]:<5} {x["under"]:<10} {x["what"]:<24} '
              f'{x["ratio"]:>5}:1  (min {x["min"]})' + (f'  {x["exception"]}' if x['exception'] else ''))
    print('-' * 74)
    print(f'{len(rows)} combinations  |  pass: {len(rows) - len(fails) - len(excs)}  |  '
          f'declared exceptions: {len(excs)}  |  fail: {len(fails)}')

    out = {'component': 'Pagination', 'rows': rows,
           'summary': {'total': len(rows), 'fail': len(fails), 'exceptions': len(excs)}}
    os.makedirs(os.path.dirname(comp_out('pagination', 'a11y.json')), exist_ok=True)
    json.dump(out, open(comp_out('pagination', 'a11y.json'), 'w'), indent=2, ensure_ascii=False)

    if fails:
        print(f'{len(fails)} COMBINATION(S) FAIL THE ACCESSIBILITY GATE')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(run())
