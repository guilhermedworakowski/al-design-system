"""
Camada de tokens do Radio.

Regra unica desta camada: nada aqui inventa valor. Todo token aponta para um
token da Foundation pelo NOME. O portao no fim do arquivo recusa qualquer
coisa que seja um valor solto - hex, px, numero.

Nomenclatura:
  codigo -> radio-border-hover      (hifen)
  Figma  -> radio/border/hover      (pasta, collection `10. Radio`)
Sao camadas diferentes. Nunca colapsar uma na outra.

E O `<input type="radio">` NATIVO

  Mesma escolha do Select e do Checkbox: o controle e do navegador, o
  componente pinta o circulo por cima com `appearance: none`. Setas dentro do
  grupo, Tab entrando uma vez so e "marcar um desmarca o outro" sao do input,
  desde que os radios da mesma pergunta dividam o mesmo `name`.

UM TAMANHO SO - REGRA DO TIER 2

  Circulo 24x24, o mesmo da caixa do Checkbox e da entrelinha do rotulo - e
  isso que alinha o circulo com a primeira linha do texto.

MARCADO NAO PINTA O FUNDO - E A DIFERENCA PARA O CHECKBOX

  No Checkbox, marcado = caixa laranja. No Radio, marcado = borda laranja +
  ponto laranja, com o fundo continuando `bg`: o anel branco entre a borda e o
  ponto E o fundo. Por isso nao existe `bg-checked`, e existem `dot` e
  `dot-disabled` no lugar do `icon` / `icon-disabled`.

O FIGMA TEM UM EIXO SO, O NAVEGADOR TEM DOIS

  O component set (node 230:611) tem seis variantes num eixo `State`: Default,
  Hover, Active (= marcado), Error, Disabled, Focus. As combinacoes que o input
  produz sao cobertas pelos mesmos tokens, com a mesma solucao do Checkbox
  (decisao de Gui na etapa 1, 24/09/2026):

    marcado + hover        -> nada muda; hover so no desmarcado (radio marcado
                              nao desmarca com clique - o hover prometeria acao)
    marcado + foco         -> anel por cima do anel laranja
    erro + marcado         -> borda e ponto laranja, rotulo vermelho
    marcado + disabled     -> `bg-disabled`, `border-disabled`, ponto em
                              `dot-disabled`

  `radio-dot-disabled` e o unico token sem variante no Figma - espelho do
  `checkbox-icon-disabled`.

O ERRO E DA PERGUNTA, NAO DO RADIO

  Precedente Primer / Carbon / Spectrum / Polaris: a variante Error acende em
  TODOS os radios da mesma pergunta ao mesmo tempo, nunca num so. Nao ha
  componente de grupo (decisao de Gui): mensagem e `aria-invalid` sao do
  formulario. Isso e regra de uso, nao token.

`border-hover` E `border-focus` APONTAM PRO MESMO ALIAS, E SAO DOIS TOKENS

  Mesma logica do Select e do Checkbox: hoje coincidem, e dois nomes deixam um
  divergir do outro depois sem mudanca quebrada.

O PONTO NAO TEM TOKEN DE TAMANHO

  14 = circulo 24 - 2 x borda 1 - 2 x padding 4. E derivado, e 14 nem existe
  na escala - tokenizar seria guardar a mesma decisao em dois lugares. O padding
  e `space-4` (nao o `space-2` do Checkbox) desde a etapa 1: com 18px o ponto
  enchia o circulo e o marcado + disabled virava um disco cinza igual ao
  desmarcado + disabled.

DUAS EXCECOES DECLARADAS DE CONTRASTE

  Ver PENDING. As mesmas do Checkbox.
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
    'bg':               'bg-surface-raised',   # desmarcado E marcado (anel branco)
    'bg-hover':         'bg-hover',
    'bg-disabled':      'bg-disabled',

    'border':           'border-default',
    'border-hover':     'border-strong',
    'border-focus':     'border-strong',
    'border-checked':   'border-brand',
    'border-error':     'border-danger',
    'border-disabled':  'border-default',

    'dot':              'bg-brand',        # ponto do marcado - piso 3:1
    'dot-disabled':     'text-disabled',   # marcado + disabled, sem variante no Figma

    'label':            'text-primary',
    'label-error':      'text-danger',
    'label-disabled':   'text-disabled',
}

# O token aponta para a SOMBRA COMPOSTA, nao para a cor crua.
RING = {
    'ring': 'focusRing.default',
}

RING_INK = {
    'ring': 'shadow-focus-default',
}

# ------------------------------------------------------------ geometria
GEOM = {
    'box-size':     'iconSize.24',
    'padding':      'space.4',        # borda -> ponto
    'gap':          'space.8',        # circulo -> rotulo
    'radius':       'radius.full',
    'border-width': 'border.width.1',
}

TYPE = {
    'label-font': 'type.styles.body-md',
}

PENDING = {
    'borda-abaixo-de-3-1': (
        'A borda do circulo desmarcado em repouso usa `border-default`: 1.57:1 no claro e '
        '1.46:1 no escuro (contra o fundo do circulo), abaixo dos 3:1 do WCAG 1.4.11. '
        'Mesma decisao consciente de Gui do Checkbox (23/09/2026), herdada no Radio em '
        '24/09/2026: seguir o padrao dos inputs do DS. A borda e o unico desenho do controle '
        'desmarcado; quem sustenta a excecao e a regra do rotulo visivel. Hover e foco '
        '(border-strong), marcado (border-brand) e erro (border-danger) passam. NAO '
        '"corrigir" sem falar com ele.'
    ),
    'disabled-abaixo-de-aa': (
        'Rotulo, borda e ponto no disabled ficam abaixo do piso. Isencao do WCAG 1.4.3 / '
        '1.4.11 para componente inativo - mesma excecao permanente do Button, do Tag, do '
        'Select e do Checkbox. Subir esse contraste faz o desabilitado parecer clicavel.'
    ),
}

CANVAS = 'bg-canvas'   # nao e token do Radio: e a tela onde ele e colocado

# (papel, token do radio, fundo(s), piso, chave da excecao em PENDING)
# A borda tem duas superficies vizinhas - a tela por fora e o circulo por
# dentro - e vale a PIOR das duas. O ponto mede contra o `bg`: e o anel branco
# que o separa da borda, nao a tela.
COMBOS = [
    ('rotulo',          'label',           'canvas',                   4.5, None),
    ('rotulo-erro',     'label-error',     'canvas',                   4.5, None),
    ('rotulo-disabled', 'label-disabled',  'canvas',                   4.5, 'disabled-abaixo-de-aa'),
    ('borda-repouso',   'border',          ('canvas', 'bg'),           3.0, 'borda-abaixo-de-3-1'),
    ('borda-hover',     'border-hover',    ('canvas', 'bg-hover'),     3.0, None),
    ('borda-focus',     'border-focus',    ('canvas', 'bg'),           3.0, None),
    ('borda-marcada',   'border-checked',  ('canvas', 'bg'),           3.0, None),
    ('borda-erro',      'border-error',    ('canvas', 'bg'),           3.0, None),
    ('borda-disabled',  'border-disabled', ('canvas', 'bg-disabled'),  3.0, 'disabled-abaixo-de-aa'),
    ('ponto',           'dot',             'bg',                       3.0, None),
    ('ponto-disabled',  'dot-disabled',    'bg-disabled',              3.0, 'disabled-abaixo-de-aa'),
    ('anel-foco',       'ring',            'canvas',                   3.0, None),
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
    que e dela: texto 4.5:1 do 1.4.3, borda e ponto 3:1 do 1.4.11."""
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
        name = f'radio-{role}'
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
        name = f'radio-{role}'
        alias[name] = ref
        try:
            v = resolve_foundation(ref)
            resolved[name] = {'light': v['light'], 'dark': v['dark']}
        except KeyError:
            problems.append(f'{name}: {ref} nao existe na Foundation')

    for group in (GEOM, TYPE):
        for role, ref in group.items():
            name = f'radio-{role}'
            alias[name] = ref
            try:
                resolved[name] = resolve_foundation(ref)
            except KeyError:
                problems.append(f'{name}: {ref} nao existe na Foundation')

    if problems:
        print(f'{len(problems)} TOKEN(S) REPROVAM O PORTAO DE ALIAS:')
        for p in problems:
            print('   ', p)
        return 1

    # derivadas - conferencia, nao token. Ver nota no cabecalho.
    box = resolve_foundation(GEOM['box-size'])
    pad = resolve_foundation(GEOM['padding'])
    bw = resolve_foundation(GEOM['border-width'])
    line = resolve_foundation(TYPE['label-font'])[2]
    derived = {
        'dot-size': box - 2 * bw - 2 * pad,
        'row-height': max(box, line),
    }

    rows = contrast_rows()
    fails = [r for r in rows if not r['pass'] and not r['exception']]
    excs = [r for r in rows if not r['pass'] and r['exception']]

    print('=' * 74)
    print('CAMADA DE TOKENS DO RADIO')
    print('=' * 74)
    for name in sorted(alias):
        print(f'  {name:<26} -> {alias[name]}')
    print('-' * 74)
    print(f'ponto derivado: {derived["dot-size"]}px  (circulo - 2 x borda - 2 x padding)')
    print(f'altura da linha: {derived["row-height"]}px')
    # conferencia, nao portao: circulo e entrelinha devem bater - e o que
    # alinha o circulo com a primeira linha do rotulo sem mexer na altura
    if box != line:
        print(f'  ATENCAO: box-size {box} != entrelinha do rotulo {line}')
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

    if fails:
        print(f'{len(fails)} COMBINACAO(OES) REPROVAM O PORTAO DE CONTRASTE:')
        for f in fails:
            print(f'    {f["what"]} ({f["theme"]}): {f["ratio"]}:1 < {f["min"]}')
        return 1

    print(f'{len(alias)} tokens, todos alias da Foundation. 0 valores soltos.')

    out = {
        'meta': {
            'component': 'Radio',
            'version': '0.1.0',
            'foundation': FOUND['meta']['version'],
            'figmaNode': '230:611',
            'figmaCollection': '10. Radio',
            'variants': [],
            'sizes': ['md'],
            'states': ['default', 'hover', 'checked', 'error', 'disabled', 'focus'],
            'nota': (
                'E o <input type="radio"> NATIVO, com o circulo pintado por cima. '
                'Um tamanho so (circulo 24px), regra de todo input do Tier 2. Marcado '
                'nao pinta o fundo: borda e ponto laranja, com o anel branco entre eles. '
                'O Figma tem um eixo so de estado; as combinacoes que o navegador produz '
                '(marcado + foco/disabled/erro) sao cobertas pelos mesmos tokens, mais '
                '`dot-disabled`, que nao tem variante no Figma. O erro acende em todos os '
                'radios da pergunta; mensagem e aria-invalid sao do formulario. Duas '
                'excecoes de contraste declaradas em pending.'
            ),
        },
        'alias': alias,
        'resolved': resolved,
        'derived': derived,
        'contrast': rows,
        'pending': PENDING,
    }
    json.dump(out, open(os.path.join(HERE, 'tokens.json'), 'w'), indent=2, ensure_ascii=False)
    print('\ncomponents/radio/tokens.json escrito')
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
    Line-height usa o MESMO nome - buscar por valor seria ambiguo."""
    for key, v in FOUND['type']['size'].items():
        if v == font_size:
            return key
    raise KeyError(f'type.size com valor {font_size} nao existe na Foundation')


def write_css(alias, derived):
    L = []
    w = L.append
    w('/* AL Design System - tokens do Radio')
    w(' * GERADO por components/radio/tokens.py. Nao editar a mao.')
    w(' *')
    w(' * Sem bloco de tema: cada token aponta para um semantico, e o tema troca')
    w(' * no :root - o mesmo elemento onde estes alias sao declarados.')
    w(' *')
    w(f' * Ponto: {derived["dot-size"]}px derivados, sem token.')
    w(' */')
    w('')
    w(':root {')

    w('')
    w('  /* fundo do circulo - o marcado continua em `bg`: e o anel branco */')
    for role in ('bg', 'bg-hover', 'bg-disabled'):
        w(f'  --al-radio-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* borda do circulo */')
    for role in ('border', 'border-hover', 'border-focus', 'border-checked',
                 'border-error', 'border-disabled'):
        w(f'  --al-radio-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* ponto do marcado */')
    for role in ('dot', 'dot-disabled'):
        w(f'  --al-radio-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* rotulo - vive fora do circulo, sobre a tela */')
    for role in ('label', 'label-error', 'label-disabled'):
        w(f'  --al-radio-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* anel de foco - aponta para a sombra composta, nao para a cor crua */')
    for role, ref in RING.items():
        w(f'  --al-radio-{role}: {css_ref(ref)};')

    w('')
    w('  /* geometria */')
    for role, ref in GEOM.items():
        w(f'  --al-radio-{role}: {css_ref(ref)};')

    w('')
    w('  /* tipografia - um estilo vira quatro vars */')
    for role, ref in TYPE.items():
        style = resolve_foundation(ref)
        key = _size_key(style[1])
        prefix = f'--al-radio-{role}'.replace('-font', '')
        w(f'  {prefix}-font-size: var(--al-font-size-{key});')
        w(f'  {prefix}-line-height: var(--al-line-height-{key});')
        w(f'  {prefix}-font-weight: {style[3]};')
        w(f'  {prefix}-tracking: {style[4]};')

    w('}')
    w('')

    # Trava: lista de grupo esquecida vira build quebrado, nao variavel faltando.
    texto = '\n'.join(L)
    faltando = [r for r in COLOR if f'--al-radio-{r}:' not in texto]
    if faltando:
        raise AssertionError(
            'papeis de cor fora do CSS (alguma lista de grupo em write_css nao '
            f'foi atualizada): {faltando}')

    path = os.path.join(HERE, 'al-radio-tokens.css')
    open(path, 'w').write(texto)
    print(f'components/radio/al-radio-tokens.css escrito ({os.path.getsize(path)} bytes)')


if __name__ == '__main__':
    sys.exit(run())
