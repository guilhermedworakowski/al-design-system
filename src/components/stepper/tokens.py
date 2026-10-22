"""
Token layer for the Stepper.

The one rule of this layer: nothing here invents a value. Every token points
to a Foundation token by NAME. The gate at the end of the file rejects
anything that is a loose value - hex, px, number.

Naming:
  code  -> stepper-current-bg   (hyphen)
  Figma -> the node binds the semantic the token points to (no component
           variable: since 10/10 a component only binds the semantic layer).

TWO SETS IN FIGMA (2026-10-22)

  `_stepper-item` (500:320): Orientation x Status (Completed, Current,
  Upcoming). `stepper` (500:387): Horizontal and Vertical, four steps.

THE CURRENT STEP IS SOLID, THE COMPLETED ONE IS TONAL

  Current: bg-brand + text-on-brand. Completed: bg-brand-subtle with a
  border-brand ring and a text-brand check - the ring carries the shape,
  since the tonal fill barely separates from the page. Upcoming: bg-surface
  with border-strong (border-default measured 1.98:1 in dark).

ONE CONTINUOUS LINE

  Horizontal: the title sits under the circle and each item draws half a line
  on each side, so neighbors join with no gap. The half before the first step
  and after the last one are left unpainted. The line before a step is brand
  when that step is completed or current; the line after, only when completed.

NO TOKEN, ON PURPOSE

  Vertical text top offset: 6 = (32 - 20) / 2, centers the title's first line
  on the circle. Horizontal item width: an equal share of the Stepper.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'tools'))
from paths import FOUNDATION_SRC, TOKENS_JSON, comp_out  # noqa: E402
sys.path.insert(0, FOUNDATION_SRC)

from palette import SEM                     # noqa: E402
from tokenlib import resolve_foundation, css_ref, save_css  # noqa: E402
from color import cr                      # noqa: E402

FOUND = json.load(open(TOKENS_JSON))   # noqa: E402

# ---------------------------------------------------------------- color
COLOR = {
  'label':              'text-primary',
  'label-upcoming':     'text-secondary',
  'description':        'text-secondary',
  'completed-bg':       'bg-brand-subtle',
  'completed-border':   'border-brand',
  'completed-icon':     'text-brand',
  'current-bg':         'bg-brand',
  'current-number':     'text-on-brand',
  'upcoming-bg':        'bg-surface',
  'upcoming-border':    'border-strong',
  'upcoming-number':    'text-secondary',
  'connector':          'border-default',
  'connector-done':     'border-brand',
}

# ------------------------------------------------------------- geometry
GEOM = {
  'indicator-size':          'space.32',
  'indicator-radius':        'radius.full',
  'indicator-border-width':  'border.width.1',
  'icon-size':               'iconSize.16',
  'connector-thickness':     'border.width.1',
  'text-gap':                'space.2',
  'horizontal-gap':          'space.8',
  'horizontal-text-padding': 'space.8',
  'vertical-gap':            'space.12',
  'vertical-rail-gap':       'space.4',
  'vertical-step-gap':       'space.24',
}

TYPE = {
  'font':             'type.styles.label-md',
  'description-font': 'type.styles.body-sm',
}

PENDING = {
  'brand-number': (
    'White on bg-brand = 3.34:1 in both themes. The brand exception the Foundation '
    'already declares, inherited from the Button, the Tab and the Pagination, hard floor 3:1.'
  ),
  'decorative-line': (
    'The pending line in border-default measures 1.98:1 in dark. Decorative, like the '
    'Divider: progress is carried by the circles and aria-current="step".'
  ),
}

UNDER = ('bg-canvas', 'bg-surface', 'bg-surface-raised')

# (what, fg role, against, floor, exception key)
COMBOS = (
  [(r, r, u, 4.5, None) for r in ('label', 'label-upcoming', 'description') for u in UNDER] +
  [(r, r, u, 3.0, None) for r in ('completed-border', 'current-bg', 'upcoming-border',
                                   'connector-done') for u in UNDER] +
  [('check on completed-bg',   'completed-icon',  'bg-brand-subtle', 3.0, None),
   ('number on current-bg',    'current-number',  'bg-brand',        4.5, 'brand-number'),
   ('number on upcoming-bg',   'upcoming-number', 'bg-surface',      4.5, None)]
)

# ------------------------------------------------------------------ gate
def contrast_rows():
    rows = []
    for what, role, under, floor, exc in COMBOS:
        fg = SEM[COLOR[role]]
        for theme, i in (('light', 0), ('dark', 1)):
            ratio = round(cr(fg[i], SEM[under][i]), 2)
            rows.append({
                'theme': theme, 'what': f'{what} on {under}',
                'fg': COLOR[role], 'bg': under,
                'ratio': ratio, 'min': floor,
                'pass': ratio >= floor,
                'exception': exc if ratio < floor else None,
            })
    return rows


def run():
    alias, resolved, problems = {}, {}, []

    for role, ref in COLOR.items():
        name = f'stepper-{role}'
        alias[name] = ref
        if ref.startswith('#'):
            problems.append(f'{name}: loose hex ({ref}) - every color value is born as an alias')
            continue
        if ref not in SEM:
            problems.append(f'{name}: points to {ref}, which does not exist in the Foundation')
            continue
        light, dark = SEM[ref]
        resolved[name] = {'light': light, 'dark': dark}

    for group in (GEOM, TYPE):
        for role, ref in group.items():
            name = f'stepper-{role}'
            alias[name] = ref
            try:
                resolved[name] = resolve_foundation(ref)
            except KeyError:
                problems.append(f'{name}: {ref} does not exist in the Foundation')

    if problems:
        print(f'{len(problems)} TOKEN(S) FAIL THE ALIAS GATE:')
        for p in problems:
            print('   ', p)
        return 1

    rows = contrast_rows()
    fails = [r for r in rows if not r['pass'] and not r['exception']]
    excs = [r for r in rows if not r['pass'] and r['exception']]

    print('=' * 74)
    print('STEPPER TOKEN LAYER')
    print('=' * 74)
    for name in sorted(alias):
        print(f'  {name:<34} -> {alias[name]}')
    print('-' * 74)
    print(f'contrast: {len(rows)} measurements  |  pass: {len(rows) - len(fails) - len(excs)}  |  '
          f'fail: {len(fails)}  |  exceptions: {len(excs)}')
    for r in excs:
        print(f'  exception {r["exception"]}: {r["what"]} ({r["theme"]}) = {r["ratio"]}:1')
    print('-' * 74)

    if fails:
        print(f'{len(fails)} COMBINATION(S) FAIL THE CONTRAST GATE:')
        for f in fails:
            print(f'    {f["what"]} ({f["theme"]}): {f["ratio"]}:1 < {f["min"]}')
        return 1

    print(f'{len(alias)} tokens, all aliases of the Foundation. 0 loose values.')

    out = {
        'meta': {
            'component': 'Stepper',
            'version': '0.1.0',
            'foundation': FOUND['meta']['version'],
            'figmaNode': '500:387',
            'orientations': ['horizontal', 'vertical'],
            'note': (
                'Current step solid, completed tonal with a brand ring, upcoming outlined in '
                'border-strong. Horizontal draws one continuous line with the title below.'
            ),
        },
        'alias': alias,
        'resolved': resolved,
        'contrast': rows,
        'pending': PENDING,
    }
    json.dump(out, open(comp_out('stepper', 'tokens.json'), 'w'), indent=2, ensure_ascii=False)
    print('\nbuild/components/stepper/tokens.json written')
    write_css()
    return 0


# ------------------------------------------------------------------- css
def write_css():
    L = []
    w = L.append
    w('/* AL Design System - Stepper tokens')
    w(' * GENERATED by src/components/stepper/tokens.py. Do not edit by hand.')
    w(' *')
    w(' * Every color is a semantic the theme switches on :root.')
    w(' */')
    w('')
    w(':root {')
    w('  /* color */')
    for role, ref in COLOR.items():
        w(f'  --al-stepper-{role}: {css_ref(ref)};')
    w('')
    w('  /* geometry */')
    for role, ref in GEOM.items():
        w(f'  --al-stepper-{role}: {css_ref(ref)};')
    w('')
    w('  /* type - title and number like label-md, description like body-sm */')
    w('  --al-stepper-font-size: var(--al-font-size-sm);')
    w('  --al-stepper-line-height: var(--al-line-height-sm);')
    w('  --al-stepper-font-weight: var(--al-font-weight-medium);')
    w('  --al-stepper-description-font-size: var(--al-font-size-sm);')
    w('  --al-stepper-description-line-height: var(--al-line-height-sm);')
    w('  --al-stepper-description-font-weight: var(--al-font-weight-regular);')
    w('}')
    w('')
    save_css('stepper', '\n'.join(L))


if __name__ == '__main__':
    sys.exit(run())
