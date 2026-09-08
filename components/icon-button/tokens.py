"""
Camada de tokens do Icon Button.

Regra unica desta camada: nada aqui inventa valor. Todo token aponta para um
token da Foundation pelo NOME. O portao no fim do arquivo recusa qualquer
coisa que seja um valor solto - hex, px, numero.

Nomenclatura:
  codigo -> icon-button-primary-bg-hover     (hifen)
  Figma  -> icon-button/primary/bg-hover     (pasta)
Sao camadas diferentes. Nunca colapsar uma na outra.

O QUE SEPARA ESTE COMPONENTE DO BUTTON

  O Button carrega o sentido num rotulo de TEXTO: criterio 1.4.3, piso 4.5:1.
  E por isso que branco sobre bg-brand (3.34:1) e uma excecao de marca nomeada
  la dentro.

  Aqui nao existe rotulo. Quem carrega o sentido e um ICONE, que e conteudo
  nao-textual: criterio 1.4.11, piso 3:1. O mesmo par deixa de ser excecao e
  passa a ser aprovacao. Este componente nao tem nenhuma excecao de marca.

  A consequencia disso e do a11y.py, nao deste arquivo - mas a decisao nasce
  aqui, e por isso esta escrita aqui.

O PAPEL SE CHAMA `ink`, NAO `label`

  `label` no Button e texto. Aqui e tinta de icone, e `ink` ja e o vocabulario
  do sistema - o componente Icon usa icon-ink-default. Mesmo conceito, mesmo
  nome.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'foundation'))

from build import SEM                     # noqa: E402

# Fonte unica, na raiz - a mesma que todos os outros portoes leem.
FOUND = json.load(open(os.path.join(ROOT, 'tokens.json')))   # noqa: E402

TRANSPARENT = 'transparent'   # ausencia de cor, nao uma escolha de cor

# ---------------------------------------------------------------- cor
# Mesma forma do Button - fundo em 4 estados, tinta em 2, borda em 2, anel de
# foco - com `ink` no lugar de `label`. Os valores coincidem com os do Button
# porque a ORIGEM e a mesma, nao porque um herda do outro: cada token aqui
# aponta direto ao semantico. O portao de alias abaixo exige isso; token de
# componente nunca referencia outro componente.
COLOR = {
  'primary': {
    'bg':               'bg-brand',
    'bg-hover':         'bg-brand-hover',
    'bg-active':        'bg-brand-active',
    'bg-disabled':      'bg-disabled',
    'ink':              'text-on-brand',
    'ink-disabled':     'text-disabled',
    'border':           TRANSPARENT,
    'border-disabled':  'border-subtle',
  },
  'secondary': {
    'bg':               TRANSPARENT,
    'bg-hover':         'bg-hover',
    'bg-active':        'bg-active',
    'bg-disabled':      TRANSPARENT,
    'ink':              'text-primary',
    'ink-disabled':     'text-disabled',
    'border':           'border-strong',
    'border-disabled':  'border-subtle',
  },
  'ghost': {
    'bg':               TRANSPARENT,
    'bg-hover':         'bg-hover',
    'bg-active':        'bg-active',
    'bg-disabled':      TRANSPARENT,
    'ink':              'text-primary',
    'ink-disabled':     'text-disabled',
    'border':           TRANSPARENT,
    'border-disabled':  TRANSPARENT,
  },
  'danger': {
    'bg':               'bg-danger',
    'bg-hover':         'bg-danger-hover',
    'bg-active':        'bg-danger-active',
    'bg-disabled':      'bg-disabled',
    'ink':              'text-on-solid',
    'ink-disabled':     'text-disabled',
    'border':           TRANSPARENT,
    'border-disabled':  'border-subtle',
  },
}

# Anel de foco: aponta para a sombra composta da Foundation, nao para a cor
# crua. E o que mantem cor-de-estado dentro do portao de contraste, em vez de
# escapar junto da elevacao. Danger usa o anel de erro; o resto usa o padrao.
RING = {
  'primary':   'focusRing.default',
  'secondary': 'focusRing.default',
  'ghost':     'focusRing.default',
  'danger':    'focusRing.error',
}

# ------------------------------------------------------------ geometria
# UM token de padding por tamanho, nao dois. O Button separa padding-x de
# padding-y porque e retangular; aqui o botao e quadrado e o valor e o mesmo
# nos quatro lados. Dois tokens fixariam a mesma decisao em dois lugares.
#
# Nao existe token de tamanho de caixa. Ele e consequencia: padding x2 mais o
# icone. sm = 8+20+8 = 36. md = 12+24+12 = 48 - exatamente as alturas do Button,
# que e o que faz os dois conviverem numa toolbar sem desalinhar.
#
# Nao ha `gap` (existe um filho so) nem `font` (nao ha texto).
SIZE = {
  'sm': {'padding': 'space.8',  'icon-size': 'iconSize.20'},
  'md': {'padding': 'space.12', 'icon-size': 'iconSize.24'},
}

SHARED = {
  'radius':       'radius.full',
  'border-width': 'border.width.1',
}

# O estado de carregando NAO gera token: o spinner reaproveita
# border.width.2, radius.full e currentColor - que aqui resolve para
# icon-button-<variante>-ink. A duracao segue literal no CSS, dentro da
# pendencia de escala de motion ja registrada no README.
#
# O mecanismo fica de pe, vazio. Pendencia some do relatorio quando some de
# verdade, nunca por esquecimento.
PENDING = {}


# ---------------------------------------------------------------- portao
def resolve_foundation(path):
    """Segue um caminho pontuado dentro de tokens.json. Levanta se nao existir."""
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


def button_heights():
    """Alturas do Button, so para conferencia de paridade. Nao e portao:
    se o Button ainda nao foi gerado, a conferencia e pulada, nao quebra."""
    path = os.path.join(ROOT, 'components', 'button', 'tokens.json')
    if not os.path.exists(path):
        return None
    return json.load(open(path)).get('derived', {}).get('height')


def run():
    alias, resolved, problems = {}, {}, []

    for variant, roles in COLOR.items():
        for role, ref in roles.items():
            name = f'icon-button-{variant}-{role}'
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
        name = f'icon-button-{variant}-ring'
        alias[name] = ref
        try:
            v = resolve_foundation(ref)
            resolved[name] = {'light': v['light'], 'dark': v['dark']}
        except KeyError:
            problems.append(f'{name}: {ref} nao existe na Foundation')

    for size, roles in SIZE.items():
        for role, ref in roles.items():
            name = f'icon-button-{size}-{role}'
            alias[name] = ref
            try:
                resolved[name] = resolve_foundation(ref)
            except KeyError:
                problems.append(f'{name}: {ref} nao existe na Foundation')

    for role, ref in SHARED.items():
        name = f'icon-button-{role}'
        alias[name] = ref
        try:
            resolved[name] = resolve_foundation(ref)
        except KeyError:
            problems.append(f'{name}: {ref} nao existe na Foundation')

    # caixa derivada, so para conferencia - nao vira token. Quadrada: o mesmo
    # numero e largura e altura.
    boxes = {}
    for size in SIZE:
        pad = resolve_foundation(SIZE[size]['padding'])
        icon = resolve_foundation(SIZE[size]['icon-size'])
        boxes[size] = pad * 2 + icon

    print('=' * 70)
    print('CAMADA DE TOKENS DO ICON BUTTON')
    print('=' * 70)
    for name in sorted(alias):
        ref = alias[name]
        tag = 'transparente' if ref == TRANSPARENT else f'-> {ref}'
        print(f'  {name:<39} {tag}')
    print('-' * 70)
    for size in SIZE:
        print(f'caixa derivada {size}: {boxes[size]}x{boxes[size]}px  (padding x2 + icone)')

    # conferencia de paridade, nao portao: o Icon Button so serve ao lado do
    # Button se as duas caixas fecharem no mesmo numero.
    bh = button_heights()
    if bh is None:
        print('paridade com o Button: nao conferida (button/tokens.json ausente)')
    else:
        for size in SIZE:
            alvo = bh.get(size)
            sinal = '=' if alvo == boxes[size] else 'DIFERE DE'
            print(f'paridade {size}: caixa {boxes[size]}px {sinal} altura do Button {alvo}px')

    if PENDING:
        for k, v in PENDING.items():
            print(f'pendente: {k} - {v}')
    else:
        print('pendencias: nenhuma')
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
            'component': 'Icon Button',
            'version': '0.1.0',
            'foundation': FOUND['meta']['version'],
            'figmaNode': '35:460',
            'variants': list(COLOR),
            'sizes': list(SIZE),
            'states': ['default', 'hover', 'pressed', 'focus', 'disabled', 'loading'],
            'nota': (
                'O piso de contraste aqui e 3:1 (WCAG 1.4.11, nao-textual): o portador '
                'do sentido e um icone, nao um rotulo. Por isso este componente nao tem '
                'excecao de marca, ao contrario do Button. O estado loading nao gera '
                'token - o spinner usa currentColor, border.width.2 e radius.full.'
            ),
        },
        'alias': alias,
        'resolved': resolved,
        'derived': {'box': boxes},
        'pending': PENDING,
    }
    json.dump(out, open(os.path.join(HERE, 'tokens.json'), 'w'), indent=2, ensure_ascii=False)
    print('\ncomponents/icon-button/tokens.json escrito')
    write_css(alias, boxes)
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
    if ref.startswith('iconSize.'):
        return f'var(--al-icon-size-{ref.split(".")[1]})'
    return f'var(--al-{ref})'          # semantico de cor


def write_css(alias, boxes):
    L = []
    w = L.append
    w('/* AL Design System - tokens do Icon Button')
    w(' * GERADO por components/icon-button/tokens.py. Nao editar a mao.')
    w(' *')
    w(' * Nao ha bloco de tema aqui, e isso e o ponto: cada token aponta para um')
    w(' * semantico, e o tema troca no :root - o mesmo elemento onde estes alias')
    w(' * sao declarados. Entao o :root re-substitui todos eles de uma vez.')
    w(' *')
    w(' * Cuidado: substituicao de custom property acontece no elemento onde ela e')
    w(' * DECLARADA, nao no ponto de uso. Tematizar um container solto exige')
    w(' * re-declarar esta camada dentro dele - ver site/site.py.')
    w(' */')
    w('')
    w(':root {')

    for variant in COLOR:
        w('')
        w(f'  /* {variant} */')
        for role, ref in COLOR[variant].items():
            w(f'  --al-icon-button-{variant}-{role}: {css_ref(ref)};')
        w(f'  --al-icon-button-{variant}-ring: {css_ref(RING[variant])};')

    for size, roles in SIZE.items():
        w('')
        w(f'  /* tamanho {size} - caixa resultante: {boxes[size]}x{boxes[size]}px */')
        for role, ref in roles.items():
            w(f'  --al-icon-button-{size}-{role}: {css_ref(ref)};')

    w('')
    w('  /* compartilhado */')
    for role, ref in SHARED.items():
        w(f'  --al-icon-button-{role}: {css_ref(ref)};')
    w('}')
    w('')

    path = os.path.join(HERE, 'al-icon-button-tokens.css')
    open(path, 'w').write('\n'.join(L))
    print(f'components/icon-button/al-icon-button-tokens.css escrito ({os.path.getsize(path)} bytes)')


if __name__ == '__main__':
    sys.exit(run())
