"""
Camada de tokens do Avatar.

Regra unica desta camada: nada aqui inventa valor. Todo token aponta para um
token da Foundation pelo NOME. O portao no fim do arquivo recusa qualquer
coisa que seja um valor solto - hex, px, numero.

Nomenclatura:
  codigo -> avatar-md-icon-size      (hifen)
  Figma  -> avatar/md/icon-size      (pasta)
Sao camadas diferentes. Nunca colapsar uma na outra.

POR QUE A COR NAO REPETE POR TAMANHO

  O Tag e o Button tem cor por variante porque a variante MUDA a cor (primary
  e laranja, danger e vermelho). O Avatar so tem uma dimensao de variante de
  verdade - o tamanho - e o tamanho nao muda cor nenhuma: os tres tamanhos
  usam o mesmo fundo e a mesma tinta. Por isso `avatar-bg`, `avatar-label` e
  `avatar-icon` sao tres tokens no total, nao nove. Nove tokens repetindo o
  mesmo valor tres vezes seriam tres lugares para o mesmo valor divergir por
  engano.

`avatar-label` E `avatar-icon` SAO TOKENS SEPARADOS MESMO APONTANDO PRO MESMO ALIAS

  Hoje os dois resolvem em `text-primary` e por isso ficam pixel-identicos.
  Mas sao papeis diferentes - um e texto (iniciais), o outro e tinta de icone
  vetorial - e o achado 1 da auditoria foi justamente a tinta do icone tendo
  ficado presa num token de FUNDO (`bg-inverse`) que so coincidia em valor.
  Separar os nomes agora e o que impede a mesma armadilha de voltar: se um dia
  a tinta do icone precisar divergir da tinta do texto, o rebind e local, e
  ninguem tem que caçar todo lugar que usava `avatar-label` para saber se
  aquele uso era texto ou era icone.

NAO HA TOKEN DE BORDA

  Diferente do Tag, o Avatar nao tem traco em variante nenhuma. Nao e uma
  omissao documentada por engano - e a forma nao usar contorno.

DOIS PISOS DE CONTRASTE, NO MESMO PAR DE COR

  `avatar-label` (iniciais) e texto: piso 4.5:1 do 1.4.3. `avatar-icon`
  (glifo vetorial) e nao-textual: piso 3:1 do 1.4.11, regra ja fixada com o
  Icon e o Icon Button. Os dois resolvem no mesmo hex hoje porque os dois
  apontam pra `text-primary`, entao os dois passam os dois pisos com folga -
  mas o portao mede cada um contra o piso que e dele, nao contra o mais
  facil.

ZERO EXCECAO DE CONTRASTE

  Terceiro componente do AL a fechar em zero excecoes, depois do Tag. Nao
  cria par novo nenhum: `text-primary` sobre `bg-subtle` ja e um dos 80 pares
  medidos pela Foundation (12.54:1 claro, 9.98:1 escuro).

DIAMETRO NAO E TOKEN

  32 / 48 / 64 nascem de `padding x2 + icon-size` do mesmo tamanho (8x2+16,
  12x2+24, 16x2+32) - e essa conta bate nos tres tipos (Initials, Icon,
  Photo) porque os tres ocupam a mesma caixa quadrada. Tokenizar o diametro
  seria guardar duas vezes a mesma informacao com duas chances de divergir,
  igual a altura do Button e do Tag.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'foundation'))

from build import SEM                     # noqa: E402
from color import cr                      # noqa: E402

FOUND = json.load(open(os.path.join(ROOT, 'tokens.json')))   # noqa: E402

# --------------------------------------------------------------- cor
# Compartilhada pelos tres tamanhos - ver nota no cabecalho.
COLOR = {
    'bg':    'bg-subtle',
    'label': 'text-primary',   # iniciais - piso de texto, 4.5:1
    'icon':  'text-primary',   # glifo vetorial - piso nao-textual, 3:1
}

# ------------------------------------------------------------ geometria
SIZE = {
    'sm': {'padding': 'space.8',  'icon-size': 'iconSize.16', 'font': 'type.styles.label-sm'},
    'md': {'padding': 'space.12', 'icon-size': 'iconSize.24', 'font': 'type.styles.heading-xs'},
    'lg': {'padding': 'space.16', 'icon-size': 'iconSize.32', 'font': 'type.styles.heading-sm'},
}

SHARED = {
    'radius': 'radius.full',
}

PENDING = {}   # nenhuma pendencia nesta versao - ver docstring


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


def bind_color(name, ref, alias, resolved, problems):
    """Um token de cor: registra o alias e resolve nos dois temas, ou reprova."""
    alias[name] = ref
    if ref.startswith('#'):
        problems.append(f'{name}: hex solto ({ref}) - todo valor de cor nasce alias do semantico')
        return
    if ref not in SEM:
        problems.append(f'{name}: aponta para {ref}, que nao existe na camada semantica')
        return
    light, dark = SEM[ref]
    resolved[name] = {'light': light, 'dark': dark}


def contrast_rows():
    """As duas combinacoes renderizadas do componente - rotulo e icone contra
    o fundo - medidas com o motor da Foundation, cada uma contra o piso que e
    dela (texto 4.5:1, nao-textual 3:1)."""
    rows = []
    pisos = {'label': 4.5, 'icon': 3.0}
    for role, min_ratio in pisos.items():
        fg_ref = COLOR[role]
        bg_ref = COLOR['bg']
        for theme, i in (('light', 0), ('dark', 1)):
            rows.append({
                'theme': theme, 'what': role,
                'fg': fg_ref, 'bg': bg_ref,
                'ratio': round(cr(SEM[fg_ref][i], SEM[bg_ref][i]), 2),
                'min': min_ratio,
            })
    for r in rows:
        r['pass'] = r['ratio'] >= r['min']
    return rows


def run():
    alias, resolved, problems = {}, {}, []

    for role, ref in COLOR.items():
        bind_color(f'avatar-{role}', ref, alias, resolved, problems)

    for size, roles in SIZE.items():
        for role, ref in roles.items():
            name = f'avatar-{size}-{role}'
            alias[name] = ref
            try:
                resolved[name] = resolve_foundation(ref)
            except KeyError:
                problems.append(f'{name}: {ref} nao existe na Foundation')

    for role, ref in SHARED.items():
        name = f'avatar-{role}'
        alias[name] = ref
        try:
            resolved[name] = resolve_foundation(ref)
        except KeyError:
            problems.append(f'{name}: {ref} nao existe na Foundation')

    # Diametro derivado - NAO vira token. Ver nota no cabecalho.
    diameters = {}
    for size in SIZE:
        pad = resolve_foundation(SIZE[size]['padding'])
        icon = resolve_foundation(SIZE[size]['icon-size'])
        diameters[size] = pad * 2 + icon

    rows = contrast_rows()
    fails = [r for r in rows if not r['pass']]

    print('=' * 74)
    print('CAMADA DE TOKENS DO AVATAR')
    print('=' * 74)
    for name in sorted(alias):
        print(f'  {name:<28} -> {alias[name]}')
    print('-' * 74)
    for size in SIZE:
        print(f'diametro derivado {size}: {diameters[size]}px  '
              f'(padding x2 + icon-size; mesma caixa nos tres tipos)')
    print('-' * 74)
    print(f'contraste: {len(rows)} medicoes  |  passam: {len(rows) - len(fails)}  |  '
          f'reprovam: {len(fails)}  |  excecoes: 0')
    pior = min(rows, key=lambda r: r['ratio'] / r['min'])
    print(f'pior margem: {pior["what"]} ({pior["theme"]}) = {pior["ratio"]}:1 '
          f'contra piso {pior["min"]}')
    if not PENDING:
        print('pendencias: nenhuma')
    print('-' * 74)

    if problems:
        print(f'{len(problems)} TOKEN(S) REPROVAM O PORTAO DE ALIAS:')
        for p in problems:
            print('   ', p)
        return 1
    if fails:
        print(f'{len(fails)} COMBINACAO(OES) REPROVAM O PORTAO DE CONTRASTE:')
        for f in fails:
            print(f'    {f["what"]} ({f["theme"]}): {f["ratio"]}:1 < {f["min"]}')
        return 1

    print(f'{len(alias)} tokens, todos alias da Foundation. 0 valores soltos.')

    out = {
        'meta': {
            'component': 'Avatar',
            'version': '0.1.0',
            'foundation': FOUND['meta']['version'],
            'figmaNode': '162:512',
            'types': ['initials', 'icon', 'photo'],
            'sizes': list(SIZE),
            'states': ['default'],
            'nota': (
                'Avatar estatico por padrao: fora da ordem de tabulacao, sem hover, '
                'sem foco proprio. Quem precisar de avatar clicavel embrulha num '
                'acionavel que ja tem anel (Icon Button, link) - o Avatar em si nunca '
                'ganha estado. Cor compartilhada pelos tres tamanhos; forma so circulo '
                'nesta versao (quadrado/organizacao fica fora, sem conceito de '
                'organizacao no AL ainda). Zero excecao de contraste.'
            ),
        },
        'alias': alias,
        'resolved': resolved,
        'derived': {'diameter': diameters},
        'contrast': rows,
        'pending': PENDING,
    }
    json.dump(out, open(os.path.join(HERE, 'tokens.json'), 'w'), indent=2, ensure_ascii=False)
    print('\ncomponents/avatar/tokens.json escrito')
    write_css(alias, diameters)
    return 0


# ---------------------------------------------------------------- css
def css_ref(ref):
    """Traduz a referencia da Foundation para a custom property equivalente."""
    if ref.startswith('space.'):
        return f'var(--al-space-{ref.split(".")[1]})'
    if ref.startswith('radius.'):
        return f'var(--al-radius-{ref.split(".")[1]})'
    if ref.startswith('iconSize.'):
        return f'var(--al-icon-size-{ref.split(".")[1]})'
    if ref.startswith('type.styles.'):
        return ref.split('.')[2]          # tratado a parte: um estilo vira quatro vars
    return f'var(--al-{ref})'             # semantico de cor


def _size_key(font_size):
    """Acha o nome do degrau (xs, sm, ..., 2xl) cujo font-size bate, na
    propria escala da Foundation. `type.size` nao tem valor repetido - dá pra
    resolver por valor com seguranca.

    O nome de line-height NAO pode nascer do mesmo truque: `leading.lg` e
    `leading.xl` valem os dois 28px, entao buscar por VALOR e ambiguo e pode
    emitir a variavel errada sem mudar nada na tela - erro silencioso. A
    saida e usar o MESMO nome de degrau do font-size (todo estilo de texto da
    Foundation casa um size e um leading do mesmo degrau nomeado)."""
    for key, v in FOUND['type']['size'].items():
        if v == font_size:
            return key
    raise KeyError(f'type.size com valor {font_size} nao existe na Foundation')


def write_css(alias, diameters):
    L = []
    w = L.append
    w('/* AL Design System - tokens do Avatar')
    w(' * GERADO por components/avatar/tokens.py. Nao editar a mao.')
    w(' *')
    w(' * Nao ha bloco de tema aqui, e isso e o ponto: cada token aponta para um')
    w(' * semantico, e o tema troca no :root - o mesmo elemento onde estes alias')
    w(' * sao declarados. Entao o :root re-substitui todos eles de uma vez.')
    w(' *')
    w(' * Cor e compartilhada pelos tres tamanhos: o tamanho nao muda fundo nem')
    w(' * tinta, so geometria.')
    w(' */')
    w('')
    w(':root {')
    w('')
    w('  /* cor - compartilhada pelos tres tamanhos */')
    for role, ref in COLOR.items():
        w(f'  --al-avatar-{role}: {css_ref(ref)};')

    for size, roles in SIZE.items():
        w('')
        w(f'  /* tamanho {size} - diametro resultante: {diameters[size]}px */')
        for role, ref in roles.items():
            if ref.startswith('type.styles.'):
                style = resolve_foundation(ref)
                key = _size_key(style[1])
                w(f'  --al-avatar-{size}-font-size: var(--al-font-size-{key});')
                w(f'  --al-avatar-{size}-line-height: var(--al-line-height-{key});')
                w(f'  --al-avatar-{size}-font-weight: {style[3]};')
                w(f'  --al-avatar-{size}-tracking: {style[4]};')
                continue
            w(f'  --al-avatar-{size}-{role}: {css_ref(ref)};')

    w('')
    w('  /* compartilhado */')
    for role, ref in SHARED.items():
        w(f'  --al-avatar-{role}: {css_ref(ref)};')
    w('}')
    w('')

    path = os.path.join(HERE, 'al-avatar-tokens.css')
    open(path, 'w').write('\n'.join(L))
    print(f'components/avatar/al-avatar-tokens.css escrito ({os.path.getsize(path)} bytes)')


if __name__ == '__main__':
    sys.exit(run())
