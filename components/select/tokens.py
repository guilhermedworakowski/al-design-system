"""
Camada de tokens do Select.

Regra unica desta camada: nada aqui inventa valor. Todo token aponta para um
token da Foundation pelo NOME. O portao no fim do arquivo recusa qualquer
coisa que seja um valor solto - hex, px, numero.

Nomenclatura:
  codigo -> select-border-hover      (hifen)
  Figma  -> select/border/hover      (pasta)
Sao camadas diferentes. Nunca colapsar uma na outra.

E O `<select>` NATIVO

  A lista de opcoes e desenhada pelo navegador e pelo sistema operacional. O
  componente entrega so o gatilho fechado. Isso nao e escopo faltando: e a
  mesma distincao que o Carbon faz entre *Select* (nativo) e *Dropdown* /
  *ComboBox* (desenhados). Consequencia pratica desta camada: nao existe
  token de painel, de item de opcao nem de item selecionado, porque nada
  disso e nosso para pintar.

A BORDA E O EIXO QUE CARREGA O ESTADO

  O fundo do campo nao muda entre repouso, hover, active, foco e erro - so a
  borda muda. Por isso ha um `bg` e seis `border-*`. O unico estado que mexe
  no fundo e o disabled, e ele mexe porque precisa parar de parecer um campo
  onde se digita.

`border-active` E `border-focus` APONTAM PRO MESMO ALIAS, E SAO DOIS TOKENS

  Gui fechou na etapa 1 que active (clique que abre a lista) e foco (chegada
  por Tab) sao estados distintos. Hoje os dois resolvem em `border-brand` e
  ficam pixel-identicos. Manter dois nomes e o que permite um divergir do
  outro depois sem virar mudanca quebrada - e o que impede alguem de ler o
  CSS e concluir que os dois estados sao a mesma coisa.

O SELECT E O PRIMEIRO COMPONENTE COM TOKEN DE COR DE ICONE

  No Button e no Tag o icone e `currentColor`: herda a cor do rotulo e por
  isso nao precisa de token. Aqui nao da. No repouso o texto do campo e
  `text-placeholder` (#717171) e a seta e `text-primary` (#292929) - duas
  cores diferentes dentro da mesma caixa. Se a seta herdasse, ela clarearia
  junto com o placeholder, que nao e o desenho. Dai `select-icon` e
  `select-icon-disabled` existirem.

  Piso da seta e 3:1 do 1.4.11 (nao-textual), nao 4.5:1 do 1.4.3 - mesma
  regra ja fixada com o Icon e o Icon Button.

PLACEHOLDER x VALOR NAO E ESTADO DE INTERACAO

  `select-text-placeholder` e `select-text-value` sao dois tokens que NAO
  dependem dos sete estados. No Figma o texto escuro aparece no Active, no
  Error e no focusError, e o cinza no Default, no Hover e no focusDefault -
  mas isso e so o que cada mockup escolheu mostrar. Na tela, quem escolheu
  uma opcao e tirou o mouse volta ao repouso COM o valor escolhido, e o texto
  continua escuro. Em CSS a troca e `:has(option[value=""]:checked)` - "ainda
  esta no placeholder" - e nunca `:hover` ou `:active`.

ALTURA NAO E TOKEN

  48 = padding-y x2 + entrelinha do texto (12+24+12), com a borda de 1px
  sobreposta ao padding - em CSS, `padding: calc(12px - 1px)`. E a mesma
  convencao do Button e do Tag. Tokenizar a altura seria fixar em dois
  lugares a mesma decisao, com duas chances de divergir.

  A altura total tambem e derivada: rotulo 24 + gap 8 + campo 48 = 80, e 104
  quando o texto de apoio aparece (+8 +16).

A MARCA "(OPCIONAL)" MARCA O INVERSO DO HABITUAL

  Gui fechou em 17/09/2026 que o AL marca o campo OPCIONAL, nao o obrigatorio:
  quem nao tem a marca e obrigatorio. E a escola oposta a do asterisco do
  Polaris, e ela ganha quando a maioria dos campos do formulario e
  obrigatoria - marca-se a minoria. `select-optional` e `select-optional-font`
  existem so por isso; a marca fica ao lado do rotulo, em `Body/sm`, uma
  entrelinha menor que o rotulo de proposito, para nao competir com ele.

  Nao ha token de "obrigatorio": a ausencia da marca E o obrigatorio, e
  ausencia nao se tokeniza.

O GAP E UM SO NOS DOIS EIXOS

  `select-gap` vale para a pilha vertical (rotulo -> campo -> apoio) E para o
  espaco horizontal entre o rotulo e a marca "(Opcional)". Os dois sao 8 e os
  dois separam partes do MESMO componente. Dois tokens com o mesmo valor
  seriam dois lugares para o mesmo respiro divergir por engano. Se um dia
  precisarem divergir, ai sim vira `gap-x` e `gap-y`.

LARGURA NAO E TOKEN

  O campo ocupa 100% do conteiner. Formulario decide largura; componente nao.

CINCO EXCECOES DECLARADAS DE CONTRASTE

  Todas em `pending`, todas nomeadas, nenhuma silenciosa. Ver a docstring de
  PENDING logo abaixo.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'foundation'))

from build import SEM                     # noqa: E402
from color import cr                      # noqa: E402

FOUND = json.load(open(os.path.join(ROOT, 'tokens.json')))   # noqa: E402

# --------------------------------------------------------------- cor
# Um tamanho, sem variante: a lista e plana. O que varia e o estado, e o
# estado quase sempre mexe so na borda.
COLOR = {
    'bg':               'bg-surface-raised',
    'bg-disabled':      'bg-disabled',

    'border':           'border-default',
    'border-hover':     'border-strong',
    'border-active':    'border-brand',
    'border-focus':     'border-brand',
    'border-error':     'border-danger',
    'border-disabled':  'border-default',

    'text-placeholder': 'text-placeholder',
    'text-value':       'text-primary',
    'text-disabled':    'text-disabled',

    'label':            'text-primary',
    'label-error':      'text-danger',
    'label-disabled':   'text-disabled',

    'help':             'text-secondary',
    'help-error':       'text-danger',

    'optional':         'text-secondary',

    'icon':             'text-primary',    # glifo vetorial - piso 3:1
    'icon-disabled':    'text-disabled',
}

# O token aponta para a SOMBRA COMPOSTA, nao para a cor crua - mesma regra do
# `button-*-ring`. A cor so e extraida para medicao, no RING_INK abaixo.
RING = {
    'ring':       'focusRing.default',
    'ring-error': 'focusRing.error',
}

# De onde sai a cor de cada anel quando o portao precisa medir contraste.
# Nao vira token: seria o mesmo valor guardado duas vezes.
RING_INK = {
    'ring':       'shadow-focus-default',
    'ring-error': 'shadow-focus-error',
}

# ------------------------------------------------------------ geometria
GEOM = {
    'padding-x':    'space.12',
    'padding-y':    'space.12',
    'gap':          'space.8',       # rotulo -> campo -> texto de apoio
    'radius':       'radius.lg',
    'border-width': 'border.width.1',
    'icon-size':    'iconSize.24',
}

TYPE = {
    'font':          'type.styles.body-md',
    'label-font':    'type.styles.body-md',
    'optional-font': 'type.styles.body-sm',
    'help-font':     'type.styles.caption',
}

PENDING = {
    'borda-abaixo-de-3-1': (
        'A borda em repouso e no disabled usa `border-default`: 1.57:1 no claro e '
        '2.42:1 no escuro, abaixo dos 3:1 do WCAG 1.4.11. Decisao consciente de Gui '
        'em 17/09/2026, depois de ver os numeros. O criterio nao falha quando a borda '
        'nao e o unico meio de perceber o componente, e aqui nao e: o campo tem rotulo '
        'visivel acima e texto dentro. Hover (4.88:1), active e foco (3.34:1) e erro '
        '(5.38:1) passam todos, entao a borda fraca existe so no repouso. '
        'NAO "corrigir" sem falar com ele.'
    ),
    'disabled-abaixo-de-aa': (
        'Rotulo, texto e seta no disabled ficam entre 1.59:1 e 3.64:1. Isencao do WCAG '
        '1.4.3 para componente inativo - mesma excecao permanente que o Button e o Tag '
        'ja carregam. Subir esse contraste faz o desabilitado parecer clicavel.'
    ),
}

CANVAS = 'bg-canvas'   # nao e token do Select: e a tela onde ele e colocado

# As combinacoes que o componente realmente renderiza: cada papel contra o
# fundo em que ele vive de verdade. Rotulo, texto de apoio e anel de foco
# vivem FORA do campo, entao medem contra a tela; o que esta dentro mede
# contra o fundo do campo. Sem isso o portao mediria par de token no vacuo -
# e no tema escuro a diferenca e real: a tela e #181818 e o campo e #3E3E3E.
#
# A BORDA TEM DUAS SUPERFICIES VIZINHAS - a tela por fora e o fundo do campo
# por dentro - e precisa se separar das DUAS para desenhar um limite. Por
# isso o fundo dela e uma tupla: o portao mede contra cada uma e guarda a
# PIOR. Medir so contra a tela deixaria passar uma borda que some por dentro.
#
# (papel, token do select, fundo(s), piso, chave da excecao em PENDING)
COMBOS = [
    ('rotulo',           'label',            'canvas',                   4.5, None),
    ('rotulo-erro',      'label-error',      'canvas',                   4.5, None),
    ('rotulo-disabled',  'label-disabled',   'canvas',                   4.5, 'disabled-abaixo-de-aa'),
    ('placeholder',      'text-placeholder', 'bg',                       4.5, None),
    ('valor',            'text-value',       'bg',                       4.5, None),
    ('texto-disabled',   'text-disabled',    'bg-disabled',              4.5, 'disabled-abaixo-de-aa'),
    ('chevron',          'icon',             'bg',                       3.0, None),
    ('chevron-disabled', 'icon-disabled',    'bg-disabled',              3.0, 'disabled-abaixo-de-aa'),
    ('opcional',         'optional',         'canvas',                   4.5, None),
    ('apoio',            'help',             'canvas',                   4.5, None),
    ('apoio-erro',       'help-error',       'canvas',                   4.5, None),
    ('borda-repouso',    'border',           ('canvas', 'bg'),           3.0, 'borda-abaixo-de-3-1'),
    ('borda-hover',      'border-hover',     ('canvas', 'bg'),           3.0, None),
    ('borda-active',     'border-active',    ('canvas', 'bg'),           3.0, None),
    ('borda-focus',      'border-focus',     ('canvas', 'bg'),           3.0, None),
    ('borda-erro',       'border-error',     ('canvas', 'bg'),           3.0, None),
    ('borda-disabled',   'border-disabled',  ('canvas', 'bg-disabled'),  3.0, 'disabled-abaixo-de-aa'),
    ('anel-foco',        'ring',             'canvas',                   3.0, None),
    ('anel-foco-erro',   'ring-error',       'canvas',                   3.0, None),
]


# ---------------------------------------------------------------- portao
def resolve_foundation(path):
    """Segue um caminho pontuado dentro de tokens.json. Levanta se nao existir.

    type.styles e uma lista de tuplas (nome, size, leading, weight, ...), nao
    um dicionario - entao o ultimo trecho do caminho casa contra o nome do
    estilo.
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


def ink(role):
    """O semantico de cor por tras de um papel - seguindo o anel ate a cor.

    `canvas` nao e papel do Select: e a tela em que ele e colocado. Fica de
    fora do COLOR de proposito - o componente nao pinta o fundo da pagina.
    """
    if role == 'canvas':
        return CANVAS
    if role in RING_INK:
        return RING_INK[role]
    return COLOR[role]


def contrast_rows():
    """Mede cada combinacao renderizada nos dois temas, cada uma contra o piso
    que e dela: texto 4.5:1 do 1.4.3, borda e glifo 3:1 do 1.4.11."""
    rows = []
    for what, fg_role, bg_spec, min_ratio, exc in COMBOS:
        fg_ref = ink(fg_role)
        bg_roles = bg_spec if isinstance(bg_spec, tuple) else (bg_spec,)
        for theme, i in (('light', 0), ('dark', 1)):
            # quando ha mais de uma superficie vizinha, vale a PIOR
            medidas = [(round(cr(SEM[fg_ref][i], SEM[ink(b)][i]), 2), ink(b))
                       for b in bg_roles]
            ratio, bg_ref = min(medidas)
            rows.append({
                'theme': theme, 'what': what,
                'fg': fg_ref, 'bg': bg_ref,
                'ratio': ratio, 'min': min_ratio,
                'pass': ratio >= min_ratio,
                'exception': exc,
            })
    return rows


def run():
    alias, resolved, problems = {}, {}, []

    for role, ref in COLOR.items():
        name = f'select-{role}'
        alias[name] = ref
        if ref.startswith('#'):
            problems.append(f'{name}: hex solto ({ref}) - todo valor de cor nasce alias do semantico')
            continue
        if ref not in SEM:
            problems.append(f'{name}: aponta para {ref}, que nao existe na camada semantica')
            continue
        light, dark = SEM[ref]
        resolved[name] = {'light': light, 'dark': dark}

    for role, ref in RING.items():
        name = f'select-{role}'
        alias[name] = ref
        try:
            v = resolve_foundation(ref)
            resolved[name] = {'light': v['light'], 'dark': v['dark']}
        except KeyError:
            problems.append(f'{name}: {ref} nao existe na Foundation')

    for group in (GEOM, TYPE):
        for role, ref in group.items():
            name = f'select-{role}'
            alias[name] = ref
            try:
                resolved[name] = resolve_foundation(ref)
            except KeyError:
                problems.append(f'{name}: {ref} nao existe na Foundation')

    # derivadas - conferencia, nao token. Ver nota no cabecalho.
    pad_y = resolve_foundation(GEOM['padding-y'])
    gap = resolve_foundation(GEOM['gap'])
    field_line = resolve_foundation(TYPE['font'])[2]
    label_line = resolve_foundation(TYPE['label-font'])[2]
    help_line = resolve_foundation(TYPE['help-font'])[2]
    field_h = pad_y * 2 + field_line
    derived = {
        'field-height': field_h,
        'total-height': label_line + gap + field_h,
        'total-height-with-help': label_line + gap + field_h + gap + help_line,
    }

    rows = contrast_rows()
    fails = [r for r in rows if not r['pass'] and not r['exception']]
    excs = [r for r in rows if not r['pass'] and r['exception']]

    print('=' * 74)
    print('CAMADA DE TOKENS DO SELECT')
    print('=' * 74)
    for name in sorted(alias):
        print(f'  {name:<26} -> {alias[name]}')
    print('-' * 74)
    print(f'altura do campo derivada: {derived["field-height"]}px  '
          f'(padding-y x2 + entrelinha; borda sobreposta ao padding)')
    print(f'altura total: {derived["total-height"]}px  '
          f'| com texto de apoio: {derived["total-height-with-help"]}px')
    # conferencia, nao portao: a seta deve bater com a entrelinha do texto -
    # e o que faz a seta nao mexer na altura do campo
    icon = resolve_foundation(GEOM['icon-size'])
    if icon != field_line:
        print(f'  ATENCAO: icon-size {icon} != entrelinha {field_line} - a seta mexe na altura')
    print('-' * 74)
    print(f'contraste: {len(rows)} medicoes  |  passam: {len(rows) - len(fails) - len(excs)}  |  '
          f'excecoes declaradas: {len(excs)}  |  reprovas: {len(fails)}')
    limpas = [r for r in rows if r['pass']]
    pior = min(limpas, key=lambda r: r['ratio'] / r['min'])
    print(f'pior margem entre as que passam: {pior["what"]} ({pior["theme"]}) = '
          f'{pior["ratio"]}:1 contra piso {pior["min"]}')
    for chave in PENDING:
        n = sum(1 for r in excs if r['exception'] == chave)
        print(f'  excecao "{chave}": {n} medicoes')
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
            'component': 'Select',
            'version': '0.1.0',
            'foundation': FOUND['meta']['version'],
            'figmaNode': '227:204',
            'variants': [],
            'sizes': ['md'],
            'states': ['default', 'hover', 'active', 'error',
                       'focus-error', 'disabled', 'focus'],
            'nota': (
                'E o <select> NATIVO: a lista de opcoes e desenhada pelo navegador, '
                'entao nao ha token de painel, de opcao nem de item selecionado. '
                'Um tamanho so (48px), por escolha declarada - como o lg que ficou de '
                'fora do Button. A borda e o eixo que carrega o estado: o fundo so muda '
                'no disabled. `border-active` e `border-focus` apontam pro mesmo alias '
                'de proposito - clique e Tab sao estados distintos que hoje coincidem. '
                'Primeiro componente do AL com token de cor de icone, porque a seta nao '
                'pode herdar a cor do placeholder. A marca "(Opcional)" ao lado do '
                'rotulo marca o INVERSO do habitual: quem nao tem a marca e '
                'obrigatorio - nao existe token de obrigatorio. Cinco excecoes de '
                'contraste declaradas em pending.'
            ),
        },
        'alias': alias,
        'resolved': resolved,
        'derived': derived,
        'contrast': rows,
        'pending': PENDING,
    }
    json.dump(out, open(os.path.join(HERE, 'tokens.json'), 'w'), indent=2, ensure_ascii=False)
    print('\ncomponents/select/tokens.json escrito')
    write_css(alias, derived)
    return 0


# ---------------------------------------------------------------- css
def css_ref(ref):
    """Traduz a referencia da Foundation para a custom property equivalente."""
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


def _size_key(font_size):
    """Acha o nome do degrau cujo font-size bate, na escala da Foundation.

    O nome de line-height NAO pode nascer do mesmo truque: `leading.lg` e
    `leading.xl` valem os dois 28px, entao buscar por VALOR e ambiguo e pode
    emitir a variavel errada sem mudar nada na tela - erro silencioso. A saida
    e usar o MESMO nome de degrau do font-size.
    """
    for key, v in FOUND['type']['size'].items():
        if v == font_size:
            return key
    raise KeyError(f'type.size com valor {font_size} nao existe na Foundation')


def write_css(alias, derived):
    L = []
    w = L.append
    w('/* AL Design System - tokens do Select')
    w(' * GERADO por components/select/tokens.py. Nao editar a mao.')
    w(' *')
    w(' * Nao ha bloco de tema aqui, e isso e o ponto: cada token aponta para um')
    w(' * semantico, e o tema troca no :root - o mesmo elemento onde estes alias')
    w(' * sao declarados. Entao o :root re-substitui todos eles de uma vez.')
    w(' *')
    w(f' * Altura do campo: {derived["field-height"]}px derivados, sem token.')
    w(' */')
    w('')
    w(':root {')

    w('')
    w('  /* fundo - so o disabled muda */')
    for role in ('bg', 'bg-disabled'):
        w(f'  --al-select-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* borda - o eixo que carrega o estado */')
    for role in ('border', 'border-hover', 'border-active', 'border-focus',
                 'border-error', 'border-disabled'):
        w(f'  --al-select-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* texto dentro do campo - placeholder x valor NAO e estado de interacao */')
    for role in ('text-placeholder', 'text-value', 'text-disabled'):
        w(f'  --al-select-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* rotulo, marca de opcional e apoio - vivem fora do campo, sobre a tela */')
    for role in ('label', 'label-error', 'label-disabled',
                 'optional', 'help', 'help-error'):
        w(f'  --al-select-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* seta - nao herda a cor do texto, ver cabecalho do tokens.py */')
    for role in ('icon', 'icon-disabled'):
        w(f'  --al-select-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* anel de foco - aponta para a sombra composta, nao para a cor crua */')
    for role, ref in RING.items():
        w(f'  --al-select-{role}: {css_ref(ref)};')

    w('')
    w('  /* geometria */')
    for role, ref in GEOM.items():
        w(f'  --al-select-{role}: {css_ref(ref)};')

    w('')
    w('  /* tipografia - um estilo vira quatro vars */')
    for role, ref in TYPE.items():
        style = resolve_foundation(ref)
        key = _size_key(style[1])
        prefix = f'--al-select-{role}'.replace('-font', '')
        if role == 'font':
            prefix = '--al-select'
        w(f'  {prefix}-font-size: var(--al-font-size-{key});')
        w(f'  {prefix}-line-height: var(--al-line-height-{key});')
        w(f'  {prefix}-font-weight: {style[3]};')
        w(f'  {prefix}-tracking: {style[4]};')

    w('}')
    w('')

    # Os grupos acima sao listas escritas a mao, para o CSS sair agrupado e
    # comentado. O preco de escrever a mao e esquecer um papel novo - foi o que
    # aconteceu quando `optional` entrou. Esta trava recusa a geracao se algum
    # token de cor nao chegou ao arquivo: lista errada vira build quebrado, nao
    # variavel faltando em silencio.
    texto = '\n'.join(L)
    faltando = [r for r in COLOR if f'--al-select-{r}:' not in texto]
    if faltando:
        raise AssertionError(
            'papeis de cor fora do CSS (alguma lista de grupo em write_css nao '
            f'foi atualizada): {faltando}')

    path = os.path.join(HERE, 'al-select-tokens.css')
    open(path, 'w').write(texto)
    print(f'components/select/al-select-tokens.css escrito ({os.path.getsize(path)} bytes)')


if __name__ == '__main__':
    sys.exit(run())
