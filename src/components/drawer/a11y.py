"""
Accessibility QA for the Drawer.

As with the other components, validation is by RENDERED COMBINATION - role x
theme - against the EFFECTIVE background, not a loose token pair.

WHAT THE EFFECTIVE BACKGROUND CHANGES HERE

  The Drawer is a layer, like the Modal: what the user sees behind it is the
  page DIMMED by the scrim, composited (scrim with transparency over
  bg-canvas or bg-surface). Inside it everything lives on
  `bg-surface-raised`, including the X and the footer buttons - so the pair
  that matters for them is not the Button/Icon Button's own (against canvas
  and surface) but against the panel.

FIVE JUDGMENTS

  1. Text (title and the X's ink): 4.5:1 floor from 1.4.3. It must pass.
  2. Focus ring and background of the action buttons INSIDE the panel: 3:1
     floor from 1.4.11. It must pass - and it is the pair the token layer
     doesn't measure.
  3. Panel against the dimmed page: 3:1. In dark it sits at ~1.8:1: that is
     the exception `card-not-separated-from-scrim-in-dark` (see tokens.py,
     the same as the Modal).
  4. INVISIBLE panel (equal to the dimmed page) fails. The exception covers
     a subtle separation, not its absence.
  5. -raised hover/pressed of the Ghost and the Secondary (and of the X): the
     text passes 4.5:1 on them AND they must be DIFFERENT from the panel. It
     was the Modal 0.18.1 defect (hover equal to the background, in dark,
     and the state disappeared); the Drawer is born with the override and
     this judgment locks it.

THE MARKUP CONTRACT IS THE OTHER HALF OF THIS GATE

  Usage rules from guidelines.md, measured on the emitted HTML:

    a) `.al-drawer` is a <dialog> (rule 24);
    b) no `open` in the markup: it opens through showModal(), never through
       the attribute or show(). The frozen ones in the matrix sit under
       `inert` and are exempt;
    c) aria-labelledby points to a .al-drawer__title that exists (rule 25);
    d) exactly one .al-drawer__title with text, inside the header (rule 6);
    e) children in the order header, body, actions - the actions are
       optional, and no divider or loose piece between the parts (rule 9);
    f) .al-drawer__actions, when it exists, has 1 or 2 actions (rule 20);
    g) the secondary action comes before the main one; the main one is
       Primary and NEVER Danger (rules 20 and 22);
    h) there is ALWAYS a visible way out (rule 14): the X, or the footer with
       a data-al-drawer-close button, or a <form method="dialog">;
    i) the X, when it exists, is an Icon Button (.al-icon-btn) with a
       non-empty aria-label, type="button", data-al-drawer-close and an
       aria-hidden svg; no other button without visible text inside the
       dialog (rule 26);
    j) never a Drawer inside a Drawer (rule 4);
    k) every data-al-drawer-open points to a <dialog class="al-drawer"> that
       exists;
    l) a button inside the footer has type="button" (or sits in a <form>):
       without it the click submits the form;
    m) size: at most one --sm|--md|--lg modifier (no modifier = md).

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
from htmltree import Tree, walk, classes, has, ancestors, text_of  # noqa: E402
FOUND = json.load(open(TOKENS_JSON))
DRW = json.load(open(comp_out('drawer', 'tokens.json')))
BTN = json.load(open(comp_out('button', 'tokens.json')))

SEM = FOUND['color']['semantic']
ALIAS = DRW['alias']
THEMES = ('light', 'dark')

TEXT_FLOOR = 4.5
NON_TEXT_FLOOR = 3.0
EXC_SCRIM = 'card-not-separated-from-scrim-in-dark'

DEFAULT_HTML = SITE_HTML
OUT_JSON = comp_out('drawer', 'a11y.json')

PAGES = (('canvas', 'bg-canvas'), ('surface', 'bg-surface'))


def sem(name, theme):
    v = SEM[name]
    return v[THEMES.index(theme)] if isinstance(v, list) else v[theme]


def drw(role, theme):
    return sem(ALIAS[f'drawer-{role}'], theme)


# ─────────────────────────────────────────────── contrast
def row(theme, what, fg_name, fg, bg_name, bg, floor, exc=None, invisible=False):
    ratio = round(cr(fg, bg), 2)
    ok = ratio >= floor
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
        card = drw('bg', theme)
        card_name = ALIAS['drawer-bg']

        # 1. title (and the body text, which inherits the same color) and the X's ink
        rows.append(row(theme, 'title', ALIAS['drawer-title'], drw('title', theme),
                        card_name, card, TEXT_FLOOR))
        rows.append(row(theme, 'x-icon-on-panel', 'text-primary', sem('text-primary', theme),
                        card_name, card, NON_TEXT_FLOOR))

        # 2. what lives INSIDE the panel - the pair the Button's gate doesn't measure
        rows.append(row(theme, 'ring-on-panel', 'shadow-focus-default',
                        sem('shadow-focus-default', theme), card_name, card, NON_TEXT_FLOOR))
        rows.append(row(theme, 'primary-button-on-panel', 'bg-brand', sem('bg-brand', theme),
                        card_name, card, NON_TEXT_FLOOR))
        sec = sem(BTN['alias']['button-secondary-border'], theme)
        rows.append(row(theme, 'secondary-border-on-panel',
                        BTN['alias']['button-secondary-border'], sec, card_name, card,
                        NON_TEXT_FLOOR))

        # 5. -raised hover and pressed: readable text AND different from the panel
        for state in ('hover', 'active'):
            name = f'bg-{state}-raised'
            bg = sem(name, theme)
            rows.append(row(theme, f'ghost-{state}-text', 'text-primary',
                            sem('text-primary', theme), name, bg, TEXT_FLOOR))
            rows.append(row(theme, f'ghost-{state}-distinct-from-panel', name, bg,
                            card_name, card, 1.0,
                            invisible=bg.lower() == card.lower()))

        # 3. panel against the page DIMMED by the scrim
        for name, role in PAGES:
            page = composite(drw('scrim', theme), sem(role, theme))
            rows.append(row(theme, f'panel-on-dimmed-{name}', card_name, card,
                            f'{role}+scrim', page, NON_TEXT_FLOOR, EXC_SCRIM,
                            invisible=card.lower() == page.lower()))
    return rows


# ─────────────────────────────────────────────── markup
def is_action(n):
    return n['tag'] == 'button' or (n['tag'] == 'a' and 'href' in n['attrs'])


PARTS = ('al-drawer__header', 'al-drawer__content', 'al-drawer__actions')


def markup_contract(path):
    if not os.path.exists(path):
        return None, [f'{path} does not exist']
    t = Tree()
    t.feed(open(path, encoding='utf-8').read())
    nodes = list(walk(t.root))
    ids = {n['attrs']['id']: n for n in nodes if 'id' in n['attrs']}

    checked, problems = 0, []

    # (k) every opener points to a <dialog>
    for n in nodes:
        target = n['attrs'].get('data-al-drawer-open')
        if target is not None:
            d = ids.get(target)
            if d is None or d['tag'] != 'dialog' or not has(d, 'al-drawer'):
                problems.append(f'line {n["line"]}: data-al-drawer-open="{target}" does not point to a '
                                f'<dialog class="al-drawer">')

    for n in nodes:
        a, tag, ln = n['attrs'], n['tag'], n['line']
        if not has(n, 'al-drawer'):
            continue
        checked += 1
        frozen = any('inert' in p['attrs'] for p in ancestors(n))

        # (a)
        if tag != 'dialog':
            problems.append(f'line {ln}: .al-drawer on <{tag}> - the Drawer is a native <dialog> (rule 24)')
            continue
        # (b)
        if 'open' in a and not frozen:
            problems.append(f'line {ln}: <dialog open> - the Drawer opens through showModal(), never '
                            f'through the attribute (rule 24)')
        # (j)
        if any(has(p, 'al-drawer') for p in ancestors(n)):
            problems.append(f'line {ln}: Drawer inside a Drawer (rule 4)')
        # (m)
        sizes = [c for c in classes(n) if c in ('al-drawer--sm', 'al-drawer--md', 'al-drawer--lg')]
        if len(sizes) > 1 or any(c.startswith('al-drawer--') and c not in sizes for c in classes(n)):
            problems.append(f'line {ln}: invalid size - one of --sm, --md or --lg')

        kids = [k for k in n['kids']]
        titles = [d for d in walk(n) if has(d, 'al-drawer__title')]
        headers = [k for k in kids if has(k, 'al-drawer__header')]
        # (d)
        if len(titles) != 1 or not text_of(titles[0]):
            problems.append(f'line {ln}: the Drawer needs exactly one .al-drawer__title with '
                            f'text (rule 6)')
        elif len(headers) != 1 or titles[0] not in list(walk(headers[0])):
            problems.append(f'line {ln}: the title lives inside the .al-drawer__header (rule 6)')
        # (c)
        lab = a.get('aria-labelledby')
        if not lab:
            problems.append(f'line {ln}: no aria-labelledby - the <dialog> doesn\'t name itself '
                            f'(rule 25)')
        elif lab not in ids or not has(ids[lab], 'al-drawer__title'):
            problems.append(f'line {ln}: aria-labelledby="{lab}" does not point to a '
                            f'.al-drawer__title (rule 25)')
        elif titles and ids[lab] is not titles[0]:
            problems.append(f'line {ln}: aria-labelledby points to the title of ANOTHER Drawer (rule 25)')

        # (e) order header, body, actions; actions optional
        order = [next((c for c in PARTS if has(k, c)), None) for k in kids]
        expected = [c for c in PARTS if c in order]
        if [o for o in order if o] != expected or (order and order[0] != 'al-drawer__header'):
            problems.append(f'line {ln}: children out of the order header, body, actions (rule 9)')
        if any(o is None for o in order):
            problems.append(f'line {ln}: direct child without a Drawer class - no divider or '
                            f'loose piece between the parts (rule 9)')
        if 'al-drawer__content' not in order:
            problems.append(f'line {ln}: the .al-drawer__content is missing')

        # (i) the X
        head = headers[0] if headers else None
        x_btns = [d for d in walk(head) if is_action(d)] if head else []
        for x in x_btns:
            if not has(x, 'al-icon-btn'):
                problems.append(f'line {x["line"]}: the only button in the header is the X, an Icon Button (rule 26)')
                continue
            if not x['attrs'].get('aria-label', '').strip():
                problems.append(f'line {x["line"]}: X without aria-label - an Icon Button without a name is a mute button (rule 26)')
            if x['attrs'].get('type') != 'button':
                problems.append(f'line {x["line"]}: X without type="button"')
            if 'data-al-drawer-close' not in x['attrs']:
                problems.append(f'line {x["line"]}: X without data-al-drawer-close - it doesn\'t close')
            for s in walk(x):
                if s['tag'] == 'svg' and s['attrs'].get('aria-hidden') != 'true':
                    problems.append(f'line {s["line"]}: the X\'s svg without aria-hidden="true"')
        if len(x_btns) > 1:
            problems.append(f'line {ln}: more than one button in the header (only the X)')
        has_x = len(x_btns) == 1 and has(x_btns[0], 'al-icon-btn')

        # other buttons without a visible label (besides the X)
        for d in walk(n):
            if d['tag'] == 'button' and not text_of(d) and d not in x_btns:
                problems.append(f'line {d["line"]}: button without visible text besides the X (rule 26)')

        actions_box = [k for k in kids if has(k, 'al-drawer__actions')]
        actions = []
        if len(actions_box) > 1:
            problems.append(f'line {ln}: more than one .al-drawer__actions')
        elif actions_box:
            actions = [d for d in walk(actions_box[0]) if is_action(d)]
            # (f)
            if not 1 <= len(actions) <= 2:
                problems.append(f'line {ln}: {len(actions)} actions in the footer - one or two (rule 20)')
            # (g)
            if len(actions) == 2:
                first, last = actions
                if has(first, 'al-btn--primary') or has(first, 'al-btn--danger'):
                    problems.append(f'line {first["line"]}: the main action comes LAST; the '
                                    f'first one is the secondary (rule 20)')
                if not has(last, 'al-btn--primary'):
                    problems.append(f'line {last["line"]}: the last action should be Primary - '
                                    f'a destructive one opens a Modal, it is not the Drawer\'s main action (rules 20 and 22)')
            if len(actions) == 1 and has(actions[0], 'al-btn--danger'):
                problems.append(f'line {actions[0]["line"]}: Danger is not the Drawer\'s main action (rule 22)')
            # (l) type
            for ac in actions:
                if ac['tag'] == 'button' and ac['attrs'].get('type') not in ('button', 'submit', 'reset'):
                    problems.append(f'line {ac["line"]}: <button> without type - inside a <form> the '
                                    f'default is submit')

        # (h) always a visible way out
        footer_exit = any('data-al-drawer-close' in d['attrs'] for d in actions) or \
            any(d['tag'] == 'form' and d['attrs'].get('method') == 'dialog' for d in walk(n))
        if not has_x and not footer_exit:
            problems.append(f'line {ln}: no visible way out - no X and no footer button that '
                            f'closes (rule 14)')
        if not has_x and not actions:
            problems.append(f'line {ln}: no X and no footer - the Drawer has no visible way out (rule 14)')

    if checked == 0:
        return None, ['no .al-drawer in the HTML']
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
    print('DRAWER ACCESSIBILITY QA')
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
        print(f'  {mark} {r["theme"]:<5} {r["what"]:<36} x {r["bg"]:<20} '
              f'{r["ratio"]:5.2f} (floor {r["floor"]})  {note}')

    print('\nMARKUP CONTRACT')
    print(f'     source: {os.path.relpath(path, ROOT)}')
    if checked is None:
        for p in mk:
            print(f'     PENDING: {p}')
    else:
        print(f'     {checked} drawer(s) checked, 13 rules (a-m)')
        for p in mk:
            print(f'     PROBLEM: {p}')

    print('-' * 78)
    print(f'{len(rows)} measurements  |  pass: {len(passing)}  |  exceptions: {len(excs)}  |  '
          f'fail: {len(fails) + len(invis)}')

    json.dump({
        'component': 'drawer',
        'criterion': 'WCAG 1.4.3 text + 1.4.11 non-text + visible panel + distinct -raised hover',
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
