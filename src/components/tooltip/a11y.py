"""
Accessibility QA for the Tooltip.

As with the other components, validation is by RENDERED COMBINATION - role x
theme - against the EFFECTIVE background, not a loose token pair.

WHAT THE EFFECTIVE BACKGROUND CHANGES HERE

  Almost nothing, and that is what this gate confirms. The tooltip lives in
  the browser's top layer (popover), with an opaque `tooltip-bg` background
  and opacity 1 when open: text and icon only touch the tooltip's own
  background, never the page. The icon inherits the text color
  (currentColor, rule 12). The box, in turn, can land on any page background
  - including the `bg-surface-raised` of a Modal or Drawer, which is where it
  shows up on top of everything.

THREE JUDGMENTS

  1. Text against the tooltip background: 4.5:1 from 1.4.3. It must pass.
  2. Icon against the tooltip background: 3:1 from 1.4.11. It must pass.
  3. Box against each page background (canvas, surface, surface-raised):
     3:1. With no border and no arrow (rule 14), the box only separates from
     the page by the inverted background - if it disappears, the text floats
     loose. It must pass.
  No contrast exception: none was declared.

THE MARKUP CONTRACT IS THE OTHER HALF OF THIS GATE

  Usage rules from guidelines.md, measured on the emitted HTML:

    a) every live tooltip is <div class="al-tooltip" id role="tooltip"
       popover="manual"> with a unique id (rule 24; "manual" because of the
       Modal's Esc);
    b) data-placement, if present, is top, bottom, left or right (rule 13);
    c) inside, in this order and nothing else: the <svg class="al-icon
       al-icon--20 al-tooltip__icon"> with aria-hidden="true"
       focusable="false" (rules 11 and 12; the icon is always present) and a
       <span class="al-tooltip__text"> with text;
    d) nothing interactive inside - no link, button, field, tabindex or
       contenteditable (rule 10);
    e) exactly one trigger points to it, through aria-labelledby OR
       aria-describedby - never both on the same trigger (rule 24);
    f) the trigger is focusable (button, link with href, field, or
       tabindex >= 0) and never `disabled` (rules 22 and 23);
    g) the tooltip is the element right after the trigger (rule 25);
    h) a trigger with aria-labelledby doesn't take aria-label (as in the Icon
       Button); a trigger with aria-describedby already has its own name -
       text or aria-label (rule 24);
    i) the site's frozen samples (.al-tooltip without popover) sit under
       `inert` and `aria-hidden` on an ancestor: a tooltip open forever
       doesn't exist in the component and doesn't count.

  The playground swaps the stage with JavaScript (Use x Side): the variants
  come from `var TT_DEMOS` in the HTML itself. The gate reads that object and
  checks each fragment too - that way the aria-describedby path, which isn't
  on the stage when the page loads, doesn't escape.

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
from htmltree import Tree, walk, classes, has, ancestors, text_of, SKIP_TEMPLATE  # noqa: E402
FOUND = json.load(open(TOKENS_JSON))
TT = json.load(open(comp_out('tooltip', 'tokens.json')))

SEM = FOUND['color']['semantic']
ALIAS = TT['alias']
THEMES = ('light', 'dark')

TEXT_FLOOR = 4.5         # 1.4.3
NON_TEXT_FLOOR = 3.0     # 1.4.11

DEFAULT_HTML = SITE_HTML
OUT_JSON = comp_out('tooltip', 'a11y.json')

PAGES = ('bg-canvas', 'bg-surface', 'bg-surface-raised')
PLACEMENTS = ('top', 'bottom', 'left', 'right')
INTERACTIVE = ('a', 'button', 'input', 'select', 'textarea', 'details', 'summary')


def sem(name, theme):
    v = SEM[name]
    return v[THEMES.index(theme)] if isinstance(v, list) else v[theme]


def tt(role, theme):
    return sem(ALIAS[f'tooltip-{role}'], theme)


def row(theme, what, fg_name, fg, bg_name, bg, floor):
    ratio = round(cr(fg, bg), 2)
    return {'theme': theme, 'what': what, 'fg': fg_name, 'fgHex': fg,
            'bg': bg_name, 'bgHex': bg, 'ratio': ratio, 'floor': floor,
            'pass': ratio >= floor, 'invisible': fg.lower() == bg.lower(),
            'exception': None}


def contrast_rows():
    rows = []
    for t in THEMES:
        bg, fg = tt('bg', t), tt('text', t)
        rows.append(row(t, 'text', ALIAS['tooltip-text'], fg, ALIAS['tooltip-bg'], bg, TEXT_FLOOR))
        rows.append(row(t, 'icon (currentColor)', ALIAS['tooltip-text'], fg, ALIAS['tooltip-bg'], bg,
                        NON_TEXT_FLOOR))
        for p in PAGES:
            rows.append(row(t, 'box on the page', ALIAS['tooltip-bg'], bg, p, sem(p, t),
                            NON_TEXT_FLOOR))
    return rows


# ─────────────────────────────────────────────── markup
def next_element(node):
    sibs = node['parent']['kids']
    i = sibs.index(node)
    return sibs[i + 1] if i + 1 < len(sibs) else None


def focusable(n):
    a = n['attrs']
    tab = a.get('tabindex')
    if tab is not None:
        try:
            return int(tab) >= 0
        except ValueError:
            return False
    if n['tag'] == 'a':
        return 'href' in a
    if n['tag'] == 'input':
        return a.get('type') != 'hidden'
    return n['tag'] in ('button', 'select', 'textarea', 'summary')


def refs(n, attr):
    return n['attrs'].get(attr, '').split()


def check_tooltip(tip, triggers, problems, where):
    ln = tip['line']
    a = tip['attrs']

    def bad(msg):
        problems.append(f'{where}line {ln}: {msg}')

    # (a)
    if tip['tag'] != 'div' or a.get('role') != 'tooltip' or a.get('popover') != 'manual':
        bad('live tooltip = <div role="tooltip" popover="manual"> (rule 24)')
    # (b)
    if 'data-placement' in a and a['data-placement'] not in PLACEMENTS:
        bad(f'data-placement="{a["data-placement"]}" - only top, bottom, left or right (rule 13)')
    # (c)
    kids = tip['kids']
    if len(kids) != 2:
        bad('inside the tooltip: icon + text, nothing else (rules 11 and 12)')
    else:
        ico, txt = kids
        ia = ico['attrs']
        if (ico['tag'] != 'svg' or not {'al-icon', 'al-icon--20', 'al-tooltip__icon'} <= set(classes(ico))
                or ia.get('aria-hidden') != 'true' or ia.get('focusable') != 'false'):
            bad('first child = <svg class="al-icon al-icon--20 al-tooltip__icon" '
                'aria-hidden="true" focusable="false"> (rules 11 and 12)')
        if txt['tag'] != 'span' or not has(txt, 'al-tooltip__text') or not text_of(txt):
            bad('second child = <span class="al-tooltip__text"> with text')
    # (d)
    for k in walk(tip):
        if (k['tag'] in INTERACTIVE or 'tabindex' in k['attrs']
                or 'contenteditable' in k['attrs']):
            bad(f'interactive <{k["tag"]}> inside the tooltip (rule 10)')
            break
    # (e)
    if len(triggers) != 1:
        bad(f'{len(triggers)} triggers point to "{a.get("id")}" - it must be exactly one (rule 24)')
        return
    trig = triggers[0]
    by_label = a['id'] in refs(trig, 'aria-labelledby')
    by_desc = a['id'] in refs(trig, 'aria-describedby')
    if by_label and by_desc:
        bad('the trigger points through both attributes - name OR description (rule 24)')
    # (f)
    if not focusable(trig):
        bad(f'trigger <{trig["tag"]}> is not focusable (rule 22)')
    if 'disabled' in trig['attrs']:
        bad('disabled trigger - to explain a block use aria-disabled (rule 23)')
    # (g)
    if next_element(trig) is not tip:
        bad('the tooltip does not come right after the trigger (rule 25)')
    # (h)
    if by_label and 'aria-label' in trig['attrs']:
        bad('trigger with aria-labelledby and aria-label together - with a tooltip, only labelledby (as in the Icon Button)')
    if by_desc and not by_label and not (trig['attrs'].get('aria-label', '').strip() or text_of(trig)):
        bad('description trigger without its own name - with no name, the tooltip is the name: aria-labelledby (rule 24)')


def markup_contract(html, where=''):
    """Checks a document (or fragment). Returns (live, frozen, problems)."""
    t = Tree(skip=SKIP_TEMPLATE)
    t.feed(html)
    nodes = list(walk(t.root))
    problems = []

    ids = {}
    for n in nodes:
        i = n['attrs'].get('id')
        if i:
            ids.setdefault(i, []).append(n)

    live, frozen = 0, 0
    for n in nodes:
        if not has(n, 'al-tooltip'):
            continue
        if 'popover' not in n['attrs']:
            # (i) frozen sample
            under = list(ancestors(n))
            if not (any('inert' in x['attrs'] for x in under)
                    and any(x['attrs'].get('aria-hidden') == 'true' for x in under)):
                problems.append(f'{where}line {n["line"]}: .al-tooltip without popover outside inert + '
                                f'aria-hidden - a tooltip open forever does not exist')
            frozen += 1
            continue
        live += 1
        tid = n['attrs'].get('id', '')
        if not tid:
            problems.append(f'{where}line {n["line"]}: live tooltip without id (rule 24)')
            continue
        if len(ids.get(tid, [])) > 1:
            problems.append(f'{where}line {n["line"]}: id "{tid}" repeated in the document')
        triggers = [x for x in nodes if tid in refs(x, 'aria-labelledby') + refs(x, 'aria-describedby')]
        check_tooltip(n, triggers, problems, where)
    return live, frozen, problems


def demos_of(html):
    m = re.search(r'var TT_DEMOS = (\{.*?\});\n', html)
    return json.loads(m.group(1)) if m else {}


def run():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_HTML
    rows = contrast_rows()
    fails = [r for r in rows if not r['pass']]

    print('=' * 74)
    print('TOOLTIP ACCESSIBILITY QA')
    print('=' * 74)
    for r in rows:
        note = 'INVISIBLE - equal to the background' if r['invisible'] else ('pass' if r['pass'] else 'FAIL')
        print(f'  {"ok" if r["pass"] else "XX"} {r["theme"]:<5} {r["what"]:<22} on {r["bg"]:<18} '
              f'{r["fgHex"]} x {r["bgHex"]}  {r["ratio"]:5.2f}  {note}')

    print('\nMARKUP CONTRACT')
    print(f'     source: {os.path.relpath(path, ROOT)}')
    if not os.path.exists(path):
        live, frozen, mk, demos = None, 0, [f'{path} does not exist'], {}
    else:
        html = open(path, encoding='utf-8').read()
        live, frozen, mk = markup_contract(html)
        demos = demos_of(html)
        for key, d in demos.items():
            dl, _, dp = markup_contract(d['html'], where=f'playground {key}, ')
            live += dl
            mk += dp
        if live == 0:
            live, mk = None, ['no live .al-tooltip in the HTML - run site.py first']
    if live is None:
        for p in mk:
            print(f'     PENDING: {p}')
    else:
        print(f'     {live} live tooltip(s) checked, 9 rules (a-i) - '
              f'{len(demos)} playground variants included; {frozen} frozen sample(s) under inert')
        for p in mk:
            print(f'     PROBLEM: {p}')

    print('-' * 74)
    print(f'{len(rows)} measurements  |  pass: {len(rows) - len(fails)}  |  exceptions: 0  |  '
          f'fail: {len(fails)}')

    json.dump({
        'component': 'tooltip',
        'criterion': 'WCAG 1.4.3 text + 1.4.11 non-text',
        'markupSource': os.path.relpath(path, ROOT),
        'markupChecked': live,
        'markupFrozen': frozen,
        'markupDemos': len(demos),
        'markupPending': live is None,
        'markupProblems': mk if live is not None else [],
        'rows': rows,
    }, open(OUT_JSON, 'w'), indent=2, ensure_ascii=False)
    print(f'{os.path.relpath(OUT_JSON, ROOT)} written')

    failed = bool(fails)
    if live is None or mk:
        print('-' * 74)
        print(f'{len(mk)} MARKUP PROBLEM(S) - gate fails')
        failed = True
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(run())
