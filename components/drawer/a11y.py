"""
QA de acessibilidade do Drawer.

Como nos outros componentes, a validacao e por COMBINACAO RENDERIZADA - papel
x tema - contra o fundo EFETIVO, nao par de token solto.

O QUE O FUNDO EFETIVO MUDA AQUI

  O Drawer e uma camada, como o Modal: o que o usuario ve atras dele e a pagina
  ESCURECIDA pelo scrim, composta (scrim com transparencia sobre bg-canvas ou
  bg-surface). Dentro dele tudo mora em `bg-surface-raised`, inclusive o X e os
  botoes do rodape - entao o par que importa para eles nao e o da etapa do
  Button/Icon Button (contra tela e superficie) e sim contra o painel.

CINCO JULGAMENTOS

  1. Texto (titulo e ink do X): piso 4,5:1 do 1.4.3. Tem que passar.
  2. Anel de foco e fundo dos botoes de acao DENTRO do painel: piso 3:1 do
     1.4.11. Tem que passar - e e o par que a etapa 3 nao media.
  3. Painel contra a pagina escurecida: 3:1. No escuro fica em ~1,8:1: e a
     excecao `card-nao-se-separa-do-scrim-no-escuro` (etapa 3, mesma do Modal).
  4. Painel INVISIVEL (igual a pagina escurecida) reprova. A excecao cobre
     separacao discreta, nao ausencia.
  5. Hover/pressed -raised do Ghost e do Secondary (e do X): o texto passa 4,5:1
     sobre eles E eles tem que ser DIFERENTES do painel. Era o defeito do
     Modal 0.18.1 (hover igual ao fundo, no escuro, e o estado sumia); o
     Drawer nasce com o override e este julgamento o tranca.

O CONTRATO DE MARCACAO E A OUTRA METADE DESTA ETAPA

  Regras de uso da etapa 4, medidas no HTML emitido:

    a) `.al-drawer` e um <dialog> (regra 24);
    b) sem `open` na marcacao: abre por showModal(), nunca por atributo nem
       show(). Os congelados da matriz ficam sob `inert` e sao isentos;
    c) aria-labelledby aponta para um .al-drawer__title que existe (regra 25);
    d) exatamente um .al-drawer__title com texto, dentro do cabecalho (regra 6);
    e) filhos na ordem cabecalho, miolo, acoes - as acoes sao opcionais, e sem
       divisoria nem peca solta entre as partes (regra 9);
    f) .al-drawer__actions, quando existe, tem 1 ou 2 acoes (regra 20);
    g) a acao secundaria vem antes da principal; a principal e Primary e NUNCA
       Danger (regras 20 e 22);
    h) existe SEMPRE uma saida visivel (regra 14): o X, ou o rodape com um botao
       data-al-drawer-close, ou um <form method="dialog">;
    i) o X, quando existe, e um Icon Button (.al-icon-btn) com aria-label nao
       vazio, type="button", data-al-drawer-close e svg aria-hidden; nenhum
       outro botao sem texto visivel dentro do dialog (regra 26);
    j) nunca Drawer dentro de Drawer (regra 4);
    k) todo data-al-drawer-open aponta para um <dialog class="al-drawer"> que
       existe;
    l) botao dentro do rodape tem type="button" (ou fica em <form>): sem isso o
       clique envia formulario;
    m) tamanho: no maximo um modificador --sm|--md|--lg (sem modificador = md).

ORDEM DE EXECUCAO - mesma dos outros: roda DEPOIS do HTML que ele mede.

Rodar: python3 a11y.py [caminho.html]
       sem argumento, mede site/drawer-qa.html
"""
import json
import os
import sys
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
FOUND = json.load(open(os.path.join(ROOT, 'tokens.json')))
DRW = json.load(open(os.path.join(HERE, 'tokens.json')))
BTN = json.load(open(os.path.join(ROOT, 'components', 'button', 'tokens.json')))

SEM = FOUND['color']['semantic']
ALIAS = DRW['alias']
THEMES = ('light', 'dark')

TEXT_FLOOR = 4.5
NON_TEXT_FLOOR = 3.0
EXC_SCRIM = 'card-nao-se-separa-do-scrim-no-escuro'

DEFAULT_HTML = os.path.join(ROOT, 'site', 'drawer-qa.html')
OUT_JSON = os.path.join(HERE, 'a11y.json')

PAGINAS = (('canvas', 'bg-canvas'), ('surface', 'bg-surface'))

VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link',
        'meta', 'source', 'track', 'wbr'}


def lin(c):
    c = c / 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def lum(h):
    h = h.lstrip('#')[:6]
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def cr(a, b):
    l1, l2 = sorted((lum(a), lum(b)), reverse=True)
    return (l1 + 0.05) / (l2 + 0.05)


def composite(hex8, base):
    h = hex8.lstrip('#')
    a = int(h[6:8], 16) / 255
    f = [int(h[i:i + 2], 16) for i in (0, 2, 4)]
    b = [int(base.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4)]
    return '#%02X%02X%02X' % tuple(round(f[i] * a + b[i] * (1 - a)) for i in range(3))


def sem(name, theme):
    v = SEM[name]
    return v[THEMES.index(theme)] if isinstance(v, list) else v[theme]


def drw(role, theme):
    return sem(ALIAS[f'drawer-{role}'], theme)


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
        card = drw('bg', theme)
        card_name = ALIAS['drawer-bg']

        # 1. titulo (e o texto do miolo, que herda a mesma cor) e ink do X
        rows.append(row(theme, 'titulo', ALIAS['drawer-title'], drw('title', theme),
                        card_name, card, TEXT_FLOOR))
        rows.append(row(theme, 'x-icone-no-painel', 'text-primary', sem('text-primary', theme),
                        card_name, card, NON_TEXT_FLOOR))

        # 2. o que mora DENTRO do painel - o par que a etapa do Button nao media
        rows.append(row(theme, 'anel-no-painel', 'shadow-focus-default',
                        sem('shadow-focus-default', theme), card_name, card, NON_TEXT_FLOOR))
        rows.append(row(theme, 'botao-principal-no-painel', 'bg-brand', sem('bg-brand', theme),
                        card_name, card, NON_TEXT_FLOOR))
        sec = sem(BTN['alias']['button-secondary-border'], theme)
        rows.append(row(theme, 'botao-secundario-borda-no-painel',
                        BTN['alias']['button-secondary-border'], sec, card_name, card,
                        NON_TEXT_FLOOR))

        # 5. hover e pressed -raised: texto legivel E diferente do painel
        for estado in ('hover', 'active'):
            nome = f'bg-{estado}-raised'
            fundo = sem(nome, theme)
            rows.append(row(theme, f'ghost-{estado}-texto', 'text-primary',
                            sem('text-primary', theme), nome, fundo, TEXT_FLOOR))
            rows.append(row(theme, f'ghost-{estado}-distinto-do-painel', nome, fundo,
                            card_name, card, 1.0,
                            invisible=fundo.lower() == card.lower()))

        # 3. painel contra a pagina ESCURECIDA pelo scrim
        for nome, papel in PAGINAS:
            pagina = composite(drw('scrim', theme), sem(papel, theme))
            rows.append(row(theme, f'painel-na-{nome}-escurecida', card_name, card,
                            f'{papel}+scrim', pagina, NON_TEXT_FLOOR, EXC_SCRIM,
                            invisible=card.lower() == pagina.lower()))
    return rows


# ─────────────────────────────────────────────── marcacao
class Tree(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = {'tag': '#root', 'attrs': {}, 'kids': [], 'text': '', 'line': 0}
        self.stack = [self.root]
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ('style', 'script'):
            self.skip += 1
            return
        if self.skip:
            return
        node = {'tag': tag, 'attrs': dict((k, v or '') for k, v in attrs),
                'kids': [], 'text': '', 'line': self.getpos()[0], 'parent': self.stack[-1]}
        self.stack[-1]['kids'].append(node)
        if tag not in VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID and not self.skip and self.stack[-1]['tag'] == tag:
            self.stack.pop()

    def handle_endtag(self, tag):
        if tag in ('style', 'script'):
            self.skip = max(0, self.skip - 1)
            return
        if self.skip:
            return
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i]['tag'] == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        if not self.skip:
            self.stack[-1]['text'] += data


def walk(node):
    for k in node['kids']:
        yield k
        yield from walk(k)


def classes(node):
    return node['attrs'].get('class', '').split()


def has(node, cls):
    return cls in classes(node)


def ancestors(node):
    p = node.get('parent')
    while p is not None and p['tag'] != '#root':
        yield p
        p = p.get('parent')


def text_of(node):
    return (node['text'] + ''.join(text_of(k) for k in node['kids'])).strip()


def is_action(n):
    return n['tag'] == 'button' or (n['tag'] == 'a' and 'href' in n['attrs'])


PARTES = ('al-drawer__header', 'al-drawer__content', 'al-drawer__actions')


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
        alvo = n['attrs'].get('data-al-drawer-open')
        if alvo is not None:
            d = ids.get(alvo)
            if d is None or d['tag'] != 'dialog' or not has(d, 'al-drawer'):
                problems.append(f'linha {n["line"]}: data-al-drawer-open="{alvo}" nao aponta para um '
                                f'<dialog class="al-drawer">')

    for n in nodes:
        a, tag, ln = n['attrs'], n['tag'], n['line']
        if not has(n, 'al-drawer'):
            continue
        checked += 1
        congelado = any('inert' in p['attrs'] for p in ancestors(n))

        # (a)
        if tag != 'dialog':
            problems.append(f'linha {ln}: .al-drawer em <{tag}> - o Drawer e um <dialog> nativo (regra 24)')
            continue
        # (b)
        if 'open' in a and not congelado:
            problems.append(f'linha {ln}: <dialog open> - o Drawer abre por showModal(), nunca por '
                            f'atributo (regra 24)')
        # (j)
        if any(has(p, 'al-drawer') for p in ancestors(n)):
            problems.append(f'linha {ln}: Drawer dentro de Drawer (regra 4)')
        # (m)
        tams = [c for c in classes(n) if c in ('al-drawer--sm', 'al-drawer--md', 'al-drawer--lg')]
        if len(tams) > 1 or any(c.startswith('al-drawer--') and c not in tams for c in classes(n)):
            problems.append(f'linha {ln}: tamanho invalido - um de --sm, --md ou --lg')

        kids = [k for k in n['kids']]
        titulos = [d for d in walk(n) if has(d, 'al-drawer__title')]
        cabecalhos = [k for k in kids if has(k, 'al-drawer__header')]
        # (d)
        if len(titulos) != 1 or not text_of(titulos[0]):
            problems.append(f'linha {ln}: o Drawer precisa de exatamente um .al-drawer__title com '
                            f'texto (regra 6)')
        elif len(cabecalhos) != 1 or titulos[0] not in list(walk(cabecalhos[0])):
            problems.append(f'linha {ln}: o titulo mora dentro do .al-drawer__header (regra 6)')
        # (c)
        lab = a.get('aria-labelledby')
        if not lab:
            problems.append(f'linha {ln}: sem aria-labelledby - o <dialog> nao se nomeia sozinho '
                            f'(regra 25)')
        elif lab not in ids or not has(ids[lab], 'al-drawer__title'):
            problems.append(f'linha {ln}: aria-labelledby="{lab}" nao aponta para um '
                            f'.al-drawer__title (regra 25)')
        elif titulos and ids[lab] is not titulos[0]:
            problems.append(f'linha {ln}: aria-labelledby aponta para o titulo de OUTRO Drawer (regra 25)')

        # (e) ordem cabecalho, miolo, acoes; acoes opcionais
        ordem = [next((c for c in PARTES if has(k, c)), None) for k in kids]
        esperado = [c for c in PARTES if c in ordem]
        if [o for o in ordem if o] != esperado or (ordem and ordem[0] != 'al-drawer__header'):
            problems.append(f'linha {ln}: filhos fora da ordem cabecalho, miolo, acoes (regra 9)')
        if any(o is None for o in ordem):
            problems.append(f'linha {ln}: filho direto sem classe do Drawer - sem divisoria nem '
                            f'peca solta entre as partes (regra 9)')
        if 'al-drawer__content' not in ordem:
            problems.append(f'linha {ln}: falta o .al-drawer__content')

        # (i) o X
        cab = cabecalhos[0] if cabecalhos else None
        x_btns = [d for d in walk(cab) if is_action(d)] if cab else []
        for x in x_btns:
            if not has(x, 'al-icon-btn'):
                problems.append(f'linha {x["line"]}: o unico botao do cabecalho e o X, um Icon Button (regra 26)')
                continue
            if not x['attrs'].get('aria-label', '').strip():
                problems.append(f'linha {x["line"]}: X sem aria-label - Icon Button sem nome e botao mudo (regra 26)')
            if x['attrs'].get('type') != 'button':
                problems.append(f'linha {x["line"]}: X sem type="button"')
            if 'data-al-drawer-close' not in x['attrs']:
                problems.append(f'linha {x["line"]}: X sem data-al-drawer-close - nao fecha')
            for s in walk(x):
                if s['tag'] == 'svg' and s['attrs'].get('aria-hidden') != 'true':
                    problems.append(f'linha {s["line"]}: svg do X sem aria-hidden="true"')
        if len(x_btns) > 1:
            problems.append(f'linha {ln}: mais de um botao no cabecalho (so o X)')
        tem_x = len(x_btns) == 1 and has(x_btns[0], 'al-icon-btn')

        # outros botoes sem rotulo visivel (fora o X)
        for d in walk(n):
            if d['tag'] == 'button' and not text_of(d) and d not in x_btns:
                problems.append(f'linha {d["line"]}: botao sem texto visivel fora o X (regra 26)')

        acoes_box = [k for k in kids if has(k, 'al-drawer__actions')]
        acoes = []
        if len(acoes_box) > 1:
            problems.append(f'linha {ln}: mais de um .al-drawer__actions')
        elif acoes_box:
            acoes = [d for d in walk(acoes_box[0]) if is_action(d)]
            # (f)
            if not 1 <= len(acoes) <= 2:
                problems.append(f'linha {ln}: {len(acoes)} acoes no rodape - sao uma ou duas (regra 20)')
            # (g)
            if len(acoes) == 2:
                primeira, ultima = acoes
                if has(primeira, 'al-btn--primary') or has(primeira, 'al-btn--danger'):
                    problems.append(f'linha {primeira["line"]}: a acao principal vem POR ULTIMO; a '
                                    f'primeira e a secundaria (regra 20)')
                if not has(ultima, 'al-btn--primary'):
                    problems.append(f'linha {ultima["line"]}: a ultima acao deveria ser Primary - '
                                    f'destrutiva abre um Modal, nao e o principal do Drawer (regras 20 e 22)')
            if len(acoes) == 1 and has(acoes[0], 'al-btn--danger'):
                problems.append(f'linha {acoes[0]["line"]}: Danger nao e o principal do Drawer (regra 22)')
            # (l) type
            for ac in acoes:
                if ac['tag'] == 'button' and ac['attrs'].get('type') not in ('button', 'submit', 'reset'):
                    problems.append(f'linha {ac["line"]}: <button> sem type - dentro de <form> o padrao '
                                    f'e submit')

        # (h) sempre uma saida visivel
        saida_rodape = any('data-al-drawer-close' in d['attrs'] for d in acoes) or \
            any(d['tag'] == 'form' and d['attrs'].get('method') == 'dialog' for d in walk(n))
        if not tem_x and not saida_rodape:
            problems.append(f'linha {ln}: nenhuma saida visivel - sem X e sem botao de rodape que '
                            f'feche (regra 14)')
        if not tem_x and not acoes:
            problems.append(f'linha {ln}: sem X e sem rodape - o Drawer fica sem saida visivel (regra 14)')

    if checked == 0:
        return None, ['nenhum .al-drawer no HTML']
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
    print('QA DE ACESSIBILIDADE DO DRAWER')
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
        print(f'  {mark} {r["theme"]:<5} {r["what"]:<36} x {r["bg"]:<20} '
              f'{r["ratio"]:5.2f} (piso {r["floor"]})  {nota}')

    print('\nCONTRATO DE MARCACAO')
    print(f'     fonte: {os.path.relpath(path, ROOT)}')
    if checked is None:
        for p in mk:
            print(f'     PENDENTE: {p}')
    else:
        print(f'     {checked} drawer(s) conferido(s), 13 regras (a-m)')
        for p in mk:
            print(f'     PROBLEMA: {p}')

    print('-' * 78)
    print(f'{len(rows)} medicoes  |  passam: {len(passa)}  |  excecoes: {len(excs)}  |  '
          f'reprovas: {len(fails) + len(invis)}')

    json.dump({
        'component': 'drawer',
        'criterion': 'WCAG 1.4.3 texto + 1.4.11 nao-textual + painel visivel + hover-raised distinto',
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
