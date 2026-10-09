"""
Token layer for the Icon Button.

The one rule of this layer: nothing here invents a value. Every token points
to a Foundation token by NAME. The gate at the end of the file rejects
anything that is a loose value - hex, px, number.

Naming:
  code  -> icon-button-primary-bg-hover     (hyphen)
  Figma -> icon-button/primary/bg-hover     (folder)
They are different layers. Never collapse one into the other.

WHAT SETS THIS COMPONENT APART FROM THE BUTTON

  The Button carries the meaning in a TEXT label: criterion 1.4.3, floor
  4.5:1. That is why white on bg-brand (3.34:1) is a brand exception named in
  there.

  Here there is no label. An ICON carries the meaning, and it is non-text
  content: criterion 1.4.11, floor 3:1. The same pair stops being an exception
  and becomes a pass. This component has no brand exception at all.

  The consequence of that belongs to a11y.py, not to this file - but the
  decision is born here, and that is why it is written here.

THE ROLE IS CALLED `ink`, NOT `label`

  `label` in the Button is text. Here it is icon ink, and `ink` is already the
  system's vocabulary - the Icon component uses icon-ink-default. Same concept,
  same name.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'tools'))
from paths import FOUNDATION_SRC, TOKENS_JSON, comp_out  # noqa: E402
sys.path.insert(0, FOUNDATION_SRC)

from palette import SEM                     # noqa: E402
from tokenlib import resolve_foundation, css_ref, save_css  # noqa: E402

# Single source, at the root - the same one every other gate reads.
FOUND = json.load(open(TOKENS_JSON))   # noqa: E402

TRANSPARENT = 'transparent'   # absence of color, not a color choice

# ---------------------------------------------------------------- color
# Same shape as the Button - background in 4 states, ink in 2, border in 2,
# focus ring - with `ink` instead of `label`. The values match the Button's
# because the SOURCE is the same, not because one inherits from the other:
# each token here points straight to the semantic. The alias gate below
# requires that; a component token never references another component.
COLOR = {
  'primary': {
    'bg':               'bg-brand',
    'bg-hover':         'bg-brand-hover',
    'bg-active':        'bg-brand-active',
    'bg-disabled':      'bg-disabled',
    'ink':              'text-on-brand',
    'ink-disabled':     'text-disabled',
    'border':           TRANSPARENT,
    'border-disabled':  'border-subtle',
  },
  'secondary': {
    'bg':               TRANSPARENT,
    'bg-hover':         'bg-hover',
    'bg-active':        'bg-active',
    'bg-disabled':      TRANSPARENT,
    'ink':              'text-primary',
    'ink-disabled':     'text-disabled',
    'border':           'border-strong',
    'border-disabled':  'border-subtle',
  },
  'ghost': {
    'bg':               TRANSPARENT,
    'bg-hover':         'bg-hover',
    'bg-active':        'bg-active',
    'bg-disabled':      TRANSPARENT,
    'ink':              'text-primary',
    'ink-disabled':     'text-disabled',
    'border':           TRANSPARENT,
    'border-disabled':  TRANSPARENT,
  },
  'danger': {
    'bg':               'bg-danger',
    'bg-hover':         'bg-danger-hover',
    'bg-active':        'bg-danger-active',
    'bg-disabled':      'bg-disabled',
    'ink':              'text-on-solid',
    'ink-disabled':     'text-disabled',
    'border':           TRANSPARENT,
    'border-disabled':  'border-subtle',
  },
}

# Focus ring: points to the Foundation's composite shadow, not the raw color.
# That is what keeps the state color inside the contrast gate, instead of
# escaping along with elevation. Danger uses the error ring; the rest use the
# default.
RING = {
  'primary':   'focusRing.default',
  'secondary': 'focusRing.default',
  'ghost':     'focusRing.default',
  'danger':    'focusRing.error',
}

# ------------------------------------------------------------- geometry
# ONE padding token per size, not two. The Button splits padding-x from
# padding-y because it is rectangular; here the button is square and the value
# is the same on all four sides. Two tokens would pin the same decision in two
# places.
#
# There is no box size token. It is a consequence: padding x2 plus the icon.
# sm = 8+20+8 = 36. md = 12+24+12 = 48 - exactly the Button's heights, which is
# what lets the two live together in a toolbar without misaligning.
#
# There is no `gap` (there is a single child) and no `font` (there is no text).
SIZE = {
  'sm': {'padding': 'space.8',  'icon-size': 'iconSize.20'},
  'md': {'padding': 'space.12', 'icon-size': 'iconSize.24'},
}

SHARED = {
  'radius':       'radius.full',
  'border-width': 'border.width.1',
}

# The loading state does NOT create a token: the spinner reuses
# border.width.2, radius.full and currentColor - which here resolves to
# icon-button-<variant>-ink. Its duration and curve come from the Foundation's
# motion tokens.
#
# The mechanism stays in place, empty. A pending item leaves the report when it
# is really gone, never by forgetting.
PENDING = {}


# ------------------------------------------------------------------ gate
def button_heights():
    """The Button's heights, only for the parity check. It is not a gate: if
    the Button hasn't been generated yet, the check is skipped, not broken."""
    path = comp_out('button', 'tokens.json')
    if not os.path.exists(path):
        return None
    return json.load(open(path)).get('derived', {}).get('height')


def run():
    alias, resolved, problems = {}, {}, []

    for variant, roles in COLOR.items():
        for role, ref in roles.items():
            name = f'icon-button-{variant}-{role}'
            alias[name] = ref
            if ref == TRANSPARENT:
                resolved[name] = {'light': TRANSPARENT, 'dark': TRANSPARENT}
                continue
            if ref.startswith('#'):
                problems.append(f'{name}: loose hex ({ref}) - every color value is born as an alias of a semantic')
                continue
            if ref not in SEM:
                problems.append(f'{name}: points to {ref}, which does not exist in the semantic layer')
                continue
            light, dark = SEM[ref]
            resolved[name] = {'light': light, 'dark': dark}

    for variant, ref in RING.items():
        name = f'icon-button-{variant}-ring'
        alias[name] = ref
        try:
            v = resolve_foundation(ref)
            resolved[name] = {'light': v['light'], 'dark': v['dark']}
        except KeyError:
            problems.append(f'{name}: {ref} does not exist in the Foundation')

    for size, roles in SIZE.items():
        for role, ref in roles.items():
            name = f'icon-button-{size}-{role}'
            alias[name] = ref
            try:
                resolved[name] = resolve_foundation(ref)
            except KeyError:
                problems.append(f'{name}: {ref} does not exist in the Foundation')

    for role, ref in SHARED.items():
        name = f'icon-button-{role}'
        alias[name] = ref
        try:
            resolved[name] = resolve_foundation(ref)
        except KeyError:
            problems.append(f'{name}: {ref} does not exist in the Foundation')

    # derived box, only for checking - it doesn't become a token. Square: the
    # same number is width and height.
    boxes = {}
    for size in SIZE:
        pad = resolve_foundation(SIZE[size]['padding'])
        icon = resolve_foundation(SIZE[size]['icon-size'])
        boxes[size] = pad * 2 + icon

    print('=' * 70)
    print('ICON BUTTON TOKEN LAYER')
    print('=' * 70)
    for name in sorted(alias):
        ref = alias[name]
        tag = 'transparent' if ref == TRANSPARENT else f'-> {ref}'
        print(f'  {name:<39} {tag}')
    print('-' * 70)
    for size in SIZE:
        print(f'derived box {size}: {boxes[size]}x{boxes[size]}px  (padding x2 + icon)')

    # a parity check, not a gate: the Icon Button only works next to the Button
    # if both boxes close at the same number.
    bh = button_heights()
    if bh is None:
        print('parity with the Button: not checked (button/tokens.json missing)')
    else:
        for size in SIZE:
            target = bh.get(size)
            sign = '=' if target == boxes[size] else 'DIFFERS FROM'
            print(f'parity {size}: box {boxes[size]}px {sign} Button height {target}px')

    if PENDING:
        for k, v in PENDING.items():
            print(f'pending: {k} - {v}')
    else:
        print('pending: none')
    print('-' * 70)

    if problems:
        print(f'{len(problems)} TOKEN(S) FAIL THE ALIAS GATE:')
        for p in problems:
            print('   ', p)
        return 1

    n_alias = sum(1 for r in alias.values() if r != TRANSPARENT)
    n_tr = len(alias) - n_alias
    print(f'{len(alias)} tokens: {n_alias} aliases of the Foundation, {n_tr} transparent.')
    print('0 loose values.')

    out = {
        'meta': {
            'component': 'Icon Button',
            'version': '0.1.0',
            'foundation': FOUND['meta']['version'],
            'figmaNode': '35:460',
            'variants': list(COLOR),
            'sizes': list(SIZE),
            'states': ['default', 'hover', 'pressed', 'focus', 'disabled', 'loading'],
            'note': (
                'The contrast floor here is 3:1 (WCAG 1.4.11, non-text): what carries '
                'the meaning is an icon, not a label. That is why this component has no '
                'brand exception, unlike the Button. The loading state creates no token '
                '- the spinner uses currentColor, border.width.2 and radius.full.'
            ),
        },
        'alias': alias,
        'resolved': resolved,
        'derived': {'box': boxes},
        'pending': PENDING,
    }
    json.dump(out, open(comp_out('icon-button', 'tokens.json'), 'w'), indent=2, ensure_ascii=False)
    print('\nbuild/components/icon-button/tokens.json written')
    write_css(alias, boxes)
    return 0


# ------------------------------------------------------------------- css
def write_css(alias, boxes):
    L = []
    w = L.append
    w('/* AL Design System - Icon Button tokens')
    w(' * GENERATED by src/components/icon-button/tokens.py. Do not edit by hand.')
    w(' *')
    w(' * There is no theme block here, and that is the point: each token points')
    w(' * to a semantic, and the theme switches on :root - the same element where')
    w(' * these aliases are declared. So :root re-substitutes all of them at once.')
    w(' *')
    w(' * Careful: custom property substitution happens on the element where it is')
    w(' * DECLARED, not at the point of use. Theming a loose container requires')
    w(' * re-declaring this layer inside it - see site/site.py.')
    w(' */')
    w('')
    w(':root {')

    for variant in COLOR:
        w('')
        w(f'  /* {variant} */')
        for role, ref in COLOR[variant].items():
            w(f'  --al-icon-button-{variant}-{role}: {css_ref(ref)};')
        w(f'  --al-icon-button-{variant}-ring: {css_ref(RING[variant])};')

    for size, roles in SIZE.items():
        w('')
        w(f'  /* size {size} - resulting box: {boxes[size]}x{boxes[size]}px */')
        for role, ref in roles.items():
            w(f'  --al-icon-button-{size}-{role}: {css_ref(ref)};')

    w('')
    w('  /* shared */')
    for role, ref in SHARED.items():
        w(f'  --al-icon-button-{role}: {css_ref(ref)};')
    w('}')
    w('')

    save_css('icon-button', '\n'.join(L))


if __name__ == '__main__':
    sys.exit(run())
