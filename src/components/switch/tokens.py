"""
Token layer for the Switch.

The one rule of this layer: nothing here invents a value. Every token points
to a Foundation token by NAME. The gate at the end of the file rejects
anything that is a loose value - hex, px, number.

Naming:
  code  -> switch-thumb-checked      (hyphen)
  Figma -> thumb/checked             (folder, collection `11. Switch`)
They are different layers. Never collapse one into the other.

IT IS THE NATIVE `<input type="checkbox" role="switch">`

  The same choice as the Select, the Checkbox and the Radio: the control
  belongs to the browser, the component paints the track on top with
  `appearance: none`. `role="switch"` changes the announcement from "checkbox,
  checked" to "switch, on".

ONE SIZE ONLY - THE TIER 2 RULE

  A 24px tall track, the same as the Radio circle and the label's line height
  - that is what aligns the control with the first line of text.

NO ERROR - DECIDED IN THE AUDIT (2026-09-25)

  Spectrum precedent: the switch takes effect immediately, it doesn't wait for
  "Submit", so there is no validation and no error. A choice that needs to be
  validated is a Checkbox. That is why there is no `label-error` and no
  `border-error`.

HOVER ONLY TOUCHES THE BORDER, FOCUS ONLY THE RING

  The track doesn't change color on hover (by design): the only signal is
  `border-hover`. On focus the border stays at rest and the ring signals it -
  that is why there is no `track-hover` and no `border-focus`.

FIGMA HAS ONE AXIS, THE BROWSER HAS TWO

  The component set (node 259:262) has five variants on one `State` axis:
  Default, Hover, Active (= on), Disabled, Focus. The combinations the input
  produces are covered by the same tokens, with the Checkbox's and the Radio's
  solution:

    on + hover      -> `border-checked` border (the orange doesn't change)
    on + focus      -> ring outside the orange track
    on + disabled   -> `track-disabled` track, thumb on the right in
                       `thumb-checked-disabled` (approved 2026-09-25)

  `switch-thumb-checked-disabled` is the only token with no variant in Figma -
  the mirror of `radio-dot-disabled` and `checkbox-icon-disabled`.

THE THUMB AND THE WIDTH HAVE NO TOKEN

  thumb  = height 24 - 2 x border 1 - 2 x padding 4 = 14
  width  = 2 x thumb + 2 x padding + 2 x border    = 38
  travel = thumb                                    = 14
  They are derived. Tokenizing them would store the same decision in two
  places, and neither 14 nor 38 exist on the scale.

THREE DECLARED CONTRAST EXCEPTIONS

  See PENDING. The off thumb one is new; the other two are the same as the
  Checkbox's and the Radio's.
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
    'track':                  'bg-surface',
    'track-checked':          'bg-brand',       # what says "on" - 3:1 floor
    'track-disabled':         'bg-disabled',    # on or off

    'border':                 'border-default',
    'border-hover':           'border-strong',
    'border-checked':         'border-brand',
    'border-disabled':        'border-default',

    'thumb':                  'bg-thumb',
    'thumb-checked':          'text-on-brand',
    'thumb-disabled':         'bg-thumb-disabled',
    'thumb-checked-disabled': 'text-disabled',  # no variant in Figma

    'label':                  'text-primary',
    'label-disabled':         'text-disabled',
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
    'track-height': 'iconSize.24',
    'padding':      'space.4',        # border -> thumb
    'gap':          'space.8',        # track -> label
    'radius':       'radius.full',
    'border-width': 'border.width.1',
}

TYPE = {
    'label-font': 'type.styles.body-md',
}

PENDING = {
    'thumb-below-3-1': (
        'The off thumb uses `bg-thumb` (neutral-400 / neutral-600): 1.96:1 in light and '
        '2.98:1 in dark against the track, below the 3:1 of WCAG 1.4.11. A conscious '
        'decision made in the audit (2026-09-25): neutral-400 is the ceiling, darkening it '
        'to border-strong was turned down. What backs the exception is the orange track of '
        'the on state, which passes (3.12:1 / 4.36:1), and the visible label rule. DO NOT '
        '"fix" it without revisiting that decision.'
    ),
    'border-below-3-1': (
        'The track border at rest uses `border-default`: 1.47:1 in light and 1.98:1 in '
        'dark, below the 3:1 of WCAG 1.4.11. The same decision as the Checkbox and the '
        'Radio: follow the pattern of the DS inputs. Hover (border-strong) and on '
        '(border-brand) pass.'
    ),
    'disabled-below-aa': (
        'Label, border and thumb in disabled fall below the floor. WCAG 1.4.3 / 1.4.11 '
        'exempt inactive components - the same permanent exception as the Button, the Tag, '
        'the Select, the Checkbox and the Radio. Raising that contrast makes disabled look '
        'clickable.'
    ),
}

CANVAS = 'bg-canvas'   # not a Switch token: it is the canvas the Switch is placed on

# (role, switch token, background(s), floor, exception key in PENDING)
# The border and the on track have two neighboring surfaces - the canvas
# outside and the off track (the state being left) - and the WORSE of the two
# counts. The thumb measures against the track it is on.
COMBOS = [
    ('label',               'label',                  'canvas',                     4.5, None),
    ('label-disabled',      'label-disabled',         'canvas',                     4.5, 'disabled-below-aa'),
    ('track-on',            'track-checked',          ('canvas', 'track'),          3.0, None),
    ('border-rest',         'border',                 ('canvas', 'track'),          3.0, 'border-below-3-1'),
    ('border-hover',        'border-hover',           ('canvas', 'track'),          3.0, None),
    ('border-disabled',     'border-disabled',        ('canvas', 'track-disabled'), 3.0, 'disabled-below-aa'),
    ('thumb-off',           'thumb',                  'track',                      3.0, 'thumb-below-3-1'),
    ('thumb-on',            'thumb-checked',          'track-checked',              3.0, None),
    ('thumb-disabled',      'thumb-disabled',         'track-disabled',             3.0, 'disabled-below-aa'),
    ('thumb-on-disabled',   'thumb-checked-disabled', 'track-disabled',             3.0, 'disabled-below-aa'),
    ('focus-ring',          'ring',                   'canvas',                     3.0, None),
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
    floor: text 4.5:1 from 1.4.3, border, track and thumb 3:1 from 1.4.11."""
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
        name = f'switch-{role}'
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
        name = f'switch-{role}'
        alias[name] = ref
        try:
            v = resolve_foundation(ref)
            resolved[name] = {'light': v['light'], 'dark': v['dark']}
        except KeyError:
            problems.append(f'{name}: {ref} does not exist in the Foundation')

    for group in (GEOM, TYPE):
        for role, ref in group.items():
            name = f'switch-{role}'
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
    h = resolve_foundation(GEOM['track-height'])
    pad = resolve_foundation(GEOM['padding'])
    bw = resolve_foundation(GEOM['border-width'])
    line = resolve_foundation(TYPE['label-font'])[2]
    thumb = h - 2 * bw - 2 * pad
    derived = {
        'thumb-size': thumb,
        'track-width': 2 * thumb + 2 * pad + 2 * bw,
        'thumb-travel': thumb,
        'row-height': max(h, line),
    }

    rows = contrast_rows()
    fails = [r for r in rows if not r['pass'] and not r['exception']]
    excs = [r for r in rows if not r['pass'] and r['exception']]

    print('=' * 74)
    print('SWITCH TOKEN LAYER')
    print('=' * 74)
    for name in sorted(alias):
        print(f'  {name:<30} -> {alias[name]}')
    print('-' * 74)
    print(f'derived thumb : {derived["thumb-size"]}px  (height - 2 x border - 2 x padding)')
    print(f'derived track : {derived["track-width"]}x{h}px  (travel {derived["thumb-travel"]}px)')
    print(f'row height    : {derived["row-height"]}px')
    # a check, not a gate: track and line height must match - that is what
    # aligns the track with the label's first line without changing the height
    if h != line:
        print(f'  WARNING: track-height {h} != label line height {line}')
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
            'component': 'Switch',
            'version': '0.1.0',
            'foundation': FOUND['meta']['version'],
            'figmaNode': '259:262',
            'figmaCollection': '11. Switch',
            'variants': [],
            'sizes': ['md'],
            'states': ['default', 'hover', 'checked', 'disabled', 'focus'],
            'note': (
                'It is the NATIVE <input type="checkbox" role="switch">, with the track '
                'painted on top. One size only (38x24 track), the rule for every Tier 2 '
                'input. No error state: the switch takes effect immediately. Figma has a '
                'single state axis; the combinations the browser produces (on + focus/'
                'hover/disabled) are covered by the same tokens, plus '
                '`thumb-checked-disabled`, which has no variant in Figma. Three contrast '
                'exceptions declared in pending.'
            ),
        },
        'alias': alias,
        'resolved': resolved,
        'derived': derived,
        'contrast': rows,
        'pending': PENDING,
    }
    json.dump(out, open(comp_out('switch', 'tokens.json'), 'w'), indent=2, ensure_ascii=False)
    print('\nbuild/components/switch/tokens.json written')
    write_css(alias, derived)
    return 0


# ------------------------------------------------------------------- css
def write_css(alias, derived):
    L = []
    w = L.append
    w('/* AL Design System - Switch tokens')
    w(' * GENERATED by src/components/switch/tokens.py. Do not edit by hand.')
    w(' *')
    w(' * No theme block: each token points to a semantic, and the theme switches')
    w(' * on :root - the same element where these aliases are declared.')
    w(' *')
    w(f' * Thumb: {derived["thumb-size"]}px, track: {derived["track-width"]}px wide,')
    w(' * travel: the thumb itself. Derived, no token.')
    w(' */')
    w('')
    w(':root {')

    w('')
    w('  /* track - the orange of the on state is what says the state */')
    for role in ('track', 'track-checked', 'track-disabled'):
        w(f'  --al-switch-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* track border - hover only touches this */')
    for role in ('border', 'border-hover', 'border-checked', 'border-disabled'):
        w(f'  --al-switch-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* thumb */')
    for role in ('thumb', 'thumb-checked', 'thumb-disabled', 'thumb-checked-disabled'):
        w(f'  --al-switch-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* label - it lives outside the track, on the canvas */')
    for role in ('label', 'label-disabled'):
        w(f'  --al-switch-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* focus ring - points to the composite shadow, not the raw color */')
    for role, ref in RING.items():
        w(f'  --al-switch-{role}: {css_ref(ref)};')

    w('')
    w('  /* geometry */')
    for role, ref in GEOM.items():
        w(f'  --al-switch-{role}: {css_ref(ref)};')

    w('')
    w('  /* typography - one style becomes four vars */')
    for role, ref in TYPE.items():
        style = resolve_foundation(ref)
        key = size_key(style[1])
        prefix = f'--al-switch-{role}'.replace('-font', '')
        w(f'  {prefix}-font-size: var(--al-font-size-{key});')
        w(f'  {prefix}-line-height: var(--al-line-height-{key});')
        w(f'  {prefix}-font-weight: {style[3]};')
        w(f'  {prefix}-tracking: {style[4]};')

    w('}')
    w('')

    # Lock: a forgotten group list becomes a broken build, not a missing variable.
    text = '\n'.join(L)
    missing = [r for r in COLOR if f'--al-switch-{r}:' not in text]
    if missing:
        raise AssertionError(
            'color roles missing from the CSS (some group list in write_css was not '
            f'updated): {missing}')

    save_css('switch', text)


if __name__ == '__main__':
    sys.exit(run())
