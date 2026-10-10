"""
Token layer for the Card.

The one rule of this layer: nothing here invents a value. Every token points
to a Foundation token by NAME. The gate at the end of the file rejects
anything that is a loose value - hex, px, number.

Naming:
  code  -> card-border-hover       (hyphen)
  Figma -> border/strong           (folder)
Figma has no variable per component: the node binds the semantic or
Foundation variable the token points to.
Hyphen in code, folder in Figma: they are different layers. Never
collapse one into the other.

SECOND COMPONENT OF TIER 3 (2026-10-07)

  Component set `card`, node 302:870, page `Tier 3` in Figma. 36 variants:
  `Type` (Filled / Border / Elevated) x `Padding` (Spaced 24 / Default 16 /
  Tight 8) x `Interaction` (static or clickable) x `State`. The static one
  only has rest; the clickable one has rest, hover and focus. Left out on
  purpose: selectable card (that is Radio/Checkbox), expandable (that is the
  Accordion), pressed and disabled (a card isn't disabled - it hides or
  explains itself).

THE BACKGROUND IS `bg-surface-raised`, NOT `bg-canvas`

  In light both are white. In dark the Foundation decided that elevation shows
  because the SURFACE LIGHTENS (950 -> 800); the shadow is a secondary clue.
  With `bg-canvas` the dark card took the color of the canvas.

THE BORDER IS `border-default`, NOT `border-subtle`

  Same lesson as the Divider: `border-subtle` and `bg-surface-raised` are the
  same neutral-800 in dark, and the border disappeared (1.00:1). Hover darkens
  it to `border-strong` (precedent: Material); orange is reserved for focus,
  which is `border-brand` + ring - the same pattern as the Input.

THREE PADDINGS, NAMES THAT DON'T CARRY THE VALUE

  Spaced 24, Default 16, Tight 8. If the scale changes, rename.

THE BORDER IS OUTSIDE

  In Figma the stroke is OUTSIDE: it doesn't enter the layout, and the three
  types measure the same without discounting padding. The CSS reproduces this
  by drawing the border OUTSIDE the box (a 1px shadow or outline), not with
  `border` - and that is why there is no `calc(padding - border-width)` here,
  unlike the Button and the Input. The types without a border do NOT get a
  transparent border.

ELEVATED FOCUS ADDS RING AND SHADOW

  In Figma the variant accepts only one effect style and the focused Elevated
  shows only the ring. In CSS the box-shadow stacks `card-ring` +
  `card-elevated-shadow`: the card doesn't "sink" when it receives focus
  (precedent: Material). No new token.

TITLE AND DESCRIPTION ARE GUIDANCE, NOT OBLIGATION

  The card brings an optional title and description with their own tokens, so
  the family doesn't get lost across products (precedent: Material/Spectrum).
  The slot accepts any content in their place.

NO TOKEN, ON PURPOSE

  Width and height: the width belongs to the container (the 320 in Figma is a
  sample) and the height is padding + content. Clickable at rest is identical
  to static - what changes is markup and cursor. The gap of 8 on the card's
  frame in Figma does nothing (it has a single child, the slot); what counts
  is the gap inside the slot.

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
    'bg':           'bg-surface-raised',

    'border':       'border-default',
    'border-hover': 'border-strong',
    'border-focus': 'border-brand',

    'title':        'text-primary',
    'description':  'text-secondary',
}

# The token points to the COMPOSITE SHADOW, not the raw color - same rule as
# `button-*-ring`. The color is only extracted for measuring, in RING_INK below.
RING = {
    'ring': 'focusRing.default',
}

RING_INK = {
    'ring': 'shadow-focus-default',
}

# Elevation is height, not state: it stays out of the color layer on purpose.
SHADOW = {
    'elevated-shadow':       'elevation.2',
    'elevated-shadow-hover': 'elevation.4',
    'filled-shadow-hover':   'elevation.2',
}

# ------------------------------------------------------------- geometry
GEOM = {
    'padding-spaced':  'space.24',
    'padding-default': 'space.16',
    'padding-tight':   'space.8',
    'gap':             'space.8',     # between blocks inside the slot
    'text-gap':        'space.4',     # title -> description
    'radius':          'radius.lg',
    'border-width':    'border.width.1',
}

TYPE = {
    'title-font':       'type.styles.heading-xs',
    'description-font': 'type.styles.body-md',
}

PENDING = {
    'border-below-3-1': (
        'The border of the Border type uses `border-default`: 1.57:1 in light and 1.46:1 in dark '
        'against the card, and between 1.47:1 and 2.42:1 against the pages. Below the 3:1 of '
        'WCAG 1.4.11. Decided on 2026-10-07: the card is recognized by its content, not by the '
        'line. The exception covers a SUBTLE line, never an invisible one - that is why it is '
        'not `border-subtle`, which gave 1.00:1 in dark. DO NOT "fix" it by darkening.'
    ),
    'card-not-separated-by-bg': (
        'The card background against the page: 1.00:1 on the canvas and 1.07:1 on the surface '
        'in light; 1.66:1 and 1.36:1 in dark. The separation comes from the border (Border), '
        'the shadow (Elevated) or placing the Filled on `bg-surface`. The exception is backed by '
        'usage rule 2 in guidelines.md: Filled never directly on the canvas.'
    ),
}

# Backgrounds the card is placed on. They are not Card tokens.
PAGES = {
    'canvas':  'bg-canvas',
    'surface': 'bg-surface',
}

# (role, card token, background(s), floor, exception key in PENDING)
# Text measures against the card background. The border measures against the
# card AND the pages and keeps the worst. The ring measures against the pages:
# it is drawn outside the card.
COMBOS = [
    ('title',          'title',        'bg',                          4.5, None),
    ('description',    'description',  'bg',                          4.5, None),
    ('border-rest',    'border',       ('bg', 'canvas', 'surface'),   3.0, 'border-below-3-1'),
    ('border-hover',   'border-hover', ('bg', 'canvas', 'surface'),   3.0, None),
    ('border-focus',   'border-focus', ('bg', 'canvas', 'surface'),   3.0, None),
    ('focus-ring',     'ring',         ('canvas', 'surface'),         3.0, None),
    ('bg-on-canvas',   'bg',           'canvas',                      3.0, 'card-not-separated-by-bg'),
    ('bg-on-surface',  'bg',           'surface',                     3.0, 'card-not-separated-by-bg'),
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
        name = f'card-{role}'
        alias[name] = ref
        if ref.startswith('#'):
            problems.append(f'{name}: loose hex ({ref}) - every color value is born as an alias of a semantic')
            continue
        if ref not in SEM:
            problems.append(f'{name}: points to {ref}, which does not exist in the semantic layer')
            continue
        light, dark = SEM[ref]
        resolved[name] = {'light': light, 'dark': dark}

    for group in (RING, SHADOW):
        for role, ref in group.items():
            name = f'card-{role}'
            alias[name] = ref
            try:
                v = resolve_foundation(ref)
                resolved[name] = {'light': v['light'], 'dark': v['dark']}
            except KeyError:
                problems.append(f'{name}: {ref} does not exist in the Foundation')

    for group in (GEOM, TYPE):
        for role, ref in group.items():
            name = f'card-{role}'
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
    print('CARD TOKEN LAYER')
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
            'component': 'Card',
            'version': '0.1.0',
            'foundation': FOUND['meta']['version'],
            'figmaNode': '302:870',
            'variants': ['filled', 'border', 'elevated'],
            'sizes': ['spaced', 'default', 'tight'],
            'states': ['default', 'hover', 'focus'],
            'note': (
                'Content container, static or clickable. Three types (Filled, Border, '
                'Elevated) and three paddings (24/16/8). Background bg-surface-raised: in dark '
                'the surface lightens. Outside border (it doesn\'t enter the layout) and focus = '
                'border-brand + ring on the Border; on the Elevated, focus adds ring and shadow. '
                'Title and description are optional and replaceable by the slot. Two contrast '
                'exceptions declared in pending.'
            ),
        },
        'alias': alias,
        'resolved': resolved,
        'contrast': rows,
        'pending': PENDING,
    }
    json.dump(out, open(comp_out('card', 'tokens.json'), 'w'), indent=2, ensure_ascii=False)
    print('\nbuild/components/card/tokens.json written')
    write_css(alias)
    return 0


# ---------------------------------------------------------------- css
def write_css(alias):
    L = []
    w = L.append
    w('/* AL Design System - Card tokens')
    w(' * GENERATED by src/components/card/tokens.py. Do not edit by hand.')
    w(' *')
    w(' * There is no theme block here: each token points to a semantic, and the')
    w(' * theme switches on :root - the same element where these aliases are declared.')
    w(' */')
    w('')
    w(':root {')

    w('')
    w('  /* background - the same in all three types */')
    w(f'  --al-card-bg: {css_ref(COLOR["bg"])};')

    w('')
    w('  /* border of the Border type - orange only on focus */')
    for role in ('border', 'border-hover', 'border-focus'):
        w(f'  --al-card-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* title and description - optional, replaceable by the slot */')
    for role in ('title', 'description'):
        w(f'  --al-card-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* focus ring - points to the composite shadow, not the raw color */')
    for role, ref in RING.items():
        w(f'  --al-card-{role}: {css_ref(ref)};')

    w('')
    w('  /* elevation - height, not state */')
    for role, ref in SHADOW.items():
        w(f'  --al-card-{role}: {css_ref(ref)};')

    w('')
    w('  /* geometry */')
    for role, ref in GEOM.items():
        w(f'  --al-card-{role}: {css_ref(ref)};')

    w('')
    w('  /* typography - one style becomes four vars */')
    for role, ref in TYPE.items():
        style = resolve_foundation(ref)
        key = size_key(style[1])
        prefix = f'--al-card-{role}'.replace('-font', '')
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

    save_css('card', text)


if __name__ == '__main__':
    sys.exit(run())
