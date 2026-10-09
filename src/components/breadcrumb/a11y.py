"""
Accessibility QA for the Breadcrumb (with _breadcrumb-more).

As with the other components, validation is by RENDERED COMBINATION - role x
theme - against the EFFECTIVE background, not a loose token pair.

WHAT THE EFFECTIVE BACKGROUND CHANGES HERE

  The trail lives on the page (`bg-canvas` or `bg-surface`, rule 7). The `…`
  menu is a `bg-surface-raised` layer on top of it, and inside it the items
  are Tab Square with hover and pressed SWAPPED for the `-raised` ones
  (rule 26). The token layer measures the pairs; here comes what only exists
  rendered:

  - the menu item label at rest, hover and pressed against the background
    THE ITEM ACTUALLY HAS (the `-raised` the menu injects into the Tab);
  - the item hover and pressed against the menu background: equal = an item
    that doesn't react, fail (the Modal 0.18.1 defect that `-raised` avoids);
  - the item focus ring, inside the menu.

FOUR JUDGMENTS

  1. Text (link, `…`, current page, menu item in each state): 4.5:1 from
     1.4.3. It must pass.
  2. Focus ring on the trail and inside the menu: 3:1 from 1.4.11. It must
     pass.
  3. Item hover and pressed DIFFERENT from the menu background. Equal = fail.
  4. Menu border: `region-border` (see tokens.py). A border EQUAL to the page
     fails: the exception covers a subtle separation, not its absence.
  The separator is decorative (aria-hidden, rule 21): outside 1.4.11.

THE MARKUP CONTRACT IS THE OTHER HALF OF THIS GATE

  Usage rules from guidelines.md, measured on the emitted HTML:

    a) `.al-breadcrumb` is a <nav> with aria-label (rule 19);
    b) one live breadcrumb per page; the sample ones sit under `inert`
       (on it or on an ancestor) and are exempt, and so does an interactive
       demo that can't be inert, marked by `data-al-demo` on an ancestor. A
       single-file site keeps each page in a subtree that toggles `hidden`:
       the nearest `hidden` ancestor marks the page, so one per subtree (rule 7);
    c) the only child is <ol class="al-breadcrumb__list"> and each of its
       children is <li class="al-breadcrumb__item"> (rule 19);
    d) the LAST item is only <span class="al-breadcrumb__current"
       aria-current="page"> with text - no <a>, no separator (rules 15 and 20);
    e) every item but the last ends in an <svg class="al-breadcrumb__separator">
       with aria-hidden="true" and focusable="false" (rule 21);
    f) every link is an <a href> with text and without aria-current;
       aria-current only on the current one (rules 15 and 20);
    g) the `…` only exists with 5 levels or more, and always as the THIRD
       item; it is a <button type="button"> with aria-label, aria-expanded and
       aria-controls pointing to the menu in the same item (rules 5, 6 and 22);
    h) the menu is <ul class="al-tabs al-tabs--square al-breadcrumb__menu">
       with no role; each item is <a href class="al-tab"> with a text
       .al-tab__label, no role nor aria-selected/aria-current (rule 17);
    i) no breadcrumb inside a Card, Modal or Drawer (rule 7);
    j) no empty label anywhere in the trail (rule 10).

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
from htmltree import Tree, walk, classes, has, ancestors, text_of, SKIP_TEMPLATE  # noqa: E402
FOUND = json.load(open(TOKENS_JSON))
BC = json.load(open(comp_out('breadcrumb', 'tokens.json')))
TAB = json.load(open(comp_out('tab', 'tokens.json')))

SEM = FOUND['color']['semantic']
ALIAS = BC['alias']
TA = TAB['alias']
THEMES = ('light', 'dark')

TEXT_FLOOR = 4.5         # 1.4.3
NON_TEXT_FLOOR = 3.0     # 1.4.11
EXC_BORDER = 'region-border'

DEFAULT_HTML = SITE_HTML
OUT_JSON = comp_out('breadcrumb', 'a11y.json')

PAGES = ('bg-canvas', 'bg-surface')


def sem(name, theme):
    v = SEM[name]
    return v[THEMES.index(theme)] if isinstance(v, list) else v[theme]


def bc(role, theme):
    return sem(ALIAS[f'breadcrumb-{role}'], theme)


def tab(role, theme):
    return sem(TA[f'tab-{role}'], theme)


def row(theme, what, fg_name, fg, bg_name, bg, floor, exc=None, invisible=False):
    ratio = round(cr(fg, bg), 2)
    ok = ratio >= floor
    return {'theme': theme, 'what': what, 'fg': fg_name, 'fgHex': fg,
            'bg': bg_name, 'bgHex': bg, 'ratio': ratio, 'floor': floor,
            'pass': ok, 'invisible': invisible,
            'exception': None if ok or invisible else exc}


def contrast_rows():
    rows = []
    for t in THEMES:
        ring = sem('shadow-focus-default', t)
        menu = bc('menu-bg', t)
        hover = bc('menu-item-bg-hover', t)
        active = bc('menu-item-bg-active', t)
        for p in PAGES:
            pg = sem(p, t)
            rows.append(row(t, 'link', ALIAS['breadcrumb-link'], bc('link', t), p, pg, TEXT_FLOOR))
            rows.append(row(t, '…', ALIAS['breadcrumb-more'], bc('more', t), p, pg, TEXT_FLOOR))
            rows.append(row(t, 'current page', ALIAS['breadcrumb-current'], bc('current', t), p, pg, TEXT_FLOOR))
            rows.append(row(t, 'ring on trail', 'shadow-focus-default', ring, p, pg, NON_TEXT_FLOOR))
            b = bc('menu-border', t)
            rows.append(row(t, 'menu border', ALIAS['breadcrumb-menu-border'], b, p, pg,
                            NON_TEXT_FLOOR, EXC_BORDER, invisible=b.lower() == pg.lower()))
        # inside the menu: the effective background of each item state
        rows.append(row(t, 'menu item', TA['tab-label'], tab('label', t),
                        'menu-bg', menu, TEXT_FLOOR))
        rows.append(row(t, 'menu item (hover)', TA['tab-label-hover'], tab('label-hover', t),
                        'menu-item-bg-hover', hover, TEXT_FLOOR))
        rows.append(row(t, 'menu item (pressed)', TA['tab-label-active'], tab('label-active', t),
                        'menu-item-bg-active', active, TEXT_FLOOR))
        rows.append(row(t, 'ring in menu', 'shadow-focus-default', ring, 'menu-bg', menu, NON_TEXT_FLOOR))
        # judgment 3: the state must exist on screen (no floor, only equality)
        for state, color in (('hover', hover), ('pressed', active)):
            r = row(t, f'item {state} vs menu', ALIAS[f'breadcrumb-menu-item-bg-{"hover" if state == "hover" else "active"}'],
                    color, 'menu-bg', menu, 1.0, invisible=color.lower() == menu.lower())
            r['pass'] = not r['invisible']
            rows.append(r)
    return rows


# ─────────────────────────────────────────────── markup
def check_breadcrumb(n, ids, problems):
    ln = n['line']

    def bad(msg):
        problems.append(f'line {ln}: {msg}')

    # (a)
    if n['tag'] != 'nav' or not n['attrs'].get('aria-label', '').strip():
        bad('.al-breadcrumb must be <nav aria-label="…"> (rule 19)')
    # (i)
    for a in ancestors(n):
        if any(has(a, c) for c in ('al-card', 'al-modal', 'al-drawer')):
            bad('breadcrumb inside a Card, Modal or Drawer (rule 7)')
            break
    # (c)
    lists = n['kids']
    if len(lists) != 1 or lists[0]['tag'] != 'ol' or not has(lists[0], 'al-breadcrumb__list'):
        bad('the only child must be <ol class="al-breadcrumb__list"> (rule 19)')
        return
    items = lists[0]['kids']
    if any(i['tag'] != 'li' or not has(i, 'al-breadcrumb__item') for i in items):
        bad('every child of the list is <li class="al-breadcrumb__item"> (rule 19)')
        return
    if len(items) < 2:
        bad('trail with fewer than 2 levels - with no parent there is no breadcrumb (rules 1 and 18)')
        return

    # (d) last item
    last = items[-1]
    cur = [k for k in walk(last) if has(k, 'al-breadcrumb__current')]
    if (len(cur) != 1 or cur[0]['tag'] != 'span' or cur[0]['attrs'].get('aria-current') != 'page'
            or not text_of(cur[0])):
        bad('last item = <span class="al-breadcrumb__current" aria-current="page"> with text (rules 15 and 20)')
    if any(k['tag'] in ('a', 'button') for k in walk(last)):
        bad('the current page is neither a link nor a button (rule 15)')
    if any(has(k, 'al-breadcrumb__separator') for k in walk(last)):
        bad('the last item takes no separator (rule 21)')

    # (e) separators
    for it in items[:-1]:
        if not it['kids'] or not has(it['kids'][-1], 'al-breadcrumb__separator'):
            bad(f'item "{text_of(it)[:20]}" without a separator at the end (rule 21)')
            continue
        s = it['kids'][-1]
        if s['tag'] != 'svg' or s['attrs'].get('aria-hidden') != 'true' or s['attrs'].get('focusable') != 'false':
            bad('the separator is an <svg> with aria-hidden="true" focusable="false" (rule 21)')

    # (f) links
    for k in walk(n):
        if has(k, 'al-breadcrumb__link'):
            if k['tag'] != 'a' or not k['attrs'].get('href'):
                bad('.al-breadcrumb__link must be <a href> (rule 15)')
            if not text_of(k):
                bad('link without text (rule 10)')
        if 'aria-current' in k['attrs'] and not has(k, 'al-breadcrumb__current'):
            bad('aria-current outside the current page (rules 15 and 20)')

    # (g) `…` and (h) menu
    mores = [i for i in items if has(i, 'al-breadcrumb__more')]
    menu_items = 0
    for m in mores:
        btn = [k for k in m['kids'] if has(k, 'al-breadcrumb__more-button')]
        if len(btn) != 1:
            bad('`…` item without .al-breadcrumb__more-button')
            continue
        b = btn[0]['attrs']
        if (btn[0]['tag'] != 'button' or b.get('type') != 'button' or not b.get('aria-label', '').strip()
                or b.get('aria-expanded') not in ('true', 'false') or not b.get('aria-controls')):
            bad('`…` = <button type="button"> with aria-label, aria-expanded and aria-controls (rule 22)')
        menu = ids.get(b.get('aria-controls'))
        if menu is None or menu.get('parent') is not m:
            bad('the `…` aria-controls does not point to a menu in the same item (rule 22)')
            continue
        mc = classes(menu)
        if menu['tag'] != 'ul' or not {'al-tabs', 'al-tabs--square', 'al-breadcrumb__menu'} <= set(mc):
            bad('menu = <ul class="al-tabs al-tabs--square al-breadcrumb__menu"> (rule 17)')
        if 'role' in menu['attrs']:
            bad(f'menu with role="{menu["attrs"]["role"]}" - they are links, never an actions menu (rule 17)')
        for li in menu['kids']:
            links = [k for k in li['kids'] if k['tag'] == 'a']
            if li['tag'] != 'li' or len(links) != 1:
                bad('each menu item is an <li> with one <a> (rule 17)')
                continue
            a = links[0]
            lab = [k for k in a['kids'] if has(k, 'al-tab__label')]
            if (not a['attrs'].get('href') or not has(a, 'al-tab') or not lab or not text_of(lab[0])
                    or any(x in a['attrs'] for x in ('role', 'aria-selected', 'aria-current'))):
                bad('menu item = <a href class="al-tab"> with .al-tab__label, no role/aria-selected/aria-current (rule 17)')
            menu_items += 1
    if len(mores) > 1:
        bad('more than one `…` in the trail (rule 6)')
    if mores:
        if items.index(mores[0]) != 2 or len(items) != 4:
            bad('the Large is first, second, `…` and current - the `…` is the third of four items (rule 6)')
        if len(items) - 1 + menu_items < 5:
            bad(f'`…` with {len(items) - 1 + menu_items} levels - it only collapses at 5 or more (rule 5)')
    elif len(items) > 4:
        bad(f'{len(items)} levels without `…` - at 5 or more the trail collapses (rule 5)')


def markup_contract(path):
    if not os.path.exists(path):
        return None, [f'{path} does not exist']
    t = Tree(skip=SKIP_TEMPLATE)
    t.feed(open(path, encoding='utf-8').read())
    ids = {n['attrs']['id']: n for n in walk(t.root) if n['attrs'].get('id')}

    found, problems, live = 0, [], {}
    for n in walk(t.root):
        if not has(n, 'al-breadcrumb'):
            continue
        found += 1
        if not any(x in a['attrs'] for a in [n, *ancestors(n)] for x in ('inert', 'data-al-demo')):
            page = next((a for a in ancestors(n) if 'hidden' in a['attrs']), t.root)
            live[id(page)] = live.get(id(page), 0) + 1
        check_breadcrumb(n, ids, problems)
    # (b)
    for count in live.values():
        if count > 1:
            problems.append(f'{count} live breadcrumbs on one page - one per page; samples sit under inert (rule 7)')
    if found == 0:
        return None, ['no .al-breadcrumb in the HTML - run site/site.py first']
    return found, problems


def run():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_HTML
    rows = contrast_rows()
    invis = [r for r in rows if r['invisible']]
    fails = [r for r in rows if not r['pass'] and not r['exception'] and not r['invisible']]
    excs = [r for r in rows if r['exception']]
    passing = [r for r in rows if r['pass']]

    checked, mk = markup_contract(path)

    print('=' * 74)
    print('BREADCRUMB ACCESSIBILITY QA')
    print('=' * 74)
    for r in rows:
        if r['invisible']:
            mark, note = 'XX', 'INVISIBLE - equal to the background'
        elif r['pass']:
            mark, note = 'ok', 'pass'
        elif r['exception']:
            mark, note = '~~', f'exception "{r["exception"]}"'
        else:
            mark, note = 'XX', 'FAIL'
        print(f'  {mark} {r["theme"]:<5} {r["what"]:<26} on {r["bg"]:<20} '
              f'{r["fgHex"]} x {r["bgHex"]}  {r["ratio"]:5.2f}  {note}')

    print('\nMARKUP CONTRACT')
    print(f'     source: {os.path.relpath(path, ROOT)}')
    if checked is None:
        for p in mk:
            print(f'     PENDING: {p}')
    else:
        print(f'     {checked} breadcrumb(s) checked, 10 rules (a-j)')
        for p in mk:
            print(f'     PROBLEM: {p}')

    print('-' * 74)
    print(f'{len(rows)} measurements  |  pass: {len(passing)}  |  exceptions: {len(excs)}  |  '
          f'fail: {len(fails) + len(invis)}')

    json.dump({
        'component': 'breadcrumb',
        'criterion': 'WCAG 1.4.3 text + 1.4.11 non-text + visible state',
        'markupSource': os.path.relpath(path, ROOT),
        'markupChecked': checked,
        'markupPending': checked is None,
        'markupProblems': mk if checked is not None else [],
        'rows': rows,
    }, open(OUT_JSON, 'w'), indent=2, ensure_ascii=False)
    print(f'{os.path.relpath(OUT_JSON, ROOT)} written')

    failed = bool(fails or invis)
    if checked is None or mk:
        print('-' * 74)
        print(f'{len(mk)} MARKUP PROBLEM(S) - gate fails')
        failed = True
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(run())
