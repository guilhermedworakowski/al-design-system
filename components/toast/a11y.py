"""
QA de acessibilidade do Toast.

Como nos outros componentes, a validacao e por COMBINACAO RENDERIZADA - papel
x status x tema - contra o fundo EFETIVO, nao par de token solto.

O QUE O FUNDO EFETIVO MUDA AQUI

  O toast mora na top layer (a regiao e um popover), com fundo opaco
  `toast-bg` (bg-surface-raised): titulo, descricao, icone e o X so encostam
  no fundo do proprio toast. Quem encosta na pagina e a BORDA - e a pagina
  pode ser a tela, a superficie ou um Modal/Drawer aberto (bg-surface-raised),
  porque com um dialog aberto a regiao muda para dentro dele. Sobre o Modal,
  fundo do toast e fundo da pagina sao a mesma cor: so a borda separa.

  O X e o Icon Button Ghost sm. Sobre surface-raised ele usa os -raised
  (bg-hover-raised / bg-active-raised, licao do Modal 0.18.1): a tinta do
  icone e medida contra o fundo de repouso, de hover e de pressionado. O anel
  de foco e medido contra o fundo do toast - par que o portao do Icon Button,
  medido sobre a pagina, nao cobre.

QUATRO JULGAMENTOS

  1. Titulo e descricao contra o fundo do toast: 4,5:1 do 1.4.3.
  2. Icone de status contra o fundo do toast: 3:1 do 1.4.11. E o icone que
     carrega o status (regra 14), entao ele tem que passar.
  3. Borda de cada status contra cada fundo de pagina (canvas, surface,
     surface-raised): 3:1. Decorativa no status, mas e ela que separa a
     caixa da pagina.
  4. X: tinta contra repouso, hover e pressionado; anel de foco contra o
     fundo do toast. 3:1.
  Sem excecao de contraste: nenhuma foi declarada nas etapas 1 a 4.

O CONTRATO DE MARCACAO E A OUTRA METADE DESTA ETAPA

  Regras de uso da etapa 4, medidas no HTML emitido:

    a) uma unica .al-toast-region por documento: <section popover="manual">
       com aria-label, fora de <template> e fora de inert (regra 23);
    b) dentro dela, exatamente duas regioes vivas: um
       <div class="al-toast-region__live" role="status"> e um com
       role="alert" - VAZIAS no carregamento: a regiao existe antes da
       primeira mensagem (regras 22 e 23);
    c) todo toast vivo nasce de um <template> cujo unico filho e a
       <div class="al-toast"> (o toast.js clona dali);
    d) um, e so um, modificador de status: --success, --warning, --error ou
       --info. Sem Neutral (regra 26);
    e) primeiro filho = <svg class="al-icon al-icon--20 al-toast__icon">
       com role="img", aria-label com o nome do status (Sucesso, Aviso, Erro,
       Informação), sem aria-hidden, e o desenho do icone do status:
       circle-check, triangle-alert, circle-alert, info (regras 13 e 14);
    f) segundo filho = <div class="al-toast__text"> com um
       <p class="al-toast__title"> com texto e, opcional, um
       <p class="al-toast__description"> com texto - nada mais;
    g) terceiro e ultimo filho = o X: <button type="button"> Icon Button
       Ghost sm com a classe al-toast__close, aria-label="Fechar notificação"
       e o icone dentro aria-hidden (regra 24);
    h) nada interativo alem do X - sem link, campo, outro botao, tabindex ou
       contenteditable (regra 25);
    i) as amostras congeladas do site (.al-toast fora de <template>) ficam
       sob `inert` e `aria-hidden` num ancestral: um toast parado para sempre
       nao existe no componente. A marcacao delas cumpre (d) a (h) igual -
       e o que a documentacao mostra.

ORDEM DE EXECUCAO - mesma dos outros: roda DEPOIS do HTML que ele mede.

Rodar: python3 a11y.py [caminho.html]
       sem argumento, mede site/index.html (piloto: sem pagina de QA separada)
"""
import json
import os
import sys
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
FOUND = json.load(open(os.path.join(ROOT, 'tokens.json')))
TS = json.load(open(os.path.join(HERE, 'tokens.json')))
IB = json.load(open(os.path.join(ROOT, 'components', 'icon-button', 'tokens.json')))
ICON_DIR = os.path.join(ROOT, 'components', 'icon', 'icons')

SEM = FOUND['color']['semantic']
ALIAS = TS['alias']
THEMES = ('light', 'dark')

TEXT_FLOOR = 4.5         # 1.4.3
NON_TEXT_FLOOR = 3.0     # 1.4.11

DEFAULT_HTML = os.path.join(ROOT, 'site', 'index.html')
OUT_JSON = os.path.join(HERE, 'a11y.json')

PAGINAS = ('bg-canvas', 'bg-surface', 'bg-surface-raised')
STATUS = {
    'success': ('Sucesso', 'circle-check'),
    'warning': ('Aviso', 'triangle-alert'),
    'error':   ('Erro', 'circle-alert'),
    'info':    ('Informação', 'info'),
}
CLOSE_CLASSES = {'al-icon-btn', 'al-icon-btn--ghost', 'al-icon-btn--sm', 'al-toast__close'}
CLOSE_LABEL = 'Fechar notificação'
INTERATIVOS = ('a', 'button', 'input', 'select', 'textarea', 'details', 'summary')

VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link',
        'meta', 'source', 'track', 'wbr', 'path', 'circle', 'line', 'rect',
        'polyline', 'polygon', 'ellipse'}


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
        # 1. texto
        rows.append(row(t, 'titulo', ALIAS['toast-title'], ts('title', t), bg_name, bg, TEXT_FLOOR))
        rows.append(row(t, 'descricao', ALIAS['toast-description'], ts('description', t), bg_name, bg,
                        TEXT_FLOOR))
        # 2. icone de status
        for s in STATUS:
            rows.append(row(t, f'{s} / icone', ALIAS[f'toast-{s}-icon'], ts(f'{s}-icon', t),
                            bg_name, bg, NON_TEXT_FLOOR))
        # 3. borda contra a pagina
        for s in STATUS:
            for p in PAGINAS:
                rows.append(row(t, f'{s} / borda', ALIAS[f'toast-{s}-border'], ts(f'{s}-border', t),
                                p, sem(p, t), NON_TEXT_FLOOR))
        # 4. o X
        ink = sem(ink_name, t)
        for estado, fundo in (('repouso', bg_name), ('hover', 'bg-hover-raised'),
                              ('pressionado', 'bg-active-raised')):
            rows.append(row(t, f'X / {estado}', ink_name, ink, fundo, sem(fundo, t), NON_TEXT_FLOOR))
        rows.append(row(t, 'X / anel de foco', 'shadow-focus-default', sem('shadow-focus-default', t),
                        bg_name, bg, NON_TEXT_FLOOR))
    return rows


# ─────────────────────────────────────────────── marcacao
class Tree(HTMLParser):
    """Arvore simples. Diferente dos outros portoes, ENTRA no <template>:
    e la que mora a marcacao viva do toast."""

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
        if self.skip or tag in VOID:
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


def shape(svg_kids):
    """Assinatura do desenho: tag + atributos geometricos de cada filho."""
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
        problems.append(f'{where}linha {ln}: {msg}')

    # (d)
    mods = [s for s in STATUS if has(el, f'al-toast--{s}')]
    extra = [c for c in classes(el) if c.startswith('al-toast--') and c[10:] not in STATUS]
    if el['tag'] != 'div':
        bad('o toast e uma <div class="al-toast">')
    if len(mods) != 1 or extra:
        bad(f'status {mods + extra} - um, e so um, entre success, warning, error e info (regra 26)')
        return
    status = mods[0]
    label, icon = STATUS[status]

    kids = el['kids']
    if len(kids) != 3:
        bad(f'{len(kids)} filhos - icone, texto e X, nada mais (regras 13, 24 e 25)')
        return
    ico, txt, close = kids

    # (e)
    ia = ico['attrs']
    if ico['tag'] != 'svg' or not {'al-icon', 'al-icon--20', 'al-toast__icon'} <= set(classes(ico)):
        bad('primeiro filho = <svg class="al-icon al-icon--20 al-toast__icon"> (regra 13)')
    else:
        if ia.get('role') != 'img' or ia.get('aria-label') != label or 'aria-hidden' in ia:
            bad(f'icone de {status}: role="img" + aria-label="{label}", sem aria-hidden - '
                f'o icone carrega o status (regra 14)')
        if shape(ico['kids']) != SHAPES[status]:
            bad(f'icone de {status} nao e o {icon} (regra 13)')

    # (f)
    tk = txt['kids']
    if txt['tag'] != 'div' or not has(txt, 'al-toast__text'):
        bad('segundo filho = <div class="al-toast__text">')
    elif not tk or tk[0]['tag'] != 'p' or not has(tk[0], 'al-toast__title') or not text_of(tk[0]):
        bad('o texto abre com <p class="al-toast__title"> com texto - o titulo e obrigatorio')
    elif len(tk) > 2 or (len(tk) == 2 and (tk[1]['tag'] != 'p' or not has(tk[1], 'al-toast__description')
                                           or not text_of(tk[1]))):
        bad('depois do titulo, so um <p class="al-toast__description"> com texto (opcional)')

    # (g)
    ca = close['attrs']
    if (close['tag'] != 'button' or ca.get('type') != 'button'
            or not CLOSE_CLASSES <= set(classes(close))):
        bad('terceiro filho = <button type="button" class="al-icon-btn al-icon-btn--ghost '
            'al-icon-btn--sm al-toast__close"> (regra 24)')
    else:
        if ca.get('aria-label') != CLOSE_LABEL:
            bad(f'o X se chama "{CLOSE_LABEL}" (regra 24)')
        svgs = [k for k in close['kids'] if k['tag'] == 'svg']
        if (len(close['kids']) != 1 or len(svgs) != 1 or svgs[0]['attrs'].get('aria-hidden') != 'true'
                or svgs[0]['attrs'].get('focusable') != 'false'):
            bad('dentro do X, so o icone, com aria-hidden="true" focusable="false"')

    # (h)
    for k in walk(el):
        if k is close:
            continue
        if any(a is close for a in ancestors(k)):
            continue
        if (k['tag'] in INTERATIVOS or 'tabindex' in k['attrs']
                or 'contenteditable' in k['attrs']):
            bad(f'<{k["tag"]}> interativo dentro do toast - so o X (regra 25)')
            break
    return status


def check_region(regions, problems):
    if len(regions) != 1:
        problems.append(f'{len(regions)} .al-toast-region no documento - tem que ser exatamente uma (regra 23)')
        if not regions:
            return
    for r in regions:
        a = r['attrs']

        def bad(msg):
            problems.append(f'linha {r["line"]}: {msg}')

        # (a)
        if r['tag'] != 'section' or a.get('popover') != 'manual' or not a.get('aria-label', '').strip():
            bad('regiao = <section class="al-toast-region" aria-label popover="manual"> (regra 23)')
        sob = list(ancestors(r))
        if any(x['tag'] == 'template' for x in sob):
            bad('a regiao esta dentro de um <template> - ela existe desde o carregamento (regra 23)')
        if any('inert' in x['attrs'] or x['attrs'].get('aria-hidden') == 'true' for x in [r] + sob):
            bad('a regiao esta sob inert ou aria-hidden - o anuncio nao chega (regra 22)')
        # (b)
        roles = [k['attrs'].get('role') for k in r['kids']]
        lives = [k for k in r['kids'] if k['tag'] == 'div' and has(k, 'al-toast-region__live')]
        if len(r['kids']) != 2 or len(lives) != 2 or sorted(roles) != ['alert', 'status']:
            bad('dentro da regiao: um __live role="status" e um role="alert", nada mais (regra 22)')
        for k in lives:
            if k['kids'] or k['text'].strip():
                bad(f'a regiao viva role="{k["attrs"].get("role")}" nao nasce vazia - '
                    f'mensagem que nasce junto com a regiao nao e anunciada (regra 23)')


def markup_contract(html):
    """Devolve (templates, congelados, por_status, problemas)."""
    t = Tree()
    t.feed(html)
    nodes = list(walk(t.root))
    problems = []

    check_region([n for n in nodes if has(n, 'al-toast-region')], problems)

    live, frozen, by_status = 0, 0, {s: 0 for s in STATUS}
    for n in nodes:
        if not has(n, 'al-toast'):
            continue
        sob = list(ancestors(n))
        tpl = next((x for x in sob if x['tag'] == 'template'), None)
        if tpl is None:
            # (i)
            if not (any('inert' in x['attrs'] for x in sob)
                    and any(x['attrs'].get('aria-hidden') == 'true' for x in sob)):
                problems.append(f'linha {n["line"]}: .al-toast fora de <template> e fora de inert + '
                                f'aria-hidden - toast parado para sempre nao existe')
            frozen += 1
            check_toast(n, problems, 'amostra, ')
            continue
        # (c)
        live += 1
        if tpl['kids'] != [n]:
            problems.append(f'linha {tpl["line"]}: <template id="{tpl["attrs"].get("id", "")}"> tem que '
                            f'ter a .al-toast como unico filho - o toast.js clona o primeiro')
        s = check_toast(n, problems, '')
        if s:
            by_status[s] += 1
    return live, frozen, by_status, problems


def run():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_HTML
    rows = contrast_rows()
    fails = [r for r in rows if not r['pass']]

    print('=' * 74)
    print('QA DE ACESSIBILIDADE DO TOAST')
    print('=' * 74)
    for r in fails:
        nota = 'INVISIVEL - igual ao fundo' if r['invisible'] else 'REPROVA'
        print(f'  XX {r["theme"]:<5} {r["what"]:<22} sobre {r["bg"]:<18} '
              f'{r["fgHex"]} x {r["bgHex"]}  {r["ratio"]:5.2f}  {nota}')

    print('\nCONTRATO DE MARCACAO')
    print(f'     fonte: {os.path.relpath(path, ROOT)}')
    by_status = {}
    if not os.path.exists(path):
        live, frozen, mk = None, 0, [f'{path} nao existe']
    else:
        live, frozen, by_status, mk = markup_contract(open(path, encoding='utf-8').read())
        if live == 0:
            live, mk = None, ['nenhum <template> com .al-toast no HTML - rode site.py antes']
    if live is None:
        for p in mk:
            print(f'     PENDENTE: {p}')
    else:
        resumo = ', '.join(f'{s} {n}' for s, n in by_status.items())
        print(f'     1 regiao + {live} template(s) conferido(s), 9 regras (a-i) - {resumo}; '
              f'{frozen} amostra(s) congelada(s) sob inert')
        for p in mk:
            print(f'     PROBLEMA: {p}')

    print('-' * 74)
    print(f'{len(rows)} medicoes  |  passam: {len(rows) - len(fails)}  |  excecoes: 0  |  '
          f'reprovas: {len(fails)}')

    json.dump({
        'component': 'toast',
        'criterion': 'WCAG 1.4.3 texto + 1.4.11 nao-textual',
        'markupSource': os.path.relpath(path, ROOT),
        'markupChecked': live,
        'markupByStatus': by_status,
        'markupFrozen': frozen,
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
