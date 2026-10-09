"""
Accessibility QA for the Card.

As with the other components, validation is by RENDERED COMBINATION - type x
state x theme x page the card is placed on - against the EFFECTIVE background,
not a loose token pair.

WHAT THE EFFECTIVE BACKGROUND CHANGES HERE

  Text measures against the card background (`bg-surface-raised`), the same
  in all three types. Border, ring and the card itself measure against the
  PAGE, and the page changes per type, because the usage rules say so:
    - Filled only on `bg-surface` (rule 2) - on the canvas it disappears;
    - Border and Elevated on the canvas or on the surface (rules 3 and 4).
  The focus ring is drawn OUTSIDE the card, on the page, with the gap in
  `bg-canvas` - that is why it measures against both pages.

THREE JUDGMENTS

  1. Text: 4.5:1 floor from 1.4.3. It must pass - no exception.
  2. Border, ring and card boundary: 3:1 floor from 1.4.11. The border at
     rest and the boundary by background fall below, and those are the
     declared exceptions `border-below-3-1` and `card-not-separated-by-bg`.
     Hover and focus must pass.
  3. INVISIBLE card - no clue separates the card from the page: same
     background, no border and no shadow. The exception covers a subtle card,
     not a card that doesn't exist. This fails. The Elevated on the light
     canvas has the same background but has a shadow, so it isn't invisible;
     the Filled on the canvas would be, and that is why the combination
     isn't even measured - rule 2 forbids it.

THE MARKUP CONTRACT IS THE OTHER HALF OF THIS GATE

  Usage rules from guidelines.md, measured on the emitted HTML:

    a) `.al-card__title` is a real heading, h1 to h6 (rule 11);
    b) a clickable card has ONE `.al-card__link`, and it lives inside the
       title (rules 13 and 16);
    c) `.al-card__link` is `<a href>` or `<button type="button">`, with a
       name (rule 16);
    d) nothing clickable besides the link inside a clickable card - link,
       button, field, tabindex (rule 15);
    e) the card itself is not clickable: no <a>/<button>, no onclick, no
       tabindex, no actionable role (rule 16);
    f) `.al-card__link` outside a clickable card doesn't exist - without the
       modifier the link stretches with no hover or ring (rule 13);
    g) `<li class="al-card">` only inside <ul>/<ol> (rule 22);
    h) no card inside a card (rule 6);
    i) no disabled: neither `disabled` nor `aria-disabled` on the card
       (rule 19);
    j) one type and one padding per card - `--border` with `--elevated`, or
       `--spaced` with `--tight`, is contradictory markup.

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
from htmltree import Tree, walk, classes, has, ancestors, text_of  # noqa: E402
FOUND = json.load(open(TOKENS_JSON))
CARD = json.load(open(comp_out('card', 'tokens.json')))

SEM = FOUND['color']['semantic']
ALIAS = CARD['alias']
THEMES = ('light', 'dark')

TEXT_FLOOR = 4.5          # 1.4.3
NON_TEXT_FLOOR = 3.0      # 1.4.11
EXC_BORDER = 'border-below-3-1'
EXC_BG = 'card-not-separated-by-bg'

DEFAULT_HTML = SITE_HTML
OUT_JSON = comp_out('card', 'a11y.json')

# pages each type can be placed on (rules 2, 3 and 4)
PAGES = {
    'filled':   ('bg-surface',),
    'border':   ('bg-canvas', 'bg-surface'),
    'elevated': ('bg-canvas', 'bg-surface'),
}

HEADINGS = {'h1', 'h2', 'h3', 'h4', 'h5', 'h6'}
ACTIONABLE_ROLES = {'button', 'link', 'checkbox', 'radio', 'switch', 'menuitem', 'tab', 'option'}


def sem(name, theme):
    """tokens.json stores the semantic as [light, dark]."""
    v = SEM[name]
    return v[THEMES.index(theme)] if isinstance(v, list) else v[theme]


def card(role, theme):
    """Color of a Card role, following the alias down to the semantic."""
    return sem(ALIAS[f'card-{role}'], theme)


# ─────────────────────────────────────────────── contrast
def row(theme, kind, state, what, fg_name, fg, bg_name, bg, floor, exc=None, invisible=False):
    ratio = round(cr(fg, bg), 2)
    ok = ratio >= floor
    return {
        'theme': theme, 'type': kind, 'state': state, 'what': what,
        'fg': fg_name, 'fgHex': fg, 'bg': bg_name, 'bgHex': bg,
        'ratio': ratio, 'floor': floor, 'pass': ok,
        'invisible': invisible,
        'exception': None if ok or invisible else exc,
    }


def contrast_rows():
    rows = []
    for theme in THEMES:
        bg = card('bg', theme)
        ring = sem('shadow-focus-default', theme)

        # 1. text - the card background is the same in all types and states
        for role, what in (('title', 'title'), ('description', 'description')):
            rows.append(row(theme, 'all', 'all', what,
                            ALIAS[f'card-{role}'], card(role, theme),
                            'card-bg', bg, TEXT_FLOOR))

        for kind, pages in PAGES.items():
            for page in pages:
                pg = sem(page, theme)

                # 2. card boundary at rest
                if kind == 'border':
                    border = card('border', theme)
                    worst = min((cr(border, bg), 'card-bg', bg),
                                (cr(border, pg), page, pg))
                    rows.append(row(theme, kind, 'rest', 'border',
                                    ALIAS['card-border'], border, worst[1], worst[2],
                                    NON_TEXT_FLOOR, EXC_BORDER,
                                    invisible=border.lower() in (bg.lower(), pg.lower())))
                else:
                    # no border: the boundary is the card background against the
                    # page. The Elevated has a shadow, so an equal background
                    # doesn't erase it.
                    has_shadow = kind == 'elevated'
                    rows.append(row(theme, kind, 'rest', 'bg-boundary',
                                    'card-bg', bg, page, pg,
                                    NON_TEXT_FLOOR, EXC_BG,
                                    invisible=(bg.lower() == pg.lower() and not has_shadow)))

                # 3. hover and focus - only the Border changes the border color
                if kind == 'border':
                    for state, role in (('hover', 'border-hover'), ('focus', 'border-focus')):
                        c = card(role, theme)
                        worst = min((cr(c, bg), 'card-bg', bg), (cr(c, pg), page, pg))
                        rows.append(row(theme, kind, state, 'border',
                                        ALIAS[f'card-{role}'], c, worst[1], worst[2],
                                        NON_TEXT_FLOOR))

                # 4. ring - outside the card, on the page; the gap is bg-canvas
                gap = sem('bg-canvas', theme)
                worst = min((cr(ring, pg), page, pg), (cr(ring, gap), 'bg-canvas (gap)', gap))
                rows.append(row(theme, kind, 'focus', 'ring',
                                'shadow-focus-default', ring, worst[1], worst[2],
                                NON_TEXT_FLOOR))
    return rows


# ─────────────────────────────────────────────── markup
def interactive(node):
    a, tag = node['attrs'], node['tag']
    if tag == 'a' and 'href' in a:
        return True
    if tag in ('button', 'input', 'select', 'textarea', 'summary'):
        return True
    if 'tabindex' in a and a['tabindex'] != '-1':
        return True
    return a.get('role') in ACTIONABLE_ROLES


def markup_contract(path):
    if not os.path.exists(path):
        return None, [f'{path} does not exist']
    t = Tree()
    t.feed(open(path, encoding='utf-8').read())

    checked, problems = 0, []
    for n in walk(t.root):
        a, tag, ln = n['attrs'], n['tag'], n['line']

        # (a) the title is a heading
        if has(n, 'al-card__title') and tag not in HEADINGS:
            problems.append(f'line {ln}: .al-card__title on <{tag}> - the card title is '
                            f'h1-h6 according to the page, never a paragraph (rule 11)')

        # (f) link without a clickable card
        if has(n, 'al-card__link'):
            owner = next((p for p in ancestors(n) if has(p, 'al-card')), None)
            if owner is None or not has(owner, 'al-card--clickable'):
                problems.append(f'line {ln}: .al-card__link outside .al-card--clickable - '
                                f'the link stretches over the card with no hover or ring (rule 13)')

        if not has(n, 'al-card'):
            continue
        checked += 1
        cl = classes(n)

        # (e) the card itself is not actionable
        if tag in ('a', 'button'):
            problems.append(f'line {ln}: .al-card on <{tag}> - the link goes in the title and '
                            f'stretches; it never wraps the card (rule 16)')
        if 'tabindex' in a:
            problems.append(f'line {ln}: tabindex on the card - the title link is what '
                            f'receives Tab (rule 16)')
        if any(k.startswith('on') for k in a):
            problems.append(f'line {ln}: event handler on the card - use the title '
                            f'link (rule 16)')
        if a.get('role') in ACTIONABLE_ROLES:
            problems.append(f'line {ln}: role="{a["role"]}" on the card - the card is not '
                            f'actionable, the title link is (rule 16)')

        # (g) list item
        if tag == 'li' and n['parent']['tag'] not in ('ul', 'ol'):
            problems.append(f'line {ln}: <li class="al-card"> outside <ul>/<ol> (rule 22)')

        # (h) card inside a card
        if any(has(p, 'al-card') for p in ancestors(n)):
            problems.append(f'line {ln}: card inside a card - subdivide with a Divider or '
                            f'a heading (rule 6)')

        # (i) no disabled
        if 'disabled' in a or 'aria-disabled' in a:
            problems.append(f'line {ln}: disabled card - it hides or explains itself in '
                            f'the content (rule 19)')

        # (j) consistent modifiers
        if 'al-card--border' in cl and 'al-card--elevated' in cl:
            problems.append(f'line {ln}: --border and --elevated on the same card - one type only')
        if 'al-card--spaced' in cl and 'al-card--tight' in cl:
            problems.append(f'line {ln}: --spaced and --tight on the same card - one padding only')

        if 'al-card--clickable' not in cl:
            continue

        # (b) one link, inside the title
        desc = list(walk(n))
        links = [d for d in desc if has(d, 'al-card__link')]
        if len(links) != 1:
            problems.append(f'line {ln}: clickable card with {len(links)} .al-card__link - '
                            f'it must be exactly one (rule 13)')
        for lk in links:
            if not any(has(p, 'al-card__title') for p in ancestors(lk)):
                problems.append(f'line {lk["line"]}: .al-card__link outside the title - the '
                                f'announced name must be the title (rule 16)')
            # (c) element and name
            la = lk['attrs']
            if lk['tag'] == 'a' and 'href' not in la:
                problems.append(f'line {lk["line"]}: <a class="al-card__link"> without href - '
                                f'it is not a link, it doesn\'t receive Tab (rule 16)')
            elif lk['tag'] == 'button' and la.get('type') != 'button':
                problems.append(f'line {lk["line"]}: <button class="al-card__link"> without '
                                f'type="button" - inside a form it would submit (rule 16)')
            elif lk['tag'] not in ('a', 'button'):
                problems.append(f'line {lk["line"]}: .al-card__link on <{lk["tag"]}> - '
                                f'use <a href> or <button type="button"> (rule 16)')
            if not text_of(lk) and not la.get('aria-label'):
                problems.append(f'line {lk["line"]}: .al-card__link without a name (rule 16)')

        # (d) nothing clickable besides the link
        for d in desc:
            if d in links or any(d is x for lk in links for x in walk(lk)):
                continue
            if interactive(d):
                problems.append(f'line {d["line"]}: interactive <{d["tag"]}> inside a clickable '
                                f'card - target overlapping the link (rule 15)')

    if checked == 0:
        return None, ['no .al-card in the HTML - the component enters the site with '
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
    print('CARD ACCESSIBILITY QA')
    print('=' * 78)
    print('\nRENDERED COMBINATIONS (theme x type x state x page)')
    for r in rows:
        if r['invisible']:
            mark, note = 'XX', 'INVISIBLE - nothing separates the card from the page'
        elif r['pass']:
            mark, note = 'ok', 'pass'
        elif r['exception']:
            mark, note = '~~', f'exception "{r["exception"]}"'
        else:
            mark, note = 'XX', 'FAIL'
        print(f'  {mark} {r["theme"]:<5} {r["type"]:<8} {r["state"]:<7} {r["what"]:<17} '
              f'x {r["bg"]:<19} {r["ratio"]:5.2f} (floor {r["floor"]})  {note}')

    print('\nMARKUP CONTRACT')
    print(f'     source: {os.path.relpath(path, ROOT)}')
    if checked is None:
        for p in mk:
            print(f'     PENDING: {p}')
    else:
        print(f'     {checked} card(s) checked, 10 rules (a-j)')
        for p in mk:
            print(f'     PROBLEM: {p}')

    print('-' * 78)
    print(f'{len(rows)} measurements  |  pass: {len(passing)}  |  exceptions: {len(excs)}  |  '
          f'fail: {len(fails) + len(invis)}')

    json.dump({
        'component': 'card',
        'criterion': 'WCAG 1.4.3 text + 1.4.11 non-text + visible card',
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
            print(f'   {r["theme"]} {r["type"]} {r["state"]} {r["what"]} x {r["bg"]}: {r["ratio"]}:1')
        failed = True
    if checked is not None and mk:
        print('-' * 78)
        print(f'{len(mk)} MARKUP PROBLEM(S) - gate fails')
        failed = True
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(run())
