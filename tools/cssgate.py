"""
Portao do CSS dos componentes, num lugar so.

Mesma ideia do portao de alias do tokens.py, uma camada acima: o CSS de um
componente nao pode conter valor literal. Toda cor, comprimento, peso de fonte e
duracao entra por var(--al-*). O portao tambem compara os tokens que o
tokens.py declarou (no al-<c>-tokens.css gerado ao lado) com os que o CSS e o
JS do componente consomem:

  - orfao: token declarado e nunca usado (o CSS esqueceu de aplicar, ou o
    token nao devia ter nascido);
  - inventado: custom property --al-<c>-* usada mas nunca declarada (token que
    so parece existir). A que o proprio CSS do componente declara e um ponto
    de ajuste publico, nao token (ex.: --al-icon-box do Icon), e passa.

Cada components/<c>/check.py so diz o que e proprio do componente: o que o
portao nao alcanca (contratos de marcacao, cobrados pelo a11y.py no HTML do
site), excecoes declaradas e conferencias extras. Exemplo:

    from cssgate import gate
    sys.exit(gate('tooltip', fora_do_css=[...]))

Palavras-chave do CSS (none, currentColor, Canvas...) nao sao valor literal e
passam: o portao so procura hex, funcao de cor, numero com unidade e peso.
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

HEX = re.compile(r'#[0-9a-fA-F]{3,8}\b')
FUNC_COLOR = re.compile(r'\b(rgba?|hsla?|oklch|lab|color)\s*\(')
# comprimento literal fora de var(): 12px, 1.5rem, 2em...
LENGTH = re.compile(r'(?<![\w-])\d*\.?\d+(px|rem|em|ch|vh|vw)\b')
DURATION = re.compile(r'(?<![\w-])\d*\.?\d+m?s\b')
# peso de fonte cravado: font-weight: 500
WEIGHT = re.compile(r'font-weight\s*:\s*\d+')
# o JS le token no CSS computado: token(el, 'delay-show')
JS_TOKEN = re.compile(r"token\([\w.]+, '([\w-]+)'\)")


def strip_comments(text):
    return re.sub(r'/\*.*?\*/', '', text, flags=re.S)


def title(c):
    return ' '.join(p.capitalize() for p in c.split('-'))


def gate(c, fora_do_css=(), excecoes=(), extra=None):
    """
    c            nome da pasta do componente ('icon-button')
    fora_do_css  contratos que este portao nao alcanca (so entram no relatorio)
    excecoes     [(nome, valor, inicio)] - o literal `valor` numa linha que comeca
                 com `inicio` e aceito e listado como excecao declarada
                 (ex.: ('ponto-de-quebra', '1024px', '@media') da Sidebar)
    extra        funcao(body) -> (ok, linhas) para uma conferencia propria
    Devolve 0 (passa) ou 1 (reprova).
    """
    here = os.path.join(ROOT, 'components', c)
    target = os.path.join(here, f'{c}.css')
    nome = title(c)
    if not os.path.exists(target):
        print(f'{c}.css nao encontrado em {target}')
        return 1

    body = strip_comments(open(target).read())
    lines = body.split('\n')
    failures, declared_exc = [], []

    for i, line in enumerate(lines, 1):
        src = line.strip()
        hits = [('hex literal', m.group(0)) for m in HEX.finditer(line)]
        hits += [('cor por funcao', m.group(0) + '…)') for m in FUNC_COLOR.finditer(line)]
        hits += [('comprimento literal', m.group(0)) for m in LENGTH.finditer(line)]
        hits += [('peso literal', m.group(0)) for m in WEIGHT.finditer(line)]
        hits += [('duracao literal', m.group(0)) for m in DURATION.finditer(line)]
        for kind, val in hits:
            exc = next((n for n, v, ini in excecoes if val == v and src.startswith(ini)), None)
            if exc:
                declared_exc.append((i, exc, src))
            else:
                failures.append((i, kind, val, src))

    n_vars = len(set(re.findall(r'var\(\s*(--al-[\w-]+)', body)))
    usados = set(re.findall(rf'var\(\s*(--al-{c}-[\w-]+)', body))
    js = os.path.join(here, f'{c}.js')
    if os.path.exists(js):
        usados |= {f'--al-{c}-{n}' for n in JS_TOKEN.findall(open(js).read())}

    tokens_css = os.path.join(here, f'al-{c}-tokens.css')
    declarados = set()
    if os.path.exists(tokens_css):
        declarados = set(re.findall(rf'^\s*(--al-{c}-[\w-]+)\s*:',
                                    open(tokens_css).read(), flags=re.M))
    locais = set(re.findall(rf'(--al-{c}-[\w-]+)\s*:', body))
    orfaos = sorted(declarados - usados)
    inventados = sorted(usados - declarados - locais) if declarados else []

    print('=' * 70)
    print(f'PORTAO DO CSS DO {nome.upper()}')
    print('=' * 70)
    print(f'  arquivo                  : components/{c}/{c}.css')
    print(f'  custom properties usadas : {n_vars}  (sendo {len(usados)} da camada do {nome})')
    print(f'  tokens declarados        : {len(declarados)}')
    if locais:
        print(f'  ajuste publico no CSS    : {", ".join(sorted(locais))}')
    print(f'  linhas                   : {len(lines)}')
    print('-' * 70)
    for contrato in fora_do_css:
        print(f'fora do alcance deste portao: {contrato}')
    if fora_do_css:
        print('-' * 70)
    for ln, exc, src in declared_exc:
        print(f'excecao declarada `{exc}`: linha {ln:>3}  {src[:52]}')

    ok = True
    if extra:
        extra_ok, extra_lines = extra(body)
        for t in extra_lines:
            print(t)
        ok = ok and extra_ok

    if inventados:
        print(f'{len(inventados)} CUSTOM PROPERTY DO {nome.upper()} QUE NAO EXISTE NA CAMADA DE TOKENS:')
        for t in inventados:
            print('   ', t)
        ok = False

    if orfaos:
        print(f'{len(orfaos)} TOKEN(S) DECLARADO(S) E NUNCA USADO(S) - PORTAO REPROVA:')
        for t in orfaos:
            print('   ', t)
        print('   token que ninguem consome e token que so parece existir: ou o CSS')
        print('   esqueceu de aplicar, ou o token nao devia ter nascido.')
        ok = False

    if failures:
        print(f'{len(failures)} VALOR(ES) LITERAL(IS) - PORTAO REPROVA:')
        for ln, kind, val, src in failures:
            print(f'   linha {ln:>3}  {kind:<20} {val:<12} {src[:44]}')
        ok = False

    if not ok:
        return 1
    print(f'0 valores literais de cor, comprimento, peso ou duracao'
          f'{f" ({len(declared_exc)} excecao(oes) declarada(s))" if declared_exc else ""}.')
    print(f'{len(declarados)} tokens declarados, {len(usados - locais)} consumidos, 0 orfaos.')
    return 0
