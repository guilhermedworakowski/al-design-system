"""
Token layer for the Avatar.

The one rule of this layer: nothing here invents a value. Every token points
to a Foundation token by NAME. The gate at the end of the file rejects
anything that is a loose value - hex, px, number.

Naming:
  code  -> avatar-md-icon-size      (hyphen)
  Figma -> avatar/md/icon-size      (folder)
They are different layers. Never collapse one into the other.

WHY THE COLOR DOESN'T REPEAT PER SIZE

  The Tag and the Button have color per variant because the variant CHANGES
  the color (primary is orange, danger is red). The Avatar has only one real
  variant dimension - size - and size changes no color at all: the three sizes
  use the same background and the same ink. That is why `avatar-bg`,
  `avatar-label` and `avatar-icon` are three tokens in total, not nine. Nine
  tokens repeating the same value three times would be three places for the
  same value to drift by mistake.

`avatar-label` AND `avatar-icon` ARE SEPARATE TOKENS EVEN POINTING TO THE SAME ALIAS

  Today both resolve to `text-primary` and so they are pixel-identical. But
  they are different roles - one is text (initials), the other is vector icon
  ink - and the audit's first finding was precisely the icon ink stuck on a
  BACKGROUND token (`bg-inverse`) that only matched in value. Separating the
  names now is what stops the same trap from coming back: if the icon ink ever
  needs to diverge from the text ink, the rebind is local, and nobody has to
  hunt down every place that used `avatar-label` to know whether that use was
  text or icon.

THERE IS NO BORDER TOKEN

  Unlike the Tag, the Avatar has no stroke in any variant. It is not an
  omission documented by mistake - it is the shape not using an outline.

TWO CONTRAST FLOORS, ON THE SAME COLOR PAIR

  `avatar-label` (initials) is text: 4.5:1 floor from 1.4.3. `avatar-icon`
  (vector glyph) is non-text: 3:1 floor from 1.4.11, a rule already set with
  the Icon and the Icon Button. Both resolve to the same hex today because both
  point to `text-primary`, so both pass both floors with room to spare - but
  the gate measures each one against its own floor, not against the easier one.

ZERO CONTRAST EXCEPTIONS

  The third AL component to close with zero exceptions, after the Tag. It
  creates no new pair at all: `text-primary` on `bg-subtle` is already one of
  the 80 pairs the Foundation measures (12.54:1 light, 9.98:1 dark).

THE DIAMETER IS NOT A TOKEN

  32 / 48 / 64 come from `padding x2 + icon-size` of the same size (8x2+16,
  12x2+24, 16x2+32) - and that math works for all three types (Initials, Icon,
  Photo) because the three take the same square box. Tokenizing the diameter
  would store the same information twice with two chances to diverge, like the
  height of the Button and the Tag.
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

# ----------------------------------------------------------------- color
# Shared by the three sizes - see the note in the header.
COLOR = {
    'bg':    'bg-subtle',
    'label': 'text-primary',   # initials - text floor, 4.5:1
    'icon':  'text-primary',   # vector glyph - non-text floor, 3:1
}

# ------------------------------------------------------------- geometry
SIZE = {
    'sm': {'padding': 'space.8',  'icon-size': 'iconSize.16', 'font': 'type.styles.label-sm'},
    'md': {'padding': 'space.12', 'icon-size': 'iconSize.24', 'font': 'type.styles.heading-xs'},
    'lg': {'padding': 'space.16', 'icon-size': 'iconSize.32', 'font': 'type.styles.heading-sm'},
}

SHARED = {
    'radius': 'radius.full',
}

PENDING = {}   # nothing pending in this version - see the docstring


# ------------------------------------------------------------------ gate
def bind_color(name, ref, alias, resolved, problems):
    """One color token: records the alias and resolves it in both themes, or fails."""
    alias[name] = ref
    if ref.startswith('#'):
        problems.append(f'{name}: loose hex ({ref}) - every color value is born as an alias of a semantic')
        return
    if ref not in SEM:
        problems.append(f'{name}: points to {ref}, which does not exist in the semantic layer')
        return
    light, dark = SEM[ref]
    resolved[name] = {'light': light, 'dark': dark}


def contrast_rows():
    """The component's two rendered combinations - label and icon against the
    background - measured with the Foundation's engine, each against its own
    floor (text 4.5:1, non-text 3:1)."""
    rows = []
    floors = {'label': 4.5, 'icon': 3.0}
    for role, min_ratio in floors.items():
        fg_ref = COLOR[role]
        bg_ref = COLOR['bg']
        for theme, i in (('light', 0), ('dark', 1)):
            rows.append({
                'theme': theme, 'what': role,
                'fg': fg_ref, 'bg': bg_ref,
                'ratio': round(cr(SEM[fg_ref][i], SEM[bg_ref][i]), 2),
                'min': min_ratio,
            })
    for r in rows:
        r['pass'] = r['ratio'] >= r['min']
    return rows


def run():
    alias, resolved, problems = {}, {}, []

    for role, ref in COLOR.items():
        bind_color(f'avatar-{role}', ref, alias, resolved, problems)

    for size, roles in SIZE.items():
        for role, ref in roles.items():
            name = f'avatar-{size}-{role}'
            alias[name] = ref
            try:
                resolved[name] = resolve_foundation(ref)
            except KeyError:
                problems.append(f'{name}: {ref} does not exist in the Foundation')

    for role, ref in SHARED.items():
        name = f'avatar-{role}'
        alias[name] = ref
        try:
            resolved[name] = resolve_foundation(ref)
        except KeyError:
            problems.append(f'{name}: {ref} does not exist in the Foundation')

    # Derived diameter - it does NOT become a token. See the note in the header.
    diameters = {}
    for size in SIZE:
        pad = resolve_foundation(SIZE[size]['padding'])
        icon = resolve_foundation(SIZE[size]['icon-size'])
        diameters[size] = pad * 2 + icon

    rows = contrast_rows()
    fails = [r for r in rows if not r['pass']]

    print('=' * 74)
    print('AVATAR TOKEN LAYER')
    print('=' * 74)
    for name in sorted(alias):
        print(f'  {name:<28} -> {alias[name]}')
    print('-' * 74)
    for size in SIZE:
        print(f'derived diameter {size}: {diameters[size]}px  '
              f'(padding x2 + icon-size; same box in all three types)')
    print('-' * 74)
    print(f'contrast: {len(rows)} measurements  |  pass: {len(rows) - len(fails)}  |  '
          f'fail: {len(fails)}  |  exceptions: 0')
    worst = min(rows, key=lambda r: r['ratio'] / r['min'])
    print(f'worst margin: {worst["what"]} ({worst["theme"]}) = {worst["ratio"]}:1 '
          f'against floor {worst["min"]}')
    if not PENDING:
        print('pending: none')
    print('-' * 74)

    if problems:
        print(f'{len(problems)} TOKEN(S) FAIL THE ALIAS GATE:')
        for p in problems:
            print('   ', p)
        return 1
    if fails:
        print(f'{len(fails)} COMBINATION(S) FAIL THE CONTRAST GATE:')
        for f in fails:
            print(f'    {f["what"]} ({f["theme"]}): {f["ratio"]}:1 < {f["min"]}')
        return 1

    print(f'{len(alias)} tokens, all aliases of the Foundation. 0 loose values.')

    out = {
        'meta': {
            'component': 'Avatar',
            'version': '0.1.0',
            'foundation': FOUND['meta']['version'],
            'figmaNode': '162:512',
            'types': ['initials', 'icon', 'photo'],
            'sizes': list(SIZE),
            'states': ['default'],
            'note': (
                'A static avatar by default: out of the tab order, no hover, no focus of '
                'its own. Whoever needs a clickable avatar wraps it in an actionable '
                'element that already has a ring (Icon Button, link) - the Avatar itself '
                'never gets a state. Color shared by the three sizes; circle shape only in '
                'this version (square/organization is left out, AL has no concept of '
                'organization yet). Zero contrast exceptions.'
            ),
        },
        'alias': alias,
        'resolved': resolved,
        'derived': {'diameter': diameters},
        'contrast': rows,
        'pending': PENDING,
    }
    json.dump(out, open(comp_out('avatar', 'tokens.json'), 'w'), indent=2, ensure_ascii=False)
    print('\nbuild/components/avatar/tokens.json written')
    write_css(alias, diameters)
    return 0


# ------------------------------------------------------------------- css
def write_css(alias, diameters):
    L = []
    w = L.append
    w('/* AL Design System - Avatar tokens')
    w(' * GENERATED by src/components/avatar/tokens.py. Do not edit by hand.')
    w(' *')
    w(' * There is no theme block here, and that is the point: each token points')
    w(' * to a semantic, and the theme switches on :root - the same element where')
    w(' * these aliases are declared. So :root re-substitutes all of them at once.')
    w(' *')
    w(' * Color is shared by the three sizes: size changes neither background nor')
    w(' * ink, only geometry.')
    w(' */')
    w('')
    w(':root {')
    w('')
    w('  /* color - shared by the three sizes */')
    for role, ref in COLOR.items():
        w(f'  --al-avatar-{role}: {css_ref(ref)};')

    for size, roles in SIZE.items():
        w('')
        w(f'  /* size {size} - resulting diameter: {diameters[size]}px */')
        for role, ref in roles.items():
            if ref.startswith('type.styles.'):
                style = resolve_foundation(ref)
                key = size_key(style[1])
                w(f'  --al-avatar-{size}-font-size: var(--al-font-size-{key});')
                w(f'  --al-avatar-{size}-line-height: var(--al-line-height-{key});')
                w(f'  --al-avatar-{size}-font-weight: {style[3]};')
                w(f'  --al-avatar-{size}-tracking: {style[4]};')
                continue
            w(f'  --al-avatar-{size}-{role}: {css_ref(ref)};')

    w('')
    w('  /* shared */')
    for role, ref in SHARED.items():
        w(f'  --al-avatar-{role}: {css_ref(ref)};')
    w('}')
    w('')

    save_css('avatar', '\n'.join(L))


if __name__ == '__main__':
    sys.exit(run())
