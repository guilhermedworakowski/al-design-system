"""
Token layer for the Radio.

The one rule of this layer: nothing here invents a value. Every token points
to a Foundation token by NAME. The gate at the end of the file rejects
anything that is a loose value - hex, px, number.

Naming:
  code  -> radio-border-hover      (hyphen)
  Figma -> border/strong           (folder)
Figma has no variable per component: the node binds the semantic or
Foundation variable the token points to.
Hyphen in code, folder in Figma: they are different layers. Never
collapse one into the other.

IT IS THE NATIVE `<input type="radio">`

  The same choice as the Select and the Checkbox: the control belongs to the
  browser, the component paints the circle on top with `appearance: none`.
  Arrows inside the group, Tab entering only once and "checking one unchecks
  the other" belong to the input, as long as the radios of the same question
  share the same `name`.

ONE SIZE ONLY - THE TIER 2 RULE

  A 24x24 circle, the same as the Checkbox box and the label's line height -
  that is what aligns the circle with the first line of text.

CHECKED DOESN'T PAINT THE BACKGROUND - THE DIFFERENCE FROM THE CHECKBOX

  In the Checkbox, checked = orange box. In the Radio, checked = orange border
  + orange dot, with the background staying `bg`: the white ring between the
  border and the dot IS the background. That is why there is no `bg-checked`,
  and there are `dot` and `dot-disabled` instead of `icon` / `icon-disabled`.

FIGMA HAS ONE AXIS, THE BROWSER HAS TWO

  The component set (node 230:611) has six variants on one `State` axis:
  Default, Hover, Active (= checked), Error, Disabled, Focus. The combinations
  the input produces are covered by the same tokens, with the same solution as
  the Checkbox (decided in the audit, 2026-09-24):

    checked + hover        -> nothing changes; hover only when unchecked (a
                              checked radio doesn't uncheck on click - the hover
                              would promise an action)
    checked + focus        -> ring on top of the orange ring
    error + checked        -> orange border and dot, red label
    checked + disabled     -> `bg-disabled`, `border-disabled`, dot in
                              `dot-disabled`

  `radio-dot-disabled` is the only token with no variant in Figma - the mirror
  of `checkbox-icon-disabled`.

THE ERROR BELONGS TO THE QUESTION, NOT TO THE RADIO

  Precedent Primer / Carbon / Spectrum / Polaris: the Error variant lights up
  on ALL the radios of the same question at once, never on just one. There is
  no group component (by design): the message and `aria-invalid` belong to the
  form. That is a usage rule, not a token.

`border-hover` AND `border-focus` POINT TO THE SAME ALIAS, AND ARE TWO TOKENS

  The same logic as the Select and the Checkbox: today they coincide, and two
  names let one diverge from the other later without a breaking change.

THE DOT HAS NO SIZE TOKEN

  14 = circle 24 - 2 x border 1 - 2 x padding 4. It is derived, and 14 doesn't
  even exist on the scale - tokenizing it would store the same decision in two
  places. The padding is `space-4` (not the Checkbox's `space-2`) since the
  audit: at 18px the dot filled the circle and checked + disabled became a gray
  disc identical to unchecked + disabled.

TWO DECLARED CONTRAST EXCEPTIONS

  See PENDING. The same as the Checkbox.
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
    'bg':               'bg-surface-raised',   # unchecked AND checked (white ring)
    'bg-hover':         'bg-hover',
    'bg-disabled':      'bg-disabled',

    'border':           'border-default',
    'border-hover':     'border-strong',
    'border-focus':     'border-strong',
    'border-checked':   'border-brand',
    'border-error':     'border-danger',
    'border-disabled':  'border-default',

    'dot':              'bg-brand',        # the checked dot - 3:1 floor
    'dot-disabled':     'text-disabled',   # checked + disabled, no variant in Figma

    'label':            'text-primary',
    'label-error':      'text-danger',
    'label-disabled':   'text-disabled',
}

# The token points to the COMPOSITE SHADOW, not the raw color.
RING = {
    'ring': 'focusRing.default',
}

RING_INK = {
    'ring': 'shadow-focus-default',
}

# ------------------------------------------------------------- geometry
GEOM = {
    'box-size':     'iconSize.24',
    'padding':      'space.4',        # border -> dot
    'gap':          'space.8',        # circle -> label
    'radius':       'radius.full',
    'border-width': 'border.width.1',
}

TYPE = {
    'label-font': 'type.styles.body-md',
}

PENDING = {
    'border-below-3-1': (
        'The border of the unchecked circle at rest uses `border-default`: 1.57:1 in light '
        'and 1.46:1 in dark (against the circle background), below the 3:1 of WCAG 1.4.11. '
        'The same conscious decision as the Checkbox (2026-09-23), carried over to the Radio '
        'on 2026-09-24: follow the pattern of the DS inputs. The border is the only drawing '
        'of the unchecked control; the visible label rule is what backs the exception. '
        'Hover and focus (border-strong), checked (border-brand) and error (border-danger) '
        'pass. DO NOT "fix" it without revisiting that decision.'
    ),
    'disabled-below-aa': (
        'Label, border and dot in disabled fall below the floor. WCAG 1.4.3 / 1.4.11 exempt '
        'inactive components - the same permanent exception as the Button, the Tag, the '
        'Select and the Checkbox. Raising that contrast makes disabled look clickable.'
    ),
}

CANVAS = 'bg-canvas'   # not a Radio token: it is the canvas the Radio is placed on

# (role, radio token, background(s), floor, exception key in PENDING)
# The border has two neighboring surfaces - the canvas outside and the circle
# inside - and the WORSE of the two counts. The dot measures against `bg`: it
# is the white ring that separates it from the border, not the canvas.
COMBOS = [
    ('label',           'label',           'canvas',                   4.5, None),
    ('label-error',     'label-error',     'canvas',                   4.5, None),
    ('label-disabled',  'label-disabled',  'canvas',                   4.5, 'disabled-below-aa'),
    ('border-rest',     'border',          ('canvas', 'bg'),           3.0, 'border-below-3-1'),
    ('border-hover',    'border-hover',    ('canvas', 'bg-hover'),     3.0, None),
    ('border-focus',    'border-focus',    ('canvas', 'bg'),           3.0, None),
    ('border-checked',  'border-checked',  ('canvas', 'bg'),           3.0, None),
    ('border-error',    'border-error',    ('canvas', 'bg'),           3.0, None),
    ('border-disabled', 'border-disabled', ('canvas', 'bg-disabled'),  3.0, 'disabled-below-aa'),
    ('dot',             'dot',             'bg',                       3.0, None),
    ('dot-disabled',    'dot-disabled',    'bg-disabled',              3.0, 'disabled-below-aa'),
    ('focus-ring',      'ring',            'canvas',                   3.0, None),
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
    floor: text 4.5:1 from 1.4.3, border and dot 3:1 from 1.4.11."""
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
        name = f'radio-{role}'
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
        name = f'radio-{role}'
        alias[name] = ref
        try:
            v = resolve_foundation(ref)
            resolved[name] = {'light': v['light'], 'dark': v['dark']}
        except KeyError:
            problems.append(f'{name}: {ref} does not exist in the Foundation')

    for group in (GEOM, TYPE):
        for role, ref in group.items():
            name = f'radio-{role}'
            alias[name] = ref
            try:
                resolved[name] = resolve_foundation(ref)
            except KeyError:
                problems.append(f'{name}: {ref} does not exist in the Foundation')

    if problems:
        print(f'{len(problems)} TOKEN(S) FAIL THE ALIAS GATE:')
        for p in problems:
            print('   ', p)
        return 1

    # derived - a check, not a token. See the note in the header.
    box = resolve_foundation(GEOM['box-size'])
    pad = resolve_foundation(GEOM['padding'])
    bw = resolve_foundation(GEOM['border-width'])
    line = resolve_foundation(TYPE['label-font'])[2]
    derived = {
        'dot-size': box - 2 * bw - 2 * pad,
        'row-height': max(box, line),
    }

    rows = contrast_rows()
    fails = [r for r in rows if not r['pass'] and not r['exception']]
    excs = [r for r in rows if not r['pass'] and r['exception']]

    print('=' * 74)
    print('RADIO TOKEN LAYER')
    print('=' * 74)
    for name in sorted(alias):
        print(f'  {name:<26} -> {alias[name]}')
    print('-' * 74)
    print(f'derived dot: {derived["dot-size"]}px  (circle - 2 x border - 2 x padding)')
    print(f'row height: {derived["row-height"]}px')
    # a check, not a gate: circle and line height must match - that is what
    # aligns the circle with the label's first line without changing the height
    if box != line:
        print(f'  WARNING: box-size {box} != label line height {line}')
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

    if fails:
        print(f'{len(fails)} COMBINATION(S) FAIL THE CONTRAST GATE:')
        for f in fails:
            print(f'    {f["what"]} ({f["theme"]}): {f["ratio"]}:1 < {f["min"]}')
        return 1

    print(f'{len(alias)} tokens, all aliases of the Foundation. 0 loose values.')

    out = {
        'meta': {
            'component': 'Radio',
            'version': '0.1.0',
            'foundation': FOUND['meta']['version'],
            'figmaNode': '230:611',
            'variants': [],
            'sizes': ['md'],
            'states': ['default', 'hover', 'checked', 'error', 'disabled', 'focus'],
            'note': (
                'It is the NATIVE <input type="radio">, with the circle painted on top. '
                'One size only (24px circle), the rule for every Tier 2 input. Checked '
                'doesn\'t paint the background: orange border and dot, with the white ring '
                'between them. Figma has a single state axis; the combinations the browser '
                'produces (checked + focus/disabled/error) are covered by the same tokens, '
                'plus `dot-disabled`, which has no variant in Figma. The error lights up on '
                'every radio of the question; message and aria-invalid belong to the form. '
                'Two contrast exceptions declared in pending.'
            ),
        },
        'alias': alias,
        'resolved': resolved,
        'derived': derived,
        'contrast': rows,
        'pending': PENDING,
    }
    json.dump(out, open(comp_out('radio', 'tokens.json'), 'w'), indent=2, ensure_ascii=False)
    print('\nbuild/components/radio/tokens.json written')
    write_css(alias, derived)
    return 0


# ------------------------------------------------------------------- css
def write_css(alias, derived):
    L = []
    w = L.append
    w('/* AL Design System - Radio tokens')
    w(' * GENERATED by src/components/radio/tokens.py. Do not edit by hand.')
    w(' *')
    w(' * No theme block: each token points to a semantic, and the theme switches')
    w(' * on :root - the same element where these aliases are declared.')
    w(' *')
    w(f' * Dot: {derived["dot-size"]}px, derived, no token.')
    w(' */')
    w('')
    w(':root {')

    w('')
    w('  /* circle background - checked stays on `bg`: it is the white ring */')
    for role in ('bg', 'bg-hover', 'bg-disabled'):
        w(f'  --al-radio-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* circle border */')
    for role in ('border', 'border-hover', 'border-focus', 'border-checked',
                 'border-error', 'border-disabled'):
        w(f'  --al-radio-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* the checked dot */')
    for role in ('dot', 'dot-disabled'):
        w(f'  --al-radio-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* label - it lives outside the circle, on the canvas */')
    for role in ('label', 'label-error', 'label-disabled'):
        w(f'  --al-radio-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* focus ring - points to the composite shadow, not the raw color */')
    for role, ref in RING.items():
        w(f'  --al-radio-{role}: {css_ref(ref)};')

    w('')
    w('  /* geometry */')
    for role, ref in GEOM.items():
        w(f'  --al-radio-{role}: {css_ref(ref)};')

    w('')
    w('  /* typography - one style becomes four vars */')
    for role, ref in TYPE.items():
        style = resolve_foundation(ref)
        key = size_key(style[1])
        prefix = f'--al-radio-{role}'.replace('-font', '')
        w(f'  {prefix}-font-size: var(--al-font-size-{key});')
        w(f'  {prefix}-line-height: var(--al-line-height-{key});')
        w(f'  {prefix}-font-weight: {style[3]};')
        w(f'  {prefix}-tracking: {style[4]};')

    w('}')
    w('')

    # Lock: a forgotten group list becomes a broken build, not a missing variable.
    text = '\n'.join(L)
    missing = [r for r in COLOR if f'--al-radio-{r}:' not in text]
    if missing:
        raise AssertionError(
            'color roles missing from the CSS (some group list in write_css was not '
            f'updated): {missing}')

    save_css('radio', text)


if __name__ == '__main__':
    sys.exit(run())
