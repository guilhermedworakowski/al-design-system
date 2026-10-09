"""
QA de acessibilidade do Sidebar.

Como nos outros componentes, a validacao e por COMBINACAO RENDERIZADA - papel
x tema - contra o fundo EFETIVO, nao par de token solto.

O QUE O FUNDO EFETIVO MUDA AQUI

  Na tela larga a Sidebar mora na pagina: fundo `bg-canvas`, e e sobre ele que
  os itens (Tab Square) e o botao do perfil (Icon Button Ghost) aparecem. A
  etapa 3 mediu os textos da propria Sidebar; aqui entram tambem os estados do
  item e do botao SOBRE O FUNDO DA SIDEBAR - que e o motivo da decisao A (com
  surface-raised o hover sumia no escuro, 1,00:1).

  Na tela estreita a Sidebar vira camada: o que fica atras e a pagina
  ESCURECIDA pelo scrim. Esse par a etapa 3 nao media.

QUATRO JULGAMENTOS

  1. Texto (nome, e-mail, rotulo de grupo, rotulo do item em cada estado):
     piso 4,5:1 do 1.4.3. Tem que passar - salvo `marca-no-hover-escuro`,
     excecao da Foundation herdada do Tab.
  2. Anel de foco, icone do botao e fundo do item selecionado/pressionado
     contra a Sidebar: 3:1 do 1.4.11 - salvo `selecao-tonal`, herdada do Tab.
  3. Hover e pressed do item e do botao tem que ser DIFERENTES do fundo da
     Sidebar (o defeito que a decisao A evitou). Igual = reprova.
  4. Borda da Sidebar: `borda-de-regiao` (etapa 3), contra a pagina ao lado e,
     no modo modal, contra a pagina escurecida. O PAINEL modal contra a pagina
     escurecida passa no claro (4,1) e no escuro fica em ~1,1:1: excecao
     `sidebar-nao-se-separa-do-scrim-no-escuro` (etapa 6, opcao a de Gui, 08/10/2026) - a
     separacao vem da borda (~2,7) e da sombra. Painel IGUAL a pagina
     escurecida reprova: a excecao cobre separacao discreta, nao ausencia.

O CONTRATO DE MARCACAO E A OUTRA METADE DESTA ETAPA

  Regras de uso da etapa 4, medidas no HTML emitido:

    a) `.al-sidebar` e um <aside> com aria-label (regra 26);
    b) uma Sidebar viva por documento; as congeladas ficam sob `inert` e sao
       isentas (regra 4);
    c) exatamente um `.al-sidebar__nav`, que e <nav> com aria-label (regra 26);
    d) filhos na ordem perfil (opcional), nav; dentro do nav, miolo e Ajuda
       (opcional), nessa ordem (regra 5);
    e) o perfil fica FORA do nav; Avatar com aria-hidden e <img alt="">
       (regras 18 e 26);
    f) o botao do perfil e um Icon Button com nome (aria-label) e svg
       aria-hidden (regra 19);
    g) todo grupo tem rotulo com texto e id, e a lista dele tem
       aria-labelledby apontando para esse rotulo (regra 27);
    h) toda lista e `.al-tabs.al-tabs--square` (regra 11);
    i) todo item e <a href> `.al-tab` com `.al-tab__label` de texto, sem
       role="tab" nem aria-selected (regra 28);
    j) no maximo um aria-current="page" na Sidebar (regra 12);
    k) nenhum rotulo de item repetido (regra 16);
    l) Ajuda: e um grupo, com no maximo 3 itens (regra 21);
    m) todo data-al-sidebar-open aponta para uma `.al-sidebar` que existe e o
       botao tem aria-label, aria-controls igual ao id e aria-expanded
       (regras 24 e 25);
    n) existe um link "pular" (href="#...") ANTES da Sidebar (regra 29).

ORDEM DE EXECUCAO - mesma dos outros: roda DEPOIS do HTML que ele mede.

Rodar: python3 a11y.py [caminho.html]
       sem argumento, mede site/index.html
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from contrast import cr, composite  # noqa: E402
from htmltree import Tree, walk, has, ancestors, text_flat  # noqa: E402
FOUND = json.load(open(os.path.join(ROOT, 'tokens.json')))
SBR = json.load(open(os.path.join(HERE, 'tokens.json')))
TAB = json.load(open(os.path.join(ROOT, 'components', 'tab', 'tokens.json')))
IBT = json.load(open(os.path.join(ROOT, 'components', 'icon-button', 'tokens.json')))

SEM = FOUND['color']['semantic']
ALIAS = SBR['alias']
TA = TAB['alias']
THEMES = ('light', 'dark')

TEXT_FLOOR = 4.5
NON_TEXT_FLOOR = 3.0
EXC_BORDA = 'borda-de-regiao'
EXC_TONAL = 'selecao-tonal'
EXC_MARCA = 'marca-no-hover-escuro'
EXC_SCRIM = 'sidebar-nao-se-separa-do-scrim-no-escuro'

DEFAULT_HTML = os.path.join(ROOT, 'site', 'index.html')
OUT_JSON = os.path.join(HERE, 'a11y.json')


def sem(name, theme):
    v = SEM[name]
    return v[THEMES.index(theme)] if isinstance(v, list) else v[theme]


def sbr(role, theme):
    return sem(ALIAS[f'sidebar-{role}'], theme)


def tab(role, theme):
    return sem(TA[f'tab-{role}'], theme)


# ─────────────────────────────────────────────── contraste
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

        # 1. textos proprios
        for what, role in (('nome', 'name'), ('email', 'email'), ('rotulo-grupo', 'group-label')):
            rows.append(row(theme, what, ALIAS[f'sidebar-{role}'], sbr(role, theme), bgn, bg, TEXT_FLOOR))

        # 1. rotulo do item em cada estado, sobre o fundo efetivo
        rows.append(row(theme, 'item-repouso', TA['tab-label'], tab('label', theme), bgn, bg, TEXT_FLOOR))
        rows.append(row(theme, 'item-hover', TA['tab-label-hover'], tab('label-hover', theme),
                        TA['tab-bg-hover'], tab('bg-hover', theme), TEXT_FLOOR))
        rows.append(row(theme, 'item-pressed', TA['tab-label-active'], tab('label-active', theme),
                        TA['tab-bg-active'], tab('bg-active', theme), TEXT_FLOOR))
        rows.append(row(theme, 'item-atual', TA['tab-square-label-selected'], tab('square-label-selected', theme),
                        TA['tab-square-bg-selected'], tab('square-bg-selected', theme), TEXT_FLOOR))
        rows.append(row(theme, 'item-atual-hover', TA['tab-square-label-selected-hover'],
                        tab('square-label-selected-hover', theme), TA['tab-square-bg-selected-hover'],
                        tab('square-bg-selected-hover', theme), TEXT_FLOOR, EXC_MARCA))
        rows.append(row(theme, 'item-atual-pressed', TA['tab-square-label-selected-active'],
                        tab('square-label-selected-active', theme), TA['tab-square-bg-selected-active'],
                        tab('square-bg-selected-active', theme), TEXT_FLOOR))

        # 2. nao-textual contra a Sidebar
        rows.append(row(theme, 'anel-de-foco', 'shadow-focus-default', sem('shadow-focus-default', theme),
                        bgn, bg, NON_TEXT_FLOOR))
        rows.append(row(theme, 'icone-do-botao-perfil', 'text-primary', sem('text-primary', theme),
                        bgn, bg, NON_TEXT_FLOOR))
        rows.append(row(theme, 'item-atual-fundo', TA['tab-square-bg-selected'],
                        tab('square-bg-selected', theme), bgn, bg, NON_TEXT_FLOOR, EXC_TONAL))
        rows.append(row(theme, 'item-atual-pressed-fundo', TA['tab-square-bg-selected-active'],
                        tab('square-bg-selected-active', theme), bgn, bg, NON_TEXT_FLOOR))

        # 3. hover e pressed tem que EXISTIR sobre a Sidebar
        for what, name in (('item-hover-distinto', TA['tab-bg-hover']),
                           ('item-pressed-distinto', TA['tab-bg-active']),
                           ('botao-hover-distinto', 'bg-hover'),
                           ('botao-pressed-distinto', 'bg-active')):
            f = sem(name, theme)
            rows.append(row(theme, what, name, f, bgn, bg, 1.0, invisible=f.lower() == bg.lower()))

        # 4. borda da regiao, contra a Sidebar e contra a pagina ao lado
        for page in ('bg-canvas', 'bg-surface'):
            rows.append(row(theme, f'borda-x-{page}', ALIAS['sidebar-border'], sbr('border', theme),
                            page, sem(page, theme), NON_TEXT_FLOOR, EXC_BORDA))

        # 4. modo modal: painel e borda contra a pagina escurecida
        for page in ('bg-canvas', 'bg-surface'):
            atras = composite(sem('bg-scrim', theme), sem(page, theme))
            rows.append(row(theme, f'painel-x-{page}-escurecida', bgn, bg, f'{page}+scrim', atras,
                            NON_TEXT_FLOOR, EXC_SCRIM, invisible=bg.lower() == atras.lower()))
            rows.append(row(theme, f'borda-do-painel-x-{page}-escurecida', ALIAS['sidebar-border'],
                            sbr('border', theme), f'{page}+scrim', atras, NON_TEXT_FLOOR, EXC_BORDA))
    return rows


# ─────────────────────────────────────────────── marcacao
def check_sidebar(n, ids, problems):
    a, ln = n['attrs'], n['line']
    # (a)
    if n['tag'] != 'aside':
        problems.append(f'linha {ln}: .al-sidebar em <{n["tag"]}> - a Sidebar e um <aside> (regra 26)')
    if not a.get('aria-label', '').strip() and not a.get('aria-labelledby'):
        problems.append(f'linha {ln}: <aside> sem nome (aria-label) (regra 26)')

    kids = n['kids']
    navs = [d for d in walk(n) if has(d, 'al-sidebar__nav')]
    # (c)
    if len(navs) != 1:
        problems.append(f'linha {ln}: {len(navs)} .al-sidebar__nav - e exatamente um (regra 26)')
        return
    nav = navs[0]
    if nav['tag'] != 'nav' or not nav['attrs'].get('aria-label', '').strip():
        problems.append(f'linha {nav["line"]}: .al-sidebar__nav tem que ser <nav aria-label> (regra 26)')

    # (d) ordem
    ordem = [('profile' if has(k, 'al-sidebar__profile') else 'nav' if k is nav else None) for k in kids]
    if None in ordem or ordem not in (['profile', 'nav'], ['nav']):
        problems.append(f'linha {ln}: filhos da Sidebar fora da ordem perfil, nav (regra 5)')
    nk = nav['kids']
    nordem = [('content' if has(k, 'al-sidebar__content') else
               'support' if has(k, 'al-sidebar__support') else None) for k in nk]
    if nordem not in (['content'], ['content', 'support']):
        problems.append(f'linha {nav["line"]}: dentro do nav a ordem e miolo e Ajuda (opcional) (regra 5)')

    # (e) (f) perfil
    for prof in (d for d in walk(n) if has(d, 'al-sidebar__profile')):
        if any(p is nav for p in ancestors(prof)):
            problems.append(f'linha {prof["line"]}: o perfil fica FORA do <nav> (regra 26)')
        for av in (d for d in walk(prof) if has(d, 'al-avatar')):
            if av['attrs'].get('aria-hidden') != 'true':
                problems.append(f'linha {av["line"]}: Avatar do perfil e decorativo - aria-hidden="true" (regra 18)')
            for img in (d for d in walk(av) if d['tag'] == 'img'):
                if img['attrs'].get('alt', None) != '':
                    problems.append(f'linha {img["line"]}: foto do perfil com alt="" (regra 18)')
        nome = [d for d in walk(prof) if has(d, 'al-sidebar__name')]
        if len(nome) != 1 or not text_flat(nome[0]):
            problems.append(f'linha {prof["line"]}: o perfil tem um .al-sidebar__name com texto (regra 18)')
        for b in (d for d in walk(prof) if d['tag'] in ('a', 'button')):
            if not has(b, 'al-icon-btn'):
                problems.append(f'linha {b["line"]}: a acao do perfil e um Icon Button (regra 19)')
            if not b['attrs'].get('aria-label', '').strip():
                problems.append(f'linha {b["line"]}: botao do perfil sem nome (aria-label) (regra 19)')
            if b['tag'] == 'a' and 'href' not in b['attrs']:
                problems.append(f'linha {b["line"]}: link do perfil sem href (regra 19)')
            for s in walk(b):
                if s['tag'] == 'svg' and s['attrs'].get('aria-hidden') != 'true':
                    problems.append(f'linha {s["line"]}: svg do botao do perfil sem aria-hidden="true"')

    # (g) grupos
    for g in (d for d in walk(nav) if has(d, 'al-sidebar__group')):
        labels = [k for k in g['kids'] if has(k, 'al-sidebar__group-label')]
        lists = [k for k in g['kids'] if k['tag'] == 'ul']
        if len(labels) != 1 or not text_flat(labels[0]) or not labels[0]['attrs'].get('id'):
            problems.append(f'linha {g["line"]}: grupo sem um rotulo com texto e id (regra 27)')
            continue
        if len(lists) != 1 or lists[0]['attrs'].get('aria-labelledby') != labels[0]['attrs']['id']:
            problems.append(f'linha {g["line"]}: a lista do grupo tem aria-labelledby apontando para o '
                            f'proprio rotulo (regra 27)')
        # (l)
        if has(g, 'al-sidebar__support'):
            itens = [d for d in walk(g) if has(d, 'al-tab')]
            if len(itens) > 3:
                problems.append(f'linha {g["line"]}: Ajuda com {len(itens)} itens - no maximo 3 (regra 21)')
    for s in (d for d in walk(nav) if has(d, 'al-sidebar__support')):
        if not has(s, 'al-sidebar__group'):
            problems.append(f'linha {s["line"]}: a Ajuda e um .al-sidebar__group (regra 21)')

    # (h) listas
    for ul in (d for d in walk(nav) if d['tag'] == 'ul'):
        if not (has(ul, 'al-tabs') and has(ul, 'al-tabs--square')):
            problems.append(f'linha {ul["line"]}: lista da Sidebar e .al-tabs.al-tabs--square (regra 11)')

    # (i) (j) (k) itens
    atuais, rotulos = 0, {}
    for it in (d for d in walk(nav) if has(d, 'al-tab')):
        ia = it['attrs']
        if it['tag'] != 'a' or 'href' not in ia:
            problems.append(f'linha {it["line"]}: item da Sidebar e <a href> (regra 28)')
        if ia.get('role') == 'tab' or 'aria-selected' in ia:
            problems.append(f'linha {it["line"]}: item de navegacao nunca e role="tab"/aria-selected (regra 28)')
        lab = [d for d in walk(it) if has(d, 'al-tab__label')]
        txt = text_flat(lab[0]) if lab else ''
        if not txt:
            problems.append(f'linha {it["line"]}: item sem .al-tab__label com texto')
        elif txt.lower() in rotulos:
            problems.append(f'linha {it["line"]}: rotulo "{txt}" repetido (linha {rotulos[txt.lower()]}) (regra 16)')
        else:
            rotulos[txt.lower()] = it['line']
        cur = ia.get('aria-current')
        if cur is not None and cur != 'false':
            atuais += 1
            if cur != 'page':
                problems.append(f'linha {it["line"]}: aria-current="{cur}" - na Sidebar e "page" (regra 28)')
    if atuais > 1:
        problems.append(f'linha {ln}: {atuais} itens atuais - no maximo um (regra 12)')


def markup_contract(path):
    if not os.path.exists(path):
        return None, [f'{path} nao existe']
    t = Tree()
    t.feed(open(path, encoding='utf-8').read())
    nodes = list(walk(t.root))
    ids = {n['attrs']['id']: n for n in nodes if 'id' in n['attrs']}
    order = {id(n): i for i, n in enumerate(nodes)}

    checked, problems, vivas = 0, [], []
    for n in nodes:
        if not has(n, 'al-sidebar'):
            continue
        checked += 1
        congelada = any('inert' in p['attrs'] for p in ancestors(n))
        if not congelada:
            vivas.append(n)
        if any(has(p, 'al-sidebar') for p in ancestors(n)):
            problems.append(f'linha {n["line"]}: Sidebar dentro de Sidebar (regra 4)')
        check_sidebar(n, ids, problems)

    # (b)
    if len(vivas) > 1:
        problems.append(f'{len(vivas)} Sidebars vivas no documento - uma por tela (regra 4)')

    # (m)
    for n in nodes:
        alvo = n['attrs'].get('data-al-sidebar-open')
        if alvo is None:
            continue
        d = ids.get(alvo)
        if d is None or not has(d, 'al-sidebar'):
            problems.append(f'linha {n["line"]}: data-al-sidebar-open="{alvo}" nao aponta para uma .al-sidebar')
        if not n['attrs'].get('aria-label', '').strip():
            problems.append(f'linha {n["line"]}: botao Menu sem aria-label (regra 24)')
        if n['attrs'].get('aria-controls') != alvo:
            problems.append(f'linha {n["line"]}: botao Menu com aria-controls diferente do id da Sidebar')
        if n['attrs'].get('aria-expanded') not in ('true', 'false'):
            problems.append(f'linha {n["line"]}: botao Menu sem aria-expanded (regra 25)')

    # (n) pular para o conteudo, antes da Sidebar viva
    for s in vivas:
        pulos = [n for n in nodes if n['tag'] == 'a' and n['attrs'].get('href', '').startswith('#')
                 and len(n['attrs']['href']) > 1 and order[id(n)] < order[id(s)]
                 and n['attrs']['href'][1:] in ids]
        if not pulos:
            problems.append(f'linha {s["line"]}: sem link "pular para o conteudo" antes da Sidebar (regra 29)')

    if checked == 0:
        return None, ['nenhuma .al-sidebar no HTML']
    return checked, problems


def run():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_HTML
    rows = contrast_rows()
    invis = [r for r in rows if r['invisible']]
    fails = [r for r in rows if not r['pass'] and not r['exception'] and not r['invisible']]
    excs = [r for r in rows if r['exception']]
    passa = [r for r in rows if r['pass']]

    checked, mk = markup_contract(path)

    print('=' * 78)
    print('QA DE ACESSIBILIDADE DO SIDEBAR')
    print('=' * 78)
    print('\nCOMBINACOES RENDERIZADAS (tema x papel)')
    for r in rows:
        if r['invisible']:
            mark, nota = 'XX', 'INVISIVEL - nada separa os dois fundos'
        elif r['pass']:
            mark, nota = 'ok', 'passa'
        elif r['exception']:
            mark, nota = '~~', f'excecao "{r["exception"]}"'
        else:
            mark, nota = 'XX', 'REPROVA'
        print(f'  {mark} {r["theme"]:<5} {r["what"]:<38} x {r["bg"]:<22} '
              f'{r["ratio"]:5.2f} (piso {r["floor"]})  {nota}')

    print('\nCONTRATO DE MARCACAO')
    print(f'     fonte: {os.path.relpath(path, ROOT)}')
    if checked is None:
        for p in mk:
            print(f'     PENDENTE: {p}')
    else:
        print(f'     {checked} sidebar(s) conferida(s), 14 regras (a-n)')
        for p in mk:
            print(f'     PROBLEMA: {p}')

    print('-' * 78)
    print(f'{len(rows)} medicoes  |  passam: {len(passa)}  |  excecoes: {len(excs)}  |  '
          f'reprovas: {len(fails) + len(invis)}')

    json.dump({
        'component': 'sidebar',
        'criterion': 'WCAG 1.4.3 texto + 1.4.11 nao-textual + estados visiveis sobre a Sidebar',
        'floors': {'text': TEXT_FLOOR, 'nonText': NON_TEXT_FLOOR},
        'markupSource': os.path.relpath(path, ROOT),
        'markupChecked': checked,
        'markupPending': checked is None,
        'markupProblems': mk if checked is not None else [],
        'rows': rows,
    }, open(OUT_JSON, 'w'), indent=2, ensure_ascii=False)
    print(f'{os.path.relpath(OUT_JSON, ROOT)} escrito')

    falhou = False
    if invis or fails:
        print('-' * 78)
        print(f'{len(invis) + len(fails)} COMBINACAO(OES) REPROVAM:')
        for r in invis + fails:
            print(f'   {r["theme"]} {r["what"]} x {r["bg"]}: {r["ratio"]}:1')
        falhou = True
    if checked is not None and mk:
        print('-' * 78)
        print(f'{len(mk)} PROBLEMA(S) DE MARCACAO - portao reprova')
        falhou = True
    if checked is None:
        falhou = True
    return 1 if falhou else 0


if __name__ == '__main__':
    sys.exit(run())
