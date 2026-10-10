"""
Token layer for the Alert.

The rule of this layer: nothing here invents a value. Every token points to a
Foundation token by NAME. There is no declared-value exception: the Alert
takes the content width and has no time on screen.

Naming:
  code  -> alert-danger-border   (hyphen)
  Figma -> border/danger         (folder)
Figma has no variable per component: the node binds the semantic or
Foundation variable the token points to.
Hyphen in code, folder in Figma: they are different layers. Never
collapse one into the other.

THIRD COMPONENT OF TIER 5 AND LAST OF V1 (2026-10-09)

  Component set `alert`, node 373:5186. 4 `Status` variants (Success /
  Warning / Danger / Info) and the `actions` and `close` booleans. Icon 24 at
  the top + 16/24 bold title + Body/md description (always present) + X
  (Ghost sm Icon Button). Action row on the right: Ghost md + Primary md
  Button. Background bg-surface-raised (the same as the Card), 1px border in
  the status color, xl radius, padding 16, no shadow: the Alert lives in the
  page flow, at the top, below the header.

  Scope decisions: Danger is NOT Error - it is caution, not failure; the
  description is always visible; 16 bold title; Ghost + Primary md actions,
  aligned to the right; optional X, Warning and Danger without an X while
  the situation exists.

THE "danger" STATUS USES THE "danger" SEMANTIC

  Unlike the Toast, where the status is called "error". In the Alert the
  name is the Foundation's because the meaning is different.

THE TITLE IS NOT A FOUNDATION STYLE

  16/24 bold doesn't exist in type.styles (Label/lg is medium). The title is
  built from three loose scale tokens - md size, md line height, bold weight
  - instead of a new style in the Foundation (only the Alert would use it).

MOTION

  Enters and exits with the controls' fast transition (duration-feedback,
  120ms), opacity only. Entering uses easing-enter, exiting easing-exit.

NO TOKEN, ON PURPOSE

  Height: comes from the content. Width: the page content's. Icon:
  `icon-size-24` straight from the Foundation (rule from the Tag and the
  Tooltip). Shadow: none. Buttons and X: the Button and Icon Button
  components; on bg-surface-raised the Ghost and the X use `bg-hover-raised`
  / `bg-active-raised` (lesson from Modal 0.18.1), no new token. The
  Primary's white label at rest (3.34:1) is the Button's brand exception,
  inherited, not new.
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
    'bg':          'bg-surface-raised',
    'title':       'text-primary',
    'description': 'text-secondary',
}

# The icon and the border carry the status; the icon is the clue that doesn't
# depend on color (Spectrum), the border passes 3:1 against the background and
# against the page.
STATUS = ('success', 'warning', 'danger', 'info')
for status in STATUS:
    COLOR[f'{status}-icon'] = f'text-{status}'
    COLOR[f'{status}-border'] = f'border-{status}'

# ------------------------------------------------------------- geometry
GEOM = {
    'padding':      'space.16',
    'gap':          'space.16',             # icon -> text -> X
    'text-gap':     'space.4',              # title -> description
    'section-gap':  'space.24',             # text -> action row
    'actions-gap':  'space.16',             # button -> button
    'radius':       'radius.xl',
    'border-width': 'border.width.1',
}

# Title built from the scale; the description is a whole style.
TITLE = {
    'title-font-size':   'type.size.md',
    'title-line-height': 'type.leading.md',
    'title-font-weight': 'type.weight.bold',
}
TYPE = {
    'description-font': 'type.styles.body-md',
}

# The controls' fast transition.
MOTION = {
    'duration':     'motion.duration.feedback',
    'easing-enter': 'motion.easing.enter',
    'easing-exit':  'motion.easing.exit',
}

PENDING = {}

# Screens the alert appears on. They are not Alert tokens.
PAGES = {
    'canvas':  'bg-canvas',
    'surface': 'bg-surface',
}

# (role, fg, background(s), floor, exception)
COMBOS = [
    ('title',       'title',       'bg', 4.5, None),
    ('description', 'description', 'bg', 4.5, None),
]
for status in STATUS:
    COMBOS.append((f'{status}/icon', f'{status}-icon', 'bg', 3.0, None))
    COMBOS.append((f'{status}/border', f'{status}-border', ('bg', 'canvas', 'surface'), 3.0, None))


# ------------------------------------------------------------------ gate
def ink(role):
    return PAGES.get(role) or COLOR[role]


def contrast_rows():
    rows = []
    for what, fg, bgs, min_ratio, exc in COMBOS:
        if isinstance(bgs, str):
            bgs = (bgs,)
        for theme, i in (('light', 0), ('dark', 1)):
            for bg in bgs:
                a, b = SEM[ink(fg)][i], SEM[ink(bg)][i]
                ratio = round(cr(a, b), 2)
                rows.append({'theme': theme, 'what': f'{what}/{bg}', 'fg': a, 'bg': b,
                             'ratio': ratio, 'min': min_ratio,
                             'pass': ratio >= min_ratio, 'exception': exc})
    return rows


def run():
    alias, resolved, problems = {}, {}, []

    for role, ref in COLOR.items():
        name = f'alert-{role}'
        alias[name] = ref
        if ref.startswith('#'):
            problems.append(f'{name}: loose hex ({ref})')
        elif ref not in SEM:
            problems.append(f'{name}: points to {ref}, which does not exist in the semantic layer')
        else:
            resolved[name] = {'light': SEM[ref][0], 'dark': SEM[ref][1]}

    for group in (GEOM, TITLE, TYPE, MOTION):
        for role, ref in group.items():
            name = f'alert-{role}'
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
    print('ALERT TOKEN LAYER')
    print('=' * 74)
    for name in sorted(alias):
        print(f'  {name:<34} -> {alias[name]}')
    print('-' * 74)
    for r in rows:
        tag = 'OK  ' if r['pass'] else ('EXC ' if r['exception'] else 'FAIL')
        print(f'  {tag} {r["what"]:<34} {r["theme"]:<5} {r["fg"]} / {r["bg"]}  {r["ratio"]}:1 (floor {r["min"]})')
    print(f'contrast: {len(rows)} measurements  |  pass: {len(rows) - len(fails) - len(excs)}  |  '
          f'declared exceptions: {len(excs)}  |  fail: {len(fails)}')
    if fails:
        print(f'{len(fails)} COMBINATION(S) FAIL THE CONTRAST GATE')
        return 1
    print(f'{len(alias)} tokens, all aliases of the Foundation.')

    out = {
        'meta': {
            'component': 'Alert',
            'version': '0.1.0',
            'foundation': FOUND['meta']['version'],
            'figmaNode': '373:5186',
            'note': (
                'Background bg-surface-raised, 1px border and icon 24 in the status color, 16/24 '
                'bold title built from the scale, Body/md description always visible, padding 16, '
                'gap 16, 24 to the action row, xl radius, no shadow. At the top of the page, below '
                'the header, at the content width. Enters and exits with opacity in '
                'duration-feedback. No contrast exception.'
            ),
        },
        'alias': alias,
        'resolved': resolved,
        'contrast': rows,
        'pending': PENDING,
    }
    json.dump(out, open(comp_out('alert', 'tokens.json'), 'w'), indent=2, ensure_ascii=False)
    print('\nbuild/components/alert/tokens.json written')
    write_css(alias)
    return 0


# ---------------------------------------------------------------- css
def _scale_key(scale, v, what):
    for key, val in FOUND['type'][scale].items():
        if val == v:
            return key
    raise KeyError(f'type.{scale} with value {v} does not exist in the Foundation ({what})')


def write_css(alias):
    L = []
    w = L.append
    w('/* AL Design System - Alert tokens')
    w(' * GENERATED by src/components/alert/tokens.py. Do not edit by hand.')
    w(' */')
    w('')
    w(':root {')
    w('')
    w('  /* color - box and text */')
    for role in ('bg', 'title', 'description'):
        w(f'  --al-alert-{role}: {css_ref(COLOR[role])};')
    w('')
    w('  /* color - status: icon and border */')
    for status in STATUS:
        for part in ('icon', 'border'):
            role = f'{status}-{part}'
            w(f'  --al-alert-{role}: {css_ref(COLOR[role])};')
    w('')
    w('  /* geometry */')
    for role, ref in GEOM.items():
        w(f'  --al-alert-{role}: {css_ref(ref)};')
    w('')
    w('  /* motion - the controls\' fast transition */')
    for role, ref in MOTION.items():
        w(f'  --al-alert-{role}: {css_ref(ref)};')
    w('')
    w('  /* typography - title built from the scale, description = Body/md */')
    for role, ref in TITLE.items():
        w(f'  --al-alert-{role}: {css_ref(ref)};')
    w('  --al-alert-title-tracking: 0em;')
    for role, ref in TYPE.items():
        style = resolve_foundation(ref)
        prefix = f'--al-alert-{role}'.replace('-font', '')
        w(f'  {prefix}-font-size: var(--al-font-size-{_scale_key("size", style[1], role)});')
        w(f'  {prefix}-line-height: var(--al-line-height-{_scale_key("leading", style[2], role)});')
        w(f'  {prefix}-font-weight: var(--al-font-weight-{_weight_key(style[3])});')
        w(f'  {prefix}-tracking: {style[4]};')
    w('}')
    w('')
    text = '\n'.join(L)
    missing = [n for n in alias if not n.endswith('-font') and f'--al-{n}:' not in text]
    if missing:
        raise AssertionError(f'tokens missing from the CSS: {missing}')
    save_css('alert', text)


def _weight_key(v):
    for key, val in FOUND['type']['weight'].items():
        if val == v:
            return key
    raise KeyError(f'type.weight with value {v} does not exist in the Foundation')


if __name__ == '__main__':
    sys.exit(run())
