"""
Portao do CSS do Icon.

Mesma ideia do portao do Button, uma camada acima da de alias: o componente nao
pode conter valor literal. Toda cor e todo comprimento entram por var(--al-*).
Se um hex ou um px aparecer no icon.css, o build para.

Uma diferenca em relacao ao Button: aqui NAO ha pendencia consciente. O Button
carrega duracoes literais porque nao existe escala de motion na Foundation; o
Icon nao anima. Se um dia animar - o `loader-circle` esta no set - a animacao
pertence ao componente Spinner, que tem set proprio no Figma, e nao deve entrar
aqui de carona.

Rodar: python3 check.py
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(HERE, 'icon.css')

HEX = re.compile(r'#[0-9a-fA-F]{3,8}\b')
FUNC_COLOR = re.compile(r'\b(rgba?|hsla?|oklch|lab|color)\s*\(')
# comprimento literal fora de var(): 12px, 1.5rem, 2em...
LENGTH = re.compile(r'(?<![\w-])\d*\.?\d+(px|rem|em|ch|vh|vw)\b')
DURATION = re.compile(r'(?<![\w-])\d*\.?\d+m?s\b')


def strip_comments(text):
    return re.sub(r'/\*.*?\*/', '', text, flags=re.S)


def run():
    if not os.path.exists(TARGET):
        print(f'icon.css nao encontrado em {TARGET}')
        return 1

    body = strip_comments(open(TARGET).read())
    lines = body.split('\n')

    failures = []
    for i, line in enumerate(lines, 1):
        for m in HEX.finditer(line):
            failures.append((i, 'hex literal', m.group(0), line.strip()))
        for m in FUNC_COLOR.finditer(line):
            failures.append((i, 'cor por funcao', m.group(0) + '…)', line.strip()))
        for m in LENGTH.finditer(line):
            failures.append((i, 'comprimento literal', m.group(0), line.strip()))
        for m in DURATION.finditer(line):
            failures.append((i, 'duracao literal', m.group(0), line.strip()))

    n_vars = len(set(re.findall(r'var\(\s*(--al-[\w-]+)', body)))
    n_icon_vars = len(set(re.findall(r'var\(\s*(--al-icon-[\w-]+)', body)))

    print('=' * 70)
    print('PORTAO DO CSS DO ICON')
    print('=' * 70)
    print(f'  arquivo                  : components/icon/icon.css')
    print(f'  custom properties usadas : {n_vars}  (sendo {n_icon_vars} da camada do Icon)')
    print(f'  linhas                   : {len(lines)}')
    print('-' * 70)

    if failures:
        print(f'{len(failures)} VALOR(ES) LITERAL(IS) - PORTAO REPROVA:')
        for ln, kind, val, src in failures:
            print(f'   linha {ln:>3}  {kind:<20} {val:<12} {src[:44]}')
        return 1

    print('0 valores literais de cor, comprimento ou peso.')
    print('0 pendencias conscientes.')
    return 0


if __name__ == '__main__':
    sys.exit(run())
