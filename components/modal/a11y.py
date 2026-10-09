"""
QA de acessibilidade do Modal.

Como nos outros componentes, a validacao e por COMBINACAO RENDERIZADA - papel
x tema - contra o fundo EFETIVO, nao par de token solto.

O QUE O FUNDO EFETIVO MUDA AQUI

  O Modal e uma camada: o que o usuario ve atras dele e a pagina ESCURECIDA
  pelo scrim, composta (scrim com transparencia sobre bg-canvas ou bg-surface).
  Dentro dele tudo mora em `bg-surface-raised`, inclusive os botoes do
  rodape - entao o par que importa para o botao nao e o da etapa do Button
  (contra tela e superficie) e sim contra o card.

QUATRO JULGAMENTOS

  1. Texto (titulo): piso 4,5:1 do 1.4.3. Tem que passar.
  2. Anel de foco dos botoes e dos campos DENTRO do card, e fundo dos botoes
     de acao contra o card: piso 3:1 do 1.4.11. Tem que passar - e e o par
     que a etapa 3 nao media.
  3. Card contra a pagina escurecida: 3:1. No escuro fica em ~1,8:1: e a
     excecao `card-nao-se-separa-do-scrim-no-escuro` (decisao G, etapa 3).
  4. Card INVISIVEL (igual a pagina escurecida) reprova. A excecao cobre
     separacao discreta, nao ausencia.

O CONTRATO DE MARCACAO E A OUTRA METADE DESTA ETAPA

  Regras de uso da etapa 4, medidas no HTML emitido:

    a) `.al-modal` e um <dialog> (regra 24);
    b) sem `open` na marcacao: abre por showModal(), nunca por atributo nem
       show(). Os congelados da matriz ficam sob `inert` e sao isentos;
    c) aria-labelledby aponta para um .al-modal__title que existe (regra 25);
    d) exatamente um .al-modal__title com texto, primeiro filho (regra 5);
    e) filhos na ordem titulo, miolo, acoes (regra 10 - sem divisoria);
    f) .al-modal__actions com 1 ou 2 acoes (regras 16 e 19);
    g) a acao secundaria vem antes da principal; a principal e Primary ou
       Danger, nunca a primeira (regras 19 e 20);
    h) existe uma saida: um botao com data-al-modal-close, ou um <form
       method="dialog"> (regra 16);
    i) sem botao X: nada com .al-modal__close, nem botao sem rotulo visivel
       dentro do dialog (regra 16);
    j) nunca Modal dentro de Modal (regra 4);
    k) todo data-al-modal-open aponta para um <dialog> que existe;
    l) botao dentro do rodape tem type="button" (ou fica em <form>): sem isso
       o clique envia formulario.

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
from htmltree import Tree, walk, has, ancestors, text_of  # noqa: E402
FOUND = json.load(open(os.path.join(ROOT, 'tokens.json')))
MOD = json.load(open(os.path.join(HERE, 'tokens.json')))
BTN = json.load(open(os.path.join(ROOT, 'components', 'button', 'tokens.json')))

SEM = FOUND['color']['semantic']
ALIAS = MOD['alias']
THEMES = ('light', 'dark')

TEXT_FLOOR = 4.5
NON_TEXT_FLOOR = 3.0
EXC_SCRIM = 'card-nao-se-separa-do-scrim-no-escuro'

DEFAULT_HTML = os.path.join(ROOT, 'site', 'index.html')
OUT_JSON = os.path.join(HERE, 'a11y.json')

PAGINAS = (('canvas', 'bg-canvas'), ('surface', 'bg-surface'))


def sem(name, theme):
    v = SEM[name]
    return v[THEMES.index(theme)] if isinstance(v, list) else v[theme]


def mod(role, theme):
    return sem(ALIAS[f'modal-{role}'], theme)


# ─────────────────────────────────────────────── contraste
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

        # 1. titulo (e o texto do miolo, que herda a mesma cor)
        rows.append(row(theme, 'titulo', ALIAS['modal-title'], mod('title', theme),
                        card_name, card, TEXT_FLOOR))

        # 2. o que mora DENTRO do card - o par que a etapa do Button nao media
        anel = sem('shadow-focus-default', theme)
        rows.append(row(theme, 'anel-no-card', 'shadow-focus-default', anel,
                        card_name, card, NON_TEXT_FLOOR))
        rows.append(row(theme, 'botao-principal-no-card', 'bg-brand', sem('bg-brand', theme),
                        card_name, card, NON_TEXT_FLOOR))
        rows.append(row(theme, 'botao-perigo-no-card', 'bg-danger', sem('bg-danger', theme),
                        card_name, card, NON_TEXT_FLOOR))
        sec = sem(BTN['alias']['button-secondary-border'], theme)
        rows.append(row(theme, 'botao-secundario-borda-no-card',
                        BTN['alias']['button-secondary-border'], sec, card_name, card,
                        NON_TEXT_FLOOR))

        # 3. card contra a pagina ESCURECIDA pelo scrim
        for nome, papel in PAGINAS:
            pagina = composite(mod('scrim', theme), sem(papel, theme))
            rows.append(row(theme, f'card-na-{nome}-escurecida', card_name, card,
                            f'{papel}+scrim', pagina, NON_TEXT_FLOOR, EXC_SCRIM,
                            invisible=card.lower() == pagina.lower()))
    return rows


# ─────────────────────────────────────────────── marcacao
def is_action(n):
    return n['tag'] == 'button' or (n['tag'] == 'a' and 'href' in n['attrs'])


def markup_contract(path):
    if not os.path.exists(path):
        return None, [f'{path} nao existe']
    t = Tree()
    t.feed(open(path, encoding='utf-8').read())
    nodes = list(walk(t.root))
    ids = {n['attrs']['id']: n for n in nodes if 'id' in n['attrs']}

    checked, problems = 0, []

    # (k) todo opener aponta para um <dialog>
    for n in nodes:
        alvo = n['attrs'].get('data-al-modal-open')
        if alvo is not None:
            d = ids.get(alvo)
            if d is None or d['tag'] != 'dialog' or not has(d, 'al-modal'):
                problems.append(f'linha {n["line"]}: data-al-modal-open="{alvo}" nao aponta para um '
                                f'<dialog class="al-modal">')

    for n in nodes:
        a, tag, ln = n['attrs'], n['tag'], n['line']
        if not has(n, 'al-modal'):
            continue
        checked += 1
        congelado = any('inert' in p['attrs'] for p in ancestors(n))

        # (a)
        if tag != 'dialog':
            problems.append(f'linha {ln}: .al-modal em <{tag}> - o Modal e um <dialog> nativo (regra 24)')
            continue
        # (b)
        if 'open' in a and not congelado:
            problems.append(f'linha {ln}: <dialog open> - o Modal abre por showModal(), nunca por '
                            f'atributo (regra 24)')
        # (j)
        if any(has(p, 'al-modal') for p in ancestors(n)):
            problems.append(f'linha {ln}: Modal dentro de Modal (regra 4)')

        kids = [k for k in n['kids'] if k['tag'] != '#text']
        titulos = [d for d in walk(n) if has(d, 'al-modal__title')]
        # (d)
        if len(titulos) != 1 or not text_of(titulos[0]):
            problems.append(f'linha {ln}: o Modal precisa de exatamente um .al-modal__title com '
                            f'texto (regra 5)')
        # (c)
        lab = a.get('aria-labelledby')
        if not lab:
            problems.append(f'linha {ln}: sem aria-labelledby - o <dialog> nao se nomeia sozinho '
                            f'(regra 25)')
        elif lab not in ids or not has(ids[lab], 'al-modal__title'):
            problems.append(f'linha {ln}: aria-labelledby="{lab}" nao aponta para um '
                            f'.al-modal__title (regra 25)')
        elif titulos and ids[lab] is not titulos[0]:
            problems.append(f'linha {ln}: aria-labelledby aponta para o titulo de OUTRO Modal (regra 25)')

        # (e) ordem titulo, miolo, acoes
        ordem = [next((c for c in ('al-modal__title', 'al-modal__content', 'al-modal__actions')
                       if has(k, c)), None) for k in kids]
        esperado = [c for c in ('al-modal__title', 'al-modal__content', 'al-modal__actions')
                    if c in ordem]
        if [o for o in ordem if o] != esperado or ordem and ordem[0] != 'al-modal__title':
            problems.append(f'linha {ln}: filhos fora da ordem titulo, miolo, acoes (regra 10)')
        if any(o is None for o in ordem):
            problems.append(f'linha {ln}: filho direto sem classe do Modal - sem divisoria nem '
                            f'peca solta entre as partes (regra 10)')

        # (i) sem X
        if any(has(d, 'al-modal__close') for d in walk(n)):
            problems.append(f'linha {ln}: .al-modal__close - o Modal nao tem botao X (regra 16)')

        acoes_box = [k for k in kids if has(k, 'al-modal__actions')]
        if len(acoes_box) != 1:
            problems.append(f'linha {ln}: o Modal precisa de exatamente um .al-modal__actions '
                            f'(regras 16 e 22)')
            continue
        acoes = [d for d in walk(acoes_box[0]) if is_action(d)]
        # (f)
        if not 1 <= len(acoes) <= 2:
            problems.append(f'linha {ln}: {len(acoes)} acoes no rodape - sao uma ou duas (regras 16 e 19)')
        # (g)
        if len(acoes) == 2:
            primeira, ultima = acoes
            for ac in (primeira,):
                if has(ac, 'al-btn--primary') or has(ac, 'al-btn--danger'):
                    problems.append(f'linha {ac["line"]}: a acao principal vem POR ULTIMO; a '
                                    f'primeira e a secundaria (regras 19 e 20)')
            if not (has(ultima, 'al-btn--primary') or has(ultima, 'al-btn--danger')):
                problems.append(f'linha {ultima["line"]}: a ultima acao deveria ser Primary ou '
                                f'Danger (regras 19 e 20)')
        # (h) saida
        saida = any('data-al-modal-close' in d['attrs'] for d in walk(n)) or \
            any(d['tag'] == 'form' and d['attrs'].get('method') == 'dialog' for d in walk(n))
        if not saida:
            problems.append(f'linha {ln}: nenhuma saida - sem data-al-modal-close nem '
                            f'<form method="dialog"> (regra 16)')
        # (i) botao sem rotulo visivel dentro do dialog
        for d in walk(n):
            if d['tag'] == 'button' and not text_of(d):
                problems.append(f'linha {d["line"]}: botao sem texto visivel - o Modal nao tem X '
                                f'nem botao so de icone (regra 16)')
        # (l) type="button"
        for ac in acoes:
            if ac['tag'] == 'button' and ac['attrs'].get('type') not in ('button', 'submit', 'reset'):
                problems.append(f'linha {ac["line"]}: <button> sem type - dentro de <form> o padrao '
                                f'e submit')

    if checked == 0:
        return None, ['nenhum .al-modal no HTML']
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
    print('QA DE ACESSIBILIDADE DO MODAL')
    print('=' * 78)
    print('\nCOMBINACOES RENDERIZADAS (tema x papel)')
    for r in rows:
        if r['invisible']:
            mark, nota = 'XX', 'INVISIVEL - nada separa o card da pagina'
        elif r['pass']:
            mark, nota = 'ok', 'passa'
        elif r['exception']:
            mark, nota = '~~', f'excecao "{r["exception"]}"'
        else:
            mark, nota = 'XX', 'REPROVA'
        print(f'  {mark} {r["theme"]:<5} {r["what"]:<32} x {r["bg"]:<24} '
              f'{r["ratio"]:5.2f} (piso {r["floor"]})  {nota}')

    print('\nCONTRATO DE MARCACAO')
    print(f'     fonte: {os.path.relpath(path, ROOT)}')
    if checked is None:
        for p in mk:
            print(f'     PENDENTE: {p}')
    else:
        print(f'     {checked} modal(is) conferido(s), 12 regras (a-l)')
        for p in mk:
            print(f'     PROBLEMA: {p}')

    print('-' * 78)
    print(f'{len(rows)} medicoes  |  passam: {len(passa)}  |  excecoes: {len(excs)}  |  '
          f'reprovas: {len(fails) + len(invis)}')

    json.dump({
        'component': 'modal',
        'criterion': 'WCAG 1.4.3 texto + 1.4.11 nao-textual + card visivel',
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
