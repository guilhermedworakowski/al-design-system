"""
Camada de tokens do Button.

Regra unica desta camada: nada aqui inventa valor. Todo token do Button
aponta para um token da Foundation pelo NOME. O portao no fim do arquivo
recusa qualquer coisa que seja um valor solto - hex, px, numero.

Nomenclatura:
  codigo -> button-primary-bg-hover     (hifen)
  Figma  -> button/primary/bg-hover     (pasta)
Sao camadas diferentes. Nunca colapsar uma na outra.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'foundation'))

from build import SEM                     # noqa: E402

# Fonte unica, na raiz. O chdir que existia aqui apontava para uma copia em
# foundation/, e era ela - nao a raiz - que os portoes liam.
FOUND = json.load(open(os.path.join(ROOT, 'tokens.json')))   # noqa: E402

TRANSPARENT = 'transparent'   # ausencia de cor, nao uma escolha de cor

# ---------------------------------------------------------------- cor
# Cada variante repete a mesma forma: fundo em 4 estados, rotulo em 2,
# borda em 2, anel de foco. Onde a variante nao tem aquele papel, o valor
# e transparente - a geometria nao muda entre estados, so a cor.
COLOR = {
  'primary': {
    'bg':               'bg-brand',
    'bg-hover':         'bg-brand-hover',
    'bg-active':        'bg-brand-active',
    'bg-disabled':      'bg-disabled',
    'label':            'text-on-brand',
    'label-disabled':   'text-disabled',
    'border':           TRANSPARENT,
    'border-disabled':  'border-subtle',
  },
  'secondary': {
    'bg':               TRANSPARENT,
    'bg-hover':         'bg-hover',
    'bg-active':        'bg-active',
    'bg-disabled':      TRANSPARENT,
    'label':            'text-primary',
    'label-disabled':   'text-disabled',
    'border':           'border-strong',
    'border-disabled':  'border-subtle',
  },
  'ghost': {
    'bg':               TRANSPARENT,
    'bg-hover':         'bg-hover',
    'bg-active':        'bg-active',
    'bg-disabled':      TRANSPARENT,
    'label':            'text-primary',
    'label-disabled':   'text-disabled',
    'border':           TRANSPARENT,
    'border-disabled':  TRANSPARENT,
  },
  'danger': {
    'bg':               'bg-danger',
    'bg-hover':         'bg-danger-hover',
    'bg-active':        'bg-danger-active',
    'bg-disabled':      'bg-disabled',
    'label':            'text-on-solid',
    'label-disabled':   'text-disabled',
    'border':           TRANSPARENT,
    'border-disabled':  'border-subtle',
  },
}

# Anel de foco: aponta para a sombra composta da Foundation, nao para a cor
# crua. Danger usa o anel de erro; o resto usa o padrao.
RING = {
  'primary':   'focusRing.default',
  'secondary': 'focusRing.default',
  'ghost':     'focusRing.default',
  'danger':    'focusRing.error',
}

# ------------------------------------------------------------ geometria
# Nao existe token de altura. A altura e consequencia: padding-y x2 mais a
# entrelinha do rotulo. sm = 8+20+8 = 36. md = 12+24+12 = 48. Criar um
# token de altura seria fixar em dois lugares a mesma decisao.
SIZE = {
  'sm': {'padding-x': 'space.12', 'padding-y': 'space.8',
         'gap': 'space.8', 'font': 'type.styles.label-md'},
  'md': {'padding-x': 'space.16', 'padding-y': 'space.12',
         'gap': 'space.8', 'font': 'type.styles.label-lg'},
}

SHARED = {
  'radius':       'radius.full',
  'border-width': 'border.width.1',
}

# Pendencia consciente: o Button usa icone de 16 nos dois tamanhos, e o set
# irmao Icon Button usa 20. Nao existe escala de icone na Foundation ainda.
# Nao invento uma aqui - ela nasce com o componente Icon, no Tier 1.
PENDING = {'icon-size': {'sm': 16, 'md': 16, 'nota': 'aguarda escala de icone na Foundation'}}


# ---------------------------------------------------------------- portao
def resolve_foundation(path):
    """Segue um caminho pontuado dentro de tokens.json. Levanta se nao existir.

    type.styles e uma lista de tuplas (nome, size, leading, weight, ...), nao um
    dicionario - entao o ultimo trecho do caminho casa contra o nome do estilo.
    """
    node = FOUND
    for part in path.split('.'):
        if isinstance(node, list):
            match = next((s for s in node if s and s[0] == part), None)
            if match is None:
                raise KeyError(path)
            node = match
            continue
        if not isinstance(node, dict) or part not in node:
            raise KeyError(path)
        node = node[part]
    return node


def run():
    alias, resolved, problems = {}, {}, []

    for variant, roles in COLOR.items():
        for role, ref in roles.items():
            name = f'button-{variant}-{role}'
            alias[name] = ref
            if ref == TRANSPARENT:
                resolved[name] = {'light': TRANSPARENT, 'dark': TRANSPARENT}
                continue
            if ref.startswith('#'):
                problems.append(f'{name}: hex solto ({ref}) - todo valor de cor nasce alias do semantico')
                continue
            if ref not in SEM:
                problems.append(f'{name}: aponta para {ref}, que nao existe na camada semantica')
                continue
            light, dark = SEM[ref]
            resolved[name] = {'light': light, 'dark': dark}

    for variant, ref in RING.items():
        name = f'button-{variant}-ring'
        alias[name] = ref
        try:
            v = resolve_foundation(ref)
            resolved[name] = {'light': v['light'], 'dark': v['dark']}
        except KeyError:
            problems.append(f'{name}: {ref} nao existe na Foundation')

    for size, roles in SIZE.items():
        for role, ref in roles.items():
            name = f'button-{size}-{role}'
            alias[name] = ref
            try:
                resolved[name] = resolve_foundation(ref)
            except KeyError:
                problems.append(f'{name}: {ref} nao existe na Foundation')

    for role, ref in SHARED.items():
        name = f'button-{role}'
        alias[name] = ref
        try:
            resolved[name] = resolve_foundation(ref)
        except KeyError:
            problems.append(f'{name}: {ref} nao existe na Foundation')

    # altura derivada, so para conferencia - nao vira token
    heights = {}
    for size in SIZE:
        py = resolve_foundation(SIZE[size]['padding-y'])
        style = resolve_foundation(SIZE[size]['font'])
        heights[size] = py * 2 + style[2]   # (nome, size, leading, ...) -> leading

    print('=' * 70)
    print('CAMADA DE TOKENS DO BUTTON')
    print('=' * 70)
    for name in sorted(alias):
        ref = alias[name]
        tag = 'transparente' if ref == TRANSPARENT else f'-> {ref}'
        print(f'  {name:<34} {tag}')
    print('-' * 70)
    print(f'altura derivada: sm {heights["sm"]}px   md {heights["md"]}px  (padding-y x2 + entrelinha)')
    print(f'pendente: icon-size {PENDING["icon-size"]["sm"]}/{PENDING["icon-size"]["md"]} - {PENDING["icon-size"]["nota"]}')
    print('-' * 70)

    if problems:
        print(f'{len(problems)} TOKEN(S) REPROVAM O PORTAO DE ALIAS:')
        for p in problems:
            print('   ', p)
        return 1

    n_alias = sum(1 for r in alias.values() if r != TRANSPARENT)
    n_tr = len(alias) - n_alias
    print(f'{len(alias)} tokens: {n_alias} alias da Foundation, {n_tr} transparentes.')
    print('0 valores soltos.')

    out = {
        'meta': {
            'component': 'Button',
            'version': '0.1.0',
            'foundation': FOUND['meta']['version'],
            'figmaNode': '23:123',
            'variants': list(COLOR),
            'sizes': list(SIZE),
            'states': ['default', 'hover', 'pressed', 'focus', 'disabled'],
            'nota': 'button-*-ring aponta para a sombra composta, nao para a cor crua.',
        },
        'alias': alias,
        'resolved': resolved,
        'derived': {'height': heights},
        'pending': PENDING,
    }
    json.dump(out, open(os.path.join(HERE, 'tokens.json'), 'w'), indent=2, ensure_ascii=False)
    print(f'\ncomponents/button/tokens.json escrito')
    write_css(alias, heights)
    return 0


# ---------------------------------------------------------------- css
def css_ref(ref):
    """Traduz a referencia da Foundation para a custom property equivalente."""
    if ref == TRANSPARENT:
        return 'transparent'
    if ref.startswith('focusRing.'):
        return f'var(--al-focus-ring-{ref.split(".")[1]})'
    if ref.startswith('space.'):
        return f'var(--al-space-{ref.split(".")[1]})'
    if ref.startswith('radius.'):
        return f'var(--al-radius-{ref.split(".")[1]})'
    if ref.startswith('border.width.'):
        return f'var(--al-border-width-{ref.split(".")[2]})'
    return f'var(--al-{ref})'          # semantico de cor


def write_css(alias, heights):
    L = []
    w = L.append
    w('/* AL Design System - tokens do Button')
    w(' * GERADO por components/button/tokens.py. Nao editar a mao.')
    w(' *')
    w(' * Nao ha bloco de tema aqui, e isso e o ponto: cada token aponta para um')
    w(' * semantico, e o tema troca no :root - o mesmo elemento onde estes alias')
    w(' * sao declarados. Entao o :root re-substitui todos eles de uma vez, e o')
    w(' * Button inteiro acompanha sem uma linha a mais.')
    w(' *')
    w(' * Cuidado: substituicao de custom property acontece no elemento onde ela e')
    w(' * DECLARADA, nao no ponto de uso. Um alias declarado aqui desce ja resolvido.')
    w(' * Por isso tematizar um container solto (e nao o :root) exige re-declarar')
    w(' * esta camada dentro do bloco daquele container - ver site/site.py.')
    w(' */')
    w('')
    w(':root {')

    for variant in COLOR:
        w('')
        w(f'  /* {variant} */')
        for role, ref in COLOR[variant].items():
            w(f'  --al-button-{variant}-{role}: {css_ref(ref)};')
        w(f'  --al-button-{variant}-ring: {css_ref(RING[variant])};')

    for size, roles in SIZE.items():
        w('')
        w(f'  /* tamanho {size} - altura resultante: {heights[size]}px */')
        for role, ref in roles.items():
            if role == 'font':
                style = resolve_foundation(ref)
                _, fsize, leading, weight, _, _ = style
                w(f'  --al-button-{size}-font-size: var(--al-font-size-{size_key(fsize)});')
                w(f'  --al-button-{size}-line-height: var(--al-line-height-{leading_key(leading)});')
                w(f'  --al-button-{size}-font-weight: var(--al-font-weight-{weight_key(weight)});')
            else:
                w(f'  --al-button-{size}-{role}: {css_ref(ref)};')

    w('')
    w('  /* compartilhado */')
    for role, ref in SHARED.items():
        w(f'  --al-button-{role}: {css_ref(ref)};')
    w(f'  --al-button-icon-size: {PENDING["icon-size"]["sm"]}px;  '
      f'/* {PENDING["icon-size"]["nota"]} */')
    w('}')
    w('')

    path = os.path.join(HERE, 'al-button-tokens.css')
    open(path, 'w').write('\n'.join(L))
    print(f'components/button/al-button-tokens.css escrito ({os.path.getsize(path)} bytes)')


def size_key(v):
    return scale_key_in(FOUND['type']['size'], v, 'font-size')


def leading_key(v):
    return scale_key_in(FOUND['type']['leading'], v, 'line-height')


def weight_key(v):
    return scale_key_in(FOUND['type']['weight'], v, 'font-weight')


def scale_key_in(d, value, label):
    for k, x in d.items():
        if x == value:
            return k
    raise KeyError(f'{value} nao e um degrau de {label}')


if __name__ == '__main__':
    sys.exit(run())
