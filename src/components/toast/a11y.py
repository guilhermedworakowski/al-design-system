"""
Accessibility QA for the Toast.

As with the other components, validation is by RENDERED COMBINATION - role x
status x theme - against the EFFECTIVE background, not a loose token pair.

WHAT THE EFFECTIVE BACKGROUND CHANGES HERE

  The toast lives in the top layer (the region is a popover), with an opaque
  `toast-bg` background (bg-surface-raised): title, description, icon and the
  X only touch the toast's own background. What touches the page is the
  BORDER - and the page can be the canvas, the surface or an open
  Modal/Drawer (bg-surface-raised), because with a dialog open the region
  moves inside it. Over the Modal, toast background and page background are
  the same color: only the border separates them.

  The X is the Ghost sm Icon Button. On surface-raised it uses the -raised
  ones (bg-hover-raised / bg-active-raised, lesson from Modal 0.18.1): the
  icon ink is measured against the rest, hover and pressed backgrounds. The
  focus ring is measured against the toast background - a pair the Icon
  Button gate, measured on the page, doesn't cover.

FOUR JUDGMENTS

  1. Title and description against the toast background: 4.5:1 from 1.4.3.
  2. Status icon against the toast background: 3:1 from 1.4.11. The icon is
     what carries the status (rule 14), so it must pass.
  3. Border of each status against each page background (canvas, surface,
     surface-raised): 3:1. Decorative for the status, but it is what
     separates the box from the page.
  4. X: ink against rest, hover and pressed; focus ring against the toast
     background. 3:1.
  No contrast exception: none was declared.

THE MARKUP CONTRACT IS THE OTHER HALF OF THIS GATE

  Usage rules from guidelines.md, measured on the emitted HTML:

    a) a single .al-toast-region per document: <section popover="manual">
       with aria-label, outside <template> and outside inert (rule 23);
    b) inside it, exactly two live regions: one
       <div class="al-toast-region__live" role="status"> and one with
       role="alert" - EMPTY on load: the region exists before the first
       message (rules 22 and 23);
    c) every live toast is born from a <template> whose only child is the
       <div class="al-toast"> (toast.js clones from there);
    d) one, and only one, status modifier: --success, --warning, --error or
       --info. No Neutral (rule 26);
    e) first child = <svg class="al-icon al-icon--20 al-toast__icon"> with
       role="img", aria-label with the status name, no aria-hidden, and the
       status icon's drawing: circle-check, triangle-alert, circle-alert,
       info (rules 13 and 14);
    f) second child = <div class="al-toast__text"> with a
       <p class="al-toast__title"> with text and, optionally, a
       <p class="al-toast__description"> with text - nothing else;
    g) third and last child = the X: <button type="button"> Ghost sm Icon
       Button with the al-toast__close class, the close aria-label and the
       icon inside aria-hidden (rule 24);
    h) nothing interactive besides the X - no link, field, other button,
       tabindex or contenteditable (rule 25);
    i) the site's frozen samples (.al-toast outside <template>) sit under
       `inert` and `aria-hidden` on an ancestor: a toast stuck forever
       doesn't exist in the component. Their markup meets (d) to (h) all the
       same - it is what the documentation shows.

RUN ORDER - same as the others: runs AFTER the HTML it measures.

Run: python3 a11y.py [path.html]
     with no argument, measures build/site/index.html
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'tools'))
from paths import ROOT, TOKENS_JSON, SITE_HTML, comp_src, comp_out  # noqa: E402
from contrast import cr  # noqa: E402
from htmltree import Tree, walk, classes, has, ancestors, text_of  # noqa: E402
FOUND = json.load(open(TOKENS_JSON))
TS = json.load(open(comp_out('toast', 'tokens.json')))
IB = json.load(open(comp_out('icon-button', 'tokens.json')))
ICON_DIR = comp_src('icon', 'icons')

SEM = FOUND['color']['semantic']
ALIAS = TS['alias']
THEMES = ('light', 'dark')

TEXT_FLOOR = 4.5         # 1.4.3
NON_TEXT_FLOOR = 3.0     # 1.4.11

DEFAULT_HTML = SITE_HTML
OUT_JSON = comp_out('toast', 'a11y.json')

PAGES = ('bg-canvas', 'bg-surface', 'bg-surface-raised')
# The status names and the X name stay in Portuguese: the site this gate
# measures is in Portuguese, and these are the exact strings it renders.
STATUS = {
    'success': ('Sucesso', 'circle-check'),
    'warning': ('Aviso', 'triangle-alert'),
    'error':   ('Erro', 'circle-alert'),
    'info':    ('Informação', 'info'),
}
CLOSE_CLASSES = {'al-icon-btn', 'al-icon-btn--ghost', 'al-icon-btn--sm', 'al-toast__close'}
CLOSE_LABEL = 'Fechar notificação'
INTERACTIVE = ('a', 'button', 'input', 'select', 'textarea', 'details', 'summary')


def sem(name, theme):
    v = SEM[name]
    return v[THEMES.index(theme)] if isinstance(v, list) else v[theme]


def ts(role, theme):
    return sem(ALIAS[f'toast-{role}'], theme)


def row(theme, what, fg_name, fg, bg_name, bg, floor):
    ratio = round(cr(fg, bg), 2)
    return {'theme': theme, 'what': what, 'fg': fg_name, 'fgHex': fg,
            'bg': bg_name, 'bgHex': bg, 'ratio': ratio, 'floor': floor,
            'pass': ratio >= floor, 'invisible': fg.lower() == bg.lower(),
            'exception': None}


def contrast_rows():
    rows = []
    bg_name = ALIAS['toast-bg']
    ink_name = IB['alias']['icon-button-ghost-ink']
    for t in THEMES:
        bg = ts('bg', t)
        # 1. text
        rows.append(row(t, 'title', ALIAS['toast-title'], ts('title', t), bg_name, bg, TEXT_FLOOR))
        rows.append(row(t, 'description', ALIAS['toast-description'], ts('description', t), bg_name, bg,
                        TEXT_FLOOR))
        # 2. status icon
        for s in STATUS:
            rows.append(row(t, f'{s} / icon', ALIAS[f'toast-{s}-icon'], ts(f'{s}-icon', t),
                            bg_name, bg, NON_TEXT_FLOOR))
        # 3. border against the page
        for s in STATUS:
            for p in PAGES:
                rows.append(row(t, f'{s} / border', ALIAS[f'toast-{s}-border'], ts(f'{s}-border', t),
                                p, sem(p, t), NON_TEXT_FLOOR))
        # 4. the X
        ink = sem(ink_name, t)
        for state, bg_role in (('rest', bg_name), ('hover', 'bg-hover-raised'),
                               ('pressed', 'bg-active-raised')):
            rows.append(row(t, f'X / {state}', ink_name, ink, bg_role, sem(bg_role, t), NON_TEXT_FLOOR))
        rows.append(row(t, 'X / focus ring', 'shadow-focus-default', sem('shadow-focus-default', t),
                        bg_name, bg, NON_TEXT_FLOOR))
    return rows


# ─────────────────────────────────────────────── markup
def shape(svg_kids):
    """Drawing signature: tag + geometric attributes of each child."""
    return [(k['tag'], tuple(sorted((a, v) for a, v in k['attrs'].items()
                                    if a not in ('class', 'style')))) for k in svg_kids]


def icon_shape(name):
    raw = open(os.path.join(ICON_DIR, name + '.svg')).read()
    t = Tree()
    t.feed(raw[raw.find('<svg'):])
    svg = next(n for n in walk(t.root) if n['tag'] == 'svg')
    return shape(svg['kids'])


SHAPES = {s: icon_shape(icon) for s, (_, icon) in STATUS.items()}


def check_toast(el, problems, where):
    ln = el['line']

    def bad(msg):
        problems.append(f'{where}line {ln}: {msg}')

    # (d)
    mods = [s for s in STATUS if has(el, f'al-toast--{s}')]
    extra = [c for c in classes(el) if c.startswith('al-toast--') and c[10:] not in STATUS]
    if el['tag'] != 'div':
        bad('the toast is a <div class="al-toast">')
    if len(mods) != 1 or extra:
        bad(f'status {mods + extra} - one, and only one, of success, warning, error and info (rule 26)')
        return
    status = mods[0]
    label, icon = STATUS[status]

    kids = el['kids']
    if len(kids) != 3:
        bad(f'{len(kids)} children - icon, text and X, nothing else (rules 13, 24 and 25)')
        return
    ico, txt, close = kids

    # (e)
    ia = ico['attrs']
    if ico['tag'] != 'svg' or not {'al-icon', 'al-icon--20', 'al-toast__icon'} <= set(classes(ico)):
        bad('first child = <svg class="al-icon al-icon--20 al-toast__icon"> (rule 13)')
    else:
        if ia.get('role') != 'img' or ia.get('aria-label') != label or 'aria-hidden' in ia:
            bad(f'{status} icon: role="img" + aria-label="{label}", no aria-hidden - '
                f'the icon carries the status (rule 14)')
        if shape(ico['kids']) != SHAPES[status]:
            bad(f'{status} icon is not {icon} (rule 13)')

    # (f)
    tk = txt['kids']
    if txt['tag'] != 'div' or not has(txt, 'al-toast__text'):
        bad('second child = <div class="al-toast__text">')
    elif not tk or tk[0]['tag'] != 'p' or not has(tk[0], 'al-toast__title') or not text_of(tk[0]):
        bad('the text opens with a <p class="al-toast__title"> with text - the title is required')
    elif len(tk) > 2 or (len(tk) == 2 and (tk[1]['tag'] != 'p' or not has(tk[1], 'al-toast__description')
                                           or not text_of(tk[1]))):
        bad('after the title, only one <p class="al-toast__description"> with text (optional)')

    # (g)
    ca = close['attrs']
    if (close['tag'] != 'button' or ca.get('type') != 'button'
            or not CLOSE_CLASSES <= set(classes(close))):
        bad('third child = <button type="button" class="al-icon-btn al-icon-btn--ghost '
            'al-icon-btn--sm al-toast__close"> (rule 24)')
    else:
        if ca.get('aria-label') != CLOSE_LABEL:
            bad(f'the X is named "{CLOSE_LABEL}" (rule 24)')
        svgs = [k for k in close['kids'] if k['tag'] == 'svg']
        if (len(close['kids']) != 1 or len(svgs) != 1 or svgs[0]['attrs'].get('aria-hidden') != 'true'
                or svgs[0]['attrs'].get('focusable') != 'false'):
            bad('inside the X, only the icon, with aria-hidden="true" focusable="false"')

    # (h)
    for k in walk(el):
        if k is close:
            continue
        if any(a is close for a in ancestors(k)):
            continue
        if (k['tag'] in INTERACTIVE or 'tabindex' in k['attrs']
                or 'contenteditable' in k['attrs']):
            bad(f'interactive <{k["tag"]}> inside the toast - only the X (rule 25)')
            break
    return status


def check_region(regions, problems):
    if len(regions) != 1:
        problems.append(f'{len(regions)} .al-toast-region in the document - it must be exactly one (rule 23)')
        if not regions:
            return
    for r in regions:
        a = r['attrs']

        def bad(msg):
            problems.append(f'line {r["line"]}: {msg}')

        # (a)
        if r['tag'] != 'section' or a.get('popover') != 'manual' or not a.get('aria-label', '').strip():
            bad('region = <section class="al-toast-region" aria-label popover="manual"> (rule 23)')
        under = list(ancestors(r))
        if any(x['tag'] == 'template' for x in under):
            bad('the region is inside a <template> - it exists from page load (rule 23)')
        if any('inert' in x['attrs'] or x['attrs'].get('aria-hidden') == 'true' for x in [r] + under):
            bad('the region is under inert or aria-hidden - the announcement does not arrive (rule 22)')
        # (b)
        roles = [k['attrs'].get('role') for k in r['kids']]
        lives = [k for k in r['kids'] if k['tag'] == 'div' and has(k, 'al-toast-region__live')]
        if len(r['kids']) != 2 or len(lives) != 2 or sorted(roles) != ['alert', 'status']:
            bad('inside the region: one __live role="status" and one role="alert", nothing else (rule 22)')
        for k in lives:
            if k['kids'] or k['text'].strip():
                bad(f'the live region role="{k["attrs"].get("role")}" is not born empty - '
                    f'a message born together with the region is not announced (rule 23)')


def markup_contract(html):
    """Returns (templates, frozen, by_status, problems)."""
    t = Tree()
    t.feed(html)
    nodes = list(walk(t.root))
    problems = []

    check_region([n for n in nodes if has(n, 'al-toast-region')], problems)

    live, frozen, by_status = 0, 0, {s: 0 for s in STATUS}
    for n in nodes:
        if not has(n, 'al-toast'):
            continue
        under = list(ancestors(n))
        tpl = next((x for x in under if x['tag'] == 'template'), None)
        if tpl is None:
            # (i)
            if not (any('inert' in x['attrs'] for x in under)
                    and any(x['attrs'].get('aria-hidden') == 'true' for x in under)):
                problems.append(f'line {n["line"]}: .al-toast outside <template> and outside inert + '
                                f'aria-hidden - a toast stuck forever does not exist')
            frozen += 1
            check_toast(n, problems, 'sample, ')
            continue
        # (c)
        live += 1
        if tpl['kids'] != [n]:
            problems.append(f'line {tpl["line"]}: <template id="{tpl["attrs"].get("id", "")}"> must '
                            f'have the .al-toast as its only child - toast.js clones the first one')
        s = check_toast(n, problems, '')
        if s:
            by_status[s] += 1
    return live, frozen, by_status, problems


def run():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_HTML
    rows = contrast_rows()
    fails = [r for r in rows if not r['pass']]

    print('=' * 74)
    print('TOAST ACCESSIBILITY QA')
    print('=' * 74)
    for r in fails:
        note = 'INVISIBLE - equal to the background' if r['invisible'] else 'FAIL'
        print(f'  XX {r["theme"]:<5} {r["what"]:<22} on {r["bg"]:<18} '
              f'{r["fgHex"]} x {r["bgHex"]}  {r["ratio"]:5.2f}  {note}')

    print('\nMARKUP CONTRACT')
    print(f'     source: {os.path.relpath(path, ROOT)}')
    by_status = {}
    if not os.path.exists(path):
        live, frozen, mk = None, 0, [f'{path} does not exist']
    else:
        live, frozen, by_status, mk = markup_contract(open(path, encoding='utf-8').read())
        if live == 0:
            live, mk = None, ['no <template> with .al-toast in the HTML - run site.py first']
    if live is None:
        for p in mk:
            print(f'     PENDING: {p}')
    else:
        summary = ', '.join(f'{s} {n}' for s, n in by_status.items())
        print(f'     1 region + {live} template(s) checked, 9 rules (a-i) - {summary}; '
              f'{frozen} frozen sample(s) under inert')
        for p in mk:
            print(f'     PROBLEM: {p}')

    print('-' * 74)
    print(f'{len(rows)} measurements  |  pass: {len(rows) - len(fails)}  |  exceptions: 0  |  '
          f'fail: {len(fails)}')

    json.dump({
        'component': 'toast',
        'criterion': 'WCAG 1.4.3 text + 1.4.11 non-text',
        'markupSource': os.path.relpath(path, ROOT),
        'markupChecked': live,
        'markupByStatus': by_status,
        'markupFrozen': frozen,
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
