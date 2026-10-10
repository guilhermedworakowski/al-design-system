"""
Token layer for the Toast.

The rule of this layer: nothing here invents a value. Every token points to a
Foundation token by NAME. The ONLY exceptions are the maximum width (WIDTH)
and the time on screen (TIMEOUT), declared, named and locked by the gate: the
Foundation has no container width scale nor a wait time scale.

Naming:
  code  -> toast-success-border   (hyphen)
  Figma -> border/success         (folder)
Figma has no variable per component: the node binds the semantic or
Foundation variable the token points to. The exception is a value the
Foundation lacks, which lives in the `4. Components` collection
(toast-max-width -> toast/max-width).
Hyphen in code, folder in Figma: they are different layers. Never
collapse one into the other.

SECOND COMPONENT OF TIER 5 (2026-10-08)

  Component set `Toast`, node 373:5287. 4 `Status` variants (Success /
  Warning / Error / Info) and the description boolean. Icon 20 aligned to the
  top + Label/md title + optional Body/sm description + X (Ghost sm Icon
  Button). Background bg-surface-raised, 1px border in the status color, lg
  radius, Elevation/3, padding 12, gap 8, 4 between title and description,
  maximum width 380.

  Scope decisions: icon at the top and 20; a triangle on Warning and a circle
  with an exclamation mark on Error; optional description; no action; no
  Neutral; Success/Info disappear in 6s and Warning/Error stay; one at a
  time, bottom right corner 16 from the edges; a queue.

THE "error" STATUS USES THE "danger" SEMANTIC

  The same mapping as the Tag: the status name is the product's, the color is
  the Foundation's.

THE BORDER IS INSIDE

  In Figma the stroke doesn't enter the layout: 12 + 20 + 4 + 20 + 12 = 68
  with the border over the padding. The CSS reproduces it with
  `calc(padding - border-width)`, like the Button and the Input.

NO TOKEN, ON PURPOSE

  Height: comes from the math (68 with a description, 60 without - the 36 X
  rules). Icon: `icon-size-20` straight from the Foundation (rule from the Tag
  and the Tooltip). X: it is the Ghost sm Icon Button; on bg-surface-raised
  the hover uses `bg-hover-raised` / `bg-active-raised` (lesson from Modal
  0.18.1), no new token. Stacking: the toast lives in the top layer
  (popover), so there is no z-index.
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
    'bg':          'bg-surface-raised',
    'title':       'text-primary',
    'description': 'text-secondary',
}

# Status -> semantic. The icon and the border carry the status; the icon is
# the clue that doesn't depend on color (Spectrum), the border is decorative
# and passes 3:1 all the same.
STATUS = {
    'success': 'success',
    'warning': 'warning',
    'error':   'danger',
    'info':    'info',
}
for status, sem in STATUS.items():
    COLOR[f'{status}-icon'] = f'text-{sem}'
    COLOR[f'{status}-border'] = f'border-{sem}'

# Elevation: height, not state. The same as the Tooltip.
SHADOW = {
    'shadow': 'elevation.3',
}

# ------------------------------------------------------------- geometry
GEOM = {
    'padding':      'space.12',
    'gap':          'space.8',              # icon -> text -> X
    'text-gap':     'space.4',              # title -> description
    'radius':       'radius.lg',
    'border-width': 'border.width.1',
    'offset':       'space.16',             # box -> screen edge
}

TYPE = {
    'title-font':       'type.styles.label-md',
    'description-font': 'type.styles.body-sm',
}

# Motion: popup = what appears small over the screen (Tooltip and Toast).
MOTION = {
    'duration':     'motion.duration.popup',
    'easing-enter': 'motion.easing.enter',
    'easing-exit':  'motion.easing.exit',
}

# Exception 1 (the same as the Sidebar, the Modal, the Drawer and the Tooltip):
# the Foundation has no container width scale. A maximum, not a fixed width -
# on a phone the box shrinks until the offset is left on both sides.
WIDTH = {
    'max-width': 380,
}

# Exception 2 (2026-10-08): the time on screen of Success and Info stays in the
# component, like the Tooltip delays. Warning and Error don't disappear.
TIMEOUT = {
    'timeout': 6000,
}

PENDING = {}

# Screens the toast appears over. They are not Toast tokens.
PAGES = {
    'canvas':  'bg-canvas',
    'surface': 'bg-surface',
}

# (role, fg, background(s), floor, exception)
COMBOS = [
    ('title',       'title',       'bg', 4.5, None),
    ('description', 'description', 'bg', 4.5, None),
]
for status in STATUS:
    COMBOS.append((f'{status}/icon', f'{status}-icon', 'bg', 3.0, None))
    COMBOS.append((f'{status}/border', f'{status}-border', ('bg', 'canvas', 'surface'), 3.0, None))


# ------------------------------------------------------------------ gate
def ink(role):
    return PAGES.get(role) or COLOR[role]


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
        name = f'toast-{role}'
        alias[name] = ref
        if ref.startswith('#'):
            problems.append(f'{name}: loose hex ({ref})')
        elif ref not in SEM:
            problems.append(f'{name}: points to {ref}, which does not exist in the semantic layer')
        else:
            resolved[name] = {'light': SEM[ref][0], 'dark': SEM[ref][1]}

    for role, ref in SHADOW.items():
        name = f'toast-{role}'
        alias[name] = ref
        try:
            v = resolve_foundation(ref)
            resolved[name] = {'light': v['light'], 'dark': v['dark']}
        except KeyError:
            problems.append(f'{name}: {ref} does not exist in the Foundation')

    for group in (GEOM, TYPE, MOTION):
        for role, ref in group.items():
            name = f'toast-{role}'
            alias[name] = ref
            try:
                resolved[name] = resolve_foundation(ref)
            except KeyError:
                problems.append(f'{name}: {ref} does not exist in the Foundation')

    # Named exceptions: a loose value is only accepted for these names.
    for role, px in WIDTH.items():
        alias[f'toast-{role}'] = f'{px}px'
        resolved[f'toast-{role}'] = px
    for role, ms in TIMEOUT.items():
        alias[f'toast-{role}'] = f'{ms}ms'
        resolved[f'toast-{role}'] = ms

    if problems:
        print(f'{len(problems)} TOKEN(S) FAIL THE ALIAS GATE:')
        for p in problems:
            print('   ', p)
        return 1

    rows = contrast_rows()
    fails = [r for r in rows if not r['pass'] and not r['exception']]
    excs = [r for r in rows if not r['pass'] and r['exception']]

    print('=' * 74)
    print('TOAST TOKEN LAYER')
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
    n_lit = len(WIDTH) + len(TIMEOUT)
    print(f'{len(alias)} tokens: {len(alias) - n_lit} aliases of the Foundation, {n_lit} with a '
          f'declared value (maximum width and time on screen).')

    out = {
        'meta': {
            'component': 'Toast',
            'version': '0.1.0',
            'foundation': FOUND['meta']['version'],
            'figmaNode': '373:5287',
            'figmaCollection': '4. Components',
            'note': (
                'Background bg-surface-raised, 1px border and icon 20 in the status color (error '
                'uses the danger semantic), Label/md title, optional Body/sm description, padding '
                '12, gap 8, lg radius, Elevation/3, maximum width 380, 16 from the screen edges. '
                'Success and Info disappear in 6s (paused on hover and focus); Warning and Error '
                'stay. One at a time, in a queue. No contrast exception.'
            ),
        },
        'alias': alias,
        'resolved': resolved,
        'contrast': rows,
        'pending': PENDING,
    }
    json.dump(out, open(comp_out('toast', 'tokens.json'), 'w'), indent=2, ensure_ascii=False)
    print('\nbuild/components/toast/tokens.json written')
    write_css(alias)
    return 0


# ---------------------------------------------------------------- css
def write_css(alias):
    L = []
    w = L.append
    w('/* AL Design System - Toast tokens')
    w(' * GENERATED by src/components/toast/tokens.py. Do not edit by hand.')
    w(' */')
    w('')
    w(':root {')
    w('')
    w('  /* color - box and text */')
    for role in ('bg', 'title', 'description'):
        w(f'  --al-toast-{role}: {css_ref(COLOR[role])};')
    w('')
    w('  /* color - status: icon and border */')
    for status in STATUS:
        for part in ('icon', 'border'):
            role = f'{status}-{part}'
            w(f'  --al-toast-{role}: {css_ref(COLOR[role])};')
    w('')
    w('  /* elevation - height, not state */')
    for role, ref in SHADOW.items():
        w(f'  --al-toast-{role}: {css_ref(ref)};')
    w('')
    w('  /* geometry */')
    for role, ref in GEOM.items():
        w(f'  --al-toast-{role}: {css_ref(ref)};')
    w('')
    w('  /* maximum width - declared value, no scale in the Foundation */')
    for role, px in WIDTH.items():
        w(f'  --al-toast-{role}: {px}px;')
    w('')
    w('  /* motion */')
    for role, ref in MOTION.items():
        w(f'  --al-toast-{role}: {css_ref(ref)};')
    w('')
    w('  /* time on screen of Success and Info - declared value. Read by toast.js */')
    for role, ms in TIMEOUT.items():
        w(f'  --al-toast-{role}: {ms}ms;')
    w('')
    w('  /* typography - each style becomes four vars */')
    for role, ref in TYPE.items():
        style = resolve_foundation(ref)
        key = size_key(style[1])
        prefix = f'--al-toast-{role}'.replace('-font', '')
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
    save_css('toast', text)


if __name__ == '__main__':
    sys.exit(run())
