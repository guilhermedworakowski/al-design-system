"""
Camada de tokens do Tab.

Regra unica desta camada: nada aqui inventa valor. Todo token aponta para um
token da Foundation pelo NOME. O portao no fim do arquivo recusa qualquer
coisa que seja um valor solto - hex, px, numero.

Nomenclatura:
  codigo -> tab-line-indicator-selected   (hifen)
  Figma  -> line/indicator/selected       (collection `17. Tab`)
Sao camadas diferentes. Nunca colapsar uma na outra.

TERCEIRO COMPONENTE DO TIER 3 (07/10/2026)

  Component set `tab`, node 306:2532, pagina `Tier 3` do Figma. 16 variantes:
  `Type` (Line / Square) x `State` (Default / Hover / Pressed / Focus) x
  `Selected`. Um tamanho. Fora por escolha: disabled (decisao D de Gui - aba
  indisponivel sai da tela), icone, contador, rolagem, vertical, fechar.

  Uso principal e trocar conteudo na mesma tela (tablist/tab/tabpanel), mas o
  Tab tambem monta sidebar e navbar com links (decisao E). O visual e o mesmo;
  a marcacao muda - isso e da etapa 5, nao desta camada.

O LINE MARCA A SELECAO PELA LINHA, NAO PELO TEXTO - DECISAO A DE GUI

  Selecionado, o rotulo e `text-primary` como o hover; quem diz "esta aqui" e
  a linha laranja (precedente Primer e Material secundario). Isso tambem
  resolveu o pressed escuro: `text-brand` sobre `bg-active` dava 3,34:1.

A LINHA FICA NA ABA, NAO NO GRUPO - DECISAO B DE GUI

  Cada aba desenha a propria linha (cinza ou laranja). As abas ficam coladas,
  sem gap, e o espaco entre rotulos vem do padding de cada uma.

O SQUARE SELECIONADO E TONAL, E ESCURECE NA MARCA AO INTERAGIR

  Repouso e foco: `bg-brand-subtle` + `text-brand`. Hover: `bg-brand-hover` e
  pressed: `bg-brand-active`, os dois com `text-on-brand` - os mesmos
  semanticos de marca do Button (decisoes C, F, G de Gui).

FOCO E O REPOUSO MAIS O ANEL

  Sem fundo de hover. No Figma as variantes de foco sem fundo levam
  `bg/canvas` so para o Figma projetar o anel (preenchimento com opacidade 0
  nao projeta - testado); no CSS o fundo continua transparente.

SEM TOKEN, DE PROPOSITO

  Altura: Square 32 = 4 + 24 + 4; Line 42 = 32 + 8 + 2. Largura: o rotulo.
  Fundo em repouso: transparente, nao ha o que tokenizar. Gap entre abas: zero.

QUATRO EXCECOES DECLARADAS DE CONTRASTE

  Ver PENDING.
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
    # os dois tipos, aba nao selecionada
    'label':        'text-secondary',
    'label-hover':  'text-primary',
    'label-active': 'text-primary',
    'bg-hover':     'bg-hover',
    'bg-active':    'bg-active',

    # Line
    'line-label-selected':     'text-primary',
    'line-indicator':          'border-subtle',
    'line-indicator-selected': 'border-brand',

    # Square selecionado
    'square-bg-selected':           'bg-brand-subtle',
    'square-label-selected':        'text-brand',
    'square-bg-selected-hover':     'bg-brand-hover',
    'square-label-selected-hover':  'text-on-brand',
    'square-bg-selected-active':    'bg-brand-active',
    'square-label-selected-active': 'text-on-brand',
}

# O token aponta para a SOMBRA COMPOSTA, nao para a cor crua - mesma regra do
# `button-*-ring`. A cor so e extraida para medicao, no RING_INK abaixo.
RING = {
    'ring': 'focusRing.default',
}

RING_INK = {
    'ring': 'shadow-focus-default',
}

# ------------------------------------------------------------ geometria
GEOM = {
    'padding-x':            'space.12',
    'padding-y':            'space.4',
    'radius':               'radius.lg',
    'line-gap':             'space.8',          # caixa do rotulo -> linha
    'line-indicator-width': 'border.width.2',
}

TYPE = {
    'label-font': 'type.styles.body-md',   # 'font' gerava --al-tab-line-height, lido como tipo Line
}

PENDING = {
    'trilho-decorativo': (
        'A linha cinza do Line (`border-subtle`) da 1.32:1 no claro e 1.66:1 no escuro contra '
        'a tela, e menos sobre superficie. Ela nao carrega estado: a selecao e a linha laranja '
        '(`border-brand`), que passa 3:1 em todo fundo. Mesmo raciocinio do Divider. NAO '
        '"corrigir" escurecendo.'
    ),
    'selecao-tonal': (
        'O fundo do Square selecionado (`bg-brand-subtle`) mal se separa da pagina: 1.16:1 / '
        '1.08:1 no claro e 1.01:1 / 1.23:1 no escuro (tela / superficie). No escuro o rotulo '
        'laranja e o cinza das outras abas tem quase a mesma luminancia (1.05:1) - a selecao '
        'e marcada pelo matiz. Decisao H de Gui (07/10/2026, opcao a), tomada sabendo disso. '
        'Quem sustenta: regra de uso da etapa 4.'
    ),
    'pressed-na-superficie-escura': (
        'O fundo do Square selecionado PRESSIONADO (`bg-brand-active`) contra `bg-surface` no '
        'escuro = 2.74:1. E o numero que a decisao H cobria quando a selecionada era toda '
        'brand-active; Gui aceitou H(a) e reconfirmou na etapa 6 (07/10/2026). O estado so dura '
        'enquanto o clique esta apertado, a selecao aparece antes e depois, e o rotulo dentro '
        'passa (5.30:1). Sobre a tela escura passa (3.35:1). NAO escurecer o semantico.'
    ),
    'marca-no-hover-escuro': (
        'Branco sobre `bg-brand-hover` no escuro = 3.85:1. E a excecao de marca que a '
        'Foundation ja declara (dark text-on-brand / bg-brand-hover), herdada do Button, com '
        'piso rigido de 3:1. No claro passa (5.30:1).'
    ),
}

# Fundos onde o tab e colocado. Nao sao tokens do Tab.
PAGES = {
    'canvas':  'bg-canvas',
    'surface': 'bg-surface',
}

# (papel, token do tab, fundo(s), piso, chave da excecao em PENDING)
# Rotulo sem fundo proprio mede contra as paginas. Linha, fundo selecionado e
# anel medem contra as paginas e guardam a pior.
COMBOS = [
    ('rotulo-repouso',               'label',                        ('canvas', 'surface'), 4.5, None),
    ('rotulo-hover',                 'label-hover',                  'bg-hover',            4.5, None),
    ('rotulo-pressed',               'label-active',                 'bg-active',           4.5, None),
    ('line-rotulo-selecionado',      'line-label-selected',          ('canvas', 'surface'), 4.5, None),
    ('line-indicador-selecionado',   'line-indicator-selected',      ('canvas', 'surface'), 3.0, None),
    ('line-trilho',                  'line-indicator',               ('canvas', 'surface'), 3.0, 'trilho-decorativo'),
    ('square-rotulo-selecionado',    'square-label-selected',        'square-bg-selected',  4.5, None),
    ('square-rotulo-sel-hover',      'square-label-selected-hover',  'square-bg-selected-hover', 4.5, 'marca-no-hover-escuro'),
    ('square-rotulo-sel-pressed',    'square-label-selected-active', 'square-bg-selected-active', 4.5, None),
    ('square-fundo-selecionado',     'square-bg-selected',           ('canvas', 'surface'), 3.0, 'selecao-tonal'),
    ('square-fundo-sel-pressed',     'square-bg-selected-active',    ('canvas', 'surface'), 3.0, 'pressed-na-superficie-escura'),
    ('anel-foco',                    'ring',                         ('canvas', 'surface'), 3.0, None),
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
    if role in PAGES:
        return PAGES[role]
    if role in RING_INK:
        return RING_INK[role]
    return COLOR[role]


def contrast_rows():
    """Mede cada combinacao renderizada nos dois temas, cada uma contra o piso
    que e dela: texto 4.5:1 do 1.4.3, borda, anel e fundo 3:1 do 1.4.11."""
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
        name = f'tab-{role}'
        alias[name] = ref
        if ref.startswith('#'):
            problems.append(f'{name}: hex solto ({ref}) - todo valor de cor nasce alias do semantico')
            continue
        if ref not in SEM:
            problems.append(f'{name}: aponta para {ref}, que nao existe na camada semantica')
            continue
        light, dark = SEM[ref]
        resolved[name] = {'light': light, 'dark': dark}

    for group in (RING,):
        for role, ref in group.items():
            name = f'tab-{role}'
            alias[name] = ref
            try:
                v = resolve_foundation(ref)
                resolved[name] = {'light': v['light'], 'dark': v['dark']}
            except KeyError:
                problems.append(f'{name}: {ref} nao existe na Foundation')

    for group in (GEOM, TYPE):
        for role, ref in group.items():
            name = f'tab-{role}'
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

    rows = contrast_rows()
    fails = [r for r in rows if not r['pass'] and not r['exception']]
    excs = [r for r in rows if not r['pass'] and r['exception']]

    print('=' * 74)
    print('CAMADA DE TOKENS DO TAB')
    print('=' * 74)
    for name in sorted(alias):
        print(f'  {name:<30} -> {alias[name]}')
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
            'component': 'Tab',
            'version': '0.1.0',
            'foundation': FOUND['meta']['version'],
            'figmaNode': '306:2532',
            'figmaCollection': '17. Tab',
            'variants': ['line', 'square'],
            'sizes': [],
            'states': ['default', 'hover', 'pressed', 'focus'],
            'selected': [False, True],
            'nota': (
                'Aba para trocar conteudo na mesma tela (e, com links, montar sidebar/navbar). '
                'Line marca a selecao pela linha laranja, rotulo text-primary. Square selecionado '
                'e tonal em repouso e escurece na marca no hover/pressed. Foco = repouso + anel. '
                'Um tamanho, sem disabled. Quatro excecoes de contraste declaradas em pending.'
            ),
        },
        'alias': alias,
        'resolved': resolved,
        'contrast': rows,
        'pending': PENDING,
    }
    json.dump(out, open(os.path.join(HERE, 'tokens.json'), 'w'), indent=2, ensure_ascii=False)
    print('\ncomponents/tab/tokens.json escrito')
    write_css(alias)
    return 0


# ---------------------------------------------------------------- css
def css_ref(ref):
    """Traduz a referencia da Foundation para a custom property equivalente."""
    if ref.startswith('focusRing.'):
        return f'var(--al-focus-ring-{ref.split(".")[1]})'
    if ref.startswith('elevation.'):
        return f'var(--al-elevation-{ref.split(".")[1]})'
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


def write_css(alias):
    L = []
    w = L.append
    w('/* AL Design System - tokens do Tab')
    w(' * GERADO por components/tab/tokens.py. Nao editar a mao.')
    w(' *')
    w(' * Nao ha bloco de tema aqui: cada token aponta para um semantico, e o tema')
    w(' * troca no :root - o mesmo elemento onde estes alias sao declarados.')
    w(' */')
    w('')
    w(':root {')

    w('')
    w('  /* os dois tipos, aba nao selecionada - hover e pressed escurecem o rotulo */')
    for role in ('label', 'label-hover', 'label-active', 'bg-hover', 'bg-active'):
        w(f'  --al-tab-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* Line - a linha e de cada aba; a laranja e quem marca a selecao */')
    for role in ('line-label-selected', 'line-indicator', 'line-indicator-selected'):
        w(f'  --al-tab-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* Square selecionado - tonal em repouso, marca no hover e no pressed */')
    for role in ('square-bg-selected', 'square-label-selected',
                 'square-bg-selected-hover', 'square-label-selected-hover',
                 'square-bg-selected-active', 'square-label-selected-active'):
        w(f'  --al-tab-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* anel de foco - aponta para a sombra composta, nao para a cor crua */')
    for role, ref in RING.items():
        w(f'  --al-tab-{role}: {css_ref(ref)};')

    w('')
    w('  /* geometria */')
    for role, ref in GEOM.items():
        w(f'  --al-tab-{role}: {css_ref(ref)};')

    w('')
    w('  /* tipografia - um estilo vira quatro vars */')
    for role, ref in TYPE.items():
        style = resolve_foundation(ref)
        key = _size_key(style[1])
        prefix = f'--al-tab-{role}'.replace('-font', '')
        w(f'  {prefix}-font-size: var(--al-font-size-{key});')
        w(f'  {prefix}-line-height: var(--al-line-height-{key});')
        w(f'  {prefix}-font-weight: {style[3]};')
        w(f'  {prefix}-tracking: {style[4]};')

    w('}')
    w('')

    # Trava herdada do Select: lista de grupo esquecida vira build quebrado,
    # nao variavel faltando em silencio.
    texto = '\n'.join(L)
    faltando = [n for n in alias
                if not n.endswith('-font') and f'--al-{n}:' not in texto]
    if faltando:
        raise AssertionError(
            'tokens fora do CSS (alguma lista de grupo em write_css nao '
            f'foi atualizada): {faltando}')

    path = os.path.join(HERE, 'al-tab-tokens.css')
    open(path, 'w').write(texto)
    print(f'components/tab/al-tab-tokens.css escrito ({os.path.getsize(path)} bytes)')


if __name__ == '__main__':
    sys.exit(run())
