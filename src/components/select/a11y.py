"""
Accessibility QA for the Select.

As in the Button, Icon Button, Icon, Tag and Avatar, validation is by RENDERED
COMBINATION - each color role against the EFFECTIVE background, not a loose
token pair.

WHAT THE EFFECTIVE BACKGROUND CHANGES HERE, THAT THE TOKEN LAYER COULDN'T SEE

  1. THE BORDER CHANGES NEIGHBOR WHEN THE FIELD GETS FOCUS. At rest it touches
     the page, which can be `bg-canvas` OR `bg-surface-raised` (a field inside
     a card or modal) - the gate measures the worse of the two. With focus,
     the ring draws a 2px gap in `bg-canvas` right against the border, so the
     outer neighbor becomes `bg-canvas` ALWAYS, wherever the field was placed.
     That is layer order, not a token pair: it only shows up by measuring the
     rendered output.

  2. THE RING COLOR COMES FROM THE box-shadow ITSELF. `select-ring` resolves to
     the composite shadow ("0 0 0 2px #FFF, 0 0 0 4px #FC5000"), and this gate
     reads the LAST hex in the string - the color that actually paints the
     ring. There is no parallel definition to drift from the CSS.

  3. THE BORDER HAS TWO NEIGHBORS. Outside the page (or the ring's gap),
     inside the field's fill. The WORSE of the two counts: a border that
     disappears on the inside draws no boundary at all.

TWO FLOORS, ON PURPOSE

  Text (label, mark, value, help) = 4.5:1 from 1.4.3.
  Non-text (border, chevron, ring) = 3:1 from 1.4.11.
  Each role against its own floor, never against the easier one.

THE MARKUP CONTRACT IS THE OTHER HALF OF THIS GATE

  In a form field, almost everything that goes wrong is markup, not style -
  and markup only exists in the rendered output. The usage rules:

    a) every `.al-select__field` has an `id`, and there is a `<label for>`
       pointing to it (rules 5 and 24);
    b) a field with `aria-invalid="true"` has `aria-describedby`, and the id it
       points to really exists in the document (rule 26);
    c) the placeholder is the first <option> with `value=""` and `selected`,
       never an invented attribute (rule 12);
    d) the chevron is decorative: `aria-hidden="true"` and `focusable="false"`
       on its own tag - the meaning lives in the label (icon.css contract);
    e) no field uses `aria-label` when there is a visible label, because the
       announced name has to match the text the person reads (rule 24);
    f) the field's `id` is UNIQUE in the document. Without it the `<label for>`
       links to the first element with that id, which may not be the field -
       that is what happened on the site's playground until 0.11.0: the field
       was called `pg-select`, the same id as the page's container, and the
       label pointed to the page. Rules (a) to (e) all passed; only counting
       the id caught it.

  A rule written on a page goes stale; a measured rule breaks the build.

RUN ORDER - this gate runs AFTER site.py

  The same arrangement the Icon already uses, for the same mechanical reason:
  the gate needs the emitted HTML to enforce markup, and the site needs the
  `a11y.json` this gate writes to build the Accessibility tab. The two
  generations converge in one pass - there is no loop. While the site doesn't
  have a Select yet, the JSON comes out with `markupPending: true` and the gate
  says so out loud.

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
FOUND = json.load(open(TOKENS_JSON))
SELECT = json.load(open(comp_out('select', 'tokens.json')))

RES = SELECT['resolved']
PENDING = SELECT['pending']
THEMES = (('light', 0), ('dark', 1))

TEXT_FLOOR = 4.5          # 1.4.3
NON_TEXT_FLOOR = 3.0      # 1.4.11

DEFAULT_HTML = SITE_HTML
OUT_JSON = comp_out('select', 'a11y.json')

# Where the field can be placed. The border at rest has to hold up against
# both: the bare page and a raised surface (card, modal).
PAGES = ('bg-canvas', 'bg-surface-raised')

# state -> roles. `ring=None` means that state draws no ring.
STATES = {
    'default':     {'border': 'select-border',          'surface': 'select-bg',          'ring': None,                'error': False, 'off': False},
    'hover':       {'border': 'select-border-hover',    'surface': 'select-bg',          'ring': None,                'error': False, 'off': False},
    'active':      {'border': 'select-border-active',   'surface': 'select-bg',          'ring': None,                'error': False, 'off': False},
    'focus':       {'border': 'select-border-focus',    'surface': 'select-bg',          'ring': 'select-ring',       'error': False, 'off': False},
    'error':       {'border': 'select-border-error',    'surface': 'select-bg',          'ring': None,                'error': True,  'off': False},
    'focus-error': {'border': 'select-border-error',    'surface': 'select-bg',          'ring': 'select-ring-error', 'error': True,  'off': False},
    'disabled':    {'border': 'select-border-disabled', 'surface': 'select-bg-disabled', 'ring': None,                'error': False, 'off': True},
}


def tok(name, theme):
    """Hex of a Select token in the requested theme."""
    return RES[name][theme]


def sem(name, theme):
    return FOUND['color']['semantic'][name][0 if theme == 'light' else 1]


def ring_ink(name, theme):
    """The color that paints the ring, read from the box-shadow the CSS itself
    emits - the last hex in the composite shadow. No parallel definition to
    drift."""
    shadow = RES[name][theme]
    hexes = re.findall(r'#[0-9a-fA-F]{6}', shadow)
    if not hexes:
        raise ValueError(f'{name} ({theme}): box-shadow with no readable color -> {shadow}')
    return hexes[-1]


def worst(fg, backgrounds):
    """The worst ratio between a foreground and the surfaces it touches."""
    measures = [(cr(fg, bg), bg) for bg in backgrounds]
    return min(measures)


def measure():
    rows = []
    for state, cfg in STATES.items():
        for theme, _ in THEMES:
            surface = tok(cfg['surface'], theme)
            pages = [sem(p, theme) for p in PAGES]

            # 1. the border. Outside: the ring's gap when there is focus,
            #    otherwise the page (worst case). Inside: the field's fill.
            if cfg['ring']:
                outside = [sem('bg-canvas', theme)]
                outside_note = 'ring gap (bg-canvas)'
            else:
                outside = pages
                outside_note = 'page (worse of canvas / surface-raised)'
            fg_hex = tok(cfg['border'], theme)
            ratio, bg_hex = worst(fg_hex, outside + [surface])
            rows.append(dict(
                state=state, theme=theme, role='border', ratio=ratio,
                token=f'select-{cfg["border"].split("select-")[-1]}'
                      if cfg['border'].startswith('select-') else cfg['border'],
                fgHex=fg_hex, bgHex=bg_hex,
                floor=NON_TEXT_FLOOR, against=f'{outside_note} + fill',
                exc='border-below-3-1' if cfg['border'] in
                    ('select-border', 'select-border-disabled') else None))

            # 2. the ring, when there is one. Inside its own gap in bg-canvas,
            #    outside the page.
            if cfg['ring']:
                ink = ring_ink(cfg['ring'], theme)
                ratio, bg_hex = worst(ink, [sem('bg-canvas', theme)] + pages)
                rows.append(dict(
                    state=state, theme=theme, role='focus ring', ratio=ratio,
                    token=cfg['ring'], fgHex=ink, bgHex=bg_hex,
                    floor=NON_TEXT_FLOOR, against='gap + page', exc=None))

            # 3. what lives INSIDE the field, against its fill
            if cfg['off']:
                inside = [('text', 'select-text-disabled', TEXT_FLOOR, 'disabled-below-aa'),
                          ('chevron', 'select-icon-disabled', NON_TEXT_FLOOR, 'disabled-below-aa')]
            else:
                inside = [('placeholder', 'select-text-placeholder', TEXT_FLOOR, None),
                          ('value', 'select-text-value', TEXT_FLOOR, None),
                          ('chevron', 'select-icon', NON_TEXT_FLOOR, None)]
            for role, token_name, floor, exc in inside:
                fg_hex = tok(token_name, theme)
                rows.append(dict(
                    state=state, theme=theme, role=role,
                    token=token_name, fgHex=fg_hex, bgHex=surface,
                    ratio=cr(fg_hex, surface),
                    floor=floor, against='field fill', exc=exc))

            # 4. what lives OUTSIDE the field, against the page (worst case)
            if cfg['off']:
                outside_field = [('label', 'select-label-disabled', 'disabled-below-aa'),
                                 ('optional mark', 'select-label-disabled', 'disabled-below-aa')]
            elif cfg['error']:
                outside_field = [('label', 'select-label-error', None),
                                 ('optional mark', 'select-optional', None),
                                 ('help', 'select-help-error', None)]
            else:
                outside_field = [('label', 'select-label', None),
                                 ('optional mark', 'select-optional', None),
                                 ('help', 'select-help', None)]
            for role, token_name, exc in outside_field:
                fg_hex = tok(token_name, theme)
                ratio, bg_hex = worst(fg_hex, pages)
                rows.append(dict(
                    state=state, theme=theme, role=role,
                    token=token_name, fgHex=fg_hex, bgHex=bg_hex, ratio=ratio,
                    floor=TEXT_FLOOR, against='page (worst case)', exc=exc))

    for l in rows:
        l['pass'] = l['ratio'] >= l['floor']
    return rows


# ------------------------------------------------------------ markup contract
def markup_only(html):
    """Strips <style> and <script> before looking for markup.

    It isn't overcaution: select.css carries the ANATOMY in a header comment,
    with an example <select> and <label> inside. The QA page inlines that CSS,
    so without this cleanup the gate would measure the comment's example as if
    it were a real field - and it PASSED, because the example is correct. A
    gate that passes by reading a comment also fails by reading a comment.
    """
    html = re.sub(r'<style\b[^>]*>.*?</style>', '', html, flags=re.S | re.I)
    html = re.sub(r'<script\b[^>]*>.*?</script>', '', html, flags=re.S | re.I)
    return html


def markup(path):
    """Reads the rendered HTML and enforces the rules. Returns (findings, count)."""
    if not os.path.exists(path):
        return ([f'HTML not found at {path} - markup contract NOT measured'], 0)

    html = markup_only(open(path, encoding='utf-8').read())
    findings = []

    fields = re.findall(r'<select\b[^>]*class="[^"]*al-select__field[^"]*"[^>]*>', html)
    label_ids = dict(re.findall(r'<label\b[^>]*for="([^"]+)"[^>]*>(.*?)</label>', html, flags=re.S))

    for tag in fields:
        m_id = re.search(r'\bid="([^"]+)"', tag)
        if not m_id:
            findings.append(f'(a) <select> without id: {tag[:70]}')
            continue
        sid = m_id.group(1)
        n_id = len(re.findall(rf'\bid="{re.escape(sid)}"', html))
        if n_id > 1:
            findings.append(f'(f) id "{sid}" appears {n_id} times - the <label for> may link to another element')
        if sid not in label_ids:
            findings.append(f'(a) no <label for="{sid}"> points to this field')
        if 'aria-label' in tag and sid in label_ids:
            findings.append(f'(e) field "{sid}" uses aria-label when there is a visible label')
        if re.search(r'aria-invalid="true"', tag):
            m_desc = re.search(r'aria-describedby="([^"]+)"', tag)
            if not m_desc:
                findings.append(f'(b) field "{sid}" is in error and has no aria-describedby')
            else:
                for ref in m_desc.group(1).split():
                    if not re.search(rf'\bid="{re.escape(ref)}"', html):
                        findings.append(f'(b) field "{sid}" is described by "{ref}", which does not exist')

    # (c) placeholder: the first empty <option> has to be selected
    for block in re.findall(r'<select\b[^>]*al-select__field.*?</select>', html, flags=re.S):
        empty = re.findall(r'<option\b[^>]*value=""[^>]*>', block)
        for op in empty:
            if 'selected' not in op:
                findings.append(f'(c) <option value=""> without selected: {op[:60]}')

    # (d) the chevron is decorative
    for svg in re.findall(r'<svg\b[^>]*al-select__chevron[^>]*>', html):
        if 'aria-hidden="true"' not in svg:
            findings.append(f'(d) chevron without aria-hidden="true": {svg[:60]}')
        if 'focusable="false"' not in svg:
            findings.append(f'(d) chevron without focusable="false": {svg[:60]}')

    return (findings, len(fields))


def run():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_HTML
    rows = measure()

    fails = [l for l in rows if not l['pass'] and not l['exc']]
    exceptions = [l for l in rows if not l['pass'] and l['exc']]
    passing = [l for l in rows if l['pass']]

    print('=' * 78)
    print('SELECT ACCESSIBILITY QA')
    print('=' * 78)
    print(f'  combinations measured : {len(rows)}  (7 states x 2 themes x visible roles)')
    print(f'  pass                  : {len(passing)}')
    print(f'  declared exceptions   : {len(exceptions)}')
    print(f'  fail                  : {len(fails)}')
    print('-' * 78)

    for state in STATES:
        of_state = [l for l in rows if l['state'] == state]
        worst_l = min(of_state, key=lambda l: l['ratio'] / l['floor'])
        mark = 'EXC' if worst_l['exc'] and not worst_l['pass'] else ('ok' if worst_l['pass'] else 'XX')
        print(f'  {state:<12} worst role: {worst_l["role"]:<15} '
              f'{worst_l["ratio"]:>6}:1 / {worst_l["floor"]}  [{worst_l["theme"]}] {mark}')

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
                span = f'{min(l["ratio"] for l in n)}:1 to {max(l["ratio"] for l in n)}:1'
                print(f'   {key}: {len(n)} measurements, {span}')
    print('-' * 78)

    findings, n_fields = markup(path)
    print(f'markup contract - {os.path.relpath(path, ROOT)}  '
          f'({n_fields} field(s) measured):')
    if findings:
        for a in findings:
            print('   ', a)
    elif n_fields == 0:
        # zero fields is not zero problems: it is nothing measured. Saying
        # "pass" here would be the worst lie a gate can tell.
        print('    PENDING - no field in this HTML. Run site/site.py and call')
        print('    this gate again (see RUN ORDER in the header).')
    else:
        print('    the six rules pass on every field')
    print('-' * 78)

    # The site reads this file to build the Accessibility tab.
    json.dump({
        'component': 'select',
        'criterion': 'WCAG 1.4.3 text (label, mark, value, help) + '
                     '1.4.11 non-text (border, chevron, ring)',
        'floors': {'text': TEXT_FLOOR, 'nonText': NON_TEXT_FLOOR},
        'markupSource': os.path.relpath(path, ROOT),
        'markupChecked': n_fields,
        'markupPending': n_fields == 0,
        'markupRules': [
            'every field has an id and a <label for> pointing to it',
            'a field in error has aria-invalid="true" and an aria-describedby that exists',
            'the placeholder is the first selected <option value="">',
            'the chevron is decorative: aria-hidden="true" and focusable="false"',
            'no field uses aria-label when there is a visible label',
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
    print(f'build/components/select/a11y.json written ({len(rows)} measurements)')
    print('-' * 78)

    if fails:
        print(f'{len(fails)} COMBINATION(S) FAIL:')
        for l in fails:
            print(f'   {l["state"]}/{l["theme"]} {l["role"]}: {l["ratio"]}:1 < {l["floor"]} '
                  f'(against {l["against"]})')
        return 1
    if findings:
        if n_fields == 0:
            print('markup contract PENDING - the site does not emit a Select yet.')
            print('Run site/site.py and call this gate again (see RUN ORDER in the header).')
            return 0
        print(f'{len(findings)} MARKUP CONTRACT BREAK(S) - GATE FAILS.')
        return 1

    if n_fields == 0:
        print('rendered contrast: in order. Markup: PENDING, nothing measured yet.')
        return 0
    print('rendered contrast and markup contract: all in order.')
    return 0


if __name__ == '__main__':
    sys.exit(run())
