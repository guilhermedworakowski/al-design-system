"""
Accessibility QA for the Menu.

Validation by RENDERED COMBINATION: theme x item type (default, danger) x
state (rest, hover, pressed, focus, disabled) x part (label, icon/shortcut).
The panel is always bg-surface-raised (usage rule 19); the item fill is what
the part really sits on. The trigger is measured by the Icon Button gate, the
separator by the Divider gate.

What is measured:
  1. Text (4.5:1, WCAG 1.4.3): label and shortcut against the item's fill.
     The icon shares the shortcut's ink, so it passes the stricter 4.5 too.
  2. Indicators (3:1, WCAG 1.4.11): the inset focus ring against the panel -
     focus drops the hover fill (rule 25), so the panel is what it sits on.
  3. The panel border against the page (bg-canvas, bg-surface).
  Declared in tokens.py: `disabled` (WCAG 1.4.3 exempts it) and
  `region-border` (the panel is a content box, not a control).

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
MENU = json.load(open(comp_out('menu', 'tokens.json')))

SEM = FOUND['color']['semantic']
RES = MENU['resolved']
THEMES = ('light', 'dark')

# (type, state) -> (fill token or None, label token, meta token)
ITEM = {
    ('default', 'rest'):     (None,               'item-label',          'item-meta'),
    ('default', 'hover'):    ('item-bg-hover',    'item-label',          'item-meta-hover'),
    ('default', 'pressed'):  ('item-bg-active',   'item-label',          'item-meta-hover'),
    ('default', 'focus'):    (None,               'item-label',          'item-meta'),
    ('default', 'disabled'): (None,               'item-label-disabled', 'item-label-disabled'),
    ('danger',  'rest'):     (None,               'danger-label',        'danger-label'),
    ('danger',  'hover'):    ('danger-bg-hover',  'danger-label',        'danger-label'),
    ('danger',  'pressed'):  ('danger-bg-active', 'danger-label-active', 'danger-label-active'),
    ('danger',  'focus'):    (None,               'danger-label',        'danger-label'),
    ('danger',  'disabled'): (None,               'item-label-disabled', 'item-label-disabled'),
}


def sem(name, theme):
    return SEM[name][0 if theme == 'light' else 1]


def tok(role, theme):
    return RES[f'menu-{role}'][theme]


def row(theme, what, ratio, floor, exc=None):
    ratio = round(ratio, 2)
    return {'theme': theme, 'what': what, 'ratio': ratio, 'min': floor,
            'pass': ratio >= floor, 'exception': exc if ratio < floor else None}


def run():
    rows = []
    for theme in THEMES:
        panel = tok('bg', theme)
        for (kind, state), (fill, label, meta) in ITEM.items():
            bg = tok(fill, theme) if fill else panel
            exc = 'disabled' if state == 'disabled' else None
            name = f'{kind} {state}'
            rows.append(row(theme, f'{name} label', cr(tok(label, theme), bg), 4.5, exc))
            rows.append(row(theme, f'{name} icon/shortcut', cr(tok(meta, theme), bg), 4.5, exc))
            if state == 'focus':
                rows.append(row(theme, f'{name} ring', cr(tok('ring', theme), panel), 3.0))
        for under in ('bg-canvas', 'bg-surface'):
            rows.append(row(theme, f'panel border on {under}',
                            cr(tok('border', theme), sem(under, theme)), 3.0, 'region-border'))

    fails = [x for x in rows if not x['pass'] and not x['exception']]
    excs = [x for x in rows if not x['pass'] and x['exception']]

    print('=' * 74)
    print('MENU - ACCESSIBILITY QA (rendered combinations)')
    print('=' * 74)
    for x in rows:
        mark = 'ok ' if x['pass'] else ('exc' if x['exception'] else 'FAIL')
        print(f'  {mark}  {x["theme"]:<5} {x["what"]:<34} '
              f'{x["ratio"]:>5}:1  (min {x["min"]})' + (f'  {x["exception"]}' if x['exception'] else ''))
    print('-' * 74)
    print(f'{len(rows)} combinations  |  pass: {len(rows) - len(fails) - len(excs)}  |  '
          f'declared exceptions: {len(excs)}  |  fail: {len(fails)}')

    out = {'component': 'Menu', 'rows': rows,
           'summary': {'total': len(rows), 'fail': len(fails), 'exceptions': len(excs)}}
    json.dump(out, open(comp_out('menu', 'a11y.json'), 'w'), indent=2, ensure_ascii=False)

    if fails:
        print(f'{len(fails)} COMBINATION(S) FAIL THE ACCESSIBILITY GATE')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(run())
