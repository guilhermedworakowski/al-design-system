"""
Token layer for the Drawer.

The rule of this layer: nothing here invents a value. Every token points to a
Foundation token by NAME. The ONLY exception is the three widths (WIDTH,
below), and it is declared, named and locked by the gate. It is the Modal's
exception, repeated on purpose: each component stays independent and, when the
Foundation gains a container width scale, the six tokens become aliases at once.

Naming:
  code  -> drawer-bg               (hyphen)
  Figma -> bg/surface-raised       (folder)
Figma has no variable per component: the node binds the semantic or
Foundation variable the token points to. The exception is a value the
Foundation lacks, which lives in the `4. Components` collection
(drawer-width-md -> drawer/width/md).
Hyphen in code, folder in Figma: they are different layers. Never
collapse one into the other.

SIXTH AND LAST COMPONENT OF TIER 3 (2026-10-07)

  Frame `drawer`, node 306:2264, page `Tier 3` in Figma. 3 variants, axis
  `Size` (sm 320 / md 480 / lg 640). Props: `Title`, `Close button` (bool),
  `Actions` (bool) and the `content` slot. Native `<dialog>` markup with
  `showModal()`. Right side only. X button kept. Closes on the scrim only
  with no fields, like the Modal. Phone: 100vw - drawer-margin. Shadow and
  dark mode as in the Modal. No divider.

SCRIM

  `bg-scrim` was born in the Foundation for the Modal and serves the Drawer.
  It is the only semantic with transparency (#RRGGBBAA). That is why it is
  not in the Foundation's PAIRS: its contrast only exists COMPOSITED on the
  page, and this file is what measures it.

NO TOKEN, ON PURPOSE

  Enter and exit: the panel slides its own width (translateX(100%)),
  entering from right to left and exiting from left to right. There is no
  offset value to keep, so there is no `drawer-offset`.

  Height: 100dvh (the screen height; the 1024 in Figma is only the sample
  frame). Width on a phone: 100vw - drawer-margin. Footer buttons and the X:
  Button and Icon Button tokens. Footer with stretching buttons: layout.
  Easing: easing-enter on opening, easing-exit on closing, straight from the
  Foundation.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'tools'))
from paths import FOUNDATION_SRC, TOKENS_JSON, comp_out  # noqa: E402
sys.path.insert(0, FOUNDATION_SRC)

from palette import SEM                     # noqa: E402
from tokenlib import resolve_foundation, css_ref, size_key, save_css  # noqa: E402
from color import cr                      # noqa: E402
from contrast import composite            # noqa: E402

FOUND = json.load(open(TOKENS_JSON))   # noqa: E402

# ------------------------------------------------------------- color
COLOR = {
    'bg':     'bg-surface-raised',
    'title':  'text-primary',
    'scrim':  'bg-scrim',               # with transparency - see the SCRIM note
}

# Elevation is height, not state: it stays out of the color layer.
SHADOW = {
    'shadow': 'elevation.5',
}

# ------------------------------------------------------------- geometry
GEOM = {
    'padding': 'space.24',
    'gap':     'space.24',              # header / body / actions and between the buttons
    'margin':  'space.16',              # gap on the left on a phone
    'radius':  'radius.2xl',            # only on the inner corners (left)
}

# Motion: the token points to the Foundation duration (panel = what covers
# the screen). The easing doesn't become a component token.
MOTION = {
    'duration': 'motion.duration.panel',
}

TYPE = {
    'title-font': 'type.styles.heading-sm',
}

# The ONLY exception to "every token is an alias" (the Modal's, repeated on
# 2026-10-07): the Foundation has no container width scale (space ends at 96).
# The values come from Figma. When the scale exists, these three become aliases.
WIDTH = {
    'width-sm': 320,
    'width-md': 480,
    'width-lg': 640,
}

PENDING = {
    'card-not-separated-from-scrim-in-dark': (
        'In dark the panel (bg-surface-raised, neutral-800) against the page dimmed by the scrim '
        'sits at ~1.8:1, below the 3:1 of 1.4.11. The separation is carried by the panel '
        'LIGHTENING (the Foundation\'s primary cue in dark) plus the shadow. Raising the opacity '
        'doesn\'t solve it: at 72% the pair goes to 1.88:1, because the background is already '
        'almost black. Same exception as the Modal (no outline in dark), applying only to the '
        'Drawer\'s inner edge. Approved on 2026-10-07. DO NOT "fix" it by darkening.'
    ),
}

# Backgrounds the Drawer opens over. They are not Drawer tokens.
PAGES = {
    'canvas':  'bg-canvas',
    'surface': 'bg-surface',
}

# (role, fg, bg, floor, exception). `scrim:<page>` = page with the scrim composited.
# The close X uses text-primary on the same background as the title: the pair is the same.
COMBOS = [
    ('title',                   'title', 'bg',            4.5, None),
    ('panel-on-dimmed-canvas',  'bg',    'scrim:canvas',  3.0, 'card-not-separated-from-scrim-in-dark'),
    ('panel-on-dimmed-surface', 'bg',    'scrim:surface', 3.0, 'card-not-separated-from-scrim-in-dark'),
]


# ------------------------------------------------------------------ gate
def color_of(role, i):
    """Rendered color of a role in theme i (0 light, 1 dark)."""
    if role.startswith('scrim:'):
        page = PAGES[role.split(':')[1]]
        return composite(SEM[COLOR['scrim']][i], SEM[page][i])
    return SEM[COLOR[role]][i]


def contrast_rows():
    rows = []
    for what, fg, bg, min_ratio, exc in COMBOS:
        for theme, i in (('light', 0), ('dark', 1)):
            a, b = color_of(fg, i), color_of(bg, i)
            ratio = round(cr(a, b), 2)
            rows.append({'theme': theme, 'what': what, 'fg': a, 'bg': b,
                         'ratio': ratio, 'min': min_ratio,
                         'pass': ratio >= min_ratio, 'exception': exc})
    return rows


def run():
    alias, resolved, problems = {}, {}, []

    for role, ref in COLOR.items():
        name = f'drawer-{role}'
        alias[name] = ref
        if ref.startswith('#'):
            problems.append(f'{name}: loose hex ({ref})')
        elif ref not in SEM:
            problems.append(f'{name}: points to {ref}, which does not exist in the semantic layer')
        else:
            resolved[name] = {'light': SEM[ref][0], 'dark': SEM[ref][1]}

    for group in (SHADOW, GEOM, MOTION, TYPE):
        for role, ref in group.items():
            name = f'drawer-{role}'
            alias[name] = ref
            try:
                resolved[name] = resolve_foundation(ref)
            except KeyError:
                problems.append(f'{name}: {ref} does not exist in the Foundation')

    # Named exception: a loose value is only accepted for these three names.
    for role, px in WIDTH.items():
        name = f'drawer-{role}'
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
    print('DRAWER TOKEN LAYER')
    print('=' * 74)
    for name in sorted(alias):
        print(f'  {name:<22} -> {alias[name]}')
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
    print(f'{len(alias)} tokens: {len(alias) - n_lit} aliases of the Foundation, {n_lit} widths with '
          f'a declared value (the same exception as the Modal).')

    out = {
        'meta': {
            'component': 'Drawer',
            'version': '0.1.0',
            'foundation': FOUND['meta']['version'],
            'figmaNode': '306:2264',
            'figmaCollection': '4. Components',
            'sizes': ['sm', 'md', 'lg'],
            'note': (
                'Native <dialog> with showModal(), right side only. Background bg-surface-raised, '
                'shadow elevation.5, scrim bg-scrim. X button kept, no dividers; only the body '
                'scrolls. Enters from right to left and exits from left to right. Three widths '
                'with a declared value. One contrast exception in pending.'
            ),
        },
        'alias': alias,
        'resolved': resolved,
        'contrast': rows,
        'pending': PENDING,
    }
    json.dump(out, open(comp_out('drawer', 'tokens.json'), 'w'), indent=2, ensure_ascii=False)
    print('\nbuild/components/drawer/tokens.json written')
    write_css(alias)
    return 0


# ---------------------------------------------------------------- css
def write_css(alias):
    L = []
    w = L.append
    w('/* AL Design System - Drawer tokens')
    w(' * GENERATED by src/components/drawer/tokens.py. Do not edit by hand.')
    w(' */')
    w('')
    w(':root {')
    w('')
    w('  /* color - the scrim has transparency; the theme switches on :root */')
    for role in COLOR:
        w(f'  --al-drawer-{role}: {css_ref(COLOR[role])};')
    w('')
    w('  /* elevation */')
    for role, ref in SHADOW.items():
        w(f'  --al-drawer-{role}: {css_ref(ref)};')
    w('')
    w('  /* geometry */')
    for role, ref in GEOM.items():
        w(f'  --al-drawer-{role}: {css_ref(ref)};')
    w('')
    w('  /* width - declared value, no scale in the Foundation (same as the Modal) */')
    for role, px in WIDTH.items():
        w(f'  --al-drawer-{role}: {px}px;')
    w('')
    w('  /* motion - easing comes straight from the Foundation */')
    for role, ref in MOTION.items():
        w(f'  --al-drawer-{role}: {css_ref(ref)};')
    w('')
    w('  /* typography - one style becomes four vars */')
    for role, ref in TYPE.items():
        style = resolve_foundation(ref)
        key = size_key(style[1])
        prefix = f'--al-drawer-{role}'.replace('-font', '')
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
    save_css('drawer', text)


if __name__ == '__main__':
    sys.exit(run())
