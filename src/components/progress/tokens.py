"""
Token layer for the Progress.

The one rule of this layer: nothing here invents a value. Every token points
to a Foundation token by NAME. The gate at the end of the file rejects
anything that is a loose value - hex, px, number.

Naming:
  code  -> progress-fill-bg      (hyphen)
  Figma -> the node binds the semantic the token points to (no component
           variable: since 10/10 a component only binds the semantic layer).

THE TRACK IS A NEW SEMANTIC

  `bg-track` was born in the Foundation for this component: the empty part of
  the bar has to read above canvas, surface and surface-raised in both themes.
  It is out of the contrast measurement - the track only hints at capacity.

TWO DECLARED CONTRAST EXCEPTIONS

  The fill against the track sits below 3:1 (2.53 light, 2.20 dark). The bar is
  never the only carrier of progress: Label shows the percentage, Steps shows
  the count, and Thin needs aria-valuenow plus a text context nearby.
  guidelines.md carries the rule. The fill against every background passes 3:1.

HEIGHTS ARE SPACE PRIMITIVES

  8px (Label, Steps) and 4px (Thin) point to space.8 and space.4, as the
  Divider did with its line - decided with Gui on 2026-10-21.

NO WIDTH TOKEN

  The bar fills its container; the fill width comes from value/max.
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
  'track-bg':   'bg-track',
  'fill-bg':    'bg-brand',
  'label-text': 'text-primary',
  'meta-text':  'text-secondary',
}

# ------------------------------------------------------------- geometry
GEOM = {
  'radius':      'radius.full',
  'height':      'space.8',
  'height-thin': 'space.4',
  'gap':         'space.8',
}

TYPE = {
  'font': 'type.styles.body-sm',
}

PENDING = {
  'fill-on-track': (
    'The fill (bg-brand) against the track (bg-track) is below 3:1 - 2.53:1 light, '
    '2.20:1 dark. The bar never carries progress alone: Label has the percentage, '
    'Steps has the count, Thin needs aria-valuenow and a text context (WCAG 1.4.11 '
    'is met by the text, not by the bar).'
  ),
}

UNDER = ('bg-canvas', 'bg-surface', 'bg-surface-raised')   # where a progress is placed

# (what, fg role, against, floor, exception key)
COMBOS = (
  [('label-text', 'label-text', u, 4.5, None) for u in UNDER] +
  [('meta-text',  'meta-text',  u, 4.5, None) for u in UNDER] +
  [('fill-bg',    'fill-bg',    u, 3.0, None) for u in UNDER] +
  [('fill-bg',    'fill-bg',    'bg-track', 3.0, 'fill-on-track')]
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
        name = f'progress-{role}'
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
            name = f'progress-{role}'
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
    print('PROGRESS TOKEN LAYER')
    print('=' * 74)
    for name in sorted(alias):
        print(f'  {name:<26} -> {alias[name]}')
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
            'component': 'Progress',
            'version': '0.1.0',
            'foundation': FOUND['meta']['version'],
            'figmaNode': '470:307',
            'types': ['label', 'steps', 'thin'],
            'note': (
                'Determinate only, no indeterminate type. Label and Steps carry text '
                'over an 8px bar; Thin is a 4px bar alone. The track is the new '
                'semantic bg-track; two declared exceptions, fill against track.'
            ),
        },
        'alias': alias,
        'resolved': resolved,
        'contrast': rows,
        'pending': PENDING,
    }
    json.dump(out, open(comp_out('progress', 'tokens.json'), 'w'), indent=2, ensure_ascii=False)
    print('\nbuild/components/progress/tokens.json written')
    write_css()
    return 0


# ------------------------------------------------------------------- css
def write_css():
    L = []
    w = L.append
    w('/* AL Design System - Progress tokens')
    w(' * GENERATED by src/components/progress/tokens.py. Do not edit by hand.')
    w(' *')
    w(' * Every color is a semantic the theme switches on :root.')
    w(' */')
    w('')
    w(':root {')
    w('  /* color */')
    for role, ref in COLOR.items():
        w(f'  --al-progress-{role}: {css_ref(ref)};')
    w('')
    w('  /* geometry */')
    for role, ref in GEOM.items():
        w(f'  --al-progress-{role}: {css_ref(ref)};')
    w('')
    w('  /* type - label and meta share one style */')
    w('  --al-progress-font-size: var(--al-font-size-sm);')
    w('  --al-progress-line-height: var(--al-line-height-sm);')
    w('  --al-progress-font-weight: var(--al-font-weight-regular);')
    w('}')
    w('')
    save_css('progress', '\n'.join(L))


if __name__ == '__main__':
    sys.exit(run())
