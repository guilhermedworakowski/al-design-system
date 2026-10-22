"""
Token layer for the Empty state.

The one rule of this layer: nothing here invents a value. Every token points
to a Foundation token by NAME. The ONLY exception is the max width, a declared
value like the Modal and the Menu (the Foundation has no container width scale).

Naming:
  code  -> empty-state-gap-icon   (hyphen)
  Figma -> the node binds the semantic the token points to (no component
           variable: since 10/10 a component only binds the semantic layer).

ONE SYMBOL IN FIGMA (2026-10-22)

  `empty-state`, node 510:1843. One size, one action. Left out on purpose:
  illustration, compact size, error variant (that is the Alert), a second
  action (Polaris: one primary call to action).

A BOX ON bg-surface-raised WITH A border-default OUTLINE

  Same background as the Card: in dark it lightens instead of vanishing.
  Against the page the box alone gives 1.07:1 light, so the border carries
  the edge. Like the Card, the stroke is OUTSIDE in Figma; the CSS draws it
  outside too, so the 48 of padding needs no discount.

ONLY ON bg-canvas OR bg-surface

  White on white disappears: never inside a Card, Modal or Drawer.

THE ICON IS text-primary

  Figma binds icon-ink; in code the Icon takes currentColor, and its default
  ink is text-primary.

NO TOKEN, ON PURPOSE

  Height: padding + content. The action: the Button Primary with its own
  tokens. Centering: layout, not value.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'tools'))
from paths import FOUNDATION_SRC, TOKENS_JSON, comp_out  # noqa: E402
sys.path.insert(0, FOUNDATION_SRC)

from palette import SEM                     # noqa: E402
from tokenlib import resolve_foundation, css_ref, size_key, save_css  # noqa: E402
from color import cr                      # noqa: E402

FOUND = json.load(open(TOKENS_JSON))   # noqa: E402

# ---------------------------------------------------------------- color
COLOR = {
  'bg':                'bg-surface-raised',
  'border':            'border-default',
  'icon':              'text-primary',
  'title':             'text-primary',
  'description':       'text-secondary',
}

# ------------------------------------------------------------- geometry
GEOM = {
  'border-width':      'border.width.1',
  'radius':            'radius.3xl',
  'padding':           'space.48',
  'icon-size':         'iconSize.32',
  'gap-icon':          'space.16',   # icon -> title
  'gap-text':          'space.8',    # title -> description
  'gap-action':        'space.24',   # text -> button
}

TYPE = {
  'title':       'type.styles.heading-xs',
  'description': 'type.styles.body-md',
}

# Declared value, no scale in the Foundation. A maximum, not a fixed width (Gui, 22/10).
WIDTH = {
  'max-width': 600,
}

PENDING = {
  'region-border': (
    'The box border (`border-default`) is decorative: WCAG 1.4.11 asks 3:1 of CONTROL '
    'outlines, and the empty state is a content box. Same exemption as the Card.'
  ),
}

UNDER = ('bg-canvas', 'bg-surface')   # where the box may sit

# (what, fg role, against (semantic), floor, exception key)
COMBOS = [
  ('title',       'title',       'bg-surface-raised', 4.5, None),
  ('description', 'description', 'bg-surface-raised', 4.5, None),
  ('icon',        'icon',        'bg-surface-raised', 3.0, None),
] + [('box border', 'border', u, 3.0, 'region-border') for u in UNDER]


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
        name = f'empty-state-{role}'
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
            name = f'empty-state-{role}' if group is GEOM else f'empty-state-{role}-font'
            alias[name] = ref
            try:
                resolved[name] = resolve_foundation(ref)
            except KeyError:
                problems.append(f'{name}: {ref} does not exist in the Foundation')

    for role, px in WIDTH.items():
        alias[f'empty-state-{role}'] = f'{px}px (declared)'
        resolved[f'empty-state-{role}'] = px

    if problems:
        print(f'{len(problems)} TOKEN(S) FAIL THE ALIAS GATE:')
        for p in problems:
            print('   ', p)
        return 1

    rows = contrast_rows()
    fails = [r for r in rows if not r['pass'] and not r['exception']]
    excs = [r for r in rows if not r['pass'] and r['exception']]

    print('=' * 74)
    print('EMPTY STATE TOKEN LAYER')
    print('=' * 74)
    for name in sorted(alias):
        print(f'  {name:<30} -> {alias[name]}')
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

    print(f'{len(alias)} tokens, {len(alias) - len(WIDTH)} aliases of the Foundation, '
          f'{len(WIDTH)} declared value.')

    out = {
        'meta': {
            'component': 'Empty state',
            'version': '0.1.0',
            'foundation': FOUND['meta']['version'],
            'figmaNode': '510:1843',
            'note': (
                'Box on bg-surface-raised with a border-default outline, max 600px, only on '
                'bg-canvas or bg-surface. Icon, title, description and one Button Primary.'
            ),
        },
        'alias': alias,
        'resolved': resolved,
        'contrast': rows,
        'pending': PENDING,
    }
    json.dump(out, open(comp_out('empty-state', 'tokens.json'), 'w'), indent=2, ensure_ascii=False)
    print('\nbuild/components/empty-state/tokens.json written')
    write_css()
    return 0


# ------------------------------------------------------------------- css
def write_css():
    L = []
    w = L.append
    w('/* AL Design System - Empty state tokens')
    w(' * GENERATED by src/components/empty-state/tokens.py. Do not edit by hand.')
    w(' *')
    w(' * Every color is a semantic the theme switches on :root.')
    w(' */')
    w('')
    w(':root {')
    w('  /* color */')
    for role, ref in COLOR.items():
        w(f'  --al-empty-state-{role}: {css_ref(ref)};')
    w('')
    w('  /* geometry */')
    for role, ref in GEOM.items():
        w(f'  --al-empty-state-{role}: {css_ref(ref)};')
    w('')
    w('  /* width - declared value, no scale in the Foundation */')
    for role, px in WIDTH.items():
        w(f'  --al-empty-state-{role}: {px}px;')
    w('')
    w('  /* typography - one style becomes four vars */')
    for role, ref in TYPE.items():
        style = resolve_foundation(ref)
        key = size_key(style[1])
        w(f'  --al-empty-state-{role}-font-size: var(--al-font-size-{key});')
        w(f'  --al-empty-state-{role}-line-height: var(--al-line-height-{key});')
        w(f'  --al-empty-state-{role}-font-weight: {style[3]};')
        w(f'  --al-empty-state-{role}-tracking: {style[4]};')
    w('}')
    w('')
    save_css('empty-state', '\n'.join(L))


if __name__ == '__main__':
    sys.exit(run())
