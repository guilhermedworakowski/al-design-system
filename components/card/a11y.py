"""
QA de acessibilidade do Card.

Como nos outros componentes, a validacao e por COMBINACAO RENDERIZADA - tipo x
estado x tema x pagina onde o card e colocado - contra o fundo EFETIVO, nao
par de token solto.

O QUE O FUNDO EFETIVO MUDA AQUI

  O texto mede contra o fundo do card (`bg-surface-raised`), o mesmo nos tres
  tipos. Borda, anel e o proprio card medem contra a PAGINA, e a pagina muda
  por tipo, porque a regra de uso manda:
    - Filled so sobre `bg-surface` (regra 2) - sobre a tela ele some;
    - Border e Elevated sobre a tela ou sobre superficie (regras 3 e 4).
  O anel de foco e desenhado FORA do card, sobre a pagina, com o respiro em
  `bg-canvas` - por isso ele mede contra as duas paginas.

TRES JULGAMENTOS

  1. Texto: piso 4,5:1 do 1.4.3. Tem que passar - sem excecao.
  2. Borda, anel e limite do card: piso 3:1 do 1.4.11. A borda em repouso e o
     limite pelo fundo ficam abaixo, e isso sao as excecoes declaradas
     `borda-abaixo-de-3-1` e `card-nao-se-separa-pelo-fundo` (decisoes A e C).
     Hover e foco tem que passar.
  3. Card INVISIVEL - nenhuma pista separa o card da pagina: fundo igual,
     sem borda e sem sombra. A excecao cobre card discreto, nao card que nao
     existe. Isso reprova. O Elevated sobre a tela clara tem fundo igual mas
     tem sombra, entao nao e invisivel; o Filled sobre a tela seria, e por
     isso a combinacao nem entra - a regra 2 proibe.

O CONTRATO DE MARCACAO E A OUTRA METADE DESTA ETAPA

  Regras de uso da etapa 4, medidas no HTML emitido:

    a) `.al-card__title` e um titulo de verdade, h1 a h6 (regra 11);
    b) card clicavel tem UM `.al-card__link`, e ele mora dentro do titulo
       (regras 13 e 16);
    c) `.al-card__link` e `<a href>` ou `<button type="button">`, com nome
       (regra 16);
    d) nada clicavel alem do link dentro do card clicavel - link, botao,
       campo, tabindex (regra 15);
    e) o card em si nao e clicavel: nem <a>/<button>, nem onclick, nem
       tabindex, nem role de acionavel (regra 16);
    f) `.al-card__link` fora de card clicavel nao existe - sem o modificador
       o link estica sem hover nem anel (regra 13);
    g) `<li class="al-card">` so dentro de <ul>/<ol> (regra 22);
    h) nada de card dentro de card (regra 6);
    i) sem disabled: nem `disabled`, nem `aria-disabled` no card (regra 19);
    j) um tipo e um padding por card - `--border` com `--elevated`, ou
       `--spaced` com `--tight`, e marcacao contraditoria.

ORDEM DE EXECUCAO - mesma dos outros: roda DEPOIS do HTML que ele mede.

Rodar: python3 a11y.py [caminho.html]
       sem argumento, mede site/index.html
"""
import json
import os
import sys
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
FOUND = json.load(open(os.path.join(ROOT, 'tokens.json')))
CARD = json.load(open(os.path.join(HERE, 'tokens.json')))

SEM = FOUND['color']['semantic']
ALIAS = CARD['alias']
THEMES = ('light', 'dark')

TEXT_FLOOR = 4.5          # 1.4.3
NON_TEXT_FLOOR = 3.0      # 1.4.11
EXC_BORDA = 'borda-abaixo-de-3-1'
EXC_FUNDO = 'card-nao-se-separa-pelo-fundo'

DEFAULT_HTML = os.path.join(ROOT, 'site', 'index.html')
OUT_JSON = os.path.join(HERE, 'a11y.json')

# paginas onde cada tipo pode ser colocado (regras 2, 3 e 4)
PAGINAS = {
    'filled':   ('bg-surface',),
    'border':   ('bg-canvas', 'bg-surface'),
    'elevated': ('bg-canvas', 'bg-surface'),
}

VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link',
        'meta', 'source', 'track', 'wbr'}
HEADINGS = {'h1', 'h2', 'h3', 'h4', 'h5', 'h6'}
ACTIONABLE_ROLES = {'button', 'link', 'checkbox', 'radio', 'switch', 'menuitem', 'tab', 'option'}


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
    """tokens.json guarda o semantico como [claro, escuro]."""
    v = SEM[name]
    return v[THEMES.index(theme)] if isinstance(v, list) else v[theme]


def card(role, theme):
    """Cor de um papel do Card, seguindo o alias ate o semantico."""
    return sem(ALIAS[f'card-{role}'], theme)


# ─────────────────────────────────────────────── contraste
def row(theme, tipo, estado, what, fg_name, fg, bg_name, bg, floor, exc=None, invisible=False):
    ratio = round(cr(fg, bg), 2)
    ok = ratio >= floor
    return {
        'theme': theme, 'type': tipo, 'state': estado, 'what': what,
        'fg': fg_name, 'fgHex': fg, 'bg': bg_name, 'bgHex': bg,
        'ratio': ratio, 'floor': floor, 'pass': ok,
        'invisible': invisible,
        'exception': None if ok or invisible else exc,
    }


def contrast_rows():
    rows = []
    for theme in THEMES:
        fundo = card('bg', theme)
        anel = sem('shadow-focus-default', theme)

        # 1. texto - o fundo do card e o mesmo nos tres tipos e nos estados
        for papel, what in (('title', 'titulo'), ('description', 'descricao')):
            rows.append(row(theme, 'todos', 'todos', what,
                            ALIAS[f'card-{papel}'], card(papel, theme),
                            'card-bg', fundo, TEXT_FLOOR))

        for tipo, paginas in PAGINAS.items():
            for pagina in paginas:
                pg = sem(pagina, theme)

                # 2. limite do card em repouso
                if tipo == 'border':
                    borda = card('border', theme)
                    pior = min((cr(borda, fundo), 'card-bg', fundo),
                               (cr(borda, pg), pagina, pg))
                    rows.append(row(theme, tipo, 'repouso', 'borda',
                                    ALIAS['card-border'], borda, pior[1], pior[2],
                                    NON_TEXT_FLOOR, EXC_BORDA,
                                    invisible=borda.lower() in (fundo.lower(), pg.lower())))
                else:
                    # sem borda: o limite e o fundo do card contra a pagina.
                    # Elevated tem sombra, entao fundo igual nao o apaga.
                    tem_sombra = tipo == 'elevated'
                    rows.append(row(theme, tipo, 'repouso', 'limite-pelo-fundo',
                                    'card-bg', fundo, pagina, pg,
                                    NON_TEXT_FLOOR, EXC_FUNDO,
                                    invisible=(fundo.lower() == pg.lower() and not tem_sombra)))

                # 3. hover e foco - so o Border muda a cor da borda
                if tipo == 'border':
                    for estado, papel in (('hover', 'border-hover'), ('foco', 'border-focus')):
                        c = card(papel, theme)
                        pior = min((cr(c, fundo), 'card-bg', fundo), (cr(c, pg), pagina, pg))
                        rows.append(row(theme, tipo, estado, 'borda',
                                        ALIAS[f'card-{papel}'], c, pior[1], pior[2],
                                        NON_TEXT_FLOOR))

                # 4. anel - fora do card, sobre a pagina; o respiro e bg-canvas
                respiro = sem('bg-canvas', theme)
                pior = min((cr(anel, pg), pagina, pg), (cr(anel, respiro), 'bg-canvas (respiro)', respiro))
                rows.append(row(theme, tipo, 'foco', 'anel',
                                'shadow-focus-default', anel, pior[1], pior[2],
                                NON_TEXT_FLOOR))
    return rows


# ─────────────────────────────────────────────── marcacao
class Tree(HTMLParser):
    """Arvore minima: so o necessario para pai, ancestrais e descendentes."""

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


def interactive(node):
    a, tag = node['attrs'], node['tag']
    if tag == 'a' and 'href' in a:
        return True
    if tag in ('button', 'input', 'select', 'textarea', 'summary'):
        return True
    if 'tabindex' in a and a['tabindex'] != '-1':
        return True
    return a.get('role') in ACTIONABLE_ROLES


def markup_contract(path):
    if not os.path.exists(path):
        return None, [f'{path} nao existe']
    t = Tree()
    t.feed(open(path, encoding='utf-8').read())

    checked, problems = 0, []
    for n in walk(t.root):
        a, tag, ln = n['attrs'], n['tag'], n['line']

        # (a) titulo e titulo
        if has(n, 'al-card__title') and tag not in HEADINGS:
            problems.append(f'linha {ln}: .al-card__title em <{tag}> - o titulo do card e '
                            f'h1-h6 conforme a pagina, nunca paragrafo (regra 11)')

        # (f) link sem card clicavel
        if has(n, 'al-card__link'):
            dono = next((p for p in ancestors(n) if has(p, 'al-card')), None)
            if dono is None or not has(dono, 'al-card--clickable'):
                problems.append(f'linha {ln}: .al-card__link fora de .al-card--clickable - '
                                f'o link estica sobre o card sem hover nem anel (regra 13)')

        if not has(n, 'al-card'):
            continue
        checked += 1
        cl = classes(n)

        # (e) o card em si nao e acionavel
        if tag in ('a', 'button'):
            problems.append(f'linha {ln}: .al-card em <{tag}> - o link vai no titulo e '
                            f'estica; nunca embrulha o card (regra 16)')
        if 'tabindex' in a:
            problems.append(f'linha {ln}: tabindex no card - quem recebe o Tab e o link '
                            f'do titulo (regra 16)')
        if any(k.startswith('on') for k in a):
            problems.append(f'linha {ln}: manipulador de evento no card - use o link do '
                            f'titulo (regra 16)')
        if a.get('role') in ACTIONABLE_ROLES:
            problems.append(f'linha {ln}: role="{a["role"]}" no card - o card nao e '
                            f'acionavel, o link do titulo e (regra 16)')

        # (g) item de lista
        if tag == 'li' and n['parent']['tag'] not in ('ul', 'ol'):
            problems.append(f'linha {ln}: <li class="al-card"> fora de <ul>/<ol> (regra 22)')

        # (h) card dentro de card
        if any(has(p, 'al-card') for p in ancestors(n)):
            problems.append(f'linha {ln}: card dentro de card - subdivida com Divider ou '
                            f'titulo (regra 6)')

        # (i) sem disabled
        if 'disabled' in a or 'aria-disabled' in a:
            problems.append(f'linha {ln}: card desabilitado - ele some ou explica no '
                            f'conteudo (regra 19)')

        # (j) modificadores coerentes
        if 'al-card--border' in cl and 'al-card--elevated' in cl:
            problems.append(f'linha {ln}: --border e --elevated no mesmo card - um tipo so')
        if 'al-card--spaced' in cl and 'al-card--tight' in cl:
            problems.append(f'linha {ln}: --spaced e --tight no mesmo card - um padding so')

        if 'al-card--clickable' not in cl:
            continue

        # (b) um link, dentro do titulo
        desc = list(walk(n))
        links = [d for d in desc if has(d, 'al-card__link')]
        if len(links) != 1:
            problems.append(f'linha {ln}: card clicavel com {len(links)} .al-card__link - '
                            f'tem que ser exatamente um (regra 13)')
        for lk in links:
            if not any(has(p, 'al-card__title') for p in ancestors(lk)):
                problems.append(f'linha {lk["line"]}: .al-card__link fora do titulo - o '
                                f'nome anunciado tem que ser o titulo (regra 16)')
            # (c) elemento e nome
            la = lk['attrs']
            if lk['tag'] == 'a' and 'href' not in la:
                problems.append(f'linha {lk["line"]}: <a class="al-card__link"> sem href - '
                                f'nao e link, nao recebe Tab (regra 16)')
            elif lk['tag'] == 'button' and la.get('type') != 'button':
                problems.append(f'linha {lk["line"]}: <button class="al-card__link"> sem '
                                f'type="button" - dentro de formulario ele enviaria (regra 16)')
            elif lk['tag'] not in ('a', 'button'):
                problems.append(f'linha {lk["line"]}: .al-card__link em <{lk["tag"]}> - '
                                f'use <a href> ou <button type="button"> (regra 16)')
            if not text_of(lk) and not la.get('aria-label'):
                problems.append(f'linha {lk["line"]}: .al-card__link sem nome (regra 16)')

        # (d) nada clicavel alem do link
        for d in desc:
            if d in links or any(d is x for lk in links for x in walk(lk)):
                continue
            if interactive(d):
                problems.append(f'linha {d["line"]}: <{d["tag"]}> interativo dentro de card '
                                f'clicavel - alvo sobreposto ao link (regra 15)')

    if checked == 0:
        return None, ['nenhum .al-card no HTML - o componente entra no site na '
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
    print('QA DE ACESSIBILIDADE DO CARD')
    print('=' * 78)
    print('\nCOMBINACOES RENDERIZADAS (tema x tipo x estado x pagina)')
    for r in rows:
        if r['invisible']:
            mark, nota = 'XX', 'INVISIVEL - nada separa o card da pagina'
        elif r['pass']:
            mark, nota = 'ok', 'passa'
        elif r['exception']:
            mark, nota = '~~', f'excecao "{r["exception"]}"'
        else:
            mark, nota = 'XX', 'REPROVA'
        print(f'  {mark} {r["theme"]:<5} {r["type"]:<8} {r["state"]:<7} {r["what"]:<17} '
              f'x {r["bg"]:<19} {r["ratio"]:5.2f} (piso {r["floor"]})  {nota}')

    print('\nCONTRATO DE MARCACAO')
    print(f'     fonte: {os.path.relpath(path, ROOT)}')
    if checked is None:
        for p in mk:
            print(f'     PENDENTE: {p}')
    else:
        print(f'     {checked} card(s) conferido(s), 10 regras (a-j)')
        for p in mk:
            print(f'     PROBLEMA: {p}')

    print('-' * 78)
    print(f'{len(rows)} medicoes  |  passam: {len(passa)}  |  excecoes: {len(excs)}  |  '
          f'reprovas: {len(fails) + len(invis)}')

    json.dump({
        'component': 'card',
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
            print(f'   {r["theme"]} {r["type"]} {r["state"]} {r["what"]} x {r["bg"]}: {r["ratio"]}:1')
        falhou = True
    if checked is not None and mk:
        print('-' * 78)
        print(f'{len(mk)} PROBLEMA(S) DE MARCACAO - portao reprova')
        falhou = True
    return 1 if falhou else 0


if __name__ == '__main__':
    sys.exit(run())
