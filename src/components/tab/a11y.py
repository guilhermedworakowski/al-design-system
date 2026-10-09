"""
Accessibility QA for the Tab.

As with the other components, validation is by RENDERED COMBINATION - type x
selected x state x theme x page - against the EFFECTIVE background, not a
loose token pair.

WHAT THE EFFECTIVE BACKGROUND CHANGES HERE

  The label measures against the background of the LABEL BOX when it has one
  (hover, pressed, selected Square) and against the PAGE when it doesn't (rest
  and focus of the unselected tab, selected Line at rest and focus). The page
  is the canvas or the surface - the sidebar usually sits on the surface.
  The Line's line, the selected Square's background and the ring measure
  against the page. The ring has a gap in `bg-canvas`, so it measures against
  both.

THREE JUDGMENTS

  1. Label: 4.5:1 floor from 1.4.3. The only exception is the brand one the
     Foundation already declares (`brand-on-dark-hover`: white on
     bg-brand-hover in dark, 3.85:1).
  2. Indicators (line, selected background, ring): 3:1 floor from 1.4.11. The
     gray line is `decorative-track`; the tonal background at rest and focus
     is `tonal-selection`. The pressed selected Square on the dark surface is
     `pressed-on-dark-surface` (2.74:1). The hover has no exception and must
     pass. The hover/pressed background of the UNSELECTED tab is not
     measured: it is pointer feedback, not a state that needs to be
     identified (the label darkens with it, and the label is what measures).
  3. INDISTINGUISHABLE selection - the selected tab equal to the unselected
     one in the same state: same background, same label color and same line.
     The exception covers a subtle selection, not a selection that doesn't
     exist. This fails.

THE MARKUP CONTRACT IS THE OTHER HALF OF THIS GATE

  Usage rules from guidelines.md, measured on the emitted HTML. Frozen samples
  (`aria-hidden="true"` + `inert`) are left out: they don't exist for the
  screen reader or the keyboard - but the sample has to be truly inert.

    a) panel group: `.al-tabs[role=tablist]` with a name (aria-label or an
       aria-labelledby that exists) (rule 21);
    b) a panel tab is `<button type="button" role="tab">` with aria-selected
       "true"/"false" and aria-controls pointing to a `role="tabpanel"` linked
       back by aria-labelledby (rule 21);
    c) exactly one selected per group, and the initial tabindex roves: the
       selected tab without tabindex=-1, the others with -1 (rules 7 and 21);
    d) navigation: a group that is not a tablist lives in a named `<nav>`,
       each tab is `<a href>`, no role="tab"/aria-selected, at most one
       aria-current (rule 22);
    e) every tab has a `.al-tab__label` with text - it is the announced name
       (rule 14);
    f) no disabled or aria-disabled (rule 18);
    g) nesting: at most two levels, Line outside and Square inside ("Tabs
       inside tabs" in guidelines.md);
    h) `<ul class="al-tabs">` only with `<li>` children, and the tab inside
       the `<li>`;
    i) unique ids in the document - tab and panel are linked by id (lesson
       from the Select);
    j) from 2 to 6 tabs per group (rule 8);
    k) the panel starts with a heading equal to the tab's label (rule 25 - it
       is what pays for `tonal-selection`);
    l) a frozen sample (aria-hidden) is `inert`.

RUN ORDER - same as the others: runs AFTER the HTML it measures.

Run: python3 a11y.py [path.html]
     with no argument, measures build/site/index.html
"""
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'tools'))
from paths import ROOT, TOKENS_JSON, SITE_HTML, comp_out  # noqa: E402
from contrast import cr  # noqa: E402
from htmltree import Tree, walk, has, ancestors, text_flat  # noqa: E402
FOUND = json.load(open(TOKENS_JSON))
TAB = json.load(open(comp_out('tab', 'tokens.json')))

SEM = FOUND['color']['semantic']
ALIAS = TAB['alias']
THEMES = ('light', 'dark')

TEXT_FLOOR = 4.5          # 1.4.3
NON_TEXT_FLOOR = 3.0      # 1.4.11
EXC_TRACK = 'decorative-track'
EXC_TONAL = 'tonal-selection'
EXC_BRAND = 'brand-on-dark-hover'
EXC_PRESSED = 'pressed-on-dark-surface'

PAGES = ('bg-canvas', 'bg-surface')
STATES = ('rest', 'hover', 'pressed', 'focus')

DEFAULT_HTML = SITE_HTML
OUT_JSON = comp_out('tab', 'a11y.json')

HEADINGS = {'h1', 'h2', 'h3', 'h4', 'h5', 'h6'}


def sem(name, theme):
    """tokens.json stores the semantic as [light, dark]."""
    v = SEM[name]
    return v[THEMES.index(theme)] if isinstance(v, list) else v[theme]


def tab(role, theme):
    """(semantic, hex) of a Tab role, following the alias."""
    ref = ALIAS[f'tab-{role}']
    return ref, sem(ref, theme)


# ─────────────────────────────────────────────── what each combination paints
def paint(kind, sel, state):
    """Roles for the label box background (None = transparent), the label and
    the line - exactly what tab.css picks for that combination."""
    if kind == 'square' and sel:
        pair = {'rest':    ('square-bg-selected', 'square-label-selected'),
                'focus':   ('square-bg-selected', 'square-label-selected'),
                'hover':   ('square-bg-selected-hover', 'square-label-selected-hover'),
                'pressed': ('square-bg-selected-active', 'square-label-selected-active')}[state]
        return pair[0], pair[1], None
    bg = {'rest': None, 'focus': None, 'hover': 'bg-hover', 'pressed': 'bg-active'}[state]
    if kind == 'line' and sel:
        label = 'line-label-selected'
    else:
        label = {'rest': 'label', 'focus': 'label',
                 'hover': 'label-hover', 'pressed': 'label-active'}[state]
    line = None
    if kind == 'line':
        line = 'line-indicator-selected' if sel else 'line-indicator'
    return bg, label, line


def row(theme, kind, sel, state, page, what, fg_name, fg, bg_name, bg, floor, exc=None):
    ratio = round(cr(fg, bg), 2)
    ok = ratio >= floor
    return {
        'theme': theme, 'type': kind, 'selected': sel, 'state': state, 'page': page,
        'what': what, 'fg': fg_name, 'fgHex': fg, 'bg': bg_name, 'bgHex': bg,
        'ratio': ratio, 'floor': floor, 'pass': ok, 'indistinct': False,
        'exception': None if ok else exc,
    }


def contrast_rows():
    rows = []
    for theme in THEMES:
        ring = sem('shadow-focus-default', theme)
        gap = sem('bg-canvas', theme)
        for page in PAGES:
            pg = sem(page, theme)
            for kind in ('line', 'square'):
                for sel in (False, True):
                    for state in STATES:
                        bg_role, lab_role, line_role = paint(kind, sel, state)
                        bg_name, bg_hex = tab(bg_role, theme) if bg_role else (page, pg)
                        lab_name, lab_hex = tab(lab_role, theme)

                        # 1. label against the effective background
                        exc = EXC_BRAND if (theme == 'dark' and lab_role == 'square-label-selected-hover') else None
                        rows.append(row(theme, kind, sel, state, page, 'label',
                                        lab_name, lab_hex, bg_name, bg_hex, TEXT_FLOOR, exc))

                        # 2a. the Line's line - only changes with selection, measured at rest
                        if line_role and state == 'rest':
                            ln, lh = tab(line_role, theme)
                            rows.append(row(theme, kind, sel, state, page, 'line', ln, lh,
                                            page, pg, NON_TEXT_FLOOR,
                                            None if sel else EXC_TRACK))

                        # 2b. selected Square background against the page
                        if kind == 'square' and sel:
                            exc = (EXC_TONAL if state in ('rest', 'focus')
                                   else EXC_PRESSED if state == 'pressed' else None)
                            rows.append(row(theme, kind, sel, state, page, 'selected-bg',
                                            bg_name, bg_hex, page, pg, NON_TEXT_FLOOR, exc))

                        # 2c. ring - around the label box, gap in bg-canvas
                        if state == 'focus':
                            worst = min((cr(ring, pg), page, pg),
                                        (cr(ring, gap), 'bg-canvas (gap)', gap))
                            rows.append(row(theme, kind, sel, state, page, 'ring',
                                            'shadow-focus-default', ring, worst[1], worst[2],
                                            NON_TEXT_FLOOR))

                # 3. indistinguishable selection: same paint with and without selection
                for state in STATES:
                    a = [tab(r, theme)[1] if r else pg for r in paint(kind, False, state)]
                    b = [tab(r, theme)[1] if r else pg for r in paint(kind, True, state)]
                    if [x.lower() for x in a] == [x.lower() for x in b]:
                        r = row(theme, kind, True, state, page, 'selection', '-', b[1],
                                '-', a[1], NON_TEXT_FLOOR)
                        r.update({'pass': False, 'indistinct': True, 'exception': None})
                        rows.append(r)
    return rows


# ─────────────────────────────────────────────── markup
def hidden_sample(node):
    """Frozen sample: inside (or being) aria-hidden="true"."""
    return any(n['attrs'].get('aria-hidden') == 'true' for n in [node, *ancestors(node)])


def tabs_of(group):
    """Tabs of the group, without descending into nested groups."""
    out = []

    def go(n):
        for k in n['kids']:
            if has(k, 'al-tabs'):
                continue
            if has(k, 'al-tab'):
                out.append(k)
            else:
                go(k)
    go(group)
    return out


def named(n, ids):
    a = n['attrs']
    if a.get('aria-label', '').strip():
        return True
    ref = a.get('aria-labelledby', '').split()
    return bool(ref) and all(r in ids for r in ref)


def markup_contract(path):
    if not os.path.exists(path):
        return None, 0, [f'{path} does not exist']
    t = Tree()
    t.feed(open(path, encoding='utf-8').read())
    nodes = list(walk(t.root))
    ids = {n['attrs']['id']: n for n in nodes if n['attrs'].get('id')}
    problems = []

    # (i) unique id
    for i, c in Counter(n['attrs']['id'] for n in nodes if n['attrs'].get('id')).items():
        if c > 1:
            problems.append(f'id "{i}" repeated {c} times - tab and panel are linked by id')

    groups, samples = 0, 0
    for g in nodes:
        if not has(g, 'al-tabs'):
            continue
        ln, a = g['line'], g['attrs']

        if hidden_sample(g):
            samples += 1
            # (l) the sample is inert
            owner = next((n for n in [g, *ancestors(g)] if n['attrs'].get('aria-hidden') == 'true'))
            if 'inert' not in owner['attrs']:
                problems.append(f'line {owner["line"]}: aria-hidden sample without inert - the '
                                f'keyboard reaches a tab the screen reader cannot see')
            continue

        groups += 1
        tabs = tabs_of(g)
        panel = a.get('role') == 'tablist'

        # (j) count
        if not 2 <= len(tabs) <= 6:
            problems.append(f'line {ln}: group with {len(tabs)} tab(s) - from 2 to 6 (rule 8)')

        # (g) nesting
        parents = [p for p in ancestors(g) if has(p, 'al-tabs')]
        level = 1 + sum(1 for p in nodes if has(p, 'al-tabs') and not hidden_sample(p)
                        and p is not g and _holds_panel_of(p, g, ids))
        if parents:
            problems.append(f'line {ln}: .al-tabs inside .al-tabs - the second level lives '
                            f'in the panel, not in the group')
        if level > 2:
            problems.append(f'line {ln}: {level} levels of tabs - two at most ("Tabs inside tabs")')
        if level == 2 and not has(g, 'al-tabs--square'):
            problems.append(f'line {ln}: second level in Line - the inner one is Square '
                            f'("Tabs inside tabs")')
        if level == 2 and _parent_level(g, nodes, ids) is not None and \
                has(_parent_level(g, nodes, ids), 'al-tabs--square'):
            problems.append(f'line {ln}: first level in Square - the outer one is Line '
                            f'("Tabs inside tabs")')

        # (h) list
        if g['tag'] in ('ul', 'ol'):
            for k in g['kids']:
                if k['tag'] != 'li':
                    problems.append(f'line {k["line"]}: <{k["tag"]}> directly in '
                                    f'<{g["tag"]} class="al-tabs"> - only <li>')

        if panel:
            # (a) group name
            if not named(g, ids):
                problems.append(f'line {ln}: tablist without a name - aria-label or aria-labelledby '
                                f'(rule 21)')
            selected = 0
            for tb in tabs:
                ta, tl = tb['attrs'], tb['line']
                # (b) element, role and state
                if tb['tag'] != 'button' or ta.get('type') != 'button' or ta.get('role') != 'tab':
                    problems.append(f'line {tl}: a panel tab must be <button type="button" '
                                    f'role="tab"> (rule 21)')
                sel = ta.get('aria-selected')
                if sel not in ('true', 'false'):
                    problems.append(f'line {tl}: aria-selected missing or invalid (rule 21)')
                if sel == 'true':
                    selected += 1
                # (c) initial tabindex
                ti = ta.get('tabindex')
                if sel == 'true' and ti == '-1':
                    problems.append(f'line {tl}: selected tab with tabindex=-1 - the Tab key '
                                    f'never enters the group (rule 21)')
                if sel == 'false' and ti != '-1':
                    problems.append(f'line {tl}: unselected tab without tabindex=-1 - the Tab '
                                    f'key stops on every one (rule 21)')
                # panel linked both ways
                pid = ta.get('aria-controls', '')
                p = ids.get(pid)
                if p is None or p['attrs'].get('role') != 'tabpanel':
                    problems.append(f'line {tl}: aria-controls="{pid}" does not point to a '
                                    f'role="tabpanel" (rule 21)')
                else:
                    if p['attrs'].get('aria-labelledby') != ta.get('id'):
                        problems.append(f'line {p["line"]}: panel "{pid}" without aria-labelledby '
                                        f'back to the tab (rule 21)')
                    # (k) heading equal to the label
                    h = next((d for d in walk(p) if d['tag'] in HEADINGS), None)
                    lab = _label(tb)
                    if h is None or text_flat(h) != lab:
                        problems.append(f'line {p["line"]}: panel "{pid}" does not start with the '
                                        f'heading "{lab}" - it is what pays for tonal-selection '
                                        f'(rule 25)')
            # (c) exactly one
            if tabs and selected != 1:
                problems.append(f'line {ln}: {selected} selected tabs - exactly '
                                f'one (rule 7)')
        else:
            # (d) navigation
            nav = next((p for p in ancestors(g) if p['tag'] == 'nav'), None)
            if nav is None:
                problems.append(f'line {ln}: .al-tabs without role="tablist" outside a <nav> - '
                                f'panel or navigation, one of the two (rules 21 and 22)')
            elif not named(nav, ids):
                problems.append(f'line {nav["line"]}: <nav> without a name (rule 22)')
            current = 0
            for tb in tabs:
                ta, tl = tb['attrs'], tb['line']
                if tb['tag'] != 'a' or 'href' not in ta:
                    problems.append(f'line {tl}: a navigation tab must be <a href> (rule 22)')
                if ta.get('role') == 'tab' or 'aria-selected' in ta:
                    problems.append(f'line {tl}: role="tab"/aria-selected on a link - promises '
                                    f'a panel that does not exist (rule 22)')
                if ta.get('aria-current') not in (None, 'false'):
                    current += 1
            if current > 1:
                problems.append(f'line {ln}: {current} links with aria-current - at most one '
                                f'(rule 22)')

        for tb in tabs:
            # (e) name
            lab = next((d for d in walk(tb) if has(d, 'al-tab__label')), None)
            if lab is None or not text_flat(lab):
                problems.append(f'line {tb["line"]}: .al-tab without an .al-tab__label with text '
                                f'(rule 14)')
            # (f) no disabled
            if 'disabled' in tb['attrs'] or 'aria-disabled' in tb['attrs']:
                problems.append(f'line {tb["line"]}: disabled tab - it leaves the group '
                                f'(rule 18)')

    # (h) tab outside a group
    for n in nodes:
        if has(n, 'al-tab') and not hidden_sample(n) and \
                not any(has(p, 'al-tabs') for p in ancestors(n)):
            problems.append(f'line {n["line"]}: .al-tab outside .al-tabs - the type belongs to '
                            f'the group (rule 6)')

    if groups == 0:
        return None, samples, ['no .al-tabs in the HTML - the component enters the site with '
                               'its playground; until then this gate stays PENDING']
    return groups, samples, problems


def _label(tb):
    lab = next((d for d in walk(tb) if has(d, 'al-tab__label')), None)
    return text_flat(lab) if lab else ''


def _panels(g, ids):
    for tb in tabs_of(g):
        p = ids.get(tb['attrs'].get('aria-controls', ''))
        if p is not None:
            yield p


def _holds_panel_of(p, g, ids):
    """Does group `p` have a panel that contains group `g`?"""
    return any(panel in list(ancestors(g)) for panel in _panels(p, ids))


def _parent_level(g, nodes, ids):
    return next((p for p in nodes if has(p, 'al-tabs') and p is not g
                 and _holds_panel_of(p, g, ids)), None)


def run():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_HTML
    rows = contrast_rows()
    indist = [r for r in rows if r['indistinct']]
    fails = [r for r in rows if not r['pass'] and not r['exception'] and not r['indistinct']]
    excs = [r for r in rows if r['exception']]
    passing = [r for r in rows if r['pass']]

    groups, samples, mk = markup_contract(path)

    print('=' * 84)
    print('TAB ACCESSIBILITY QA')
    print('=' * 84)
    print('\nRENDERED COMBINATIONS (theme x page x type x selected x state)')
    for r in rows:
        if r['indistinct']:
            mark, note = 'XX', 'INDISTINGUISHABLE - selected equal to unselected'
        elif r['pass']:
            mark, note = 'ok', 'pass'
        elif r['exception']:
            mark, note = '~~', f'exception "{r["exception"]}"'
        else:
            mark, note = 'XX', 'FAIL'
        sel = 'sel' if r['selected'] else '   '
        print(f'  {mark} {r["theme"]:<5} {r["page"]:<10} {r["type"]:<6} {sel} {r["state"]:<7} '
              f'{r["what"]:<17} x {r["bg"]:<21} {r["ratio"]:5.2f} (floor {r["floor"]})  {note}')

    print('\nMARKUP CONTRACT')
    print(f'     source: {os.path.relpath(path, ROOT)}')
    if groups is None:
        for p in mk:
            print(f'     PENDING: {p}')
    else:
        print(f'     {groups} group(s) checked, {samples} frozen sample(s), '
              f'12 rules (a-l)')
        for p in mk:
            print(f'     PROBLEM: {p}')

    print('-' * 84)
    print(f'{len(rows)} measurements  |  pass: {len(passing)}  |  exceptions: {len(excs)}  |  '
          f'fail: {len(fails) + len(indist)}')
    for key in (EXC_TRACK, EXC_TONAL, EXC_PRESSED, EXC_BRAND):
        print(f'  exception "{key}": {sum(1 for r in excs if r["exception"] == key)} measurements')

    json.dump({
        'component': 'tab',
        'criterion': 'WCAG 1.4.3 label + 1.4.11 indicators + distinguishable selection',
        'floors': {'text': TEXT_FLOOR, 'nonText': NON_TEXT_FLOOR},
        'markupSource': os.path.relpath(path, ROOT),
        'markupChecked': groups,
        'markupSamples': samples,
        'markupPending': groups is None,
        'markupProblems': mk if groups is not None else [],
        'rows': rows,
    }, open(OUT_JSON, 'w'), indent=2, ensure_ascii=False)
    print(f'{os.path.relpath(OUT_JSON, ROOT)} written')

    failed = False
    if indist or fails:
        print('-' * 84)
        print(f'{len(indist) + len(fails)} COMBINATION(S) FAIL:')
        for r in indist + fails:
            print(f'   {r["theme"]} {r["page"]} {r["type"]} sel={r["selected"]} {r["state"]} '
                  f'{r["what"]} x {r["bg"]}: {r["ratio"]}:1')
        failed = True
    if groups is not None and mk:
        print('-' * 84)
        print(f'{len(mk)} MARKUP PROBLEM(S) - gate fails')
        failed = True
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(run())
