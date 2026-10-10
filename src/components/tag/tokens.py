"""
Token layer for the Tag.

The one rule of this layer: nothing here invents a value. Every token points
to a Foundation token by NAME. The gate at the end of the file rejects
anything that is a loose value - hex, px, number.

Naming:
  code  -> tag-filled-success-bg       (hyphen)
  Figma -> bg/success                  (folder)
Figma has no variable per component: the node binds the semantic or
Foundation variable the token points to.
Hyphen in code, folder in Figma: they are different layers. Never
collapse one into the other.

WHY THE TYPE COMES BEFORE THE STATUS

  The Tag has two variant dimensions, and they are not symmetric. `Type`
  (filled/outlined) decides WHICH ROLES EXIST: filled has a fill and a
  transparent border; outlined has a transparent background and a colored
  border. `Status` only swaps WHICH COLOR goes into each role.

  That is why the type takes the same place `primary`/`secondary`/`ghost`/
  `danger` take in the Button - and the status goes one level down.

THE OUTLINED LABEL IS NOT `text-on-solid`

  It looks like a detail and it isn't. With no fill, the outlined label is not
  on a solid - it is on the canvas. `text-on-solid` is #FFFFFF in the light
  theme and #181818 in dark, which are exactly the two `bg-canvas` values:
  using it there gives 1.00 contrast in both themes, invisible text. The
  outlined uses the STATUS ink (`text-success`, `text-danger`, ...), measured
  against the canvas.

  It came up in the audit. It is written here so it doesn't come back.

ZERO CONTRAST EXCEPTIONS

  The Button has three brand exceptions because the brand orange doesn't reach
  4.5:1 with white on top. The Tag has none - the Brand status was left out of
  this version on purpose, and without it no pair drops below the floor. It is
  the first AL component to close with zero exceptions while CARRYING TEXT (the
  Icon Button closes at zero, but against the 3:1 floor of 1.4.11).
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

TRANSPARENT = 'transparent'   # absence of color, not a color choice

# ---------------------------------------------------------------- color
# Two dimensions: type -> status -> role.
#
# The filled border exists and is transparent. It is not decoration: it is
# what makes filled take the SAME BOX as outlined. Without it, the outlined
# 1px border would grow the box by 2px on both axes and a row of filters mixing
# the two types would misalign. Same mechanism as the Button.
COLOR = {
  'filled': {
    'success': {'bg': 'bg-success', 'label': 'text-on-solid', 'border': TRANSPARENT},
    'warning': {'bg': 'bg-warning', 'label': 'text-on-solid', 'border': TRANSPARENT},
    'error':   {'bg': 'bg-danger',  'label': 'text-on-solid', 'border': TRANSPARENT},
    'info':    {'bg': 'bg-info',    'label': 'text-on-solid', 'border': TRANSPARENT},
    # The neutral's light gray calls for dark ink, not the solid one.
    'neutral': {'bg': 'bg-active',  'label': 'text-primary',  'border': TRANSPARENT},
  },
  'outlined': {
    'success': {'label': 'text-success', 'border': 'border-success'},
    'warning': {'label': 'text-warning', 'border': 'border-warning'},
    'error':   {'label': 'text-danger',  'border': 'border-danger'},
    'info':    {'label': 'text-info',    'border': 'border-info'},
    # There is no `border-neutral`; border-strong is the system's outline gray.
    'neutral': {'label': 'text-primary', 'border': 'border-strong'},
  },
}

# ONE token, not five. The outlined background doesn't vary by status - five
# tokens with the same value would be five places to get the same thing wrong.
TYPE_SHARED = {
  'outlined': {'bg': TRANSPARENT},
}

# --------------------------------------------------------------- dismiss
# The X is focusable: when the boolean `Icon` property is on, the tag stops
# being read-only and enters the tab order. The focus ring is the same as the
# Button's and the Icon Button's - it points to the Foundation's composite
# shadow, not the raw color, which is what keeps the state color inside the
# contrast gate.
#
# There is NO X ink token: it inherits the label's color through currentColor,
# which already varies by type and status. Ten tokens to reproduce ten values
# the CSS inherits by itself would be noise. Same decision as the Icon Button's
# spinner.
#
# There is NO hover token: by design the X has no hover background, only the
# cursor changes. `cursor` is a keyword, not a scale value.
DISMISS = {
  'ring': 'focusRing.default',
}

# ------------------------------------------------------------- geometry
# padding-x and padding-y separate, unlike the Icon Button: the Tag is
# rectangular, like the Button.
#
# The gap is space.8 in both sizes - the same as the Button, which is what lets
# a dismissible Tag and a Button live together without a different inner rhythm.
SIZE = {
  'sm': {'padding-x': 'space.8',  'padding-y': 'space.2',
         'gap': 'space.8', 'font': 'type.styles.label-sm', 'icon-size': 'iconSize.16'},
  'md': {'padding-x': 'space.12', 'padding-y': 'space.4',
         'gap': 'space.8', 'font': 'type.styles.label-md', 'icon-size': 'iconSize.20'},
}

SHARED = {
  'radius':       'radius.full',
  'border-width': 'border.width.1',
}

# Recorded, not forgotten: the X target is smaller than the 24px of WCAG 2.5.8.
# Same family of tradeoff as the Button's sm (36 against Carbon's 44), and the
# answer is the same - a usage rule, not geometry. guidelines.md covers it.
PENDING = {
  'x-target': ('16px in sm and 20px in md, below the 24px of WCAG 2.5.8. '
               'A conscious decision: no expansion through a pseudo-element. The usage '
               'rule reserves the dismissible sm for pointer interfaces.'),
}


# ------------------------------------------------------------------ gate
def bind_color(name, ref, alias, resolved, problems):
    """One color token: records the alias and resolves it in both themes, or fails."""
    alias[name] = ref
    if ref == TRANSPARENT:
        resolved[name] = {'light': TRANSPARENT, 'dark': TRANSPARENT}
        return
    if ref.startswith('#'):
        problems.append(f'{name}: loose hex ({ref}) - every color value is born as an alias of a semantic')
        return
    if ref not in SEM:
        problems.append(f'{name}: points to {ref}, which does not exist in the semantic layer')
        return
    light, dark = SEM[ref]
    resolved[name] = {'light': light, 'dark': dark}


def contrast_rows():
    """The component's rendered combinations, measured with the Foundation's
    engine. Filled measures the label against its own fill; outlined measures
    the label and the border against the canvas AND the surface, because with
    no fill it is the page background that shows through."""
    rows = []
    for status, roles in COLOR['filled'].items():
        for theme, i in (('light', 0), ('dark', 1)):
            rows.append({
                'theme': theme, 'type': 'filled', 'status': status, 'what': 'label',
                'fg': roles['label'], 'bg': roles['bg'],
                'ratio': round(cr(SEM[roles['label']][i], SEM[roles['bg']][i]), 2),
                'min': 4.5,
            })
    for status, roles in COLOR['outlined'].items():
        for under in ('bg-canvas', 'bg-surface'):
            for theme, i in (('light', 0), ('dark', 1)):
                rows.append({
                    'theme': theme, 'type': 'outlined', 'status': status, 'what': f'label on {under}',
                    'fg': roles['label'], 'bg': under,
                    'ratio': round(cr(SEM[roles['label']][i], SEM[under][i]), 2),
                    'min': 4.5,
                })
                rows.append({
                    'theme': theme, 'type': 'outlined', 'status': status, 'what': f'border on {under}',
                    'fg': roles['border'], 'bg': under,
                    'ratio': round(cr(SEM[roles['border']][i], SEM[under][i]), 2),
                    'min': 3.0,
                })
    for r in rows:
        r['pass'] = r['ratio'] >= r['min']
    return rows


def run():
    alias, resolved, problems = {}, {}, []

    for kind, statuses in COLOR.items():
        for status, roles in statuses.items():
            for role, ref in roles.items():
                bind_color(f'tag-{kind}-{status}-{role}', ref, alias, resolved, problems)

    for kind, roles in TYPE_SHARED.items():
        for role, ref in roles.items():
            bind_color(f'tag-{kind}-{role}', ref, alias, resolved, problems)

    for role, ref in DISMISS.items():
        name = f'tag-dismiss-{role}'
        alias[name] = ref
        try:
            v = resolve_foundation(ref)
            resolved[name] = {'light': v['light'], 'dark': v['dark']}
        except KeyError:
            problems.append(f'{name}: {ref} does not exist in the Foundation')

    for size, roles in SIZE.items():
        for role, ref in roles.items():
            name = f'tag-{size}-{role}'
            alias[name] = ref
            try:
                resolved[name] = resolve_foundation(ref)
            except KeyError:
                problems.append(f'{name}: {ref} does not exist in the Foundation')

    for role, ref in SHARED.items():
        name = f'tag-{role}'
        alias[name] = ref
        try:
            resolved[name] = resolve_foundation(ref)
        except KeyError:
            problems.append(f'{name}: {ref} does not exist in the Foundation')

    # Derived height - it does NOT become a token. The border is absorbed by the
    # padding (padding: calc(pad - border-width)), so it doesn't enter the math
    # and both types close at the same number.
    heights = {}
    for size in SIZE:
        pad_y = resolve_foundation(SIZE[size]['padding-y'])
        leading = resolve_foundation(SIZE[size]['font'])[2]
        heights[size] = pad_y * 2 + leading

    rows = contrast_rows()
    fails = [r for r in rows if not r['pass']]

    print('=' * 74)
    print('TAG TOKEN LAYER')
    print('=' * 74)
    for name in sorted(alias):
        ref = alias[name]
        tag = 'transparent' if ref == TRANSPARENT else f'-> {ref}'
        print(f'  {name:<32} {tag}')
    print('-' * 74)
    for size in SIZE:
        print(f'derived height {size}: {heights[size]}px  (padding-y x2 + line height; '
              f'the border is absorbed by the padding)')
    print('filled and outlined take the same box: the outlined 1px border '
          'doesn\'t grow the tag')

    print('-' * 74)
    print(f'contrast: {len(rows)} measurements  |  pass: {len(rows) - len(fails)}  |  '
          f'fail: {len(fails)}  |  exceptions: 0')
    worst = min(rows, key=lambda r: r['ratio'] / r['min'])
    print(f'worst margin: {worst["type"]} {worst["status"]} {worst["what"]} ({worst["theme"]}) '
          f'= {worst["ratio"]}:1 against floor {worst["min"]}')

    for k, v in PENDING.items():
        print(f'pending: {k} - {v}')
    print('-' * 74)

    if problems:
        print(f'{len(problems)} TOKEN(S) FAIL THE ALIAS GATE:')
        for p in problems:
            print('   ', p)
        return 1
    if fails:
        print(f'{len(fails)} COMBINATION(S) FAIL THE CONTRAST GATE:')
        for f in fails:
            print(f'    {f["type"]} {f["status"]} {f["what"]} ({f["theme"]}): '
                  f'{f["ratio"]}:1 < {f["min"]}')
        return 1

    n_alias = sum(1 for r in alias.values() if r != TRANSPARENT)
    n_tr = len(alias) - n_alias
    print(f'{len(alias)} tokens: {n_alias} aliases of the Foundation, {n_tr} transparent.')
    print('0 loose values.')

    out = {
        'meta': {
            'component': 'Tag',
            'version': '0.1.0',
            'foundation': FOUND['meta']['version'],
            'figmaNode': '160:484',
            'types': list(COLOR),
            'statuses': list(COLOR['filled']),
            'sizes': list(SIZE),
            'states': ['default'],
            'note': (
                'A Tag is read-only by default: out of the tab order, no focus, no hover. '
                'The boolean `dismissible` property turns on a focusable X - only it '
                'enters the tab order, and only it has a ring. The X creates no ink '
                'token: it inherits the label through currentColor. Zero contrast '
                'exceptions; the Brand status was left out of this version by design.'
            ),
        },
        'alias': alias,
        'resolved': resolved,
        'derived': {'height': heights},
        'contrast': rows,
        'pending': PENDING,
    }
    json.dump(out, open(comp_out('tag', 'tokens.json'), 'w'), indent=2, ensure_ascii=False)
    print('\nbuild/components/tag/tokens.json written')
    write_css(alias, heights)
    return 0


# ------------------------------------------------------------------- css
def write_css(alias, heights):
    L = []
    w = L.append
    w('/* AL Design System - Tag tokens')
    w(' * GENERATED by src/components/tag/tokens.py. Do not edit by hand.')
    w(' *')
    w(' * There is no theme block here, and that is the point: each token points')
    w(' * to a semantic, and the theme switches on :root - the same element where')
    w(' * these aliases are declared. So :root re-substitutes all of them at once.')
    w(' *')
    w(' * The type comes before the status in the name because the type decides')
    w(' * which roles exist; the status only swaps the color of each role.')
    w(' */')
    w('')
    w(':root {')

    for kind, statuses in COLOR.items():
        w('')
        w(f'  /* {kind} */')
        for role, ref in TYPE_SHARED.get(kind, {}).items():
            w(f'  --al-tag-{kind}-{role}: {css_ref(ref)};')
        for status, roles in statuses.items():
            for role, ref in roles.items():
                w(f'  --al-tag-{kind}-{status}-{role}: {css_ref(ref)};')

    w('')
    w('  /* dismiss - only the X is focusable; the tag itself never gets focus */')
    for role, ref in DISMISS.items():
        w(f'  --al-tag-dismiss-{role}: {css_ref(ref)};')

    for size, roles in SIZE.items():
        w('')
        w(f'  /* size {size} - resulting height: {heights[size]}px */')
        for role, ref in roles.items():
            if ref.startswith('type.styles.'):
                style = resolve_foundation(ref)
                w(f'  --al-tag-{size}-font-size: var(--al-font-size-'
                  f'{"xs" if style[1] == 12 else "sm"});')
                w(f'  --al-tag-{size}-line-height: var(--al-line-height-'
                  f'{"xs" if style[2] == 16 else "sm"});')
                w(f'  --al-tag-{size}-font-weight: var(--al-font-weight-medium);')
                w(f'  --al-tag-{size}-tracking: {style[4]};')
                continue
            w(f'  --al-tag-{size}-{role}: {css_ref(ref)};')

    w('')
    w('  /* shared */')
    for role, ref in SHARED.items():
        w(f'  --al-tag-{role}: {css_ref(ref)};')
    w('}')
    w('')

    save_css('tag', '\n'.join(L))


if __name__ == '__main__':
    sys.exit(run())
