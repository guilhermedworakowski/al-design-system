"""
Camada de tokens do Checkbox.

Regra unica desta camada: nada aqui inventa valor. Todo token aponta para um
token da Foundation pelo NOME. O portao no fim do arquivo recusa qualquer
coisa que seja um valor solto - hex, px, numero.

Nomenclatura:
  codigo -> checkbox-border-hover      (hifen)
  Figma  -> checkbox/border/hover      (pasta)
Sao camadas diferentes. Nunca colapsar uma na outra.

E O `<input type="checkbox">` NATIVO

  Mesma escolha do Select: o controle e do navegador, o componente pinta a
  caixa por cima com `appearance: none`. Teclado (Espaco), estado marcado e
  `indeterminate` sao do input - nao ha comportamento proprio a construir.

UM TAMANHO SO - REGRA DO TIER 2

  Gui fechou em 23/09/2026 que todo input do Tier 2 tem um tamanho so. A caixa
  e 24x24, o mesmo grid de 24 do desenho Lucide do check, e a mesma entrelinha
  do rotulo - e isso que alinha a caixa com a primeira linha do texto.

O FIGMA TEM UM EIXO SO, O NAVEGADOR TEM DOIS

  O component set (node 229:509) tem sete variantes num eixo `State`: Default,
  Hover, Active (= marcado), Error, Disabled, Focus, Indeterminate. Variantes
  combinadas (marcado + hover, marcado + disabled...) ficaram de fora desta
  primeira versao por decisao de Gui. Mas o input nativo produz essas
  combinacoes de qualquer jeito, entao os tokens abaixo as cobrem SEM token
  novo, com uma excecao aprovada:

    marcado + hover        -> caixa laranja nao muda; hover so no desmarcado
    marcado + foco         -> anel por cima da caixa laranja
    erro + foco            -> anel padrao (nao ha anel de erro desenhado)
    erro + marcado         -> caixa laranja, rotulo vermelho
    marcado + disabled     -> `bg-disabled` com o check em `icon-disabled`

  `checkbox-icon-disabled` e o unico token que nao tem variante no Figma. Gui
  aprovou em 23/09/2026 (opcao "a" da etapa 3): o caso aparece em qualquer tela
  de configuracao bloqueada, e uma regra de "nao usar" seria quebrada no
  primeiro uso.

`bg-checked` VALE PARA MARCADO E INDETERMINADO

  O que diferencia os dois e o glifo (check x traco), nao a caixa. Um token so
  de fundo e um so de borda, igual ao desenho.

`border-hover` E `border-focus` APONTAM PRO MESMO ALIAS, E SAO DOIS TOKENS

  Mesma logica do `border-active` / `border-focus` do Select: hoje coincidem,
  e dois nomes deixam um divergir do outro depois sem mudanca quebrada.

O ICONE TEM TOKEN DE COR

  O rotulo e escuro e o check e branco - nao da para herdar `currentColor`.
  Piso do check e 3:1 do 1.4.11 (glifo), nao 4.5:1: branco sobre a marca da
  3.34:1 e passa com folga. Nao e excecao.

O ICONE NAO TEM TOKEN DE TAMANHO

  18 = caixa 24 - 2 x borda 1 - 2 x padding 2. E derivado, e 18 nem existe na
  escala `icon-size` - tokenizar seria guardar a mesma decisao em dois lugares.

DUAS EXCECOES DECLARADAS DE CONTRASTE

  Ver PENDING. A da borda em repouso NAO e a mesma do Select, e isso importa.
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
    'bg-hover':         'bg-hover',
    'bg-checked':       'bg-brand',        # marcado e indeterminado
    'bg-disabled':      'bg-disabled',

    'border':           'border-default',
    'border-hover':     'border-strong',
    'border-focus':     'border-strong',
    'border-checked':   'border-brand',
    'border-error':     'border-danger',
    'border-disabled':  'border-default',

    'icon':             'text-on-brand',   # check e traco - piso 3:1
    'icon-disabled':    'text-disabled',   # marcado + disabled, sem variante no Figma

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
    'padding':      'space.2',        # borda -> glifo
    'gap':          'space.8',        # caixa -> rotulo
    'radius':       'radius.sm',
    'border-width': 'border.width.1',
}

TYPE = {
    'label-font': 'type.styles.body-md',
}

PENDING = {
    'borda-abaixo-de-3-1': (
        'A borda da caixa desmarcada em repouso usa `border-default`: 1.57:1 no claro e '
        '1.46:1 no escuro (contra o fundo da caixa), abaixo dos 3:1 do WCAG 1.4.11. '
        'Decisao consciente de Gui em 23/09/2026, para seguir o padrao dos inputs do DS '
        '(o Select usa a mesma borda). ATENCAO: o argumento do Select NAO vale aqui - '
        'no Checkbox a borda e o unico desenho do controle desmarcado; foi apontado como '
        'bloqueante na etapa 1 e mantido por decisao de padrao. Hover e foco (border-strong) '
        'e erro (border-danger) passam. NAO "corrigir" sem falar com ele.'
    ),
    'disabled-abaixo-de-aa': (
        'Rotulo, borda e check no disabled ficam abaixo do piso. Isencao do WCAG 1.4.3 / '
        '1.4.11 para componente inativo - mesma excecao permanente do Button, do Tag e do '
        'Select. Subir esse contraste faz o desabilitado parecer clicavel.'
    ),
}

CANVAS = 'bg-canvas'   # nao e token do Checkbox: e a tela onde ele e colocado

# (papel, token do checkbox, fundo(s), piso, chave da excecao em PENDING)
# A borda tem duas superficies vizinhas - a tela por fora e a caixa por dentro -
# e vale a PIOR das duas. A caixa marcada mede o PREENCHIMENTO contra a tela:
# e ele, nao a borda, que desenha o limite do controle marcado.
COMBOS = [
    ('rotulo',          'label',           'canvas',                   4.5, None),
    ('rotulo-erro',     'label-error',     'canvas',                   4.5, None),
    ('rotulo-disabled', 'label-disabled',  'canvas',                   4.5, 'disabled-abaixo-de-aa'),
    ('borda-repouso',   'border',          ('canvas', 'bg'),           3.0, 'borda-abaixo-de-3-1'),
    ('borda-hover',     'border-hover',    ('canvas', 'bg-hover'),     3.0, None),
    ('borda-focus',     'border-focus',    ('canvas', 'bg'),           3.0, None),
    ('borda-erro',      'border-error',    ('canvas', 'bg'),           3.0, None),
    ('borda-disabled',  'border-disabled', ('canvas', 'bg-disabled'),  3.0, 'disabled-abaixo-de-aa'),
    ('caixa-marcada',   'bg-checked',      'canvas',                   3.0, None),
    ('check',           'icon',            'bg-checked',               3.0, None),
    ('check-disabled',  'icon-disabled',   'bg-disabled',              3.0, 'disabled-abaixo-de-aa'),
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
    que e dela: texto 4.5:1 do 1.4.3, borda e glifo 3:1 do 1.4.11."""
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
        name = f'checkbox-{role}'
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
        name = f'checkbox-{role}'
        alias[name] = ref
        try:
            v = resolve_foundation(ref)
            resolved[name] = {'light': v['light'], 'dark': v['dark']}
        except KeyError:
            problems.append(f'{name}: {ref} nao existe na Foundation')

    for group in (GEOM, TYPE):
        for role, ref in group.items():
            name = f'checkbox-{role}'
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
        'icon-size': box - 2 * bw - 2 * pad,
        'row-height': max(box, line),
    }

    rows = contrast_rows()
    fails = [r for r in rows if not r['pass'] and not r['exception']]
    excs = [r for r in rows if not r['pass'] and r['exception']]

    print('=' * 74)
    print('CAMADA DE TOKENS DO CHECKBOX')
    print('=' * 74)
    for name in sorted(alias):
        print(f'  {name:<26} -> {alias[name]}')
    print('-' * 74)
    print(f'glifo derivado: {derived["icon-size"]}px  (caixa - 2 x borda - 2 x padding)')
    print(f'altura da linha: {derived["row-height"]}px')
    # conferencia, nao portao: caixa e entrelinha devem bater - e o que alinha
    # a caixa com a primeira linha do rotulo sem mexer na altura
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
            'component': 'Checkbox',
            'version': '0.1.0',
            'foundation': FOUND['meta']['version'],
            'figmaNode': '229:509',
            'variants': [],
            'sizes': ['md'],
            'states': ['default', 'hover', 'checked', 'error',
                       'disabled', 'focus', 'indeterminate'],
            'nota': (
                'E o <input type="checkbox"> NATIVO, com a caixa pintada por cima. '
                'Um tamanho so (caixa 24px), regra de todo input do Tier 2. O Figma '
                'tem um eixo so de estado; as combinacoes que o navegador produz '
                '(marcado + hover/foco/disabled/erro) sao cobertas pelos mesmos tokens, '
                'mais `icon-disabled`, que nao tem variante no Figma. `bg-checked` vale '
                'para marcado e indeterminado. Sem texto de apoio/erro: a mensagem de '
                'erro e do formulario. Duas excecoes de contraste declaradas em pending.'
            ),
        },
        'alias': alias,
        'resolved': resolved,
        'derived': derived,
        'contrast': rows,
        'pending': PENDING,
    }
    json.dump(out, open(os.path.join(HERE, 'tokens.json'), 'w'), indent=2, ensure_ascii=False)
    print('\ncomponents/checkbox/tokens.json escrito')
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
    w('/* AL Design System - tokens do Checkbox')
    w(' * GERADO por components/checkbox/tokens.py. Nao editar a mao.')
    w(' *')
    w(' * Sem bloco de tema: cada token aponta para um semantico, e o tema troca')
    w(' * no :root - o mesmo elemento onde estes alias sao declarados.')
    w(' *')
    w(f' * Glifo: {derived["icon-size"]}px derivados, sem token.')
    w(' */')
    w('')
    w(':root {')

    w('')
    w('  /* fundo da caixa - marcado e indeterminado dividem o mesmo */')
    for role in ('bg', 'bg-hover', 'bg-checked', 'bg-disabled'):
        w(f'  --al-checkbox-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* borda da caixa */')
    for role in ('border', 'border-hover', 'border-focus', 'border-checked',
                 'border-error', 'border-disabled'):
        w(f'  --al-checkbox-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* check e traco - nao herdam a cor do rotulo */')
    for role in ('icon', 'icon-disabled'):
        w(f'  --al-checkbox-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* rotulo - vive fora da caixa, sobre a tela */')
    for role in ('label', 'label-error', 'label-disabled'):
        w(f'  --al-checkbox-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* anel de foco - aponta para a sombra composta, nao para a cor crua */')
    for role, ref in RING.items():
        w(f'  --al-checkbox-{role}: {css_ref(ref)};')

    w('')
    w('  /* geometria */')
    for role, ref in GEOM.items():
        w(f'  --al-checkbox-{role}: {css_ref(ref)};')

    w('')
    w('  /* tipografia - um estilo vira quatro vars */')
    for role, ref in TYPE.items():
        style = resolve_foundation(ref)
        key = _size_key(style[1])
        prefix = f'--al-checkbox-{role}'.replace('-font', '')
        w(f'  {prefix}-font-size: var(--al-font-size-{key});')
        w(f'  {prefix}-line-height: var(--al-line-height-{key});')
        w(f'  {prefix}-font-weight: {style[3]};')
        w(f'  {prefix}-tracking: {style[4]};')

    w('}')
    w('')

    # Trava: lista de grupo esquecida vira build quebrado, nao variavel faltando.
    texto = '\n'.join(L)
    faltando = [r for r in COLOR if f'--al-checkbox-{r}:' not in texto]
    if faltando:
        raise AssertionError(
            'papeis de cor fora do CSS (alguma lista de grupo em write_css nao '
            f'foi atualizada): {faltando}')

    path = os.path.join(HERE, 'al-checkbox-tokens.css')
    open(path, 'w').write(texto)
    print(f'components/checkbox/al-checkbox-tokens.css escrito ({os.path.getsize(path)} bytes)')


if __name__ == '__main__':
    sys.exit(run())
