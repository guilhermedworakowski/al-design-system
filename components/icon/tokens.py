"""
Camada de tokens do Icon.

Mesma regra unica da camada do Button: nada aqui inventa valor. Todo token do
Icon aponta para um token da Foundation pelo NOME, e o portao no fim do arquivo
recusa qualquer coisa que seja valor solto.

Nomenclatura:
  codigo -> icon-ink-on-brand      (hifen)
  Figma  -> icon/ink               (pasta, collection `3. Icon ink`)
Sao camadas diferentes. Nunca colapsar uma na outra.

Duas decisoes desta camada que o diff nao explica sozinho:

1. A CAIXA se chama `icon-box`, nao `icon-size`. `--al-icon-size-16` ja existe
   e e a primitiva da Foundation; se o token do componente tivesse o mesmo
   nome, ele apontaria para si mesmo e a custom property morreria em ciclo.
   `box` e o papel no componente, `size` e o degrau na escala.

2. A TINTA tem quatro tokens porque a collection `3. Icon ink` do Figma tem
   quatro modes. Mas o default do CSS nao e nenhum deles: e `currentColor`.
   Os modes existem no Figma porque o Figma nao tem `currentColor` - dentro do
   Button, o icone precisa que ALGUEM diga de que cor ele e. Na web o icone
   herda a cor do rotulo sozinho, e uma palavra-chave substitui a collection
   inteira. Estes quatro tokens sao a saida EXPLICITA, para icone que vive
   fora de um acionavel e nao tem de quem herdar.

Rodar: python3 tokens.py     (escreve al-icon-tokens.css, nao redirecionar stdout)
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'foundation'))

from build import SEM                     # noqa: E402

FOUND = json.load(open(os.path.join(ROOT, 'tokens.json')))   # noqa: E402


# ---------------------------------------------------------------- caixa
# Os quatro degraus recorrentes. Nao sao um teto: `--al-icon-box` e publica e
# aceita qualquer valor no ponto de uso. O componente e vetorizado no grid de
# 24 e vale em qualquer tamanho - estes quatro so nomeiam o que se repete.
BOX = {
  '16': 'iconSize.16',
  '20': 'iconSize.20',
  '24': 'iconSize.24',
  '32': 'iconSize.32',
}

# ---------------------------------------------------------------- tinta
# Uma linha por mode da collection `3. Icon ink`. A ordem e a mesma do Figma.
INK = {
  'default':  'text-primary',
  'on-brand': 'text-on-brand',
  'on-solid': 'text-on-solid',
  'disabled': 'text-disabled',
}

# Degrau padrao do componente. Vive aqui e nao no CSS para que trocar o padrao
# seja uma linha de token, nao uma edicao de folha de estilo.
DEFAULT_BOX = '24'


# ---------------------------------------------------------------- portao
def resolve_foundation(path):
    """Segue um caminho pontuado dentro de tokens.json. Levanta se nao existir."""
    node = FOUND
    for part in path.split('.'):
        node = node[part]
    return node


def run():
    alias, resolved, problems = {}, {}, []

    for step, ref in BOX.items():
        name = f'icon-box-{step}'
        alias[name] = ref
        try:
            resolved[name] = resolve_foundation(ref)
        except (KeyError, TypeError):
            problems.append(f'{name}: {ref} nao existe na Foundation')

    for mode, ref in INK.items():
        name = f'icon-ink-{mode}'
        alias[name] = ref
        if ref.startswith('#'):
            problems.append(f'{name}: hex solto ({ref}) - toda cor nasce alias do semantico')
            continue
        if ref not in SEM:
            problems.append(f'{name}: aponta para {ref}, que nao existe na camada semantica')
            continue
        light, dark = SEM[ref]
        resolved[name] = {'light': light, 'dark': dark}

    if DEFAULT_BOX not in BOX:
        problems.append(f'degrau padrao {DEFAULT_BOX} nao existe em BOX')

    print('=' * 70)
    print('CAMADA DE TOKENS DO ICON')
    print('=' * 70)
    for name in sorted(alias):
        print(f'  {name:<24} -> {alias[name]}')
    print('-' * 70)
    print(f'degrau padrao: {DEFAULT_BOX}px  (o resto e modificador ou valor no ponto de uso)')
    print('pendencias: nenhuma')
    print('-' * 70)

    if problems:
        print(f'{len(problems)} TOKEN(S) REPROVAM O PORTAO DE ALIAS:')
        for p in problems:
            print('   ', p)
        return 1

    print(f'{len(alias)} tokens: {len(alias)} alias da Foundation, 0 valores soltos.')
    write_css(alias)
    write_json(alias, resolved)
    return 0


def css_ref(ref):
    """Traduz a referencia da Foundation para a custom property equivalente."""
    if ref.startswith('iconSize.'):
        return f'var(--al-icon-size-{ref.split(".")[1]})'
    return f'var(--al-{ref})'          # semantico de cor


def write_css(alias):
    L = []
    w = L.append
    w('/* AL Design System - tokens do Icon')
    w(' * GERADO por components/icon/tokens.py. Nao editar a mao.')
    w(' *')
    w(' * Nao ha bloco de tema aqui: cada tinta aponta para um semantico, e o tema')
    w(' * troca no :root - o mesmo elemento onde estes alias sao declarados. Entao o')
    w(' * :root re-substitui todos eles de uma vez.')
    w(' */')
    w('')
    w(':root {')
    w('')
    w('  /* caixa - degrau recorrente, nao teto */')
    for step in BOX:
        w(f'  --al-icon-box-{step}: {css_ref(BOX[step])};')
    w('')
    w('  /* tinta - saida explicita. O default do componente e currentColor. */')
    for mode in INK:
        w(f'  --al-icon-ink-{mode}: {css_ref(INK[mode])};')
    w('}')
    w('')

    path = os.path.join(HERE, 'al-icon-tokens.css')
    open(path, 'w').write('\n'.join(L))
    print(f'components/icon/al-icon-tokens.css escrito ({os.path.getsize(path)} bytes)')


def write_json(alias, resolved):
    out = {'component': 'icon', 'defaultBox': DEFAULT_BOX,
           'alias': alias, 'resolved': resolved, 'pending': {}}
    path = os.path.join(HERE, 'tokens.json')
    json.dump(out, open(path, 'w'), indent=2, ensure_ascii=False)
    print('components/icon/tokens.json escrito')


if __name__ == '__main__':
    sys.exit(run())
