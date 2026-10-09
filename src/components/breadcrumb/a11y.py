"""
QA de acessibilidade do Breadcrumb (com o _breadcrumb-more).

Como nos outros componentes, a validacao e por COMBINACAO RENDERIZADA - papel
x tema - contra o fundo EFETIVO, nao par de token solto.

O QUE O FUNDO EFETIVO MUDA AQUI

  A trilha mora na pagina (`bg-canvas` ou `bg-surface`, regra 7). O menu do
  `…` e uma camada `bg-surface-raised` por cima dela, e dentro dele os itens
  sao Tab Square com o hover e o pressed TROCADOS para os `-raised` (regra
  26). A etapa 3 mediu os pares; aqui entra o que so existe renderizado:

  - o rotulo do item do menu em repouso, hover e pressed contra o fundo QUE O
    ITEM REALMENTE TEM (o `-raised` que o menu injeta no Tab);
  - o hover e o pressed do item contra o fundo do menu: iguais = item que nao
    reage, reprova (o defeito do Modal 0.18.1 que o `-raised` evita);
  - o anel de foco do item, dentro do menu.

QUATRO JULGAMENTOS

  1. Texto (link, `…`, pagina atual, item do menu em cada estado): 4,5:1 do
     1.4.3. Tem que passar.
  2. Anel de foco na trilha e dentro do menu: 3:1 do 1.4.11. Tem que passar.
  3. Hover e pressed do item DIFERENTES do fundo do menu. Igual = reprova.
  4. Borda do menu: `borda-de-regiao` (etapa 3). Borda IGUAL a pagina
     reprova: a excecao cobre separacao discreta, nao ausencia.
  O separador e decorativo (aria-hidden, regra 21): fora do 1.4.11.

O CONTRATO DE MARCACAO E A OUTRA METADE DESTA ETAPA

  Regras de uso da etapa 4, medidas no HTML emitido:

    a) `.al-breadcrumb` e <nav> com aria-label (regra 19);
    b) um breadcrumb vivo por documento; os de exemplo ficam sob `inert` (nele
       ou num ancestral) e sao isentos (regra 7);
    c) o unico filho e <ol class="al-breadcrumb__list"> e todo filho dele e
       <li class="al-breadcrumb__item"> (regra 19);
    d) o ULTIMO item e so <span class="al-breadcrumb__current"
       aria-current="page"> com texto - sem <a>, sem separador (regras 15 e 20);
    e) todo item que nao e o ultimo termina num <svg class="al-breadcrumb__separator">
       com aria-hidden="true" e focusable="false" (regra 21);
    f) todo link e <a href> com texto e sem aria-current; aria-current so na
       atual (regras 15 e 20);
    g) o `…` so existe com 5 niveis ou mais, e sempre no TERCEIRO item; e
       <button type="button"> com aria-label, aria-expanded e aria-controls
       apontando para o menu do mesmo item (regras 5, 6 e 22);
    h) o menu e <ul class="al-tabs al-tabs--square al-breadcrumb__menu"> sem
       role; cada item e <a href class="al-tab"> com .al-tab__label de texto,
       sem role nem aria-selected/aria-current (regra 17);
    i) nenhum breadcrumb dentro de Card, Modal ou Drawer (regra 7);
    j) nenhum rotulo vazio em lugar nenhum da trilha (regra 10).

ORDEM DE EXECUCAO - mesma dos outros: roda DEPOIS do HTML que ele mede.

Rodar: python3 a11y.py [caminho.html]
       sem argumento, mede build/site/index.html
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
EXC_BORDA = 'borda-de-regiao'

DEFAULT_HTML = SITE_HTML
OUT_JSON = comp_out('breadcrumb', 'a11y.json')

PAGINAS = ('bg-canvas', 'bg-surface')


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
        for p in PAGINAS:
            pg = sem(p, t)
            rows.append(row(t, 'link', ALIAS['breadcrumb-link'], bc('link', t), p, pg, TEXT_FLOOR))
            rows.append(row(t, '…', ALIAS['breadcrumb-more'], bc('more', t), p, pg, TEXT_FLOOR))
            rows.append(row(t, 'pagina atual', ALIAS['breadcrumb-current'], bc('current', t), p, pg, TEXT_FLOOR))
            rows.append(row(t, 'anel na trilha', 'shadow-focus-default', ring, p, pg, NON_TEXT_FLOOR))
            b = bc('menu-border', t)
            rows.append(row(t, 'borda do menu', ALIAS['breadcrumb-menu-border'], b, p, pg,
                            NON_TEXT_FLOOR, EXC_BORDA, invisible=b.lower() == pg.lower()))
        # dentro do menu: o fundo efetivo de cada estado do item
        rows.append(row(t, 'item do menu', TA['tab-label'], tab('label', t),
                        'menu-bg', menu, TEXT_FLOOR))
        rows.append(row(t, 'item do menu (hover)', TA['tab-label-hover'], tab('label-hover', t),
                        'menu-item-bg-hover', hover, TEXT_FLOOR))
        rows.append(row(t, 'item do menu (pressed)', TA['tab-label-active'], tab('label-active', t),
                        'menu-item-bg-active', active, TEXT_FLOOR))
        rows.append(row(t, 'anel no menu', 'shadow-focus-default', ring, 'menu-bg', menu, NON_TEXT_FLOOR))
        # julgamento 3: o estado tem que existir na tela (sem piso, so igualdade)
        for nome, cor in (('hover', hover), ('pressed', active)):
            r = row(t, f'{nome} do item vs menu', ALIAS[f'breadcrumb-menu-item-bg-{"hover" if nome == "hover" else "active"}'],
                    cor, 'menu-bg', menu, 1.0, invisible=cor.lower() == menu.lower())
            r['pass'] = not r['invisible']
            rows.append(r)
    return rows


# ─────────────────────────────────────────────── marcacao
def check_breadcrumb(n, ids, problems):
    ln = n['line']

    def bad(msg):
        problems.append(f'linha {ln}: {msg}')

    # (a)
    if n['tag'] != 'nav' or not n['attrs'].get('aria-label', '').strip():
        bad('.al-breadcrumb tem que ser <nav aria-label="…"> (regra 19)')
    # (i)
    for a in ancestors(n):
        if any(has(a, c) for c in ('al-card', 'al-modal', 'al-drawer')):
            bad('breadcrumb dentro de Card, Modal ou Drawer (regra 7)')
            break
    # (c)
    lists = n['kids']
    if len(lists) != 1 or lists[0]['tag'] != 'ol' or not has(lists[0], 'al-breadcrumb__list'):
        bad('o unico filho tem que ser <ol class="al-breadcrumb__list"> (regra 19)')
        return
    items = lists[0]['kids']
    if any(i['tag'] != 'li' or not has(i, 'al-breadcrumb__item') for i in items):
        bad('todo filho da lista e <li class="al-breadcrumb__item"> (regra 19)')
        return
    if len(items) < 2:
        bad('trilha com menos de 2 niveis - sem pai nao ha breadcrumb (regras 1 e 18)')
        return

    # (d) ultimo item
    last = items[-1]
    cur = [k for k in walk(last) if has(k, 'al-breadcrumb__current')]
    if (len(cur) != 1 or cur[0]['tag'] != 'span' or cur[0]['attrs'].get('aria-current') != 'page'
            or not text_of(cur[0])):
        bad('ultimo item = <span class="al-breadcrumb__current" aria-current="page"> com texto (regras 15 e 20)')
    if any(k['tag'] in ('a', 'button') for k in walk(last)):
        bad('a pagina atual nao e link nem botao (regra 15)')
    if any(has(k, 'al-breadcrumb__separator') for k in walk(last)):
        bad('o ultimo item nao leva separador (regra 21)')

    # (e) separadores
    for it in items[:-1]:
        if not it['kids'] or not has(it['kids'][-1], 'al-breadcrumb__separator'):
            bad(f'item "{text_of(it)[:20]}" sem separador no fim (regra 21)')
            continue
        s = it['kids'][-1]
        if s['tag'] != 'svg' or s['attrs'].get('aria-hidden') != 'true' or s['attrs'].get('focusable') != 'false':
            bad('separador e <svg> com aria-hidden="true" focusable="false" (regra 21)')

    # (f) links
    for k in walk(n):
        if has(k, 'al-breadcrumb__link'):
            if k['tag'] != 'a' or not k['attrs'].get('href'):
                bad('.al-breadcrumb__link tem que ser <a href> (regra 15)')
            if not text_of(k):
                bad('link sem texto (regra 10)')
        if 'aria-current' in k['attrs'] and not has(k, 'al-breadcrumb__current'):
            bad('aria-current fora da pagina atual (regras 15 e 20)')

    # (g) `…` e (h) menu
    mores = [i for i in items if has(i, 'al-breadcrumb__more')]
    menu_items = 0
    for m in mores:
        btn = [k for k in m['kids'] if has(k, 'al-breadcrumb__more-button')]
        if len(btn) != 1:
            bad('item do `…` sem .al-breadcrumb__more-button')
            continue
        b = btn[0]['attrs']
        if (btn[0]['tag'] != 'button' or b.get('type') != 'button' or not b.get('aria-label', '').strip()
                or b.get('aria-expanded') not in ('true', 'false') or not b.get('aria-controls')):
            bad('`…` = <button type="button"> com aria-label, aria-expanded e aria-controls (regra 22)')
        menu = ids.get(b.get('aria-controls'))
        if menu is None or menu.get('parent') is not m:
            bad('aria-controls do `…` nao aponta para um menu no mesmo item (regra 22)')
            continue
        mc = classes(menu)
        if menu['tag'] != 'ul' or not {'al-tabs', 'al-tabs--square', 'al-breadcrumb__menu'} <= set(mc):
            bad('menu = <ul class="al-tabs al-tabs--square al-breadcrumb__menu"> (regra 17)')
        if 'role' in menu['attrs']:
            bad(f'menu com role="{menu["attrs"]["role"]}" - sao links, nunca menu de acoes (regra 17)')
        for li in menu['kids']:
            links = [k for k in li['kids'] if k['tag'] == 'a']
            if li['tag'] != 'li' or len(links) != 1:
                bad('cada item do menu e <li> com um <a> (regra 17)')
                continue
            a = links[0]
            lab = [k for k in a['kids'] if has(k, 'al-tab__label')]
            if (not a['attrs'].get('href') or not has(a, 'al-tab') or not lab or not text_of(lab[0])
                    or any(x in a['attrs'] for x in ('role', 'aria-selected', 'aria-current'))):
                bad('item do menu = <a href class="al-tab"> com .al-tab__label, sem role/aria-selected/aria-current (regra 17)')
            menu_items += 1
    if len(mores) > 1:
        bad('mais de um `…` na trilha (regra 6)')
    if mores:
        if items.index(mores[0]) != 2 or len(items) != 4:
            bad('a Large e primeiro, segundo, `…` e atual - o `…` e o terceiro de quatro itens (regra 6)')
        if len(items) - 1 + menu_items < 5:
            bad(f'`…` com {len(items) - 1 + menu_items} niveis - so colapsa com 5 ou mais (regra 5)')
    elif len(items) > 4:
        bad(f'{len(items)} niveis sem `…` - com 5 ou mais a trilha colapsa (regra 5)')


def markup_contract(path):
    if not os.path.exists(path):
        return None, [f'{path} nao existe']
    t = Tree(skip=SKIP_TEMPLATE)
    t.feed(open(path, encoding='utf-8').read())
    ids = {n['attrs']['id']: n for n in walk(t.root) if n['attrs'].get('id')}

    found, problems, live = 0, [], 0
    for n in walk(t.root):
        if not has(n, 'al-breadcrumb'):
            continue
        found += 1
        if 'inert' not in n['attrs'] and not any('inert' in a['attrs'] for a in ancestors(n)):
            live += 1
        check_breadcrumb(n, ids, problems)
    # (b)
    if live > 1:
        problems.append(f'{live} breadcrumbs vivos no documento - um por pagina; exemplos ficam sob inert (regra 7)')
    if found == 0:
        return None, ['nenhum .al-breadcrumb no HTML - rode site/site.py antes']
    return found, problems


def run():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_HTML
    rows = contrast_rows()
    invis = [r for r in rows if r['invisible']]
    fails = [r for r in rows if not r['pass'] and not r['exception'] and not r['invisible']]
    excs = [r for r in rows if r['exception']]
    passa = [r for r in rows if r['pass']]

    checked, mk = markup_contract(path)

    print('=' * 74)
    print('QA DE ACESSIBILIDADE DO BREADCRUMB')
    print('=' * 74)
    for r in rows:
        if r['invisible']:
            mark, nota = 'XX', 'INVISIVEL - igual ao fundo'
        elif r['pass']:
            mark, nota = 'ok', 'passa'
        elif r['exception']:
            mark, nota = '~~', f'excecao "{r["exception"]}"'
        else:
            mark, nota = 'XX', 'REPROVA'
        print(f'  {mark} {r["theme"]:<5} {r["what"]:<26} sobre {r["bg"]:<20} '
              f'{r["fgHex"]} x {r["bgHex"]}  {r["ratio"]:5.2f}  {nota}')

    print('\nCONTRATO DE MARCACAO')
    print(f'     fonte: {os.path.relpath(path, ROOT)}')
    if checked is None:
        for p in mk:
            print(f'     PENDENTE: {p}')
    else:
        print(f'     {checked} breadcrumb(s) conferido(s), 10 regras (a-j)')
        for p in mk:
            print(f'     PROBLEMA: {p}')

    print('-' * 74)
    print(f'{len(rows)} medicoes  |  passam: {len(passa)}  |  excecoes: {len(excs)}  |  '
          f'reprovas: {len(fails) + len(invis)}')

    json.dump({
        'component': 'breadcrumb',
        'criterion': 'WCAG 1.4.3 texto + 1.4.11 nao-textual + estado visivel',
        'markupSource': os.path.relpath(path, ROOT),
        'markupChecked': checked,
        'markupPending': checked is None,
        'markupProblems': mk if checked is not None else [],
        'rows': rows,
    }, open(OUT_JSON, 'w'), indent=2, ensure_ascii=False)
    print(f'{os.path.relpath(OUT_JSON, ROOT)} escrito')

    falhou = bool(fails or invis)
    if checked is None or mk:
        print('-' * 74)
        print(f'{len(mk)} PROBLEMA(S) DE MARCACAO - portao reprova')
        falhou = True
    return 1 if falhou else 0


if __name__ == '__main__':
    sys.exit(run())
