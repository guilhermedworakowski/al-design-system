"""
Accessibility QA for the Password.

As in the Input, validation is by RENDERED COMBINATION - each color role
against the EFFECTIVE background, not a loose token pair.

WHAT THE EFFECTIVE BACKGROUND CHANGES HERE

  1. THE BORDER CHANGES NEIGHBOR WHEN THE FIELD GETS FOCUS. At rest it touches
     the page (`bg-canvas` or `bg-surface-raised` - the worse counts). With
     focus, the ring draws a 2px gap in `bg-canvas` right against the border.

  2. THE RING COLOR COMES FROM THE box-shadow ITSELF - the last hex of the
     composite shadow.

  3. THE EYE RING LIVES INSIDE THE FIELD. Its 2px gap is `bg-canvas`, not the
     field background: in dark it is a #181818 outline inside #3E3E3E
     (accepted with the tokens). The ring is measured against BOTH things that
     touch its color - the gap and the field fill - and the worse counts. It
     is always the default ring, including with the field in error (rule 19).

  4. THE EYE IS GRAPHIC: 3:1 floor (1.4.11), against the field fill.

TWO FLOORS: text 4.5:1 (1.4.3); border, rings and eye 3:1 (1.4.11).

THE MARKUP CONTRACT - ten usage rules, plus the unique id

    a) every `.al-password__field` has an `id` and a label `<label for>`
       pointing to it (rules 4 and 29);
    b) a field with `aria-invalid="true"` has `aria-describedby`, the id
       exists and the text inside is not empty (rules 8 and 29);
    c) no field uses `aria-label` when there is a visible label (rule 29);
    d) no field uses `maxlength` (rule 12);
    e) the field starts as `type="password"` (rule 13);
    f) the field declares `autocomplete` current-password or new-password,
       `spellcheck="false"` and `autocapitalize="none"` (rules 25-26);
    g) the eye is a `<button type="button">` with `aria-controls` = the field
       id and a non-empty `aria-label` (rule 28);
    h) the eye icons are `aria-hidden="true" focusable="false"` (Icon contract);
    i) a disabled field -> the eye button is `disabled` too (rule 20);
    j) the field `id` is UNIQUE in the document (the Select's lesson, 0.11.0).

RUN ORDER - runs AFTER site.py (the same arrangement as the Input). With no
argument it measures build/site/index.html; while the site doesn't have a
Password, the JSON comes out with `markupPending: true`.

Run: python3 a11y.py [path.html]
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
FOUND = json.load(open(TOKENS_JSON))
PW = json.load(open(comp_out('password', 'tokens.json')))

RES = PW['resolved']
PENDING = PW['pending']
THEMES = (('light', 0), ('dark', 1))

TEXT_FLOOR = 4.5
NON_TEXT_FLOOR = 3.0

DEFAULT_HTML = SITE_HTML
OUT_JSON = comp_out('password', 'a11y.json')

PAGES = ('bg-canvas', 'bg-surface-raised')

BORDER = 'border-below-3-1'
OFF = 'disabled-below-aa'

# state -> roles. `ring`: the FIELD ring. `toggle_ring`: the eye can be focused
# in that state (not in disabled: a disabled button doesn't get focus).
STATES = {
    'default':     dict(border='password-border',          surface='password-bg',          ring=None,                  kind='normal', exc=BORDER, toggle_ring=True),
    'hover':       dict(border='password-border-hover',    surface='password-bg',          ring=None,                  kind='normal', exc=None,   toggle_ring=False),
    'focus':       dict(border='password-border-focus',    surface='password-bg',          ring='password-ring',       kind='normal', exc=None,   toggle_ring=False),
    'error':       dict(border='password-border-error',    surface='password-bg',          ring=None,                  kind='error',  exc=None,   toggle_ring=True),
    'focus-error': dict(border='password-border-error',    surface='password-bg',          ring='password-ring-error', kind='error',  exc=None,   toggle_ring=False),
    'disabled':    dict(border='password-border-disabled', surface='password-bg-disabled', ring=None,                  kind='off',    exc=OFF,    toggle_ring=False),
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

            # 3. the eye ring - inside the field
            if cfg['toggle_ring']:
                ink = ring_ink('password-toggle-ring', theme)
                ratio, bg = worst(ink, [sem('bg-canvas', theme), surface])
                add(state, theme, 'eye ring', 'password-toggle-ring', ink, bg, ratio,
                    NON_TEXT_FLOOR, 'gap (bg-canvas) + fill', None)

            # 4. inside the field
            if cfg['kind'] == 'off':
                inside = [('text', 'password-text-disabled', TEXT_FLOOR, OFF),
                          ('eye', 'password-toggle-icon-disabled', NON_TEXT_FLOOR, OFF)]
            else:
                inside = [('placeholder', 'password-text-placeholder', TEXT_FLOOR, None),
                          ('value', 'password-text-value', TEXT_FLOOR, None),
                          ('eye', 'password-toggle-icon', NON_TEXT_FLOOR, None)]
            for role, name, floor, exc in inside:
                fg = tok(name, theme)
                add(state, theme, role, name, fg, surface, cr(fg, surface),
                    floor, 'field fill', exc)

            # 5. outside the field, against the page (worst case)
            if cfg['kind'] == 'off':
                outside_field = [('label', 'password-label-disabled', OFF)]
            elif cfg['kind'] == 'error':
                outside_field = [('label', 'password-label-error', None),
                                 ('error message', 'password-help-error', None)]
            else:
                outside_field = [('label', 'password-label', None)]
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
    """Strips <style> and <script> before looking for markup - password.css
    carries the ANATOMY in a comment, and the page inlines it. A lesson from the
    Select."""
    html = re.sub(r'<style\b[^>]*>.*?</style>', '', html, flags=re.S | re.I)
    html = re.sub(r'<script\b[^>]*>.*?</script>', '', html, flags=re.S | re.I)
    return html


def attr(tag, name):
    m = re.search(rf'\b{name}="([^"]*)"', tag)
    return m.group(1) if m else None


def markup(path):
    if not os.path.exists(path):
        return ([f'HTML not found at {path} - markup contract NOT measured'], 0)

    html = markup_only(open(path, encoding='utf-8').read())
    findings = []

    label_of = {}
    for lb in re.findall(r'<label\b[^>]*>', html):
        if 'al-password__label' in (attr(lb, 'class') or '') and attr(lb, 'for'):
            label_of[attr(lb, 'for')] = True

    # each whole component, to match the field and the button of the same block
    blocks = re.findall(r'<div class="al-password">(.*?)</div>\s*(?:<p\b[^>]*>.*?</p>\s*)?</div>',
                        html, flags=re.S)
    n_fields = 0
    for block in blocks:
        field = re.search(r'<input\b[^>]*al-password__field[^>]*>', block)
        if not field:
            continue
        n_fields += 1
        tag = field.group(0)
        cid = attr(tag, 'id')
        if not cid:
            findings.append(f'(a) <input> without id: {tag[:70]}')
            continue
        n_id = len(re.findall(rf'\bid="{re.escape(cid)}"', html))
        if n_id > 1:
            findings.append(f'(j) id "{cid}" appears {n_id} times')
        if cid not in label_of:
            findings.append(f'(a) no <label class="al-password__label" for="{cid}">')
        if re.search(r'\baria-label=', tag) and cid in label_of:
            findings.append(f'(c) field "{cid}" uses aria-label when there is a visible label')
        if re.search(r'\bmaxlength=', tag):
            findings.append(f'(d) field "{cid}" uses maxlength')
        if attr(tag, 'type') != 'password':
            findings.append(f'(e) field "{cid}" does not start as type="password"')
        if attr(tag, 'autocomplete') not in ('current-password', 'new-password'):
            findings.append(f'(f) field "{cid}": autocomplete must be current-password or new-password')
        if attr(tag, 'spellcheck') != 'false' or attr(tag, 'autocapitalize') != 'none':
            findings.append(f'(f) field "{cid}": missing spellcheck="false" or autocapitalize="none"')

        if 'aria-invalid="true"' in tag:
            desc = attr(tag, 'aria-describedby')
            if not desc:
                findings.append(f'(b) field "{cid}" is in error and has no aria-describedby')
            else:
                for ref in desc.split():
                    m = re.search(rf'<(\w+)\b[^>]*\bid="{re.escape(ref)}"[^>]*>(.*?)</\1>', html, flags=re.S)
                    if not m:
                        findings.append(f'(b) field "{cid}" is described by "{ref}", which does not exist')
                    elif not re.sub(r'<[^>]+>', '', m.group(2)).strip():
                        findings.append(f'(b) field "{cid}": the message "{ref}" is empty')

        button = re.search(r'<button\b[^>]*al-password__toggle[^>]*>(.*?)</button>', block, flags=re.S)
        if not button:
            findings.append(f'(g) field "{cid}" without the eye button')
            continue
        btag = re.match(r'<button\b[^>]*>', button.group(0)).group(0)
        if attr(btag, 'type') != 'button':
            findings.append(f'(g) eye of "{cid}" without type="button" - it would submit the form')
        if attr(btag, 'aria-controls') != cid:
            findings.append(f'(g) eye of "{cid}": aria-controls does not point to the field')
        if not (attr(btag, 'aria-label') or '').strip():
            findings.append(f'(g) eye of "{cid}" without aria-label')
        for svg in re.findall(r'<svg\b[^>]*>', button.group(1)):
            if 'aria-hidden="true"' not in svg or 'focusable="false"' not in svg:
                findings.append(f'(h) eye icon of "{cid}" without aria-hidden/focusable')
        if re.search(r'\sdisabled\b', tag) and not re.search(r'\sdisabled\b', btag):
            findings.append(f'(i) field "{cid}" is disabled and the eye is not')

    return (findings, n_fields)


def run():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_HTML
    rows = measure()

    fails = [l for l in rows if not l['pass'] and not l['exc']]
    exceptions = [l for l in rows if not l['pass'] and l['exc']]
    passing = [l for l in rows if l['pass']]

    print('=' * 78)
    print('PASSWORD ACCESSIBILITY QA')
    print('=' * 78)
    print(f'  combinations measured : {len(rows)}  ({len(STATES)} states x 2 themes x visible roles)')
    print(f'  pass                  : {len(passing)}')
    print(f'  declared exceptions   : {len(exceptions)}')
    print(f'  fail                  : {len(fails)}')
    print('-' * 78)
    for state in STATES:
        of_state = [l for l in rows if l['state'] == state]
        p = min(of_state, key=lambda l: l['ratio'] / l['floor'])
        mark = 'EXC' if p['exc'] and not p['pass'] else ('ok' if p['pass'] else 'XX')
        print(f'  {state:<12} worst role: {p["role"]:<18} '
              f'{p["ratio"]:>6}:1 / {p["floor"]}  [{p["theme"]}] {mark}')
    print('-' * 78)
    print('eye ring (it lives inside the field - what the token layer could not see):')
    for theme, _ in THEMES:
        l = next(l for l in rows if l['state'] == 'default' and l['theme'] == theme
                 and l['role'] == 'eye ring')
        print(f'  [{theme:<5}] {l["ratio"]}:1 against {l["bgHex"]} (worse of gap and fill)')
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
        print('    the ten rules pass on every field')
    print('-' * 78)

    json.dump({
        'component': 'password',
        'criterion': 'WCAG 1.4.3 text (label, value, placeholder, error) + '
                     '1.4.11 non-text (border, rings, eye)',
        'floors': {'text': TEXT_FLOOR, 'nonText': NON_TEXT_FLOOR},
        'markupSource': os.path.relpath(path, ROOT),
        'markupChecked': n_fields,
        'markupPending': n_fields == 0,
        'markupRules': [
            'every field has an id and a label <label for> pointing to it',
            'a field in error has aria-invalid="true" and aria-describedby to a non-empty message',
            'no field uses aria-label when there is a visible label',
            'no field uses maxlength',
            'the field starts as type="password"',
            'autocomplete current/new-password, spellcheck="false", autocapitalize="none"',
            'the eye is a <button type="button"> with aria-controls and aria-label',
            'eye icons with aria-hidden="true" focusable="false"',
            'disabled field -> disabled eye',
            'the field id is unique in the document',
        ],
        'fails': len(fails),
        'exceptions': {k: len([l for l in exceptions if l['exc'] == k]) for k in PENDING},
        'rows': rows,
    }, open(OUT_JSON, 'w'), indent=2, ensure_ascii=False)
    print(f'build/components/password/a11y.json written ({len(rows)} measurements)')
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
