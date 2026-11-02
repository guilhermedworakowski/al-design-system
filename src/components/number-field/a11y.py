"""
Accessibility QA for the Number field.

As in the Input, validation is by RENDERED COMBINATION - each color role
against the EFFECTIVE background, not a loose token pair.

WHAT THE EFFECTIVE BACKGROUND CHANGES HERE

  1. THE BORDER CHANGES NEIGHBOR WHEN THE FIELD GETS FOCUS. At rest it touches
     the page (`bg-canvas` or `bg-surface-raised` - the worse counts). With
     focus, the ring draws a 2px gap in `bg-canvas` right against the border.

  2. THE RING COLOR COMES FROM THE box-shadow ITSELF - the last hex of the
     composite shadow.

  3. THE STEPPERS ARE GRAPHIC: 3:1 floor (1.4.11), against the field fill.
     They have no ring - they are out of the Tab order (rule 13). The one at
     the limit is a disabled button: declared exception.

  4. READ-ONLY HAS NO STEPPERS (rule 17), so there is no stepper measurement
     on `bg-readonly`.

TWO FLOORS: text 4.5:1 (1.4.3); border, rings and steppers 3:1 (1.4.11).

THE MARKUP CONTRACT

  The rules are data: src/components/number-field/contract.json, checked by
  tools/contract.py here and by the package's validator, from the same
  file. Each rule says why it exists. What this file still checks in
  code is listed there under "manual": what needs the whole page, the
  site's exact shape or its wording.

RUN ORDER - runs AFTER site.py. With no argument it measures
build/site/index.html; while the site doesn't have a Number field, the JSON
comes out with `markupPending: true`.

Run: python3 a11y.py [path.html]
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'tools'))
from paths import ROOT, TOKENS_JSON, SITE_HTML, comp_out  # noqa: E402
import contract  # noqa: E402
from contrast import cr2 as cr  # noqa: E402
FOUND = json.load(open(TOKENS_JSON))
NF = json.load(open(comp_out('number-field', 'tokens.json')))

RES = NF['resolved']
PENDING = NF['pending']
THEMES = (('light', 0), ('dark', 1))

TEXT_FLOOR = 4.5
NON_TEXT_FLOOR = 3.0

DEFAULT_HTML = SITE_HTML
OUT_JSON = comp_out('number-field', 'a11y.json')

PAGES = ('bg-canvas', 'bg-surface-raised')

BORDER = 'border-below-3-1'
OFF = 'disabled-below-aa'

P = 'number-field'
STATES = {
    'default':     dict(border=f'{P}-border',          surface=f'{P}-bg',          ring=None,            kind='normal', exc=BORDER),
    'hover':       dict(border=f'{P}-border-hover',    surface=f'{P}-bg',          ring=None,            kind='normal', exc=None),
    'focus':       dict(border=f'{P}-border-focus',    surface=f'{P}-bg',          ring=f'{P}-ring',       kind='normal', exc=None),
    'error':       dict(border=f'{P}-border-error',    surface=f'{P}-bg',          ring=None,            kind='error',  exc=None),
    'focus-error': dict(border=f'{P}-border-error',    surface=f'{P}-bg',          ring=f'{P}-ring-error', kind='error',  exc=None),
    'readonly':    dict(border=f'{P}-border-readonly', surface=f'{P}-bg-readonly', ring=None,            kind='readonly', exc=BORDER),
    'disabled':    dict(border=f'{P}-border-disabled', surface=f'{P}-bg-disabled', ring=None,            kind='off',    exc=OFF),
}


def tok(name, theme):
    return RES[name][theme]


def sem(name, theme):
    return FOUND['color']['semantic'][name][0 if theme == 'light' else 1]


def ring_ink(name, theme):
    hexes = re.findall(r'#[0-9a-fA-F]{6}', RES[name][theme])
    if not hexes:
        raise ValueError(f'{name} ({theme}): box-shadow with no readable color')
    return hexes[-1]


def worst(fg, backgrounds):
    return min((cr(fg, bg), bg) for bg in backgrounds)


def measure():
    rows = []

    def add(state, theme, role, token, fg, bg, ratio, floor, against, exc):
        rows.append(dict(state=state, theme=theme, role=role, token=token,
                         fgHex=fg, bgHex=bg, ratio=ratio, floor=floor,
                         against=against, exc=exc))

    for state, cfg in STATES.items():
        for theme, _ in THEMES:
            surface = tok(cfg['surface'], theme)
            pages = [sem(p, theme) for p in PAGES]

            # 1. border
            if cfg['ring']:
                outside, note = [sem('bg-canvas', theme)], 'ring gap (bg-canvas)'
            else:
                outside, note = pages, 'page (worse of canvas / surface-raised)'
            fg = tok(cfg['border'], theme)
            ratio, bg = worst(fg, outside + [surface])
            add(state, theme, 'border', cfg['border'], fg, bg, ratio,
                NON_TEXT_FLOOR, f'{note} + fill', cfg['exc'])

            # 2. the field ring
            if cfg['ring']:
                ink = ring_ink(cfg['ring'], theme)
                ratio, bg = worst(ink, [sem('bg-canvas', theme)] + pages)
                add(state, theme, 'field ring', cfg['ring'], ink, bg, ratio,
                    NON_TEXT_FLOOR, 'gap + page', None)

            # 3. inside the field
            if cfg['kind'] == 'off':
                inside = [('value', f'{P}-text-disabled', TEXT_FLOOR, OFF),
                          ('stepper', f'{P}-stepper-icon-disabled', NON_TEXT_FLOOR, OFF)]
            elif cfg['kind'] == 'readonly':
                inside = [('value', f'{P}-text-value', TEXT_FLOOR, None)]
            else:
                inside = [('value', f'{P}-text-value', TEXT_FLOOR, None),
                          ('stepper', f'{P}-stepper-icon', NON_TEXT_FLOOR, None),
                          ('stepper at limit', f'{P}-stepper-icon-disabled', NON_TEXT_FLOOR, OFF)]
            for role, name, floor, exc in inside:
                fg = tok(name, theme)
                add(state, theme, role, name, fg, surface, cr(fg, surface),
                    floor, 'field fill', exc)

            # 4. outside the field, against the page (worst case)
            if cfg['kind'] == 'off':
                outside_field = [('label', f'{P}-label-disabled', OFF)]
            elif cfg['kind'] == 'error':
                outside_field = [('label', f'{P}-label-error', None),
                                 ('error message', f'{P}-help-error', None)]
            else:
                outside_field = [('label', f'{P}-label', None),
                                 ('help', f'{P}-help', None)]
            for role, name, exc in outside_field:
                fg = tok(name, theme)
                ratio, bg = worst(fg, pages)
                add(state, theme, role, name, fg, bg, ratio,
                    TEXT_FLOOR, 'page (worst case)', exc)

    for l in rows:
        l['pass'] = l['ratio'] >= l['floor']
    return rows


# ------------------------------------------------------------ markup contract
def markup_only(html):
    """Strips <style> and <script> - the CSS carries the MARKUP CONTRACT in a comment."""
    html = re.sub(r'<style\b[^>]*>.*?</style>', '', html, flags=re.S | re.I)
    html = re.sub(r'<script\b[^>]*>.*?</script>', '', html, flags=re.S | re.I)
    return html


def attr(tag, name):
    m = re.search(rf'\b{name}="([^"]*)"', tag)
    return m.group(1) if m else None


def markup(path):
    """The rules of each field and its steppers are in contract.json
    (tools/contract.py checks them). What stays here ties each stepper to its
    own field: the `manual` entries of contract.json."""
    findings, n, html = contract.audit('number-field', path, '.al-number-field__field')
    if not html:
        return (findings, n)
    html = markup_only(html)
    for block in re.findall(r'<div\b[^>]*class="[^"]*al-number-field__control[^"]*"[^>]*>.*?</div>', html, flags=re.S):
        tag = re.search(r'<input\b[^>]*al-number-field__field[^>]*>', block)
        if not tag:
            continue
        tag, cid = tag.group(0), attr(tag.group(0), 'id')
        for btag in re.findall(r'<button\b[^>]*al-number-field__step[^>]*>', block):
            if attr(btag, 'aria-controls') != cid:
                findings.append(f'[stepper-points-to-field] stepper of "{cid}": aria-controls does not point to its own field')
            if re.search(r'\sdisabled\b', tag) and not re.search(r'\sdisabled\b', btag):
                findings.append(f'[disabled-together] field "{cid}" is disabled and a stepper is not')
    return (findings, n)


def run():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_HTML
    rows = measure()

    fails = [l for l in rows if not l['pass'] and not l['exc']]
    exceptions = [l for l in rows if not l['pass'] and l['exc']]
    passing = [l for l in rows if l['pass']]

    print('=' * 78)
    print('NUMBER FIELD ACCESSIBILITY QA')
    print('=' * 78)
    print(f'  combinations measured : {len(rows)}  ({len(STATES)} states x 2 themes x visible roles)')
    print(f'  pass                  : {len(passing)}')
    print(f'  declared exceptions   : {len(exceptions)}')
    print(f'  fail                  : {len(fails)}')
    print('-' * 78)
    for state in STATES:
        of_state = [l for l in rows if l['state'] == state and (l['pass'] or not l['exc'])]
        if not of_state:
            continue
        p = min(of_state, key=lambda l: l['ratio'] / l['floor'])
        mark = 'ok' if p['pass'] else 'XX'
        print(f'  {state:<12} worst role: {p["role"]:<18} '
              f'{p["ratio"]:>6}:1 / {p["floor"]}  [{p["theme"]}] {mark}')
    print('-' * 78)
    if exceptions:
        print(f'conscious exceptions - {len(exceptions)} measurements, none is a new finding:')
        for key in PENDING:
            n = [l for l in exceptions if l['exc'] == key]
            if n:
                print(f'   {key}: {len(n)} measurements, '
                      f'{min(l["ratio"] for l in n)}:1 to {max(l["ratio"] for l in n)}:1')
    print('-' * 78)

    findings, n_fields = markup(path)
    print(f'markup contract - {os.path.relpath(path, ROOT)}  ({n_fields} field(s) measured):')
    if n_fields == 0 and not findings:
        print('    PENDING - no field in this HTML. Run site/site.py and call')
        print('    this gate again (see RUN ORDER in the header).')
    elif findings:
        for a in findings:
            print('   ', a)
    else:
        print(f'    the {len(contract.whys("number-field"))} rules of contract.json pass on every field')
    print('-' * 78)

    json.dump({
        'component': 'number-field',
        'criterion': 'WCAG 1.4.3 text (label, value, help) + 1.4.11 non-text (border, ring, steppers)',
        'floors': {'text': TEXT_FLOOR, 'nonText': NON_TEXT_FLOOR},
        'markupSource': os.path.relpath(path, ROOT),
        'markupChecked': n_fields,
        'markupPending': n_fields == 0,
        'fails': len(fails),
        'exceptions': {k: len([l for l in exceptions if l['exc'] == k]) for k in PENDING},
        'rows': rows,
    }, open(OUT_JSON, 'w'), indent=2, ensure_ascii=False)
    print(f'build/components/number-field/a11y.json written ({len(rows)} measurements)')
    print('-' * 78)

    if fails:
        print(f'{len(fails)} COMBINATION(S) FAIL:')
        for l in fails:
            print(f'   {l["state"]}/{l["theme"]} {l["role"]}: {l["ratio"]}:1 < {l["floor"]} '
                  f'(against {l["against"]})')
        return 1
    if findings and n_fields:
        print(f'{len(findings)} MARKUP CONTRACT BREAK(S) - GATE FAILS.')
        return 1
    if n_fields == 0:
        print('rendered contrast: in order. Markup: PENDING, nothing measured yet.')
        return 0
    print('rendered contrast and markup contract: all in order.')
    return 0


if __name__ == '__main__':
    sys.exit(run())
