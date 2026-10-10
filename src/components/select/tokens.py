"""
Token layer for the Select.

The one rule of this layer: nothing here invents a value. Every token points
to a Foundation token by NAME. The gate at the end of the file rejects
anything that is a loose value - hex, px, number.

Naming:
  code  -> select-border-hover      (hyphen)
  Figma -> border/strong            (folder)
Figma has no variable per component: the node binds the semantic or
Foundation variable the token points to.
Hyphen in code, folder in Figma: they are different layers. Never
collapse one into the other.

IT IS THE NATIVE `<select>`

  The list of options is drawn by the browser and the operating system. The
  component only delivers the closed trigger. That is not missing scope: it is
  the same distinction Carbon makes between *Select* (native) and *Dropdown* /
  *ComboBox* (drawn). The practical consequence for this layer: there is no
  panel token, no option item token and no selected item token, because none
  of that is ours to paint.

THE BORDER IS THE AXIS THAT CARRIES THE STATE

  The field background doesn't change between rest, hover, active, focus and
  error - only the border changes. That is why there is one `bg` and six
  `border-*`. The only state that touches the background is disabled, and it
  does because it needs to stop looking like a field you can type into.

`border-active` AND `border-focus` POINT TO THE SAME ALIAS, AND ARE TWO TOKENS

  Active is the INSTANT the mouse button is held down; focus is the state that
  STAYS while the field is focused, by Tab or by click. The original reading
  ("focus is arriving by Tab") fell in QA, measured: Chromium matches
  `:focus-visible` on a <select> clicked with the mouse. Today both resolve to
  `border-brand` and are pixel-identical. Keeping two names is what lets one
  diverge from the other later without a breaking change - and what stops
  someone from reading the CSS and concluding that both states are the same
  thing.

THE SELECT IS THE FIRST COMPONENT WITH AN ICON COLOR TOKEN

  In the Button and the Tag the icon is `currentColor`: it inherits the label's
  color and so it needs no token. Not here. At rest the field text is
  `text-placeholder` (#717171) and the chevron is `text-primary` (#292929) -
  two different colors inside the same box. If the chevron inherited, it would
  lighten together with the placeholder, which is not the design. That is why
  `select-icon` and `select-icon-disabled` exist.

  The chevron's floor is the 3:1 of 1.4.11 (non-text), not the 4.5:1 of 1.4.3
  - the same rule already set with the Icon and the Icon Button.

PLACEHOLDER x VALUE IS NOT AN INTERACTION STATE

  `select-text-placeholder` and `select-text-value` are two tokens that do NOT
  depend on the seven states. In Figma the dark text shows up in Active, Error
  and focusError, and the gray in Default, Hover and focusDefault - but that is
  only what each mockup chose to show. On screen, someone who picked an option
  and moved the mouse away goes back to rest WITH the chosen value, and the
  text stays dark. In CSS the switch is `:has(option[value=""]:checked)` -
  "still on the placeholder" - and never `:hover` or `:active`.

HEIGHT IS NOT A TOKEN

  48 = padding-y x2 + the text's line height (12+24+12), with the 1px border
  overlapping the padding - in CSS, `padding: calc(12px - 1px)`. It is the same
  convention as the Button and the Tag. Tokenizing the height would pin the
  same decision in two places, with two chances to diverge.

  The total height is derived too: label 24 + gap 8 + field 48 = 80, and 104
  when the help text shows (+8 +16).

THE "(OPTIONAL)" MARK MARKS THE OPPOSITE OF THE USUAL

  Decided on 2026-09-17: AL marks the OPTIONAL field, not the required one:
  whatever has no mark is required. It is the opposite school to Polaris's
  asterisk, and it wins when most of the form's fields are required - you mark
  the minority. `select-optional` and `select-optional-font` exist only for
  that; the mark sits next to the label, in `Body/sm`, one line height smaller
  than the label on purpose, so it doesn't compete with it.

  There is no "required" token: the absence of the mark IS required, and an
  absence isn't tokenized.

THE GAP IS ONE ON BOTH AXES

  `select-gap` applies to the vertical stack (label -> field -> help) AND to
  the horizontal space between the label and the "(Optional)" mark. Both are 8
  and both separate parts of the SAME component. Two tokens with the same value
  would be two places for the same breathing room to drift by mistake. If they
  ever need to diverge, then it becomes `gap-x` and `gap-y`.

WIDTH IS NOT A TOKEN

  The field takes 100% of its container. The form decides width; the
  component doesn't.

DECLARED CONTRAST EXCEPTIONS

  All in `pending`, all named, none silent. See PENDING right below.
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
# One size, no variant: the list is flat. What varies is the state, and the
# state almost always only touches the border.
COLOR = {
    'bg':               'bg-surface-raised',
    'bg-disabled':      'bg-disabled',

    'border':           'border-default',
    'border-hover':     'border-strong',
    'border-active':    'border-brand',
    'border-focus':     'border-brand',
    'border-error':     'border-danger',
    'border-disabled':  'border-default',

    'text-placeholder': 'text-placeholder',
    'text-value':       'text-primary',
    'text-disabled':    'text-disabled',

    'label':            'text-primary',
    'label-error':      'text-danger',
    'label-disabled':   'text-disabled',

    'help':             'text-secondary',
    'help-error':       'text-danger',

    'optional':         'text-secondary',

    'icon':             'text-primary',    # vector glyph - 3:1 floor
    'icon-disabled':    'text-disabled',
}

# The token points to the COMPOSITE SHADOW, not the raw color - same rule as
# `button-*-ring`. The color is only extracted for measuring, in RING_INK below.
RING = {
    'ring':       'focusRing.default',
    'ring-error': 'focusRing.error',
}

# Where each ring's color comes from when the gate needs to measure contrast.
# It doesn't become a token: it would be the same value stored twice.
RING_INK = {
    'ring':       'shadow-focus-default',
    'ring-error': 'shadow-focus-error',
}

# ------------------------------------------------------------- geometry
GEOM = {
    'padding-x':    'space.12',
    'padding-y':    'space.12',
    'gap':          'space.8',       # label -> field -> help text
    'radius':       'radius.lg',
    'border-width': 'border.width.1',
    'icon-size':    'iconSize.24',
}

TYPE = {
    'font':          'type.styles.body-md',
    'label-font':    'type.styles.body-md',
    'optional-font': 'type.styles.body-sm',
    'help-font':     'type.styles.caption',
}

PENDING = {
    'border-below-3-1': (
        'The border at rest and in disabled uses `border-default`: 1.57:1 in light and '
        '2.42:1 in dark, below the 3:1 of WCAG 1.4.11. A conscious decision made on '
        '2026-09-17, after seeing the numbers. The criterion does not fail when the border '
        'is not the only way to perceive the component, and here it is not: the field has '
        'a visible label above and text inside. Hover (4.88:1), active and focus (3.34:1) '
        'and error (5.38:1) all pass, so the weak border only exists at rest. '
        'DO NOT "fix" it without revisiting that decision.'
    ),
    'disabled-below-aa': (
        'Label, text and chevron in disabled sit between 1.59:1 and 3.64:1. WCAG 1.4.3 '
        'exempts inactive components - the same permanent exception the Button and the '
        'Tag already carry. Raising that contrast makes disabled look clickable.'
    ),
}

CANVAS = 'bg-canvas'   # not a Select token: it is the canvas the Select is placed on

# The combinations the component really renders: each role against the
# background it really lives on. Label, help text and focus ring live OUTSIDE
# the field, so they measure against the canvas; what is inside measures
# against the field background. Without that the gate would measure a token
# pair in a vacuum - and in the dark theme the difference is real: the canvas
# is #181818 and the field is #3E3E3E.
#
# THE BORDER HAS TWO NEIGHBORING SURFACES - the canvas outside and the field
# background inside - and it has to separate from BOTH to draw a boundary.
# That is why its background is a tuple: the gate measures against each one
# and keeps the WORST. Measuring only against the canvas would let a border
# that disappears on the inside pass.
#
# (role, select token, background(s), floor, exception key in PENDING)
COMBOS = [
    ('label',            'label',            'canvas',                   4.5, None),
    ('label-error',      'label-error',      'canvas',                   4.5, None),
    ('label-disabled',   'label-disabled',   'canvas',                   4.5, 'disabled-below-aa'),
    ('placeholder',      'text-placeholder', 'bg',                       4.5, None),
    ('value',            'text-value',       'bg',                       4.5, None),
    ('text-disabled',    'text-disabled',    'bg-disabled',              4.5, 'disabled-below-aa'),
    ('chevron',          'icon',             'bg',                       3.0, None),
    ('chevron-disabled', 'icon-disabled',    'bg-disabled',              3.0, 'disabled-below-aa'),
    ('optional',         'optional',         'canvas',                   4.5, None),
    ('help',             'help',             'canvas',                   4.5, None),
    ('help-error',       'help-error',       'canvas',                   4.5, None),
    ('border-rest',      'border',           ('canvas', 'bg'),           3.0, 'border-below-3-1'),
    ('border-hover',     'border-hover',     ('canvas', 'bg'),           3.0, None),
    ('border-active',    'border-active',    ('canvas', 'bg'),           3.0, None),
    ('border-focus',     'border-focus',     ('canvas', 'bg'),           3.0, None),
    ('border-error',     'border-error',     ('canvas', 'bg'),           3.0, None),
    ('border-disabled',  'border-disabled',  ('canvas', 'bg-disabled'),  3.0, 'disabled-below-aa'),
    ('focus-ring',       'ring',             'canvas',                   3.0, None),
    ('focus-ring-error', 'ring-error',       'canvas',                   3.0, None),
]


# ------------------------------------------------------------------ gate
def ink(role):
    """The color semantic behind a role - following the ring down to the color.

    `canvas` is not a Select role: it is the canvas the Select is placed on. It
    stays out of COLOR on purpose - the component doesn't paint the page
    background.
    """
    if role == 'canvas':
        return CANVAS
    if role in RING_INK:
        return RING_INK[role]
    return COLOR[role]


def contrast_rows():
    """Measures each rendered combination in both themes, each against its own
    floor: text 4.5:1 from 1.4.3, border and glyph 3:1 from 1.4.11."""
    rows = []
    for what, fg_role, bg_spec, min_ratio, exc in COMBOS:
        fg_ref = ink(fg_role)
        bg_roles = bg_spec if isinstance(bg_spec, tuple) else (bg_spec,)
        for theme, i in (('light', 0), ('dark', 1)):
            # when there is more than one neighboring surface, the WORST counts
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
        name = f'select-{role}'
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
        name = f'select-{role}'
        alias[name] = ref
        try:
            v = resolve_foundation(ref)
            resolved[name] = {'light': v['light'], 'dark': v['dark']}
        except KeyError:
            problems.append(f'{name}: {ref} does not exist in the Foundation')

    for group in (GEOM, TYPE):
        for role, ref in group.items():
            name = f'select-{role}'
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
    print('SELECT TOKEN LAYER')
    print('=' * 74)
    for name in sorted(alias):
        print(f'  {name:<26} -> {alias[name]}')
    print('-' * 74)
    print(f'derived field height: {derived["field-height"]}px  '
          f'(padding-y x2 + line height; border overlapping the padding)')
    print(f'total height: {derived["total-height"]}px  '
          f'| with help text: {derived["total-height-with-help"]}px')
    # a check, not a gate: the chevron must match the text's line height - that
    # is what keeps the chevron from changing the field's height
    icon = resolve_foundation(GEOM['icon-size'])
    if icon != field_line:
        print(f'  WARNING: icon-size {icon} != line height {field_line} - the chevron changes the height')
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
            'component': 'Select',
            'version': '0.1.0',
            'foundation': FOUND['meta']['version'],
            'figmaNode': '227:204',
            'variants': [],
            'sizes': ['md'],
            'states': ['default', 'hover', 'active', 'error',
                       'focus-error', 'disabled', 'focus'],
            'note': (
                'It is the NATIVE <select>: the list of options is drawn by the browser, '
                'so there is no panel, option or selected item token. One size only '
                '(48px), a declared choice - like the lg left out of the Button. The '
                'border is the axis that carries the state: the background only changes '
                'in disabled. `border-active` and `border-focus` point to the same alias '
                'on purpose - click and Tab are distinct states that coincide today. The '
                'first AL component with an icon color token, because the chevron cannot '
                'inherit the placeholder color. The "(Optional)" mark next to the label '
                'marks the OPPOSITE of the usual: whatever has no mark is required - there '
                'is no required token. Contrast exceptions declared in pending.'
            ),
        },
        'alias': alias,
        'resolved': resolved,
        'derived': derived,
        'contrast': rows,
        'pending': PENDING,
    }
    json.dump(out, open(comp_out('select', 'tokens.json'), 'w'), indent=2, ensure_ascii=False)
    print('\nbuild/components/select/tokens.json written')
    write_css(alias, derived)
    return 0


# ------------------------------------------------------------------- css
def write_css(alias, derived):
    L = []
    w = L.append
    w('/* AL Design System - Select tokens')
    w(' * GENERATED by src/components/select/tokens.py. Do not edit by hand.')
    w(' *')
    w(' * There is no theme block here, and that is the point: each token points')
    w(' * to a semantic, and the theme switches on :root - the same element where')
    w(' * these aliases are declared. So :root re-substitutes all of them at once.')
    w(' *')
    w(f' * Field height: {derived["field-height"]}px, derived, no token.')
    w(' */')
    w('')
    w(':root {')

    w('')
    w('  /* background - only disabled changes it */')
    for role in ('bg', 'bg-disabled'):
        w(f'  --al-select-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* border - the axis that carries the state */')
    for role in ('border', 'border-hover', 'border-active', 'border-focus',
                 'border-error', 'border-disabled'):
        w(f'  --al-select-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* text inside the field - placeholder x value is NOT an interaction state */')
    for role in ('text-placeholder', 'text-value', 'text-disabled'):
        w(f'  --al-select-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* label, optional mark and help - they live outside the field, on the canvas */')
    for role in ('label', 'label-error', 'label-disabled',
                 'optional', 'help', 'help-error'):
        w(f'  --al-select-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* chevron - it doesn\'t inherit the text color, see the tokens.py header */')
    for role in ('icon', 'icon-disabled'):
        w(f'  --al-select-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* focus ring - points to the composite shadow, not the raw color */')
    for role, ref in RING.items():
        w(f'  --al-select-{role}: {css_ref(ref)};')

    w('')
    w('  /* geometry */')
    for role, ref in GEOM.items():
        w(f'  --al-select-{role}: {css_ref(ref)};')

    w('')
    w('  /* typography - one style becomes four vars */')
    for role, ref in TYPE.items():
        style = resolve_foundation(ref)
        key = size_key(style[1])
        prefix = f'--al-select-{role}'.replace('-font', '')
        if role == 'font':
            prefix = '--al-select'
        w(f'  {prefix}-font-size: var(--al-font-size-{key});')
        w(f'  {prefix}-line-height: var(--al-line-height-{key});')
        w(f'  {prefix}-font-weight: {style[3]};')
        w(f'  {prefix}-tracking: {style[4]};')

    w('}')
    w('')

    # The groups above are handwritten lists, so the CSS comes out grouped and
    # commented. The price of writing them by hand is forgetting a new role -
    # which is what happened when `optional` came in. This lock refuses to
    # generate if any color token didn't reach the file: a wrong list becomes a
    # broken build, not a variable silently missing.
    text = '\n'.join(L)
    missing = [r for r in COLOR if f'--al-select-{r}:' not in text]
    if missing:
        raise AssertionError(
            'color roles missing from the CSS (some group list in write_css was not '
            f'updated): {missing}')

    save_css('select', text)


if __name__ == '__main__':
    sys.exit(run())
