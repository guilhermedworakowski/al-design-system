"""
Camada de tokens do Sidebar.

Regra desta camada: nada aqui inventa valor. Todo token aponta para um token da
Foundation pelo NOME. A UNICA excecao e a largura (WIDTH, abaixo), declarada,
nomeada e travada pelo portao - a mesma do Modal e do Drawer: a Foundation nao
tem escala de largura de container.

Nomenclatura:
  codigo -> sidebar-profile-gap     (hifen)
  Figma  -> profile/gap             (collection `21. Sidebar`)
Sao camadas diferentes. Nunca colapsar uma na outra.

PRIMEIRO COMPONENTE DO TIER 4 (08/10/2026)

  Componente `sidebar`, node 339:2916, pagina `Tier 4` do Figma. Uma variante
  so, 296 de largura. Cabecalho de perfil (Avatar md + nome + e-mail + Icon
  Button Ghost sm), slot `content` com os grupos de navegacao e a secao de
  Ajuda (rotulo de grupo + itens). Props: `Avatar`, `Support area`, `Support`
  (texto), `Item 1..3`, `content` (slot).

  Decisoes da etapa 1: fundo `bg-canvas` com borda a direita em
  `border-default` (A), e-mail em `text-secondary` (B), perfil com Icon Button
  (C), itens sem icone (D), sem aninhamento (E), altura da tela com so o miolo
  rolando (F), no celular vira painel modal pela esquerda reaproveitando o
  Drawer (G), sem modo recolhido (H).

O ITEM E O TAB

  Cada item e um Tab Square de largura cheia (regra 4 e decisao J do Tab). Os
  pares dele ja foram medidos sobre `bg-canvas` em components/tab/tokens.py, e
  o botao do perfil em components/icon-button/tokens.py. Por isso o fundo da
  sidebar e a tela: com `bg-surface-raised` o hover sumia no escuro (1,00:1).

SEM TOKEN, DE PROPOSITO

  Altura: 100dvh (o 1024 do Figma e so o quadro). Raio: nenhum, a sidebar cola
  na borda da tela. Item, Avatar e Icon Button: tokens dos proprios
  componentes. Celular: scrim, duracao e sombra do Drawer, no CSS da etapa 5.
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
    'bg':          'bg-canvas',
    'border':      'border-default',      # a cor do Divider
    'name':        'text-primary',
    'email':       'text-secondary',
    'group-label': 'text-secondary',
}

# ------------------------------------------------------------ geometria
GEOM = {
    'border-width':      'border.width.1',
    'padding':           'space.24',
    'gap':               'space.24',      # perfil / miolo / ajuda, e entre grupos
    'profile-gap':       'space.8',       # avatar -> textos
    'profile-text-gap':  'space.4',       # nome -> e-mail, textos -> botao
    'group-gap':         'space.16',      # rotulo do grupo -> itens
    'item-gap':          'space.8',       # entre itens
}

TYPE = {
    'name-font':        'type.styles.heading-xs',
    'email-font':       'type.styles.body-sm',
    'group-label-font': 'type.styles.code-md',
}

# Estilos que nao usam a familia padrao (sans).
MONO = {'group-label-font'}

# UNICA excecao a "todo token e alias" (mesma do Modal e do Drawer): a
# Foundation nao tem escala de largura de container. Quando existir, vira alias.
WIDTH = {
    'width': 296,
}

PENDING = {
    'borda-de-regiao': (
        'A linha a direita (`border-default`) da 1.57:1 no claro e 2.42:1 no escuro contra a '
        'sidebar, e 1.47:1 / 1.98:1 contra uma pagina em `bg-surface`. O 3:1 do WCAG 1.4.11 '
        'vale para o contorno de CONTROLES; a sidebar e uma regiao da pagina, reconhecida pelo '
        'conteudo e, no leitor de tela, pelo nome do <nav>. Mesmo raciocinio do Divider e da '
        'borda do Card (decisao A de Gui, 08/10/2026). NAO "corrigir" escurecendo.'
    ),
}

# Fundos ao lado dos quais a sidebar fica. Nao sao tokens do Sidebar.
PAGES = {
    'canvas':  'bg-canvas',
    'surface': 'bg-surface',
}

# (papel, fg, fundo(s), piso, excecao)
COMBOS = [
    ('nome',          'name',        'bg',                 4.5, None),
    ('email',         'email',       'bg',                 4.5, None),
    ('rotulo-grupo',  'group-label', 'bg',                 4.5, None),
    ('borda',         'border',      ('bg', 'surface'),    3.0, 'borda-de-regiao'),
]


# ---------------------------------------------------------------- portao
def resolve_foundation(path):
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
    if role in PAGES:
        return PAGES[role]
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
        name = f'sidebar-{role}'
        alias[name] = ref
        if ref.startswith('#'):
            problems.append(f'{name}: hex solto ({ref})')
        elif ref not in SEM:
            problems.append(f'{name}: aponta para {ref}, que nao existe na camada semantica')
        else:
            resolved[name] = {'light': SEM[ref][0], 'dark': SEM[ref][1]}

    for group in (GEOM, TYPE):
        for role, ref in group.items():
            name = f'sidebar-{role}'
            alias[name] = ref
            try:
                resolved[name] = resolve_foundation(ref)
            except KeyError:
                problems.append(f'{name}: {ref} nao existe na Foundation')

    # Excecao nomeada: valor solto so e aceito para este nome.
    for role, px in WIDTH.items():
        name = f'sidebar-{role}'
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
    print('CAMADA DE TOKENS DO SIDEBAR')
    print('=' * 74)
    for name in sorted(alias):
        print(f'  {name:<30} -> {alias[name]}')
    print('-' * 74)
    for r in rows:
        tag = 'OK  ' if r['pass'] else ('EXCE' if r['exception'] else 'FALHA')
        print(f'  {tag} {r["what"]:<24} {r["theme"]:<5} {r["fg"]} / {r["bg"]}  {r["ratio"]}:1 (piso {r["min"]})')
    print(f'contraste: {len(rows)} medicoes  |  passam: {len(rows) - len(fails) - len(excs)}  |  '
          f'excecoes declaradas: {len(excs)}  |  reprovas: {len(fails)}')
    if fails:
        print(f'{len(fails)} COMBINACAO(OES) REPROVAM O PORTAO DE CONTRASTE')
        return 1
    n_lit = len(WIDTH)
    print(f'{len(alias)} tokens: {len(alias) - n_lit} alias da Foundation, {n_lit} largura com valor '
          f'declarado (mesma excecao do Modal e do Drawer).')

    out = {
        'meta': {
            'component': 'Sidebar',
            'version': '0.1.0',
            'foundation': FOUND['meta']['version'],
            'figmaNode': '339:2916',
            'figmaCollection': '21. Sidebar',
            'nota': (
                'Navegacao lateral fixa, 296 de largura, fundo bg-canvas com borda a direita em '
                'border-default. Perfil, slot de grupos e secao de Ajuda; itens sao Tab Square de '
                'largura cheia. Altura da tela, so o miolo rola. No celular vira painel modal pela '
                'esquerda (mecanismo do Drawer). Uma excecao de contraste em pending.'
            ),
        },
        'alias': alias,
        'resolved': resolved,
        'contrast': rows,
        'pending': PENDING,
    }
    json.dump(out, open(comp_out('sidebar', 'tokens.json'), 'w'), indent=2, ensure_ascii=False)
    print('\nbuild/components/sidebar/tokens.json escrito')
    write_css(alias)
    return 0


# ---------------------------------------------------------------- css
def css_ref(ref):
    if ref.startswith('space.'):
        return f'var(--al-space-{ref.split(".")[1]})'
    if ref.startswith('border.width.'):
        return f'var(--al-border-width-{ref.split(".")[2]})'
    return f'var(--al-{ref})'


def _size_key(font_size):
    for key, v in FOUND['type']['size'].items():
        if v == font_size:
            return key
    raise KeyError(f'type.size com valor {font_size} nao existe na Foundation')


def write_css(alias):
    L = []
    w = L.append
    w('/* AL Design System - tokens do Sidebar')
    w(' * GERADO por components/sidebar/tokens.py. Nao editar a mao.')
    w(' */')
    w('')
    w(':root {')
    w('')
    w('  /* cor - o tema troca no :root */')
    for role, ref in COLOR.items():
        w(f'  --al-sidebar-{role}: {css_ref(ref)};')
    w('')
    w('  /* geometria */')
    for role, ref in GEOM.items():
        w(f'  --al-sidebar-{role}: {css_ref(ref)};')
    w('')
    w('  /* largura - valor declarado, sem escala na Foundation (mesma excecao do Modal e do Drawer) */')
    for role, px in WIDTH.items():
        w(f'  --al-sidebar-{role}: {px}px;')
    w('')
    w('  /* tipografia - um estilo vira quatro vars (cinco no rotulo, que e mono) */')
    for role, ref in TYPE.items():
        style = resolve_foundation(ref)
        key = _size_key(style[1])
        prefix = f'--al-sidebar-{role}'.replace('-font', '')
        if role in MONO:
            w(f'  {prefix}-font-family: var(--al-font-mono);')
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
    path = comp_out('sidebar', 'al-sidebar-tokens.css')
    open(path, 'w').write(texto)
    print(f'build/components/sidebar/al-sidebar-tokens.css escrito ({os.path.getsize(path)} bytes)')


if __name__ == '__main__':
    sys.exit(run())
