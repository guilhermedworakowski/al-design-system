"""
Token layer for the Link.

The one rule of this layer: nothing here invents a value. Every token points
to a Foundation token by NAME. The gate at the end of the file rejects
anything that is a loose value - hex, px, number.

Naming:
  code  -> link-text-hover      (hyphen)
  Figma -> the node binds the semantic the token points to (no component
           variable: since 10/10 a component only binds the semantic layer).

THE DEFAULT INK IS A PRIMITIVE, NOT A SEMANTIC

  The rest ink is the brand orange (#FC5000) in both themes - a design decision
  about the action color, taken in the audit. There is no text semantic with
  that value (`text-brand` is the darker #992700 precisely because #FC5000
  doesn't reach 4.5:1 on white), and creating one would change the semantic
  layer for a single component. So the token points to the primitive
  `color.primitive.orange.500`, which is theme-invariant.

ONE DECLARED CONTRAST EXCEPTION

  Default on the light canvas and surface sits below 4.5:1 (brand exception,
  taken consciously in the audit). In the dark theme it passes on the canvas
  but not on the surface (4.36:1) - same exception.
  What pays the exception is the underline, present in every state: the link
  never depends on color alone (WCAG 1.4.1). guidelines.md carries the rule.

NO UNDERLINE OR ICON COLOR TOKEN

  Both inherit the text through currentColor, which already varies by state.

TYPOGRAPHY

  Standalone, the link uses label-md. Inside running text it inherits the
  paragraph's font - the CSS does that with `font: inherit` on the inline
  modifier, so there is no second set of type tokens.
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

PRIMITIVE = 'color.primitive.'

# ---------------------------------------------------------------- color
COLOR = {
  'text-default': 'color.primitive.orange.500',
  'text-hover':   'text-brand',
  'text-focus':   'text-brand',
}

# The ring points to the Foundation's composite shadow, not to a raw color -
# that keeps the state color inside the contrast gate. Same as the Button.
RING = {
  'ring': 'focusRing.default',
}

# ------------------------------------------------------------- geometry
GEOM = {
  'underline-default': 'border.width.1',
  'underline-hover':   'border.width.2',
  'underline-offset':  'space.4',
  'gap':               'space.8',
  'icon-size':         'iconSize.20',
}

TYPE = {
  'font': 'type.styles.label-md',
}

PENDING = {
  'default-below-aa': (
    'Default (#FC5000) on the light canvas/surface is below 4.5:1. Brand exception '
    'decided in the audit; the underline in every state keeps the link from '
    'depending on color alone (WCAG 1.4.1). On the dark canvas it passes (5.32:1); '
    'on the dark surface it falls to 4.36:1 and is covered by the same exception.'
  ),
}

# (what, ink role, floor, exception key)
COMBOS = [
  ('text-default', 'text-default', 4.5, 'default-below-aa'),
  ('text-hover',   'text-hover',   4.5, None),
  ('text-focus',   'text-focus',   4.5, None),
]
UNDER = ('bg-canvas', 'bg-surface')   # where a link is placed


# ------------------------------------------------------------------ gate
def themes(ref):
    """(light, dark) of a color ref - a semantic, or a theme-invariant primitive."""
    if ref.startswith(PRIMITIVE):
        v = resolve_foundation('color.primitive.' + '.'.join(ref.split('.')[2:]))
        return v, v
    return SEM[ref]


def color_css(ref):
    if ref.startswith(PRIMITIVE):
        return 'var(--al-color-' + '-'.join(ref.split('.')[2:]) + ')'
    return css_ref(ref)


def contrast_rows():
    rows = []
    for what, role, floor, exc in COMBOS:
        fg = themes(COLOR[role])
        for under in UNDER:
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
        name = f'link-{role}'
        alias[name] = ref
        if ref.startswith('#'):
            problems.append(f'{name}: loose hex ({ref}) - every color value is born as an alias')
            continue
        try:
            light, dark = themes(ref)
        except KeyError:
            problems.append(f'{name}: points to {ref}, which does not exist in the Foundation')
            continue
        resolved[name] = {'light': light, 'dark': dark}

    for group in (RING, GEOM, TYPE):
        for role, ref in group.items():
            name = f'link-{role}'
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
    print('LINK TOKEN LAYER')
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
            'component': 'Link',
            'version': '0.1.0',
            'foundation': FOUND['meta']['version'],
            'figmaNode': '464:490',
            'states': ['default', 'hover', 'focus'],
            'note': (
                'One type, always underlined, optional trailing icon. Standalone uses '
                'label-md; inline inherits the paragraph font. No visited state. One '
                'declared exception: the brand-orange default in the light theme.'
            ),
        },
        'alias': alias,
        'resolved': resolved,
        'contrast': rows,
        'pending': PENDING,
    }
    json.dump(out, open(comp_out('link', 'tokens.json'), 'w'), indent=2, ensure_ascii=False)
    print('\nbuild/components/link/tokens.json written')
    write_css()
    return 0


# ------------------------------------------------------------------- css
def write_css():
    L = []
    w = L.append
    w('/* AL Design System - Link tokens')
    w(' * GENERATED by src/components/link/tokens.py. Do not edit by hand.')
    w(' *')
    w(' * The default ink is the theme-invariant brand primitive; hover and focus')
    w(' * point to text-brand, which the theme switches on :root.')
    w(' */')
    w('')
    w(':root {')
    w('  /* color - underline and icon inherit through currentColor */')
    for role, ref in COLOR.items():
        w(f'  --al-link-{role}: {color_css(ref)};')
    w('')
    w('  /* focus */')
    for role, ref in RING.items():
        w(f'  --al-link-{role}: {css_ref(ref)};')
    w('')
    w('  /* geometry */')
    for role, ref in GEOM.items():
        w(f'  --al-link-{role}: {css_ref(ref)};')
    w('')
    w('  /* type - standalone only; inline inherits the paragraph */')
    style = resolve_foundation(TYPE['font'])
    w('  --al-link-font-size: var(--al-font-size-sm);' if style[1] == 14 else
      f'  --al-link-font-size: {style[1]}px;')
    w('  --al-link-line-height: var(--al-line-height-sm);')
    w('  --al-link-font-weight: var(--al-font-weight-medium);')
    w(f'  --al-link-tracking: {style[4]};')
    w('}')
    w('')
    save_css('link', '\n'.join(L))


if __name__ == '__main__':
    sys.exit(run())
