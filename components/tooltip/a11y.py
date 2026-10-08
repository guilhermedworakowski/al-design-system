"""
QA de acessibilidade do Tooltip.

Como nos outros componentes, a validacao e por COMBINACAO RENDERIZADA - papel
x tema - contra o fundo EFETIVO, nao par de token solto.

O QUE O FUNDO EFETIVO MUDA AQUI

  Quase nada, e e isso que este portao confirma. O tooltip mora na top layer
  do navegador (popover), com fundo opaco `tooltip-bg` e opacidade 1 quando
  aberto: o texto e o icone so encostam no fundo do proprio tooltip, nunca na
  pagina. O icone herda a cor do texto (currentColor, regra 12). A caixa, por
  sua vez, pode cair sobre qualquer fundo de pagina - inclusive o
  `bg-surface-raised` de um Modal ou Drawer, que e onde ela aparece por cima
  de tudo.

TRES JULGAMENTOS

  1. Texto contra o fundo do tooltip: 4,5:1 do 1.4.3. Tem que passar.
  2. Icone contra o fundo do tooltip: 3:1 do 1.4.11. Tem que passar.
  3. Caixa contra cada fundo de pagina (canvas, surface, surface-raised): 3:1.
     Sem borda e sem seta (regra 14), a caixa so se separa da pagina pelo
     fundo invertido - se ela some, o texto flutua solto. Tem que passar.
  Sem excecao de contraste: nenhuma foi declarada nas etapas 1 a 4.

O CONTRATO DE MARCACAO E A OUTRA METADE DESTA ETAPA

  Regras de uso da etapa 4, medidas no HTML emitido:

    a) todo tooltip vivo e <div class="al-tooltip" id role="tooltip"
       popover="manual"> com id unico (regra 24; "manual" pelo Esc do Modal);
    b) data-placement, se existir, e top, bottom, left ou right (regra 13);
    c) dentro, nesta ordem e nada mais: o <svg class="al-icon al-icon--20
       al-tooltip__icon"> com aria-hidden="true" focusable="false" (regras 11
       e 12; o icone e sempre presente) e um <span class="al-tooltip__text">
       com texto;
    d) nada interativo dentro - sem link, botao, campo, tabindex ou
       contenteditable (regra 10);
    e) exatamente um gatilho aponta para ele, por aria-labelledby OU
       aria-describedby - nunca os dois no mesmo gatilho (regra 24);
    f) o gatilho e focavel (botao, link com href, campo, ou tabindex >= 0) e
       nunca `disabled` (regras 22 e 23);
    g) o tooltip e o elemento logo depois do gatilho (regra 25);
    h) gatilho com aria-labelledby nao leva aria-label (decisao (a), Icon
       Button); gatilho com aria-describedby ja tem nome proprio - texto ou
       aria-label (regra 24);
    i) as amostras congeladas do site (.al-tooltip sem popover) ficam sob
       `inert` e `aria-hidden` num ancestral: um tooltip aberto para sempre
       nao existe no componente e nao conta.

  O playground troca o palco por JavaScript (Uso x Lado): as variantes saem
  de `var TT_DEMOS` no proprio HTML. O portao le esse objeto e confere cada
  fragmento tambem - assim o caminho do aria-describedby, que nao esta no
  palco quando a pagina carrega, nao escapa.

ORDEM DE EXECUCAO - mesma dos outros: roda DEPOIS do HTML que ele mede.

Rodar: python3 a11y.py [caminho.html]
       sem argumento, mede site/index.html (piloto: sem pagina de QA separada)
"""
import json
import os
import re
import sys
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
FOUND = json.load(open(os.path.join(ROOT, 'tokens.json')))
TT = json.load(open(os.path.join(HERE, 'tokens.json')))

SEM = FOUND['color']['semantic']
ALIAS = TT['alias']
THEMES = ('light', 'dark')

TEXT_FLOOR = 4.5         # 1.4.3
NON_TEXT_FLOOR = 3.0     # 1.4.11

DEFAULT_HTML = os.path.join(ROOT, 'site', 'index.html')
OUT_JSON = os.path.join(HERE, 'a11y.json')

PAGINAS = ('bg-canvas', 'bg-surface', 'bg-surface-raised')
PLACEMENTS = ('top', 'bottom', 'left', 'right')
INTERATIVOS = ('a', 'button', 'input', 'select', 'textarea', 'details', 'summary')

VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link',
        'meta', 'source', 'track', 'wbr', 'path'}


def lin(c):
    c = c / 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def lum(h):
    h = h.lstrip('#')
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def cr(a, b):
    l1, l2 = sorted((lum(a), lum(b)), reverse=True)
    return (l1 + 0.05) / (l2 + 0.05)


def sem(name, theme):
    v = SEM[name]
    return v[THEMES.index(theme)] if isinstance(v, list) else v[theme]


def tt(role, theme):
    return sem(ALIAS[f'tooltip-{role}'], theme)


def row(theme, what, fg_name, fg, bg_name, bg, floor):
    ratio = round(cr(fg, bg), 2)
    return {'theme': theme, 'what': what, 'fg': fg_name, 'fgHex': fg,
            'bg': bg_name, 'bgHex': bg, 'ratio': ratio, 'floor': floor,
            'pass': ratio >= floor, 'invisible': fg.lower() == bg.lower(),
            'exception': None}


def contrast_rows():
    rows = []
    for t in THEMES:
        bg, fg = tt('bg', t), tt('text', t)
        rows.append(row(t, 'texto', ALIAS['tooltip-text'], fg, ALIAS['tooltip-bg'], bg, TEXT_FLOOR))
        rows.append(row(t, 'icone (currentColor)', ALIAS['tooltip-text'], fg, ALIAS['tooltip-bg'], bg,
                        NON_TEXT_FLOOR))
        for p in PAGINAS:
            rows.append(row(t, 'caixa sobre a pagina', ALIAS['tooltip-bg'], bg, p, sem(p, t),
                            NON_TEXT_FLOOR))
    return rows


# ─────────────────────────────────────────────── marcacao
class Tree(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = {'tag': '#root', 'attrs': {}, 'kids': [], 'text': '', 'line': 0}
        self.stack = [self.root]
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ('style', 'script', 'template'):
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
        if tag in ('style', 'script', 'template'):
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
    while p is not None:
        yield p
        p = p.get('parent')


def text_of(node):
    return (node['text'] + ''.join(text_of(k) for k in node['kids'])).strip()


def next_element(node):
    sibs = node['parent']['kids']
    i = sibs.index(node)
    return sibs[i + 1] if i + 1 < len(sibs) else None


def focusable(n):
    a = n['attrs']
    tab = a.get('tabindex')
    if tab is not None:
        try:
            return int(tab) >= 0
        except ValueError:
            return False
    if n['tag'] == 'a':
        return 'href' in a
    if n['tag'] == 'input':
        return a.get('type') != 'hidden'
    return n['tag'] in ('button', 'select', 'textarea', 'summary')


def refs(n, attr):
    return n['attrs'].get(attr, '').split()


def check_tooltip(tip, triggers, problems, where):
    ln = tip['line']
    a = tip['attrs']

    def bad(msg):
        problems.append(f'{where}linha {ln}: {msg}')

    # (a)
    if tip['tag'] != 'div' or a.get('role') != 'tooltip' or a.get('popover') != 'manual':
        bad('tooltip vivo = <div role="tooltip" popover="manual"> (regra 24)')
    # (b)
    if 'data-placement' in a and a['data-placement'] not in PLACEMENTS:
        bad(f'data-placement="{a["data-placement"]}" - so top, bottom, left ou right (regra 13)')
    # (c)
    kids = tip['kids']
    if len(kids) != 2:
        bad('dentro do tooltip: icone + texto, nada mais (regras 11 e 12)')
    else:
        ico, txt = kids
        ia = ico['attrs']
        if (ico['tag'] != 'svg' or not {'al-icon', 'al-icon--20', 'al-tooltip__icon'} <= set(classes(ico))
                or ia.get('aria-hidden') != 'true' or ia.get('focusable') != 'false'):
            bad('primeiro filho = <svg class="al-icon al-icon--20 al-tooltip__icon" '
                'aria-hidden="true" focusable="false"> (regras 11 e 12)')
        if txt['tag'] != 'span' or not has(txt, 'al-tooltip__text') or not text_of(txt):
            bad('segundo filho = <span class="al-tooltip__text"> com texto')
    # (d)
    for k in walk(tip):
        if (k['tag'] in INTERATIVOS or 'tabindex' in k['attrs']
                or 'contenteditable' in k['attrs']):
            bad(f'<{k["tag"]}> interativo dentro do tooltip (regra 10)')
            break
    # (e)
    if len(triggers) != 1:
        bad(f'{len(triggers)} gatilhos apontam para "{a.get("id")}" - tem que ser exatamente um (regra 24)')
        return
    trig = triggers[0]
    by_label = a['id'] in refs(trig, 'aria-labelledby')
    by_desc = a['id'] in refs(trig, 'aria-describedby')
    if by_label and by_desc:
        bad('o gatilho aponta pelos dois atributos - nome OU descricao (regra 24)')
    # (f)
    if not focusable(trig):
        bad(f'gatilho <{trig["tag"]}> nao e focavel (regra 22)')
    if 'disabled' in trig['attrs']:
        bad('gatilho disabled - para explicar bloqueio use aria-disabled (regra 23)')
    # (g)
    if next_element(trig) is not tip:
        bad('o tooltip nao vem logo depois do gatilho (regra 25)')
    # (h)
    if by_label and 'aria-label' in trig['attrs']:
        bad('gatilho com aria-labelledby e aria-label juntos - com tooltip, so labelledby (decisao (a))')
    if by_desc and not by_label and not (trig['attrs'].get('aria-label', '').strip() or text_of(trig)):
        bad('gatilho de descricao sem nome proprio - sem nome, o tooltip e o nome: aria-labelledby (regra 24)')


def markup_contract(html, where=''):
    """Confere um documento (ou fragmento). Devolve (vivos, congelados, problemas)."""
    t = Tree()
    t.feed(html)
    nodes = list(walk(t.root))
    problems = []

    ids = {}
    for n in nodes:
        i = n['attrs'].get('id')
        if i:
            ids.setdefault(i, []).append(n)

    live, frozen = 0, 0
    for n in nodes:
        if not has(n, 'al-tooltip'):
            continue
        if 'popover' not in n['attrs']:
            # (i) amostra congelada
            sob = list(ancestors(n))
            if not (any('inert' in x['attrs'] for x in sob)
                    and any(x['attrs'].get('aria-hidden') == 'true' for x in sob)):
                problems.append(f'{where}linha {n["line"]}: .al-tooltip sem popover fora de inert + '
                                f'aria-hidden - tooltip aberto para sempre nao existe')
            frozen += 1
            continue
        live += 1
        tid = n['attrs'].get('id', '')
        if not tid:
            problems.append(f'{where}linha {n["line"]}: tooltip vivo sem id (regra 24)')
            continue
        if len(ids.get(tid, [])) > 1:
            problems.append(f'{where}linha {n["line"]}: id "{tid}" repetido no documento')
        triggers = [x for x in nodes if tid in refs(x, 'aria-labelledby') + refs(x, 'aria-describedby')]
        check_tooltip(n, triggers, problems, where)
    return live, frozen, problems


def demos_of(html):
    m = re.search(r'var TT_DEMOS = (\{.*?\});\n', html)
    return json.loads(m.group(1)) if m else {}


def run():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_HTML
    rows = contrast_rows()
    fails = [r for r in rows if not r['pass']]

    print('=' * 74)
    print('QA DE ACESSIBILIDADE DO TOOLTIP')
    print('=' * 74)
    for r in rows:
        nota = 'INVISIVEL - igual ao fundo' if r['invisible'] else ('passa' if r['pass'] else 'REPROVA')
        print(f'  {"ok" if r["pass"] else "XX"} {r["theme"]:<5} {r["what"]:<22} sobre {r["bg"]:<18} '
              f'{r["fgHex"]} x {r["bgHex"]}  {r["ratio"]:5.2f}  {nota}')

    print('\nCONTRATO DE MARCACAO')
    print(f'     fonte: {os.path.relpath(path, ROOT)}')
    if not os.path.exists(path):
        live, frozen, mk, demos = None, 0, [f'{path} nao existe'], {}
    else:
        html = open(path, encoding='utf-8').read()
        live, frozen, mk = markup_contract(html)
        demos = demos_of(html)
        for key, d in demos.items():
            dl, _, dp = markup_contract(d['html'], where=f'playground {key}, ')
            live += dl
            mk += dp
        if live == 0:
            live, mk = None, ['nenhum .al-tooltip vivo no HTML - rode site.py antes']
    if live is None:
        for p in mk:
            print(f'     PENDENTE: {p}')
    else:
        print(f'     {live} tooltip(s) vivo(s) conferido(s), 9 regras (a-i) - '
              f'{len(demos)} variantes do playground incluidas; {frozen} amostra(s) congelada(s) sob inert')
        for p in mk:
            print(f'     PROBLEMA: {p}')

    print('-' * 74)
    print(f'{len(rows)} medicoes  |  passam: {len(rows) - len(fails)}  |  excecoes: 0  |  '
          f'reprovas: {len(fails)}')

    json.dump({
        'component': 'tooltip',
        'criterion': 'WCAG 1.4.3 texto + 1.4.11 nao-textual',
        'markupSource': os.path.relpath(path, ROOT),
        'markupChecked': live,
        'markupFrozen': frozen,
        'markupDemos': len(demos),
        'markupPending': live is None,
        'markupProblems': mk if live is not None else [],
        'rows': rows,
    }, open(OUT_JSON, 'w'), indent=2, ensure_ascii=False)
    print(f'{os.path.relpath(OUT_JSON, ROOT)} escrito')

    falhou = bool(fails)
    if live is None or mk:
        print('-' * 74)
        print(f'{len(mk)} PROBLEMA(S) DE MARCACAO - portao reprova')
        falhou = True
    return 1 if falhou else 0


if __name__ == '__main__':
    sys.exit(run())
