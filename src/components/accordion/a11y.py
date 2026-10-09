"""
QA de acessibilidade do Accordion.

Como nos outros componentes, a validacao e por COMBINACAO RENDERIZADA - estado
x tema - contra o fundo EFETIVO, nao par de token solto.

O QUE O FUNDO EFETIVO MUDA AQUI

  So o cabecalho (<summary>) muda de fundo: repouso, hover, pressed. O foco
  volta ao repouso e soma o anel (decisao I). Titulo e chevron medem contra o
  fundo do cabecalho em cada estado. A divisoria e a borda de cima do
  conteudo: encosta no cabecalho por cima e no conteudo por baixo, e mede
  contra os dois, guardando o pior. O item mede contra a PAGINA, e a pagina e
  so `bg-surface` - a regra 14 proibe a tela e o card. O anel e desenhado
  fora do cabecalho, com o respiro em `bg-canvas`: mede contra a pagina e
  contra o respiro.

TRES JULGAMENTOS

  1. Texto: piso 4,5:1 do 1.4.3. Tem que passar - sem excecao.
  2. Chevron, divisoria, limite do item e anel: piso 3:1 do 1.4.11. Divisoria
     e limite ficam abaixo - sao as excecoes declaradas `divisoria-decorativa`
     e `item-nao-se-separa-pelo-fundo` (etapa 3). Chevron e anel tem que passar.
  3. Item INVISIVEL - fundo igual a pagina. A excecao cobre item discreto, nao
     item que nao existe. Isso reprova.

O CONTRATO DE MARCACAO E A OUTRA METADE DESTA ETAPA

  Regras de uso da etapa 4, medidas no HTML emitido:

    a) `.al-accordion` e um <details> (regra 24);
    b) o primeiro filho e o <summary class="al-accordion__header"> - e
       `.al-accordion__header` so existe em <summary> (regra 24);
    c) o <summary> tem nome: `.al-accordion__title` com texto (regra 15);
    d) nada de <h1>-<h6> dentro do <summary> (regra 25);
    e) nada interativo dentro do <summary> - link, botao, campo, tabindex,
       role de acionavel (regra 17);
    f) icone e chevron com aria-hidden="true" (regras 18 e 19);
    g) nada de Accordion dentro de Accordion (regra 5);
    h) nativo puro: sem role, aria-expanded, aria-controls nem tabindex no
       <details> ou no <summary> (regra 24);
    i) sem disabled: nem `disabled`, nem `aria-disabled` (regra 20);
    j) exatamente um `.al-accordion__content`, filho direto, depois do
       <summary>.

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
from htmltree import Tree, walk, has, ancestors, text_of  # noqa: E402
FOUND = json.load(open(TOKENS_JSON))
ACC = json.load(open(comp_out('accordion', 'tokens.json')))

SEM = FOUND['color']['semantic']
ALIAS = ACC['alias']
THEMES = ('light', 'dark')

TEXT_FLOOR = 4.5          # 1.4.3
NON_TEXT_FLOOR = 3.0      # 1.4.11
EXC_DIV = 'divisoria-decorativa'
EXC_ITEM = 'item-nao-se-separa-pelo-fundo'

DEFAULT_HTML = SITE_HTML
OUT_JSON = comp_out('accordion', 'a11y.json')

PAGINA = 'bg-surface'     # regra 14: so aqui

# estado -> papel do fundo do cabecalho. Foco = repouso (decisao I).
ESTADOS = (('repouso', 'bg'), ('hover', 'bg-hover'), ('pressed', 'bg-active'), ('foco', 'bg'))

HEADINGS = {'h1', 'h2', 'h3', 'h4', 'h5', 'h6'}
ACTIONABLE_ROLES = {'button', 'link', 'checkbox', 'radio', 'switch', 'menuitem', 'tab', 'option'}


def sem(name, theme):
    """tokens.json guarda o semantico como [claro, escuro]."""
    v = SEM[name]
    return v[THEMES.index(theme)] if isinstance(v, list) else v[theme]


def acc(role, theme):
    """Cor de um papel do Accordion, seguindo o alias ate o semantico."""
    return sem(ALIAS[f'accordion-{role}'], theme)


# ─────────────────────────────────────────────── contraste
def row(theme, estado, what, fg_name, fg, bg_name, bg, floor, exc=None, invisible=False):
    ratio = round(cr(fg, bg), 2)
    ok = ratio >= floor
    return {
        'theme': theme, 'state': estado, 'what': what,
        'fg': fg_name, 'fgHex': fg, 'bg': bg_name, 'bgHex': bg,
        'ratio': ratio, 'floor': floor, 'pass': ok,
        'invisible': invisible,
        'exception': None if ok or invisible else exc,
    }


def contrast_rows():
    rows = []
    for theme in THEMES:
        titulo = acc('title', theme)
        conteudo = acc('bg', theme)
        linha = acc('divider', theme)
        pg = sem(PAGINA, theme)

        for estado, papel in ESTADOS:
            cab = acc(papel, theme)
            nome = ALIAS[f'accordion-{papel}']
            # 1. titulo e chevron (currentColor) contra o cabecalho
            rows.append(row(theme, estado, 'titulo', ALIAS['accordion-title'], titulo,
                            nome, cab, TEXT_FLOOR))
            rows.append(row(theme, estado, 'chevron', ALIAS['accordion-title'], titulo,
                            nome, cab, NON_TEXT_FLOOR))
            # 2. divisoria (so aberto) - entre cabecalho e conteudo, o pior
            if estado != 'foco':      # foco tem o fundo do repouso: mesma medida
                pior = min((cr(linha, cab), nome, cab),
                           (cr(linha, conteudo), ALIAS['accordion-bg'], conteudo))
                rows.append(row(theme, estado, 'divisoria', ALIAS['accordion-divider'], linha,
                                pior[1], pior[2], NON_TEXT_FLOOR, EXC_DIV))

        # 3. limite do item contra a pagina
        rows.append(row(theme, 'repouso', 'limite-pelo-fundo', ALIAS['accordion-bg'], conteudo,
                        PAGINA, pg, NON_TEXT_FLOOR, EXC_ITEM,
                        invisible=conteudo.lower() == pg.lower()))

        # 4. anel - fora do cabecalho; o respiro e bg-canvas
        anel = sem('shadow-focus-default', theme)
        respiro = sem('bg-canvas', theme)
        pior = min((cr(anel, pg), PAGINA, pg), (cr(anel, respiro), 'bg-canvas (respiro)', respiro))
        rows.append(row(theme, 'foco', 'anel', 'shadow-focus-default', anel,
                        pior[1], pior[2], NON_TEXT_FLOOR))
    return rows


# ─────────────────────────────────────────────── marcacao
def interactive(node):
    a, tag = node['attrs'], node['tag']
    if tag == 'a' and 'href' in a:
        return True
    if tag in ('button', 'input', 'select', 'textarea', 'summary', 'details'):
        return True
    if 'tabindex' in a and a['tabindex'] != '-1':
        return True
    return a.get('role') in ACTIONABLE_ROLES


NATIVE_ONLY = ('role', 'aria-expanded', 'aria-controls', 'tabindex')


def markup_contract(path):
    if not os.path.exists(path):
        return None, [f'{path} nao existe']
    t = Tree()
    t.feed(open(path, encoding='utf-8').read())

    checked, problems = 0, []
    for n in walk(t.root):
        a, tag, ln = n['attrs'], n['tag'], n['line']

        # (b) o cabecalho so existe em <summary>
        if has(n, 'al-accordion__header') and tag != 'summary':
            problems.append(f'linha {ln}: .al-accordion__header em <{tag}> - o cabecalho e o '
                            f'<summary> nativo (regra 24)')

        if not has(n, 'al-accordion'):
            continue
        checked += 1

        # (a) <details>
        if tag != 'details':
            problems.append(f'linha {ln}: .al-accordion em <{tag}> - o item e um <details> '
                            f'nativo (regra 24)')

        # (g) nada de Accordion dentro de Accordion
        if any(has(p, 'al-accordion') for p in ancestors(n)):
            problems.append(f'linha {ln}: Accordion dentro de Accordion (regra 5)')

        # (i) sem disabled
        if 'disabled' in a or 'aria-disabled' in a:
            problems.append(f'linha {ln}: Accordion desabilitado - item sem conteudo sai da '
                            f'pilha (regra 20)')

        # (h) nativo puro no <details>
        for attr in NATIVE_ONLY:
            if attr in a:
                problems.append(f'linha {ln}: {attr} no <details> - o navegador ja anuncia o '
                                f'estado; nada de ARIA manual (regra 24)')

        kids = n['kids']
        # (b) o primeiro filho e o summary do componente
        head = kids[0] if kids else None
        if head is None or head['tag'] != 'summary' or not has(head, 'al-accordion__header'):
            problems.append(f'linha {ln}: o primeiro filho do Accordion tem que ser '
                            f'<summary class="al-accordion__header"> (regra 24)')
            continue

        ha, hl = head['attrs'], head['line']
        # (h) nativo puro no <summary>
        for attr in NATIVE_ONLY:
            if attr in ha:
                problems.append(f'linha {hl}: {attr} no <summary> - nativo puro (regra 24)')
        if 'disabled' in ha or 'aria-disabled' in ha:
            problems.append(f'linha {hl}: <summary> desabilitado (regra 20)')

        desc = list(walk(head))
        # (c) nome
        titulos = [d for d in desc if has(d, 'al-accordion__title')]
        if len(titulos) != 1 or not text_of(titulos[0]):
            problems.append(f'linha {hl}: o <summary> precisa de um .al-accordion__title com '
                            f'texto - e o nome anunciado (regra 15)')
        for d in desc:
            # (d) heading
            if d['tag'] in HEADINGS:
                problems.append(f'linha {d["line"]}: <{d["tag"]}> dentro do <summary> - em parte '
                                f'dos leitores sai da lista de titulos; o titulo real vai '
                                f'ANTES da pilha (regra 25)')
            # (e) interativo
            if interactive(d):
                problems.append(f'linha {d["line"]}: <{d["tag"]}> interativo dentro do <summary> '
                                f'- o cabecalho inteiro ja e o botao (regra 17)')
            # (f) icones decorativos
            if (has(d, 'al-accordion__icon') or has(d, 'al-accordion__chevron')) \
                    and d['attrs'].get('aria-hidden') != 'true':
                problems.append(f'linha {d["line"]}: icone do Accordion sem aria-hidden="true" - '
                                f'e decorativo; quem fala e o titulo (regras 18 e 19)')

        # (j) um conteudo, filho direto, depois do summary
        conteudos = [k for k in kids if has(k, 'al-accordion__content')]
        soltos = [d for d in walk(n) if has(d, 'al-accordion__content') and d['parent'] is not n]
        if len(conteudos) != 1 or soltos:
            problems.append(f'linha {ln}: o Accordion tem que ter exatamente um '
                            f'.al-accordion__content, filho direto do <details>')
        elif kids.index(conteudos[0]) == 0:
            problems.append(f'linha {ln}: .al-accordion__content antes do <summary>')

    if checked == 0:
        return None, ['nenhum .al-accordion no HTML - o componente entra no site na '
                      'etapa 7; ate la este portao fica PENDENTE']
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
    print('QA DE ACESSIBILIDADE DO ACCORDION')
    print('=' * 78)
    print('\nCOMBINACOES RENDERIZADAS (tema x estado), pagina bg-surface')
    for r in rows:
        if r['invisible']:
            mark, nota = 'XX', 'INVISIVEL - nada separa o item da pagina'
        elif r['pass']:
            mark, nota = 'ok', 'passa'
        elif r['exception']:
            mark, nota = '~~', f'excecao "{r["exception"]}"'
        else:
            mark, nota = 'XX', 'REPROVA'
        print(f'  {mark} {r["theme"]:<5} {r["state"]:<8} {r["what"]:<17} '
              f'x {r["bg"]:<20} {r["ratio"]:5.2f} (piso {r["floor"]})  {nota}')

    print('\nCONTRATO DE MARCACAO')
    print(f'     fonte: {os.path.relpath(path, ROOT)}')
    if checked is None:
        for p in mk:
            print(f'     PENDENTE: {p}')
    else:
        print(f'     {checked} accordion(s) conferido(s), 10 regras (a-j)')
        for p in mk:
            print(f'     PROBLEMA: {p}')

    print('-' * 78)
    print(f'{len(rows)} medicoes  |  passam: {len(passa)}  |  excecoes: {len(excs)}  |  '
          f'reprovas: {len(fails) + len(invis)}')

    json.dump({
        'component': 'accordion',
        'criterion': 'WCAG 1.4.3 texto + 1.4.11 nao-textual + item visivel',
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
            print(f'   {r["theme"]} {r["state"]} {r["what"]} x {r["bg"]}: {r["ratio"]}:1')
        falhou = True
    if checked is not None and mk:
        print('-' * 78)
        print(f'{len(mk)} PROBLEMA(S) DE MARCACAO - portao reprova')
        falhou = True
    return 1 if falhou else 0


if __name__ == '__main__':
    sys.exit(run())
