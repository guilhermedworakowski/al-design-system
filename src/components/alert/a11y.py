"""
Accessibility QA for the Alert.

As with the other components, validation is by RENDERED COMBINATION - role x
status x theme - against the EFFECTIVE background, not a loose token pair.

WHAT THE EFFECTIVE BACKGROUND CHANGES HERE

  The Alert is page content, with an opaque `alert-bg` background
  (bg-surface-raised): title, description, icon, the X and the buttons only
  touch the Alert's own background. What touches the page is the BORDER - and
  the page is the canvas (bg-canvas) or the surface (bg-surface). No Modal:
  the Alert lives at the top of the page, never inside a dialog (rule 9).

  The X and the actions' Ghost on surface-raised use the -raised ones
  (bg-hover-raised / bg-active-raised, lesson from Modal 0.18.1): the ink is
  measured against the rest, hover and pressed backgrounds. The focus ring of
  every button is measured against the Alert background - a pair the Button
  and Icon Button gates, measured on the page, don't cover.

  The Primary's label only touches the button's own background (bg-brand),
  which doesn't change inside the Alert: it is the Button gate's pair, with
  the inherited brand exception (white label 3.34:1). It isn't measured again
  here.

FIVE JUDGMENTS

  1. Title and description against the Alert background: 4.5:1 from 1.4.3.
  2. Status icon against the Alert background: 3:1 from 1.4.11. The icon is
     what carries the status (rule 16), so it must pass.
  3. Border of each status against the Alert background and against each
     page (canvas, surface): 3:1. Decorative for the status, but it is what
     separates the box from the page.
  4. X: ink against rest, hover and pressed. 3:1.
  5. Actions' Ghost: label against rest, hover and pressed, 4.5:1. Focus
     ring (X, Ghost and Primary) against the Alert background, 3:1.
  No new contrast exception: none was declared.

THE MARKUP CONTRACT IS THE OTHER HALF OF THIS GATE

  Usage rules from guidelines.md, measured on the emitted HTML:

    a) .al-alert-slot is a <div> outside <template> and outside inert, with
       at most one .al-alert inside - one per page (rules 9 and 11);
    b) the Alert present on page load (in the slot, outside <template>) has
       no role nor aria-live, neither it nor the slot: it is regular content
       (rule 23). The role only appears when alert.js inserts it later;
    c) every Alert inserted later is born from a <template> whose only child
       is the <div class="al-alert"> (alert.js clones from there);
    d) one, and only one, status modifier: --success, --warning, --danger or
       --info. No Neutral (rule 28);
    e) children = <div class="al-alert__body"> and, optionally,
       <div class="al-alert__actions">, in that order;
    f) in the body, first child = <svg class="al-icon al-icon--24
       al-alert__icon"> with role="img", aria-label with the status name, no
       aria-hidden, and the status icon's drawing: circle-check,
       triangle-alert, circle-alert, info (rules 15 and 16);
    g) then, <div class="al-alert__text"> with <p class="al-alert__title">
       and <p class="al-alert__description">, both with text - nothing else.
       The description is required (rule 13). No heading anywhere in the
       Alert: neither h1-h6 nor role="heading" (rule 26);
    h) the X, if present, is the body's last child: <button type="button">
       Ghost sm Icon Button with the al-alert__close class,
       data-al-alert-close, the close aria-label and the icon inside
       aria-hidden (rule 27);
    i) actions: one or two <button type="button" class="al-btn ... al-btn--md">
       with a label; with two, Ghost first and Primary after (rule 17).
       Nothing interactive outside the X and the actions - no link, field,
       tabindex or contenteditable;
    j) the site's frozen samples (.al-alert outside <template> and outside
       the slot) sit under `inert` and `aria-hidden` on an ancestor. Their
       markup meets (d) to (i) all the same - it is what the documentation
       shows.

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
AL = json.load(open(comp_out('alert', 'tokens.json')))
IB = json.load(open(comp_out('icon-button', 'tokens.json')))
BT = json.load(open(comp_out('button', 'tokens.json')))
ICON_DIR = comp_src('icon', 'icons')

SEM = FOUND['color']['semantic']
ALIAS = AL['alias']
THEMES = ('light', 'dark')

TEXT_FLOOR = 4.5         # 1.4.3
NON_TEXT_FLOOR = 3.0     # 1.4.11

DEFAULT_HTML = SITE_HTML
OUT_JSON = comp_out('alert', 'a11y.json')

PAGES = ('bg-canvas', 'bg-surface')
# The status names and the X name stay in Portuguese: the site this gate
# measures is in Portuguese, and these are the exact strings it renders.
STATUS = {
    'success': ('Sucesso', 'circle-check'),
    'warning': ('Aviso', 'triangle-alert'),
    'danger':  ('Perigo', 'circle-alert'),
    'info':    ('Informação', 'info'),
}
CLOSE_CLASSES = {'al-icon-btn', 'al-icon-btn--ghost', 'al-icon-btn--sm', 'al-alert__close'}
CLOSE_LABEL = 'Fechar aviso'
INTERACTIVE = ('a', 'button', 'input', 'select', 'textarea', 'details', 'summary')
HEADINGS = ('h1', 'h2', 'h3', 'h4', 'h5', 'h6')


def sem(name, theme):
    v = SEM[name]
    return v[THEMES.index(theme)] if isinstance(v, list) else v[theme]


def al(role, theme):
    return sem(ALIAS[f'alert-{role}'], theme)


def row(theme, what, fg_name, fg, bg_name, bg, floor):
    ratio = round(cr(fg, bg), 2)
    return {'theme': theme, 'what': what, 'fg': fg_name, 'fgHex': fg,
            'bg': bg_name, 'bgHex': bg, 'ratio': ratio, 'floor': floor,
            'pass': ratio >= floor, 'invisible': fg.lower() == bg.lower(),
            'exception': None}


def contrast_rows():
    rows = []
    bg_name = ALIAS['alert-bg']
    x_ink = IB['alias']['icon-button-ghost-ink']
    ghost_label = BT['alias']['button-ghost-label']
    states = (('rest', bg_name), ('hover', 'bg-hover-raised'), ('pressed', 'bg-active-raised'))
    for t in THEMES:
        bg = al('bg', t)
        # 1. text
        rows.append(row(t, 'title', ALIAS['alert-title'], al('title', t), bg_name, bg, TEXT_FLOOR))
        rows.append(row(t, 'description', ALIAS['alert-description'], al('description', t), bg_name, bg,
                        TEXT_FLOOR))
        # 2. status icon
        for s in STATUS:
            rows.append(row(t, f'{s} / icon', ALIAS[f'alert-{s}-icon'], al(f'{s}-icon', t),
                            bg_name, bg, NON_TEXT_FLOOR))
        # 3. border against its own background and against the page
        for s in STATUS:
            for p in (bg_name,) + PAGES:
                rows.append(row(t, f'{s} / border', ALIAS[f'alert-{s}-border'], al(f'{s}-border', t),
                                p, sem(p, t), NON_TEXT_FLOOR))
        # 4. the X
        for state, bg_role in states:
            rows.append(row(t, f'X / {state}', x_ink, sem(x_ink, t), bg_role, sem(bg_role, t), NON_TEXT_FLOOR))
        # 5. actions' Ghost + focus ring
        for state, bg_role in states:
            rows.append(row(t, f'Ghost / {state}', ghost_label, sem(ghost_label, t), bg_role, sem(bg_role, t),
                            TEXT_FLOOR))
        rows.append(row(t, 'focus ring', 'shadow-focus-default', sem('shadow-focus-default', t),
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


def check_alert(el, problems, where):
    """Returns (status, has_actions, has_x) or None."""
    ln = el['line']

    def bad(msg):
        problems.append(f'{where}line {ln}: {msg}')

    # (d)
    mods = [s for s in STATUS if has(el, f'al-alert--{s}')]
    extra = [c for c in classes(el) if c.startswith('al-alert--') and c[10:] not in STATUS]
    if el['tag'] != 'div':
        bad('the Alert is a <div class="al-alert">')
    if len(mods) != 1 or extra:
        bad(f'status {mods + extra} - one, and only one, of success, warning, danger and info (rule 28)')
        return None
    status = mods[0]
    label, icon = STATUS[status]

    # (g) heading at any depth
    for k in walk(el):
        if k['tag'] in HEADINGS or k['attrs'].get('role') == 'heading':
            bad(f'<{k["tag"]}> as a heading inside the Alert - the title is a <p> (rule 26)')
            break

    # (e)
    kids = el['kids']
    if not kids or kids[0]['tag'] != 'div' or not has(kids[0], 'al-alert__body'):
        bad('first child = <div class="al-alert__body">')
        return None
    if len(kids) > 2 or (len(kids) == 2 and (kids[1]['tag'] != 'div' or not has(kids[1], 'al-alert__actions'))):
        bad('after the body, only one <div class="al-alert__actions"> (optional)')
        return None
    body = kids[0]
    actions = kids[1] if len(kids) == 2 else None

    bk = body['kids']
    if len(bk) not in (2, 3):
        bad(f'{len(bk)} children in the body - icon, text and, optionally, the X')
        return None
    ico, txt = bk[0], bk[1]
    close = bk[2] if len(bk) == 3 else None

    # (f)
    ia = ico['attrs']
    if ico['tag'] != 'svg' or not {'al-icon', 'al-icon--24', 'al-alert__icon'} <= set(classes(ico)):
        bad('first child of the body = <svg class="al-icon al-icon--24 al-alert__icon"> (rule 15)')
    else:
        if ia.get('role') != 'img' or ia.get('aria-label') != label or 'aria-hidden' in ia:
            bad(f'{status} icon: role="img" + aria-label="{label}", no aria-hidden - '
                f'the icon carries the status (rule 16)')
        if shape(ico['kids']) != SHAPES[status]:
            bad(f'{status} icon is not {icon} (rule 15)')

    # (g)
    tk = txt['kids']
    if txt['tag'] != 'div' or not has(txt, 'al-alert__text'):
        bad('second child of the body = <div class="al-alert__text">')
    elif (len(tk) != 2
          or tk[0]['tag'] != 'p' or not has(tk[0], 'al-alert__title') or not text_of(tk[0])
          or tk[1]['tag'] != 'p' or not has(tk[1], 'al-alert__description') or not text_of(tk[1])):
        bad('the text is <p class="al-alert__title"> + <p class="al-alert__description">, both with '
            'text - the description is required (rules 13 and 26)')

    # (h)
    if close is not None:
        ca = close['attrs']
        if (close['tag'] != 'button' or ca.get('type') != 'button'
                or not CLOSE_CLASSES <= set(classes(close)) or 'data-al-alert-close' not in ca):
            bad('third child of the body = <button type="button" class="al-icon-btn al-icon-btn--ghost '
                'al-icon-btn--sm al-alert__close" data-al-alert-close> (rule 27)')
        else:
            if ca.get('aria-label') != CLOSE_LABEL:
                bad(f'the X is named "{CLOSE_LABEL}" (rule 27)')
            svgs = [k for k in close['kids'] if k['tag'] == 'svg']
            if (len(close['kids']) != 1 or len(svgs) != 1
                    or svgs[0]['attrs'].get('aria-hidden') != 'true'
                    or svgs[0]['attrs'].get('focusable') != 'false'):
                bad('inside the X, only the icon, with aria-hidden="true" focusable="false"')

    # (i)
    buttons = []
    if actions is not None:
        buttons = actions['kids']
        ok = 1 <= len(buttons) <= 2 and all(
            b['tag'] == 'button' and b['attrs'].get('type') == 'button'
            and {'al-btn', 'al-btn--md'} <= set(classes(b)) and text_of(b) for b in buttons)
        if not ok:
            bad('actions = one or two <button type="button" class="al-btn ... al-btn--md"> with a label (rule 17)')
        elif len(buttons) == 2 and not (has(buttons[0], 'al-btn--ghost') and has(buttons[1], 'al-btn--primary')):
            bad('with two actions, Ghost first and Primary after (rule 17)')
    allowed = [b for b in buttons] + ([close] if close is not None else [])
    for k in walk(el):
        if any(k is p or any(a is p for a in ancestors(k)) for p in allowed):
            continue
        if (k['tag'] in INTERACTIVE or 'tabindex' in k['attrs']
                or 'contenteditable' in k['attrs']):
            bad(f'interactive <{k["tag"]}> inside the Alert - only the X and the actions')
            break
    return status, actions is not None, close is not None


def frozen(under):
    return (any('inert' in x['attrs'] for x in under)
            and any(x['attrs'].get('aria-hidden') == 'true' for x in under))


def markup_contract(html):
    """Returns (slots, present, templates, frozen, by_status, problems)."""
    t = Tree()
    t.feed(html)
    nodes = list(walk(t.root))
    problems = []

    # (a)
    slots = [n for n in nodes if has(n, 'al-alert-slot')]
    for s in slots:
        under = list(ancestors(s))
        if s['tag'] != 'div':
            problems.append(f'line {s["line"]}: the slot is a <div class="al-alert-slot">')
        if any(x['tag'] == 'template' for x in under):
            problems.append(f'line {s["line"]}: slot inside a <template> - it exists from page load')
        if any('inert' in x['attrs'] or x['attrs'].get('aria-hidden') == 'true' for x in [s] + under):
            problems.append(f'line {s["line"]}: slot under inert or aria-hidden - the Alert would vanish from the screen reader')
        # (b) the slot isn't a live region on page load either
        if s['attrs'].get('role') or 'aria-live' in s['attrs']:
            problems.append(f'line {s["line"]}: slot with role/aria-live - present on load it is '
                            f'regular content (rule 23)')
        inside = [n for n in walk(s) if has(n, 'al-alert')]
        if len(inside) > 1:
            problems.append(f'line {s["line"]}: {len(inside)} Alerts in the slot - one per page (rule 11)')

    present, tpls, frz = 0, 0, 0
    by_status = {s: 0 for s in STATUS}
    for n in nodes:
        if not has(n, 'al-alert'):
            continue
        under = list(ancestors(n))
        tpl = next((x for x in under if x['tag'] == 'template'), None)
        slot = next((x for x in under if has(x, 'al-alert-slot')), None)
        if tpl is not None:
            # (c)
            tpls += 1
            if tpl['kids'] != [n]:
                problems.append(f'line {tpl["line"]}: <template id="{tpl["attrs"].get("id", "")}"> must '
                                f'have the .al-alert as its only child - alert.js clones from there')
            r = check_alert(n, problems, '')
            if r:
                by_status[r[0]] += 1
        elif slot is not None:
            # (b)
            present += 1
            for x in [n] + under[:under.index(slot)]:
                if x['attrs'].get('role') or 'aria-live' in x['attrs']:
                    problems.append(f'line {n["line"]}: Alert present on load with role/aria-live - '
                                    f'it is regular content (rule 23)')
                    break
            check_alert(n, problems, 'present, ')
        else:
            # (j)
            frz += 1
            if not frozen(under):
                problems.append(f'line {n["line"]}: .al-alert outside the slot and outside <template> without inert + '
                                f'aria-hidden - a sample the keyboard reaches')
            check_alert(n, problems, 'sample, ')
    return len(slots), present, tpls, frz, by_status, problems


def run():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_HTML
    rows = contrast_rows()
    fails = [r for r in rows if not r['pass']]

    print('=' * 74)
    print('ALERT ACCESSIBILITY QA')
    print('=' * 74)
    for r in fails:
        note = 'INVISIBLE - equal to the background' if r['invisible'] else 'FAIL'
        print(f'  XX {r["theme"]:<5} {r["what"]:<22} on {r["bg"]:<18} '
              f'{r["fgHex"]} x {r["bgHex"]}  {r["ratio"]:5.2f}  {note}')

    print('\nMARKUP CONTRACT')
    print(f'     source: {os.path.relpath(path, ROOT)}')
    by_status, slots, present, frz = {}, 0, 0, 0
    if not os.path.exists(path):
        tpls, mk = None, [f'{path} does not exist']
    else:
        slots, present, tpls, frz, by_status, mk = markup_contract(open(path, encoding='utf-8').read())
        if tpls == 0:
            tpls, mk = None, ['no <template> with .al-alert in the HTML - run site.py first']
    if tpls is None:
        for p in mk:
            print(f'     PENDING: {p}')
    else:
        summary = ', '.join(f'{s} {n}' for s, n in by_status.items())
        print(f'     {slots} slot(s), {present} Alert(s) present on load, {tpls} template(s) - '
              f'{summary}; {frz} frozen sample(s) under inert; 10 rules (a-j)')
        for p in mk:
            print(f'     PROBLEM: {p}')

    print('-' * 74)
    print(f'{len(rows)} measurements  |  pass: {len(rows) - len(fails)}  |  exceptions: 0  |  '
          f'fail: {len(fails)}')

    json.dump({
        'component': 'alert',
        'criterion': 'WCAG 1.4.3 text + 1.4.11 non-text',
        'markupSource': os.path.relpath(path, ROOT),
        'markupSlots': slots,
        'markupPresent': present,
        'markupChecked': tpls,
        'markupByStatus': by_status,
        'markupFrozen': frz,
        'markupPending': tpls is None,
        'markupProblems': mk if tpls is not None else [],
        'rows': rows,
    }, open(OUT_JSON, 'w'), indent=2, ensure_ascii=False)
    print(f'{os.path.relpath(OUT_JSON, ROOT)} written')

    failed = bool(fails)
    if tpls is None or mk:
        print('-' * 74)
        print(f'{len(mk)} MARKUP PROBLEM(S) - gate fails')
        failed = True
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(run())
