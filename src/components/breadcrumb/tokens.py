"""
Token layer for the Breadcrumb (with `_breadcrumb-more`).

The rule of this layer: nothing here invents a value. Every token points to a
Foundation token by NAME. The ONLY exception is the menu's minimum width
(WIDTH, below), declared, named and locked by the gate - the same as the
Sidebar, the Modal and the Drawer: the Foundation has no container width scale.

Naming:
  code  -> breadcrumb-menu-bg      (hyphen)
  Figma -> bg/surface-raised       (folder)
Figma has no variable per component: the node binds the semantic or
Foundation variable the token points to. The exception is a value the
Foundation lacks, which lives in the `4. Components` collection
(breadcrumb-menu-min-width -> breadcrumb/menu/min-width).
Hyphen in code, folder in Figma: they are different layers. Never
collapse one into the other.

LAST COMPONENT OF TIER 4 (2026-10-08)

  Two components that go together in every step, page `Tier 4` in Figma:
    `breadcrumb`        COMPONENT_SET 339:3785 - Size Short (2 levels), Medium
                        (3) and Large (first, second, `...`, current). Text
                        props First page, Second page, Current page.
    `_breadcrumb-more`  COMPONENT_SET 339:4046 - State Opened / Closed. The
                        `...` is the trigger; the menu opens 8 below, centered,
                        with Tab Square items.

  Scope decisions: no hover (only the cursor changes); menu = button + list
  of links with a small JS; collapses at 5 levels or more, in the Large
  format; the current page is text with aria-current, not a link; separator
  in `text-secondary`; line wrapping on a narrow screen; focus with the
  default ring. Menu with Elevation/3. Minimum width 108, the menu grows with
  the text.

THE MENU ITEM IS THE TAB

  Each menu item is a Tab Square (text, padding, radius and label come from
  components/tab/tokens.py). What changes is the hover and pressed
  background: the menu lives on `bg-surface-raised`, where `bg-hover`
  disappears in dark (1.00:1) - the same defect as Modal 0.18.1. Hence the
  two `-raised` below.

NO TOKEN, ON PURPOSE

  Height: comes from the Label/md line height (20). Separator size:
  `icon-size-16` straight from the Foundation (rule from the Tag and the Icon
  Button). Horizontal position of the menu: centered under the `...`,
  computed in the CSS.
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

# ------------------------------------------------------------- color
COLOR = {
    'link':      'text-secondary',
    'current':   'text-brand',
    'separator': 'text-secondary',
    'more':      'text-secondary',        # the `...` trigger

    'menu-bg':             'bg-surface-raised',
    'menu-border':         'border-default',
    'menu-item-bg-hover':  'bg-hover-raised',
    'menu-item-bg-active': 'bg-active-raised',
}

# Focus ring: points to the Foundation's composite shadow, like
# `button-*-ring`. The color is only extracted for measuring, in RING_INK below.
RING = {
    'ring': 'focusRing.default',
}

RING_INK = {
    'ring': 'shadow-focus-default',
}

# Elevation: height, not state (Elevation/3).
SHADOW = {
    'menu-shadow': 'elevation.3',
}

# ------------------------------------------------------------- geometry
GEOM = {
    'gap':               'space.8',           # item -> separator -> item
    'ring-radius':       'radius.sm',         # ring corner on link and `…`
    'menu-padding':      'space.8',
    'menu-gap':          'space.8',           # between menu items
    'menu-offset':       'space.8',           # `...` -> menu
    'menu-radius':       'radius.xl',
    'menu-border-width': 'border.width.1',
}

TYPE = {
    'label-font': 'type.styles.label-md',
}

# The ONLY exception to "every token is an alias" (the same as the Sidebar, the
# Modal and the Drawer): the Foundation has no container width scale. A minimum,
# not a fixed width: the menu grows with the page name (2026-10-08).
WIDTH = {
    'menu-min-width': 108,
}

PENDING = {
    'region-border': (
        'The menu border (`border-default`) gives 1.57:1 in light and 2.42:1 in dark against the '
        'canvas, and 1.47:1 / 1.98:1 against a page in `bg-surface`. The 3:1 of WCAG 1.4.11 '
        'applies to the outline of CONTROLS; the menu is a content box, recognized by its items '
        'and by the Elevation/3 shadow. Same reasoning as the Sidebar and the Card. DO NOT "fix" '
        'it by darkening.'
    ),
}

# Backgrounds the breadcrumb sits on. They are not Breadcrumb tokens.
PAGES = {
    'canvas':  'bg-canvas',
    'surface': 'bg-surface',
}

# Menu item label: comes from the Tab Square (tab-label, tab-label-hover).
TAB_INK = {
    'item':       'text-secondary',
    'item-hover': 'text-primary',
}

# (role, fg, background(s), floor, exception)
COMBOS = [
    ('link',             'link',        ('canvas', 'surface'),    4.5, None),
    ('current-page',     'current',     ('canvas', 'surface'),    4.5, None),
    ('more',             'more',        ('canvas', 'surface'),    4.5, None),
    ('menu-item',        'item',        'menu-bg',                4.5, None),
    ('menu-item-hover',  'item-hover',  'menu-item-bg-hover',     4.5, None),
    ('menu-item-active', 'item-hover',  'menu-item-bg-active',    4.5, None),
    ('trail-ring',       'ring',        ('canvas', 'surface'),    3.0, None),
    ('menu-ring',        'ring',        'menu-bg',                3.0, None),
    ('menu-border',      'menu-border', ('canvas', 'surface'),    3.0, 'region-border'),
]


# ------------------------------------------------------------------ gate
def ink(role):
    """The color semantic behind a role - following the ring down to the color."""
    for table in (PAGES, RING_INK, TAB_INK):
        if role in table:
            return table[role]
    return COLOR[role]


def contrast_rows():
    rows = []
    for what, fg, bgs, min_ratio, exc in COMBOS:
        if isinstance(bgs, str):
            bgs = (bgs,)
        for theme, i in (('light', 0), ('dark', 1)):
            for bg in bgs:
                a, b = SEM[ink(fg)][i], SEM[ink(bg)][i]
                ratio = round(cr(a, b), 2)
                rows.append({'theme': theme, 'what': f'{what}/{bg}', 'fg': a, 'bg': b,
                             'ratio': ratio, 'min': min_ratio,
                             'pass': ratio >= min_ratio, 'exception': exc})
    return rows


def run():
    alias, resolved, problems = {}, {}, []

    for role, ref in COLOR.items():
        name = f'breadcrumb-{role}'
        alias[name] = ref
        if ref.startswith('#'):
            problems.append(f'{name}: loose hex ({ref})')
        elif ref not in SEM:
            problems.append(f'{name}: points to {ref}, which does not exist in the semantic layer')
        else:
            resolved[name] = {'light': SEM[ref][0], 'dark': SEM[ref][1]}

    for group in (RING, SHADOW):
        for role, ref in group.items():
            name = f'breadcrumb-{role}'
            alias[name] = ref
            try:
                v = resolve_foundation(ref)
                resolved[name] = {'light': v['light'], 'dark': v['dark']}
            except KeyError:
                problems.append(f'{name}: {ref} does not exist in the Foundation')

    for group in (GEOM, TYPE):
        for role, ref in group.items():
            name = f'breadcrumb-{role}'
            alias[name] = ref
            try:
                resolved[name] = resolve_foundation(ref)
            except KeyError:
                problems.append(f'{name}: {ref} does not exist in the Foundation')

    # Named exception: a loose value is only accepted for this name.
    for role, px in WIDTH.items():
        name = f'breadcrumb-{role}'
        alias[name] = f'{px}px'
        resolved[name] = px

    if problems:
        print(f'{len(problems)} TOKEN(S) FAIL THE ALIAS GATE:')
        for p in problems:
            print('   ', p)
        return 1

    rows = contrast_rows()
    fails = [r for r in rows if not r['pass'] and not r['exception']]
    excs = [r for r in rows if not r['pass'] and r['exception']]

    print('=' * 74)
    print('BREADCRUMB TOKEN LAYER')
    print('=' * 74)
    for name in sorted(alias):
        print(f'  {name:<34} -> {alias[name]}')
    print('-' * 74)
    for r in rows:
        tag = 'OK  ' if r['pass'] else ('EXC ' if r['exception'] else 'FAIL')
        print(f'  {tag} {r["what"]:<34} {r["theme"]:<5} {r["fg"]} / {r["bg"]}  {r["ratio"]}:1 (floor {r["min"]})')
    print(f'contrast: {len(rows)} measurements  |  pass: {len(rows) - len(fails) - len(excs)}  |  '
          f'declared exceptions: {len(excs)}  |  fail: {len(fails)}')
    if fails:
        print(f'{len(fails)} COMBINATION(S) FAIL THE CONTRAST GATE')
        return 1
    n_lit = len(WIDTH)
    print(f'{len(alias)} tokens: {len(alias) - n_lit} aliases of the Foundation, {n_lit} width with a '
          f'declared value (the same exception as the Sidebar, the Modal and the Drawer).')

    out = {
        'meta': {
            'component': 'Breadcrumb',
            'version': '0.1.0',
            'foundation': FOUND['meta']['version'],
            'figmaNode': '339:3785 + 339:4046',
            'figmaCollection': '4. Components',
            'note': (
                'Navigation trail: links in text-secondary, current page in text-brand (text, not '
                'a link), chevron 16 separator in text-secondary, Label/md, gap 8. With 5 levels '
                'or more the middle ones go into the `...` menu (bg-surface-raised, border, xl '
                'radius, Elevation/3, Tab Square items with -raised hover). No hover on the '
                'trail: only the cursor changes. One contrast exception in pending.'
            ),
        },
        'alias': alias,
        'resolved': resolved,
        'contrast': rows,
        'pending': PENDING,
    }
    json.dump(out, open(comp_out('breadcrumb', 'tokens.json'), 'w'), indent=2, ensure_ascii=False)
    print('\nbuild/components/breadcrumb/tokens.json written')
    write_css(alias)
    return 0


# ---------------------------------------------------------------- css
def write_css(alias):
    L = []
    w = L.append
    w('/* AL Design System - Breadcrumb tokens (with _breadcrumb-more)')
    w(' * GENERATED by src/components/breadcrumb/tokens.py. Do not edit by hand.')
    w(' */')
    w('')
    w(':root {')
    w('')
    w('  /* trail - the theme switches on :root */')
    for role in ('link', 'current', 'separator', 'more'):
        w(f'  --al-breadcrumb-{role}: {css_ref(COLOR[role])};')
    w('')
    w('  /* ... menu - -raised hover and pressed (the menu lives on surface-raised) */')
    for role in ('menu-bg', 'menu-border', 'menu-item-bg-hover', 'menu-item-bg-active'):
        w(f'  --al-breadcrumb-{role}: {css_ref(COLOR[role])};')
    w('')
    w('  /* focus ring - points to the composite shadow, not the raw color */')
    for role, ref in RING.items():
        w(f'  --al-breadcrumb-{role}: {css_ref(ref)};')
    w('')
    w('  /* menu elevation - height, not state */')
    for role, ref in SHADOW.items():
        w(f'  --al-breadcrumb-{role}: {css_ref(ref)};')
    w('')
    w('  /* geometry */')
    for role, ref in GEOM.items():
        w(f'  --al-breadcrumb-{role}: {css_ref(ref)};')
    w('')
    w('  /* menu minimum width - declared value, no scale in the Foundation */')
    for role, px in WIDTH.items():
        w(f'  --al-breadcrumb-{role}: {px}px;')
    w('')
    w('  /* typography - one style becomes four vars */')
    for role, ref in TYPE.items():
        style = resolve_foundation(ref)
        key = size_key(style[1])
        prefix = f'--al-breadcrumb-{role}'.replace('-font', '')
        w(f'  {prefix}-font-size: var(--al-font-size-{key});')
        w(f'  {prefix}-line-height: var(--al-line-height-{key});')
        w(f'  {prefix}-font-weight: {style[3]};')
        w(f'  {prefix}-tracking: {style[4]};')
    w('}')
    w('')
    text = '\n'.join(L)
    missing = [n for n in alias if not n.endswith('-font') and f'--al-{n}:' not in text]
    if missing:
        raise AssertionError(f'tokens missing from the CSS: {missing}')
    save_css('breadcrumb', text)


if __name__ == '__main__':
    sys.exit(run())
