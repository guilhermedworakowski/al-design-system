"""
Token layer for the Checkbox.

The one rule of this layer: nothing here invents a value. Every token points
to a Foundation token by NAME. The gate at the end of the file rejects
anything that is a loose value - hex, px, number.

Naming:
  code  -> checkbox-border-hover      (hyphen)
  Figma -> checkbox/border/hover      (folder)
They are different layers. Never collapse one into the other.

IT IS THE NATIVE `<input type="checkbox">`

  The same choice as the Select: the control belongs to the browser, the
  component paints the box on top with `appearance: none`. Keyboard (Space),
  the checked state and `indeterminate` belong to the input - there is no
  behavior of its own to build.

ONE SIZE ONLY - THE TIER 2 RULE

  Decided on 2026-09-23: every Tier 2 input has a single size. The box is
  24x24, the same 24 grid as the Lucide check drawing, and the same line
  height as the label - that is what aligns the box with the first line of
  text.

FIGMA HAS ONE AXIS, THE BROWSER HAS TWO

  The component set (node 229:509) has seven variants on one `State` axis:
  Default, Hover, Active (= checked), Error, Disabled, Focus, Indeterminate.
  Combined variants (checked + hover, checked + disabled...) were left out of
  this first version by design. But the native input produces those
  combinations anyway, so the tokens below cover them WITHOUT a new token,
  with one approved exception:

    checked + hover        -> the orange box doesn't change; hover only when unchecked
    checked + focus        -> ring on top of the orange box
    error + focus          -> default ring (there is no drawn error ring)
    error + checked        -> orange box, red label
    checked + disabled     -> `bg-disabled` with the check in `icon-disabled`

  `checkbox-icon-disabled` is the only token with no variant in Figma.
  Approved on 2026-09-23: the case shows up on any locked settings screen, and
  a "don't use" rule would be broken on first use.

`bg-checked` APPLIES TO CHECKED AND INDETERMINATE

  What tells them apart is the glyph (check x dash), not the box. One
  background token and one border token, like the design.

`border-hover` AND `border-focus` POINT TO THE SAME ALIAS, AND ARE TWO TOKENS

  The same logic as the Select's `border-active` / `border-focus`: today they
  coincide, and two names let one diverge from the other later without a
  breaking change.

THE ICON HAS A COLOR TOKEN

  The label is dark and the check is white - `currentColor` can't be
  inherited. The check's floor is the 3:1 of 1.4.11 (glyph), not 4.5:1: white
  on the brand gives 3.34:1 and passes with room to spare. It is not an
  exception.

THE ICON HAS NO SIZE TOKEN

  18 = box 24 - 2 x border 1 - 2 x padding 2. It is derived, and 18 doesn't
  even exist on the `icon-size` scale - tokenizing it would store the same
  decision in two places.

TWO DECLARED CONTRAST EXCEPTIONS

  See PENDING. The resting border one is NOT the same as the Select's, and
  that matters.
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
    'bg-hover':         'bg-hover',
    'bg-checked':       'bg-brand',        # checked and indeterminate
    'bg-disabled':      'bg-disabled',

    'border':           'border-default',
    'border-hover':     'border-strong',
    'border-focus':     'border-strong',
    'border-checked':   'border-brand',
    'border-error':     'border-danger',
    'border-disabled':  'border-default',

    'icon':             'text-on-brand',   # check and dash - 3:1 floor
    'icon-disabled':    'text-disabled',   # checked + disabled, no variant in Figma

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
    'padding':      'space.2',        # border -> glyph
    'gap':          'space.8',        # box -> label
    'radius':       'radius.sm',
    'border-width': 'border.width.1',
}

TYPE = {
    'label-font': 'type.styles.body-md',
}

PENDING = {
    'border-below-3-1': (
        'The border of the unchecked box at rest uses `border-default`: 1.57:1 in light and '
        '1.46:1 in dark (against the box background), below the 3:1 of WCAG 1.4.11. '
        'A conscious decision made on 2026-09-23, to follow the pattern of the DS inputs '
        '(the Select uses the same border). WARNING: the Select\'s argument does NOT hold '
        'here - in the Checkbox the border is the only drawing of the unchecked control; it '
        'was flagged as blocking in the audit and kept as a pattern decision. Hover and '
        'focus (border-strong) and error (border-danger) pass. DO NOT "fix" it without '
        'revisiting that decision.'
    ),
    'disabled-below-aa': (
        'Label, border and check in disabled fall below the floor. WCAG 1.4.3 / 1.4.11 '
        'exempt inactive components - the same permanent exception as the Button, the Tag '
        'and the Select. Raising that contrast makes disabled look clickable.'
    ),
}

CANVAS = 'bg-canvas'   # not a Checkbox token: it is the canvas the Checkbox is placed on

# (role, checkbox token, background(s), floor, exception key in PENDING)
# The border has two neighboring surfaces - the canvas outside and the box
# inside - and the WORSE of the two counts. The checked box measures the FILL
# against the canvas: it is the fill, not the border, that draws the boundary
# of the checked control.
COMBOS = [
    ('label',           'label',           'canvas',                   4.5, None),
    ('label-error',     'label-error',     'canvas',                   4.5, None),
    ('label-disabled',  'label-disabled',  'canvas',                   4.5, 'disabled-below-aa'),
    ('border-rest',     'border',          ('canvas', 'bg'),           3.0, 'border-below-3-1'),
    ('border-hover',    'border-hover',    ('canvas', 'bg-hover'),     3.0, None),
    ('border-focus',    'border-focus',    ('canvas', 'bg'),           3.0, None),
    ('border-error',    'border-error',    ('canvas', 'bg'),           3.0, None),
    ('border-disabled', 'border-disabled', ('canvas', 'bg-disabled'),  3.0, 'disabled-below-aa'),
    ('checked-box',     'bg-checked',      'canvas',                   3.0, None),
    ('check',           'icon',            'bg-checked',               3.0, None),
    ('check-disabled',  'icon-disabled',   'bg-disabled',              3.0, 'disabled-below-aa'),
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
    floor: text 4.5:1 from 1.4.3, border and glyph 3:1 from 1.4.11."""
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
        name = f'checkbox-{role}'
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
        name = f'checkbox-{role}'
        alias[name] = ref
        try:
            v = resolve_foundation(ref)
            resolved[name] = {'light': v['light'], 'dark': v['dark']}
        except KeyError:
            problems.append(f'{name}: {ref} does not exist in the Foundation')

    for group in (GEOM, TYPE):
        for role, ref in group.items():
            name = f'checkbox-{role}'
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
        'icon-size': box - 2 * bw - 2 * pad,
        'row-height': max(box, line),
    }

    rows = contrast_rows()
    fails = [r for r in rows if not r['pass'] and not r['exception']]
    excs = [r for r in rows if not r['pass'] and r['exception']]

    print('=' * 74)
    print('CHECKBOX TOKEN LAYER')
    print('=' * 74)
    for name in sorted(alias):
        print(f'  {name:<26} -> {alias[name]}')
    print('-' * 74)
    print(f'derived glyph: {derived["icon-size"]}px  (box - 2 x border - 2 x padding)')
    print(f'row height: {derived["row-height"]}px')
    # a check, not a gate: box and line height must match - that is what aligns
    # the box with the label's first line without changing the height
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
            'component': 'Checkbox',
            'version': '0.1.0',
            'foundation': FOUND['meta']['version'],
            'figmaNode': '229:509',
            'variants': [],
            'sizes': ['md'],
            'states': ['default', 'hover', 'checked', 'error',
                       'disabled', 'focus', 'indeterminate'],
            'note': (
                'It is the NATIVE <input type="checkbox">, with the box painted on top. '
                'One size only (24px box), the rule for every Tier 2 input. Figma has a '
                'single state axis; the combinations the browser produces (checked + '
                'hover/focus/disabled/error) are covered by the same tokens, plus '
                '`icon-disabled`, which has no variant in Figma. `bg-checked` applies to '
                'checked and indeterminate. No help/error text: the error message belongs '
                'to the form. Two contrast exceptions declared in pending.'
            ),
        },
        'alias': alias,
        'resolved': resolved,
        'derived': derived,
        'contrast': rows,
        'pending': PENDING,
    }
    json.dump(out, open(comp_out('checkbox', 'tokens.json'), 'w'), indent=2, ensure_ascii=False)
    print('\nbuild/components/checkbox/tokens.json written')
    write_css(alias, derived)
    return 0


# ------------------------------------------------------------------- css
def write_css(alias, derived):
    L = []
    w = L.append
    w('/* AL Design System - Checkbox tokens')
    w(' * GENERATED by src/components/checkbox/tokens.py. Do not edit by hand.')
    w(' *')
    w(' * No theme block: each token points to a semantic, and the theme switches')
    w(' * on :root - the same element where these aliases are declared.')
    w(' *')
    w(f' * Glyph: {derived["icon-size"]}px, derived, no token.')
    w(' */')
    w('')
    w(':root {')

    w('')
    w('  /* box background - checked and indeterminate share the same one */')
    for role in ('bg', 'bg-hover', 'bg-checked', 'bg-disabled'):
        w(f'  --al-checkbox-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* box border */')
    for role in ('border', 'border-hover', 'border-focus', 'border-checked',
                 'border-error', 'border-disabled'):
        w(f'  --al-checkbox-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* check and dash - they don\'t inherit the label color */')
    for role in ('icon', 'icon-disabled'):
        w(f'  --al-checkbox-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* label - it lives outside the box, on the canvas */')
    for role in ('label', 'label-error', 'label-disabled'):
        w(f'  --al-checkbox-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* focus ring - points to the composite shadow, not the raw color */')
    for role, ref in RING.items():
        w(f'  --al-checkbox-{role}: {css_ref(ref)};')

    w('')
    w('  /* geometry */')
    for role, ref in GEOM.items():
        w(f'  --al-checkbox-{role}: {css_ref(ref)};')

    w('')
    w('  /* typography - one style becomes four vars */')
    for role, ref in TYPE.items():
        style = resolve_foundation(ref)
        key = size_key(style[1])
        prefix = f'--al-checkbox-{role}'.replace('-font', '')
        w(f'  {prefix}-font-size: var(--al-font-size-{key});')
        w(f'  {prefix}-line-height: var(--al-line-height-{key});')
        w(f'  {prefix}-font-weight: {style[3]};')
        w(f'  {prefix}-tracking: {style[4]};')

    w('}')
    w('')

    # Lock: a forgotten group list becomes a broken build, not a missing variable.
    text = '\n'.join(L)
    missing = [r for r in COLOR if f'--al-checkbox-{r}:' not in text]
    if missing:
        raise AssertionError(
            'color roles missing from the CSS (some group list in write_css was not '
            f'updated): {missing}')

    save_css('checkbox', text)


if __name__ == '__main__':
    sys.exit(run())
