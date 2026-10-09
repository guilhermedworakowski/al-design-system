"""
Accessibility QA for the Input.

As in the Select, validation is by RENDERED COMBINATION - each color role
against the EFFECTIVE background, not a loose token pair.

WHAT THE EFFECTIVE BACKGROUND CHANGES HERE

  1. THE BORDER CHANGES NEIGHBOR WHEN THE FIELD GETS FOCUS. At rest it touches
     the page, which can be `bg-canvas` OR `bg-surface-raised` (a field inside
     a card or modal) - the worse counts. With focus, the ring draws a 2px gap
     in `bg-canvas` right against the border, and the outer neighbor is always
     `bg-canvas`.

  2. THE RING COLOR COMES FROM THE box-shadow ITSELF - the last hex of the
     composite shadow.

  3. THE BORDER HAS TWO NEIGHBORS: outside the page (or the ring's gap),
     inside the field's fill. The WORSE counts.

  4. READ-ONLY HAS ITS OWN BACKGROUND. Value and affix measure against
     `bg-readonly`, and the placeholder is NOT measured there because the CSS
     makes it transparent (rule 22) - the markup contract below requires the
     read-only field to have a value.

TWO FLOORS: text 4.5:1 (1.4.3); border and ring 3:1 (1.4.11).

THE MARKUP CONTRACT - eight rules, seven from the usage rules and one from the
Select's lesson

    a) every `.al-input__field` has an `id` and a label `<label for>`
       (`.al-input__label`) pointing to it (rules 4 and 28);
    b) a field with `aria-invalid="true"` has `aria-describedby`, the id
       exists and the text inside is not empty - the message is required
       (rules 17, 30);
    c) a field with an affix has `aria-labelledby` with the label's id and the
       id of each affix pointing to it (rule 29);
    d) no field uses `aria-label` when there is a visible label (rule 28);
    e) no field uses `maxlength` - the limit doesn't block typing (rule 14);
    f) every counter declares `aria-live` (rule 30);
    g) a `readonly` field has a non-empty `value` - empty shows "—" (rule 22);
    h) the field's `id` is UNIQUE in the document - otherwise the `<label for>`
       links to the first element with that id. The Select's playground fell
       into that until 0.11.0 (`pg-select` was also the page's id) and no
       other rule saw it.

RUN ORDER - runs AFTER site.py (the same arrangement as the Select). While the
site doesn't have an Input, the JSON comes out with `markupPending: true`.

Run: python3 a11y.py [path.html]     with no argument, measures build/site/index.html
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
INPUT = json.load(open(comp_out('input', 'tokens.json')))

RES = INPUT['resolved']
PENDING = INPUT['pending']
THEMES = (('light', 0), ('dark', 1))

TEXT_FLOOR = 4.5
NON_TEXT_FLOOR = 3.0

DEFAULT_HTML = SITE_HTML
OUT_JSON = comp_out('input', 'a11y.json')

PAGES = ('bg-canvas', 'bg-surface-raised')

BORDER = 'border-below-3-1'
OFF = 'disabled-below-aa'

# state -> roles. `ring=None`: that state draws no ring.
STATES = {
    'default':     dict(border='input-border',          surface='input-bg',          ring=None,               kind='normal',   exc=BORDER),
    'hover':       dict(border='input-border-hover',    surface='input-bg',          ring=None,               kind='normal',   exc=None),
    'focus':       dict(border='input-border-focus',    surface='input-bg',          ring='input-ring',       kind='normal',   exc=None),
    'error':       dict(border='input-border-error',    surface='input-bg',          ring=None,               kind='error',    exc=None),
    'focus-error': dict(border='input-border-error',    surface='input-bg',          ring='input-ring-error', kind='error',    exc=None),
    'disabled':    dict(border='input-border-disabled', surface='input-bg-disabled', ring=None,               kind='off',      exc=OFF),
    'readonly':    dict(border='input-border-readonly', surface='input-bg-readonly', ring=None,               kind='readonly', exc=BORDER),
    # read-only gets focus (rule 23): the ring applies there too
    'focus-readonly': dict(border='input-border-readonly', surface='input-bg-readonly', ring='input-ring', kind='readonly', exc=BORDER),
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

            # 2. ring
            if cfg['ring']:
                ink = ring_ink(cfg['ring'], theme)
                ratio, bg = worst(ink, [sem('bg-canvas', theme)] + pages)
                add(state, theme, 'focus ring', cfg['ring'], ink, bg, ratio,
                    NON_TEXT_FLOOR, 'gap + page', None)

            # 3. inside the field, against the fill
            if cfg['kind'] == 'off':
                inside = [('text', 'input-text-disabled', OFF)]
            elif cfg['kind'] == 'readonly':
                inside = [('value', 'input-text-value', None),
                          ('affix', 'input-affix', None)]
            else:
                inside = [('placeholder', 'input-text-placeholder', None),
                          ('value', 'input-text-value', None),
                          ('affix', 'input-affix', None)]
            for role, name, exc in inside:
                fg = tok(name, theme)
                add(state, theme, role, name, fg, surface, cr(fg, surface),
                    TEXT_FLOOR, 'field fill', exc)

            # 4. outside the field, against the page (worst case)
            if cfg['kind'] == 'off':
                outside_field = [('label', 'input-label-disabled', OFF),
                                 ('optional mark', 'input-label-disabled', OFF),
                                 ('counter', 'input-label-disabled', OFF)]
            elif cfg['kind'] == 'error':
                outside_field = [('label', 'input-label-error', None),
                                 ('optional mark', 'input-optional', None),
                                 ('counter', 'input-counter', None),
                                 ('error message', 'input-help-error', None)]
            else:
                outside_field = [('label', 'input-label', None),
                                 ('optional mark', 'input-optional', None),
                                 ('counter', 'input-counter', None),
                                 ('counter over limit', 'input-counter-error', None),
                                 ('help', 'input-help', None)]
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
    """Strips <style> and <script> before looking for markup - input.css carries
    the ANATOMY in a comment, and the page inlines it. A lesson from the Select."""
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

    fields = re.findall(r'<input\b[^>]*class="[^"]*al-input__field[^"]*"[^>]*>', html)
    labels = re.findall(r'<label\b[^>]*>', html)
    label_of = {}
    affixes_of = {}
    for lb in labels:
        target, cls = attr(lb, 'for'), attr(lb, 'class') or ''
        if not target:
            continue
        if 'al-input__label' in cls:
            label_of[target] = attr(lb, 'id')
        elif 'al-input__affix' in cls:
            affixes_of.setdefault(target, []).append(attr(lb, 'id'))

    for tag in fields:
        cid = attr(tag, 'id')
        if not cid:
            findings.append(f'(a) <input> without id: {tag[:70]}')
            continue
        n_id = len(re.findall(rf'\bid="{re.escape(cid)}"', html))
        if n_id > 1:
            findings.append(f'(h) id "{cid}" appears {n_id} times - the <label for> may link to another element')
        if cid not in label_of:
            findings.append(f'(a) no <label class="al-input__label" for="{cid}">')
        if re.search(r'\baria-label=', tag) and cid in label_of:
            findings.append(f'(d) field "{cid}" uses aria-label when there is a visible label')
        if re.search(r'\bmaxlength=', tag):
            findings.append(f'(e) field "{cid}" uses maxlength - the limit doesn\'t block typing')

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
                        findings.append(f'(b) field "{cid}" is in error and the message "{ref}" is empty')

        affixes = affixes_of.get(cid, [])
        if affixes:
            names = (attr(tag, 'aria-labelledby') or '').split()
            missing = [i for i in [label_of.get(cid)] + affixes if i and i not in names]
            if not names:
                findings.append(f'(c) field "{cid}" has an affix and no aria-labelledby')
            elif missing:
                findings.append(f'(c) field "{cid}": aria-labelledby does not include {missing}')

        if re.search(r'\sreadonly\b', tag):
            if not (attr(tag, 'value') or '').strip():
                findings.append(f'(g) read-only field "{cid}" is empty - use "—" as the value')

    for sp in re.findall(r'<span\b[^>]*class="[^"]*al-input__counter[^"]*"[^>]*>', html):
        if 'aria-live=' not in sp:
            findings.append(f'(f) counter without aria-live: {sp[:60]}')

    return (findings, len(fields))


def run():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_HTML
    rows = measure()

    fails = [l for l in rows if not l['pass'] and not l['exc']]
    exceptions = [l for l in rows if not l['pass'] and l['exc']]
    passing = [l for l in rows if l['pass']]

    print('=' * 78)
    print('INPUT ACCESSIBILITY QA')
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
        print(f'  {state:<15} worst role: {p["role"]:<24} '
              f'{p["ratio"]:>6}:1 / {p["floor"]}  [{p["theme"]}] {mark}')
    print('-' * 78)
    print('effect of layer order (what the token layer could not see):')
    for theme, _ in THEMES:
        rest = next(l for l in rows if l['state'] == 'default' and l['theme'] == theme and l['role'] == 'border')
        foc = next(l for l in rows if l['state'] == 'focus' and l['theme'] == theme and l['role'] == 'border')
        print(f'  border [{theme:<5}] rest {rest["ratio"]}:1 against the page  ->  '
              f'focus {foc["ratio"]}:1 against the ring gap')
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
        print('    the eight rules pass on every field')
    print('-' * 78)

    json.dump({
        'component': 'input',
        'criterion': 'WCAG 1.4.3 text (label, mark, counter, value, affix, help) + '
                     '1.4.11 non-text (border, ring)',
        'floors': {'text': TEXT_FLOOR, 'nonText': NON_TEXT_FLOOR},
        'markupSource': os.path.relpath(path, ROOT),
        'markupChecked': n_fields,
        'markupPending': n_fields == 0,
        'markupRules': [
            'every field has an id and a label <label for> pointing to it',
            'a field in error has aria-invalid="true" and aria-describedby to a non-empty message',
            'a field with an affix has aria-labelledby = label + affixes',
            'no field uses aria-label when there is a visible label',
            'no field uses maxlength',
            'every counter declares aria-live',
            'a read-only field has a value ("—" when empty)',
            'the field id is unique in the document',
        ],
        'fails': len(fails),
        'exceptions': {k: len([l for l in exceptions if l['exc'] == k]) for k in PENDING},
        'layerEffect': [
            {'theme': theme,
             'rest': next(l['ratio'] for l in rows if l['state'] == 'default'
                          and l['theme'] == theme and l['role'] == 'border'),
             'focused': next(l['ratio'] for l in rows if l['state'] == 'focus'
                             and l['theme'] == theme and l['role'] == 'border')}
            for theme, _ in THEMES],
        'rows': rows,
    }, open(OUT_JSON, 'w'), indent=2, ensure_ascii=False)
    print(f'build/components/input/a11y.json written ({len(rows)} measurements)')
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
