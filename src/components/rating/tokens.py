"""
Token layer for the Rating.

The one rule of this layer: nothing here invents a value. Every token points
to a Foundation token by NAME. The gate at the end of the file rejects
anything that is a loose value - hex, px, number.

Naming:
  code  -> rating-star-on      (hyphen)
  Figma -> the node binds the semantic the token points to (no component
           variable: since 10/10 a component only binds the semantic layer).

A RADIO GROUP OF FIVE WHOLE STARS - DECIDED IN THE AUDIT (2026-10-22)

  The APG rating pattern: one Tab stop, arrows move and check. No half
  stars, no way back to zero in v1. Read-only is a single image announced as
  "3 out of 5 stars", with no focus.

THE STAR IS BRAND, NOT WARNING (D1)

  bg-warning is a dark brown in light (#704F00) and doesn't read as a star.

THE HOVER PREVIEW IS A DECLARED EXCEPTION

  The preview (bg-brand-hover) against a checked star (bg-brand) is 1.59
  light, 1.15 dark. It is transient and never the only cue: the checked radio
  and its announcement carry the value.

THE OFF STAR IS AN OUTLINE OF border-width.2 (F=a, 2026-10-22)

  The drawing had 1.5px, which is not on the scale.

THE FOCUSED STAR NEEDS A BACKGROUND

  The ring is drawn around the 24px box; the box gets bg-canvas so the
  ring's gap shows (A4 in the audit).

NO SIZE FOR THE GLYPH

  The 20px star inside the 24px box is the shape of the icon, not a spacing
  decision.
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
  'label-text':          'text-primary',
  'label-text-disabled': 'text-disabled',
  'star-on':             'bg-brand',
  'star-preview':        'bg-brand-hover',
  'star-off':            'border-strong',
  'star-disabled':       'text-disabled',
  'focus-gap':           'bg-canvas',
}

# ------------------------------------------------------------- geometry
GEOM = {
  'star-size':     'iconSize.24',
  'star-stroke':   'border.width.2',
  'gap':           'space.4',
  'focus-radius':  'radius.sm',
}

TYPE = {
  'font': 'type.styles.body-md',
}

PENDING = {
  'star-preview-on-brand': (
    'The hover preview (bg-brand-hover) against a checked star (bg-brand) is '
    '1.59:1 light, 1.15:1 dark. It is transient and never the only cue: the '
    'checked radio and its announcement carry the value.'
  ),
}

UNDER = ('bg-canvas', 'bg-surface', 'bg-surface-raised')   # where a rating is placed

# (what, fg role, against, floor, exception key)
COMBOS = (
  [('label-text',   'label-text',   u, 4.5, None) for u in UNDER] +
  [('star-on',      'star-on',      u, 3.0, None) for u in UNDER] +
  [('star-off',     'star-off',     u, 3.0, None) for u in UNDER] +
  [('star-preview', 'star-preview', 'bg-brand', 3.0, 'star-preview-on-brand')]
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
        name = f'rating-{role}'
        alias[name] = ref
        if ref.startswith('#'):
            problems.append(f'{name}: loose hex ({ref}) - every color value is born as an alias')
            continue
        if ref not in SEM:
            problems.append(f'{name}: points to {ref}, which does not exist in the Foundation')
            continue
        light, dark = SEM[ref]
        resolved[name] = {'light': light, 'dark': dark}

    for group in (GEOM, TYPE):
        for role, ref in group.items():
            name = f'rating-{role}'
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
    print('RATING TOKEN LAYER')
    print('=' * 74)
    for name in sorted(alias):
        print(f'  {name:<28} -> {alias[name]}')
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
            'component': 'Rating',
            'version': '0.1.0',
            'foundation': FOUND['meta']['version'],
            'figmaNode': '514:577',
            'states': ['default', 'hover', 'focus', 'disabled', 'read-only'],
            'note': (
                'Radio group of five whole stars, no way back to zero. Read-only is '
                'one image. One declared exception, the hover preview on a checked star.'
            ),
        },
        'alias': alias,
        'resolved': resolved,
        'contrast': rows,
        'pending': PENDING,
    }
    json.dump(out, open(comp_out('rating', 'tokens.json'), 'w'), indent=2, ensure_ascii=False)
    print('\nbuild/components/rating/tokens.json written')
    write_css()
    return 0


# ------------------------------------------------------------------- css
def write_css():
    L = []
    w = L.append
    w('/* AL Design System - Rating tokens')
    w(' * GENERATED by src/components/rating/tokens.py. Do not edit by hand.')
    w(' *')
    w(' * Every color is a semantic the theme switches on :root.')
    w(' */')
    w('')
    w(':root {')
    w('  /* color */')
    for role, ref in COLOR.items():
        w(f'  --al-rating-{role}: {css_ref(ref)};')
    w('')
    w('  /* geometry */')
    for role, ref in GEOM.items():
        w(f'  --al-rating-{role}: {css_ref(ref)};')
    w('')
    w('  /* type */')
    w('  --al-rating-font-size: var(--al-font-size-md);')
    w('  --al-rating-line-height: var(--al-line-height-md);')
    w('  --al-rating-font-weight: var(--al-font-weight-regular);')
    w('}')
    w('')
    save_css('rating', '\n'.join(L))


if __name__ == '__main__':
    sys.exit(run())
