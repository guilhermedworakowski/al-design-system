"""
Accessibility QA for the Textarea.

As in the Select and the Input, validation is by RENDERED COMBINATION - each
color role against the EFFECTIVE background, not a loose token pair.

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

  4. READ-ONLY HAS ITS OWN BACKGROUND. The value measures against
     `bg-readonly`, and the placeholder is NOT measured there because the CSS
     makes it transparent (rule 24) - the markup contract below requires the
     read-only field to have content.

  A difference from the Input: there is no affix, and the box is the
  <textarea> itself - the colors the browser paints come from the same element
  that receives the state.

TWO FLOORS: text 4.5:1 (1.4.3); border and ring 3:1 (1.4.11).

THE MARKUP CONTRACT - eight rules, all from the usage rules

    a) every `.al-textarea__field` has an `id` and a label `<label for>`
       (`.al-textarea__label`) pointing to it (rules 4 and 27);
    b) a field with `aria-invalid="true"` has `aria-describedby`, the id
       exists and the text inside is not empty - the message is required
       (rules 19, 28);
    c) the field is a native `<textarea>` - no other element gets the
       `al-textarea__field` class, and nothing gets `contenteditable` instead
       (rule 26);
    d) no field uses `aria-label` when there is a visible label (rule 27);
    e) no field uses `maxlength` - the limit doesn't block typing (rule 16);
    f) every counter declares `aria-live` (rule 28);
    g) a `readonly` field has non-empty content - empty shows "—" (rule 24);
    h) every field declares `rows` >= 3 (rules 9 and 10) and the `id` is
       UNIQUE in the document (the Select's lesson until 0.11.0).

RUN ORDER - runs AFTER site.py (the same arrangement as the Select). While the
site doesn't have a Textarea, the JSON comes out with `markupPending: true`.

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
TA = json.load(open(comp_out('textarea', 'tokens.json')))

RES = TA['resolved']
PENDING = TA['pending']
THEMES = (('light', 0), ('dark', 1))

TEXT_FLOOR = 4.5
NON_TEXT_FLOOR = 3.0

DEFAULT_HTML = SITE_HTML
OUT_JSON = comp_out('textarea', 'a11y.json')

PAGES = ('bg-canvas', 'bg-surface-raised')

BORDER = 'border-below-3-1'
OFF = 'disabled-below-aa'

# state -> roles. `ring=None`: that state draws no ring.
STATES = {
    'default':     dict(border='textarea-border',          surface='textarea-bg',          ring=None,               kind='normal',   exc=BORDER),
    'hover':       dict(border='textarea-border-hover',    surface='textarea-bg',          ring=None,               kind='normal',   exc=None),
    'focus':       dict(border='textarea-border-focus',    surface='textarea-bg',          ring='textarea-ring',       kind='normal',   exc=None),
    'error':       dict(border='textarea-border-error',    surface='textarea-bg',          ring=None,               kind='error',    exc=None),
    'focus-error': dict(border='textarea-border-error',    surface='textarea-bg',          ring='textarea-ring-error', kind='error',    exc=None),
    'disabled':    dict(border='textarea-border-disabled', surface='textarea-bg-disabled', ring=None,               kind='off',      exc=OFF),
    'readonly':    dict(border='textarea-border-readonly', surface='textarea-bg-readonly', ring=None,               kind='readonly', exc=BORDER),
    # read-only gets focus (rule 24): the ring applies there too
    'focus-readonly': dict(border='textarea-border-readonly', surface='textarea-bg-readonly', ring='textarea-ring', kind='readonly', exc=BORDER),
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
                inside = [('text', 'textarea-text-disabled', OFF)]
            elif cfg['kind'] == 'readonly':
                inside = [('value', 'textarea-text-value', None)]
            else:
                inside = [('placeholder', 'textarea-text-placeholder', None),
                          ('value', 'textarea-text-value', None)]
            for role, name, exc in inside:
                fg = tok(name, theme)
                add(state, theme, role, name, fg, surface, cr(fg, surface),
                    TEXT_FLOOR, 'field fill', exc)

            # 4. outside the field, against the page (worst case)
            if cfg['kind'] == 'off':
                outside_field = [('label', 'textarea-label-disabled', OFF),
                                 ('optional mark', 'textarea-label-disabled', OFF),
                                 ('counter', 'textarea-label-disabled', OFF)]
            elif cfg['kind'] == 'error':
                outside_field = [('label', 'textarea-label-error', None),
                                 ('optional mark', 'textarea-optional', None),
                                 ('counter', 'textarea-counter', None),
                                 ('error message', 'textarea-help-error', None)]
            else:
                outside_field = [('label', 'textarea-label', None),
                                 ('optional mark', 'textarea-optional', None),
                                 ('counter', 'textarea-counter', None),
                                 ('counter over limit', 'textarea-counter-error', None),
                                 ('help', 'textarea-help', None)]
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
    """Strips <style> and <script> before looking for markup - textarea.css
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

    # (c) the field class can only be on a <textarea>
    for m in re.finditer(r'<(\w+)\b[^>]*class="[^"]*al-textarea__field[^"]*"[^>]*>', html):
        if m.group(1).lower() != 'textarea':
            findings.append(f'(c) al-textarea__field on a <{m.group(1)}> - use a native <textarea>')
    if re.search(r'class="[^"]*al-textarea[^"]*"[^>]*contenteditable|contenteditable[^>]*class="[^"]*al-textarea', html):
        findings.append('(c) contenteditable inside the Textarea - use a native <textarea>')

    fields = re.findall(r'(<textarea\b[^>]*class="[^"]*al-textarea__field[^"]*"[^>]*>)(.*?)</textarea>',
                        html, flags=re.S)
    label_of = {}
    for lb in re.findall(r'<label\b[^>]*>', html):
        target, cls = attr(lb, 'for'), attr(lb, 'class') or ''
        if target and 'al-textarea__label' in cls:
            label_of[target] = attr(lb, 'id')

    for tag, content in fields:
        cid = attr(tag, 'id')
        if not cid:
            findings.append(f'(a) <textarea> without id: {tag[:70]}')
            continue
        n_id = len(re.findall(rf'\bid="{re.escape(cid)}"', html))
        if n_id > 1:
            findings.append(f'(h) id "{cid}" appears {n_id} times - the <label for> may link to another element')
        rows = attr(tag, 'rows')
        if not rows or not rows.isdigit() or int(rows) < 3:
            findings.append(f'(h) field "{cid}" without rows >= 3 (has: {rows})')
        if cid not in label_of:
            findings.append(f'(a) no <label class="al-textarea__label" for="{cid}">')
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

        if re.search(r'\sreadonly\b', tag) and not content.strip():
            findings.append(f'(g) read-only field "{cid}" is empty - use "—" as the content')

    for sp in re.findall(r'<span\b[^>]*class="[^"]*al-textarea__counter[^"]*"[^>]*>', html):
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
    print('TEXTAREA ACCESSIBILITY QA')
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
        'component': 'textarea',
        'criterion': 'WCAG 1.4.3 text (label, mark, counter, value, help) + '
                     '1.4.11 non-text (border, ring)',
        'floors': {'text': TEXT_FLOOR, 'nonText': NON_TEXT_FLOOR},
        'markupSource': os.path.relpath(path, ROOT),
        'markupChecked': n_fields,
        'markupPending': n_fields == 0,
        'markupRules': [
            'every field has an id and a label <label for> pointing to it',
            'a field in error has aria-invalid="true" and aria-describedby to a non-empty message',
            'the field is a native <textarea>, never contenteditable',
            'no field uses aria-label when there is a visible label',
            'no field uses maxlength',
            'every counter declares aria-live',
            'a read-only field has content ("—" when empty)',
            'every field declares rows >= 3 and the id is unique in the document',
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
    print(f'build/components/textarea/a11y.json written ({len(rows)} measurements)')
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
