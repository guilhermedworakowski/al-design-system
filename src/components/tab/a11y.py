"""
QA de acessibilidade do Tab.

Como nos outros componentes, a validacao e por COMBINACAO RENDERIZADA - tipo x
selecionada x estado x tema x pagina - contra o fundo EFETIVO, nao par de
token solto.

O QUE O FUNDO EFETIVO MUDA AQUI

  O rotulo mede contra o fundo da CAIXA DO ROTULO quando ela tem fundo (hover,
  pressed, Square selecionada) e contra a PAGINA quando nao tem (repouso e
  foco da nao selecionada, Line selecionada em repouso e foco). A pagina e a
  tela ou a superficie - a sidebar costuma ficar na superficie (decisao E).
  A linha do Line, o fundo da Square selecionada e o anel medem contra a
  pagina. O anel tem respiro em `bg-canvas`, entao mede contra os dois.

TRES JULGAMENTOS

  1. Rotulo: piso 4,5:1 do 1.4.3. A unica excecao e a de marca que a
     Foundation ja declara (`marca-no-hover-escuro`: branco sobre
     bg-brand-hover no escuro, 3,85:1).
  2. Indicadores (linha, fundo selecionado, anel): piso 3:1 do 1.4.11. A linha
     cinza e `trilho-decorativo`; o fundo tonal em repouso e foco e
     `selecao-tonal` (decisao H). O pressed da Square selecionada sobre a
     superficie escura e `pressed-na-superficie-escura` (2,74:1 - H(a),
     reconfirmada na etapa 6). O hover nao tem excecao e tem que passar.
     O fundo do hover/pressed da NAO selecionada nao e medido: e retorno de
     ponteiro, nao estado que precise ser identificado (o rotulo escurece
     junto e e ele que mede).
  3. Selecao INDISTINGUIVEL - a selecionada igual a nao selecionada no mesmo
     estado: mesmo fundo, mesma cor de rotulo e mesma linha. A excecao cobre
     selecao discreta, nao selecao que nao existe. Isso reprova.

O CONTRATO DE MARCACAO E A OUTRA METADE DESTA ETAPA

  Regras de uso da etapa 4, medidas no HTML emitido. Amostras congeladas
  (`aria-hidden="true"` + `inert`) ficam fora: nao existem para o leitor de
  tela nem para o teclado - mas a amostra tem que ser inerte de verdade.

    a) grupo de painel: `.al-tabs[role=tablist]` com nome (aria-label ou
       aria-labelledby que existe) (regra 21);
    b) aba de painel e `<button type="button" role="tab">` com aria-selected
       "true"/"false" e aria-controls apontando para um `role="tabpanel"`
       ligado de volta por aria-labelledby (regra 21);
    c) exatamente uma selecionada por grupo, e o tabindex inicial rola: a
       selecionada sem tabindex=-1, as outras com -1 (regras 7 e 21);
    d) navegacao: grupo que nao e tablist mora num `<nav>` com nome, cada aba
       e `<a href>`, sem role="tab"/aria-selected, no maximo um aria-current
       (regra 22);
    e) toda aba tem `.al-tab__label` com texto - e o nome anunciado (regra 14);
    f) sem disabled nem aria-disabled (regra 18);
    g) aninhamento: no maximo dois niveis, Line fora e Square dentro
       (decisao I);
    h) `<ul class="al-tabs">` so com `<li>` filhos, e a aba dentro do `<li>`;
    i) id unico no documento - o tab e o painel se ligam por id (licao do
       Select);
    j) de 2 a 6 abas por grupo (regra 8);
    k) o painel comeca com um titulo igual ao rotulo da aba (regra 25 - e o
       que paga a `selecao-tonal`);
    l) amostra congelada (aria-hidden) e `inert`.

ORDEM DE EXECUCAO - mesma dos outros: roda DEPOIS do HTML que ele mede.

Rodar: python3 a11y.py [caminho.html]
       sem argumento, mede build/site/index.html
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
EXC_TRILHO = 'trilho-decorativo'
EXC_TONAL = 'selecao-tonal'
EXC_MARCA = 'marca-no-hover-escuro'
EXC_PRESSED = 'pressed-na-superficie-escura'

PAGINAS = ('bg-canvas', 'bg-surface')
ESTADOS = ('repouso', 'hover', 'pressed', 'foco')

DEFAULT_HTML = SITE_HTML
OUT_JSON = comp_out('tab', 'a11y.json')

HEADINGS = {'h1', 'h2', 'h3', 'h4', 'h5', 'h6'}


def sem(name, theme):
    """tokens.json guarda o semantico como [claro, escuro]."""
    v = SEM[name]
    return v[THEMES.index(theme)] if isinstance(v, list) else v[theme]


def tab(role, theme):
    """(semantico, hex) de um papel do Tab, seguindo o alias."""
    ref = ALIAS[f'tab-{role}']
    return ref, sem(ref, theme)


# ─────────────────────────────────────────────── o que cada combinacao pinta
def pintura(tipo, sel, estado):
    """Papeis de fundo da caixa do rotulo (None = transparente), do rotulo e da
    linha - exatamente o que o tab.css escolhe para essa combinacao."""
    if tipo == 'square' and sel:
        par = {'repouso': ('square-bg-selected', 'square-label-selected'),
               'foco':    ('square-bg-selected', 'square-label-selected'),
               'hover':   ('square-bg-selected-hover', 'square-label-selected-hover'),
               'pressed': ('square-bg-selected-active', 'square-label-selected-active')}[estado]
        return par[0], par[1], None
    bg = {'repouso': None, 'foco': None, 'hover': 'bg-hover', 'pressed': 'bg-active'}[estado]
    if tipo == 'line' and sel:
        rotulo = 'line-label-selected'
    else:
        rotulo = {'repouso': 'label', 'foco': 'label',
                  'hover': 'label-hover', 'pressed': 'label-active'}[estado]
    linha = None
    if tipo == 'line':
        linha = 'line-indicator-selected' if sel else 'line-indicator'
    return bg, rotulo, linha


def row(theme, tipo, sel, estado, pagina, what, fg_name, fg, bg_name, bg, floor, exc=None):
    ratio = round(cr(fg, bg), 2)
    ok = ratio >= floor
    return {
        'theme': theme, 'type': tipo, 'selected': sel, 'state': estado, 'page': pagina,
        'what': what, 'fg': fg_name, 'fgHex': fg, 'bg': bg_name, 'bgHex': bg,
        'ratio': ratio, 'floor': floor, 'pass': ok, 'indistinct': False,
        'exception': None if ok else exc,
    }


def contrast_rows():
    rows = []
    for theme in THEMES:
        anel = sem('shadow-focus-default', theme)
        respiro = sem('bg-canvas', theme)
        for pagina in PAGINAS:
            pg = sem(pagina, theme)
            for tipo in ('line', 'square'):
                for sel in (False, True):
                    for estado in ESTADOS:
                        bg_role, rot_role, lin_role = pintura(tipo, sel, estado)
                        bg_name, bg_hex = tab(bg_role, theme) if bg_role else (pagina, pg)
                        rot_name, rot_hex = tab(rot_role, theme)

                        # 1. rotulo contra o fundo efetivo
                        exc = EXC_MARCA if (theme == 'dark' and rot_role == 'square-label-selected-hover') else None
                        rows.append(row(theme, tipo, sel, estado, pagina, 'rotulo',
                                        rot_name, rot_hex, bg_name, bg_hex, TEXT_FLOOR, exc))

                        # 2a. linha do Line - so muda com a selecao, mede no repouso
                        if lin_role and estado == 'repouso':
                            ln, lh = tab(lin_role, theme)
                            rows.append(row(theme, tipo, sel, estado, pagina, 'linha', ln, lh,
                                            pagina, pg, NON_TEXT_FLOOR,
                                            None if sel else EXC_TRILHO))

                        # 2b. fundo da Square selecionada contra a pagina
                        if tipo == 'square' and sel:
                            exc = (EXC_TONAL if estado in ('repouso', 'foco')
                                   else EXC_PRESSED if estado == 'pressed' else None)
                            rows.append(row(theme, tipo, sel, estado, pagina, 'fundo-selecionado',
                                            bg_name, bg_hex, pagina, pg, NON_TEXT_FLOOR, exc))

                        # 2c. anel - em volta da caixa do rotulo, respiro em bg-canvas
                        if estado == 'foco':
                            pior = min((cr(anel, pg), pagina, pg),
                                       (cr(anel, respiro), 'bg-canvas (respiro)', respiro))
                            rows.append(row(theme, tipo, sel, estado, pagina, 'anel',
                                            'shadow-focus-default', anel, pior[1], pior[2],
                                            NON_TEXT_FLOOR))

                # 3. selecao indistinguivel: mesma pintura com e sem selecao
                for estado in ESTADOS:
                    a = [tab(r, theme)[1] if r else pg for r in pintura(tipo, False, estado)]
                    b = [tab(r, theme)[1] if r else pg for r in pintura(tipo, True, estado)]
                    if [x.lower() for x in a] == [x.lower() for x in b]:
                        r = row(theme, tipo, True, estado, pagina, 'selecao', '-', b[1],
                                '-', a[1], NON_TEXT_FLOOR)
                        r.update({'pass': False, 'indistinct': True, 'exception': None})
                        rows.append(r)
    return rows


# ─────────────────────────────────────────────── marcacao
def hidden_sample(node):
    """Amostra congelada: dentro (ou sendo) de aria-hidden="true"."""
    return any(n['attrs'].get('aria-hidden') == 'true' for n in [node, *ancestors(node)])


def tabs_of(group):
    """Abas do grupo, sem descer em grupos aninhados."""
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
        return None, 0, [f'{path} nao existe']
    t = Tree()
    t.feed(open(path, encoding='utf-8').read())
    nodes = list(walk(t.root))
    ids = {n['attrs']['id']: n for n in nodes if n['attrs'].get('id')}
    problems = []

    # (i) id unico
    for i, c in Counter(n['attrs']['id'] for n in nodes if n['attrs'].get('id')).items():
        if c > 1:
            problems.append(f'id "{i}" repetido {c} vezes - tab e painel se ligam por id')

    grupos, amostras = 0, 0
    for g in nodes:
        if not has(g, 'al-tabs'):
            continue
        ln, a = g['line'], g['attrs']

        if hidden_sample(g):
            amostras += 1
            # (l) amostra e inerte
            dono = next((n for n in [g, *ancestors(g)] if n['attrs'].get('aria-hidden') == 'true'))
            if 'inert' not in dono['attrs']:
                problems.append(f'linha {dono["line"]}: amostra aria-hidden sem inert - o '
                                f'teclado chega numa aba que o leitor de tela nao ve')
            continue

        grupos += 1
        abas = tabs_of(g)
        painel = a.get('role') == 'tablist'

        # (j) quantidade
        if not 2 <= len(abas) <= 6:
            problems.append(f'linha {ln}: grupo com {len(abas)} aba(s) - de 2 a 6 (regra 8)')

        # (g) aninhamento
        pais = [p for p in ancestors(g) if has(p, 'al-tabs')]
        nivel = 1 + sum(1 for p in nodes if has(p, 'al-tabs') and not hidden_sample(p)
                        and p is not g and _contem_painel_de(p, g, ids))
        if pais:
            problems.append(f'linha {ln}: .al-tabs dentro de .al-tabs - o segundo nivel mora '
                            f'no painel, nao no grupo')
        if nivel > 2:
            problems.append(f'linha {ln}: {nivel} niveis de abas - no maximo dois (decisao I)')
        if nivel == 2 and not has(g, 'al-tabs--square'):
            problems.append(f'linha {ln}: segundo nivel em Line - o de dentro e Square '
                            f'(decisao I)')
        if nivel == 2 and _pai_nivel(g, nodes, ids) is not None and \
                has(_pai_nivel(g, nodes, ids), 'al-tabs--square'):
            problems.append(f'linha {ln}: primeiro nivel em Square - o de fora e Line '
                            f'(decisao I)')

        # (h) lista
        if g['tag'] in ('ul', 'ol'):
            for k in g['kids']:
                if k['tag'] != 'li':
                    problems.append(f'linha {k["line"]}: <{k["tag"]}> direto em '
                                    f'<{g["tag"]} class="al-tabs"> - so <li>')

        if painel:
            # (a) nome do grupo
            if not named(g, ids):
                problems.append(f'linha {ln}: tablist sem nome - aria-label ou aria-labelledby '
                                f'(regra 21)')
            selecionadas = 0
            for tb in abas:
                ta, tl = tb['attrs'], tb['line']
                # (b) elemento, role e estado
                if tb['tag'] != 'button' or ta.get('type') != 'button' or ta.get('role') != 'tab':
                    problems.append(f'linha {tl}: aba de painel tem que ser <button type="button" '
                                    f'role="tab"> (regra 21)')
                sel = ta.get('aria-selected')
                if sel not in ('true', 'false'):
                    problems.append(f'linha {tl}: aria-selected ausente ou invalido (regra 21)')
                if sel == 'true':
                    selecionadas += 1
                # (c) tabindex inicial
                ti = ta.get('tabindex')
                if sel == 'true' and ti == '-1':
                    problems.append(f'linha {tl}: aba selecionada com tabindex=-1 - o Tab nao '
                                    f'entra no grupo (regra 21)')
                if sel == 'false' and ti != '-1':
                    problems.append(f'linha {tl}: aba nao selecionada sem tabindex=-1 - o Tab '
                                    f'para em todas (regra 21)')
                # painel ligado nos dois sentidos
                pid = ta.get('aria-controls', '')
                p = ids.get(pid)
                if p is None or p['attrs'].get('role') != 'tabpanel':
                    problems.append(f'linha {tl}: aria-controls="{pid}" nao aponta para um '
                                    f'role="tabpanel" (regra 21)')
                else:
                    if p['attrs'].get('aria-labelledby') != ta.get('id'):
                        problems.append(f'linha {p["line"]}: painel "{pid}" sem aria-labelledby '
                                        f'de volta para a aba (regra 21)')
                    # (k) titulo igual ao rotulo
                    h = next((d for d in walk(p) if d['tag'] in HEADINGS), None)
                    rot = _rotulo(tb)
                    if h is None or text_flat(h) != rot:
                        problems.append(f'linha {p["line"]}: painel "{pid}" nao comeca com titulo '
                                        f'"{rot}" - e o que paga a selecao-tonal (regra 25)')
            # (c) exatamente uma
            if abas and selecionadas != 1:
                problems.append(f'linha {ln}: {selecionadas} abas selecionadas - exatamente '
                                f'uma (regra 7)')
        else:
            # (d) navegacao
            nav = next((p for p in ancestors(g) if p['tag'] == 'nav'), None)
            if nav is None:
                problems.append(f'linha {ln}: .al-tabs sem role="tablist" fora de <nav> - '
                                f'painel ou navegacao, um dos dois (regras 21 e 22)')
            elif not named(nav, ids):
                problems.append(f'linha {nav["line"]}: <nav> sem nome (regra 22)')
            atuais = 0
            for tb in abas:
                ta, tl = tb['attrs'], tb['line']
                if tb['tag'] != 'a' or 'href' not in ta:
                    problems.append(f'linha {tl}: aba de navegacao tem que ser <a href> (regra 22)')
                if ta.get('role') == 'tab' or 'aria-selected' in ta:
                    problems.append(f'linha {tl}: role="tab"/aria-selected num link - promete '
                                    f'um painel que nao existe (regra 22)')
                if ta.get('aria-current') not in (None, 'false'):
                    atuais += 1
            if atuais > 1:
                problems.append(f'linha {ln}: {atuais} links com aria-current - no maximo um '
                                f'(regra 22)')

        for tb in abas:
            # (e) nome
            lab = next((d for d in walk(tb) if has(d, 'al-tab__label')), None)
            if lab is None or not text_flat(lab):
                problems.append(f'linha {tb["line"]}: .al-tab sem .al-tab__label com texto '
                                f'(regra 14)')
            # (f) sem disabled
            if 'disabled' in tb['attrs'] or 'aria-disabled' in tb['attrs']:
                problems.append(f'linha {tb["line"]}: aba desabilitada - ela sai do grupo '
                                f'(regra 18)')

    # (h) aba fora de grupo
    for n in nodes:
        if has(n, 'al-tab') and not hidden_sample(n) and \
                not any(has(p, 'al-tabs') for p in ancestors(n)):
            problems.append(f'linha {n["line"]}: .al-tab fora de .al-tabs - o tipo e do grupo '
                            f'(regra 6)')

    if grupos == 0:
        return None, amostras, ['nenhum .al-tabs no HTML - o componente entra no site na '
                                'etapa 7; ate la este portao fica PENDENTE']
    return grupos, amostras, problems


def _rotulo(tb):
    lab = next((d for d in walk(tb) if has(d, 'al-tab__label')), None)
    return text_flat(lab) if lab else ''


def _paineis(g, ids):
    for tb in tabs_of(g):
        p = ids.get(tb['attrs'].get('aria-controls', ''))
        if p is not None:
            yield p


def _contem_painel_de(p, g, ids):
    """O grupo `p` tem um painel que contem o grupo `g`?"""
    return any(painel in list(ancestors(g)) for painel in _paineis(p, ids))


def _pai_nivel(g, nodes, ids):
    return next((p for p in nodes if has(p, 'al-tabs') and p is not g
                 and _contem_painel_de(p, g, ids)), None)


def run():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_HTML
    rows = contrast_rows()
    indist = [r for r in rows if r['indistinct']]
    fails = [r for r in rows if not r['pass'] and not r['exception'] and not r['indistinct']]
    excs = [r for r in rows if r['exception']]
    passa = [r for r in rows if r['pass']]

    grupos, amostras, mk = markup_contract(path)

    print('=' * 84)
    print('QA DE ACESSIBILIDADE DO TAB')
    print('=' * 84)
    print('\nCOMBINACOES RENDERIZADAS (tema x pagina x tipo x selecionada x estado)')
    for r in rows:
        if r['indistinct']:
            mark, nota = 'XX', 'INDISTINGUIVEL - selecionada igual a nao selecionada'
        elif r['pass']:
            mark, nota = 'ok', 'passa'
        elif r['exception']:
            mark, nota = '~~', f'excecao "{r["exception"]}"'
        else:
            mark, nota = 'XX', 'REPROVA'
        sel = 'sel' if r['selected'] else '   '
        print(f'  {mark} {r["theme"]:<5} {r["page"]:<10} {r["type"]:<6} {sel} {r["state"]:<7} '
              f'{r["what"]:<17} x {r["bg"]:<21} {r["ratio"]:5.2f} (piso {r["floor"]})  {nota}')

    print('\nCONTRATO DE MARCACAO')
    print(f'     fonte: {os.path.relpath(path, ROOT)}')
    if grupos is None:
        for p in mk:
            print(f'     PENDENTE: {p}')
    else:
        print(f'     {grupos} grupo(s) conferido(s), {amostras} amostra(s) congelada(s), '
              f'12 regras (a-l)')
        for p in mk:
            print(f'     PROBLEMA: {p}')

    print('-' * 84)
    print(f'{len(rows)} medicoes  |  passam: {len(passa)}  |  excecoes: {len(excs)}  |  '
          f'reprovas: {len(fails) + len(indist)}')
    for chave in (EXC_TRILHO, EXC_TONAL, EXC_PRESSED, EXC_MARCA):
        print(f'  excecao "{chave}": {sum(1 for r in excs if r["exception"] == chave)} medicoes')

    json.dump({
        'component': 'tab',
        'criterion': 'WCAG 1.4.3 rotulo + 1.4.11 indicadores + selecao distinguivel',
        'floors': {'text': TEXT_FLOOR, 'nonText': NON_TEXT_FLOOR},
        'markupSource': os.path.relpath(path, ROOT),
        'markupChecked': grupos,
        'markupSamples': amostras,
        'markupPending': grupos is None,
        'markupProblems': mk if grupos is not None else [],
        'rows': rows,
    }, open(OUT_JSON, 'w'), indent=2, ensure_ascii=False)
    print(f'{os.path.relpath(OUT_JSON, ROOT)} escrito')

    falhou = False
    if indist or fails:
        print('-' * 84)
        print(f'{len(indist) + len(fails)} COMBINACAO(OES) REPROVAM:')
        for r in indist + fails:
            print(f'   {r["theme"]} {r["page"]} {r["type"]} sel={r["selected"]} {r["state"]} '
                  f'{r["what"]} x {r["bg"]}: {r["ratio"]}:1')
        falhou = True
    if grupos is not None and mk:
        print('-' * 84)
        print(f'{len(mk)} PROBLEMA(S) DE MARCACAO - portao reprova')
        falhou = True
    return 1 if falhou else 0


if __name__ == '__main__':
    sys.exit(run())
