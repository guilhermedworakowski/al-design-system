"""
Accessibility QA for the Radio.

As with the other components, validation is by RENDERED COMBINATION - each
color role against the EFFECTIVE background, not a loose token pair.

THE COMBINATIONS INCLUDE THE ONES THAT ONLY EXIST IN CODE

  Figma has six variants on a single axis. The native input produces more:
  checked + focus, error + focus, error + checked, checked + disabled. They
  were decided with the tokens and are painted by radio.css - so they are
  measured here like any other. The gate doesn't measure what Figma drew; it
  measures what the browser paints.

WHAT THE EFFECTIVE BACKGROUND CHANGES HERE

  1. WHERE THE RADIO IS PLACED. The bare page (`bg-canvas`), a section band
     (`bg-surface`) or a card/modal (`bg-surface-raised`). The WORST counts.

  2. IN THE RADIO, THE BORDER ALWAYS DRAWS THE BOUNDARY - THE DIFFERENCE FROM
     THE CHECKBOX. Checked doesn't paint the background: the orange border sits
     between the page outside and the `bg` ring inside, and it is measured
     against both. The dot is measured against the `bg` ring around it.

  3. WITH FOCUS, THE OUTER NEIGHBOR IS THE RING'S GAP. The ring draws 2px of
     `bg-canvas` right against the circle, wherever it was placed.

  4. THE RING COLOR COMES FROM THE box-shadow ITSELF - the last hex of the
     composite shadow. No parallel definition to drift from the CSS.

TWO FLOORS, ON PURPOSE

  Text (label)                     = 4.5:1 from 1.4.3.
  Non-text (border, dot, ring)     = 3:1 from 1.4.11.

THE MARKUP CONTRACT IS THE OTHER HALF OF THIS GATE

  Six rules, all from the usage rules:

    a) every `.al-radio__input` is a native `<input type="radio">`, inside a
       `<label class="al-radio">`, and nobody writes `role="radio"` (rules 11
       and 25);
    b) every radio has a VISIBLE, non-empty label in `.al-radio__label`, and
       doesn't use `aria-label` (rule 27 - the rule that pays for the 1.57:1
       border);
    c) every radio has a `name`, and each `name` groups TWO options or more - a
       lone radio doesn't exist (rules 3 and 5);
    d) the radios of a `name` live in the same `<fieldset>`, with a non-empty
       `<legend>` - it is the question, which the application builds (rule 6);
    e) the error belongs to the question: `aria-invalid="true"` goes on the
       `<fieldset>`, with `aria-describedby` to an id that exists - never on
       the radio, where ARIA doesn't provide for it (rules 21, 22 and 26);
    f) the dot is decorative: `aria-hidden="true"`.

RUN ORDER - same as the Select and the Checkbox: runs AFTER the HTML it
measures.

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
RADIO = json.load(open(comp_out('radio', 'tokens.json')))

RES = RADIO['resolved']
PENDING = RADIO['pending']
THEMES = (('light', 0), ('dark', 1))

TEXT_FLOOR = 4.5          # 1.4.3
NON_TEXT_FLOOR = 3.0      # 1.4.11

DEFAULT_HTML = SITE_HTML
OUT_JSON = comp_out('radio', 'a11y.json')

PAGES = ('bg-canvas', 'bg-surface', 'bg-surface-raised')

# state -> how the circle is painted.
#   dot:   the dot token, or None if the circle is empty
#   label: the label token
STATES = {
    'default':          dict(border='radio-border',          fill='radio-bg',          dot=None,                 ring=False, label='radio-label',          boundary_exc='border-below-3-1'),
    'hover':            dict(border='radio-border-hover',    fill='radio-bg-hover',    dot=None,                 ring=False, label='radio-label',          boundary_exc=None),
    'focus':            dict(border='radio-border-focus',    fill='radio-bg',          dot=None,                 ring=True,  label='radio-label',          boundary_exc=None),
    'checked':          dict(border='radio-border-checked',  fill='radio-bg',          dot='radio-dot',          ring=False, label='radio-label',          boundary_exc=None),
    'checked-focus':    dict(border='radio-border-checked',  fill='radio-bg',          dot='radio-dot',          ring=True,  label='radio-label',          boundary_exc=None),
    'error':            dict(border='radio-border-error',    fill='radio-bg',          dot=None,                 ring=False, label='radio-label-error',    boundary_exc=None),
    'error-focus':      dict(border='radio-border-error',    fill='radio-bg',          dot=None,                 ring=True,  label='radio-label-error',    boundary_exc=None),
    'error-checked':    dict(border='radio-border-checked',  fill='radio-bg',          dot='radio-dot',          ring=False, label='radio-label-error',    boundary_exc=None),
    'disabled':         dict(border='radio-border-disabled', fill='radio-bg-disabled', dot=None,                 ring=False, label='radio-label-disabled', boundary_exc='disabled-below-aa'),
    'disabled-checked': dict(border='radio-border-disabled', fill='radio-bg-disabled', dot='radio-dot-disabled', ring=False, label='radio-label-disabled', boundary_exc='disabled-below-aa'),
}

# states with no variant in Figma - painted only by the code
CODE_ONLY = ('checked-focus', 'error-focus', 'error-checked', 'disabled-checked')


def tok(name, theme):
    return RES[name][theme]


def sem(name, theme):
    return FOUND['color']['semantic'][name][0 if theme == 'light' else 1]


def ring_ink(theme):
    """The color that paints the ring, read from the box-shadow ITSELF - the last hex."""
    shadow = RES['radio-ring'][theme]
    hexes = re.findall(r'#[0-9a-fA-F]{6}', shadow)
    if not hexes:
        raise ValueError(f'radio-ring ({theme}): box-shadow with no readable color -> {shadow}')
    return hexes[-1]


def worst(fg, backgrounds):
    return min((cr(fg, bg), bg) for bg in backgrounds)


def measure():
    rows = []
    for state, cfg in STATES.items():
        for theme, _ in THEMES:
            pages = [sem(p, theme) for p in PAGES]
            fill = tok(cfg['fill'], theme)
            outside = [sem('bg-canvas', theme)] if cfg['ring'] else pages
            outside_note = 'ring gap (bg-canvas)' if cfg['ring'] else 'page (worst case)'
            exc_dis = 'disabled-below-aa' if state.startswith('disabled') else None

            # 1. the circle's boundary - always the border (header, item 2)
            fg_hex = tok(cfg['border'], theme)
            ratio, bg_hex = worst(fg_hex, outside + [fill])
            rows.append(dict(state=state, theme=theme, role='border',
                             token=cfg['border'], fgHex=fg_hex, bgHex=bg_hex, ratio=ratio,
                             floor=NON_TEXT_FLOOR, against=f'{outside_note} + circle background',
                             exc=cfg['boundary_exc']))

            # 2. the ring
            if cfg['ring']:
                ink = ring_ink(theme)
                ratio, bg_hex = worst(ink, [sem('bg-canvas', theme)] + pages)
                rows.append(dict(state=state, theme=theme, role='focus ring',
                                 token='radio-ring', fgHex=ink, bgHex=bg_hex, ratio=ratio,
                                 floor=NON_TEXT_FLOOR, against='gap + page', exc=None))

            # 3. the dot, against the background ring around it
            if cfg['dot']:
                fg_hex = tok(cfg['dot'], theme)
                rows.append(dict(state=state, theme=theme, role='dot',
                                 token=cfg['dot'], fgHex=fg_hex, bgHex=fill,
                                 ratio=cr(fg_hex, fill), floor=NON_TEXT_FLOOR,
                                 against='circle background', exc=exc_dis))

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
def markup_only(html):
    """Strips <style> and <script> before looking for markup - radio.css carries
    the ANATOMY in a comment, and the QA page inlines it. A lesson from the
    Select."""
    html = re.sub(r'<style\b[^>]*>.*?</style>', '', html, flags=re.S | re.I)
    html = re.sub(r'<script\b[^>]*>.*?</script>', '', html, flags=re.S | re.I)
    return html


def text(fragment):
    return re.sub(r'<[^>]+>', '', fragment).strip()


def markup(path):
    if not os.path.exists(path):
        return ([f'HTML not found at {path} - markup contract NOT measured'], 0)

    html = markup_only(open(path, encoding='utf-8').read())
    findings = []

    inputs = re.findall(r'<input\b[^>]*class="[^"]*al-radio__input[^"]*"[^>]*>', html)
    blocks = re.findall(r'<label\b[^>]*class="[^"]*\bal-radio\b[^"]*"[^>]*>(.*?)</label>',
                        html, flags=re.S)
    inside = sum(len(re.findall(r'al-radio__input', b)) for b in blocks)

    # (a)
    if inside != len(inputs):
        findings.append(f'(a) {len(inputs) - inside} input(s) outside <label class="al-radio">')
    # Only inside a TAG: prose can quote role="radio" in <code> to say it is not used.
    if re.search(r'<[a-zA-Z][^>]*\srole="radio"', html):
        findings.append('(a) role="radio" on the page - the component is the native input')

    names = {}
    for tag in inputs:
        if not re.search(r'\btype="radio"', tag):
            findings.append(f'(a) input without type="radio": {tag[:70]}')
        if 'aria-label' in tag:
            findings.append(f'(b) input uses aria-label when there is a visible label: {tag[:70]}')
        if 'aria-invalid' in tag:
            findings.append(f'(e) aria-invalid on the radio - the error belongs to the question and goes on the fieldset: {tag[:70]}')
        m = re.search(r'\bname="([^"]+)"', tag)
        if not m:
            findings.append(f'(c) radio without a name: {tag[:70]}')
        else:
            names[m.group(1)] = names.get(m.group(1), 0) + 1

    # (b) a visible, non-empty label in each block
    for b in blocks:
        m = re.search(r'<span\b[^>]*al-radio__label[^>]*>(.*?)</span>', b, flags=re.S)
        if not m or not text(m.group(1)):
            findings.append('(b) radio without a visible label in .al-radio__label')

    # (c) each question has two options or more
    for name, n in names.items():
        if n < 2:
            findings.append(f'(c) name="{name}" has a single radio - a lone radio doesn\'t exist')

    # (d) and (e) - per fieldset. Fieldsets don't nest on AL pages; if they ever
    # do, this cut starts lying and needs to become a parser.
    fieldsets = re.findall(r'(<fieldset\b[^>]*>)(.*?)</fieldset>', html, flags=re.S)
    name_in = {}
    for opening, body in fieldsets:
        inside_fs = re.findall(r'<input\b[^>]*al-radio__input[^>]*\bname="([^"]+)"', body)
        if not inside_fs:
            continue
        lg = re.search(r'<legend\b[^>]*>(.*?)</legend>', body, flags=re.S)
        if not lg or not text(lg.group(1)):
            findings.append(f'(d) fieldset with radios and no visible <legend>: {opening[:60]}')
        for name in inside_fs:
            name_in.setdefault(name, set()).add(opening)
        if 'aria-invalid="true"' in opening:
            m = re.search(r'aria-describedby="([^"]+)"', opening)
            if not m:
                findings.append(f'(e) question in error without aria-describedby: {opening[:60]}')
            else:
                for ref in m.group(1).split():
                    if not re.search(rf'\bid="{re.escape(ref)}"', html):
                        findings.append(f'(e) question is described by "{ref}", which does not exist')
    for name in names:
        where = name_in.get(name)
        if not where:
            findings.append(f'(d) name="{name}" outside a <fieldset> - the question is not announced')
        elif len(where) > 1:
            findings.append(f'(d) name="{name}" spread over {len(where)} fieldsets')

    # (f)
    for dot in re.findall(r'<span\b[^>]*al-radio__dot[^>]*>', html):
        if 'aria-hidden="true"' not in dot:
            findings.append(f'(f) dot without aria-hidden="true": {dot[:60]}')

    return (findings, len(inputs))


def run():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_HTML
    rows = measure()

    fails = [l for l in rows if not l['pass'] and not l['exc']]
    exceptions = [l for l in rows if not l['pass'] and l['exc']]
    passing = [l for l in rows if l['pass']]

    print('=' * 78)
    print('RADIO ACCESSIBILITY QA')
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

    findings, n = markup(path)
    print(f'markup contract - {os.path.relpath(path, ROOT)}  ({n} radio(s) measured):')
    if findings:
        for a in findings:
            print('   ', a)
    elif n == 0:
        print('    PENDING - no radio in this HTML. Nothing measured is not nothing wrong.')
    else:
        print('    the six rules pass on every radio')
    print('-' * 78)

    json.dump({
        'component': 'radio',
        'criterion': 'WCAG 1.4.3 text (label) + 1.4.11 non-text (border, dot, ring)',
        'floors': {'text': TEXT_FLOOR, 'nonText': NON_TEXT_FLOOR},
        'pages': list(PAGES),
        'markupSource': os.path.relpath(path, ROOT),
        'markupChecked': n,
        'markupPending': n == 0,
        'markupRules': [
            'native input type="radio" inside <label class="al-radio">, no role="radio"',
            'a visible, non-empty label, no aria-label',
            'every radio has a name, and each name groups two options or more',
            'the radios of a name live in a single <fieldset> with a visible <legend>',
            'error on the fieldset: aria-invalid="true" + an aria-describedby that exists; never on the radio',
            'decorative dot: aria-hidden="true"',
        ],
        'fails': len(fails),
        'exceptions': {k: len([l for l in exceptions if l['exc'] == k]) for k in PENDING},
        'codeOnlyStates': list(CODE_ONLY),
        'rows': rows,
    }, open(OUT_JSON, 'w'), indent=2, ensure_ascii=False)
    print(f'build/components/radio/a11y.json written ({len(rows)} measurements)')
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
