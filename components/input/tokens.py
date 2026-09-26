"""
Camada de tokens do Input.

Regra unica desta camada: nada aqui inventa valor. Todo token aponta para um
token da Foundation pelo NOME. O portao no fim do arquivo recusa qualquer
coisa que seja um valor solto - hex, px, numero.

Nomenclatura:
  codigo -> input-border-hover      (hifen)
  Figma  -> input/border/hover      (pasta)
Sao camadas diferentes. Nunca colapsar uma na outra.

CAMPO DE TEXTO DE UMA LINHA

  Cobre `type` text, email, url e tel. Senha vira componente proprio
  (Password); number e search ficam fora desta versao por escolha - e a mesma
  separacao do Carbon, que trata PasswordInput, NumberInput e Search como
  componentes a parte. Fora tambem, por escolha: warning, icone a esquerda,
  botao de limpar e tamanhos extras.

SETE ESTADOS, E DOIS QUE FICARAM DE FORA DE PROPOSITO

  Default, Hover, Error, focusError, Disabled, focusDefault, readOnly.

  Nao existe Active. No Select o clique abre a lista, e por isso Active tinha
  sentido; aqui nao ha nada que abre. E campo de texto SEMPRE casa
  `:focus-visible`, inclusive com clique de mouse - a spec manda isso para todo
  elemento que aceita digitacao. A borda laranja de 1px do Active duraria so o
  instante do botao pressionado, e em seguida o anel de foco cobriria tudo.
  Por isso tambem nao ha `border-active`.

  Nao existe Typed. Ter valor e conteudo, nao interacao: um campo pode estar
  com hover E com valor. A troca placeholder/valor e `:placeholder-shown` no
  CSS, nunca `:hover` ou `:focus`.

A BORDA E O EIXO QUE CARREGA O ESTADO

  O fundo do campo nao muda entre repouso, hover, foco e erro - so a borda.
  Os dois estados que mexem no fundo sao os que mudam o que se PODE fazer com
  o campo: disabled (nada) e readOnly (ler e copiar, nao editar).

READ-ONLY NAO E DISABLED

  O disabled e isento do WCAG 1.4.3 por ser inativo; o read-only nao e. O
  conteudo existe para ser lido - e por isso o texto do read-only e
  `text-value`, o mesmo do campo editavel, e nao um cinza. Nao ha
  `input-text-readonly`: seria o mesmo valor guardado duas vezes.

  O fundo e `bg-subtle`, decisao de Gui em 26/09/2026. No tema escuro o
  `bg-subtle` coincide com `bg-surface-raised` (#3E3E3E), entao read-only e
  editavel se separam so pela borda e pelo cursor - escolha consciente, nao
  esquecimento. Nao propor `bg-readonly` semantico sem motivo novo.

  O read-only NUNCA mostra placeholder. Cinza do placeholder sobre o fundo do
  read-only da 4.21:1, abaixo do piso - e placeholder e dica de como
  preencher, que nao se aplica a um campo que ninguem preenche. O CSS esconde;
  a regra de uso manda o read-only vazio mostrar "—" como valor.

PREFIXO E SUFIXO TEM TOKEN PROPRIO

  Com o campo vazio, o prefixo ("www.") e escuro e o placeholder ao lado e
  cinza - duas cores na mesma linha. Se o afixo herdasse a cor do texto, ele
  clarearia junto com o placeholder. Dai `input-affix`. No disabled o afixo
  usa `text-disabled`, como todo texto dentro do campo desabilitado.

O CONTADOR SO FICA VERMELHO QUANDO O ERRO E O LIMITE

  No estado Error o contador continua `counter` (text-secondary): se o erro e
  "campo obrigatorio", contador vermelho aponta para a causa errada.
  `counter-error` existe para quando a contagem passa do limite, o que so
  acontece no codigo - o Figma nao tem variante disso, e a variavel existe la
  sem variante, como o `icon/disabled` do Checkbox.

ALTURA NAO E TOKEN

  48 = padding-y x2 + entrelinha do texto (12+24+12), com a borda de 1px
  sobreposta ao padding - em CSS, `padding: calc(12px - 1px)`. Mesma convencao
  do Button, do Tag e do Select. Altura total: rotulo 24 + gap 8 + campo 48 =
  80, e 104 com o texto de apoio (+8 +16).

O GAP E UM SO EM TRES LUGARES

  `input-gap` vale para a pilha vertical (rotulo -> campo -> apoio), para o
  espaco entre o rotulo e "(Opcional)" e para o espaco entre o prefixo e o
  texto. Os tres sao 8. Mesma regra do Select: dois tokens com o mesmo valor
  seriam dois lugares para o mesmo respiro divergir por engano.

  O sufixo nao usa gap: ele e empurrado para a borda direita do campo.

LARGURA NAO E TOKEN

  O campo ocupa 100% do conteiner. Formulario decide largura; componente nao.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'foundation'))

from build import SEM                     # noqa: E402
from color import cr                      # noqa: E402

FOUND = json.load(open(os.path.join(ROOT, 'tokens.json')))   # noqa: E402

# --------------------------------------------------------------- cor
COLOR = {
    'bg':               'bg-surface-raised',
    'bg-disabled':      'bg-disabled',
    'bg-readonly':      'bg-subtle',

    'border':           'border-default',
    'border-hover':     'border-strong',
    'border-focus':     'border-brand',
    'border-error':     'border-danger',
    'border-disabled':  'border-default',
    'border-readonly':  'border-subtle',

    'text-placeholder': 'text-placeholder',
    'text-value':       'text-primary',
    'text-disabled':    'text-disabled',

    'affix':            'text-primary',

    'label':            'text-primary',
    'label-error':      'text-danger',
    'label-disabled':   'text-disabled',

    'optional':         'text-secondary',

    'counter':          'text-secondary',
    'counter-error':    'text-danger',

    'help':             'text-secondary',
    'help-error':       'text-danger',
}

# O token aponta para a SOMBRA COMPOSTA, nao para a cor crua - mesma regra do
# `button-*-ring`. A cor so e extraida para medicao, no RING_INK abaixo.
RING = {
    'ring':       'focusRing.default',
    'ring-error': 'focusRing.error',
}

RING_INK = {
    'ring':       'shadow-focus-default',
    'ring-error': 'shadow-focus-error',
}

# ------------------------------------------------------------ geometria
GEOM = {
    'padding-x':    'space.12',
    'padding-y':    'space.12',
    'gap':          'space.8',       # pilha, rotulo -> opcional, prefixo -> texto
    'radius':       'radius.lg',
    'border-width': 'border.width.1',
}

TYPE = {
    'font':          'type.styles.body-md',
    'label-font':    'type.styles.body-md',
    'optional-font': 'type.styles.body-sm',
    'counter-font':  'type.styles.body-sm',
    'help-font':     'type.styles.caption',
}

PENDING = {
    'borda-abaixo-de-3-1': (
        'A borda em repouso usa `border-default` (1.57:1 no claro, 1.46:1 no escuro '
        'contra o fundo do campo) e a do read-only usa `border-subtle` (1.14:1 no claro, '
        '1.00:1 no escuro). Abaixo dos 3:1 do WCAG 1.4.11. Mesma decisao consciente do '
        'Select, estendida ao read-only por Gui em 26/09/2026. O criterio nao falha quando '
        'a borda nao e o unico meio de perceber o componente, e aqui nao e: o campo tem '
        'rotulo visivel acima e texto dentro. NAO "corrigir" sem falar com ele.'
    ),
    'disabled-abaixo-de-aa': (
        'Rotulo, texto e borda no disabled ficam abaixo do minimo. Isencao do WCAG 1.4.3 '
        'para componente inativo - mesma excecao permanente do Button, do Tag e do '
        'Select. Subir esse contraste faz o desabilitado parecer editavel.'
    ),
}

CANVAS = 'bg-canvas'   # nao e token do Input: e a tela onde ele e colocado

# (papel, token do input, fundo(s), piso, chave da excecao em PENDING)
# Rotulo, marca, contador, apoio e anel vivem FORA do campo e medem contra a
# tela; o que esta dentro mede contra o fundo do campo daquele estado. A borda
# mede contra as DUAS superficies vizinhas e guarda a pior.
#
# Nao ha combinacao placeholder x bg-readonly: o read-only nao mostra
# placeholder (ver cabecalho). O portao de marcacao/QA confere isso no CSS.
COMBOS = [
    ('rotulo',            'label',            'canvas',                   4.5, None),
    ('rotulo-erro',       'label-error',      'canvas',                   4.5, None),
    ('rotulo-disabled',   'label-disabled',   'canvas',                   4.5, 'disabled-abaixo-de-aa'),
    ('opcional',          'optional',         'canvas',                   4.5, None),
    ('contador',          'counter',          'canvas',                   4.5, None),
    ('contador-erro',     'counter-error',    'canvas',                   4.5, None),
    ('apoio',             'help',             'canvas',                   4.5, None),
    ('apoio-erro',        'help-error',       'canvas',                   4.5, None),
    ('placeholder',       'text-placeholder', 'bg',                       4.5, None),
    ('valor',             'text-value',       'bg',                       4.5, None),
    ('afixo',             'affix',            'bg',                       4.5, None),
    ('valor-readonly',    'text-value',       'bg-readonly',              4.5, None),
    ('afixo-readonly',    'affix',            'bg-readonly',              4.5, None),
    ('texto-disabled',    'text-disabled',    'bg-disabled',              4.5, 'disabled-abaixo-de-aa'),
    ('borda-repouso',     'border',           ('canvas', 'bg'),           3.0, 'borda-abaixo-de-3-1'),
    ('borda-hover',       'border-hover',     ('canvas', 'bg'),           3.0, None),
    ('borda-focus',       'border-focus',     ('canvas', 'bg'),           3.0, None),
    ('borda-erro',        'border-error',     ('canvas', 'bg'),           3.0, None),
    ('borda-disabled',    'border-disabled',  ('canvas', 'bg-disabled'),  3.0, 'disabled-abaixo-de-aa'),
    ('borda-readonly',    'border-readonly',  ('canvas', 'bg-readonly'),  3.0, 'borda-abaixo-de-3-1'),
    ('anel-foco',         'ring',             'canvas',                   3.0, None),
    ('anel-foco-erro',    'ring-error',       'canvas',                   3.0, None),
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
    """O semantico de cor por tras de um papel - seguindo o anel ate a cor."""
    if role == 'canvas':
        return CANVAS
    if role in RING_INK:
        return RING_INK[role]
    return COLOR[role]


def contrast_rows():
    """Mede cada combinacao renderizada nos dois temas, cada uma contra o piso
    que e dela: texto 4.5:1 do 1.4.3, borda e anel 3:1 do 1.4.11."""
    rows = []
    for what, fg_role, bg_spec, min_ratio, exc in COMBOS:
        fg_ref = ink(fg_role)
        bg_roles = bg_spec if isinstance(bg_spec, tuple) else (bg_spec,)
        for theme, i in (('light', 0), ('dark', 1)):
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
        name = f'input-{role}'
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
        name = f'input-{role}'
        alias[name] = ref
        try:
            v = resolve_foundation(ref)
            resolved[name] = {'light': v['light'], 'dark': v['dark']}
        except KeyError:
            problems.append(f'{name}: {ref} nao existe na Foundation')

    for group in (GEOM, TYPE):
        for role, ref in group.items():
            name = f'input-{role}'
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
    print('CAMADA DE TOKENS DO INPUT')
    print('=' * 74)
    for name in sorted(alias):
        print(f'  {name:<26} -> {alias[name]}')
    print('-' * 74)
    print(f'altura do campo derivada: {derived["field-height"]}px  '
          f'(padding-y x2 + entrelinha; borda sobreposta ao padding)')
    print(f'altura total: {derived["total-height"]}px  '
          f'| com texto de apoio: {derived["total-height-with-help"]}px')
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
            'component': 'Input',
            'version': '0.1.0',
            'foundation': FOUND['meta']['version'],
            'figmaNode': '263:502',
            'variants': [],
            'sizes': ['md'],
            'states': ['default', 'hover', 'error', 'focus-error',
                       'disabled', 'focus', 'readonly'],
            'nota': (
                'Campo de texto de uma linha (text, email, url, tel). Senha vira o '
                'componente Password. Um tamanho so (48px). Sem Active - campo de '
                'texto sempre casa :focus-visible, inclusive no clique - e sem Typed, '
                'porque ter valor e conteudo, nao estado. A borda carrega o estado; o '
                'fundo so muda no disabled e no readonly. O read-only nao e isento de '
                'contraste como o disabled, usa o texto de valor e nunca mostra '
                'placeholder. Prefixo e sufixo tem token proprio (`affix`). O contador '
                'so fica vermelho quando passa do limite. Duas excecoes de contraste '
                'declaradas em pending.'
            ),
        },
        'alias': alias,
        'resolved': resolved,
        'derived': derived,
        'contrast': rows,
        'pending': PENDING,
    }
    json.dump(out, open(os.path.join(HERE, 'tokens.json'), 'w'), indent=2, ensure_ascii=False)
    print('\ncomponents/input/tokens.json escrito')
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
    return f'var(--al-{ref})'          # semantico de cor


def _size_key(font_size):
    """Acha o nome do degrau cujo font-size bate, na escala da Foundation.
    Ver a nota do Select: line-height usa o MESMO nome de degrau."""
    for key, v in FOUND['type']['size'].items():
        if v == font_size:
            return key
    raise KeyError(f'type.size com valor {font_size} nao existe na Foundation')


def write_css(alias, derived):
    L = []
    w = L.append
    w('/* AL Design System - tokens do Input')
    w(' * GERADO por components/input/tokens.py. Nao editar a mao.')
    w(' *')
    w(' * Nao ha bloco de tema aqui: cada token aponta para um semantico, e o tema')
    w(' * troca no :root - o mesmo elemento onde estes alias sao declarados.')
    w(' *')
    w(f' * Altura do campo: {derived["field-height"]}px derivados, sem token.')
    w(' */')
    w('')
    w(':root {')

    w('')
    w('  /* fundo - so o disabled e o readonly mudam */')
    for role in ('bg', 'bg-disabled', 'bg-readonly'):
        w(f'  --al-input-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* borda - o eixo que carrega o estado */')
    for role in ('border', 'border-hover', 'border-focus', 'border-error',
                 'border-disabled', 'border-readonly'):
        w(f'  --al-input-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* texto dentro do campo - placeholder x valor NAO e estado de interacao */')
    for role in ('text-placeholder', 'text-value', 'text-disabled'):
        w(f'  --al-input-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* prefixo e sufixo - nao herdam a cor do placeholder */')
    w(f'  --al-input-affix: {css_ref(COLOR["affix"])};')

    w('')
    w('  /* rotulo, marca, contador e apoio - vivem fora do campo, sobre a tela */')
    for role in ('label', 'label-error', 'label-disabled', 'optional',
                 'counter', 'counter-error', 'help', 'help-error'):
        w(f'  --al-input-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* anel de foco - aponta para a sombra composta, nao para a cor crua */')
    for role, ref in RING.items():
        w(f'  --al-input-{role}: {css_ref(ref)};')

    w('')
    w('  /* geometria */')
    for role, ref in GEOM.items():
        w(f'  --al-input-{role}: {css_ref(ref)};')

    w('')
    w('  /* tipografia - um estilo vira quatro vars */')
    for role, ref in TYPE.items():
        style = resolve_foundation(ref)
        key = _size_key(style[1])
        prefix = f'--al-input-{role}'.replace('-font', '')
        if role == 'font':
            prefix = '--al-input'
        w(f'  {prefix}-font-size: var(--al-font-size-{key});')
        w(f'  {prefix}-line-height: var(--al-line-height-{key});')
        w(f'  {prefix}-font-weight: {style[3]};')
        w(f'  {prefix}-tracking: {style[4]};')

    w('}')
    w('')

    # Trava herdada do Select: lista de grupo esquecida vira build quebrado,
    # nao variavel faltando em silencio.
    texto = '\n'.join(L)
    faltando = [r for r in COLOR if f'--al-input-{r}:' not in texto]
    if faltando:
        raise AssertionError(
            'papeis de cor fora do CSS (alguma lista de grupo em write_css nao '
            f'foi atualizada): {faltando}')

    path = os.path.join(HERE, 'al-input-tokens.css')
    open(path, 'w').write(texto)
    print(f'components/input/al-input-tokens.css escrito ({os.path.getsize(path)} bytes)')


if __name__ == '__main__':
    sys.exit(run())
