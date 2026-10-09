"""
Token layer for the Tab.

The one rule of this layer: nothing here invents a value. Every token points
to a Foundation token by NAME. The gate at the end of the file rejects
anything that is a loose value - hex, px, number.

Naming:
  code  -> tab-line-indicator-selected   (hyphen)
  Figma -> line/indicator/selected       (collection `17. Tab`)
They are different layers. Never collapse one into the other.

THIRD COMPONENT OF TIER 3 (2026-10-07)

  Component set `tab`, node 306:2532, page `Tier 3` in Figma. 16 variants:
  `Type` (Line / Square) x `State` (Default / Hover / Pressed / Focus) x
  `Selected`. One size. Left out on purpose: disabled (an unavailable tab
  leaves the screen), icon, counter, scrolling, vertical, close.

  The main use is switching content on the same screen (tablist/tab/tabpanel),
  but the Tab also builds sidebars and navbars with links. The look is the
  same; the markup changes - that belongs to the CSS, not to this layer.

LINE MARKS THE SELECTION WITH THE LINE, NOT THE TEXT

  Selected, the label is `text-primary` like the hover; what says "you are
  here" is the orange line (precedent: Primer and secondary Material). This
  also solved the dark pressed state: `text-brand` on `bg-active` gave 3.34:1.

THE LINE BELONGS TO THE TAB, NOT TO THE GROUP

  Each tab draws its own line (gray or orange). Tabs sit flush, with no gap,
  and the space between labels comes from each tab's padding.

THE SELECTED SQUARE IS TONAL, AND DARKENS INTO THE BRAND ON INTERACTION

  Rest and focus: `bg-brand-subtle` + `text-brand`. Hover: `bg-brand-hover`
  and pressed: `bg-brand-active`, both with `text-on-brand` - the same brand
  semantics as the Button.

FOCUS IS REST PLUS THE RING

  No hover background. In Figma the focus variants without a background use
  `bg/canvas` only so Figma can project the ring (a fill at opacity 0 doesn't
  project - tested); in CSS the background stays transparent.

NO TOKEN, ON PURPOSE

  Height: Square 32 = 4 + 24 + 4; Line 42 = 32 + 8 + 2. Width: the label.
  Resting background: transparent, nothing to tokenize. Gap between tabs: zero.

FOUR DECLARED CONTRAST EXCEPTIONS

  See PENDING.
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

# ------------------------------------------------------------- color
COLOR = {
    # both types, tab not selected
    'label':        'text-secondary',
    'label-hover':  'text-primary',
    'label-active': 'text-primary',
    'bg-hover':     'bg-hover',
    'bg-active':    'bg-active',

    # Line
    'line-label-selected':     'text-primary',
    'line-indicator':          'border-subtle',
    'line-indicator-selected': 'border-brand',

    # selected Square
    'square-bg-selected':           'bg-brand-subtle',
    'square-label-selected':        'text-brand',
    'square-bg-selected-hover':     'bg-brand-hover',
    'square-label-selected-hover':  'text-on-brand',
    'square-bg-selected-active':    'bg-brand-active',
    'square-label-selected-active': 'text-on-brand',
}

# The token points to the COMPOSITE SHADOW, not the raw color - same rule as
# `button-*-ring`. The color is only extracted for measuring, in RING_INK below.
RING = {
    'ring': 'focusRing.default',
}

RING_INK = {
    'ring': 'shadow-focus-default',
}

# ------------------------------------------------------------- geometry
GEOM = {
    'padding-x':            'space.12',
    'padding-y':            'space.4',
    'radius':               'radius.lg',
    'line-gap':             'space.8',          # label box -> line
    'line-indicator-width': 'border.width.2',
}

TYPE = {
    'label-font': 'type.styles.body-md',   # 'font' produced --al-tab-line-height, read as the Line type
}

PENDING = {
    'decorative-track': (
        'The gray line of the Line (`border-subtle`) gives 1.32:1 in light and 1.66:1 in dark '
        'against the canvas, and less on the surface. It carries no state: the selection is the '
        'orange line (`border-brand`), which passes 3:1 on every background. Same reasoning as '
        'the Divider. DO NOT "fix" it by darkening.'
    ),
    'tonal-selection': (
        'The background of the selected Square (`bg-brand-subtle`) barely separates from the '
        'page: 1.16:1 / 1.08:1 in light and 1.01:1 / 1.23:1 in dark (canvas / surface). In dark '
        'mode the orange label and the gray of the other tabs have almost the same luminance '
        '(1.05:1) - the selection is marked by hue. Accepted knowing this (2026-10-07). '
        'Backed by usage rule 25 in guidelines.md.'
    ),
    'pressed-on-dark-surface': (
        'The background of the selected Square while PRESSED (`bg-brand-active`) against '
        '`bg-surface` in dark = 2.74:1. Accepted with the tonal selection and confirmed again in '
        'QA (2026-10-07). The state only lasts while the click is held, the selection shows '
        'before and after, and the label inside passes (5.30:1). On the dark canvas it passes '
        '(3.35:1). DO NOT darken the semantic.'
    ),
    'brand-on-dark-hover': (
        'White on `bg-brand-hover` in dark = 3.85:1. It is the brand exception the Foundation '
        'already declares (dark text-on-brand / bg-brand-hover), inherited from the Button, with '
        'a hard floor of 3:1. In light it passes (5.30:1).'
    ),
}

# Backgrounds the tab is placed on. They are not Tab tokens.
PAGES = {
    'canvas':  'bg-canvas',
    'surface': 'bg-surface',
}

# (role, tab token, background(s), floor, exception key in PENDING)
# A label with no background of its own measures against the pages. Line,
# selected background and ring measure against the pages and keep the worst.
COMBOS = [
    ('label-rest',                   'label',                        ('canvas', 'surface'), 4.5, None),
    ('label-hover',                  'label-hover',                  'bg-hover',            4.5, None),
    ('label-pressed',                'label-active',                 'bg-active',           4.5, None),
    ('line-label-selected',          'line-label-selected',          ('canvas', 'surface'), 4.5, None),
    ('line-indicator-selected',      'line-indicator-selected',      ('canvas', 'surface'), 3.0, None),
    ('line-track',                   'line-indicator',               ('canvas', 'surface'), 3.0, 'decorative-track'),
    ('square-label-selected',        'square-label-selected',        'square-bg-selected',  4.5, None),
    ('square-label-sel-hover',       'square-label-selected-hover',  'square-bg-selected-hover', 4.5, 'brand-on-dark-hover'),
    ('square-label-sel-pressed',     'square-label-selected-active', 'square-bg-selected-active', 4.5, None),
    ('square-bg-selected',           'square-bg-selected',           ('canvas', 'surface'), 3.0, 'tonal-selection'),
    ('square-bg-sel-pressed',        'square-bg-selected-active',    ('canvas', 'surface'), 3.0, 'pressed-on-dark-surface'),
    ('focus-ring',                   'ring',                         ('canvas', 'surface'), 3.0, None),
]


# ------------------------------------------------------------------ gate
def ink(role):
    """The color semantic behind a role - following the ring down to the color."""
    if role in PAGES:
        return PAGES[role]
    if role in RING_INK:
        return RING_INK[role]
    return COLOR[role]


def contrast_rows():
    """Measures each rendered combination in both themes, each against its own
    floor: text 4.5:1 from 1.4.3, border, ring and background 3:1 from 1.4.11."""
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
        name = f'tab-{role}'
        alias[name] = ref
        if ref.startswith('#'):
            problems.append(f'{name}: loose hex ({ref}) - every color value is born as an alias of a semantic')
            continue
        if ref not in SEM:
            problems.append(f'{name}: points to {ref}, which does not exist in the semantic layer')
            continue
        light, dark = SEM[ref]
        resolved[name] = {'light': light, 'dark': dark}

    for group in (RING,):
        for role, ref in group.items():
            name = f'tab-{role}'
            alias[name] = ref
            try:
                v = resolve_foundation(ref)
                resolved[name] = {'light': v['light'], 'dark': v['dark']}
            except KeyError:
                problems.append(f'{name}: {ref} does not exist in the Foundation')

    for group in (GEOM, TYPE):
        for role, ref in group.items():
            name = f'tab-{role}'
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

    rows = contrast_rows()
    fails = [r for r in rows if not r['pass'] and not r['exception']]
    excs = [r for r in rows if not r['pass'] and r['exception']]

    print('=' * 74)
    print('TAB TOKEN LAYER')
    print('=' * 74)
    for name in sorted(alias):
        print(f'  {name:<30} -> {alias[name]}')
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
            'component': 'Tab',
            'version': '0.1.0',
            'foundation': FOUND['meta']['version'],
            'figmaNode': '306:2532',
            'figmaCollection': '17. Tab',
            'variants': ['line', 'square'],
            'sizes': [],
            'states': ['default', 'hover', 'pressed', 'focus'],
            'selected': [False, True],
            'note': (
                'Tab for switching content on the same screen (and, with links, building a '
                'sidebar/navbar). Line marks the selection with the orange line, label '
                'text-primary. The selected Square is tonal at rest and darkens into the brand on '
                'hover/pressed. Focus = rest + ring. One size, no disabled. Four contrast '
                'exceptions declared in pending.'
            ),
        },
        'alias': alias,
        'resolved': resolved,
        'contrast': rows,
        'pending': PENDING,
    }
    json.dump(out, open(comp_out('tab', 'tokens.json'), 'w'), indent=2, ensure_ascii=False)
    print('\nbuild/components/tab/tokens.json written')
    write_css(alias)
    return 0


# ---------------------------------------------------------------- css
def write_css(alias):
    L = []
    w = L.append
    w('/* AL Design System - Tab tokens')
    w(' * GENERATED by src/components/tab/tokens.py. Do not edit by hand.')
    w(' *')
    w(' * There is no theme block here: each token points to a semantic, and the')
    w(' * theme switches on :root - the same element where these aliases are declared.')
    w(' */')
    w('')
    w(':root {')

    w('')
    w('  /* both types, tab not selected - hover and pressed darken the label */')
    for role in ('label', 'label-hover', 'label-active', 'bg-hover', 'bg-active'):
        w(f'  --al-tab-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* Line - each tab owns its line; the orange one marks the selection */')
    for role in ('line-label-selected', 'line-indicator', 'line-indicator-selected'):
        w(f'  --al-tab-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* selected Square - tonal at rest, brand on hover and pressed */')
    for role in ('square-bg-selected', 'square-label-selected',
                 'square-bg-selected-hover', 'square-label-selected-hover',
                 'square-bg-selected-active', 'square-label-selected-active'):
        w(f'  --al-tab-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* focus ring - points to the composite shadow, not the raw color */')
    for role, ref in RING.items():
        w(f'  --al-tab-{role}: {css_ref(ref)};')

    w('')
    w('  /* geometry */')
    for role, ref in GEOM.items():
        w(f'  --al-tab-{role}: {css_ref(ref)};')

    w('')
    w('  /* typography - one style becomes four vars */')
    for role, ref in TYPE.items():
        style = resolve_foundation(ref)
        key = size_key(style[1])
        prefix = f'--al-tab-{role}'.replace('-font', '')
        w(f'  {prefix}-font-size: var(--al-font-size-{key});')
        w(f'  {prefix}-line-height: var(--al-line-height-{key});')
        w(f'  {prefix}-font-weight: {style[3]};')
        w(f'  {prefix}-tracking: {style[4]};')

    w('}')
    w('')

    # Lock inherited from the Select: a forgotten group list breaks the build
    # instead of leaving a variable silently missing.
    text = '\n'.join(L)
    missing = [n for n in alias
               if not n.endswith('-font') and f'--al-{n}:' not in text]
    if missing:
        raise AssertionError(
            'tokens missing from the CSS (some group list in write_css was not '
            f'updated): {missing}')

    save_css('tab', text)


if __name__ == '__main__':
    sys.exit(run())
