"""
Token layer for the Button.

The one rule of this layer: nothing here invents a value. Every Button token
points to a Foundation token by NAME. The gate at the end of the file rejects
anything that is a loose value - hex, px, number.

Naming:
  code  -> button-primary-bg-hover     (hyphen)
  Figma -> button/primary/bg-hover     (folder)
They are different layers. Never collapse one into the other.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'tools'))
from paths import FOUNDATION_SRC, TOKENS_JSON, comp_out  # noqa: E402
sys.path.insert(0, FOUNDATION_SRC)

from palette import SEM                     # noqa: E402
from tokenlib import resolve_foundation, css_ref, save_css  # noqa: E402

# Single source, at the root. The chdir that used to be here pointed to a copy
# in foundation/, and that copy - not the root - was what the gates read.
FOUND = json.load(open(TOKENS_JSON))   # noqa: E402

TRANSPARENT = 'transparent'   # absence of color, not a color choice

# ---------------------------------------------------------------- color
# Each variant repeats the same shape: background in 4 states, label in 2,
# border in 2, focus ring. Where the variant doesn't have that role, the value
# is transparent - the geometry doesn't change between states, only the color.
COLOR = {
  'primary': {
    'bg':               'bg-brand',
    'bg-hover':         'bg-brand-hover',
    'bg-active':        'bg-brand-active',
    'bg-disabled':      'bg-disabled',
    'label':            'text-on-brand',
    'label-disabled':   'text-disabled',
    'border':           TRANSPARENT,
    'border-disabled':  'border-subtle',
  },
  'secondary': {
    'bg':               TRANSPARENT,
    'bg-hover':         'bg-hover',
    'bg-active':        'bg-active',
    'bg-disabled':      TRANSPARENT,
    'label':            'text-primary',
    'label-disabled':   'text-disabled',
    'border':           'border-strong',
    'border-disabled':  'border-subtle',
  },
  'ghost': {
    'bg':               TRANSPARENT,
    'bg-hover':         'bg-hover',
    'bg-active':        'bg-active',
    'bg-disabled':      TRANSPARENT,
    'label':            'text-primary',
    'label-disabled':   'text-disabled',
    'border':           TRANSPARENT,
    'border-disabled':  TRANSPARENT,
  },
  'danger': {
    'bg':               'bg-danger',
    'bg-hover':         'bg-danger-hover',
    'bg-active':        'bg-danger-active',
    'bg-disabled':      'bg-disabled',
    'label':            'text-on-solid',
    'label-disabled':   'text-disabled',
    'border':           TRANSPARENT,
    'border-disabled':  'border-subtle',
  },
}

# Focus ring: points to the Foundation's composite shadow, not the raw color.
# Danger uses the error ring; the rest use the default.
RING = {
  'primary':   'focusRing.default',
  'secondary': 'focusRing.default',
  'ghost':     'focusRing.default',
  'danger':    'focusRing.error',
}

# ------------------------------------------------------------- geometry
# There is no height token. Height is a consequence: padding-y x2 plus the
# label's line height. sm = 8+20+8 = 36. md = 12+24+12 = 48. A height token
# would pin the same decision in two places.
#
# The icon also goes here, and not in SHARED, because it has no size of its
# own: it has the label's LINE HEIGHT. sm uses label-md, line height 20; md
# uses label-lg, line height 24. That is why turning the icon on doesn't change
# the button's height - it takes exactly the box the line of text already takes.
SIZE = {
  'sm': {'padding-x': 'space.12', 'padding-y': 'space.8',
         'gap': 'space.8', 'font': 'type.styles.label-md',
         'icon-size': 'iconSize.20'},
  'md': {'padding-x': 'space.16', 'padding-y': 'space.12',
         'gap': 'space.8', 'font': 'type.styles.label-lg',
         'icon-size': 'iconSize.24'},
}

SHARED = {
  'radius':       'radius.full',
  'border-width': 'border.width.1',
}

# Resolved on 2026-09-06: the icon scale was born in the Foundation together
# with the Icon component, and the Button's icon-size became a pure alias. The
# rendered value didn't change at that moment - it was 16px literal, it became
# 16px by token.
#
# Resolved on 2026-09-07, in the migration PR: the design moved the icon up to
# 20 in sm and 24 in md, matching the label's line height. With that the token
# stopped being a single one (button-icon-size) and became one per size - that
# is why it left SHARED and went into SIZE.
#
# Corrected on 2026-09-08: the previous note said the Icon Button would use 20
# in both sizes. That's not what happened - it closed at 20 in sm and 24 in md,
# the same steps as here. The reason isn't imitation: there the box is padding
# x2 plus the icon, and 36 and 48 only work out with 8+20+8 and 12+24+12,
# because 14 is not a spacing step. Each token's reason to exist is still
# different - here the icon follows the label's line height, there it is the
# whole content - but the value matches, and that is what keeps both aligned
# in a toolbar.
#
# The mechanism stays in place, empty. A pending item leaves the report when it
# is really gone, never by forgetting.
PENDING = {}


# ------------------------------------------------------------------ gate
def run():
    alias, resolved, problems = {}, {}, []

    for variant, roles in COLOR.items():
        for role, ref in roles.items():
            name = f'button-{variant}-{role}'
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
        name = f'button-{variant}-ring'
        alias[name] = ref
        try:
            v = resolve_foundation(ref)
            resolved[name] = {'light': v['light'], 'dark': v['dark']}
        except KeyError:
            problems.append(f'{name}: {ref} does not exist in the Foundation')

    for size, roles in SIZE.items():
        for role, ref in roles.items():
            name = f'button-{size}-{role}'
            alias[name] = ref
            try:
                resolved[name] = resolve_foundation(ref)
            except KeyError:
                problems.append(f'{name}: {ref} does not exist in the Foundation')

    for role, ref in SHARED.items():
        name = f'button-{role}'
        alias[name] = ref
        try:
            resolved[name] = resolve_foundation(ref)
        except KeyError:
            problems.append(f'{name}: {ref} does not exist in the Foundation')

    # derived height, only for checking - it doesn't become a token
    heights = {}
    for size in SIZE:
        py = resolve_foundation(SIZE[size]['padding-y'])
        style = resolve_foundation(SIZE[size]['font'])
        heights[size] = py * 2 + style[2]   # (name, size, leading, ...) -> leading

    print('=' * 70)
    print('BUTTON TOKEN LAYER')
    print('=' * 70)
    for name in sorted(alias):
        ref = alias[name]
        tag = 'transparent' if ref == TRANSPARENT else f'-> {ref}'
        print(f'  {name:<34} {tag}')
    print('-' * 70)
    print(f'derived height: sm {heights["sm"]}px   md {heights["md"]}px  (padding-y x2 + line height)')
    # a check, not a gate: the icon must match the label's line height - that
    # is what makes turning the icon on not change the button's height
    for size in SIZE:
        box = resolve_foundation(SIZE[size]['icon-size'])
        lead = resolve_foundation(SIZE[size]['font'])[2]
        sign = '=' if box == lead else 'DIFFERS FROM'
        print(f'icon {size}: {box}px {sign} line height {lead}px')
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
            'component': 'Button',
            # 0.2.0: the icon got one token per size (20 in sm, 24 in md). The
            # button-icon-size token stopped existing and the rendered value
            # changed - so MINOR, not PATCH.
            'version': '0.2.0',
            'foundation': FOUND['meta']['version'],
            'figmaNode': '23:123',
            'variants': list(COLOR),
            'sizes': list(SIZE),
            'states': ['default', 'hover', 'pressed', 'focus', 'disabled'],
            'note': 'button-*-ring points to the composite shadow, not the raw color.',
        },
        'alias': alias,
        'resolved': resolved,
        'derived': {'height': heights},
        'pending': PENDING,
    }
    json.dump(out, open(comp_out('button', 'tokens.json'), 'w'), indent=2, ensure_ascii=False)
    print(f'\nbuild/components/button/tokens.json written')
    write_css(alias, heights)
    return 0


# ------------------------------------------------------------------- css
def write_css(alias, heights):
    L = []
    w = L.append
    w('/* AL Design System - Button tokens')
    w(' * GENERATED by src/components/button/tokens.py. Do not edit by hand.')
    w(' *')
    w(' * There is no theme block here, and that is the point: each token points')
    w(' * to a semantic, and the theme switches on :root - the same element where')
    w(' * these aliases are declared. So :root re-substitutes all of them at once,')
    w(' * and the whole Button follows without one extra line.')
    w(' *')
    w(' * Careful: custom property substitution happens on the element where it is')
    w(' * DECLARED, not at the point of use. An alias declared here inherits already')
    w(' * resolved. That is why theming a loose container (not :root) requires')
    w(' * re-declaring this layer inside that container\'s block - see site/site.py.')
    w(' */')
    w('')
    w(':root {')

    for variant in COLOR:
        w('')
        w(f'  /* {variant} */')
        for role, ref in COLOR[variant].items():
            w(f'  --al-button-{variant}-{role}: {css_ref(ref)};')
        w(f'  --al-button-{variant}-ring: {css_ref(RING[variant])};')

    for size, roles in SIZE.items():
        w('')
        w(f'  /* size {size} - resulting height: {heights[size]}px */')
        for role, ref in roles.items():
            if role == 'font':
                style = resolve_foundation(ref)
                _, fsize, leading, weight, _, _ = style
                w(f'  --al-button-{size}-font-size: var(--al-font-size-{size_key(fsize)});')
                w(f'  --al-button-{size}-line-height: var(--al-line-height-{leading_key(leading)});')
                w(f'  --al-button-{size}-font-weight: var(--al-font-weight-{weight_key(weight)});')
            else:
                w(f'  --al-button-{size}-{role}: {css_ref(ref)};')

    w('')
    w('  /* shared */')
    for role, ref in SHARED.items():
        w(f'  --al-button-{role}: {css_ref(ref)};')
    w('}')
    w('')

    save_css('button', '\n'.join(L))


def size_key(v):
    return scale_key_in(FOUND['type']['size'], v, 'font-size')


def leading_key(v):
    return scale_key_in(FOUND['type']['leading'], v, 'line-height')


def weight_key(v):
    return scale_key_in(FOUND['type']['weight'], v, 'font-weight')


def scale_key_in(d, value, label):
    for k, x in d.items():
        if x == value:
            return k
    raise KeyError(f'{value} is not a {label} step')


if __name__ == '__main__':
    sys.exit(run())
