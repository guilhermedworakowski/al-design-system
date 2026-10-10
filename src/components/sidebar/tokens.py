"""
Token layer for the Sidebar.

The rule of this layer: nothing here invents a value. Every token points to a
Foundation token by NAME. The ONLY exception is the width (WIDTH, below),
declared, named and locked by the gate - the same as the Modal and the Drawer:
the Foundation has no container width scale.

Naming:
  code  -> sidebar-profile-gap     (hyphen)
  Figma -> space/8                 (folder)
Figma has no variable per component: the node binds the semantic or
Foundation variable the token points to. The exception is a value the
Foundation lacks, which lives in the `4. Components` collection
(sidebar-width -> sidebar/width).
Hyphen in code, folder in Figma: they are different layers. Never
collapse one into the other.

FIRST COMPONENT OF TIER 4 (2026-10-08)

  Component `sidebar`, node 339:2916, page `Tier 4` in Figma. One variant,
  296 wide. Profile header (Avatar md + name + e-mail + Ghost sm Icon
  Button), `content` slot with the navigation groups, and the Help section
  (group label + items). Props: `Avatar`, `Support area`, `Support` (text),
  `Item 1..3`, `content` (slot).

  Scope decisions: `bg-canvas` background with a right border in
  `border-default`, e-mail in `text-secondary`, profile with an Icon Button,
  items without icons, no nesting, screen height with only the body
  scrolling, on a phone it becomes a modal panel from the left reusing the
  Drawer, no collapsed mode.

THE ITEM IS THE TAB

  Each item is a full-width Tab Square (Tab rule 4). Its pairs were already
  measured on `bg-canvas` in components/tab/tokens.py, and the profile button
  in components/icon-button/tokens.py. That is why the sidebar background is
  the canvas: with `bg-surface-raised` the hover disappeared in dark (1.00:1).

NO TOKEN, ON PURPOSE

  Height: 100dvh (the 1024 in Figma is only the frame). Radius: none, the
  sidebar sticks to the screen edge. Item, Avatar and Icon Button: their own
  components' tokens. Phone: the Drawer's scrim, duration and shadow, in
  sidebar.css.
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
    'bg':          'bg-canvas',
    'border':      'border-default',      # the Divider's color
    'name':        'text-primary',
    'email':       'text-secondary',
    'group-label': 'text-secondary',
}

# ------------------------------------------------------------- geometry
GEOM = {
    'border-width':      'border.width.1',
    'padding':           'space.24',
    'gap':               'space.24',      # profile / body / help, and between groups
    'profile-gap':       'space.8',       # avatar -> texts
    'profile-text-gap':  'space.4',       # name -> e-mail, texts -> button
    'group-gap':         'space.16',      # group label -> items
    'item-gap':          'space.8',       # between items
}

TYPE = {
    'name-font':        'type.styles.heading-xs',
    'email-font':       'type.styles.body-sm',
    'group-label-font': 'type.styles.code-md',
}

# Styles that don't use the default family (sans).
MONO = {'group-label-font'}

# The ONLY exception to "every token is an alias" (the same as the Modal and the
# Drawer): the Foundation has no container width scale. When it exists, this
# becomes an alias.
WIDTH = {
    'width': 296,
}

PENDING = {
    'region-border': (
        'The line on the right (`border-default`) gives 1.57:1 in light and 2.42:1 in dark '
        'against the sidebar, and 1.47:1 / 1.98:1 against a page in `bg-surface`. The 3:1 of '
        'WCAG 1.4.11 applies to the outline of CONTROLS; the sidebar is a region of the page, '
        'recognized by its content and, by the screen reader, by the <nav> name. Same reasoning '
        'as the Divider and the Card border (2026-10-08). DO NOT "fix" it by darkening.'
    ),
}

# Backgrounds the sidebar sits next to. They are not Sidebar tokens.
PAGES = {
    'canvas':  'bg-canvas',
    'surface': 'bg-surface',
}

# (role, fg, background(s), floor, exception)
COMBOS = [
    ('name',         'name',        'bg',                 4.5, None),
    ('email',        'email',       'bg',                 4.5, None),
    ('group-label',  'group-label', 'bg',                 4.5, None),
    ('border',       'border',      ('bg', 'surface'),    3.0, 'region-border'),
]


# ------------------------------------------------------------------ gate
def ink(role):
    if role in PAGES:
        return PAGES[role]
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
        name = f'sidebar-{role}'
        alias[name] = ref
        if ref.startswith('#'):
            problems.append(f'{name}: loose hex ({ref})')
        elif ref not in SEM:
            problems.append(f'{name}: points to {ref}, which does not exist in the semantic layer')
        else:
            resolved[name] = {'light': SEM[ref][0], 'dark': SEM[ref][1]}

    for group in (GEOM, TYPE):
        for role, ref in group.items():
            name = f'sidebar-{role}'
            alias[name] = ref
            try:
                resolved[name] = resolve_foundation(ref)
            except KeyError:
                problems.append(f'{name}: {ref} does not exist in the Foundation')

    # Named exception: a loose value is only accepted for this name.
    for role, px in WIDTH.items():
        name = f'sidebar-{role}'
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
    print('SIDEBAR TOKEN LAYER')
    print('=' * 74)
    for name in sorted(alias):
        print(f'  {name:<30} -> {alias[name]}')
    print('-' * 74)
    for r in rows:
        tag = 'OK  ' if r['pass'] else ('EXC ' if r['exception'] else 'FAIL')
        print(f'  {tag} {r["what"]:<24} {r["theme"]:<5} {r["fg"]} / {r["bg"]}  {r["ratio"]}:1 (floor {r["min"]})')
    print(f'contrast: {len(rows)} measurements  |  pass: {len(rows) - len(fails) - len(excs)}  |  '
          f'declared exceptions: {len(excs)}  |  fail: {len(fails)}')
    if fails:
        print(f'{len(fails)} COMBINATION(S) FAIL THE CONTRAST GATE')
        return 1
    n_lit = len(WIDTH)
    print(f'{len(alias)} tokens: {len(alias) - n_lit} aliases of the Foundation, {n_lit} width with a '
          f'declared value (the same exception as the Modal and the Drawer).')

    out = {
        'meta': {
            'component': 'Sidebar',
            'version': '0.1.0',
            'foundation': FOUND['meta']['version'],
            'figmaNode': '339:2916',
            'figmaCollection': '4. Components',
            'note': (
                'Fixed side navigation, 296 wide, bg-canvas background with a right border in '
                'border-default. Profile, group slot and Help section; items are full-width Tab '
                'Square. Screen height, only the body scrolls. On a phone it becomes a modal '
                'panel from the left (the Drawer mechanism). One contrast exception in pending.'
            ),
        },
        'alias': alias,
        'resolved': resolved,
        'contrast': rows,
        'pending': PENDING,
    }
    json.dump(out, open(comp_out('sidebar', 'tokens.json'), 'w'), indent=2, ensure_ascii=False)
    print('\nbuild/components/sidebar/tokens.json written')
    write_css(alias)
    return 0


# ---------------------------------------------------------------- css
def write_css(alias):
    L = []
    w = L.append
    w('/* AL Design System - Sidebar tokens')
    w(' * GENERATED by src/components/sidebar/tokens.py. Do not edit by hand.')
    w(' */')
    w('')
    w(':root {')
    w('')
    w('  /* color - the theme switches on :root */')
    for role, ref in COLOR.items():
        w(f'  --al-sidebar-{role}: {css_ref(ref)};')
    w('')
    w('  /* geometry */')
    for role, ref in GEOM.items():
        w(f'  --al-sidebar-{role}: {css_ref(ref)};')
    w('')
    w('  /* width - declared value, no scale in the Foundation (the same exception as the Modal and the Drawer) */')
    for role, px in WIDTH.items():
        w(f'  --al-sidebar-{role}: {px}px;')
    w('')
    w('  /* typography - one style becomes four vars (five on the label, which is mono) */')
    for role, ref in TYPE.items():
        style = resolve_foundation(ref)
        key = size_key(style[1])
        prefix = f'--al-sidebar-{role}'.replace('-font', '')
        if role in MONO:
            w(f'  {prefix}-font-family: var(--al-font-mono);')
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
    save_css('sidebar', text)


if __name__ == '__main__':
    sys.exit(run())
