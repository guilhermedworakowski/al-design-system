"""
Token layer for the Accordion.

The one rule of this layer: nothing here invents a value. Every token points
to a Foundation token by NAME. The gate at the end of the file rejects
anything that is a loose value - hex, px, number.

Naming:
  code  -> accordion-bg-hover      (hyphen)
  Figma -> bg/hover                (collection `18. Accordion`)
They are different layers. Never collapse one into the other.

FOURTH COMPONENT OF TIER 3 (2026-10-07)

  Component set `Accordion`, node 306:2643, page `Tier 3` in Figma. 8
  variants: `State` (Default / Hover / Pressed / Focus) x `Type` (Closed /
  Opened). One item, one size, no disabled. Left out on purpose: a group
  component (like the Radio, whoever stacks decides the space), sizes, and
  disabled (a panel that doesn't open is hidden content with no way out).
  Native `<details>`/`<summary>` markup, `name=` for the exclusive mode.

THE HEADER IS THE ONLY PART THAT REACTS

  Hover, pressed and ring stay on the header - it is the `<summary>`, the
  only clickable part. The content stays on the rest background in every
  state: painting the content would suggest it is clickable too.

HOVER AND PRESSED ARE `-raised`

  The item lives on `bg-surface-raised` (like the Card). In dark, `bg-hover`
  is the same neutral-800 as the raised surface, and the hover disappeared
  (1.00:1). The Foundation gained `bg-hover-raised` and `bg-active-raised`,
  one step above in dark. The distinct-state gate below locks the regression.

FOCUS = REST + RING

  As in the Tab. Whoever arrives by keyboard doesn't see the hover background
  without the mouse.

1px DIVIDER IN `border-default`

  The same line as the Divider. It stays still in every state: only the
  header background changes.

NO TOKEN, ON PURPOSE

  Chevron and icon color: it is the title's, so it is `currentColor` (rule
  from the Button and the Tag; the Select only has an icon token because
  there the color differs from the label). Height: padding + line height +
  padding = 76. Width: the container's. Space between stacked items: the
  layout's. Chevron rotation: the motion tokens, in accordion.css.

TWO DECLARED CONTRAST EXCEPTIONS

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
    'bg':        'bg-surface-raised',   # item, header at rest and focus, content
    'bg-hover':  'bg-hover-raised',     # header
    'bg-active': 'bg-active-raised',    # header

    'title':     'text-primary',        # chevron and icon inherit (currentColor)

    'divider':   'border-default',
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
    'padding':       'space.24',        # header and content
    'gap':           'space.8',         # icon -> title
    'content-gap':   'space.8',         # between blocks inside the content
    'radius':        'radius.lg',
    'divider-width': 'border.width.1',
    'icon-size':     'iconSize.24',     # left icon and chevron
}

TYPE = {
    'title-font': 'type.styles.heading-xs',
}

PENDING = {
    'decorative-divider': (
        'The line between header and content uses `border-default`: between 1.19:1 and 1.57:1 '
        'in light and between 1.00:1 and 1.50:1 in dark against the header. It only separates - '
        'what says the item is open is the chevron and the content appearing. The 1.00 is the '
        'dark hover (border-default and bg-hover-raised are the same neutral-700); there the '
        'boundary stays visible because the header separates from the content by background '
        '(1.46:1). Same logic as the Divider. DO NOT "fix" it by darkening.'
    ),
    'item-not-separated-by-bg': (
        'The item background against the page: 1.00:1 on the canvas and 1.07:1 on the surface '
        'in light; 1.66:1 and 1.36:1 in dark. Same case as the Filled Card: the exception is '
        'backed by usage rule 14 in guidelines.md - the Accordion goes on `bg-surface`, never '
        'directly on the canvas.'
    ),
}

# Backgrounds the item is placed on. They are not Accordion tokens.
PAGES = {
    'canvas':  'bg-canvas',
    'surface': 'bg-surface',
}

# (role, accordion token, background, floor, exception key in PENDING)
# Title and chevron measure against the header in each state, and so does the
# divider. The ring measures against the page: the ring's inner layer is the
# canvas color, so it never touches the item.
COMBOS = [
    ('title-rest',      'title',   'bg',        4.5, None),
    ('title-hover',     'title',   'bg-hover',  4.5, None),
    ('title-pressed',   'title',   'bg-active', 4.5, None),
    ('chevron-rest',    'title',   'bg',        3.0, None),
    ('chevron-hover',   'title',   'bg-hover',  3.0, None),
    ('chevron-pressed', 'title',   'bg-active', 3.0, None),
    ('divider-rest',    'divider', 'bg',        3.0, 'decorative-divider'),
    ('divider-hover',   'divider', 'bg-hover',  3.0, 'decorative-divider'),
    ('divider-pressed', 'divider', 'bg-active', 3.0, 'decorative-divider'),
    ('item-on-canvas',  'bg',      'canvas',    3.0, 'item-not-separated-by-bg'),
    ('item-on-surface', 'bg',      'surface',   3.0, 'item-not-separated-by-bg'),
    ('ring-on-canvas',  'ring',    'canvas',    3.0, None),
    ('ring-on-surface', 'ring',    'surface',   3.0, None),
]

# Not a WCAG floor: it locks the -raised hover. Hover and pressed must be
# distinguishable from rest in both themes, or the header doesn't react.
DISTINCT = [
    ('hover-vs-rest',    'bg-hover',  'bg'),
    ('pressed-vs-rest',  'bg-active', 'bg'),
    ('pressed-vs-hover', 'bg-active', 'bg-hover'),
]
DISTINCT_MIN = 1.1


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
    floor: text 4.5:1 from 1.4.3, glyph, line, ring and background 3:1 from 1.4.11."""
    rows = []
    for what, fg_role, bg_role, min_ratio, exc in COMBOS:
        fg_ref, bg_ref = ink(fg_role), ink(bg_role)
        for theme, i in (('light', 0), ('dark', 1)):
            ratio = round(cr(SEM[fg_ref][i], SEM[bg_ref][i]), 2)
            rows.append({
                'theme': theme, 'what': what,
                'fg': fg_ref, 'bg': bg_ref,
                'ratio': ratio, 'min': min_ratio,
                'pass': ratio >= min_ratio,
                'exception': exc,
            })
    return rows


def distinct_rows():
    rows = []
    for what, a, b in DISTINCT:
        for theme, i in (('light', 0), ('dark', 1)):
            ratio = round(cr(SEM[ink(a)][i], SEM[ink(b)][i]), 2)
            rows.append({'theme': theme, 'what': what, 'ratio': ratio,
                         'pass': ratio >= DISTINCT_MIN})
    return rows


def run():
    alias, resolved, problems = {}, {}, []

    for role, ref in COLOR.items():
        name = f'accordion-{role}'
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
        name = f'accordion-{role}'
        alias[name] = ref
        try:
            v = resolve_foundation(ref)
            resolved[name] = {'light': v['light'], 'dark': v['dark']}
        except KeyError:
            problems.append(f'{name}: {ref} does not exist in the Foundation')

    for group in (GEOM, TYPE):
        for role, ref in group.items():
            name = f'accordion-{role}'
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
    dist = distinct_rows()
    dist_fails = [r for r in dist if not r['pass']]

    print('=' * 74)
    print('ACCORDION TOKEN LAYER')
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
    print(f'distinct state (floor {DISTINCT_MIN}:1, locks the -raised hover): '
          + '  '.join(f'{r["what"]} {r["theme"]} {r["ratio"]}' for r in dist))
    print('-' * 74)

    if fails:
        print(f'{len(fails)} COMBINATION(S) FAIL THE CONTRAST GATE:')
        for f in fails:
            print(f'    {f["what"]} ({f["theme"]}): {f["ratio"]}:1 < {f["min"]}')
        return 1
    if dist_fails:
        print(f'{len(dist_fails)} STATE(S) NOT DISTINGUISHABLE FROM THE NEIGHBOR:')
        for f in dist_fails:
            print(f'    {f["what"]} ({f["theme"]}): {f["ratio"]}:1 < {DISTINCT_MIN}')
        return 1

    print(f'{len(alias)} tokens, all aliases of the Foundation. 0 loose values.')

    out = {
        'meta': {
            'component': 'Accordion',
            'version': '0.1.0',
            'foundation': FOUND['meta']['version'],
            'figmaNode': '306:2643',
            'figmaCollection': '18. Accordion',
            'variants': ['closed', 'opened'],
            'sizes': ['default'],
            'states': ['default', 'hover', 'pressed', 'focus'],
            'note': (
                'Expandable content item, native (<details>/<summary>). One size, no disabled, '
                'no group component. Background bg-surface-raised; only the header reacts, with '
                '-raised hover and pressed. Focus = rest + ring. 1px border-default divider. Two '
                'contrast exceptions declared in pending.'
            ),
        },
        'alias': alias,
        'resolved': resolved,
        'contrast': rows,
        'distinct': dist,
        'pending': PENDING,
    }
    json.dump(out, open(comp_out('accordion', 'tokens.json'), 'w'), indent=2, ensure_ascii=False)
    print('\nbuild/components/accordion/tokens.json written')
    write_css(alias)
    return 0


# ---------------------------------------------------------------- css
def write_css(alias):
    L = []
    w = L.append
    w('/* AL Design System - Accordion tokens')
    w(' * GENERATED by src/components/accordion/tokens.py. Do not edit by hand.')
    w(' *')
    w(' * There is no theme block here: each token points to a semantic, and the')
    w(' * theme switches on :root - the same element where these aliases are declared.')
    w(' */')
    w('')
    w(':root {')

    w('')
    w('  /* background - only the header reacts; the content stays at rest */')
    for role in ('bg', 'bg-hover', 'bg-active'):
        w(f'  --al-accordion-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* title - chevron and icon inherit through currentColor */')
    w(f'  --al-accordion-title: {css_ref(COLOR["title"])};')

    w('')
    w('  /* divider between header and content - still in every state */')
    w(f'  --al-accordion-divider: {css_ref(COLOR["divider"])};')

    w('')
    w('  /* focus ring - points to the composite shadow, not the raw color */')
    for role, ref in RING.items():
        w(f'  --al-accordion-{role}: {css_ref(ref)};')

    w('')
    w('  /* geometry */')
    for role, ref in GEOM.items():
        w(f'  --al-accordion-{role}: {css_ref(ref)};')

    w('')
    w('  /* typography - one style becomes four vars */')
    for role, ref in TYPE.items():
        style = resolve_foundation(ref)
        key = size_key(style[1])
        prefix = f'--al-accordion-{role}'.replace('-font', '')
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

    save_css('accordion', text)


if __name__ == '__main__':
    sys.exit(run())
