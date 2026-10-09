"""
Accessibility QA for the Checkbox.

As with the other components, validation is by RENDERED COMBINATION - each
color role against the EFFECTIVE background, not a loose token pair.

THE COMBINATIONS INCLUDE THE ONES THAT ONLY EXIST IN CODE

  Figma has seven variants on a single axis. The native input produces more:
  checked + focus, error + checked, checked + disabled. They were decided with
  the tokens and are painted by checkbox.css - so they are measured here like
  any other. The gate doesn't measure what Figma drew; it measures what the
  browser paints.

WHAT THE EFFECTIVE BACKGROUND CHANGES HERE

  1. WHERE THE CHECKBOX IS PLACED. The bare page (`bg-canvas`), a section band
     (`bg-surface`) or a card/modal (`bg-surface-raised`). The Checkbox lives
     in settings lists, which usually sit on `bg-surface` - that is why it
     comes in here, besides the two pages the Select measures. The WORST
     counts.

  2. WHAT DRAWS THE BOUNDARY CHANGES WITH THE STATE. Unchecked, it is the
     border - against the page outside and the fill inside. Checked, border
     and fill are the same color, so the boundary is the whole FILL against
     the page. Measuring the checked box's border against its own background
     would give 1:1 and fail a perfectly visible box.

  3. WITH FOCUS, THE OUTER NEIGHBOR IS THE RING'S GAP. The ring draws 2px of
     `bg-canvas` right against the box, wherever it was placed.

  4. THE RING COLOR COMES FROM THE box-shadow ITSELF - the last hex of the
     composite shadow. No parallel definition to drift from the CSS.

TWO FLOORS, ON PURPOSE

  Text (label)                          = 4.5:1 from 1.4.3.
  Non-text (border, box, glyph, ring)   = 3:1 from 1.4.11.

THE MARKUP CONTRACT IS THE OTHER HALF OF THIS GATE

  Five rules, all from the usage rules:

    a) every `.al-checkbox__input` is a native `<input type="checkbox">`,
       inside a `<label class="al-checkbox">` (rules 9 and 21);
    b) every checkbox has a VISIBLE, non-empty label in `.al-checkbox__label`,
       and doesn't use `aria-label` (rule 23 - the rule that pays for the
       1.57:1 border);
    c) a checkbox with `aria-invalid="true"` has `aria-describedby`, and the
       id it points to exists in the document (rules 19 and 22 - the error
       text belongs to the form, but it has to exist);
    d) the glyphs are decorative: `aria-hidden="true"` and `focusable="false"`;
    e) nobody writes `indeterminate` as an HTML attribute: it doesn't exist,
       and the browser ignores it silently. Indeterminate only through JS
       (rule 8).

RUN ORDER - same as the Select: runs AFTER the HTML it measures.

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
CHECKBOX = json.load(open(comp_out('checkbox', 'tokens.json')))

RES = CHECKBOX['resolved']
PENDING = CHECKBOX['pending']
THEMES = (('light', 0), ('dark', 1))

TEXT_FLOOR = 4.5          # 1.4.3
NON_TEXT_FLOOR = 3.0      # 1.4.11

DEFAULT_HTML = SITE_HTML
OUT_JSON = comp_out('checkbox', 'a11y.json')

PAGES = ('bg-canvas', 'bg-surface', 'bg-surface-raised')

# state -> how the box is painted.
#   checked: the boundary is the fill, not the border (see the header, item 2)
#   glyph:   the check/dash token, or None if the box is empty
#   label:   the label token
STATES = {
    'default':           dict(border='checkbox-border',          fill='checkbox-bg',          checked=False, glyph=None,                     ring=False, label='checkbox-label',          boundary_exc='border-below-3-1'),
    'hover':             dict(border='checkbox-border-hover',    fill='checkbox-bg-hover',    checked=False, glyph=None,                     ring=False, label='checkbox-label',          boundary_exc=None),
    'focus':             dict(border='checkbox-border-focus',    fill='checkbox-bg',          checked=False, glyph=None,                     ring=True,  label='checkbox-label',          boundary_exc=None),
    'checked':           dict(border='checkbox-border-checked',  fill='checkbox-bg-checked',  checked=True,  glyph='checkbox-icon',          ring=False, label='checkbox-label',          boundary_exc=None),
    'checked-focus':     dict(border='checkbox-border-checked',  fill='checkbox-bg-checked',  checked=True,  glyph='checkbox-icon',          ring=True,  label='checkbox-label',          boundary_exc=None),
    'indeterminate':     dict(border='checkbox-border-checked',  fill='checkbox-bg-checked',  checked=True,  glyph='checkbox-icon',          ring=False, label='checkbox-label',          boundary_exc=None),
    'error':             dict(border='checkbox-border-error',    fill='checkbox-bg',          checked=False, glyph=None,                     ring=False, label='checkbox-label-error',    boundary_exc=None),
    'error-focus':       dict(border='checkbox-border-error',    fill='checkbox-bg',          checked=False, glyph=None,                     ring=True,  label='checkbox-label-error',    boundary_exc=None),
    'error-checked':     dict(border='checkbox-border-checked',  fill='checkbox-bg-checked',  checked=True,  glyph='checkbox-icon',          ring=False, label='checkbox-label-error',    boundary_exc=None),
    'disabled':          dict(border='checkbox-border-disabled', fill='checkbox-bg-disabled', checked=False, glyph=None,                     ring=False, label='checkbox-label-disabled', boundary_exc='disabled-below-aa'),
    'disabled-checked':  dict(border='checkbox-border-disabled', fill='checkbox-bg-disabled', checked=False, glyph='checkbox-icon-disabled', ring=False, label='checkbox-label-disabled', boundary_exc='disabled-below-aa'),
}

# states with no variant in Figma - painted only by the code
CODE_ONLY = ('checked-focus', 'error-focus', 'error-checked', 'disabled-checked')


def tok(name, theme):
    return RES[name][theme]


def sem(name, theme):
    return FOUND['color']['semantic'][name][0 if theme == 'light' else 1]


def ring_ink(theme):
    """The color that paints the ring, read from the box-shadow ITSELF - the last hex."""
    shadow = RES['checkbox-ring'][theme]
    hexes = re.findall(r'#[0-9a-fA-F]{6}', shadow)
    if not hexes:
        raise ValueError(f'checkbox-ring ({theme}): box-shadow with no readable color -> {shadow}')
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

            # 1. the box boundary
            if cfg['checked']:
                ratio, bg_hex = worst(fill, outside)
                rows.append(dict(state=state, theme=theme, role='checked box',
                                 token=cfg['fill'], fgHex=fill, bgHex=bg_hex, ratio=ratio,
                                 floor=NON_TEXT_FLOOR, against=outside_note, exc=None))
            else:
                fg_hex = tok(cfg['border'], theme)
                ratio, bg_hex = worst(fg_hex, outside + [fill])
                rows.append(dict(state=state, theme=theme, role='border',
                                 token=cfg['border'], fgHex=fg_hex, bgHex=bg_hex, ratio=ratio,
                                 floor=NON_TEXT_FLOOR, against=f'{outside_note} + fill',
                                 exc=cfg['boundary_exc']))

            # 2. the ring
            if cfg['ring']:
                ink = ring_ink(theme)
                ratio, bg_hex = worst(ink, [sem('bg-canvas', theme)] + pages)
                rows.append(dict(state=state, theme=theme, role='focus ring',
                                 token='checkbox-ring', fgHex=ink, bgHex=bg_hex, ratio=ratio,
                                 floor=NON_TEXT_FLOOR, against='gap + page', exc=None))

            # 3. the glyph, against the box fill
            if cfg['glyph']:
                fg_hex = tok(cfg['glyph'], theme)
                exc = 'disabled-below-aa' if state.startswith('disabled') else None
                rows.append(dict(state=state, theme=theme,
                                 role='dash' if state == 'indeterminate' else 'check',
                                 token=cfg['glyph'], fgHex=fg_hex, bgHex=fill,
                                 ratio=cr(fg_hex, fill), floor=NON_TEXT_FLOOR,
                                 against='box fill', exc=exc))

            # 4. the label, against the page
            fg_hex = tok(cfg['label'], theme)
            ratio, bg_hex = worst(fg_hex, pages)
            exc = 'disabled-below-aa' if state.startswith('disabled') else None
            rows.append(dict(state=state, theme=theme, role='label',
                             token=cfg['label'], fgHex=fg_hex, bgHex=bg_hex, ratio=ratio,
                             floor=TEXT_FLOOR, against='page (worst case)', exc=exc))

    for l in rows:
        l['pass'] = l['ratio'] >= l['floor']
        l['codeOnly'] = l['state'] in CODE_ONLY
    return rows


# ------------------------------------------------------------ markup contract
def markup_only(html):
    """Strips <style> and <script> before looking for markup - checkbox.css
    carries the ANATOMY in a comment, and the QA page inlines it. A lesson from
    the Select."""
    html = re.sub(r'<style\b[^>]*>.*?</style>', '', html, flags=re.S | re.I)
    html = re.sub(r'<script\b[^>]*>.*?</script>', '', html, flags=re.S | re.I)
    return html


def markup(path):
    if not os.path.exists(path):
        return ([f'HTML not found at {path} - markup contract NOT measured'], 0)

    html = markup_only(open(path, encoding='utf-8').read())
    findings = []

    inputs = re.findall(r'<input\b[^>]*class="[^"]*al-checkbox__input[^"]*"[^>]*>', html)
    blocks = re.findall(r'<label\b[^>]*class="[^"]*\bal-checkbox\b[^"]*"[^>]*>(.*?)</label>',
                        html, flags=re.S)
    inside = sum(len(re.findall(r'al-checkbox__input', b)) for b in blocks)

    # (a)
    if inside != len(inputs):
        findings.append(f'(a) {len(inputs) - inside} input(s) outside <label class="al-checkbox">')
    for tag in inputs:
        if not re.search(r'\btype="checkbox"', tag):
            findings.append(f'(a) input without type="checkbox": {tag[:70]}')
        if 'aria-label' in tag:
            findings.append(f'(b) input uses aria-label when there is a visible label: {tag[:70]}')
        if re.search(r'\sindeterminate(\s|=|>|/)', tag):
            findings.append(f'(e) indeterminate attribute in the markup - it doesn\'t exist, use JS: {tag[:70]}')
        if 'aria-invalid="true"' in tag:
            m = re.search(r'aria-describedby="([^"]+)"', tag)
            if not m:
                findings.append(f'(c) checkbox in error without aria-describedby: {tag[:70]}')
            else:
                for ref in m.group(1).split():
                    if not re.search(rf'\bid="{re.escape(ref)}"', html):
                        findings.append(f'(c) checkbox is described by "{ref}", which does not exist')
    # Only inside a TAG: the site's Accessibility tab writes role="checkbox" in
    # prose, inside <code>, precisely to say it is not used.
    if re.search(r'<[a-zA-Z][^>]*\srole="checkbox"', html):
        findings.append('(a) role="checkbox" on the page - the component is the native input')

    # (b) a visible, non-empty label in each block
    for b in blocks:
        m = re.search(r'<span\b[^>]*al-checkbox__label[^>]*>(.*?)</span>', b, flags=re.S)
        if not m or not re.sub(r'<[^>]+>', '', m.group(1)).strip():
            findings.append('(b) checkbox without a visible label in .al-checkbox__label')

    # (d)
    for svg in re.findall(r'<svg\b[^>]*al-checkbox__(?:check|dash)[^>]*>', html):
        if 'aria-hidden="true"' not in svg:
            findings.append(f'(d) glyph without aria-hidden="true": {svg[:60]}')
        if 'focusable="false"' not in svg:
            findings.append(f'(d) glyph without focusable="false": {svg[:60]}')

    return (findings, len(inputs))


def run():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_HTML
    rows = measure()

    fails = [l for l in rows if not l['pass'] and not l['exc']]
    exceptions = [l for l in rows if not l['pass'] and l['exc']]
    passing = [l for l in rows if l['pass']]

    print('=' * 78)
    print('CHECKBOX ACCESSIBILITY QA')
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
    print(f'markup contract - {os.path.relpath(path, ROOT)}  ({n} checkbox(es) measured):')
    if findings:
        for a in findings:
            print('   ', a)
    elif n == 0:
        print('    PENDING - no checkbox in this HTML. Nothing measured is not nothing wrong.')
    else:
        print('    the five rules pass on every checkbox')
    print('-' * 78)

    json.dump({
        'component': 'checkbox',
        'criterion': 'WCAG 1.4.3 text (label) + 1.4.11 non-text (border, box, glyph, ring)',
        'floors': {'text': TEXT_FLOOR, 'nonText': NON_TEXT_FLOOR},
        'pages': list(PAGES),
        'markupSource': os.path.relpath(path, ROOT),
        'markupChecked': n,
        'markupPending': n == 0,
        'markupRules': [
            'native input type="checkbox" inside <label class="al-checkbox">',
            'a visible, non-empty label, no aria-label',
            'in error: aria-invalid="true" + an aria-describedby that exists',
            'decorative glyphs: aria-hidden="true" and focusable="false"',
            'indeterminate never as an HTML attribute - only through JS',
        ],
        'fails': len(fails),
        'exceptions': {k: len([l for l in exceptions if l['exc'] == k]) for k in PENDING},
        'codeOnlyStates': list(CODE_ONLY),
        'rows': rows,
    }, open(OUT_JSON, 'w'), indent=2, ensure_ascii=False)
    print(f'build/components/checkbox/a11y.json written ({len(rows)} measurements)')
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
