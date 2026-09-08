"""
Portao do CSS do Icon Button.

Mesma ideia do portao de alias em tokens.py, uma camada acima: o componente nao
pode conter valor literal. Toda cor, comprimento e peso tem que entrar por
var(--al-*). Se um hex ou um px aparecer no icon-button.css, o build para.

Duracao de animacao e a excecao consciente, herdada do Button: a Foundation
ainda nao tem escala de motion. Fica listada como pendencia, nao como reprova.

Rodar: python3 check.py
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(HERE, 'icon-button.css')

# palavras-chave do CSS que nao sao "valor literal" no sentido que importa aqui
ALLOWED_WORDS = {
    'none', 'transparent', 'currentColor', 'inherit', 'initial', 'unset', 'auto',
    'block', 'flex', 'inline-flex', 'center', 'solid', 'ease', 'linear', 'infinite',
    'border-box', 'pointer', 'not-allowed', 'rotate',
    # cores de sistema do modo de alto contraste - vem do SO, nao do design system
    'Highlight', 'GrayText', 'ButtonText', 'ButtonFace', 'CanvasText', 'Canvas',
}

HEX = re.compile(r'#[0-9a-fA-F]{3,8}\b')
FUNC_COLOR = re.compile(r'\b(rgba?|hsla?|oklch|lab|color)\s*\(')
# comprimento literal fora de var(): 12px, 1.5rem, 2em...
LENGTH = re.compile(r'(?<![\w-])\d*\.?\d+(px|rem|em|ch|vh|vw)\b')
DURATION = re.compile(r'(?<![\w-])\d*\.?\d+m?s\b')

# O nome acessivel nao e opcional neste componente, e diferente das outras
# regras ele nao vive no CSS - vive na marcacao. O portao nao consegue medir
# isso aqui; quem cobra e o a11y.py da etapa 6, no HTML emitido. Esta constante
# existe para o relatorio dizer isso em voz alta, em vez de silenciar.
CONTRATO_FORA_DO_CSS = 'aria-label obrigatorio no <button> - medido pelo a11y.py, nao aqui'


def strip_comments(text):
    return re.sub(r'/\*.*?\*/', '', text, flags=re.S)


def run():
    if not os.path.exists(TARGET):
        print(f'icon-button.css nao encontrado em {TARGET}')
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
        for m in DURATION.finditer(line):
            pending.append((i, m.group(0), line.strip()))

    n_vars = len(set(re.findall(r'var\(\s*(--al-[\w-]+)', body)))
    n_ib_vars = len(set(re.findall(r'var\(\s*(--al-icon-button-[\w-]+)', body)))

    print('=' * 70)
    print('PORTAO DO CSS DO ICON BUTTON')
    print('=' * 70)
    print(f'  arquivo                  : components/icon-button/icon-button.css')
    print(f'  custom properties usadas : {n_vars}  (sendo {n_ib_vars} da camada do Icon Button)')
    print(f'  linhas                   : {len(lines)}')
    print('-' * 70)
    print(f'contrato fora do alcance deste portao: {CONTRATO_FORA_DO_CSS}')
    print('-' * 70)

    if pending:
        print(f'pendencia consciente - {len(pending)} duracao(oes) literal(is), '
              f'aguardando escala de motion na Foundation:')
        for ln, val, src in pending:
            print(f'   linha {ln:>3}  {val:<8} {src[:52]}')
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
