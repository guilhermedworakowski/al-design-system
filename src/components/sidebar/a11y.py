"""
Accessibility QA for the Sidebar.

As with the other components, validation is by RENDERED COMBINATION - role x
theme - against the EFFECTIVE background, not a loose token pair.

WHAT THE EFFECTIVE BACKGROUND CHANGES HERE

  On a wide screen the Sidebar lives on the page: background `bg-canvas`, and
  that is where the items (Tab Square) and the profile button (Ghost Icon
  Button) appear. The token layer measures the Sidebar's own texts; here the
  item and button states ON THE SIDEBAR BACKGROUND come in too - which is the
  reason for the `bg-canvas` background (with surface-raised the hover
  disappeared in dark, 1.00:1).

  On a narrow screen the Sidebar becomes a layer: what sits behind it is the
  page DIMMED by the scrim. The token layer doesn't measure that pair.

FOUR JUDGMENTS

  1. Text (name, e-mail, group label, item label in each state): 4.5:1 floor
     from 1.4.3. It must pass - except `brand-on-dark-hover`, the Foundation
     exception inherited from the Tab.
  2. Focus ring, button icon and selected/pressed item background against the
     Sidebar: 3:1 from 1.4.11 - except `tonal-selection`, inherited from the
     Tab.
  3. Item and button hover and pressed must be DIFFERENT from the Sidebar
     background (the defect the `bg-canvas` background avoided). Equal = fail.
  4. Sidebar border: `region-border` (see tokens.py), against the page next to
     it and, in modal mode, against the dimmed page. The modal PANEL against
     the dimmed page passes in light (4.1) and in dark sits at ~1.1:1:
     exception `sidebar-not-separated-from-scrim-in-dark` (approved on
     2026-10-08) - the separation comes from the border (~2.7) and the
     shadow. A panel EQUAL to the dimmed page fails: the exception covers a
     subtle separation, not its absence.

THE MARKUP CONTRACT IS THE OTHER HALF OF THIS GATE

  Usage rules from guidelines.md, measured on the emitted HTML:

    a) `.al-sidebar` is an <aside> with aria-label (rule 26);
    b) one live Sidebar per document; frozen ones sit under `inert` and are
       exempt (rule 4);
    c) exactly one `.al-sidebar__nav`, which is a <nav> with aria-label
       (rule 26);
    d) children in the order profile (optional), nav; inside the nav, body
       and Help (optional), in that order (rule 5);
    e) the profile stays OUTSIDE the nav; Avatar with aria-hidden and
       <img alt=""> (rules 18 and 26);
    f) the profile button is an Icon Button with a name (aria-label) and an
       aria-hidden svg (rule 19);
    g) every group has a label with text and an id, and its list has
       aria-labelledby pointing to that label (rule 27);
    h) every list is `.al-tabs.al-tabs--square` (rule 11);
    i) every item is an <a href> `.al-tab` with a text `.al-tab__label`, no
       role="tab" nor aria-selected (rule 28);
    j) at most one aria-current="page" in the Sidebar (rule 12);
    k) no repeated item label (rule 16);
    l) Help: it is a group, with at most 3 items (rule 21);
    m) every data-al-sidebar-open points to a `.al-sidebar` that exists and
       the button has aria-label, aria-controls equal to the id and
       aria-expanded (rules 24 and 25);
    n) there is a "skip" link (href="#...") BEFORE the Sidebar (rule 29).

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
from contrast import cr, composite  # noqa: E402
from htmltree import Tree, walk, has, ancestors, text_flat  # noqa: E402
FOUND = json.load(open(TOKENS_JSON))
SBR = json.load(open(comp_out('sidebar', 'tokens.json')))
TAB = json.load(open(comp_out('tab', 'tokens.json')))
IBT = json.load(open(comp_out('icon-button', 'tokens.json')))

SEM = FOUND['color']['semantic']
ALIAS = SBR['alias']
TA = TAB['alias']
THEMES = ('light', 'dark')

TEXT_FLOOR = 4.5
NON_TEXT_FLOOR = 3.0
EXC_BORDER = 'region-border'
EXC_TONAL = 'tonal-selection'
EXC_BRAND = 'brand-on-dark-hover'
EXC_SCRIM = 'sidebar-not-separated-from-scrim-in-dark'

DEFAULT_HTML = SITE_HTML
OUT_JSON = comp_out('sidebar', 'a11y.json')


def sem(name, theme):
    v = SEM[name]
    return v[THEMES.index(theme)] if isinstance(v, list) else v[theme]


def sbr(role, theme):
    return sem(ALIAS[f'sidebar-{role}'], theme)


def tab(role, theme):
    return sem(TA[f'tab-{role}'], theme)


# ─────────────────────────────────────────────── contrast
def row(theme, what, fg_name, fg, bg_name, bg, floor, exc=None, invisible=False):
    ratio = round(cr(fg, bg), 2)
    ok = ratio >= floor and not invisible
    return {
        'theme': theme, 'what': what,
        'fg': fg_name, 'fgHex': fg, 'bg': bg_name, 'bgHex': bg,
        'ratio': ratio, 'floor': floor, 'pass': ok,
        'invisible': invisible,
        'exception': None if ok or invisible else exc,
    }


def contrast_rows():
    rows = []
    for theme in THEMES:
        bg = sbr('bg', theme)
        bgn = ALIAS['sidebar-bg']

        # 1. the Sidebar's own texts
        for what, role in (('name', 'name'), ('email', 'email'), ('group-label', 'group-label')):
            rows.append(row(theme, what, ALIAS[f'sidebar-{role}'], sbr(role, theme), bgn, bg, TEXT_FLOOR))

        # 1. item label in each state, on the effective background
        rows.append(row(theme, 'item-rest', TA['tab-label'], tab('label', theme), bgn, bg, TEXT_FLOOR))
        rows.append(row(theme, 'item-hover', TA['tab-label-hover'], tab('label-hover', theme),
                        TA['tab-bg-hover'], tab('bg-hover', theme), TEXT_FLOOR))
        rows.append(row(theme, 'item-pressed', TA['tab-label-active'], tab('label-active', theme),
                        TA['tab-bg-active'], tab('bg-active', theme), TEXT_FLOOR))
        rows.append(row(theme, 'item-current', TA['tab-square-label-selected'], tab('square-label-selected', theme),
                        TA['tab-square-bg-selected'], tab('square-bg-selected', theme), TEXT_FLOOR))
        rows.append(row(theme, 'item-current-hover', TA['tab-square-label-selected-hover'],
                        tab('square-label-selected-hover', theme), TA['tab-square-bg-selected-hover'],
                        tab('square-bg-selected-hover', theme), TEXT_FLOOR, EXC_BRAND))
        rows.append(row(theme, 'item-current-pressed', TA['tab-square-label-selected-active'],
                        tab('square-label-selected-active', theme), TA['tab-square-bg-selected-active'],
                        tab('square-bg-selected-active', theme), TEXT_FLOOR))

        # 2. non-text against the Sidebar
        rows.append(row(theme, 'focus-ring', 'shadow-focus-default', sem('shadow-focus-default', theme),
                        bgn, bg, NON_TEXT_FLOOR))
        rows.append(row(theme, 'profile-button-icon', 'text-primary', sem('text-primary', theme),
                        bgn, bg, NON_TEXT_FLOOR))
        rows.append(row(theme, 'item-current-bg', TA['tab-square-bg-selected'],
                        tab('square-bg-selected', theme), bgn, bg, NON_TEXT_FLOOR, EXC_TONAL))
        rows.append(row(theme, 'item-current-pressed-bg', TA['tab-square-bg-selected-active'],
                        tab('square-bg-selected-active', theme), bgn, bg, NON_TEXT_FLOOR))

        # 3. hover and pressed must EXIST on the Sidebar
        for what, name in (('item-hover-distinct', TA['tab-bg-hover']),
                           ('item-pressed-distinct', TA['tab-bg-active']),
                           ('button-hover-distinct', 'bg-hover'),
                           ('button-pressed-distinct', 'bg-active')):
            f = sem(name, theme)
            rows.append(row(theme, what, name, f, bgn, bg, 1.0, invisible=f.lower() == bg.lower()))

        # 4. region border, against the Sidebar and against the page next to it
        for page in ('bg-canvas', 'bg-surface'):
            rows.append(row(theme, f'border-x-{page}', ALIAS['sidebar-border'], sbr('border', theme),
                            page, sem(page, theme), NON_TEXT_FLOOR, EXC_BORDER))

        # 4. modal mode: panel and border against the dimmed page
        for page in ('bg-canvas', 'bg-surface'):
            behind = composite(sem('bg-scrim', theme), sem(page, theme))
            rows.append(row(theme, f'panel-x-{page}-dimmed', bgn, bg, f'{page}+scrim', behind,
                            NON_TEXT_FLOOR, EXC_SCRIM, invisible=bg.lower() == behind.lower()))
            rows.append(row(theme, f'panel-border-x-{page}-dimmed', ALIAS['sidebar-border'],
                            sbr('border', theme), f'{page}+scrim', behind, NON_TEXT_FLOOR, EXC_BORDER))
    return rows


# ─────────────────────────────────────────────── markup
def check_sidebar(n, ids, problems):
    a, ln = n['attrs'], n['line']
    # (a)
    if n['tag'] != 'aside':
        problems.append(f'line {ln}: .al-sidebar on <{n["tag"]}> - the Sidebar is an <aside> (rule 26)')
    if not a.get('aria-label', '').strip() and not a.get('aria-labelledby'):
        problems.append(f'line {ln}: <aside> without a name (aria-label) (rule 26)')

    kids = n['kids']
    navs = [d for d in walk(n) if has(d, 'al-sidebar__nav')]
    # (c)
    if len(navs) != 1:
        problems.append(f'line {ln}: {len(navs)} .al-sidebar__nav - it is exactly one (rule 26)')
        return
    nav = navs[0]
    if nav['tag'] != 'nav' or not nav['attrs'].get('aria-label', '').strip():
        problems.append(f'line {nav["line"]}: .al-sidebar__nav must be <nav aria-label> (rule 26)')

    # (d) order
    order = [('profile' if has(k, 'al-sidebar__profile') else 'nav' if k is nav else None) for k in kids]
    if None in order or order not in (['profile', 'nav'], ['nav']):
        problems.append(f'line {ln}: Sidebar children out of the order profile, nav (rule 5)')
    nk = nav['kids']
    norder = [('content' if has(k, 'al-sidebar__content') else
               'support' if has(k, 'al-sidebar__support') else None) for k in nk]
    if norder not in (['content'], ['content', 'support']):
        problems.append(f'line {nav["line"]}: inside the nav the order is body and Help (optional) (rule 5)')

    # (e) (f) profile
    for prof in (d for d in walk(n) if has(d, 'al-sidebar__profile')):
        if any(p is nav for p in ancestors(prof)):
            problems.append(f'line {prof["line"]}: the profile stays OUTSIDE the <nav> (rule 26)')
        for av in (d for d in walk(prof) if has(d, 'al-avatar')):
            if av['attrs'].get('aria-hidden') != 'true':
                problems.append(f'line {av["line"]}: the profile Avatar is decorative - aria-hidden="true" (rule 18)')
            for img in (d for d in walk(av) if d['tag'] == 'img'):
                if img['attrs'].get('alt', None) != '':
                    problems.append(f'line {img["line"]}: profile photo with alt="" (rule 18)')
        name = [d for d in walk(prof) if has(d, 'al-sidebar__name')]
        if len(name) != 1 or not text_flat(name[0]):
            problems.append(f'line {prof["line"]}: the profile has one .al-sidebar__name with text (rule 18)')
        for b in (d for d in walk(prof) if d['tag'] in ('a', 'button')):
            if not has(b, 'al-icon-btn'):
                problems.append(f'line {b["line"]}: the profile action is an Icon Button (rule 19)')
            if not b['attrs'].get('aria-label', '').strip():
                problems.append(f'line {b["line"]}: profile button without a name (aria-label) (rule 19)')
            if b['tag'] == 'a' and 'href' not in b['attrs']:
                problems.append(f'line {b["line"]}: profile link without href (rule 19)')
            for s in walk(b):
                if s['tag'] == 'svg' and s['attrs'].get('aria-hidden') != 'true':
                    problems.append(f'line {s["line"]}: profile button svg without aria-hidden="true"')

    # (g) groups
    for g in (d for d in walk(nav) if has(d, 'al-sidebar__group')):
        labels = [k for k in g['kids'] if has(k, 'al-sidebar__group-label')]
        lists = [k for k in g['kids'] if k['tag'] == 'ul']
        if len(labels) != 1 or not text_flat(labels[0]) or not labels[0]['attrs'].get('id'):
            problems.append(f'line {g["line"]}: group without one label with text and id (rule 27)')
            continue
        if len(lists) != 1 or lists[0]['attrs'].get('aria-labelledby') != labels[0]['attrs']['id']:
            problems.append(f'line {g["line"]}: the group list has aria-labelledby pointing to its '
                            f'own label (rule 27)')
        # (l)
        if has(g, 'al-sidebar__support'):
            items = [d for d in walk(g) if has(d, 'al-tab')]
            if len(items) > 3:
                problems.append(f'line {g["line"]}: Help with {len(items)} items - at most 3 (rule 21)')
    for s in (d for d in walk(nav) if has(d, 'al-sidebar__support')):
        if not has(s, 'al-sidebar__group'):
            problems.append(f'line {s["line"]}: Help is a .al-sidebar__group (rule 21)')

    # (h) lists
    for ul in (d for d in walk(nav) if d['tag'] == 'ul'):
        if not (has(ul, 'al-tabs') and has(ul, 'al-tabs--square')):
            problems.append(f'line {ul["line"]}: a Sidebar list is .al-tabs.al-tabs--square (rule 11)')

    # (i) (j) (k) items
    current, labels_seen = 0, {}
    for it in (d for d in walk(nav) if has(d, 'al-tab')):
        ia = it['attrs']
        if it['tag'] != 'a' or 'href' not in ia:
            problems.append(f'line {it["line"]}: a Sidebar item is <a href> (rule 28)')
        if ia.get('role') == 'tab' or 'aria-selected' in ia:
            problems.append(f'line {it["line"]}: a navigation item is never role="tab"/aria-selected (rule 28)')
        lab = [d for d in walk(it) if has(d, 'al-tab__label')]
        txt = text_flat(lab[0]) if lab else ''
        if not txt:
            problems.append(f'line {it["line"]}: item without a .al-tab__label with text')
        elif txt.lower() in labels_seen:
            problems.append(f'line {it["line"]}: label "{txt}" repeated (line {labels_seen[txt.lower()]}) (rule 16)')
        else:
            labels_seen[txt.lower()] = it['line']
        cur = ia.get('aria-current')
        if cur is not None and cur != 'false':
            current += 1
            if cur != 'page':
                problems.append(f'line {it["line"]}: aria-current="{cur}" - in the Sidebar it is "page" (rule 28)')
    if current > 1:
        problems.append(f'line {ln}: {current} current items - at most one (rule 12)')


def markup_contract(path):
    if not os.path.exists(path):
        return None, [f'{path} does not exist']
    t = Tree()
    t.feed(open(path, encoding='utf-8').read())
    nodes = list(walk(t.root))
    ids = {n['attrs']['id']: n for n in nodes if 'id' in n['attrs']}
    order = {id(n): i for i, n in enumerate(nodes)}

    checked, problems, live = 0, [], []
    for n in nodes:
        if not has(n, 'al-sidebar'):
            continue
        checked += 1
        frozen = any('inert' in p['attrs'] for p in ancestors(n))
        if not frozen:
            live.append(n)
        if any(has(p, 'al-sidebar') for p in ancestors(n)):
            problems.append(f'line {n["line"]}: Sidebar inside a Sidebar (rule 4)')
        check_sidebar(n, ids, problems)

    # (b)
    if len(live) > 1:
        problems.append(f'{len(live)} live Sidebars in the document - one per screen (rule 4)')

    # (m)
    for n in nodes:
        target = n['attrs'].get('data-al-sidebar-open')
        if target is None:
            continue
        d = ids.get(target)
        if d is None or not has(d, 'al-sidebar'):
            problems.append(f'line {n["line"]}: data-al-sidebar-open="{target}" does not point to a .al-sidebar')
        if not n['attrs'].get('aria-label', '').strip():
            problems.append(f'line {n["line"]}: Menu button without aria-label (rule 24)')
        if n['attrs'].get('aria-controls') != target:
            problems.append(f'line {n["line"]}: Menu button with aria-controls different from the Sidebar id')
        if n['attrs'].get('aria-expanded') not in ('true', 'false'):
            problems.append(f'line {n["line"]}: Menu button without aria-expanded (rule 25)')

    # (n) skip to content, before the live Sidebar
    for s in live:
        skips = [n for n in nodes if n['tag'] == 'a' and n['attrs'].get('href', '').startswith('#')
                 and len(n['attrs']['href']) > 1 and order[id(n)] < order[id(s)]
                 and n['attrs']['href'][1:] in ids]
        if not skips:
            problems.append(f'line {s["line"]}: no "skip to content" link before the Sidebar (rule 29)')

    if checked == 0:
        return None, ['no .al-sidebar in the HTML']
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
    print('SIDEBAR ACCESSIBILITY QA')
    print('=' * 78)
    print('\nRENDERED COMBINATIONS (theme x role)')
    for r in rows:
        if r['invisible']:
            mark, note = 'XX', 'INVISIBLE - nothing separates the two backgrounds'
        elif r['pass']:
            mark, note = 'ok', 'pass'
        elif r['exception']:
            mark, note = '~~', f'exception "{r["exception"]}"'
        else:
            mark, note = 'XX', 'FAIL'
        print(f'  {mark} {r["theme"]:<5} {r["what"]:<38} x {r["bg"]:<22} '
              f'{r["ratio"]:5.2f} (floor {r["floor"]})  {note}')

    print('\nMARKUP CONTRACT')
    print(f'     source: {os.path.relpath(path, ROOT)}')
    if checked is None:
        for p in mk:
            print(f'     PENDING: {p}')
    else:
        print(f'     {checked} sidebar(s) checked, 14 rules (a-n)')
        for p in mk:
            print(f'     PROBLEM: {p}')

    print('-' * 78)
    print(f'{len(rows)} measurements  |  pass: {len(passing)}  |  exceptions: {len(excs)}  |  '
          f'fail: {len(fails) + len(invis)}')

    json.dump({
        'component': 'sidebar',
        'criterion': 'WCAG 1.4.3 text + 1.4.11 non-text + visible states on the Sidebar',
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
            print(f'   {r["theme"]} {r["what"]} x {r["bg"]}: {r["ratio"]}:1')
        failed = True
    if checked is not None and mk:
        print('-' * 78)
        print(f'{len(mk)} MARKUP PROBLEM(S) - gate fails')
        failed = True
    if checked is None:
        failed = True
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(run())
