"""
Accessibility QA for the Tag.

As in the Button and the Icon Button, validation is by RENDERED COMBINATION -
each type, each status, each theme, against the effective background the
element really has on screen. A type with no fill touches the CANVAS, not
"transparent" - and, since a tag usually lives inside a card, it also touches
bg-surface. Both backgrounds are measured.

WHAT CHANGES COMPARED WITH THE ICON BUTTON

  There, an icon carries the meaning: 3:1 floor, criterion 1.4.11.
  Here a TEXT LABEL carries it: 4.5:1 floor, criterion 1.4.3.
  That is why the Brand status left the scope - white on bg-brand gives
  3.34:1, which passes as an icon and fails as text. Same color, different
  criterion, different decision.

THE PILL BOUNDARY IS NOT A GATE, IT IS A REPORT

  In the Icon Button the component's visible boundary is measured as a gate,
  because with no label the drawing itself is the only thing that says there
  is an actionable element there. Not here: the text says it. The pill outline
  is decoration, and 1.4.11 requires contrast for a graphic element that is
  NEEDED to understand the content - which this one is not.

  The concrete consequence is the filled neutral, which gives 1.32:1 against
  the light canvas. That was measured and accepted in the audit. It stays
  measured and listed here as EXEMPT, never as a failure - and it never leaves
  the report, so nobody "fixes" it thinking it slipped.

THE MARKUP CONTRACT

  The rules are data: src/components/tag/contract.json, checked by
  tools/contract.py here and by the package's validator, from the same
  file. Each rule says why it exists. What this file still checks in
  code is listed there under "manual": what needs the whole page, the
  site's exact shape or its wording.

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
import contract  # noqa: E402
from htmltree import Tree  # noqa: E402
from contrast import cr  # noqa: E402
FOUND = json.load(open(TOKENS_JSON))
TAG = json.load(open(comp_out('tag', 'tokens.json')))

SEM = FOUND['color']['semantic']
RES = TAG['resolved']
THEMES = ('light', 'dark')
TYPES = ('filled', 'outlined')
STATUSES = ('success', 'warning', 'error', 'info', 'neutral')

TEXT_FLOOR = 4.5          # 1.4.3 - the label is text
NON_TEXT_FLOOR = 3.0      # 1.4.11 - the focus ring is a non-text element

# The two backgrounds where a tag really appears. bg-surface matters because a
# tag almost always lives inside a card, table or panel, not loose on the canvas.
UNDERS = ('bg-canvas', 'bg-surface')

SITE = SITE_HTML


def tok(name, theme):
    v = RES[f'tag-{name}']
    return v[theme] if isinstance(v, dict) else v


def sem(name, theme):
    return SEM[name][0 if theme == 'light' else 1]


def effective_bg(kind, status, theme, under):
    """The background the label actually touches. Transparent = the background shows."""
    key = f'{kind}-{status}-bg' if kind == 'filled' else f'{kind}-bg'
    value = tok(key, theme)
    return sem(under, theme) if value == 'transparent' else value


# ─────────────────────────────────────────────── markup contract
OPEN_TAG = re.compile(r'<(\w+)\b([^>]*\bclass="[^"]*\bal-tag\b[^"]*"[^>]*)>')
DISMISS = re.compile(r'<button\b[^>]*\bclass="[^"]*\bal-tag__dismiss\b[^"]*"[^>]*>')


def strip_tags(s):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', s)).strip()


def markup_contract(path):
    """The contract of each .al-tag is in contract.json, checked by
    tools/contract.py: not a control (usage rules 23/24), the X a named
    type="button" with a decorative svg. What stays here reads text against an
    attribute - the `manual` entry: the X's aria-label includes the tag's label
    (rule 25), or several "Remove" buttons sound the same.

    Returns (checked, problems). checked = None when the HTML doesn't emit the
    component yet: that is PENDING, not a pass.
    """
    if not os.path.exists(path):
        return None, [f'{path} does not exist']

    t = Tree()
    t.feed(open(path, encoding='utf-8').read())
    problems, _ = contract.check('tag', t, skip=None)

    html = open(path).read()
    for pat in (r'<style\b.*?</style>', r'<script\b.*?</script>', r'<!--.*?-->'):
        html = re.sub(pat, lambda m: '\n' * m.group(0).count('\n'), html, flags=re.S)

    checked = sum(1 for m in OPEN_TAG.finditer(html) if not re.search(r'\bal-tag__', m.group(2)))
    for m in DISMISS.finditer(html):
        label = re.search(r'aria-label="([^"]*)"', m.group(0))
        if not (label and label.group(1).strip()):
            continue
        # the tag's label is the text between the .al-tag opening and the X
        open_m = None
        for om in OPEN_TAG.finditer(html[:m.start()]):
            if not re.search(r'\bal-tag__', om.group(2)):
                open_m = om
        text = strip_tags(html[open_m.end():m.start()]) if open_m else ''
        if text and text.lower() not in label.group(1).lower():
            line = html.count('\n', 0, m.start()) + 1
            problems.append(
                f'line {line}: aria-label "{label.group(1)}" does not include the label '
                f'"{text}" - in a list of filters, several "Remove" buttons are '
                f'indistinguishable to a screen reader')

    if checked == 0:
        return None, ['no .al-tag in the HTML - the component enters the site with its '
                      'playground; until then this gate stays pending']
    return checked, problems


def write_report(rows, checked, targets, path_html):
    out = {
        'component': 'tag',
        'criterion': 'WCAG 1.4.3 text (label) + 1.4.11 non-text (focus ring)',
        'floors': {'text': TEXT_FLOOR, 'nonText': NON_TEXT_FLOOR},
        'markupSource': os.path.relpath(path_html, ROOT),
        'markupChecked': checked,
        'markupPending': checked is None,
        'fails': sum(1 for r in rows if r[6] is not None and not r[7]),
        'targets': [{'size': s, 'box': b, 'meetsMinimum': b >= 24} for s, b in targets],
        'rows': [{'group': g, 'theme': t, 'label': l, 'fg': fg, 'bg': bg,
                  'ratio': round(ratio, 2), 'floor': floor,
                  'pass': ok, 'exempt': floor is None}
                 for g, t, l, fg, bg, ratio, floor, ok in rows],
    }
    p = comp_out('tag', 'a11y.json')
    json.dump(out, open(p, 'w'), indent=2, ensure_ascii=False)
    return p


def run(path_html):
    rows, failures = [], []

    # ---- 1. label against the effective background (1.4.3, 4.5:1) ----
    for theme in THEMES:
        for kind in TYPES:
            for status in STATUSES:
                fg = tok(f'{kind}-{status}-label', theme)
                for under in UNDERS:
                    bg = effective_bg(kind, status, theme, under)
                    ratio = cr(fg, bg)
                    ok = ratio >= TEXT_FLOOR
                    rows.append(('label', theme, f'{kind} {status} · on {under}',
                                 fg, bg, ratio, TEXT_FLOOR, ok))
                    if not ok:
                        failures.append((theme, kind, status, under, ratio, TEXT_FLOOR))
                    if kind == 'filled':
                        break   # the fill covers the background: measuring once is enough

    # ---- 2. pill boundary: measured, EXEMPT, never a gate ----
    # See the header: the text carries the meaning, so the outline is decoration
    # and 1.4.11 doesn't apply. The neutral at 1.32 is the known case.
    for theme in THEMES:
        for kind in TYPES:
            for status in STATUSES:
                key = f'{kind}-{status}-bg' if kind == 'filled' else f'{kind}-{status}-border'
                edge = tok(key, theme)
                if edge == 'transparent':
                    continue
                for under in UNDERS:
                    rows.append(('boundary', theme, f'{kind} {status} · on {under}',
                                 edge, sem(under, theme), cr(edge, sem(under, theme)),
                                 None, True))

    # ---- 3. the X focus ring against the background (1.4.11, 3:1) ----
    # The ring is composite: 2px of bg-canvas as a gap, then 4px in the focus
    # color. The outer color is what has to stand out from the background.
    for theme in THEMES:
        fg = sem('shadow-focus-default', theme)
        for under in UNDERS:
            bg = sem(under, theme)
            ratio = cr(fg, bg)
            ok = ratio >= NON_TEXT_FLOOR
            rows.append(('focus', theme, f'X ring · on {under}',
                         fg, bg, ratio, NON_TEXT_FLOOR, ok))
            if not ok:
                failures.append((theme, 'dismiss', 'ring', under, ratio, NON_TEXT_FLOOR))

    # ---- 4. the X touch target ----
    targets = [(s, TAG['resolved'][f'tag-{s}-icon-size']) for s in ('sm', 'md')]

    checked, mk_problems = markup_contract(path_html)

    print('=' * 74)
    print('TAG ACCESSIBILITY QA')
    print('=' * 74)
    for group, title in (('label', 'LABEL against the effective background (1.4.3, floor 4.5)'),
                         ('focus', 'X FOCUS RING against the background (1.4.11, floor 3.0)'),
                         ('boundary', 'PILL BOUNDARY - measured, EXEMPT (the text carries the meaning)')):
        sel = [r for r in rows if r[0] == group]
        print(f'\n{title}')
        for _, theme, label, fg, bg, ratio, floor, ok in sel:
            mark = '  ' if floor is None else ('ok' if ok else 'XX')
            floor_s = '  exempt' if floor is None else f'floor {floor}'
            print(f'  {mark} {theme:<5} {label:<40} {fg} on {bg}  {ratio:5.2f}  {floor_s}')

    print('\nX TOUCH TARGET (WCAG 2.5.8, minimum 24px)')
    for size, box in targets:
        state = 'ok' if box >= 24 else 'below the minimum - a conscious, declared exception'
        print(f'     {size:<5} {box}x{box}px  {state}')

    print('\nMARKUP CONTRACT')
    print(f'     source: {os.path.relpath(path_html, ROOT)}')
    if checked is None:
        for p in mk_problems:
            print(f'     pending: {p}')
    else:
        print(f'     {checked} tag(s) checked')
        for p in mk_problems:
            print(f'     PROBLEM: {p}')

    measured = [r for r in rows if r[6] is not None]
    exempt = [r for r in rows if r[6] is None]
    print('-' * 74)
    print(f'{len(measured)} combinations with a floor  |  pass: {len(measured) - len(failures)}  |  '
          f'fail: {len(failures)}  |  exempt, measured: {len(exempt)}')

    path = write_report(rows, checked, targets, path_html)
    print(f'{os.path.relpath(path, ROOT)} written')

    if failures:
        print('-' * 74)
        print(f'{len(failures)} COMBINATION(S) FAIL:')
        for theme, kind, status, under, ratio, floor in failures:
            print(f'   {theme} {kind} {status} on {under}: {ratio:.2f} < {floor}')
        return 1
    if checked is not None and mk_problems:
        print('-' * 74)
        print(f'{len(mk_problems)} MARKUP PROBLEM(S) - gate fails')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(run(sys.argv[1] if len(sys.argv) > 1 else SITE))
