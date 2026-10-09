"""
Token layer for the Password.

The one rule of this layer: nothing here invents a value. Every token points
to a Foundation token by NAME. The gate at the end of the file rejects
anything that is a loose value - hex, px, number.

Naming:
  code  -> password-toggle-ring       (hyphen)
  Figma -> password/toggle/ring       (folder)
They are different layers. Never collapse one into the other.

PASSWORD FIELD, IN PLACE OF THE DATE PICKER

  It is the Input without what the Password Figma doesn't draw, plus the eye
  button. Six states (Default, Hover, Error, focusError, Disabled,
  focusDefault), the same colors, the same two contrast exceptions. No Active
  and no Typed for the same reason as the Input - see the header of
  components/input/tokens.py.

  Out, decided in the audit (2026-10-06): read-only (a "read only" password
  exposes the data), counter, prefix and suffix, the "(Optional)" mark and
  help text outside the error. That is why there are no `bg-readonly`,
  `border-readonly`, `optional`, `counter*`, `affix` or `help` - only
  `help-error`.

  Figma's `Type` axis (No / Visible / Hidden) does NOT become a token: it is
  the <input>'s `type` attribute (password x text) and the icon the button
  shows. The value color is the same in all three, including in error
  (`text-primary`, never red).

THE EYE BUTTON

  It is a real <button>, focusable, after the field in the Tab order. The icon
  shows the ACTION (eye = show, eye-off = hide), like Material and Carbon.

  - A ring only around the eye (Carbon precedent), never on the whole field.
    Always the DEFAULT ring, even with the field in error: the ring says where
    focus is, and the error belongs to the field, not the button. The same
    solution as the Tag's X (`tag-dismiss-ring`).
  - The ring's shape: `radius.full`, a circle, like the Tag's X.
  - No hover: Figma doesn't draw one, only the cursor changes.
  - The clickable area IS the icon-size: 24x24, the EXACT minimum of WCAG
    2.5.8. No slack - if the icon shrinks, the target fails.
  - The ring's 2px gap is `bg-canvas`, not the field background. In dark that
    draws a thin #181818 outline inside the #3E3E3E field. Accepted with the
    tokens: the ring still passes against the field background and a new ring
    in the Foundation isn't worth it just for this.

HEIGHT IS NOT A TOKEN

  48 = padding-y x2 + line height (12 + 24 + 12), with the 1px border
  overlapping the padding. The same as the Input.

THE GAP IS ONE IN TWO PLACES

  `password-gap` applies to the vertical stack (label -> field -> error) and
  to the space between the text and the eye. Both are 8.

WIDTH IS NOT A TOKEN

  The field takes 100% of its container. The form decides width; the
  component doesn't.
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

# ----------------------------------------------------------------- color
COLOR = {
    'bg':               'bg-surface-raised',
    'bg-disabled':      'bg-disabled',

    'border':           'border-default',
    'border-hover':     'border-strong',
    'border-focus':     'border-brand',
    'border-error':     'border-danger',
    'border-disabled':  'border-default',

    'text-placeholder': 'text-placeholder',
    'text-value':       'text-primary',     # dots or text, including in error
    'text-disabled':    'text-disabled',

    'label':            'text-primary',
    'label-error':      'text-danger',
    'label-disabled':   'text-disabled',

    'help-error':       'text-danger',

    'toggle-icon':          'text-primary',   # vector glyph - 3:1 floor
    'toggle-icon-disabled': 'text-disabled',
}

# The token points to the COMPOSITE SHADOW, not the raw color - same rule as
# `button-*-ring`. The color is only extracted for measuring, in RING_INK below.
RING = {
    'ring':        'focusRing.default',
    'ring-error':  'focusRing.error',
    'toggle-ring': 'focusRing.default',   # always the default, see the header
}

RING_INK = {
    'ring':        'shadow-focus-default',
    'ring-error':  'shadow-focus-error',
    'toggle-ring': 'shadow-focus-default',
}

# ------------------------------------------------------------- geometry
GEOM = {
    'padding-x':     'space.12',
    'padding-y':     'space.12',
    'gap':           'space.8',       # stack, text -> eye
    'radius':        'radius.lg',
    'border-width':  'border.width.1',
    'icon-size':     'iconSize.24',   # also the eye's clickable area
    'toggle-radius': 'radius.full',   # the shape of the eye's ring
}

TYPE = {
    'font':       'type.styles.body-md',
    'label-font': 'type.styles.body-md',
    'help-font':  'type.styles.caption',
}

PENDING = {
    'border-below-3-1': (
        'The border at rest uses `border-default` (1.57:1 in light, 1.46:1 in dark '
        'against the field background). Below the 3:1 of WCAG 1.4.11. The same conscious '
        'decision as the Select, the Input and the Textarea. The criterion does not fail '
        'when the border is not the only way to perceive the component, and here it is '
        'not: the field has a visible label above and the eye inside. DO NOT "fix" it '
        'without revisiting that decision.'
    ),
    'disabled-below-aa': (
        'Label, text, border and eye in disabled fall below the minimum. WCAG 1.4.3 '
        'exempts inactive components - the same permanent exception as the Button, the '
        'Tag, the Select and the Input. Raising that contrast makes disabled look '
        'editable.'
    ),
}

CANVAS = 'bg-canvas'   # not a Password token: it is the canvas the Password is placed on

# (role, password token, background(s), floor, exception key in PENDING)
# Label, error and the field ring live OUTSIDE the field and measure against
# the canvas; what is inside (value, eye, eye ring) measures against that
# state's field background. The border measures against BOTH neighboring
# surfaces and keeps the worse.
#
# There is no eye ring in disabled: a disabled button doesn't get focus.
COMBOS = [
    ('label',             'label',                'canvas',                   4.5, None),
    ('label-error',       'label-error',          'canvas',                   4.5, None),
    ('label-disabled',    'label-disabled',       'canvas',                   4.5, 'disabled-below-aa'),
    ('help-error',        'help-error',           'canvas',                   4.5, None),
    ('placeholder',       'text-placeholder',     'bg',                       4.5, None),
    ('value',             'text-value',           'bg',                       4.5, None),
    ('text-disabled',     'text-disabled',        'bg-disabled',              4.5, 'disabled-below-aa'),
    ('eye',               'toggle-icon',          'bg',                       3.0, None),
    ('eye-disabled',      'toggle-icon-disabled', 'bg-disabled',              3.0, 'disabled-below-aa'),
    ('border-rest',       'border',               ('canvas', 'bg'),           3.0, 'border-below-3-1'),
    ('border-hover',      'border-hover',         ('canvas', 'bg'),           3.0, None),
    ('border-focus',      'border-focus',         ('canvas', 'bg'),           3.0, None),
    ('border-error',      'border-error',         ('canvas', 'bg'),           3.0, None),
    ('border-disabled',   'border-disabled',      ('canvas', 'bg-disabled'),  3.0, 'disabled-below-aa'),
    ('focus-ring',        'ring',                 'canvas',                   3.0, None),
    ('focus-ring-error',  'ring-error',           'canvas',                   3.0, None),
    ('eye-ring',          'toggle-ring',          'bg',                       3.0, None),
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
        name = f'password-{role}'
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
        name = f'password-{role}'
        alias[name] = ref
        try:
            v = resolve_foundation(ref)
            resolved[name] = {'light': v['light'], 'dark': v['dark']}
        except KeyError:
            problems.append(f'{name}: {ref} does not exist in the Foundation')

    for group in (GEOM, TYPE):
        for role, ref in group.items():
            name = f'password-{role}'
            alias[name] = ref
            try:
                resolved[name] = resolve_foundation(ref)
            except KeyError:
                problems.append(f'{name}: {ref} does not exist in the Foundation')

    # derived - a check, not a token. See the note in the header.
    pad_y = resolve_foundation(GEOM['padding-y'])
    gap = resolve_foundation(GEOM['gap'])
    field_line = resolve_foundation(TYPE['font'])[2]
    label_line = resolve_foundation(TYPE['label-font'])[2]
    help_line = resolve_foundation(TYPE['help-font'])[2]
    icon = resolve_foundation(GEOM['icon-size'])
    field_h = pad_y * 2 + field_line
    derived = {
        'field-height': field_h,
        'toggle-target': icon,
        'total-height': label_line + gap + field_h,
        'total-height-with-error': label_line + gap + field_h + gap + help_line,
    }
    if icon > field_line:
        problems.append(f'icon-size {icon} > line height {field_line} - the eye changes the field height')
    if icon < 24:
        problems.append(f'eye target {icon}px < the 24px of WCAG 2.5.8')

    rows = contrast_rows()
    fails = [r for r in rows if not r['pass'] and not r['exception']]
    excs = [r for r in rows if not r['pass'] and r['exception']]

    print('=' * 74)
    print('PASSWORD TOKEN LAYER')
    print('=' * 74)
    for name in sorted(alias):
        print(f'  {name:<28} -> {alias[name]}')
    print('-' * 74)
    print(f'derived field height: {derived["field-height"]}px  '
          f'(padding-y x2 + line height; border overlapping the padding)')
    print(f'total height: {derived["total-height"]}px  '
          f'| with error message: {derived["total-height-with-error"]}px')
    print(f'eye target: {icon}x{icon}px (WCAG 2.5.8 minimum: 24)')
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
            'component': 'Password',
            'version': '0.1.0',
            'foundation': FOUND['meta']['version'],
            'figmaNode': '299:536',
            'variants': [],
            'sizes': ['md'],
            'states': ['default', 'hover', 'error', 'focus-error',
                       'disabled', 'focus'],
            'note': (
                'A password field with a show/hide button. It is the Input without '
                'read-only, counter, affixes, optional mark and help outside the error, '
                'plus the eye. Figma\'s Type axis (No/Visible/Hidden) is the input\'s type '
                'attribute, not a token. The eye is a focusable button with its own ring, '
                'circular and always the default; a 24px target. Two contrast exceptions '
                'declared in pending.'
            ),
        },
        'alias': alias,
        'resolved': resolved,
        'derived': derived,
        'contrast': rows,
        'pending': PENDING,
    }
    json.dump(out, open(comp_out('password', 'tokens.json'), 'w'), indent=2, ensure_ascii=False)
    print('\nbuild/components/password/tokens.json written')
    write_css(alias, derived)
    return 0


# ------------------------------------------------------------------- css
def write_css(alias, derived):
    L = []
    w = L.append
    w('/* AL Design System - Password tokens')
    w(' * GENERATED by src/components/password/tokens.py. Do not edit by hand.')
    w(' *')
    w(' * There is no theme block here: each token points to a semantic, and the')
    w(' * theme switches on :root - the same element where these aliases are declared.')
    w(' *')
    w(f' * Field height: {derived["field-height"]}px, derived, no token.')
    w(f' * Eye target: {derived["toggle-target"]}px = icon-size, no token of its own.')
    w(' */')
    w('')
    w(':root {')

    w('')
    w('  /* background - only disabled changes it */')
    for role in ('bg', 'bg-disabled'):
        w(f'  --al-password-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* border - the axis that carries the state */')
    for role in ('border', 'border-hover', 'border-focus', 'border-error',
                 'border-disabled'):
        w(f'  --al-password-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* text inside the field - dots and plain text use the same color */')
    for role in ('text-placeholder', 'text-value', 'text-disabled'):
        w(f'  --al-password-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* label and error - they live outside the field, on the canvas */')
    for role in ('label', 'label-error', 'label-disabled', 'help-error'):
        w(f'  --al-password-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* eye button */')
    for role in ('toggle-icon', 'toggle-icon-disabled'):
        w(f'  --al-password-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* focus rings - they point to the composite shadow, not the raw color */')
    for role, ref in RING.items():
        w(f'  --al-password-{role}: {css_ref(ref)};')

    w('')
    w('  /* geometry */')
    for role, ref in GEOM.items():
        w(f'  --al-password-{role}: {css_ref(ref)};')

    w('')
    w('  /* typography - one style becomes four vars */')
    for role, ref in TYPE.items():
        style = resolve_foundation(ref)
        key = size_key(style[1])
        prefix = f'--al-password-{role}'.replace('-font', '')
        if role == 'font':
            prefix = '--al-password'
        w(f'  {prefix}-font-size: var(--al-font-size-{key});')
        w(f'  {prefix}-line-height: var(--al-line-height-{key});')
        w(f'  {prefix}-font-weight: {style[3]};')
        w(f'  {prefix}-tracking: {style[4]};')

    w('}')
    w('')

    # Lock inherited from the Select: a forgotten group list breaks the build
    # instead of leaving a variable silently missing.
    text = '\n'.join(L)
    missing = [r for r in COLOR if f'--al-password-{r}:' not in text]
    if missing:
        raise AssertionError(
            'color roles missing from the CSS (some group list in write_css was not '
            f'updated): {missing}')

    save_css('password', text)


if __name__ == '__main__':
    sys.exit(run())
