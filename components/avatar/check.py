"""
Portao do CSS do Avatar.

Mesma ideia do portao de alias em tokens.py, uma camada acima: o componente nao
pode conter valor literal. Toda cor, comprimento e peso tem que entrar por
var(--al-*). Se um hex ou um px aparecer no avatar.css, o build para.

Igual ao Tag e diferente do Button e do Icon Button: aqui NAO ha excecao de
duracao de motion. O Avatar nao tem hover, nao tem transicao e nao tem estado -
e conteudo, nao controle. Entao a pendencia de escala de motion, que os dois
acionaveis carregam, simplesmente nao existe neste componente. O mecanismo de
relatorio fica de pe, vazio: pendencia some do relatorio quando some de verdade,
nunca por esquecimento.

Rodar: python3 check.py
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(HERE, 'avatar.css')

HEX = re.compile(r'#[0-9a-fA-F]{3,8}\b')
FUNC_COLOR = re.compile(r'\b(rgba?|hsla?|oklch|lab|color)\s*\(')
# comprimento literal fora de var(): 12px, 1.5rem, 2em...
LENGTH = re.compile(r'(?<![\w-])\d*\.?\d+(px|rem|em|ch|vh|vw)\b')
DURATION = re.compile(r'(?<![\w-])\d*\.?\d+m?s\b')
# peso de fonte cravado: font-weight: 500
WEIGHT = re.compile(r'font-weight\s*:\s*\d+')

# Os tres contratos deste componente nao vivem no CSS - vivem na marcacao e no
# conteudo que quem consome escreve. O portao de CSS nao alcanca nenhum deles;
# o segundo e cobrado pelo a11y.py da etapa 6, no HTML emitido. Os outros dois
# nao tem portao possivel, e por isso estao escritos no cabecalho do avatar.css
# e nas regras de uso. Esta lista existe para o relatorio dizer isso em voz alta.
CONTRATOS_FORA_DO_CSS = [
    'a cadeia Photo -> Iniciais -> Icon e comportamento de quem consome - troca de filho, nao de classe',
    'aria-hidden (decorativo) vs role="img" + aria-label (conteudo) no involucro - medido pelo a11y.py',
    'iniciais: no maximo 2 caracteres, derivadas do nome - regra de conteudo, sem portao possivel',
]


def strip_comments(text):
    return re.sub(r'/\*.*?\*/', '', text, flags=re.S)


def run():
    if not os.path.exists(TARGET):
        print(f'avatar.css nao encontrado em {TARGET}')
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
    n_avatar_vars = len(set(re.findall(r'var\(\s*(--al-avatar-[\w-]+)', body)))

    print('=' * 70)
    print('PORTAO DO CSS DO AVATAR')
    print('=' * 70)
    print(f'  arquivo                  : components/avatar/avatar.css')
    print(f'  custom properties usadas : {n_vars}  (sendo {n_avatar_vars} da camada do Avatar)')
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
