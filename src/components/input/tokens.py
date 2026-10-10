"""
Token layer for the Input.

The one rule of this layer: nothing here invents a value. Every token points
to a Foundation token by NAME. The gate at the end of the file rejects
anything that is a loose value - hex, px, number.

Naming:
  code  -> input-border-hover      (hyphen)
  Figma -> border/strong           (folder)
Figma has no variable per component: the node binds the semantic or
Foundation variable the token points to.
Hyphen in code, folder in Figma: they are different layers. Never
collapse one into the other.

SINGLE-LINE TEXT FIELD

  Covers `type` text, email, url and tel. Password becomes its own component
  (Password); number and search stay out of this version by choice - the same
  split as Carbon, which treats PasswordInput, NumberInput and Search as
  separate components. Also out, by choice: warning, leading icon, clear
  button and extra sizes.

SEVEN STATES, AND TWO LEFT OUT ON PURPOSE

  Default, Hover, Error, focusError, Disabled, focusDefault, readOnly.

  There is no Active. In the Select the click opens the list, so Active made
  sense; here nothing opens. And a text field ALWAYS matches `:focus-visible`,
  including on mouse click - the spec requires that for every element that
  accepts typing. A 1px orange Active border would only last the instant the
  button is held, and right after the focus ring would cover everything. That
  is also why there is no `border-active`.

  There is no Typed. Having a value is content, not interaction: a field can
  be on hover AND have a value. The placeholder/value switch is
  `:placeholder-shown` in CSS, never `:hover` or `:focus`.

THE BORDER IS THE AXIS THAT CARRIES THE STATE

  The field background doesn't change between rest, hover, focus and error -
  only the border does. The two states that touch the background are the ones
  that change what you CAN do with the field: disabled (nothing) and readOnly
  (read and copy, not edit).

READ-ONLY IS NOT DISABLED

  Disabled is exempt from WCAG 1.4.3 for being inactive; read-only is not. The
  content exists to be read - that is why the read-only text is `text-value`,
  the same as the editable field, and not a gray. There is no
  `input-text-readonly`: it would be the same value stored twice.

  The background is `bg-subtle`, decided on 2026-09-26. In the dark theme
  `bg-subtle` matches `bg-surface-raised` (#3E3E3E), so read-only and editable
  only separate by the border and the cursor - a conscious choice, not
  forgetfulness. Don't propose a semantic `bg-readonly` without a new reason.

  Read-only NEVER shows a placeholder. The placeholder gray on the read-only
  background gives 4.21:1, below the floor - and a placeholder is a hint about
  how to fill in, which doesn't apply to a field nobody fills in. The CSS hides
  it; the usage rule tells an empty read-only to show "—" as its value.

PREFIX AND SUFFIX HAVE THEIR OWN TOKEN

  With the field empty, the prefix ("www.") is dark and the placeholder next to
  it is gray - two colors on the same line. If the affix inherited the text
  color, it would lighten together with the placeholder. Hence `input-affix`.
  In disabled the affix uses `text-disabled`, like all text inside the
  disabled field.

THE COUNTER ONLY TURNS RED WHEN THE ERROR IS THE LIMIT

  In the Error state the counter stays `counter` (text-secondary): if the
  error is "required field", a red counter points to the wrong cause.
  `counter-error` exists for when the count goes over the limit, which only
  happens in code - Figma has no variant for it, and the variable exists there
  with no variant, like the Checkbox's `icon/disabled`.

HEIGHT IS NOT A TOKEN

  48 = padding-y x2 + the text's line height (12+24+12), with the 1px border
  overlapping the padding - in CSS, `padding: calc(12px - 1px)`. The same
  convention as the Button, the Tag and the Select. Total height: label 24 +
  gap 8 + field 48 = 80, and 104 with the help text (+8 +16).

THE GAP IS ONE IN THREE PLACES

  `input-gap` applies to the vertical stack (label -> field -> help), to the
  space between the label and "(Optional)" and to the space between the prefix
  and the text. All three are 8. The same rule as the Select: two tokens with
  the same value would be two places for the same breathing room to drift by
  mistake.

  The suffix doesn't use the gap: it is pushed to the field's right edge.

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
    'bg-readonly':      'bg-subtle',

    'border':           'border-default',
    'border-hover':     'border-strong',
    'border-focus':     'border-brand',
    'border-error':     'border-danger',
    'border-disabled':  'border-default',
    'border-readonly':  'border-subtle',

    'text-placeholder': 'text-placeholder',
    'text-value':       'text-primary',
    'text-disabled':    'text-disabled',

    'affix':            'text-primary',

    'label':            'text-primary',
    'label-error':      'text-danger',
    'label-disabled':   'text-disabled',

    'optional':         'text-secondary',

    'counter':          'text-secondary',
    'counter-error':    'text-danger',

    'help':             'text-secondary',
    'help-error':       'text-danger',
}

# The token points to the COMPOSITE SHADOW, not the raw color - same rule as
# `button-*-ring`. The color is only extracted for measuring, in RING_INK below.
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
    'gap':          'space.8',       # stack, label -> optional, prefix -> text
    'radius':       'radius.lg',
    'border-width': 'border.width.1',
}

TYPE = {
    'font':          'type.styles.body-md',
    'label-font':    'type.styles.body-md',
    'optional-font': 'type.styles.body-sm',
    'counter-font':  'type.styles.body-sm',
    'help-font':     'type.styles.caption',
}

PENDING = {
    'border-below-3-1': (
        'The border at rest uses `border-default` (1.57:1 in light, 1.46:1 in dark '
        'against the field background) and the read-only one uses `border-subtle` (1.14:1 '
        'in light, 1.00:1 in dark). Below the 3:1 of WCAG 1.4.11. The same conscious '
        'decision as the Select, extended to read-only on 2026-09-26. The criterion does '
        'not fail when the border is not the only way to perceive the component, and here '
        'it is not: the field has a visible label above and text inside. DO NOT "fix" it '
        'without revisiting that decision.'
    ),
    'disabled-below-aa': (
        'Label, text and border in disabled fall below the minimum. WCAG 1.4.3 exempts '
        'inactive components - the same permanent exception as the Button, the Tag and the '
        'Select. Raising that contrast makes disabled look editable.'
    ),
}

CANVAS = 'bg-canvas'   # not an Input token: it is the canvas the Input is placed on

# (role, input token, background(s), floor, exception key in PENDING)
# Label, mark, counter, help and ring live OUTSIDE the field and measure
# against the canvas; what is inside measures against that state's field
# background. The border measures against BOTH neighboring surfaces and keeps
# the worse.
#
# There is no placeholder x bg-readonly combination: read-only doesn't show a
# placeholder (see the header). The markup/QA gate checks that in the CSS.
COMBOS = [
    ('label',             'label',            'canvas',                   4.5, None),
    ('label-error',       'label-error',      'canvas',                   4.5, None),
    ('label-disabled',    'label-disabled',   'canvas',                   4.5, 'disabled-below-aa'),
    ('optional',          'optional',         'canvas',                   4.5, None),
    ('counter',           'counter',          'canvas',                   4.5, None),
    ('counter-error',     'counter-error',    'canvas',                   4.5, None),
    ('help',              'help',             'canvas',                   4.5, None),
    ('help-error',        'help-error',       'canvas',                   4.5, None),
    ('placeholder',       'text-placeholder', 'bg',                       4.5, None),
    ('value',             'text-value',       'bg',                       4.5, None),
    ('affix',             'affix',            'bg',                       4.5, None),
    ('value-readonly',    'text-value',       'bg-readonly',              4.5, None),
    ('affix-readonly',    'affix',            'bg-readonly',              4.5, None),
    ('text-disabled',     'text-disabled',    'bg-disabled',              4.5, 'disabled-below-aa'),
    ('border-rest',       'border',           ('canvas', 'bg'),           3.0, 'border-below-3-1'),
    ('border-hover',      'border-hover',     ('canvas', 'bg'),           3.0, None),
    ('border-focus',      'border-focus',     ('canvas', 'bg'),           3.0, None),
    ('border-error',      'border-error',     ('canvas', 'bg'),           3.0, None),
    ('border-disabled',   'border-disabled',  ('canvas', 'bg-disabled'),  3.0, 'disabled-below-aa'),
    ('border-readonly',   'border-readonly',  ('canvas', 'bg-readonly'),  3.0, 'border-below-3-1'),
    ('focus-ring',        'ring',             'canvas',                   3.0, None),
    ('focus-ring-error',  'ring-error',       'canvas',                   3.0, None),
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
    floor: text 4.5:1 from 1.4.3, border and ring 3:1 from 1.4.11."""
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
        name = f'input-{role}'
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
        name = f'input-{role}'
        alias[name] = ref
        try:
            v = resolve_foundation(ref)
            resolved[name] = {'light': v['light'], 'dark': v['dark']}
        except KeyError:
            problems.append(f'{name}: {ref} does not exist in the Foundation')

    for group in (GEOM, TYPE):
        for role, ref in group.items():
            name = f'input-{role}'
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
    field_h = pad_y * 2 + field_line
    derived = {
        'field-height': field_h,
        'total-height': label_line + gap + field_h,
        'total-height-with-help': label_line + gap + field_h + gap + help_line,
    }

    rows = contrast_rows()
    fails = [r for r in rows if not r['pass'] and not r['exception']]
    excs = [r for r in rows if not r['pass'] and r['exception']]

    print('=' * 74)
    print('INPUT TOKEN LAYER')
    print('=' * 74)
    for name in sorted(alias):
        print(f'  {name:<26} -> {alias[name]}')
    print('-' * 74)
    print(f'derived field height: {derived["field-height"]}px  '
          f'(padding-y x2 + line height; border overlapping the padding)')
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
            'component': 'Input',
            'version': '0.1.0',
            'foundation': FOUND['meta']['version'],
            'figmaNode': '263:502',
            'variants': [],
            'sizes': ['md'],
            'states': ['default', 'hover', 'error', 'focus-error',
                       'disabled', 'focus', 'readonly'],
            'note': (
                'A single-line text field (text, email, url, tel). Password becomes the '
                'Password component. One size only (48px). No Active - a text field always '
                'matches :focus-visible, including on click - and no Typed, because having '
                'a value is content, not a state. The border carries the state; the '
                'background only changes in disabled and readonly. Read-only is not exempt '
                'from contrast like disabled, uses the value text and never shows a '
                'placeholder. Prefix and suffix have their own token (`affix`). The counter '
                'only turns red when it goes over the limit. Two contrast exceptions '
                'declared in pending.'
            ),
        },
        'alias': alias,
        'resolved': resolved,
        'derived': derived,
        'contrast': rows,
        'pending': PENDING,
    }
    json.dump(out, open(comp_out('input', 'tokens.json'), 'w'), indent=2, ensure_ascii=False)
    print('\nbuild/components/input/tokens.json written')
    write_css(alias, derived)
    return 0


# ------------------------------------------------------------------- css
def write_css(alias, derived):
    L = []
    w = L.append
    w('/* AL Design System - Input tokens')
    w(' * GENERATED by src/components/input/tokens.py. Do not edit by hand.')
    w(' *')
    w(' * There is no theme block here: each token points to a semantic, and the')
    w(' * theme switches on :root - the same element where these aliases are declared.')
    w(' *')
    w(f' * Field height: {derived["field-height"]}px, derived, no token.')
    w(' */')
    w('')
    w(':root {')

    w('')
    w('  /* background - only disabled and readonly change it */')
    for role in ('bg', 'bg-disabled', 'bg-readonly'):
        w(f'  --al-input-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* border - the axis that carries the state */')
    for role in ('border', 'border-hover', 'border-focus', 'border-error',
                 'border-disabled', 'border-readonly'):
        w(f'  --al-input-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* text inside the field - placeholder x value is NOT an interaction state */')
    for role in ('text-placeholder', 'text-value', 'text-disabled'):
        w(f'  --al-input-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* prefix and suffix - they don\'t inherit the placeholder color */')
    w(f'  --al-input-affix: {css_ref(COLOR["affix"])};')

    w('')
    w('  /* label, mark, counter and help - they live outside the field, on the canvas */')
    for role in ('label', 'label-error', 'label-disabled', 'optional',
                 'counter', 'counter-error', 'help', 'help-error'):
        w(f'  --al-input-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* focus ring - points to the composite shadow, not the raw color */')
    for role, ref in RING.items():
        w(f'  --al-input-{role}: {css_ref(ref)};')

    w('')
    w('  /* geometry */')
    for role, ref in GEOM.items():
        w(f'  --al-input-{role}: {css_ref(ref)};')

    w('')
    w('  /* typography - one style becomes four vars */')
    for role, ref in TYPE.items():
        style = resolve_foundation(ref)
        key = size_key(style[1])
        prefix = f'--al-input-{role}'.replace('-font', '')
        if role == 'font':
            prefix = '--al-input'
        w(f'  {prefix}-font-size: var(--al-font-size-{key});')
        w(f'  {prefix}-line-height: var(--al-line-height-{key});')
        w(f'  {prefix}-font-weight: {style[3]};')
        w(f'  {prefix}-tracking: {style[4]};')

    w('}')
    w('')

    # Lock inherited from the Select: a forgotten group list breaks the build
    # instead of leaving a variable silently missing.
    text = '\n'.join(L)
    missing = [r for r in COLOR if f'--al-input-{r}:' not in text]
    if missing:
        raise AssertionError(
            'color roles missing from the CSS (some group list in write_css was not '
            f'updated): {missing}')

    save_css('input', text)


if __name__ == '__main__':
    sys.exit(run())
