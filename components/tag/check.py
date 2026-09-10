"""
Portao do CSS do Tag.

Mesma ideia do portao de alias em tokens.py, uma camada acima: o componente nao
pode conter valor literal. Toda cor, comprimento e peso tem que entrar por
var(--al-*). Se um hex ou um px aparecer no tag.css, o build para.

Diferenca em relacao ao Button e ao Icon Button: aqui NAO ha excecao de duracao
de motion. O Tag nao tem hover, nao tem transicao e nao tem animacao - por
decisao, o unico retorno do X e o cursor. Entao a pendencia de escala de motion,
que os outros dois carregam, simplesmente nao existe neste componente. O
mecanismo de relatorio fica de pe, vazio: pendencia some do relatorio quando
some de verdade, nunca por esquecimento.

Rodar: python3 check.py
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(HERE, 'tag.css')

HEX = re.compile(r'#[0-9a-fA-F]{3,8}\b')
FUNC_COLOR = re.compile(r'\b(rgba?|hsla?|oklch|lab|color)\s*\(')
# comprimento literal fora de var(): 12px, 1.5rem, 2em...
LENGTH = re.compile(r'(?<![\w-])\d*\.?\d+(px|rem|em|ch|vh|vw)\b')
DURATION = re.compile(r'(?<![\w-])\d*\.?\d+m?s\b')
# peso de fonte cravado: font-weight: 500
WEIGHT = re.compile(r'font-weight\s*:\s*\d+')

# Os dois contratos deste componente nao vivem no CSS - vivem na marcacao e no
# texto que quem consome escreve. O portao nao alcanca nenhum dos dois; quem
# cobra o segundo e o a11y.py da etapa 6, no HTML emitido. O primeiro nao tem
# portao possivel, e por isso esta escrito no cabecalho do tag.css e na regra
# de uso. Esta lista existe para o relatorio dizer isso em voz alta.
CONTRATOS_FORA_DO_CSS = [
    'o rotulo carrega o sentido, a cor nao - nenhum portao mede isso, e regra de uso',
    'aria-label obrigatorio no <button> do X, incluindo o rotulo - medido pelo a11y.py',
]


def strip_comments(text):
    return re.sub(r'/\*.*?\*/', '', text, flags=re.S)


def run():
    if not os.path.exists(TARGET):
        print(f'tag.css nao encontrado em {TARGET}')
        return 1

    raw = open(TARGET).read()
    body = strip_comments(raw)
    lines = body.split('\n')

    failures, pending = [], []

    for i, line in enumerate(lines, 1):
        for m in HEX.finditer(line):
            failures.append((i, 'hex literal', m.group(0), line.strip()))
        for m in FUNC_COLOR.finditer(line):
            failures.append((i, 'cor por funcao', m.group(0) + '…)', line.strip()))
        for m in LENGTH.finditer(line):
            failures.append((i, 'comprimento literal', m.group(0), line.strip()))
        for m in WEIGHT.finditer(line):
            failures.append((i, 'peso literal', m.group(0), line.strip()))
        for m in DURATION.finditer(line):
            pending.append((i, m.group(0), line.strip()))

    n_vars = len(set(re.findall(r'var\(\s*(--al-[\w-]+)', body)))
    n_tag_vars = len(set(re.findall(r'var\(\s*(--al-tag-[\w-]+)', body)))

    print('=' * 70)
    print('PORTAO DO CSS DO TAG')
    print('=' * 70)
    print(f'  arquivo                  : components/tag/tag.css')
    print(f'  custom properties usadas : {n_vars}  (sendo {n_tag_vars} da camada do Tag)')
    print(f'  linhas                   : {len(lines)}')
    print('-' * 70)
    for c in CONTRATOS_FORA_DO_CSS:
        print(f'contrato fora do alcance deste portao: {c}')
    print('-' * 70)

    if pending:
        print(f'pendencia consciente - {len(pending)} duracao(oes) literal(is), '
              f'aguardando escala de motion na Foundation:')
        for ln, val, src in pending:
            print(f'   linha {ln:>3}  {val:<8} {src[:52]}')
    else:
        print('pendencias: nenhuma - este componente nao tem transicao nem animacao')
    print('-' * 70)

    if failures:
        print(f'{len(failures)} VALOR(ES) LITERAL(IS) - PORTAO REPROVA:')
        for ln, kind, val, src in failures:
            print(f'   linha {ln:>3}  {kind:<20} {val:<12} {src[:44]}')
        return 1

    print('0 valores literais de cor, comprimento ou peso.')
    return 0


if __name__ == '__main__':
    sys.exit(run())
