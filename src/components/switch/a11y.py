"""
Accessibility QA for the Switch.

As with the other components, validation is by RENDERED COMBINATION - each
color role against the EFFECTIVE background, not a loose token pair.

THE COMBINATIONS INCLUDE THE ONES THAT ONLY EXIST IN CODE

  Figma has five variants on a single axis. The native input produces more:
  on + focus and on + disabled. They were decided with the tokens and are
  painted by switch.css - so they are measured here like any other. On + hover
  doesn't come in: it is identical to on (the force beats the hover, rule 14).

WHAT THE EFFECTIVE BACKGROUND CHANGES HERE

  1. WHERE THE SWITCH IS PLACED. The bare page (`bg-canvas`), a section band
     (`bg-surface`) or a card/modal (`bg-surface-raised`). The WORST counts.

  2. THE BORDER HAS TWO NEIGHBORS: the page outside and the track inside. A
     detail the token layer couldn't see: the off track is `bg-surface` - on a
     section band, track and page are the SAME color, and only the border and
     the thumb draw the control. That is why the visible label rule exists.

  3. THE THUMB MEASURES AGAINST THE TRACK IT IS ON, never against the page.

  4. WITH FOCUS, THE OUTER NEIGHBOR IS THE RING'S GAP (2px of `bg-canvas`),
     and the ring color comes from the box-shadow ITSELF - the last hex of the
     composite shadow.

TWO FLOORS, ON PURPOSE

  Text (label)                                = 4.5:1 from 1.4.3.
  Non-text (border, track, thumb, ring)       = 3:1 from 1.4.11.

THE MARKUP CONTRACT

  The rules are data: src/components/switch/contract.json, checked by
  tools/contract.py here and by the package's validator, from the same
  file. Each rule says why it exists. What this file still checks in
  code is listed there under "manual": what needs the whole page, the
  site's exact shape or its wording.

RUN ORDER - same as the Select, the Checkbox and the Radio: runs AFTER the
HTML it measures.

Run: python3 a11y.py [path.html]
     with no argument, measures build/site/index.html
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'tools'))
from paths import ROOT, TOKENS_JSON, SITE_HTML, comp_out  # noqa: E402
# this gate compares the ratio already rounded to 2 places, as it always has
from contrast import cr2 as cr  # noqa: E402
from htmltree import Tree, walk, has  # noqa: E402
import contract  # noqa: E402
FOUND = json.load(open(TOKENS_JSON))
SWITCH = json.load(open(comp_out('switch', 'tokens.json')))

RES = SWITCH['resolved']
PENDING = SWITCH['pending']
THEMES = (('light', 0), ('dark', 1))

TEXT_FLOOR = 4.5          # 1.4.3
NON_TEXT_FLOOR = 3.0      # 1.4.11

DEFAULT_HTML = SITE_HTML
OUT_JSON = comp_out('switch', 'a11y.json')

PAGES = ('bg-canvas', 'bg-surface', 'bg-surface-raised')

# state -> how the switch is painted, and which exception covers each role
STATES = {
    'default':          dict(border='switch-border',          track='switch-track',          thumb='switch-thumb',                  ring=False, label='switch-label',
                             border_exc='border-below-3-1',    thumb_exc='thumb-below-3-1'),
    'hover':            dict(border='switch-border-hover',    track='switch-track',          thumb='switch-thumb',                  ring=False, label='switch-label',
                             border_exc=None,                  thumb_exc='thumb-below-3-1'),
    'focus':            dict(border='switch-border',          track='switch-track',          thumb='switch-thumb',                  ring=True,  label='switch-label',
                             border_exc='border-below-3-1',    thumb_exc='thumb-below-3-1'),
    'checked':          dict(border='switch-border-checked',  track='switch-track-checked',  thumb='switch-thumb-checked',          ring=False, label='switch-label',
                             border_exc=None,                  thumb_exc=None),
    'checked-focus':    dict(border='switch-border-checked',  track='switch-track-checked',  thumb='switch-thumb-checked',          ring=True,  label='switch-label',
                             border_exc=None,                  thumb_exc=None),
    'disabled':         dict(border='switch-border-disabled', track='switch-track-disabled', thumb='switch-thumb-disabled',         ring=False, label='switch-label-disabled',
                             border_exc='disabled-below-aa',   thumb_exc='disabled-below-aa'),
    'disabled-checked': dict(border='switch-border-disabled', track='switch-track-disabled', thumb='switch-thumb-checked-disabled', ring=False, label='switch-label-disabled',
                             border_exc='disabled-below-aa',   thumb_exc='disabled-below-aa'),
}

# states with no variant in Figma - painted only by the code
CODE_ONLY = ('checked-focus', 'disabled-checked')


def tok(name, theme):
    return RES[name][theme]


def sem(name, theme):
    return FOUND['color']['semantic'][name][0 if theme == 'light' else 1]


def ring_ink(theme):
    """The color that paints the ring, read from the box-shadow ITSELF - the last hex."""
    shadow = RES['switch-ring'][theme]
    hexes = re.findall(r'#[0-9a-fA-F]{6}', shadow)
    if not hexes:
        raise ValueError(f'switch-ring ({theme}): box-shadow with no readable color -> {shadow}')
    return hexes[-1]


def worst(fg, backgrounds):
    return min((cr(fg, bg), bg) for bg in backgrounds)


def measure():
    rows = []
    for state, cfg in STATES.items():
        for theme, _ in THEMES:
            pages = [sem(p, theme) for p in PAGES]
            track = tok(cfg['track'], theme)
            outside = [sem('bg-canvas', theme)] if cfg['ring'] else pages
            outside_note = 'ring gap (bg-canvas)' if cfg['ring'] else 'page (worst case)'
            exc_dis = 'disabled-below-aa' if state.startswith('disabled') else None

            # 1. the border - neighbor of the page outside and the track inside
            fg_hex = tok(cfg['border'], theme)
            backgrounds = outside + ([track] if track.lower() != fg_hex.lower() else [])
            ratio, bg_hex = worst(fg_hex, backgrounds)
            rows.append(dict(state=state, theme=theme, role='border',
                             token=cfg['border'], fgHex=fg_hex, bgHex=bg_hex, ratio=ratio,
                             floor=NON_TEXT_FLOOR, against=f'{outside_note} + track',
                             exc=cfg['border_exc']))

            # 2. the ring
            if cfg['ring']:
                ink = ring_ink(theme)
                ratio, bg_hex = worst(ink, [sem('bg-canvas', theme)] + pages)
                rows.append(dict(state=state, theme=theme, role='focus ring',
                                 token='switch-ring', fgHex=ink, bgHex=bg_hex, ratio=ratio,
                                 floor=NON_TEXT_FLOOR, against='gap + page', exc=None))

            # 3. the thumb, against the track it is on
            fg_hex = tok(cfg['thumb'], theme)
            rows.append(dict(state=state, theme=theme, role='thumb',
                             token=cfg['thumb'], fgHex=fg_hex, bgHex=track,
                             ratio=cr(fg_hex, track), floor=NON_TEXT_FLOOR,
                             against='track', exc=cfg['thumb_exc']))

            # 4. the label, against the page
            fg_hex = tok(cfg['label'], theme)
            ratio, bg_hex = worst(fg_hex, pages)
            rows.append(dict(state=state, theme=theme, role='label',
                             token=cfg['label'], fgHex=fg_hex, bgHex=bg_hex, ratio=ratio,
                             floor=TEXT_FLOOR, against='page (worst case)', exc=exc_dis))

    for l in rows:
        l['pass'] = l['ratio'] >= l['floor']
        l['codeOnly'] = l['state'] in CODE_ONLY
    return rows


# ------------------------------------------------------------ markup contract
def markup(path):
    """The rules live in contract.json and are checked by tools/contract.py -
    the same file the package's validator reads."""
    if not os.path.exists(path):
        return ([f'HTML not found at {path} - markup contract NOT measured'], 0)
    tree = Tree()
    tree.feed(open(path, encoding='utf-8').read())
    findings, _ = contract.check('switch', tree)
    n = sum(1 for d in walk(tree.root) if has(d, 'al-switch__input'))
    return (findings, n)


def run():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_HTML
    rows = measure()

    fails = [l for l in rows if not l['pass'] and not l['exc']]
    exceptions = [l for l in rows if not l['pass'] and l['exc']]
    passing = [l for l in rows if l['pass']]

    print('=' * 78)
    print('SWITCH ACCESSIBILITY QA')
    print('=' * 78)
    print(f'  combinations measured : {len(rows)}  ({len(STATES)} states x 2 themes x visible roles;'
          f' {len(CODE_ONLY)} states only exist in code)')
    print(f'  pass                  : {len(passing)}')
    print(f'  declared exceptions   : {len(exceptions)}')
    print(f'  fail                  : {len(fails)}')
    print('-' * 78)
    for state in STATES:
        of_state = [l for l in rows if l['state'] == state]
        p = min(of_state, key=lambda l: l['ratio'] / l['floor'])
        mark = 'EXC' if p['exc'] and not p['pass'] else ('ok' if p['pass'] else 'XX')
        code = ' (code only)' if state in CODE_ONLY else ''
        print(f'  {state:<17} worst: {p["role"]:<14} {p["ratio"]:>6}:1 / {p["floor"]}'
              f'  [{p["theme"]}] {mark}{code}')
    print('-' * 78)
    print('effect of the page (what the token layer could not see):')
    for theme, _ in THEMES:
        tr = tok('switch-track', theme)
        sf = sem('bg-surface', theme)
        same = 'SAME color' if tr.lower() == sf.lower() else f'{cr(tr, sf)}:1'
        print(f'  off track x bg-surface band [{theme:<5}]: {same} - '
              f'the boundary is only the border and the thumb')
    print('-' * 78)
    if exceptions:
        print(f'conscious exceptions - {len(exceptions)} measurements, none is a new finding:')
        for key in PENDING:
            n = [l for l in exceptions if l['exc'] == key]
            if n:
                print(f'   {key}: {len(n)} measurements, '
                      f'{min(l["ratio"] for l in n)}:1 to {max(l["ratio"] for l in n)}:1')
    print('-' * 78)

    findings, n = markup(path)
    print(f'markup contract - {os.path.relpath(path, ROOT)}  ({n} switch(es) measured):')
    if findings:
        for a in findings:
            print('   ', a)
    elif n == 0:
        print('    PENDING - no switch in this HTML. Nothing measured is not nothing wrong.')
    else:
        print(f'    the {len(contract.load("switch")["rules"])} rules of contract.json pass on every switch')
    print('-' * 78)

    json.dump({
        'component': 'switch',
        'criterion': 'WCAG 1.4.3 text (label) + 1.4.11 non-text (border, thumb, ring)',
        'floors': {'text': TEXT_FLOOR, 'nonText': NON_TEXT_FLOOR},
        'pages': list(PAGES),
        'markupSource': os.path.relpath(path, ROOT),
        'markupChecked': n,
        'markupPending': n == 0,
        'markupRules': [r.get('why', '') for r in contract.load('switch')['rules']],
        'fails': len(fails),
        'exceptions': {k: len([l for l in exceptions if l['exc'] == k]) for k in PENDING},
        'codeOnlyStates': list(CODE_ONLY),
        'rows': rows,
    }, open(OUT_JSON, 'w'), indent=2, ensure_ascii=False)
    print(f'build/components/switch/a11y.json written ({len(rows)} measurements)')
    print('-' * 78)

    if fails:
        print(f'{len(fails)} COMBINATION(S) FAIL:')
        for l in fails:
            print(f'   {l["state"]}/{l["theme"]} {l["role"]}: {l["ratio"]}:1 < {l["floor"]} '
                  f'(against {l["against"]})')
        return 1
    if findings and n > 0:
        print(f'{len(findings)} MARKUP CONTRACT BREAK(S) - GATE FAILS.')
        return 1
    if n == 0:
        print('rendered contrast: in order. Markup: PENDING, nothing measured yet.')
        return 0
    print('rendered contrast and markup contract: all in order.')
    return 0


if __name__ == '__main__':
    sys.exit(run())
