"""
Token layer for the Tooltip.

The rule of this layer: nothing here invents a value. Every token points to a
Foundation token by NAME. The ONLY exceptions are the maximum width (WIDTH)
and the two wait times (DELAY), declared, named and locked by the gate: the
Foundation has no container width scale nor a delay scale.

Naming:
  code  -> tooltip-padding-y      (hyphen)
  Figma -> space/8                (folder)
Figma has no variable per component: the node binds the semantic or
Foundation variable the token points to. The exception is a value the
Foundation lacks, which lives in the `4. Components` collection
(tooltip-max-width -> tooltip/max-width).
Hyphen in code, folder in Figma: they are different layers. Never
collapse one into the other.

FIRST COMPONENT OF TIER 5 (2026-10-08)

  `tooltip` - COMPONENT 373:5340 (no variants). Icon 20 + Body/sm text,
  inverted background, Elevation/3, padding 8 x 12, gap 8, lg radius,
  maximum width 280.

  Scope decisions: inverted background; 14/20 text and 8 x 12 padding; the
  icon is ALWAYS present; no arrow, 4 from the trigger; maximum width 280;
  the delay lives in the component and not in the Foundation; no border.

NO TOKEN, ON PURPOSE

  Height: comes from padding-y x 2 + the Body/sm line height (36). Icon:
  `icon-size-20` straight from the Foundation (rule from the Tag and the
  Breadcrumb); the color follows the text through `currentColor`. Stacking:
  the tooltip lives in the top layer (popover), so there is no z-index.
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
    'bg':   'bg-inverse',
    'text': 'text-inverse',               # the icon inherits through currentColor
}

# Elevation: height, not state. The same as the Breadcrumb menu.
SHADOW = {
    'shadow': 'elevation.3',
}

# ------------------------------------------------------------- geometry
GEOM = {
    'padding-y': 'space.8',
    'padding-x': 'space.12',
    'gap':       'space.8',               # icon -> text
    'offset':    'space.4',               # trigger -> tooltip (no arrow)
    'radius':    'radius.lg',
}

TYPE = {
    'font': 'type.styles.body-sm',
}

# Motion: popup = what appears small over the screen (Tooltip and Toast).
MOTION = {
    'duration':     'motion.duration.popup',
    'easing-enter': 'motion.easing.enter',
    'easing-exit':  'motion.easing.exit',
}

# Exception 1 (the same as the Sidebar, the Modal, the Drawer and the
# Breadcrumb): the Foundation has no container width scale. A maximum, not a
# fixed width.
WIDTH = {
    'max-width': 280,
}

# Exception 2 (2026-10-08): the delay stays in the component. If a second
# component needs a delay, it moves up to the Foundation.
#   delay-show - hover wait before opening (on focus it opens at once)
#   delay-hide - slack for the pointer to go from the trigger to the tooltip (WCAG 1.4.13)
DELAY = {
    'delay-show': 500,
    'delay-hide': 100,
}

PENDING = {}

# Backgrounds the tooltip appears over. They are not Tooltip tokens.
PAGES = {
    'canvas':  'bg-canvas',
    'surface': 'bg-surface',
    'raised':  'bg-surface-raised',
}

# (role, fg, background(s), floor, exception)
COMBOS = [
    ('text',  'text', 'bg',                              4.5, None),
    ('icon',  'text', 'bg',                              3.0, None),
    ('box',   'bg',   ('canvas', 'surface', 'raised'),   3.0, None),
]


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
        name = f'tooltip-{role}'
        alias[name] = ref
        if ref.startswith('#'):
            problems.append(f'{name}: loose hex ({ref})')
        elif ref not in SEM:
            problems.append(f'{name}: points to {ref}, which does not exist in the semantic layer')
        else:
            resolved[name] = {'light': SEM[ref][0], 'dark': SEM[ref][1]}

    for role, ref in SHADOW.items():
        name = f'tooltip-{role}'
        alias[name] = ref
        try:
            v = resolve_foundation(ref)
            resolved[name] = {'light': v['light'], 'dark': v['dark']}
        except KeyError:
            problems.append(f'{name}: {ref} does not exist in the Foundation')

    for group in (GEOM, TYPE, MOTION):
        for role, ref in group.items():
            name = f'tooltip-{role}'
            alias[name] = ref
            try:
                resolved[name] = resolve_foundation(ref)
            except KeyError:
                problems.append(f'{name}: {ref} does not exist in the Foundation')

    # Named exceptions: a loose value is only accepted for these names.
    for role, px in WIDTH.items():
        alias[f'tooltip-{role}'] = f'{px}px'
        resolved[f'tooltip-{role}'] = px
    for role, ms in DELAY.items():
        alias[f'tooltip-{role}'] = f'{ms}ms'
        resolved[f'tooltip-{role}'] = ms

    if problems:
        print(f'{len(problems)} TOKEN(S) FAIL THE ALIAS GATE:')
        for p in problems:
            print('   ', p)
        return 1

    rows = contrast_rows()
    fails = [r for r in rows if not r['pass'] and not r['exception']]
    excs = [r for r in rows if not r['pass'] and r['exception']]

    print('=' * 74)
    print('TOOLTIP TOKEN LAYER')
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
    n_lit = len(WIDTH) + len(DELAY)
    print(f'{len(alias)} tokens: {len(alias) - n_lit} aliases of the Foundation, {n_lit} with a '
          f'declared value (maximum width and the two delays).')

    out = {
        'meta': {
            'component': 'Tooltip',
            'version': '0.1.0',
            'foundation': FOUND['meta']['version'],
            'figmaNode': '373:5340',
            'figmaCollection': '4. Components',
            'note': (
                'Inverted background (bg-inverse / text-inverse), icon 20 always present '
                'following the text, Body/sm, padding 8 x 12, gap 8, lg radius, Elevation/3, no '
                'border and no arrow, 4 from the trigger, maximum width 280. Opens on hover after '
                '500ms and on focus at once; 100ms of slack for the pointer to reach the tooltip. '
                'No contrast exception.'
            ),
        },
        'alias': alias,
        'resolved': resolved,
        'contrast': rows,
        'pending': PENDING,
    }
    json.dump(out, open(comp_out('tooltip', 'tokens.json'), 'w'), indent=2, ensure_ascii=False)
    print('\nbuild/components/tooltip/tokens.json written')
    write_css(alias)
    return 0


# ---------------------------------------------------------------- css
def write_css(alias):
    L = []
    w = L.append
    w('/* AL Design System - Tooltip tokens')
    w(' * GENERATED by src/components/tooltip/tokens.py. Do not edit by hand.')
    w(' */')
    w('')
    w(':root {')
    w('')
    w('  /* color - inverted background; the theme switches on :root */')
    for role, ref in COLOR.items():
        w(f'  --al-tooltip-{role}: {css_ref(ref)};')
    w('')
    w('  /* elevation - height, not state */')
    for role, ref in SHADOW.items():
        w(f'  --al-tooltip-{role}: {css_ref(ref)};')
    w('')
    w('  /* geometry */')
    for role, ref in GEOM.items():
        w(f'  --al-tooltip-{role}: {css_ref(ref)};')
    w('')
    w('  /* maximum width - declared value, no scale in the Foundation */')
    for role, px in WIDTH.items():
        w(f'  --al-tooltip-{role}: {px}px;')
    w('')
    w('  /* motion */')
    for role, ref in MOTION.items():
        w(f'  --al-tooltip-{role}: {css_ref(ref)};')
    w('')
    w('  /* delay - declared value, stays in the component. Read by tooltip.js */')
    for role, ms in DELAY.items():
        w(f'  --al-tooltip-{role}: {ms}ms;')
    w('')
    w('  /* typography - one style becomes four vars */')
    for role, ref in TYPE.items():
        style = resolve_foundation(ref)
        key = size_key(style[1])
        prefix = f'--al-tooltip-{role}'.replace('-font', '')
        w(f'  {prefix}-font-size: var(--al-font-size-{key});')
        w(f'  {prefix}-line-height: var(--al-line-height-{key});')
        w(f'  {prefix}-font-weight: {style[3]};')
        w(f'  {prefix}-tracking: {style[4]};')
    w('}')
    w('')
    text = '\n'.join(L)
    missing = [n for n in alias if n != 'tooltip-font' and f'--al-{n}:' not in text]
    if missing:
        raise AssertionError(f'tokens missing from the CSS: {missing}')
    save_css('tooltip', text)


if __name__ == '__main__':
    sys.exit(run())
