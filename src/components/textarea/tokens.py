"""
Token layer for the Textarea.

The one rule of this layer: nothing here invents a value. Every token points
to a Foundation token by NAME. The gate at the end of the file rejects
anything that is a loose value - hex, px, number.

Naming:
  code  -> textarea-border-hover      (hyphen)
  Figma -> textarea/border/hover      (folder)
They are different layers. Never collapse one into the other.

MULTI-LINE TEXT FIELD

  It is the Input without prefix and suffix. The same seven states (Default,
  Hover, Error, focusError, Disabled, focusDefault, readOnly), the same colors,
  the same two contrast exceptions - and so the same measurements. No Active
  and no Typed, for the same reason as the Input: a text field always matches
  `:focus-visible`, and having a value is content, not a state. See the header
  of components/input/tokens.py.

  Prefix and suffix stay out: a fixed part of the value makes no sense in
  free multi-line text. No `affix`.

THE FOCUS BORDER IS `border-brand`, FOR CONSISTENCY

  The same as the Input and the Select (decided on 2026-10-06). In dark
  `border-brand` stays orange-500 and the `shadow-focus-default` ring is
  orange-400; `border-focus` would match the two. Changing it only here would
  make the Textarea different from its siblings - if it ever changes, it is a
  PATCH on all three together.

HEIGHT IS NOT A TOKEN: IT IS THREE LINES

  96 = padding-y x2 + 3 line heights (12 + 72 + 12), with the 1px border
  overlapping the padding. The three lines are the HTML `rows="3"` attribute,
  not a token - no Foundation scale stores "number of lines". Total height:
  label 24 + gap 8 + field 96 = 128, and 152 with the help text.

FIXED HEIGHT, RESIZES ONLY VERTICALLY

  Text longer than the field scrolls. The person can drag the corner down
  (`resize: vertical`); not horizontally, because width belongs to the form.
  It doesn't grow by itself in this version. Disabled doesn't resize
  (`resize: none`); read-only does - whoever reads a long text may want to
  make room.

  The grip and the scrollbar belong to the browser and have NO token. What the
  CSS guarantees is that they follow the theme (`color-scheme`).

THE GAP IS ONE IN TWO PLACES

  `textarea-gap` applies to the vertical stack (label -> field -> help) and to
  the space between the label and "(Optional)". Both are 8.
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

# Visible lines. It is NOT a token: it is the HTML `rows` attribute, and the
# field height derives from it. See the header.
ROWS = 3

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
    'gap':          'space.8',       # stack, label -> optional
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
        'decision as the Select, extended to read-only in the Input on 2026-09-26 and '
        'inherited by the Textarea. The criterion does not fail when the border is not the '
        'only way to perceive the component, and here it is not: the field has a visible '
        'label above and text inside. DO NOT "fix" it without revisiting that decision.'
    ),
    'disabled-below-aa': (
        'Label, text and border in disabled fall below the minimum. WCAG 1.4.3 exempts '
        'inactive components - the same permanent exception as the Button, the Tag, the '
        'Select and the Input. Raising that contrast makes disabled look editable.'
    ),
}

CANVAS = 'bg-canvas'   # not a Textarea token: it is the canvas the Textarea is placed on

# (role, textarea token, background(s), floor, exception key in PENDING)
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
    ('value-readonly',    'text-value',       'bg-readonly',              4.5, None),
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
        name = f'textarea-{role}'
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
        name = f'textarea-{role}'
        alias[name] = ref
        try:
            v = resolve_foundation(ref)
            resolved[name] = {'light': v['light'], 'dark': v['dark']}
        except KeyError:
            problems.append(f'{name}: {ref} does not exist in the Foundation')

    for group in (GEOM, TYPE):
        for role, ref in group.items():
            name = f'textarea-{role}'
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
    field_h = pad_y * 2 + field_line * ROWS
    derived = {
        'rows': ROWS,
        'field-height': field_h,
        'total-height': label_line + gap + field_h,
        'total-height-with-help': label_line + gap + field_h + gap + help_line,
    }

    rows = contrast_rows()
    fails = [r for r in rows if not r['pass'] and not r['exception']]
    excs = [r for r in rows if not r['pass'] and r['exception']]

    print('=' * 74)
    print('TEXTAREA TOKEN LAYER')
    print('=' * 74)
    for name in sorted(alias):
        print(f'  {name:<26} -> {alias[name]}')
    print('-' * 74)
    print(f'derived field height: {derived["field-height"]}px  '
          f'(padding-y x2 + {ROWS} line heights; border overlapping the padding)')
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
            'component': 'Textarea',
            'version': '0.1.0',
            'foundation': FOUND['meta']['version'],
            'figmaNode': '294:71',
            'variants': [],
            'sizes': ['md'],
            'states': ['default', 'hover', 'error', 'focus-error',
                       'disabled', 'focus', 'readonly'],
            'note': (
                'A multi-line text field. It is the Input without prefix and suffix: the '
                'same seven states, the same colors, the same exceptions. One size only, '
                'with 3 visible lines (96px, rows attribute). Fixed height, scrolls when '
                'the text goes over, resizes only vertically; disabled doesn\'t resize. '
                'Grip and scrollbar belong to the browser, no token. Focus border in '
                'border-brand for consistency with the Input and the Select. The counter '
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
    json.dump(out, open(comp_out('textarea', 'tokens.json'), 'w'), indent=2, ensure_ascii=False)
    print('\nbuild/components/textarea/tokens.json written')
    write_css(alias, derived)
    return 0


# ------------------------------------------------------------------- css
def write_css(alias, derived):
    L = []
    w = L.append
    w('/* AL Design System - Textarea tokens')
    w(' * GENERATED by src/components/textarea/tokens.py. Do not edit by hand.')
    w(' *')
    w(' * There is no theme block here: each token points to a semantic, and the')
    w(' * theme switches on :root - the same element where these aliases are declared.')
    w(' *')
    w(f' * Field height: {derived["field-height"]}px, derived ({ROWS} lines), no token.')
    w(' */')
    w('')
    w(':root {')

    w('')
    w('  /* background - only disabled and readonly change it */')
    for role in ('bg', 'bg-disabled', 'bg-readonly'):
        w(f'  --al-textarea-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* border - the axis that carries the state */')
    for role in ('border', 'border-hover', 'border-focus', 'border-error',
                 'border-disabled', 'border-readonly'):
        w(f'  --al-textarea-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* text inside the field - placeholder x value is NOT an interaction state */')
    for role in ('text-placeholder', 'text-value', 'text-disabled'):
        w(f'  --al-textarea-{role}: {css_ref(COLOR[role])};')


    w('')
    w('  /* label, mark, counter and help - they live outside the field, on the canvas */')
    for role in ('label', 'label-error', 'label-disabled', 'optional',
                 'counter', 'counter-error', 'help', 'help-error'):
        w(f'  --al-textarea-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* focus ring - points to the composite shadow, not the raw color */')
    for role, ref in RING.items():
        w(f'  --al-textarea-{role}: {css_ref(ref)};')

    w('')
    w('  /* geometry */')
    for role, ref in GEOM.items():
        w(f'  --al-textarea-{role}: {css_ref(ref)};')

    w('')
    w('  /* typography - one style becomes four vars */')
    for role, ref in TYPE.items():
        style = resolve_foundation(ref)
        key = size_key(style[1])
        prefix = f'--al-textarea-{role}'.replace('-font', '')
        if role == 'font':
            prefix = '--al-textarea'
        w(f'  {prefix}-font-size: var(--al-font-size-{key});')
        w(f'  {prefix}-line-height: var(--al-line-height-{key});')
        w(f'  {prefix}-font-weight: {style[3]};')
        w(f'  {prefix}-tracking: {style[4]};')

    w('}')
    w('')

    # Lock inherited from the Select: a forgotten group list breaks the build
    # instead of leaving a variable silently missing.
    text = '\n'.join(L)
    missing = [r for r in COLOR if f'--al-textarea-{r}:' not in text]
    if missing:
        raise AssertionError(
            'color roles missing from the CSS (some group list in write_css was not '
            f'updated): {missing}')

    save_css('textarea', text)


if __name__ == '__main__':
    sys.exit(run())
