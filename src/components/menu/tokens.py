"""
Token layer for the Menu.

The one rule of this layer: nothing here invents a value. Every token points
to a Foundation token by NAME. The ONLY exception is the menu width, a declared
value like the Breadcrumb menu (the Foundation has no container width scale).

Naming:
  code  -> menu-item-bg-hover   (hyphen)
  Figma -> the node binds the semantic the token points to (no component
           variable: since 10/10 a component only binds the semantic layer).

TWO SETS IN FIGMA (2026-10-22, page Actions)

  `_menu-item` (490:177): Type Default/Danger x State Default/Hover/Pressed/
  Focus/Disabled; props Label, Icon, Icon name, Shortcut, Show shortcut.
  `menu` (490:1214): Closed, Hovered, Opened. The trigger is the Icon Button
  Ghost sm (ellipsis-vertical); opened, it sits on bg-active.

ACTIONS, NOT LINKS

  The Breadcrumb `...` menu holds links (Tab Square items). This one holds
  actions (role="menu" / "menuitem"). No submenu, no checkable item, no group
  title: groups are split by the Divider only. Danger goes last.

DANGER LEAVES THE -RAISED GREYS

  text-danger on bg-hover-raised in dark = 3.31:1, on bg-active-raised 2.2:1.
  Hover goes to bg-danger-subtle, pressed to bg-danger with white ink (Primer).

ICON AND SHORTCUT DARKEN WITH THE LABEL

  text-secondary on bg-hover-raised in dark = 3.5:1, on bg-active-raised
  2.33:1. At rest they are secondary; on hover and pressed, primary.

FOCUS IS AN INSET RING

  2px border-focus inside the item: an outer ring would hit the neighbours.
  Focus drops the hover background (ring on bg-hover-raised = 2.88:1 light).

NO TOKEN, ON PURPOSE

  Item height: 36 = 8 + 20 + 8. Resting item background: transparent.
  Separator: the Divider. Trigger: the Icon Button.
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
  'bg':                  'bg-surface-raised',
  'border':              'border-default',
  'item-label':          'text-primary',
  'item-meta':           'text-secondary',   # icon and shortcut at rest
  'item-meta-hover':     'text-primary',
  'item-bg-hover':       'bg-hover-raised',
  'item-bg-active':      'bg-active-raised',
  'item-label-disabled': 'text-disabled',
  'danger-label':        'text-danger',
  'danger-bg-hover':     'bg-danger-subtle',
  'danger-bg-active':    'bg-danger',
  'danger-label-active': 'text-on-solid',
  'ring':                'border-focus',     # inset, 2px
}

# Elevation: height, not state (Elevation/3, like the Breadcrumb menu).
SHADOW = {
  'shadow': 'elevation.3',
}

# ------------------------------------------------------------- geometry
GEOM = {
  'padding':          'space.4',
  'gap':              'space.2',
  'offset':           'space.4',            # trigger -> panel
  'radius':           'radius.xl',
  'border-width':     'border.width.1',
  'item-padding-y':   'space.8',
  'item-padding-x':   'space.12',
  'item-gap':         'space.8',
  'item-radius':      'radius.lg',
  'item-icon-size':   'iconSize.16',
  'ring-width':       'border.width.2',
}

TYPE = {
  'font': 'type.styles.body-sm',
}

# Declared value, no scale in the Foundation. Fixed, not a minimum (Gui, 22/10).
WIDTH = {
  'width': 200,
}

PENDING = {
  'region-border': (
    'The panel border (`border-default`) gives 1.57:1 light / 2.42:1 dark on the canvas and '
    '1.47:1 / 1.98:1 on bg-surface. WCAG 1.4.11 asks 3:1 of CONTROL outlines; the panel is a '
    'content box, recognized by its items and the Elevation/3 shadow. Same as the Breadcrumb.'
  ),
  'disabled': (
    'text-disabled on bg-surface-raised = 2.1:1 / 2.19:1. Disabled items are exempt from '
    'WCAG 1.4.3.'
  ),
}

UNDER = ('bg-canvas', 'bg-surface')   # what the panel floats over

# (what, fg role, against (semantic), floor, exception key)
COMBOS = [
  ('label',               'item-label',          'bg-surface-raised', 4.5, None),
  ('meta',                'item-meta',           'bg-surface-raised', 4.5, None),
  ('label on hover',      'item-label',          'bg-hover-raised',   4.5, None),
  ('meta on hover',       'item-meta-hover',     'bg-hover-raised',   4.5, None),
  ('label on pressed',    'item-label',          'bg-active-raised',  4.5, None),
  ('meta on pressed',     'item-meta-hover',     'bg-active-raised',  4.5, None),
  ('disabled',            'item-label-disabled', 'bg-surface-raised', 4.5, 'disabled'),
  ('danger',              'danger-label',        'bg-surface-raised', 4.5, None),
  ('danger on hover',     'danger-label',        'bg-danger-subtle',  4.5, None),
  ('danger on pressed',   'danger-label-active', 'bg-danger',         4.5, None),
  ('focus ring',          'ring',                'bg-surface-raised', 3.0, None),
] + [('panel border', 'border', u, 3.0, 'region-border') for u in UNDER]


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
        name = f'menu-{role}'
        alias[name] = ref
        if ref.startswith('#'):
            problems.append(f'{name}: loose hex ({ref}) - every color value is born as an alias')
            continue
        if ref not in SEM:
            problems.append(f'{name}: points to {ref}, which does not exist in the Foundation')
            continue
        light, dark = SEM[ref]
        resolved[name] = {'light': light, 'dark': dark}

    for group in (SHADOW, GEOM, TYPE):
        for role, ref in group.items():
            name = f'menu-{role}'
            alias[name] = ref
            try:
                resolved[name] = resolve_foundation(ref)
            except KeyError:
                problems.append(f'{name}: {ref} does not exist in the Foundation')

    for role, px in WIDTH.items():
        alias[f'menu-{role}'] = f'{px}px (declared)'
        resolved[f'menu-{role}'] = px

    if problems:
        print(f'{len(problems)} TOKEN(S) FAIL THE ALIAS GATE:')
        for p in problems:
            print('   ', p)
        return 1

    rows = contrast_rows()
    fails = [r for r in rows if not r['pass'] and not r['exception']]
    excs = [r for r in rows if not r['pass'] and r['exception']]

    print('=' * 74)
    print('MENU TOKEN LAYER')
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

    print(f'{len(alias)} tokens, {len(alias) - len(WIDTH)} aliases of the Foundation, '
          f'{len(WIDTH)} declared value.')

    out = {
        'meta': {
            'component': 'Menu',
            'version': '0.1.0',
            'foundation': FOUND['meta']['version'],
            'figmaNode': '490:1214',
            'types': ['default', 'danger'],
            'note': (
                'Action menu on bg-surface-raised, fixed 200px. Danger leaves the -raised greys '
                '(danger-subtle hover, solid pressed). Inset focus ring. Divider between groups.'
            ),
        },
        'alias': alias,
        'resolved': resolved,
        'contrast': rows,
        'pending': PENDING,
    }
    json.dump(out, open(comp_out('menu', 'tokens.json'), 'w'), indent=2, ensure_ascii=False)
    print('\nbuild/components/menu/tokens.json written')
    write_css()
    return 0


# ------------------------------------------------------------------- css
def write_css():
    L = []
    w = L.append
    w('/* AL Design System - Menu tokens')
    w(' * GENERATED by src/components/menu/tokens.py. Do not edit by hand.')
    w(' *')
    w(' * Every color is a semantic the theme switches on :root.')
    w(' */')
    w('')
    w(':root {')
    w('  /* color - -raised hover and pressed (the menu lives on surface-raised) */')
    for role, ref in COLOR.items():
        w(f'  --al-menu-{role}: {css_ref(ref)};')
    w('')
    w('  /* elevation - height, not state */')
    for role, ref in SHADOW.items():
        w(f'  --al-menu-{role}: {css_ref(ref)};')
    w('')
    w('  /* geometry */')
    for role, ref in GEOM.items():
        w(f'  --al-menu-{role}: {css_ref(ref)};')
    w('')
    w('  /* width - declared value, no scale in the Foundation */')
    for role, px in WIDTH.items():
        w(f'  --al-menu-{role}: {px}px;')
    w('')
    w('  /* typography - one style becomes four vars */')
    for role, ref in TYPE.items():
        style = resolve_foundation(ref)
        key = size_key(style[1])
        w(f'  --al-menu-font-size: var(--al-font-size-{key});')
        w(f'  --al-menu-line-height: var(--al-line-height-{key});')
        w(f'  --al-menu-font-weight: {style[3]};')
        w(f'  --al-menu-tracking: {style[4]};')
    w('}')
    w('')
    save_css('menu', '\n'.join(L))


if __name__ == '__main__':
    sys.exit(run())
