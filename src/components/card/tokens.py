"""
Camada de tokens do Card.

Regra unica desta camada: nada aqui inventa valor. Todo token aponta para um
token da Foundation pelo NOME. O portao no fim do arquivo recusa qualquer
coisa que seja um valor solto - hex, px, numero.

Nomenclatura:
  codigo -> card-border-hover       (hifen)
  Figma  -> border/hover            (collection `16. Card`)
Sao camadas diferentes. Nunca colapsar uma na outra.

SEGUNDO COMPONENTE DO TIER 3 (07/10/2026)

  Component set `card`, node 302:870, pagina `Tier 3` do Figma. 36 variantes:
  `Type` (Filled / Border / Elevated) x `Padding` (Spaced 24 / Default 16 /
  Tight 8) x `Interaction` (estatico ou clicavel) x `State`. O estatico so tem
  repouso; o clicavel tem repouso, hover e foco. Fora por escolha: card
  selecionavel (e Radio/Checkbox), expansivel (e o Accordion), pressionado e
  disabled (card nao se desabilita - se esconde ou se explica).

O FUNDO E `bg-surface-raised`, NAO `bg-canvas`

  No claro os dois sao branco. No escuro a Foundation decidiu que a elevacao
  aparece porque a SUPERFICIE CLAREIA (950 -> 800); a sombra e pista
  secundaria. Com `bg-canvas` o card escuro ficava da cor da tela.

A BORDA E `border-default`, NAO `border-subtle`

  Mesma licao do Divider: `border-subtle` e `bg-surface-raised` sao o mesmo
  neutral-800 no escuro, e a borda sumia (1,00:1). O hover escurece para
  `border-strong` (precedente Material); laranja ficou reservado ao foco, que
  e `border-brand` + anel - o mesmo padrao do Input.

TRES PADDINGS, NOMES QUE NAO CARREGAM O VALOR

  Spaced 24, Default 16, Tight 8. Decisao B de Gui: se a escala mudar, renomeia.

A BORDA E OUTSIDE - DECISAO F DE GUI

  No Figma o stroke e OUTSIDE: nao entra no layout, e os tres tipos medem igual
  sem descontar padding. O CSS reproduz isso desenhando a borda FORA da caixa
  (sombra de 1px ou outline), nao com `border` - e por isso nao ha
  `calc(padding - border-width)` aqui, ao contrario do Button e do Input.
  Os tipos sem borda NAO ganham borda transparente.

FOCO DO ELEVATED SOMA ANEL E SOMBRA - DECISAO D DE GUI

  No Figma a variante so aceita um effect style e o Elevated com foco mostra
  so o anel. No CSS o box-shadow empilha `card-ring` + `card-elevated-shadow`:
  o card nao "afunda" ao receber foco (precedente Material). Sem token novo.

TITULO E DESCRICAO SAO ORIENTACAO, NAO OBRIGACAO - DECISAO E DE GUI

  O card traz titulo e descricao opcionais com tokens proprios, para que a
  familia nao se perca entre produtos (precedente Material/Spectrum). O slot
  aceita qualquer conteudo no lugar deles.

SEM TOKEN, DE PROPOSITO

  Largura e altura: a largura e do conteiner (os 320 do Figma sao exemplo) e
  a altura e padding + conteudo. Clicavel em repouso e identico ao estatico -
  o que muda e marcacao e cursor. O gap de 8 do frame do card no Figma nao faz
  nada (ele tem um filho so, o slot); o que vale e o gap de dentro do slot.

DUAS EXCECOES DECLARADAS DE CONTRASTE

  Ver PENDING.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'tools'))
from paths import FOUNDATION_SRC, TOKENS_JSON, comp_out  # noqa: E402
sys.path.insert(0, FOUNDATION_SRC)

from palette import SEM                     # noqa: E402
from color import cr                      # noqa: E402

FOUND = json.load(open(TOKENS_JSON))   # noqa: E402

# --------------------------------------------------------------- cor
COLOR = {
    'bg':           'bg-surface-raised',

    'border':       'border-default',
    'border-hover': 'border-strong',
    'border-focus': 'border-brand',

    'title':        'text-primary',
    'description':  'text-secondary',
}

# O token aponta para a SOMBRA COMPOSTA, nao para a cor crua - mesma regra do
# `button-*-ring`. A cor so e extraida para medicao, no RING_INK abaixo.
RING = {
    'ring': 'focusRing.default',
}

RING_INK = {
    'ring': 'shadow-focus-default',
}

# Elevacao e altura, nao estado: fica fora da camada de cor de proposito.
SHADOW = {
    'elevated-shadow':       'elevation.2',
    'elevated-shadow-hover': 'elevation.4',
    'filled-shadow-hover':   'elevation.2',
}

# ------------------------------------------------------------ geometria
GEOM = {
    'padding-spaced':  'space.24',
    'padding-default': 'space.16',
    'padding-tight':   'space.8',
    'gap':             'space.8',     # entre blocos dentro do slot
    'text-gap':        'space.4',     # titulo -> descricao
    'radius':          'radius.lg',
    'border-width':    'border.width.1',
}

TYPE = {
    'title-font':       'type.styles.heading-xs',
    'description-font': 'type.styles.body-md',
}

PENDING = {
    'borda-abaixo-de-3-1': (
        'A borda do tipo Border usa `border-default`: 1.57:1 no claro e 1.46:1 no escuro '
        'contra o card, e entre 1.47:1 e 2.42:1 contra as paginas. Abaixo dos 3:1 do WCAG '
        '1.4.11. Decisao C de Gui (07/10/2026): o card se reconhece pelo conteudo, nao pela '
        'linha. A excecao cobre linha DISCRETA, nunca invisivel - por isso nao e '
        '`border-subtle`, que dava 1,00:1 no escuro. NAO "corrigir" escurecendo.'
    ),
    'card-nao-se-separa-pelo-fundo': (
        'O fundo do card contra a pagina: 1.00:1 sobre a tela e 1.07:1 sobre superficie no '
        'claro; 1.66:1 e 1.36:1 no escuro. A separacao vem da borda (Border), da sombra '
        '(Elevated) ou de colocar o Filled sobre `bg-surface` (decisao A de Gui). Quem '
        'sustenta a excecao e a regra de uso da etapa 4: Filled nunca direto sobre a tela.'
    ),
}

# Fundos onde o card e colocado. Nao sao tokens do Card.
PAGES = {
    'canvas':  'bg-canvas',
    'surface': 'bg-surface',
}

# (papel, token do card, fundo(s), piso, chave da excecao em PENDING)
# Texto mede contra o fundo do card. Borda mede contra o card E as paginas e
# guarda a pior. Anel mede contra as paginas: e desenhado fora do card.
COMBOS = [
    ('titulo',           'title',        'bg',                          4.5, None),
    ('descricao',        'description',  'bg',                          4.5, None),
    ('borda-repouso',    'border',       ('bg', 'canvas', 'surface'),   3.0, 'borda-abaixo-de-3-1'),
    ('borda-hover',      'border-hover', ('bg', 'canvas', 'surface'),   3.0, None),
    ('borda-foco',       'border-focus', ('bg', 'canvas', 'surface'),   3.0, None),
    ('anel-foco',        'ring',         ('canvas', 'surface'),         3.0, None),
    ('fundo-na-tela',    'bg',           'canvas',                      3.0, 'card-nao-se-separa-pelo-fundo'),
    ('fundo-em-superficie', 'bg',        'surface',                     3.0, 'card-nao-se-separa-pelo-fundo'),
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
        name = f'card-{role}'
        alias[name] = ref
        if ref.startswith('#'):
            problems.append(f'{name}: hex solto ({ref}) - todo valor de cor nasce alias do semantico')
            continue
        if ref not in SEM:
            problems.append(f'{name}: aponta para {ref}, que nao existe na camada semantica')
            continue
        light, dark = SEM[ref]
        resolved[name] = {'light': light, 'dark': dark}

    for group in (RING, SHADOW):
        for role, ref in group.items():
            name = f'card-{role}'
            alias[name] = ref
            try:
                v = resolve_foundation(ref)
                resolved[name] = {'light': v['light'], 'dark': v['dark']}
            except KeyError:
                problems.append(f'{name}: {ref} nao existe na Foundation')

    for group in (GEOM, TYPE):
        for role, ref in group.items():
            name = f'card-{role}'
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
    print('CAMADA DE TOKENS DO CARD')
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
            'component': 'Card',
            'version': '0.1.0',
            'foundation': FOUND['meta']['version'],
            'figmaNode': '302:870',
            'figmaCollection': '16. Card',
            'variants': ['filled', 'border', 'elevated'],
            'sizes': ['spaced', 'default', 'tight'],
            'states': ['default', 'hover', 'focus'],
            'nota': (
                'Conteiner de conteudo, estatico ou clicavel. Tres tipos (Filled, Border, '
                'Elevated) e tres paddings (24/16/8). Fundo bg-surface-raised: no escuro a '
                'superficie clareia. Borda outside (nao entra no layout) e foco = border-brand '
                '+ anel no Border; no Elevated o foco soma anel e sombra. Titulo e descricao '
                'sao opcionais e substituiveis pelo slot. Duas excecoes de contraste '
                'declaradas em pending.'
            ),
        },
        'alias': alias,
        'resolved': resolved,
        'contrast': rows,
        'pending': PENDING,
    }
    json.dump(out, open(comp_out('card', 'tokens.json'), 'w'), indent=2, ensure_ascii=False)
    print('\nbuild/components/card/tokens.json escrito')
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
    w('/* AL Design System - tokens do Card')
    w(' * GERADO por components/card/tokens.py. Nao editar a mao.')
    w(' *')
    w(' * Nao ha bloco de tema aqui: cada token aponta para um semantico, e o tema')
    w(' * troca no :root - o mesmo elemento onde estes alias sao declarados.')
    w(' */')
    w('')
    w(':root {')

    w('')
    w('  /* fundo - o mesmo nos tres tipos */')
    w(f'  --al-card-bg: {css_ref(COLOR["bg"])};')

    w('')
    w('  /* borda do tipo Border - laranja so no foco */')
    for role in ('border', 'border-hover', 'border-focus'):
        w(f'  --al-card-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* titulo e descricao - opcionais, substituiveis pelo slot */')
    for role in ('title', 'description'):
        w(f'  --al-card-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* anel de foco - aponta para a sombra composta, nao para a cor crua */')
    for role, ref in RING.items():
        w(f'  --al-card-{role}: {css_ref(ref)};')

    w('')
    w('  /* elevacao - altura, nao estado */')
    for role, ref in SHADOW.items():
        w(f'  --al-card-{role}: {css_ref(ref)};')

    w('')
    w('  /* geometria */')
    for role, ref in GEOM.items():
        w(f'  --al-card-{role}: {css_ref(ref)};')

    w('')
    w('  /* tipografia - um estilo vira quatro vars */')
    for role, ref in TYPE.items():
        style = resolve_foundation(ref)
        key = _size_key(style[1])
        prefix = f'--al-card-{role}'.replace('-font', '')
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

    path = comp_out('card', 'al-card-tokens.css')
    open(path, 'w').write(texto)
    print(f'build/components/card/al-card-tokens.css escrito ({os.path.getsize(path)} bytes)')


if __name__ == '__main__':
    sys.exit(run())
