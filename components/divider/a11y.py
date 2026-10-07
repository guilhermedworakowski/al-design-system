"""
QA de acessibilidade do Divider.

Como nos outros componentes, a validacao e por COMBINACAO RENDERIZADA - a linha
contra o fundo EFETIVO onde ela e colocada, nao par de token solto.

O QUE O FUNDO EFETIVO MUDA AQUI

  A etapa 3 mediu a linha contra a tela (`bg-canvas`) e a faixa de secao
  (`bg-surface`). Faltava a terceira superficie do sistema: card e modal
  (`bg-surface-raised`) - justamente onde o divisor mais aparece (rodape de
  card, grupos de menu). Ela entra aqui, e vale cada uma.

DOIS JULGAMENTOS, NAO UM

  1. Piso de 3:1 do 1.4.11. A linha fica abaixo em todo fundo, e isso e a
     excecao declarada `linha-abaixo-de-3-1`, sustentada pela regra 8 (a linha
     nunca e a unica pista do agrupamento). Nao reprova.
  2. Linha INVISIVEL - cor da linha identica a do fundo. A excecao cobre uma
     linha discreta; nao cobre uma linha que nao existe na tela. Isso reprova.

O CONTRATO DE MARCACAO E A OUTRA METADE DESTA ETAPA

  Regras de uso da etapa 4, medidas no HTML emitido:

    a) `.al-divider` e `<hr>` ou `<li role="separator">` - nada de <div>
       pintado (regras 12 e 15);
    b) `<hr>` nunca e filho direto de <ul>/<ol> - la so cabe <li> (regra 15);
    c) o separador em lista e vazio - sem texto no divisor (regra 11);
    d) vertical anunciada leva aria-orientation="vertical"; horizontal nao
       (regra 14);
    e) nunca focavel nem clicavel: sem tabindex, sem onclick, sem role que nao
       seja `separator` (regra 16);
    f) decorativo e aria-hidden="true" e nada mais (regra 13);
    g) nada de divisor no comeco ou no fim do conteiner, nem dois seguidos
       (regra 4).

ORDEM DE EXECUCAO - mesma dos outros: roda DEPOIS do HTML que ele mede.

Rodar: python3 a11y.py [caminho.html]
       sem argumento, mede site/index.html
"""
import json
import os
import re
import sys
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
FOUND = json.load(open(os.path.join(ROOT, 'tokens.json')))
DIVIDER = json.load(open(os.path.join(HERE, 'tokens.json')))

SEM = FOUND['color']['semantic']
RES = DIVIDER['resolved']
THEMES = ('light', 'dark')

NON_TEXT_FLOOR = 3.0      # 1.4.11
EXC = 'linha-abaixo-de-3-1'

DEFAULT_HTML = os.path.join(ROOT, 'site', 'index.html')
OUT_JSON = os.path.join(HERE, 'a11y.json')

PAGINAS = ('bg-canvas', 'bg-surface', 'bg-surface-raised')

VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link',
        'meta', 'source', 'track', 'wbr'}


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


# ─────────────────────────────────────────────── contraste
def contrast_rows():
    rows = []
    for theme in THEMES:
        fg = RES['divider-color'][theme]
        for page in PAGINAS:
            bg = sem(page, theme)
            ratio = round(cr(fg, bg), 2)
            invisivel = fg.lower() == bg.lower()
            rows.append({
                'theme': theme, 'bg': page, 'fg': fg, 'bgHex': bg,
                'ratio': ratio, 'floor': NON_TEXT_FLOOR,
                'pass': ratio >= NON_TEXT_FLOOR,
                'invisible': invisivel,
                'exception': None if ratio >= NON_TEXT_FLOOR or invisivel else EXC,
            })
    return rows


# ─────────────────────────────────────────────── marcacao
class Tree(HTMLParser):
    """Arvore minima: so o necessario para pai, irmaos e filhos."""

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


def is_divider(node):
    return 'al-divider' in node['attrs'].get('class', '').split()


def markup_contract(path):
    if not os.path.exists(path):
        return None, [f'{path} nao existe']
    t = Tree()
    t.feed(open(path, encoding='utf-8').read())

    checked, problems = 0, []
    for n in walk(t.root):
        if not is_divider(n):
            continue
        checked += 1
        a, tag, ln = n['attrs'], n['tag'], n['line']
        classes = a.get('class', '').split()
        hidden = a.get('aria-hidden')
        parent = n['parent']

        # (a) elemento certo
        if tag not in ('hr', 'li'):
            problems.append(f'linha {ln}: .al-divider em <{tag}> - use <hr> (ou '
                            f'<li role="separator"> em lista) (regras 12 e 15)')
        if tag == 'li' and a.get('role') != 'separator' and hidden != 'true':
            problems.append(f'linha {ln}: <li class="al-divider"> sem role="separator" '
                            f'- o leitor de tela anunciaria um item vazio (regra 15)')

        # (b) <hr> solto em lista
        if tag == 'hr' and parent['tag'] in ('ul', 'ol'):
            problems.append(f'linha {ln}: <hr> filho direto de <{parent["tag"]}> - '
                            f'HTML invalido, use <li role="separator"> (regra 15)')

        # (c) sem texto
        if tag == 'li' and (n['text'].strip() or n['kids']):
            problems.append(f'linha {ln}: separador com conteudo - o divisor nao '
                            f'leva texto; nomeie o grupo com um titulo (regra 11)')

        # (d) orientacao
        vertical = 'al-divider--vertical' in classes
        orient = a.get('aria-orientation')
        if vertical and hidden != 'true' and orient != 'vertical':
            problems.append(f'linha {ln}: vertical anunciada sem aria-orientation='
                            f'"vertical" - o separador e horizontal por padrao (regra 14)')
        if not vertical and orient == 'vertical':
            problems.append(f'linha {ln}: aria-orientation="vertical" num divisor '
                            f'horizontal - anuncio diverge da tela (regra 14)')

        # (e) nunca focavel nem clicavel
        if 'tabindex' in a:
            problems.append(f'linha {ln}: tabindex no divisor - separador focavel e '
                            f'Window Splitter, outro componente (regra 16)')
        if any(k.startswith('on') for k in a):
            problems.append(f'linha {ln}: manipulador de evento no divisor - ele '
                            f'nunca e clicavel (regra 16)')
        role = a.get('role')
        if role and role != 'separator':
            problems.append(f'linha {ln}: role="{role}" - o unico papel do divisor e '
                            f'separator; decorativo e aria-hidden (regras 13 e 16)')

        # (f) decorativo
        if hidden is not None and hidden != 'true':
            problems.append(f'linha {ln}: aria-hidden="{hidden}" - decorativo e '
                            f'"true"; anunciado nao leva o atributo (regra 13)')

        # (g) posicao no conteiner
        irmaos = [k for k in parent['kids']]
        i = irmaos.index(n)
        if i == 0 or i == len(irmaos) - 1:
            problems.append(f'linha {ln}: divisor no {"comeco" if i == 0 else "fim"} '
                            f'do <{parent["tag"]}> - nao separa nada (regra 4)')
        if i > 0 and is_divider(irmaos[i - 1]) and not (n['text'] or '').strip():
            problems.append(f'linha {ln}: dois divisores seguidos - linha dupla (regra 4)')

    if checked == 0:
        return None, ['nenhum .al-divider no HTML - o componente entra no site na '
                      'etapa 7; ate la este portao fica PENDENTE']
    return checked, problems


def run():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_HTML
    rows = contrast_rows()
    invis = [r for r in rows if r['invisible']]
    excs = [r for r in rows if r['exception']]
    passa = [r for r in rows if r['pass']]

    checked, mk = markup_contract(path)

    print('=' * 74)
    print('QA DE ACESSIBILIDADE DO DIVIDER')
    print('=' * 74)
    print('\nLINHA contra cada superficie onde ela e colocada')
    for r in rows:
        if r['invisible']:
            mark, nota = 'XX', 'INVISIVEL - linha e fundo tem a mesma cor'
        elif r['pass']:
            mark, nota = 'ok', 'passa'
        else:
            mark, nota = '~~', f'excecao "{EXC}"'
        print(f'  {mark} {r["theme"]:<5} sobre {r["bg"]:<18} {r["fg"]} x {r["bgHex"]}  '
              f'{r["ratio"]:5.2f}  {nota}')

    print('\nANEL DE FOCO')
    print('     n/a - o divisor nunca recebe foco (regra 16)')

    print('\nCONTRATO DE MARCACAO')
    print(f'     fonte: {os.path.relpath(path, ROOT)}')
    if checked is None:
        for p in mk:
            print(f'     PENDENTE: {p}')
    else:
        print(f'     {checked} divisor(es) conferido(s), 7 regras (a-g)')
        for p in mk:
            print(f'     PROBLEMA: {p}')

    print('-' * 74)
    print(f'{len(rows)} medicoes  |  passam: {len(passa)}  |  excecoes: {len(excs)}  |  '
          f'reprovas: {len(invis)}')

    json.dump({
        'component': 'divider',
        'criterion': 'WCAG 1.4.11 nao-textual + linha visivel',
        'floor': NON_TEXT_FLOOR,
        'markupSource': os.path.relpath(path, ROOT),
        'markupChecked': checked,
        'markupPending': checked is None,
        'markupProblems': mk if checked is not None else [],
        'rows': rows,
    }, open(OUT_JSON, 'w'), indent=2, ensure_ascii=False)
    print(f'{os.path.relpath(OUT_JSON, ROOT)} escrito')

    falhou = False
    if invis:
        print('-' * 74)
        print(f'{len(invis)} SUPERFICIE(S) ONDE A LINHA NAO EXISTE NA TELA:')
        for r in invis:
            print(f'   {r["theme"]} sobre {r["bg"]}: {r["fg"]} = {r["bgHex"]}')
        falhou = True
    if checked is not None and mk:
        print('-' * 74)
        print(f'{len(mk)} PROBLEMA(S) DE MARCACAO - portao reprova')
        falhou = True
    return 1 if falhou else 0


if __name__ == '__main__':
    sys.exit(run())
