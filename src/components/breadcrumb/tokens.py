"""
Camada de tokens do Breadcrumb (com o `_breadcrumb-more`).

Regra desta camada: nada aqui inventa valor. Todo token aponta para um token da
Foundation pelo NOME. A UNICA excecao e a largura minima do menu (WIDTH,
abaixo), declarada, nomeada e travada pelo portao - a mesma da Sidebar, do
Modal e do Drawer: a Foundation nao tem escala de largura de container.

Nomenclatura:
  codigo -> breadcrumb-menu-bg      (hifen)
  Figma  -> menu/bg                 (collection `22. Breadcrumb`)
Sao camadas diferentes. Nunca colapsar uma na outra.

ULTIMO COMPONENTE DO TIER 4 (08/10/2026)

  Dois componentes que andam juntos em todas as etapas, pagina `Tier 4` do
  Figma:
    `breadcrumb`        COMPONENT_SET 339:3785 - Size Short (2 niveis), Medium
                        (3) e Large (primeiro, segundo, `...`, atual). Props de
                        texto First page, Second page, Current page.
    `_breadcrumb-more`  COMPONENT_SET 339:4046 - State Opened / Closed. O `...`
                        e o gatilho; o menu sai 8 abaixo, centralizado, com
                        itens Tab Square.

  Decisoes da etapa 1: sem hover (so o cursor muda); menu = botao + lista de
  links com JS pequeno (5a); colapsa com 5 niveis ou mais, no formato da Large
  (6); pagina atual e texto com aria-current, nao link (7); separador em
  `text-secondary` (8, Gui ajustou no Figma); quebra de linha em tela estreita
  (9); foco com o anel padrao (10). Menu com Elevation/3 (4, Gui criou).
  Etapa 3: largura minima 108, o menu cresce com o texto (A = a).

O ITEM DO MENU E O TAB

  Cada item do menu e um Tab Square (texto, padding, raio e rotulo vem de
  components/tab/tokens.py). O que muda e o fundo de hover e pressed: o menu
  mora em `bg-surface-raised`, onde `bg-hover` some no escuro (1,00:1) - o
  mesmo defeito do Modal 0.18.1. Por isso os dois `-raised` abaixo.

SEM TOKEN, DE PROPOSITO

  Altura: sai da entrelinha do Label/md (20). Tamanho do separador:
  `icon-size-16` direto da Foundation (regra do Tag e do Icon Button). Posicao
  horizontal do menu: centralizado sob o `...`, calculado no CSS.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'tools'))
from paths import FOUNDATION_SRC, TOKENS_JSON, comp_out  # noqa: E402
sys.path.insert(0, FOUNDATION_SRC)

from palette import SEM                     # noqa: E402
from tokenlib import resolve_foundation, css_ref, size_key, save_css  # noqa: E402
from color import cr                      # noqa: E402

FOUND = json.load(open(TOKENS_JSON))   # noqa: E402

# --------------------------------------------------------------- cor
COLOR = {
    'link':      'text-secondary',
    'current':   'text-brand',
    'separator': 'text-secondary',        # decisao 8 (Gui ajustou no Figma)
    'more':      'text-secondary',        # o gatilho `...`

    'menu-bg':             'bg-surface-raised',
    'menu-border':         'border-default',
    'menu-item-bg-hover':  'bg-hover-raised',
    'menu-item-bg-active': 'bg-active-raised',
}

# Anel de foco: aponta para a sombra composta da Foundation, como o
# `button-*-ring`. A cor so e extraida para medicao, no RING_INK abaixo.
RING = {
    'ring': 'focusRing.default',
}

RING_INK = {
    'ring': 'shadow-focus-default',
}

# Elevacao: altura, nao estado (decisao 4 de Gui, Elevation/3).
SHADOW = {
    'menu-shadow': 'elevation.3',
}

# ------------------------------------------------------------ geometria
GEOM = {
    'gap':               'space.8',           # item -> separador -> item
    'ring-radius':       'radius.sm',         # canto do anel em link e `…` (decisao C)
    'menu-padding':      'space.8',
    'menu-gap':          'space.8',           # entre itens do menu
    'menu-offset':       'space.8',           # `...` -> menu
    'menu-radius':       'radius.xl',
    'menu-border-width': 'border.width.1',
}

TYPE = {
    'label-font': 'type.styles.label-md',
}

# UNICA excecao a "todo token e alias" (mesma da Sidebar, do Modal e do Drawer):
# a Foundation nao tem escala de largura de container. Minima, nao fixa: o menu
# cresce com o nome da pagina (decisao A de Gui, 08/10/2026).
WIDTH = {
    'menu-min-width': 108,
}

PENDING = {
    'borda-de-regiao': (
        'A borda do menu (`border-default`) da 1.57:1 no claro e 2.42:1 no escuro contra a '
        'tela, e 1.47:1 / 1.98:1 contra uma pagina em `bg-surface`. O 3:1 do WCAG 1.4.11 vale '
        'para o contorno de CONTROLES; o menu e uma caixa de conteudo, reconhecida pelos itens '
        'e, desde a etapa 1, pela sombra Elevation/3. Mesmo raciocinio da Sidebar e do Card. '
        'NAO "corrigir" escurecendo.'
    ),
}

# Fundos sobre os quais o breadcrumb fica. Nao sao tokens do Breadcrumb.
PAGES = {
    'canvas':  'bg-canvas',
    'surface': 'bg-surface',
}

# Rotulo do item do menu: vem do Tab Square (tab-label, tab-label-hover).
TAB_INK = {
    'item':       'text-secondary',
    'item-hover': 'text-primary',
}

# (papel, fg, fundo(s), piso, excecao)
COMBOS = [
    ('link',             'link',       ('canvas', 'surface'),     4.5, None),
    ('pagina-atual',     'current',    ('canvas', 'surface'),     4.5, None),
    ('mais',             'more',       ('canvas', 'surface'),     4.5, None),
    ('item-menu',        'item',       'menu-bg',                 4.5, None),
    ('item-menu-hover',  'item-hover', 'menu-item-bg-hover',      4.5, None),
    ('item-menu-active', 'item-hover', 'menu-item-bg-active',     4.5, None),
    ('anel-trilha',      'ring',       ('canvas', 'surface'),     3.0, None),
    ('anel-menu',        'ring',       'menu-bg',                 3.0, None),
    ('borda-menu',       'menu-border', ('canvas', 'surface'),    3.0, 'borda-de-regiao'),
]


# ---------------------------------------------------------------- portao
def ink(role):
    """O semantico de cor por tras de um papel - seguindo o anel ate a cor."""
    for table in (PAGES, RING_INK, TAB_INK):
        if role in table:
            return table[role]
    return COLOR[role]


def contrast_rows():
    rows = []
    for what, fg, bgs, min_ratio, exc in COMBOS:
        if isinstance(bgs, str):
            bgs = (bgs,)
        for theme, i in (('light', 0), ('dark', 1)):
            for bg in bgs:
                a, b = SEM[ink(fg)][i], SEM[ink(bg)][i]
                ratio = round(cr(a, b), 2)
                rows.append({'theme': theme, 'what': f'{what}/{bg}', 'fg': a, 'bg': b,
                             'ratio': ratio, 'min': min_ratio,
                             'pass': ratio >= min_ratio, 'exception': exc})
    return rows


def run():
    alias, resolved, problems = {}, {}, []

    for role, ref in COLOR.items():
        name = f'breadcrumb-{role}'
        alias[name] = ref
        if ref.startswith('#'):
            problems.append(f'{name}: hex solto ({ref})')
        elif ref not in SEM:
            problems.append(f'{name}: aponta para {ref}, que nao existe na camada semantica')
        else:
            resolved[name] = {'light': SEM[ref][0], 'dark': SEM[ref][1]}

    for group in (RING, SHADOW):
        for role, ref in group.items():
            name = f'breadcrumb-{role}'
            alias[name] = ref
            try:
                v = resolve_foundation(ref)
                resolved[name] = {'light': v['light'], 'dark': v['dark']}
            except KeyError:
                problems.append(f'{name}: {ref} nao existe na Foundation')

    for group in (GEOM, TYPE):
        for role, ref in group.items():
            name = f'breadcrumb-{role}'
            alias[name] = ref
            try:
                resolved[name] = resolve_foundation(ref)
            except KeyError:
                problems.append(f'{name}: {ref} nao existe na Foundation')

    # Excecao nomeada: valor solto so e aceito para este nome.
    for role, px in WIDTH.items():
        name = f'breadcrumb-{role}'
        alias[name] = f'{px}px'
        resolved[name] = px

    if problems:
        print(f'{len(problems)} TOKEN(S) REPROVAM O PORTAO DE ALIAS:')
        for p in problems:
            print('   ', p)
        return 1

    rows = contrast_rows()
    fails = [r for r in rows if not r['pass'] and not r['exception']]
    excs = [r for r in rows if not r['pass'] and r['exception']]

    print('=' * 74)
    print('CAMADA DE TOKENS DO BREADCRUMB')
    print('=' * 74)
    for name in sorted(alias):
        print(f'  {name:<34} -> {alias[name]}')
    print('-' * 74)
    for r in rows:
        tag = 'OK  ' if r['pass'] else ('EXCE' if r['exception'] else 'FALHA')
        print(f'  {tag} {r["what"]:<34} {r["theme"]:<5} {r["fg"]} / {r["bg"]}  {r["ratio"]}:1 (piso {r["min"]})')
    print(f'contraste: {len(rows)} medicoes  |  passam: {len(rows) - len(fails) - len(excs)}  |  '
          f'excecoes declaradas: {len(excs)}  |  reprovas: {len(fails)}')
    if fails:
        print(f'{len(fails)} COMBINACAO(OES) REPROVAM O PORTAO DE CONTRASTE')
        return 1
    n_lit = len(WIDTH)
    print(f'{len(alias)} tokens: {len(alias) - n_lit} alias da Foundation, {n_lit} largura com valor '
          f'declarado (mesma excecao da Sidebar, do Modal e do Drawer).')

    out = {
        'meta': {
            'component': 'Breadcrumb',
            'version': '0.1.0',
            'foundation': FOUND['meta']['version'],
            'figmaNode': '339:3785 + 339:4046',
            'figmaCollection': '22. Breadcrumb',
            'nota': (
                'Trilha de navegacao: links em text-secondary, pagina atual em text-brand (texto, '
                'nao link), separador chevron 16 em text-secondary, Label/md, gap 8. Com 5 niveis '
                'ou mais os do meio vao para o menu do `...` (bg-surface-raised, borda, raio xl, '
                'Elevation/3, itens Tab Square com hover -raised). Sem hover na trilha: so o '
                'cursor muda. Uma excecao de contraste em pending.'
            ),
        },
        'alias': alias,
        'resolved': resolved,
        'contrast': rows,
        'pending': PENDING,
    }
    json.dump(out, open(comp_out('breadcrumb', 'tokens.json'), 'w'), indent=2, ensure_ascii=False)
    print('\nbuild/components/breadcrumb/tokens.json escrito')
    write_css(alias)
    return 0


# ---------------------------------------------------------------- css
def write_css(alias):
    L = []
    w = L.append
    w('/* AL Design System - tokens do Breadcrumb (com o _breadcrumb-more)')
    w(' * GERADO por src/components/breadcrumb/tokens.py. Nao editar a mao.')
    w(' */')
    w('')
    w(':root {')
    w('')
    w('  /* trilha - o tema troca no :root */')
    for role in ('link', 'current', 'separator', 'more'):
        w(f'  --al-breadcrumb-{role}: {css_ref(COLOR[role])};')
    w('')
    w('  /* menu do ... - hover e pressed -raised (o menu mora em surface-raised) */')
    for role in ('menu-bg', 'menu-border', 'menu-item-bg-hover', 'menu-item-bg-active'):
        w(f'  --al-breadcrumb-{role}: {css_ref(COLOR[role])};')
    w('')
    w('  /* anel de foco - aponta para a sombra composta, nao para a cor crua */')
    for role, ref in RING.items():
        w(f'  --al-breadcrumb-{role}: {css_ref(ref)};')
    w('')
    w('  /* elevacao do menu - altura, nao estado */')
    for role, ref in SHADOW.items():
        w(f'  --al-breadcrumb-{role}: {css_ref(ref)};')
    w('')
    w('  /* geometria */')
    for role, ref in GEOM.items():
        w(f'  --al-breadcrumb-{role}: {css_ref(ref)};')
    w('')
    w('  /* largura minima do menu - valor declarado, sem escala na Foundation */')
    for role, px in WIDTH.items():
        w(f'  --al-breadcrumb-{role}: {px}px;')
    w('')
    w('  /* tipografia - um estilo vira quatro vars */')
    for role, ref in TYPE.items():
        style = resolve_foundation(ref)
        key = size_key(style[1])
        prefix = f'--al-breadcrumb-{role}'.replace('-font', '')
        w(f'  {prefix}-font-size: var(--al-font-size-{key});')
        w(f'  {prefix}-line-height: var(--al-line-height-{key});')
        w(f'  {prefix}-font-weight: {style[3]};')
        w(f'  {prefix}-tracking: {style[4]};')
    w('}')
    w('')
    texto = '\n'.join(L)
    faltando = [n for n in alias if not n.endswith('-font') and f'--al-{n}:' not in texto]
    if faltando:
        raise AssertionError(f'tokens fora do CSS: {faltando}')
    save_css('breadcrumb', texto)


if __name__ == '__main__':
    sys.exit(run())
