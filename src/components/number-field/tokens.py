"""
Token layer for the Number field.

The one rule of this layer: nothing here invents a value. Every token points
to a Foundation token by NAME. The gate at the end of the file rejects
anything that is a loose value - hex, px, number.

Naming:
  code  -> number-field-border-hover      (hyphen)
  Figma -> border/strong                  (folder)
Figma has no variable per component: the node binds the semantic or
Foundation variable the token points to.

THE INPUT'S SKIN, PLUS TWO STEPPERS

  The same seven states as the Input (Default, Hover, Error, focusError,
  Disabled, focusDefault, readOnly), the same colors and the same two contrast
  exceptions - see the header of components/input/tokens.py. On top of that,
  a - button on the left and a + button on the right, with the value centered.

  Out, decided in the audit (2026-10-21): extra sizes, unit/suffix, currency
  and percent formatting, stacked buttons. There is no placeholder: a number
  field always has a value (the minimum or the default), so there is no
  `text-placeholder`.

THE STEPPERS ARE NOT IN THE TAB ORDER

  The field is a single tab stop (Carbon precedent); the keyboard changes the
  value with the arrow keys or by typing. That is why the - and + have no ring
  and no hover of their own: the field's border and ring already say where the
  pointer and the focus are.

  At the minimum the - goes `stepper-icon-disabled`, at the maximum the +.
  That only exists in code - Figma has no variant for it.

  Read-only has no steppers at all: nothing can change, so they would only be
  noise next to the value.

  The clickable area of each stepper IS the icon-size: 24x24, the EXACT
  minimum of WCAG 2.5.8. No slack - if the icon shrinks, the target fails.

HEIGHT IS NOT A TOKEN

  48 = padding-y x2 + line height (12 + 24 + 12), with the 1px border
  overlapping the padding. The same as the Input.

WIDTH IS FIXED: 140

  The box (`__control`) is 140px wide, decided on 2026-10-21 - it replaced
  the 100% of the container chosen in the token stage. A quantity is a few
  digits; a field stretched across the form puts the - and the + far apart.
  Label and help text are NOT limited by it: they may be wider than the box.
  The Foundation has no container width scale, so it is a declared literal -
  the same exception as the Sidebar, the Tooltip and the Toast. In Figma it
  lives in the `4. Components` collection (number-field/width).
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

C = 'number-field'

# ----------------------------------------------------------------- color
COLOR = {
    'bg':                    'bg-surface-raised',
    'bg-disabled':           'bg-disabled',
    'bg-readonly':           'bg-subtle',

    'border':                'border-default',
    'border-hover':          'border-strong',
    'border-focus':          'border-brand',
    'border-error':          'border-danger',
    'border-disabled':       'border-default',
    'border-readonly':       'border-subtle',

    'text-value':            'text-primary',
    'text-disabled':         'text-disabled',

    'stepper-icon':          'text-primary',   # vector glyph - 3:1 floor
    'stepper-icon-disabled': 'text-disabled',  # at the limit, and in disabled

    'label':                 'text-primary',
    'label-error':           'text-danger',
    'label-disabled':        'text-disabled',

    'optional':              'text-secondary',

    'help':                  'text-secondary',
    'help-error':            'text-danger',
}

# The token points to the COMPOSITE SHADOW, not the raw color - same rule as
# `input-ring`. The color is only extracted for measuring, in RING_INK below.
RING = {
    'ring':       'focusRing.default',
    'ring-error': 'focusRing.error',
}

RING_INK = {
    'ring':       'shadow-focus-default',
    'ring-error': 'shadow-focus-error',
}

# ------------------------------------------------------------- geometry
GEOM = {
    'padding-x':    'space.12',
    'padding-y':    'space.12',
    'gap':          'space.8',       # stack, label -> optional
    'stepper-gap':  'space.24',      # minimum between a stepper and the value
    'radius':       'radius.lg',
    'border-width': 'border.width.1',
    'icon-size':    'iconSize.24',   # also each stepper's clickable area
}

# Exception (2026-10-21): the Foundation has no container width scale.
WIDTH = {
    'width': 140,
}

TYPE = {
    'font':          'type.styles.body-md',
    'label-font':    'type.styles.body-md',
    'optional-font': 'type.styles.body-sm',
    'help-font':     'type.styles.caption',
}

PENDING = {
    'border-below-3-1': (
        'The border at rest uses `border-default` and the read-only one uses '
        '`border-subtle`, below the 3:1 of WCAG 1.4.11. The same conscious decision as the '
        'Input and the Select: the field has a visible label above and a value inside, so '
        'the border is not the only way to perceive it. DO NOT "fix" it without revisiting '
        'that decision.'
    ),
    'disabled-below-aa': (
        'Label, text, border and steppers in disabled - and the stepper at the limit - fall '
        'below the minimum. WCAG 1.4.3 and 1.4.11 exempt inactive components - the same '
        'permanent exception as the Button and the Input.'
    ),
}

CANVAS = 'bg-canvas'   # not a Number field token: it is the canvas it is placed on

# (role, token, background(s), floor, exception key in PENDING)
# There is no stepper x bg-readonly combination: read-only has no steppers.
COMBOS = [
    ('label',                 'label',                 'canvas',                  4.5, None),
    ('label-error',           'label-error',           'canvas',                  4.5, None),
    ('label-disabled',        'label-disabled',        'canvas',                  4.5, 'disabled-below-aa'),
    ('optional',              'optional',              'canvas',                  4.5, None),
    ('help',                  'help',                  'canvas',                  4.5, None),
    ('help-error',            'help-error',            'canvas',                  4.5, None),
    ('value',                 'text-value',            'bg',                      4.5, None),
    ('value-readonly',        'text-value',            'bg-readonly',             4.5, None),
    ('text-disabled',         'text-disabled',         'bg-disabled',             4.5, 'disabled-below-aa'),
    ('stepper',               'stepper-icon',          'bg',                      3.0, None),
    ('stepper-at-limit',      'stepper-icon-disabled', 'bg',                      3.0, 'disabled-below-aa'),
    ('stepper-disabled',      'stepper-icon-disabled', 'bg-disabled',             3.0, 'disabled-below-aa'),
    ('border-rest',           'border',                ('canvas', 'bg'),          3.0, 'border-below-3-1'),
    ('border-hover',          'border-hover',          ('canvas', 'bg'),          3.0, None),
    ('border-focus',          'border-focus',          ('canvas', 'bg'),          3.0, None),
    ('border-error',          'border-error',          ('canvas', 'bg'),          3.0, None),
    ('border-disabled',       'border-disabled',       ('canvas', 'bg-disabled'), 3.0, 'disabled-below-aa'),
    ('border-readonly',       'border-readonly',       ('canvas', 'bg-readonly'), 3.0, 'border-below-3-1'),
    ('focus-ring',            'ring',                  'canvas',                  3.0, None),
    ('focus-ring-error',      'ring-error',            'canvas',                  3.0, None),
]


# ------------------------------------------------------------------ gate
def ink(role):
    """The color semantic behind a role - following the ring down to the color."""
    if role == 'canvas':
        return CANVAS
    if role in RING_INK:
        return RING_INK[role]
    return COLOR[role]


def contrast_rows():
    """Measures each rendered combination in both themes, each against its own
    floor: text 4.5:1 from 1.4.3, border, icon and ring 3:1 from 1.4.11."""
    rows = []
    for what, fg_role, bg_spec, min_ratio, exc in COMBOS:
        fg_ref = ink(fg_role)
        bg_roles = bg_spec if isinstance(bg_spec, tuple) else (bg_spec,)
        for theme, i in (('light', 0), ('dark', 1)):
            measures = [(round(cr(SEM[fg_ref][i], SEM[ink(b)][i]), 2), ink(b))
                        for b in bg_roles]
            ratio, bg_ref = min(measures)
            rows.append({
                'theme': theme, 'what': what,
                'fg': fg_ref, 'bg': bg_ref,
                'ratio': ratio, 'min': min_ratio,
                'pass': ratio >= min_ratio,
                'exception': exc,
            })
    return rows


def run():
    alias, resolved, problems = {}, {}, []

    for role, ref in COLOR.items():
        name = f'{C}-{role}'
        alias[name] = ref
        if ref.startswith('#'):
            problems.append(f'{name}: loose hex ({ref}) - every color value is born as an alias of a semantic')
            continue
        if ref not in SEM:
            problems.append(f'{name}: points to {ref}, which does not exist in the semantic layer')
            continue
        light, dark = SEM[ref]
        resolved[name] = {'light': light, 'dark': dark}

    for role, ref in RING.items():
        name = f'{C}-{role}'
        alias[name] = ref
        try:
            v = resolve_foundation(ref)
            resolved[name] = {'light': v['light'], 'dark': v['dark']}
        except KeyError:
            problems.append(f'{name}: {ref} does not exist in the Foundation')

    for group in (GEOM, TYPE):
        for role, ref in group.items():
            name = f'{C}-{role}'
            alias[name] = ref
            try:
                resolved[name] = resolve_foundation(ref)
            except KeyError:
                problems.append(f'{name}: {ref} does not exist in the Foundation')

    for role, px in WIDTH.items():
        alias[f'{C}-{role}'] = f'{px}px'
        resolved[f'{C}-{role}'] = px

    # derived - a check, not a token. See the note in the header.
    pad_y = resolve_foundation(GEOM['padding-y'])
    gap = resolve_foundation(GEOM['gap'])
    icon = resolve_foundation(GEOM['icon-size'])
    field_line = resolve_foundation(TYPE['font'])[2]
    label_line = resolve_foundation(TYPE['label-font'])[2]
    help_line = resolve_foundation(TYPE['help-font'])[2]
    field_h = pad_y * 2 + field_line
    derived = {
        'field-height': field_h,
        'stepper-target': icon,
        'total-height': label_line + gap + field_h,
        'total-height-with-help': label_line + gap + field_h + gap + help_line,
    }
    if icon > field_line:
        problems.append(f'icon-size {icon} > line height {field_line} - the steppers change the field height')
    if icon < 24:
        problems.append(f'stepper target {icon}px < the 24px of WCAG 2.5.8')

    rows = contrast_rows()
    fails = [r for r in rows if not r['pass'] and not r['exception']]
    excs = [r for r in rows if not r['pass'] and r['exception']]

    print('=' * 74)
    print('NUMBER FIELD TOKEN LAYER')
    print('=' * 74)
    for name in sorted(alias):
        print(f'  {name:<34} -> {alias[name]}')
    print('-' * 74)
    print(f'derived field height: {derived["field-height"]}px  '
          f'(padding-y x2 + line height; border overlapping the padding)')
    print(f'stepper target: {icon}x{icon}px (WCAG 2.5.8 minimum: 24)')
    print(f'total height: {derived["total-height"]}px  '
          f'| with help text: {derived["total-height-with-help"]}px')
    print('-' * 74)
    print(f'contrast: {len(rows)} measurements  |  pass: {len(rows) - len(fails) - len(excs)}  |  '
          f'declared exceptions: {len(excs)}  |  fail: {len(fails)}')
    clean = [r for r in rows if r['pass']]
    worst = min(clean, key=lambda r: r['ratio'] / r['min'])
    print(f'worst margin among those that pass: {worst["what"]} ({worst["theme"]}) = '
          f'{worst["ratio"]}:1 against floor {worst["min"]}')
    for key in PENDING:
        n = sum(1 for r in excs if r['exception'] == key)
        print(f'  exception "{key}": {n} measurements')
    print('-' * 74)

    if problems:
        print(f'{len(problems)} TOKEN(S) FAIL THE ALIAS GATE:')
        for p in problems:
            print('   ', p)
        return 1
    if fails:
        print(f'{len(fails)} COMBINATION(S) FAIL THE CONTRAST GATE:')
        for f in fails:
            print(f'    {f["what"]} ({f["theme"]}): {f["ratio"]}:1 < {f["min"]}')
        return 1

    print(f'{len(alias)} tokens, all aliases of the Foundation. 0 loose values.')

    out = {
        'meta': {
            'component': 'Number field',
            'version': '0.1.0',
            'foundation': FOUND['meta']['version'],
            'figmaNode': '480:692',
            'variants': [],
            'sizes': ['md'],
            'states': ['default', 'hover', 'error', 'focus-error',
                       'disabled', 'focus', 'readonly'],
            'note': (
                'The Input\'s skin with a - and a + stepper and the value centered. One size '
                '(48px), the box fixed at 140px (label and help may be wider). The steppers are out of the Tab order '
                '(Carbon): one tab stop, arrow keys or typing. No hover or ring on the '
                'steppers; the one at the limit goes disabled, in code only. Read-only has '
                'no steppers. No placeholder. Two contrast exceptions declared in pending.'
            ),
        },
        'alias': alias,
        'resolved': resolved,
        'derived': derived,
        'contrast': rows,
        'pending': PENDING,
    }
    json.dump(out, open(comp_out(C, 'tokens.json'), 'w'), indent=2, ensure_ascii=False)
    print(f'\nbuild/components/{C}/tokens.json written')
    write_css(derived)
    return 0


# ------------------------------------------------------------------- css
def write_css(derived):
    L = []
    w = L.append
    w('/* AL Design System - Number field tokens')
    w(' * GENERATED by src/components/number-field/tokens.py. Do not edit by hand.')
    w(' *')
    w(' * There is no theme block here: each token points to a semantic, and the')
    w(' * theme switches on :root - the same element where these aliases are declared.')
    w(' *')
    w(f' * Field height: {derived["field-height"]}px, derived, no token.')
    w(f' * Stepper target: {derived["stepper-target"]}px = icon-size, no token of its own.')
    w(' */')
    w('')
    w(':root {')

    w('')
    w('  /* background - only disabled and readonly change it */')
    for role in ('bg', 'bg-disabled', 'bg-readonly'):
        w(f'  --al-{C}-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* border - the axis that carries the state */')
    for role in ('border', 'border-hover', 'border-focus', 'border-error',
                 'border-disabled', 'border-readonly'):
        w(f'  --al-{C}-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* value - no placeholder, the field always has a value */')
    for role in ('text-value', 'text-disabled'):
        w(f'  --al-{C}-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* steppers - out of the Tab order, no hover or ring of their own */')
    for role in ('stepper-icon', 'stepper-icon-disabled'):
        w(f'  --al-{C}-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* label, mark and help - they live outside the field, on the canvas */')
    for role in ('label', 'label-error', 'label-disabled', 'optional',
                 'help', 'help-error'):
        w(f'  --al-{C}-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* focus ring - points to the composite shadow, not the raw color */')
    for role, ref in RING.items():
        w(f'  --al-{C}-{role}: {css_ref(ref)};')

    w('')
    w('  /* geometry */')
    for role, ref in GEOM.items():
        w(f'  --al-{C}-{role}: {css_ref(ref)};')

    w('')
    w('  /* width of the box - declared literal, the Foundation has no width scale */')
    for role, px in WIDTH.items():
        w(f'  --al-{C}-{role}: {px}px;')

    w('')
    w('  /* typography - one style becomes four vars */')
    for role, ref in TYPE.items():
        style = resolve_foundation(ref)
        key = size_key(style[1])
        prefix = f'--al-{C}-{role}'.replace('-font', '')
        if role == 'font':
            prefix = f'--al-{C}'
        w(f'  {prefix}-font-size: var(--al-font-size-{key});')
        w(f'  {prefix}-line-height: var(--al-line-height-{key});')
        w(f'  {prefix}-font-weight: {style[3]};')
        w(f'  {prefix}-tracking: {style[4]};')

    w('}')
    w('')

    # Lock inherited from the Select: a forgotten group list breaks the build
    # instead of leaving a variable silently missing.
    text = '\n'.join(L)
    missing = [r for r in COLOR if f'--al-{C}-{r}:' not in text]
    if missing:
        raise AssertionError(
            'color roles missing from the CSS (some group list in write_css was not '
            f'updated): {missing}')

    save_css(C, text)


if __name__ == '__main__':
    sys.exit(run())
