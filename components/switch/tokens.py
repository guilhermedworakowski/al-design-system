"""
Camada de tokens do Switch.

Regra unica desta camada: nada aqui inventa valor. Todo token aponta para um
token da Foundation pelo NOME. O portao no fim do arquivo recusa qualquer
coisa que seja um valor solto - hex, px, numero.

Nomenclatura:
  codigo -> switch-thumb-checked      (hifen)
  Figma  -> thumb/checked             (pasta, collection `11. Switch`)
Sao camadas diferentes. Nunca colapsar uma na outra.

E O `<input type="checkbox" role="switch">` NATIVO

  Mesma escolha do Select, do Checkbox e do Radio: o controle e do navegador,
  o componente pinta o trilho por cima com `appearance: none`. `role="switch"`
  troca o anuncio de "caixa de selecao, marcada" para "chave, ligada".

UM TAMANHO SO - REGRA DO TIER 2

  Trilho 24px de altura, a mesma do circulo do Radio e da entrelinha do
  rotulo - e isso que alinha o controle com a primeira linha do texto.

SEM ERRO - DECISAO DE GUI NA ETAPA 1 (25/09/2026)

  Precedente Spectrum: o switch tem efeito imediato, nao espera "Enviar", entao
  nao ha validacao e nao ha erro. Escolha que precisa ser validada e Checkbox.
  Por isso nao existe `label-error` nem `border-error`.

O HOVER SO MEXE NA BORDA, O FOCO SO NO ANEL

  O trilho nao muda de cor no hover (decisao de Gui): o unico sinal e
  `border-hover`. No foco a borda fica a de repouso e quem sinaliza e o anel -
  por isso nao existe `track-hover` nem `border-focus`.

O FIGMA TEM UM EIXO SO, O NAVEGADOR TEM DOIS

  O component set (node 259:262) tem cinco variantes num eixo `State`: Default,
  Hover, Active (= ligado), Disabled, Focus. As combinacoes que o input produz
  sao cobertas pelos mesmos tokens, com a solucao do Checkbox e do Radio:

    ligado + hover      -> borda `border-checked` (o laranja nao muda)
    ligado + foco       -> anel por fora do trilho laranja
    ligado + disabled   -> trilho `track-disabled`, bolinha a direita em
                           `thumb-checked-disabled` (aprovado por Gui, 25/09/2026)

  `switch-thumb-checked-disabled` e o unico token sem variante no Figma -
  espelho do `radio-dot-disabled` e do `checkbox-icon-disabled`.

A BOLINHA E A LARGURA NAO TEM TOKEN

  bolinha = altura 24 - 2 x borda 1 - 2 x padding 4 = 14
  largura = 2 x bolinha + 2 x padding + 2 x borda   = 38
  curso   = bolinha                                  = 14
  Sao derivadas. Tokenizar seria guardar a mesma decisao em dois lugares, e
  nem 14 nem 38 existem na escala.

TRES EXCECOES DECLARADAS DE CONTRASTE

  Ver PENDING. A da bolinha desligada e a nova; as outras duas sao as mesmas
  do Checkbox e do Radio.
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
    'track':                  'bg-surface',
    'track-checked':          'bg-brand',       # quem diz "ligado" - piso 3:1
    'track-disabled':         'bg-disabled',    # ligado ou desligado

    'border':                 'border-default',
    'border-hover':           'border-strong',
    'border-checked':         'border-brand',
    'border-disabled':        'border-default',

    'thumb':                  'bg-thumb',
    'thumb-checked':          'text-on-brand',
    'thumb-disabled':         'bg-thumb-disabled',
    'thumb-checked-disabled': 'text-disabled',  # sem variante no Figma

    'label':                  'text-primary',
    'label-disabled':         'text-disabled',
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
    'track-height': 'iconSize.24',
    'padding':      'space.4',        # borda -> bolinha
    'gap':          'space.8',        # trilho -> rotulo
    'radius':       'radius.full',
    'border-width': 'border.width.1',
}

TYPE = {
    'label-font': 'type.styles.body-md',
}

PENDING = {
    'bolinha-abaixo-de-3-1': (
        'A bolinha desligada usa `bg-thumb` (neutral-400 / neutral-600): 1.96:1 no claro e '
        '2.98:1 no escuro contra o trilho, abaixo dos 3:1 do WCAG 1.4.11. Decisao consciente '
        'de Gui na etapa 1 (25/09/2026): neutral-400 e o teto, ele recusou escurecer ate '
        'border-strong. Quem sustenta a excecao e o trilho laranja do ligado, que passa '
        '(3.12:1 / 4.36:1), e a regra do rotulo visivel. NAO "corrigir" sem falar com ele.'
    ),
    'borda-abaixo-de-3-1': (
        'A borda do trilho em repouso usa `border-default`: 1.47:1 no claro e 1.98:1 no '
        'escuro, abaixo dos 3:1 do WCAG 1.4.11. Mesma decisao do Checkbox e do Radio: '
        'seguir o padrao dos inputs do DS. Hover (border-strong) e ligado (border-brand) passam.'
    ),
    'disabled-abaixo-de-aa': (
        'Rotulo, borda e bolinha no disabled ficam abaixo do piso. Isencao do WCAG 1.4.3 / '
        '1.4.11 para componente inativo - mesma excecao permanente do Button, do Tag, do '
        'Select, do Checkbox e do Radio. Subir esse contraste faz o desabilitado parecer clicavel.'
    ),
}

CANVAS = 'bg-canvas'   # nao e token do Switch: e a tela onde ele e colocado

# (papel, token do switch, fundo(s), piso, chave da excecao em PENDING)
# A borda e o trilho ligado tem duas superficies vizinhas - a tela por fora e
# o trilho desligado (o estado de onde se sai) - e vale a PIOR das duas. A
# bolinha mede contra o trilho em que ela esta.
COMBOS = [
    ('rotulo',                  'label',                  'canvas',                     4.5, None),
    ('rotulo-disabled',         'label-disabled',         'canvas',                     4.5, 'disabled-abaixo-de-aa'),
    ('trilho-ligado',           'track-checked',          ('canvas', 'track'),          3.0, None),
    ('borda-repouso',           'border',                 ('canvas', 'track'),          3.0, 'borda-abaixo-de-3-1'),
    ('borda-hover',             'border-hover',           ('canvas', 'track'),          3.0, None),
    ('borda-disabled',          'border-disabled',        ('canvas', 'track-disabled'), 3.0, 'disabled-abaixo-de-aa'),
    ('bolinha-desligada',       'thumb',                  'track',                      3.0, 'bolinha-abaixo-de-3-1'),
    ('bolinha-ligada',          'thumb-checked',          'track-checked',              3.0, None),
    ('bolinha-disabled',        'thumb-disabled',         'track-disabled',             3.0, 'disabled-abaixo-de-aa'),
    ('bolinha-ligada-disabled', 'thumb-checked-disabled', 'track-disabled',             3.0, 'disabled-abaixo-de-aa'),
    ('anel-foco',               'ring',                   'canvas',                     3.0, None),
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
    que e dela: texto 4.5:1 do 1.4.3, borda, trilho e bolinha 3:1 do 1.4.11."""
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
        name = f'switch-{role}'
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
        name = f'switch-{role}'
        alias[name] = ref
        try:
            v = resolve_foundation(ref)
            resolved[name] = {'light': v['light'], 'dark': v['dark']}
        except KeyError:
            problems.append(f'{name}: {ref} nao existe na Foundation')

    for group in (GEOM, TYPE):
        for role, ref in group.items():
            name = f'switch-{role}'
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
    h = resolve_foundation(GEOM['track-height'])
    pad = resolve_foundation(GEOM['padding'])
    bw = resolve_foundation(GEOM['border-width'])
    line = resolve_foundation(TYPE['label-font'])[2]
    thumb = h - 2 * bw - 2 * pad
    derived = {
        'thumb-size': thumb,
        'track-width': 2 * thumb + 2 * pad + 2 * bw,
        'thumb-travel': thumb,
        'row-height': max(h, line),
    }

    rows = contrast_rows()
    fails = [r for r in rows if not r['pass'] and not r['exception']]
    excs = [r for r in rows if not r['pass'] and r['exception']]

    print('=' * 74)
    print('CAMADA DE TOKENS DO SWITCH')
    print('=' * 74)
    for name in sorted(alias):
        print(f'  {name:<30} -> {alias[name]}')
    print('-' * 74)
    print(f'bolinha derivada: {derived["thumb-size"]}px  (altura - 2 x borda - 2 x padding)')
    print(f'trilho derivado : {derived["track-width"]}x{h}px  (curso {derived["thumb-travel"]}px)')
    print(f'altura da linha : {derived["row-height"]}px')
    # conferencia, nao portao: trilho e entrelinha devem bater - e o que
    # alinha o trilho com a primeira linha do rotulo sem mexer na altura
    if h != line:
        print(f'  ATENCAO: track-height {h} != entrelinha do rotulo {line}')
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
            'component': 'Switch',
            'version': '0.1.0',
            'foundation': FOUND['meta']['version'],
            'figmaNode': '259:262',
            'figmaCollection': '11. Switch',
            'variants': [],
            'sizes': ['md'],
            'states': ['default', 'hover', 'checked', 'disabled', 'focus'],
            'nota': (
                'E o <input type="checkbox" role="switch"> NATIVO, com o trilho pintado '
                'por cima. Um tamanho so (trilho 38x24), regra de todo input do Tier 2. '
                'Sem estado de erro: o switch tem efeito imediato. O Figma tem um eixo so '
                'de estado; as combinacoes que o navegador produz (ligado + foco/hover/'
                'disabled) sao cobertas pelos mesmos tokens, mais `thumb-checked-disabled`, '
                'que nao tem variante no Figma. Tres excecoes de contraste declaradas em pending.'
            ),
        },
        'alias': alias,
        'resolved': resolved,
        'derived': derived,
        'contrast': rows,
        'pending': PENDING,
    }
    json.dump(out, open(os.path.join(HERE, 'tokens.json'), 'w'), indent=2, ensure_ascii=False)
    print('\ncomponents/switch/tokens.json escrito')
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
    w('/* AL Design System - tokens do Switch')
    w(' * GERADO por components/switch/tokens.py. Nao editar a mao.')
    w(' *')
    w(' * Sem bloco de tema: cada token aponta para um semantico, e o tema troca')
    w(' * no :root - o mesmo elemento onde estes alias sao declarados.')
    w(' *')
    w(f' * Bolinha: {derived["thumb-size"]}px, trilho: {derived["track-width"]}px de largura,')
    w(' * curso: a propria bolinha. Derivados, sem token.')
    w(' */')
    w('')
    w(':root {')

    w('')
    w('  /* trilho - o laranja do ligado e quem diz o estado */')
    for role in ('track', 'track-checked', 'track-disabled'):
        w(f'  --al-switch-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* borda do trilho - o hover so mexe aqui */')
    for role in ('border', 'border-hover', 'border-checked', 'border-disabled'):
        w(f'  --al-switch-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* bolinha */')
    for role in ('thumb', 'thumb-checked', 'thumb-disabled', 'thumb-checked-disabled'):
        w(f'  --al-switch-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* rotulo - vive fora do trilho, sobre a tela */')
    for role in ('label', 'label-disabled'):
        w(f'  --al-switch-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* anel de foco - aponta para a sombra composta, nao para a cor crua */')
    for role, ref in RING.items():
        w(f'  --al-switch-{role}: {css_ref(ref)};')

    w('')
    w('  /* geometria */')
    for role, ref in GEOM.items():
        w(f'  --al-switch-{role}: {css_ref(ref)};')

    w('')
    w('  /* tipografia - um estilo vira quatro vars */')
    for role, ref in TYPE.items():
        style = resolve_foundation(ref)
        key = _size_key(style[1])
        prefix = f'--al-switch-{role}'.replace('-font', '')
        w(f'  {prefix}-font-size: var(--al-font-size-{key});')
        w(f'  {prefix}-line-height: var(--al-line-height-{key});')
        w(f'  {prefix}-font-weight: {style[3]};')
        w(f'  {prefix}-tracking: {style[4]};')

    w('}')
    w('')

    # Trava: lista de grupo esquecida vira build quebrado, nao variavel faltando.
    texto = '\n'.join(L)
    faltando = [r for r in COLOR if f'--al-switch-{r}:' not in texto]
    if faltando:
        raise AssertionError(
            'papeis de cor fora do CSS (alguma lista de grupo em write_css nao '
            f'foi atualizada): {faltando}')

    path = os.path.join(HERE, 'al-switch-tokens.css')
    open(path, 'w').write(texto)
    print(f'components/switch/al-switch-tokens.css escrito ({os.path.getsize(path)} bytes)')


if __name__ == '__main__':
    sys.exit(run())
