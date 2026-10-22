"""
Accessibility QA for the Stepper.

Validation by RENDERED COMBINATION: theme x page background (bg-canvas,
bg-surface, bg-surface-raised - usage rule 8) x step status (completed,
current, upcoming). Not clickable (rule 24): no hover, pressed or focus.

What is measured:
  1. Text (4.5:1, WCAG 1.4.3): the title and the description against the
     page; the number against the circle's own fill. White on bg-brand is
     `brand-number`, declared in tokens.py.
  2. Indicators (3:1, WCAG 1.4.11): the circle's outer edge against the page -
     the border when it has one, the fill when the border is painted in it;
     the check against the tonal fill; the walked line against the page. The
     pending line is `decorative-line` (rule 21).

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
STP = json.load(open(comp_out('stepper', 'tokens.json')))

SEM = FOUND['color']['semantic']
RES = STP['resolved']
THEMES = ('light', 'dark')
UNDER = ('bg-canvas', 'bg-surface', 'bg-surface-raised')

# status -> (edge, fill, glyph, glyph is text?, label)
STEP = {
    'completed': ('completed-border', 'completed-bg', 'completed-icon',  False, 'label'),
    'current':   ('current-bg',       'current-bg',   'current-number',  True,  'label'),
    'upcoming':  ('upcoming-border',  'upcoming-bg',  'upcoming-number', True,  'label-upcoming'),
}


def sem(name, theme):
    return SEM[name][0 if theme == 'light' else 1]


def tok(role, theme):
    return RES[f'stepper-{role}'][theme]


def row(theme, under, what, ratio, floor, exc=None):
    ratio = round(ratio, 2)
    return {'theme': theme, 'under': under, 'what': what, 'ratio': ratio, 'min': floor,
            'pass': ratio >= floor, 'exception': exc if ratio < floor else None}


def run():
    rows = []
    for theme in THEMES:
        for under in UNDER:
            page = sem(under, theme)
            for status, (edge, fill, glyph, is_text, label) in STEP.items():
                rows.append(row(theme, under, f'{status} circle edge', cr(tok(edge, theme), page), 3.0))
                exc = 'brand-number' if status == 'current' else None
                rows.append(row(theme, under, f'{status} {"number" if is_text else "check"}',
                                cr(tok(glyph, theme), tok(fill, theme)), 4.5 if is_text else 3.0, exc))
                rows.append(row(theme, under, f'{status} title', cr(tok(label, theme), page), 4.5))
            rows.append(row(theme, under, 'description', cr(tok('description', theme), page), 4.5))
            rows.append(row(theme, under, 'walked line', cr(tok('connector-done', theme), page), 3.0))
            rows.append(row(theme, under, 'pending line', cr(tok('connector', theme), page), 3.0,
                            'decorative-line'))

    fails = [x for x in rows if not x['pass'] and not x['exception']]
    excs = [x for x in rows if not x['pass'] and x['exception']]

    print('=' * 78)
    print('STEPPER - ACCESSIBILITY QA (rendered combinations)')
    print('=' * 78)
    for x in rows:
        mark = 'ok ' if x['pass'] else ('exc' if x['exception'] else 'FAIL')
        print(f'  {mark}  {x["theme"]:<5} {x["under"]:<17} {x["what"]:<22} '
              f'{x["ratio"]:>5}:1  (min {x["min"]})' + (f'  {x["exception"]}' if x['exception'] else ''))
    print('-' * 78)
    print(f'{len(rows)} combinations  |  pass: {len(rows) - len(fails) - len(excs)}  |  '
          f'declared exceptions: {len(excs)}  |  fail: {len(fails)}')

    out = {'component': 'Stepper', 'rows': rows,
           'summary': {'total': len(rows), 'fail': len(fails), 'exceptions': len(excs)}}
    os.makedirs(os.path.dirname(comp_out('stepper', 'a11y.json')), exist_ok=True)
    json.dump(out, open(comp_out('stepper', 'a11y.json'), 'w'), indent=2, ensure_ascii=False)

    if fails:
        print(f'{len(fails)} COMBINATION(S) FAIL THE ACCESSIBILITY GATE')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(run())
