"""
Accessibility QA for the Accordion.

As with the other components, validation is by RENDERED COMBINATION - state x
theme - against the EFFECTIVE background, not a loose token pair.

WHAT THE EFFECTIVE BACKGROUND CHANGES HERE

  Only the header (<summary>) changes background: rest, hover, pressed. Focus
  goes back to rest and adds the ring. Title and chevron measure against the
  header background in each state. The divider is the content's top border:
  it touches the header above and the content below, and measures against
  both, keeping the worst. The item measures against the PAGE, and the page
  is only `bg-surface` - rule 14 forbids the canvas and the card. The ring is
  drawn outside the header, with the gap in `bg-canvas`: it measures against
  the page and against the gap.

THREE JUDGMENTS

  1. Text: 4.5:1 floor from 1.4.3. It must pass - no exception.
  2. Chevron, divider, item boundary and ring: 3:1 floor from 1.4.11. Divider
     and boundary fall below - they are the declared exceptions
     `decorative-divider` and `item-not-separated-by-bg` (see tokens.py).
     Chevron and ring must pass.
  3. INVISIBLE item - background equal to the page. The exception covers a
     subtle item, not an item that doesn't exist. This fails.

THE MARKUP CONTRACT IS THE OTHER HALF OF THIS GATE

  Usage rules from guidelines.md, measured on the emitted HTML:

    a) `.al-accordion` is a <details> (rule 24);
    b) the first child is the <summary class="al-accordion__header"> - and
       `.al-accordion__header` only exists on <summary> (rule 24);
    c) the <summary> has a name: `.al-accordion__title` with text (rule 15);
    d) no <h1>-<h6> inside the <summary> (rule 25);
    e) nothing interactive inside the <summary> - link, button, field,
       tabindex, actionable role (rule 17);
    f) icon and chevron with aria-hidden="true" (rules 18 and 19);
    g) no Accordion inside an Accordion (rule 5);
    h) pure native: no role, aria-expanded, aria-controls or tabindex on the
       <details> or the <summary> (rule 24);
    i) no disabled: neither `disabled` nor `aria-disabled` (rule 20);
    j) exactly one `.al-accordion__content`, direct child, after the
       <summary>.

RUN ORDER - same as the others: runs AFTER the HTML it measures.

Run: python3 a11y.py [path.html]
     with no argument, measures build/site/index.html
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'tools'))
from paths import ROOT, TOKENS_JSON, SITE_HTML, comp_out  # noqa: E402
from contrast import cr  # noqa: E402
from htmltree import Tree, walk, has, ancestors, text_of  # noqa: E402
FOUND = json.load(open(TOKENS_JSON))
ACC = json.load(open(comp_out('accordion', 'tokens.json')))

SEM = FOUND['color']['semantic']
ALIAS = ACC['alias']
THEMES = ('light', 'dark')

TEXT_FLOOR = 4.5          # 1.4.3
NON_TEXT_FLOOR = 3.0      # 1.4.11
EXC_DIV = 'decorative-divider'
EXC_ITEM = 'item-not-separated-by-bg'

DEFAULT_HTML = SITE_HTML
OUT_JSON = comp_out('accordion', 'a11y.json')

PAGE = 'bg-surface'     # rule 14: only here

# state -> role of the header background. Focus = rest.
STATES = (('rest', 'bg'), ('hover', 'bg-hover'), ('pressed', 'bg-active'), ('focus', 'bg'))

HEADINGS = {'h1', 'h2', 'h3', 'h4', 'h5', 'h6'}
ACTIONABLE_ROLES = {'button', 'link', 'checkbox', 'radio', 'switch', 'menuitem', 'tab', 'option'}


def sem(name, theme):
    """tokens.json stores the semantic as [light, dark]."""
    v = SEM[name]
    return v[THEMES.index(theme)] if isinstance(v, list) else v[theme]


def acc(role, theme):
    """Color of an Accordion role, following the alias down to the semantic."""
    return sem(ALIAS[f'accordion-{role}'], theme)


# ─────────────────────────────────────────────── contrast
def row(theme, state, what, fg_name, fg, bg_name, bg, floor, exc=None, invisible=False):
    ratio = round(cr(fg, bg), 2)
    ok = ratio >= floor
    return {
        'theme': theme, 'state': state, 'what': what,
        'fg': fg_name, 'fgHex': fg, 'bg': bg_name, 'bgHex': bg,
        'ratio': ratio, 'floor': floor, 'pass': ok,
        'invisible': invisible,
        'exception': None if ok or invisible else exc,
    }


def contrast_rows():
    rows = []
    for theme in THEMES:
        title = acc('title', theme)
        content = acc('bg', theme)
        line = acc('divider', theme)
        pg = sem(PAGE, theme)

        for state, role in STATES:
            head = acc(role, theme)
            name = ALIAS[f'accordion-{role}']
            # 1. title and chevron (currentColor) against the header
            rows.append(row(theme, state, 'title', ALIAS['accordion-title'], title,
                            name, head, TEXT_FLOOR))
            rows.append(row(theme, state, 'chevron', ALIAS['accordion-title'], title,
                            name, head, NON_TEXT_FLOOR))
            # 2. divider (open only) - between header and content, the worst
            if state != 'focus':      # focus has the rest background: same measurement
                worst = min((cr(line, head), name, head),
                            (cr(line, content), ALIAS['accordion-bg'], content))
                rows.append(row(theme, state, 'divider', ALIAS['accordion-divider'], line,
                                worst[1], worst[2], NON_TEXT_FLOOR, EXC_DIV))

        # 3. item boundary against the page
        rows.append(row(theme, 'rest', 'bg-boundary', ALIAS['accordion-bg'], content,
                        PAGE, pg, NON_TEXT_FLOOR, EXC_ITEM,
                        invisible=content.lower() == pg.lower()))

        # 4. ring - outside the header; the gap is bg-canvas
        ring = sem('shadow-focus-default', theme)
        gap = sem('bg-canvas', theme)
        worst = min((cr(ring, pg), PAGE, pg), (cr(ring, gap), 'bg-canvas (gap)', gap))
        rows.append(row(theme, 'focus', 'ring', 'shadow-focus-default', ring,
                        worst[1], worst[2], NON_TEXT_FLOOR))
    return rows


# ─────────────────────────────────────────────── markup
def interactive(node):
    a, tag = node['attrs'], node['tag']
    if tag == 'a' and 'href' in a:
        return True
    if tag in ('button', 'input', 'select', 'textarea', 'summary', 'details'):
        return True
    if 'tabindex' in a and a['tabindex'] != '-1':
        return True
    return a.get('role') in ACTIONABLE_ROLES


NATIVE_ONLY = ('role', 'aria-expanded', 'aria-controls', 'tabindex')


def markup_contract(path):
    if not os.path.exists(path):
        return None, [f'{path} does not exist']
    t = Tree()
    t.feed(open(path, encoding='utf-8').read())

    checked, problems = 0, []
    for n in walk(t.root):
        a, tag, ln = n['attrs'], n['tag'], n['line']

        # (b) the header only exists on <summary>
        if has(n, 'al-accordion__header') and tag != 'summary':
            problems.append(f'line {ln}: .al-accordion__header on <{tag}> - the header is the '
                            f'native <summary> (rule 24)')

        if not has(n, 'al-accordion'):
            continue
        checked += 1

        # (a) <details>
        if tag != 'details':
            problems.append(f'line {ln}: .al-accordion on <{tag}> - the item is a native '
                            f'<details> (rule 24)')

        # (g) no Accordion inside an Accordion
        if any(has(p, 'al-accordion') for p in ancestors(n)):
            problems.append(f'line {ln}: Accordion inside an Accordion (rule 5)')

        # (i) no disabled
        if 'disabled' in a or 'aria-disabled' in a:
            problems.append(f'line {ln}: disabled Accordion - an item with no content leaves '
                            f'the stack (rule 20)')

        # (h) pure native on <details>
        for attr in NATIVE_ONLY:
            if attr in a:
                problems.append(f'line {ln}: {attr} on <details> - the browser already announces '
                                f'the state; no manual ARIA (rule 24)')

        kids = n['kids']
        # (b) the first child is the component's summary
        head = kids[0] if kids else None
        if head is None or head['tag'] != 'summary' or not has(head, 'al-accordion__header'):
            problems.append(f'line {ln}: the Accordion\'s first child must be '
                            f'<summary class="al-accordion__header"> (rule 24)')
            continue

        ha, hl = head['attrs'], head['line']
        # (h) pure native on <summary>
        for attr in NATIVE_ONLY:
            if attr in ha:
                problems.append(f'line {hl}: {attr} on <summary> - pure native (rule 24)')
        if 'disabled' in ha or 'aria-disabled' in ha:
            problems.append(f'line {hl}: disabled <summary> (rule 20)')

        desc = list(walk(head))
        # (c) name
        titles = [d for d in desc if has(d, 'al-accordion__title')]
        if len(titles) != 1 or not text_of(titles[0]):
            problems.append(f'line {hl}: the <summary> needs one .al-accordion__title with '
                            f'text - it is the announced name (rule 15)')
        for d in desc:
            # (d) heading
            if d['tag'] in HEADINGS:
                problems.append(f'line {d["line"]}: <{d["tag"]}> inside the <summary> - in some '
                                f'screen readers it leaves the headings list; the real heading '
                                f'goes BEFORE the stack (rule 25)')
            # (e) interactive
            if interactive(d):
                problems.append(f'line {d["line"]}: interactive <{d["tag"]}> inside the <summary> '
                                f'- the whole header is already the button (rule 17)')
            # (f) decorative icons
            if (has(d, 'al-accordion__icon') or has(d, 'al-accordion__chevron')) \
                    and d['attrs'].get('aria-hidden') != 'true':
                problems.append(f'line {d["line"]}: Accordion icon without aria-hidden="true" - '
                                f'it is decorative; the title is what speaks (rules 18 and 19)')

        # (j) one content, direct child, after the summary
        contents = [k for k in kids if has(k, 'al-accordion__content')]
        loose = [d for d in walk(n) if has(d, 'al-accordion__content') and d['parent'] is not n]
        if len(contents) != 1 or loose:
            problems.append(f'line {ln}: the Accordion must have exactly one '
                            f'.al-accordion__content, direct child of the <details>')
        elif kids.index(contents[0]) == 0:
            problems.append(f'line {ln}: .al-accordion__content before the <summary>')

    if checked == 0:
        return None, ['no .al-accordion in the HTML - the component enters the site with '
                      'its playground; until then this gate stays pending']
    return checked, problems


def run():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_HTML
    rows = contrast_rows()
    invis = [r for r in rows if r['invisible']]
    fails = [r for r in rows if not r['pass'] and not r['exception'] and not r['invisible']]
    excs = [r for r in rows if r['exception']]
    passing = [r for r in rows if r['pass']]

    checked, mk = markup_contract(path)

    print('=' * 78)
    print('ACCORDION ACCESSIBILITY QA')
    print('=' * 78)
    print('\nRENDERED COMBINATIONS (theme x state), page bg-surface')
    for r in rows:
        if r['invisible']:
            mark, note = 'XX', 'INVISIBLE - nothing separates the item from the page'
        elif r['pass']:
            mark, note = 'ok', 'pass'
        elif r['exception']:
            mark, note = '~~', f'exception "{r["exception"]}"'
        else:
            mark, note = 'XX', 'FAIL'
        print(f'  {mark} {r["theme"]:<5} {r["state"]:<8} {r["what"]:<17} '
              f'x {r["bg"]:<20} {r["ratio"]:5.2f} (floor {r["floor"]})  {note}')

    print('\nMARKUP CONTRACT')
    print(f'     source: {os.path.relpath(path, ROOT)}')
    if checked is None:
        for p in mk:
            print(f'     PENDING: {p}')
    else:
        print(f'     {checked} accordion(s) checked, 10 rules (a-j)')
        for p in mk:
            print(f'     PROBLEM: {p}')

    print('-' * 78)
    print(f'{len(rows)} measurements  |  pass: {len(passing)}  |  exceptions: {len(excs)}  |  '
          f'fail: {len(fails) + len(invis)}')

    json.dump({
        'component': 'accordion',
        'criterion': 'WCAG 1.4.3 text + 1.4.11 non-text + visible item',
        'floors': {'text': TEXT_FLOOR, 'nonText': NON_TEXT_FLOOR},
        'markupSource': os.path.relpath(path, ROOT),
        'markupChecked': checked,
        'markupPending': checked is None,
        'markupProblems': mk if checked is not None else [],
        'rows': rows,
    }, open(OUT_JSON, 'w'), indent=2, ensure_ascii=False)
    print(f'{os.path.relpath(OUT_JSON, ROOT)} written')

    failed = False
    if invis or fails:
        print('-' * 78)
        print(f'{len(invis) + len(fails)} COMBINATION(S) FAIL:')
        for r in invis + fails:
            print(f'   {r["theme"]} {r["state"]} {r["what"]} x {r["bg"]}: {r["ratio"]}:1')
        failed = True
    if checked is not None and mk:
        print('-' * 78)
        print(f'{len(mk)} MARKUP PROBLEM(S) - gate fails')
        failed = True
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(run())
