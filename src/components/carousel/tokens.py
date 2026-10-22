"""
Token layer for the Carousel.

The one rule of this layer: nothing here invents a value. Every token points
to a Foundation token by NAME. The gate at the end of the file rejects
anything that is a loose value - hex, px, number.

Naming:
  code  -> carousel-dot-current   (hyphen)
  Figma -> the node binds the semantic the token points to (no component
           variable: since 10/10 a component only binds the semantic layer).

THREE PIECES IN FIGMA (2026-10-22)

  `carousel` (521:352): Position = Start, Middle, End. `_carousel-dot`
  (521:257): Current True/False. `_carousel-slide` (521:258): the content
  slot, its "Slide" text is a Figma placeholder only.

THE BASIC CAROUSEL OF THE APG

  Previous and next are the Icon Button Secondary sm, below the content and
  disabled at the ends: no loop, no auto-rotation. The dots are decorative
  (aria-hidden, no focus). As many slides as fit, the next one cut at the
  edge to show there is more.

NO TOKEN, ON PURPOSE

  Arrows: the Icon Button tokens. Slide width: set by the layout. Scroll
  motion: the browser's smooth scroll, off under prefers-reduced-motion.
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

# ---------------------------------------------------------------- color
COLOR = {
  'dot':          'border-strong',
  'dot-current':  'bg-brand',
  'slide-bg':     'bg-subtle',
}

# ------------------------------------------------------------- geometry
GEOM = {
  'gap':                'space.16',
  'controls-gap':       'space.16',
  'nav-gap':            'space.8',
  'dot-size':           'space.8',
  'dot-current-width':  'space.24',
  'dot-gap':            'space.8',
  'dot-radius':         'radius.full',
  'slide-radius':       'radius.lg',
}

PENDING = {
  'dot-shape': (
    'Current dot on the other dots = 1.46:1 light, 1.10:1 dark. Shape carries the '
    'state (24px pill vs 8px dot) and the dots are decorative (aria-hidden).'
  ),
  'slide-content': (
    'Slide background on the page = 1.00-1.66:1. The slide is content, not a control, '
    'like the Card border; the content draws its own edge. On surface-raised in dark '
    'the empty slide matches the page (D1=a: accepted, said in the usage rules).'
  ),
}

UNDER = ('bg-canvas', 'bg-surface', 'bg-surface-raised')

# (what, fg role, against, floor, exception key)
COMBOS = (
  [(r, r, u, 3.0, None) for r in ('dot', 'dot-current') for u in UNDER] +
  [('current dot', 'dot-current', COLOR['dot'], 3.0, 'dot-shape')] +
  [('slide-bg', 'slide-bg', u, 3.0, 'slide-content') for u in UNDER]
)

# ------------------------------------------------------------------ gate
def contrast_rows():
    rows = []
    for what, role, under, floor, exc in COMBOS:
        fg = SEM[COLOR[role]]
        for theme, i in (('light', 0), ('dark', 1)):
            ratio = round(cr(fg[i], SEM[under][i]), 2)
            rows.append({
                'theme': theme, 'what': f'{what} on {under}',
                'fg': COLOR[role], 'bg': under,
                'ratio': ratio, 'min': floor,
                'pass': ratio >= floor,
                'exception': exc if ratio < floor else None,
            })
    return rows


def run():
    alias, resolved, problems = {}, {}, []

    for role, ref in COLOR.items():
        name = f'carousel-{role}'
        alias[name] = ref
        if ref.startswith('#'):
            problems.append(f'{name}: loose hex ({ref}) - every color value is born as an alias')
            continue
        if ref not in SEM:
            problems.append(f'{name}: points to {ref}, which does not exist in the Foundation')
            continue
        light, dark = SEM[ref]
        resolved[name] = {'light': light, 'dark': dark}

    for role, ref in GEOM.items():
        name = f'carousel-{role}'
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
    print('CAROUSEL TOKEN LAYER')
    print('=' * 74)
    for name in sorted(alias):
        print(f'  {name:<34} -> {alias[name]}')
    print('-' * 74)
    print(f'contrast: {len(rows)} measurements  |  pass: {len(rows) - len(fails) - len(excs)}  |  '
          f'fail: {len(fails)}  |  exceptions: {len(excs)}')
    for r in excs:
        print(f'  exception {r["exception"]}: {r["what"]} ({r["theme"]}) = {r["ratio"]}:1')
    print('-' * 74)

    if fails:
        print(f'{len(fails)} COMBINATION(S) FAIL THE CONTRAST GATE:')
        for f in fails:
            print(f'    {f["what"]} ({f["theme"]}): {f["ratio"]}:1 < {f["min"]}')
        return 1

    print(f'{len(alias)} tokens, all aliases of the Foundation. 0 loose values.')

    out = {
        'meta': {
            'component': 'Carousel',
            'version': '0.1.0',
            'foundation': FOUND['meta']['version'],
            'figmaNode': '521:352',
            'positions': ['start', 'middle', 'end'],
            'note': (
                'Basic APG carousel: previous and next below the content, disabled at the '
                'ends, decorative dots, as many slides as fit with the next one cut.'
            ),
        },
        'alias': alias,
        'resolved': resolved,
        'contrast': rows,
        'pending': PENDING,
    }
    json.dump(out, open(comp_out('carousel', 'tokens.json'), 'w'), indent=2, ensure_ascii=False)
    print('\nbuild/components/carousel/tokens.json written')
    write_css()
    return 0


# ------------------------------------------------------------------- css
def write_css():
    L = []
    w = L.append
    w('/* AL Design System - Carousel tokens')
    w(' * GENERATED by src/components/carousel/tokens.py. Do not edit by hand.')
    w(' *')
    w(' * Every color is a semantic the theme switches on :root.')
    w(' */')
    w('')
    w(':root {')
    w('  /* color */')
    for role, ref in COLOR.items():
        w(f'  --al-carousel-{role}: {css_ref(ref)};')
    w('')
    w('  /* geometry */')
    for role, ref in GEOM.items():
        w(f'  --al-carousel-{role}: {css_ref(ref)};')
    w('}')
    w('')
    save_css('carousel', '\n'.join(L))


if __name__ == '__main__':
    sys.exit(run())
