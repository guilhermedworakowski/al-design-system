"""
Accessibility QA for the Modal.

As with the other components, validation is by RENDERED COMBINATION - role x
theme - against the EFFECTIVE background, not a loose token pair.

WHAT THE EFFECTIVE BACKGROUND CHANGES HERE

  The Modal is a layer: what the user sees behind it is the page DIMMED by
  the scrim, composited (scrim with transparency over bg-canvas or
  bg-surface). Inside it everything lives on `bg-surface-raised`, including
  the footer buttons - so the pair that matters for the button is not the
  Button's own (against canvas and surface) but against the card.

FOUR JUDGMENTS

  1. Text (title): 4.5:1 floor from 1.4.3. It must pass.
  2. Focus ring of the buttons and fields INSIDE the card, and background of
     the action buttons against the card: 3:1 floor from 1.4.11. It must
     pass - and it is the pair the token layer doesn't measure.
  3. Card against the dimmed page: 3:1. In dark it sits at ~1.8:1: that is
     the exception `card-not-separated-from-scrim-in-dark` (see tokens.py).
  4. INVISIBLE card (equal to the dimmed page) fails. The exception covers a
     subtle separation, not its absence.

THE MARKUP CONTRACT IS THE OTHER HALF OF THIS GATE

  Usage rules from guidelines.md, measured on the emitted HTML:

    a) `.al-modal` is a <dialog> (rule 24);
    b) no `open` in the markup: it opens through showModal(), never through
       the attribute or show(). The frozen ones in the matrix sit under
       `inert` and are exempt;
    c) aria-labelledby points to a .al-modal__title that exists (rule 25);
    d) exactly one .al-modal__title with text, first child (rule 5);
    e) children in the order title, body, actions (rule 10 - no divider);
    f) .al-modal__actions with 1 or 2 actions (rules 16 and 19);
    g) the secondary action comes before the main one; the main one is
       Primary or Danger, never the first (rules 19 and 20);
    h) there is a way out: a button with data-al-modal-close, or a <form
       method="dialog"> (rule 16);
    i) no X button: nothing with .al-modal__close, nor a button without a
       visible label inside the dialog (rule 16);
    j) never a Modal inside a Modal (rule 4);
    k) every data-al-modal-open points to a <dialog> that exists;
    l) a button inside the footer has type="button" (or sits in a <form>):
       without it the click submits the form.

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
from htmltree import Tree, walk, has, ancestors, text_of  # noqa: E402
FOUND = json.load(open(TOKENS_JSON))
MOD = json.load(open(comp_out('modal', 'tokens.json')))
BTN = json.load(open(comp_out('button', 'tokens.json')))

SEM = FOUND['color']['semantic']
ALIAS = MOD['alias']
THEMES = ('light', 'dark')

TEXT_FLOOR = 4.5
NON_TEXT_FLOOR = 3.0
EXC_SCRIM = 'card-not-separated-from-scrim-in-dark'

DEFAULT_HTML = SITE_HTML
OUT_JSON = comp_out('modal', 'a11y.json')

PAGES = (('canvas', 'bg-canvas'), ('surface', 'bg-surface'))


def sem(name, theme):
    v = SEM[name]
    return v[THEMES.index(theme)] if isinstance(v, list) else v[theme]


def mod(role, theme):
    return sem(ALIAS[f'modal-{role}'], theme)


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
        card = mod('bg', theme)
        card_name = ALIAS['modal-bg']

        # 1. title (and the body text, which inherits the same color)
        rows.append(row(theme, 'title', ALIAS['modal-title'], mod('title', theme),
                        card_name, card, TEXT_FLOOR))

        # 2. what lives INSIDE the card - the pair the Button's gate doesn't measure
        ring = sem('shadow-focus-default', theme)
        rows.append(row(theme, 'ring-on-card', 'shadow-focus-default', ring,
                        card_name, card, NON_TEXT_FLOOR))
        rows.append(row(theme, 'primary-button-on-card', 'bg-brand', sem('bg-brand', theme),
                        card_name, card, NON_TEXT_FLOOR))
        rows.append(row(theme, 'danger-button-on-card', 'bg-danger', sem('bg-danger', theme),
                        card_name, card, NON_TEXT_FLOOR))
        sec = sem(BTN['alias']['button-secondary-border'], theme)
        rows.append(row(theme, 'secondary-border-on-card',
                        BTN['alias']['button-secondary-border'], sec, card_name, card,
                        NON_TEXT_FLOOR))

        # 3. card against the page DIMMED by the scrim
        for name, role in PAGES:
            page = composite(mod('scrim', theme), sem(role, theme))
            rows.append(row(theme, f'card-on-dimmed-{name}', card_name, card,
                            f'{role}+scrim', page, NON_TEXT_FLOOR, EXC_SCRIM,
                            invisible=card.lower() == page.lower()))
    return rows


# ─────────────────────────────────────────────── markup
def is_action(n):
    return n['tag'] == 'button' or (n['tag'] == 'a' and 'href' in n['attrs'])


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
        target = n['attrs'].get('data-al-modal-open')
        if target is not None:
            d = ids.get(target)
            if d is None or d['tag'] != 'dialog' or not has(d, 'al-modal'):
                problems.append(f'line {n["line"]}: data-al-modal-open="{target}" does not point to a '
                                f'<dialog class="al-modal">')

    for n in nodes:
        a, tag, ln = n['attrs'], n['tag'], n['line']
        if not has(n, 'al-modal'):
            continue
        checked += 1
        frozen = any('inert' in p['attrs'] for p in ancestors(n))

        # (a)
        if tag != 'dialog':
            problems.append(f'line {ln}: .al-modal on <{tag}> - the Modal is a native <dialog> (rule 24)')
            continue
        # (b)
        if 'open' in a and not frozen:
            problems.append(f'line {ln}: <dialog open> - the Modal opens through showModal(), never '
                            f'through the attribute (rule 24)')
        # (j)
        if any(has(p, 'al-modal') for p in ancestors(n)):
            problems.append(f'line {ln}: Modal inside a Modal (rule 4)')

        kids = [k for k in n['kids'] if k['tag'] != '#text']
        titles = [d for d in walk(n) if has(d, 'al-modal__title')]
        # (d)
        if len(titles) != 1 or not text_of(titles[0]):
            problems.append(f'line {ln}: the Modal needs exactly one .al-modal__title with '
                            f'text (rule 5)')
        # (c)
        lab = a.get('aria-labelledby')
        if not lab:
            problems.append(f'line {ln}: no aria-labelledby - the <dialog> doesn\'t name itself '
                            f'(rule 25)')
        elif lab not in ids or not has(ids[lab], 'al-modal__title'):
            problems.append(f'line {ln}: aria-labelledby="{lab}" does not point to a '
                            f'.al-modal__title (rule 25)')
        elif titles and ids[lab] is not titles[0]:
            problems.append(f'line {ln}: aria-labelledby points to the title of ANOTHER Modal (rule 25)')

        # (e) order title, body, actions
        order = [next((c for c in ('al-modal__title', 'al-modal__content', 'al-modal__actions')
                       if has(k, c)), None) for k in kids]
        expected = [c for c in ('al-modal__title', 'al-modal__content', 'al-modal__actions')
                    if c in order]
        if [o for o in order if o] != expected or order and order[0] != 'al-modal__title':
            problems.append(f'line {ln}: children out of the order title, body, actions (rule 10)')
        if any(o is None for o in order):
            problems.append(f'line {ln}: direct child without a Modal class - no divider or '
                            f'loose piece between the parts (rule 10)')

        # (i) no X
        if any(has(d, 'al-modal__close') for d in walk(n)):
            problems.append(f'line {ln}: .al-modal__close - the Modal has no X button (rule 16)')

        actions_box = [k for k in kids if has(k, 'al-modal__actions')]
        if len(actions_box) != 1:
            problems.append(f'line {ln}: the Modal needs exactly one .al-modal__actions '
                            f'(rules 16 and 22)')
            continue
        actions = [d for d in walk(actions_box[0]) if is_action(d)]
        # (f)
        if not 1 <= len(actions) <= 2:
            problems.append(f'line {ln}: {len(actions)} actions in the footer - one or two (rules 16 and 19)')
        # (g)
        if len(actions) == 2:
            first, last = actions
            for ac in (first,):
                if has(ac, 'al-btn--primary') or has(ac, 'al-btn--danger'):
                    problems.append(f'line {ac["line"]}: the main action comes LAST; the '
                                    f'first one is the secondary (rules 19 and 20)')
            if not (has(last, 'al-btn--primary') or has(last, 'al-btn--danger')):
                problems.append(f'line {last["line"]}: the last action should be Primary or '
                                f'Danger (rules 19 and 20)')
        # (h) way out
        way_out = any('data-al-modal-close' in d['attrs'] for d in walk(n)) or \
            any(d['tag'] == 'form' and d['attrs'].get('method') == 'dialog' for d in walk(n))
        if not way_out:
            problems.append(f'line {ln}: no way out - no data-al-modal-close nor '
                            f'<form method="dialog"> (rule 16)')
        # (i) button without a visible label inside the dialog
        for d in walk(n):
            if d['tag'] == 'button' and not text_of(d):
                problems.append(f'line {d["line"]}: button without visible text - the Modal has no X '
                                f'nor an icon-only button (rule 16)')
        # (l) type="button"
        for ac in actions:
            if ac['tag'] == 'button' and ac['attrs'].get('type') not in ('button', 'submit', 'reset'):
                problems.append(f'line {ac["line"]}: <button> without type - inside a <form> the '
                                f'default is submit')

    if checked == 0:
        return None, ['no .al-modal in the HTML']
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
    print('MODAL ACCESSIBILITY QA')
    print('=' * 78)
    print('\nRENDERED COMBINATIONS (theme x role)')
    for r in rows:
        if r['invisible']:
            mark, note = 'XX', 'INVISIBLE - nothing separates the card from the page'
        elif r['pass']:
            mark, note = 'ok', 'pass'
        elif r['exception']:
            mark, note = '~~', f'exception "{r["exception"]}"'
        else:
            mark, note = 'XX', 'FAIL'
        print(f'  {mark} {r["theme"]:<5} {r["what"]:<32} x {r["bg"]:<24} '
              f'{r["ratio"]:5.2f} (floor {r["floor"]})  {note}')

    print('\nMARKUP CONTRACT')
    print(f'     source: {os.path.relpath(path, ROOT)}')
    if checked is None:
        for p in mk:
            print(f'     PENDING: {p}')
    else:
        print(f'     {checked} modal(s) checked, 12 rules (a-l)')
        for p in mk:
            print(f'     PROBLEM: {p}')

    print('-' * 78)
    print(f'{len(rows)} measurements  |  pass: {len(passing)}  |  exceptions: {len(excs)}  |  '
          f'fail: {len(fails) + len(invis)}')

    json.dump({
        'component': 'modal',
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
