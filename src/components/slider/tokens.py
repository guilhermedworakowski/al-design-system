"""
Token layer for the Slider.

The one rule of this layer: nothing here invents a value. Every token points
to a Foundation token by NAME. The gate at the end of the file rejects
anything that is a loose value - hex, px, number.

Naming:
  code  -> slider-thumb-bg-hover      (hyphen)
  Figma -> the node binds the semantic the token points to (no component
           variable: since 10/10 a component only binds the semantic layer).

ONE THUMB, ONE SIZE, NO ERROR - DECIDED IN THE AUDIT (2026-10-22)

  A slider always holds a value, so there is nothing to validate (the
  Switch's reasoning). No range slider in v1.

THE TRACK REUSES THE PROGRESS EXCEPTION

  The fill against the track sits below 3:1 (2.53 light, 2.20 dark), the
  same pair as `fill-on-track` in the Progress. The value in text pays for
  it: `Show value` only turns off when the value is shown somewhere else.

HOVER AND ACTIVE ARE TRANSIENT (E=b, 2026-10-22)

  At rest the thumb (bg-brand) passes 3:1 on every background. In dark,
  brand-hover and brand-active drop below 3:1 on surface and surface-raised.
  WCAG 1.4.11 asks 3:1 for what identifies the control, and the resting
  state does that; hover and active last while the pointer is on it.

THE FOCUS GAP

  border-focus is the same orange as the thumb in light (1.0:1), so the ring
  would read as a bigger thumb. A 2px inner border in bg-canvas separates
  them (A1 in the audit).

THE HIT AREA ONLY EXISTS IN CODE

  The thumb is drawn at 20px; the area that takes the pointer is 24px
  (WCAG 2.5.8, A2 in the audit).

NO WIDTH TOKEN

  The slider fills its container; the fill width and the thumb position
  come from value/max.
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
  'value-text':          'text-primary',
  'range-text':          'text-secondary',
  'track-bg':            'bg-track',
  'fill-bg':             'bg-brand',
  'thumb-bg':            'bg-brand',
  'thumb-bg-hover':      'bg-brand-hover',
  'thumb-bg-active':     'bg-brand-active',
  'thumb-focus-gap':     'bg-canvas',
  'label-text-disabled': 'text-disabled',
  'track-bg-disabled':   'bg-disabled',
  'fill-bg-disabled':    'text-disabled',
  'thumb-bg-disabled':   'text-disabled',
}

# ------------------------------------------------------------- geometry
GEOM = {
  'track-height': 'space.4',
  'thumb-size':   'space.20',
  'thumb-hit':    'space.24',
  'radius':       'radius.full',
  'gap':          'space.8',
}

TYPE = {
  'font':       'type.styles.body-md',
  'range-font': 'type.styles.caption',
}

PENDING = {
  'fill-on-track': (
    'The fill (bg-brand) against the track (bg-track) is below 3:1 - 2.53:1 light, '
    '2.20:1 dark. Same pair as the Progress. The value in text carries the state '
    '(WCAG 1.4.11 is met by the text, not by the bar).'
  ),
  'thumb-transient': (
    'In dark, the hover and active thumb drop below 3:1 on surface and '
    'surface-raised (2.02 to 2.78). They are transient; the resting thumb passes '
    '3:1 on every background and identifies the control (decided E=b, 2026-10-22).'
  ),
}

UNDER = ('bg-canvas', 'bg-surface', 'bg-surface-raised')   # where a slider is placed

# (what, fg role, against, floor, exception key)
COMBOS = (
  [('label-text',      'label-text',      u, 4.5, None) for u in UNDER] +
  [('range-text',      'range-text',      u, 4.5, None) for u in UNDER] +
  [('fill-bg',         'fill-bg',         u, 3.0, None) for u in UNDER] +
  [('thumb-bg',        'thumb-bg',        u, 3.0, None) for u in UNDER] +
  [('thumb-bg-hover',  'thumb-bg-hover',  u, 3.0, 'thumb-transient') for u in UNDER] +
  [('thumb-bg-active', 'thumb-bg-active', u, 3.0, 'thumb-transient') for u in UNDER] +
  [('fill-bg',         'fill-bg',         'bg-track', 3.0, 'fill-on-track')]
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
        name = f'slider-{role}'
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
            name = f'slider-{role}'
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
    print('SLIDER TOKEN LAYER')
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
            'component': 'Slider',
            'version': '0.1.0',
            'foundation': FOUND['meta']['version'],
            'figmaNode': '514:501',
            'states': ['default', 'hover', 'active', 'focus', 'disabled'],
            'note': (
                'One thumb, one size, no error. The track reuses the Progress '
                'fill-on-track exception; hover and active are a declared '
                'transient exception in dark.'
            ),
        },
        'alias': alias,
        'resolved': resolved,
        'contrast': rows,
        'pending': PENDING,
    }
    json.dump(out, open(comp_out('slider', 'tokens.json'), 'w'), indent=2, ensure_ascii=False)
    print('\nbuild/components/slider/tokens.json written')
    write_css()
    return 0


# ------------------------------------------------------------------- css
def write_css():
    L = []
    w = L.append
    w('/* AL Design System - Slider tokens')
    w(' * GENERATED by src/components/slider/tokens.py. Do not edit by hand.')
    w(' *')
    w(' * Every color is a semantic the theme switches on :root.')
    w(' */')
    w('')
    w(':root {')
    w('  /* color */')
    for role, ref in COLOR.items():
        w(f'  --al-slider-{role}: {css_ref(ref)};')
    w('')
    w('  /* geometry */')
    for role, ref in GEOM.items():
        w(f'  --al-slider-{role}: {css_ref(ref)};')
    w('')
    w('  /* type - label and value share body-md, the range uses caption */')
    w('  --al-slider-font-size: var(--al-font-size-md);')
    w('  --al-slider-line-height: var(--al-line-height-md);')
    w('  --al-slider-font-weight: var(--al-font-weight-regular);')
    w('  --al-slider-range-font-size: var(--al-font-size-xs);')
    w('  --al-slider-range-line-height: var(--al-line-height-xs);')
    w('}')
    w('')
    save_css('slider', '\n'.join(L))


if __name__ == '__main__':
    sys.exit(run())
