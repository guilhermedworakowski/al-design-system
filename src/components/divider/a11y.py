"""
Accessibility QA for the Divider.

As with the other components, validation is by RENDERED COMBINATION - the line
against the EFFECTIVE background it is placed on, not a loose token pair.

WHAT THE EFFECTIVE BACKGROUND CHANGES HERE

  The token layer measures the line against the canvas (`bg-canvas`) and the
  section band (`bg-surface`). The system's third surface is measured here
  too: card and modal (`bg-surface-raised`) - exactly where the divider shows
  up the most (card footer, menu groups). Each one counts.

TWO JUDGMENTS, NOT ONE

  1. 3:1 floor from 1.4.11. The line falls below it on every background, and
     that is the declared exception `line-below-3-1`, backed by rule 8 (the
     line is never the only clue of the grouping). It does not fail.
  2. INVISIBLE line - line color identical to the background. The exception
     covers a subtle line; it does not cover a line that doesn't exist on
     screen. This fails.

THE MARKUP CONTRACT IS THE OTHER HALF OF THIS GATE

  Usage rules from guidelines.md, measured on the emitted HTML:

    a) `.al-divider` is `<hr>` or `<li role="separator">` - no painted <div>
       (rules 12 and 15);
    b) `<hr>` is never a direct child of <ul>/<ol> - only <li> fits there
       (rule 15);
    c) the separator in a list is empty - no text in the divider (rule 11);
    d) an announced vertical one has aria-orientation="vertical"; a
       horizontal one doesn't (rule 14);
    e) never focusable or clickable: no tabindex, no onclick, no role other
       than `separator` (rule 16);
    f) decorative is aria-hidden="true" and nothing else (rule 13);
    g) no divider at the start or end of the container, nor two in a row
       (rule 4).

RUN ORDER - same as the others: runs AFTER the HTML it measures.

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
from contrast import cr  # noqa: E402
from htmltree import Tree, walk  # noqa: E402
FOUND = json.load(open(TOKENS_JSON))
DIVIDER = json.load(open(comp_out('divider', 'tokens.json')))

SEM = FOUND['color']['semantic']
RES = DIVIDER['resolved']
THEMES = ('light', 'dark')

NON_TEXT_FLOOR = 3.0      # 1.4.11
EXC = 'line-below-3-1'

DEFAULT_HTML = SITE_HTML
OUT_JSON = comp_out('divider', 'a11y.json')

PAGES = ('bg-canvas', 'bg-surface', 'bg-surface-raised')


def sem(name, theme):
    """tokens.json stores the semantic as [light, dark]."""
    v = SEM[name]
    return v[THEMES.index(theme)] if isinstance(v, list) else v[theme]


# ─────────────────────────────────────────────── contrast
def contrast_rows():
    rows = []
    for theme in THEMES:
        fg = RES['divider-color'][theme]
        for page in PAGES:
            bg = sem(page, theme)
            ratio = round(cr(fg, bg), 2)
            invisible = fg.lower() == bg.lower()
            rows.append({
                'theme': theme, 'bg': page, 'fg': fg, 'bgHex': bg,
                'ratio': ratio, 'floor': NON_TEXT_FLOOR,
                'pass': ratio >= NON_TEXT_FLOOR,
                'invisible': invisible,
                'exception': None if ratio >= NON_TEXT_FLOOR or invisible else EXC,
            })
    return rows


# ─────────────────────────────────────────────── markup
def is_divider(node):
    return 'al-divider' in node['attrs'].get('class', '').split()


def markup_contract(path):
    if not os.path.exists(path):
        return None, [f'{path} does not exist']
    t = Tree()
    t.feed(open(path, encoding='utf-8').read())

    checked, problems = 0, []
    for n in walk(t.root):
        if not is_divider(n):
            continue
        checked += 1
        a, tag, ln = n['attrs'], n['tag'], n['line']
        classes = a.get('class', '').split()
        hidden = a.get('aria-hidden')
        parent = n['parent']

        # (a) the right element
        if tag not in ('hr', 'li'):
            problems.append(f'line {ln}: .al-divider on <{tag}> - use <hr> (or '
                            f'<li role="separator"> in a list) (rules 12 and 15)')
        if tag == 'li' and a.get('role') != 'separator' and hidden != 'true':
            problems.append(f'line {ln}: <li class="al-divider"> without role="separator" '
                            f'- the screen reader would announce an empty item (rule 15)')

        # (b) loose <hr> in a list
        if tag == 'hr' and parent['tag'] in ('ul', 'ol'):
            problems.append(f'line {ln}: <hr> as a direct child of <{parent["tag"]}> - '
                            f'invalid HTML, use <li role="separator"> (rule 15)')

        # (c) no text
        if tag == 'li' and (n['text'].strip() or n['kids']):
            problems.append(f'line {ln}: separator with content - the divider takes '
                            f'no text; name the group with a heading (rule 11)')

        # (d) orientation
        vertical = 'al-divider--vertical' in classes
        orient = a.get('aria-orientation')
        if vertical and hidden != 'true' and orient != 'vertical':
            problems.append(f'line {ln}: announced vertical without aria-orientation='
                            f'"vertical" - the separator is horizontal by default (rule 14)')
        if not vertical and orient == 'vertical':
            problems.append(f'line {ln}: aria-orientation="vertical" on a horizontal '
                            f'divider - the announcement diverges from the screen (rule 14)')

        # (e) never focusable or clickable
        if 'tabindex' in a:
            problems.append(f'line {ln}: tabindex on the divider - a focusable separator '
                            f'is a Window Splitter, another component (rule 16)')
        if any(k.startswith('on') for k in a):
            problems.append(f'line {ln}: event handler on the divider - it is never '
                            f'clickable (rule 16)')
        role = a.get('role')
        if role and role != 'separator':
            problems.append(f'line {ln}: role="{role}" - the divider\'s only role is '
                            f'separator; decorative is aria-hidden (rules 13 and 16)')

        # (f) decorative
        if hidden is not None and hidden != 'true':
            problems.append(f'line {ln}: aria-hidden="{hidden}" - decorative is '
                            f'"true"; announced has no attribute (rule 13)')

        # (g) position in the container
        siblings = [k for k in parent['kids']]
        i = siblings.index(n)
        if i == 0 or i == len(siblings) - 1:
            problems.append(f'line {ln}: divider at the {"start" if i == 0 else "end"} '
                            f'of the <{parent["tag"]}> - it separates nothing (rule 4)')
        if i > 0 and is_divider(siblings[i - 1]) and not (n['text'] or '').strip():
            problems.append(f'line {ln}: two dividers in a row - double line (rule 4)')

    if checked == 0:
        return None, ['no .al-divider in the HTML - the component enters the site with '
                      'its playground; until then this gate stays pending']
    return checked, problems


def run():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_HTML
    rows = contrast_rows()
    invis = [r for r in rows if r['invisible']]
    excs = [r for r in rows if r['exception']]
    passing = [r for r in rows if r['pass']]

    checked, mk = markup_contract(path)

    print('=' * 74)
    print('DIVIDER ACCESSIBILITY QA')
    print('=' * 74)
    print('\nLINE against each surface it is placed on')
    for r in rows:
        if r['invisible']:
            mark, note = 'XX', 'INVISIBLE - line and background have the same color'
        elif r['pass']:
            mark, note = 'ok', 'pass'
        else:
            mark, note = '~~', f'exception "{EXC}"'
        print(f'  {mark} {r["theme"]:<5} on {r["bg"]:<18} {r["fg"]} x {r["bgHex"]}  '
              f'{r["ratio"]:5.2f}  {note}')

    print('\nFOCUS RING')
    print('     n/a - the divider never receives focus (rule 16)')

    print('\nMARKUP CONTRACT')
    print(f'     source: {os.path.relpath(path, ROOT)}')
    if checked is None:
        for p in mk:
            print(f'     PENDING: {p}')
    else:
        print(f'     {checked} divider(s) checked, 7 rules (a-g)')
        for p in mk:
            print(f'     PROBLEM: {p}')

    print('-' * 74)
    print(f'{len(rows)} measurements  |  pass: {len(passing)}  |  exceptions: {len(excs)}  |  '
          f'fail: {len(invis)}')

    json.dump({
        'component': 'divider',
        'criterion': 'WCAG 1.4.11 non-text + visible line',
        'floor': NON_TEXT_FLOOR,
        'markupSource': os.path.relpath(path, ROOT),
        'markupChecked': checked,
        'markupPending': checked is None,
        'markupProblems': mk if checked is not None else [],
        'rows': rows,
    }, open(OUT_JSON, 'w'), indent=2, ensure_ascii=False)
    print(f'{os.path.relpath(OUT_JSON, ROOT)} written')

    failed = False
    if invis:
        print('-' * 74)
        print(f'{len(invis)} SURFACE(S) WHERE THE LINE DOES NOT EXIST ON SCREEN:')
        for r in invis:
            print(f'   {r["theme"]} on {r["bg"]}: {r["fg"]} = {r["bgHex"]}')
        failed = True
    if checked is not None and mk:
        print('-' * 74)
        print(f'{len(mk)} MARKUP PROBLEM(S) - gate fails')
        failed = True
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(run())
