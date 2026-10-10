"""
Token layer for the Divider.

The one rule of this layer: nothing here invents a value. Every token points
to a Foundation token by NAME. The gate at the end of the file rejects
anything that is a loose value - hex, px, number.

Naming:
  code  -> divider-color             (hyphen)
  Figma -> border/default            (folder)
Figma has no variable per component: the node binds the semantic or
Foundation variable the token points to.
Hyphen in code, folder in Figma: they are different layers. Never
collapse one into the other.

FIRST COMPONENT OF TIER 3 (2026-10-07)

  Component set `divider`, node 304:1076, page `Tier 3` in Figma. One axis,
  `Orientation` (Horizontal / Vertical). One thickness only (precedent:
  Polaris), no inset, no text in the middle, no brand or status color.

THE COLOR IS `border-default`, NOT `border-subtle`

  It was born `border-subtle`. The contrast gate measured the system's third
  surface and found the line INVISIBLE in dark on card and modal:
  `border-subtle` and `bg-surface-raised` are the same neutral-800 there.
  Changing only the Divider solves it without touching the Foundation or the
  other components that use `border-subtle`.

THE LINE IS THE COMPONENT - HENCE `color` AND `thickness`

  In the other components the border outlines a box and the token is called
  `border` / `border-width`. Here the line is the component itself; `color`
  and `thickness` are the names Spectrum and Material use, and they read the
  same in both orientations. In Figma the line is a FILLED 1px rectangle, not
  a stroke - the thickness is the height (or the width, when vertical).

LENGTH AND MARGIN HAVE NO TOKEN

  Horizontal takes the container's width, vertical follows its height. The
  space around it is a layout decision. The 158/160 in Figma are sample
  measurements.

ANNOUNCED OR DECORATIVE IS MARKUP, NOT A TOKEN

  Decided on 2026-10-07: an announced `<hr>` ("separator") is the default;
  decorative (`aria-hidden`) is the user's choice. Visually identical.

ONE DECLARED CONTRAST EXCEPTION

  See PENDING.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'tools'))
from paths import FOUNDATION_SRC, TOKENS_JSON, comp_out  # noqa: E402
sys.path.insert(0, FOUNDATION_SRC)

from palette import SEM                     # noqa: E402
from tokenlib import resolve_foundation, css_ref, save_css  # noqa: E402
from color import cr                      # noqa: E402

FOUND = json.load(open(TOKENS_JSON))   # noqa: E402

# ------------------------------------------------------------- color
COLOR = {
    'color': 'border-default',   # was border-subtle - see the header
}

# ------------------------------------------------------------- geometry
GEOM = {
    'thickness': 'border.width.1',
}

PENDING = {
    'line-below-3-1': (
        'The line uses `border-default`: 1.57:1 on the canvas, 1.47:1 on the surface and 1.57:1 '
        'on a card in light; 2.42:1 / 1.98:1 / 1.46:1 in dark - below the 3:1 of WCAG 1.4.11. The '
        'criterion only applies to a graphical object REQUIRED to understand the content, and the '
        'divider can never be the only clue of the grouping: space or a heading does that job, '
        'and the screen reader hears "separator" on the <hr>. The exception covers a SUBTLE line, '
        'never an invisible one: the original border-subtle disappeared on a card in dark and was '
        'replaced (2026-10-07). The exception is backed by usage rule 8 in guidelines.md. DO NOT '
        '"fix" it by darkening.'
    ),
}

# Backgrounds the divider is placed on. They are not Divider tokens.
BACKGROUNDS = {
    'canvas':  'bg-canvas',
    'surface': 'bg-surface',
    'raised':  'bg-surface-raised',   # card and modal
}

# (role, divider token, background, floor, exception key in PENDING)
COMBOS = [
    ('line-on-canvas',  'color', 'canvas',  3.0, 'line-below-3-1'),
    ('line-on-surface', 'color', 'surface', 3.0, 'line-below-3-1'),
    ('line-on-card',    'color', 'raised',  3.0, 'line-below-3-1'),
]


# ------------------------------------------------------------------ gate
def contrast_rows():
    """Measures the line against each background in both themes, against the 3:1 floor from 1.4.11."""
    rows = []
    for what, fg_role, bg_role, min_ratio, exc in COMBOS:
        fg_ref, bg_ref = COLOR[fg_role], BACKGROUNDS[bg_role]
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


def run():
    alias, resolved, problems = {}, {}, []

    for role, ref in COLOR.items():
        name = f'divider-{role}'
        alias[name] = ref
        if ref.startswith('#'):
            problems.append(f'{name}: loose hex ({ref}) - every color value is born as an alias of a semantic')
            continue
        if ref not in SEM:
            problems.append(f'{name}: points to {ref}, which does not exist in the semantic layer')
            continue
        light, dark = SEM[ref]
        resolved[name] = {'light': light, 'dark': dark}

    for role, ref in GEOM.items():
        name = f'divider-{role}'
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
    print('DIVIDER TOKEN LAYER')
    print('=' * 74)
    for name in sorted(alias):
        print(f'  {name:<30} -> {alias[name]}')
    print('-' * 74)
    print(f'contrast: {len(rows)} measurements  |  pass: {len(rows) - len(fails) - len(excs)}  |  '
          f'declared exceptions: {len(excs)}  |  fail: {len(fails)}')
    for r in rows:
        print(f'  {r["what"]:<22} {r["theme"]:<6} {r["ratio"]}:1  (floor {r["min"]})')
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
            'component': 'Divider',
            'version': '0.1.0',
            'foundation': FOUND['meta']['version'],
            'figmaNode': '304:1076',
            'variants': ['horizontal', 'vertical'],
            'sizes': [],
            'states': [],
            'note': (
                '1px line in border-default, horizontal or vertical. No state, no size, no '
                'inset: length and margin belong to the layout. An announced <hr> is the '
                'default; decorative is markup, not a token. One contrast exception declared '
                'in pending.'
            ),
        },
        'alias': alias,
        'resolved': resolved,
        'contrast': rows,
        'pending': PENDING,
    }
    json.dump(out, open(comp_out('divider', 'tokens.json'), 'w'), indent=2, ensure_ascii=False)
    print('\nbuild/components/divider/tokens.json written')
    write_css(alias)
    return 0


# ---------------------------------------------------------------- css
def write_css(alias):
    L = []
    w = L.append
    w('/* AL Design System - Divider tokens')
    w(' * GENERATED by src/components/divider/tokens.py. Do not edit by hand.')
    w(' *')
    w(' * There is no theme block here: each token points to a semantic, and the')
    w(' * theme switches on :root - the same element where these aliases are declared.')
    w(' */')
    w('')
    w(':root {')
    for role, ref in COLOR.items():
        w(f'  --al-divider-{role}: {css_ref(ref)};')
    for role, ref in GEOM.items():
        w(f'  --al-divider-{role}: {css_ref(ref)};')
    w('}')
    w('')

    text = '\n'.join(L)
    missing = [n for n in alias if f'--al-{n}:' not in text]
    if missing:
        raise AssertionError(f'tokens missing from the CSS: {missing}')

    save_css('divider', text)


if __name__ == '__main__':
    sys.exit(run())
