"""
Portao do CSS do Password.

Mesma ideia do portao de alias em tokens.py, uma camada acima: o componente nao
pode conter valor literal. Toda cor, comprimento e peso tem que entrar por
var(--al-*). Se um hex ou um px aparecer no password.css, o build para.

Igual ao Select e ao Input: aqui HA excecao de duracao de motion. O Password e controle,
tem hover e foco, e por isso tem transicao - e a Foundation ainda nao tem escala de motion para os 120ms
apontarem. A duracao entra como pendencia nomeada, nunca como reprova.

Rodar: python3 check.py
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(HERE, 'password.css')

HEX = re.compile(r'#[0-9a-fA-F]{3,8}\b')
FUNC_COLOR = re.compile(r'\b(rgba?|hsla?|oklch|lab|color)\s*\(')
# comprimento literal fora de var(): 12px, 1.5rem, 2em...
LENGTH = re.compile(r'(?<![\w-])\d*\.?\d+(px|rem|em|ch|vh|vw)\b')
DURATION = re.compile(r'(?<![\w-])\d*\.?\d+m?s\b')
# peso de fonte cravado: font-weight: 500
WEIGHT = re.compile(r'font-weight\s*:\s*\d+')

# O que este portao NAO alcanca. Quase tudo que pode dar errado num campo de
# formulario e marcacao, nao estilo - e marcacao so existe na saida renderizada.
# O a11y.py da etapa 6 cobra os tres primeiros no HTML que o site emite.
CONTRATOS_FORA_DO_CSS = [
    '<label for> ligado ao id do <input> - sem aria-label havendo rotulo visivel',
    'erro: aria-invalid="true" + aria-describedby apontando para o id da mensagem (regra 29)',
    'erro exige a mensagem; __help so existe no erro (regras 7 e 8)',
    'olho: <button type="button"> + aria-controls + aria-label alternando, nasce hidden (regra 28)',
    'icones do olho com aria-hidden="true" focusable="false" (contrato do Icon)',
    'campo desabilitado -> botao do olho tambem disabled (regra 20)',
    'autocomplete current-password/new-password, spellcheck=false, autocapitalize=none (regras 25-26)',
    'sem maxlength (regra 12); colar permitido (regra 27)',
]


def strip_comments(text):
    return re.sub(r'/\*.*?\*/', '', text, flags=re.S)


def run():
    if not os.path.exists(TARGET):
        print(f'password.css nao encontrado em {TARGET}')
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
    usados = set(re.findall(r'var\(\s*(--al-password-[\w-]+)', body))

    # Segundo portao, herdado do Select: token declarado e nunca usado e token
    # que so parece existir. Compara o que o tokens.py emitiu com o que o CSS
    # consome, pelo arquivo de tokens gerado ao lado.
    tokens_css = os.path.join(HERE, 'al-password-tokens.css')
    declarados = set()
    if os.path.exists(tokens_css):
        declarados = set(re.findall(r'^\s*(--al-password-[\w-]+)\s*:',
                                    open(tokens_css).read(), flags=re.M))
    orfaos = sorted(declarados - usados)
    inventados = sorted(usados - declarados) if declarados else []

    print('=' * 70)
    print('PORTAO DO CSS DO PASSWORD')
    print('=' * 70)
    print(f'  arquivo                  : components/password/password.css')
    print(f'  custom properties usadas : {n_vars}  (sendo {len(usados)} da camada do Password)')
    print(f'  tokens declarados        : {len(declarados)}')
    print(f'  linhas                   : {len(lines)}')
    print('-' * 70)
    for c in CONTRATOS_FORA_DO_CSS:
        print(f'fora do alcance deste portao: {c}')
    print('-' * 70)

    if pending:
        print(f'pendencia consciente - {len(pending)} duracao(oes) literal(is), '
              f'aguardando escala de motion na Foundation:')
        for ln, val, src in pending:
            print(f'   linha {ln:>3}  {val:<8} {src[:52]}')
    else:
        print('pendencias: nenhuma')
    print('-' * 70)

    if inventados:
        print(f'{len(inventados)} CUSTOM PROPERTY DO PASSWORD QUE NAO EXISTE NA CAMADA DE TOKENS:')
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

    print('0 valores literais de cor, comprimento ou peso.')
    print(f'{len(declarados)} tokens declarados, {len(usados)} consumidos, 0 orfaos.')
    return 0


if __name__ == '__main__':
    sys.exit(run())
