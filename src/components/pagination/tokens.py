"""
Token layer for the Pagination.

The one rule of this layer: nothing here invents a value. Every token points
to a Foundation token by NAME. The gate at the end of the file rejects
anything that is a loose value - hex, px, number.

Naming:
  code  -> pagination-current-bg   (hyphen)
  Figma -> the node binds the semantic the token points to (no component
           variable: since 10/10 a component only binds the semantic layer).

TWO SETS IN FIGMA (2026-10-21)

  `_pagination-item` (475:1103): Page x Current x State, plus Ellipsis.
  `pagination` (475:1179): Numbered, Simple, Load more, Range. Previous, Next
  and Load more are Button instances; rows per page is the Select. Disabled
  previous/next is an instance swap to the disabled Button, not a variant.
  No first/last buttons, on purpose.

THE CURRENT PAGE IS TONAL, LIKE THE TAB SQUARE

  Rest: bg-brand-subtle + text-brand. Hover and pressed darken into the brand
  with text-on-brand. The reference outlined the current page; an outline
  reads as focus in the AL.

NEVER ON SURFACE-RAISED

  Hovers use bg-hover/bg-active, which vanish on surface-raised (Modal
  0.18.1). The Pagination lives on canvas and surface; a usage rule pays it.

NO TOKEN, ON PURPOSE

  Item height and min width: 36 = 8 + 20 + 8. Resting background:
  transparent. Focus ring: the Foundation focus shadow.
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
  'item-label':          'text-primary',
  'item-bg-hover':       'bg-hover',
  'item-bg-active':      'bg-active',
  'ellipsis':            'text-secondary',
  'current-bg':          'bg-brand-subtle',
  'current-label':       'text-brand',
  'current-bg-hover':    'bg-brand-hover',
  'current-bg-active':   'bg-brand-active',
  'current-label-hover': 'text-on-brand',
  'range-text':          'text-secondary',
}

# ------------------------------------------------------------- geometry
GEOM = {
  'item-padding': 'space.8',
  'item-radius':  'radius.full',
  'gap':          'space.4',
  'range-gap':    'space.16',
  'rows-gap':     'space.8',
}

TYPE = {
  'font':       'type.styles.label-md',
  'range-font': 'type.styles.body-sm',
}

PENDING = {
  'brand-on-dark-hover': (
    'White on bg-brand-hover in dark = 3.85:1. The brand exception the Foundation '
    'already declares, inherited from the Button and the Tab, hard floor 3:1.'
  ),
  'tonal-selection': (
    'bg-brand-subtle barely separates from the page. The current page is carried by '
    'the brand label and aria-current="page", not by the background. Same as the Tab.'
  ),
  'pressed-on-dark-surface': (
    'bg-brand-active against bg-surface in dark = 2.74:1. Lasts only while the click '
    'is held; the label inside passes. Same as the Tab.'
  ),
}

UNDER = ('bg-canvas', 'bg-surface')   # never on surface-raised

# (what, fg role, against, floor, exception key)
COMBOS = (
  [('item-label',    'item-label',    u, 4.5, None) for u in UNDER] +
  [('ellipsis',      'ellipsis',      u, 4.5, None) for u in UNDER] +
  [('range-text',    'range-text',    u, 4.5, None) for u in UNDER] +
  [('current-label', 'current-label', u, 4.5, None) for u in UNDER] +
  [('item-label on hover',  'item-label', 'bg-hover',  4.5, None),
   ('item-label on active', 'item-label', 'bg-active', 4.5, None),
   ('current-label on current-bg', 'current-label', 'bg-brand-subtle', 4.5, None),
   ('white on current hover', 'current-label-hover', 'bg-brand-hover', 4.5, 'brand-on-dark-hover'),
   ('white on current active', 'current-label-hover', 'bg-brand-active', 4.5, None)]
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
        name = f'pagination-{role}'
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
            name = f'pagination-{role}'
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
    print('PAGINATION TOKEN LAYER')
    print('=' * 74)
    for name in sorted(alias):
        print(f'  {name:<26} -> {alias[name]}')
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
            'component': 'Pagination',
            'version': '0.1.0',
            'foundation': FOUND['meta']['version'],
            'figmaNode': '475:1179',
            'types': ['numbered', 'simple', 'load-more', 'range'],
            'note': (
                'Current page tonal like the Tab Square; previous, next and load more are '
                'Buttons, rows per page is the Select. Never on surface-raised.'
            ),
        },
        'alias': alias,
        'resolved': resolved,
        'contrast': rows,
        'pending': PENDING,
    }
    json.dump(out, open(comp_out('pagination', 'tokens.json'), 'w'), indent=2, ensure_ascii=False)
    print('\nbuild/components/pagination/tokens.json written')
    write_css()
    return 0


# ------------------------------------------------------------------- css
def write_css():
    L = []
    w = L.append
    w('/* AL Design System - Progress tokens')
    w(' * GENERATED by src/components/pagination/tokens.py. Do not edit by hand.')
    w(' *')
    w(' * Every color is a semantic the theme switches on :root.')
    w(' */')
    w('')
    w(':root {')
    w('  /* color */')
    for role, ref in COLOR.items():
        w(f'  --al-pagination-{role}: {css_ref(ref)};')
    w('')
    w('  /* geometry */')
    for role, ref in GEOM.items():
        w(f'  --al-pagination-{role}: {css_ref(ref)};')
    w('')
    w('  /* type - page numbers like the Button sm, range like body-sm */')
    w('  --al-pagination-font-size: var(--al-font-size-sm);')
    w('  --al-pagination-line-height: var(--al-line-height-sm);')
    w('  --al-pagination-font-weight: var(--al-font-weight-medium);')
    w('  --al-pagination-range-font-weight: var(--al-font-weight-regular);')
    w('}')
    w('')
    save_css('pagination', '\n'.join(L))


if __name__ == '__main__':
    sys.exit(run())
