"""
Portao do CSS do Sidebar.

Mesma ideia do portao de alias em tokens.py, uma camada acima: o componente nao
pode conter valor literal. Toda cor e comprimento tem que entrar por var(--al-*).
Se um hex ou um px aparecer no sidebar.css, o build para.

Sem pendencia de motion: o modo modal usa motion.duration.panel e as curvas da
Foundation. Qualquer duracao literal que aparecer aqui e erro.

UMA EXCECAO NOMEADA - `ponto-de-quebra`: @media nao le custom property e a
Foundation nao tem escala de ponto de quebra. O valor 1024px e aceito SO
dentro de uma linha @media e SO esse valor (decisao 1 da etapa 4). Qualquer
outro comprimento, ou o 1024 fora de @media, reprova.

Herdado do Select: tambem reprova token declarado e nunca consumido (orfao) e
custom property do Sidebar que nao existe na camada de tokens (inventada).

Rodar: python3 check.py
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(HERE, 'sidebar.css')

HEX = re.compile(r'#[0-9a-fA-F]{3,8}\b')
FUNC_COLOR = re.compile(r'\b(rgba?|hsla?|oklch|lab|color)\s*\(')
# comprimento literal fora de var(): 12px, 1.5rem, 2em...
LENGTH = re.compile(r'(?<![\w-])\d*\.?\d+(px|rem|em|ch|vh|vw)\b')
DURATION = re.compile(r'(?<![\w-])\d*\.?\d+m?s\b')
# peso de fonte cravado: font-weight: 500
WEIGHT = re.compile(r'font-weight\s*:\s*\d+')

# O que este portao NAO alcanca: marcacao so existe na saida renderizada.
# O a11y.py da etapa 6 cobra estas regras no HTML que o site emite.
CONTRATOS_FORA_DO_CSS = [
    '<aside> com nome; grupos e Ajuda dentro de <nav aria-label>; perfil fora do nav (regra 26)',
    'cada grupo <ul> nomeada pelo rotulo via aria-labelledby (regra 27)',
    'itens sao <a> com aria-current="page" no atual, no maximo um, nunca role="tab" (regras 12 e 28)',
    'Avatar decorativo (aria-hidden, alt="") e Icon Button do perfil com nome (regras 18 e 19)',
    'nenhum rotulo repetido (regra 16); uma Sidebar por tela (regra 4)',
    'modo modal: mover para <dialog>, foco no atual, fecha no destino e no scrim, sem X: sidebar.js (regra 25)',
]

BREAKPOINT = '1024px'


def strip_comments(text):
    return re.sub(r'/\*.*?\*/', '', text, flags=re.S)


def run():
    if not os.path.exists(TARGET):
        print(f'sidebar.css nao encontrado em {TARGET}')
        return 1

    raw = open(TARGET).read()
    body = strip_comments(raw)
    lines = body.split('\n')

    failures, pending, excecoes = [], [], []

    for i, line in enumerate(lines, 1):
        for m in HEX.finditer(line):
            failures.append((i, 'hex literal', m.group(0), line.strip()))
        for m in FUNC_COLOR.finditer(line):
            failures.append((i, 'cor por funcao', m.group(0) + '…)', line.strip()))
        for m in LENGTH.finditer(line):
            if m.group(0) == BREAKPOINT and line.lstrip().startswith('@media'):
                excecoes.append((i, m.group(0), line.strip()))
                continue
            failures.append((i, 'comprimento literal', m.group(0), line.strip()))
        for m in WEIGHT.finditer(line):
            failures.append((i, 'peso literal', m.group(0), line.strip()))
        for m in DURATION.finditer(line):
            pending.append((i, m.group(0), line.strip()))

    n_vars = len(set(re.findall(r'var\(\s*(--al-[\w-]+)', body)))
    usados = set(re.findall(r'var\(\s*(--al-sidebar-[\w-]+)', body))

    # Segundo portao, herdado do Select: token declarado e nunca usado e token
    # que so parece existir. Compara o que o tokens.py emitiu com o que o CSS
    # consome, pelo arquivo de tokens gerado ao lado.
    tokens_css = os.path.join(HERE, 'al-sidebar-tokens.css')
    declarados = set()
    if os.path.exists(tokens_css):
        declarados = set(re.findall(r'^\s*(--al-sidebar-[\w-]+)\s*:',
                                    open(tokens_css).read(), flags=re.M))
    orfaos = sorted(declarados - usados)
    inventados = sorted(usados - declarados) if declarados else []

    print('=' * 70)
    print('PORTAO DO CSS DO SIDEBAR')
    print('=' * 70)
    print(f'  arquivo                  : components/sidebar/sidebar.css')
    print(f'  custom properties usadas : {n_vars}  (sendo {len(usados)} da camada do Sidebar)')
    print(f'  tokens declarados        : {len(declarados)}')
    print(f'  linhas                   : {len(lines)}')
    print('-' * 70)
    for c in CONTRATOS_FORA_DO_CSS:
        print(f'fora do alcance deste portao: {c}')
    print('-' * 70)

    if pending:
        print(f'DURACAO LITERAL - o Sidebar usa motion.duration.panel, nao deveria haver nenhuma:')
        for ln, val, src in pending:
            print(f'   linha {ln:>3}  {val:<8} {src[:52]}')
    else:
        print('pendencias: nenhuma')
    for ln, val, src in excecoes:
        print(f'excecao `ponto-de-quebra`: linha {ln:>3}  {src[:52]}')
    print('-' * 70)

    if inventados:
        print(f'{len(inventados)} CUSTOM PROPERTY DO SIDEBAR QUE NAO EXISTE NA CAMADA DE TOKENS:')
        for t in inventados:
            print('   ', t)
        return 1

    if orfaos:
        print(f'{len(orfaos)} TOKEN(S) DECLARADO(S) E NUNCA USADO(S) - PORTAO REPROVA:')
        for t in orfaos:
            print('   ', t)
        print('   token que ninguem consome e token que so parece existir: ou o CSS')
        print('   esqueceu de aplicar, ou o token nao devia ter nascido.')
        return 1

    if failures:
        print(f'{len(failures)} VALOR(ES) LITERAL(IS) - PORTAO REPROVA:')
        for ln, kind, val, src in failures:
            print(f'   linha {ln:>3}  {kind:<20} {val:<12} {src[:44]}')
        return 1

    print(f'0 valores literais de cor, comprimento ou peso ({len(excecoes)} ponto(s) de quebra declarados).')
    print(f'{len(declarados)} tokens declarados, {len(usados)} consumidos, 0 orfaos.')
    return 0


if __name__ == '__main__':
    sys.exit(run())
