"""
Camada de tokens do Tooltip.

Regra desta camada: nada aqui inventa valor. Todo token aponta para um token da
Foundation pelo NOME. As UNICAS excecoes sao a largura maxima (WIDTH) e os dois
tempos de espera (DELAY), declarados, nomeados e travados pelo portao: a
Foundation nao tem escala de largura de container nem de atraso.

Nomenclatura:
  codigo -> tooltip-padding-y      (hifen)
  Figma  -> padding/y              (collection `23. Tooltip`)
Sao camadas diferentes. Nunca colapsar uma na outra.

PRIMEIRO COMPONENTE DO TIER 5 (08/10/2026)

  `tooltip` - COMPONENT 373:5340 (sem variantes). Icone 20 + texto Body/sm,
  fundo invertido, Elevation/3, padding 8 x 12, gap 8, raio lg, largura
  maxima 280. Primeiro componente do piloto de pipeline em duas sessoes.

  Decisoes da etapa 1: fundo invertido (1), texto 14/20 e padding 8 x 12 (2),
  icone SEMPRE presente (3 e B), sem seta, a 4 do gatilho (4), largura maxima
  280 (5), atraso no componente e nao na Foundation (6), sem borda (A).

SEM TOKEN, DE PROPOSITO

  Altura: sai da conta padding-y x 2 + entrelinha do Body/sm (36). Icone:
  `icon-size-20` direto da Foundation (regra do Tag e do Breadcrumb); a cor
  segue o texto por `currentColor`. Empilhamento: o tooltip mora na top layer
  (popover), entao nao ha z-index.
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
    'bg':   'bg-inverse',                 # decisao 1
    'text': 'text-inverse',               # o icone herda por currentColor
}

# Elevacao: altura, nao estado. Mesma do menu do Breadcrumb.
SHADOW = {
    'shadow': 'elevation.3',
}

# ------------------------------------------------------------ geometria
GEOM = {
    'padding-y': 'space.8',
    'padding-x': 'space.12',
    'gap':       'space.8',               # icone -> texto
    'offset':    'space.4',               # gatilho -> tooltip (sem seta, decisao 4)
    'radius':    'radius.lg',
}

TYPE = {
    'font': 'type.styles.body-sm',
}

# Movimento: popup = o que aparece pequeno por cima da tela (Tooltip e Toast).
MOTION = {
    'duration':     'motion.duration.popup',
    'easing-enter': 'motion.easing.enter',
    'easing-exit':  'motion.easing.exit',
}

# Excecao 1 (mesma da Sidebar, do Modal, do Drawer e do Breadcrumb): a
# Foundation nao tem escala de largura de container. Maxima, nao fixa.
WIDTH = {
    'max-width': 280,
}

# Excecao 2 (decisao 6 de Gui, 08/10/2026): o atraso fica no componente. Se um
# segundo componente precisar de atraso, ele sobe para a Foundation.
#   delay-show - espera do hover antes de abrir (no foco abre na hora)
#   delay-hide - folga para o ponteiro ir do gatilho ao tooltip (WCAG 1.4.13)
DELAY = {
    'delay-show': 500,
    'delay-hide': 100,
}

PENDING = {}

# Fundos sobre os quais o tooltip aparece. Nao sao tokens do Tooltip.
PAGES = {
    'canvas':  'bg-canvas',
    'surface': 'bg-surface',
    'raised':  'bg-surface-raised',
}

# (papel, fg, fundo(s), piso, excecao)
COMBOS = [
    ('texto',       'text', 'bg',                              4.5, None),
    ('icone',       'text', 'bg',                              3.0, None),
    ('caixa',       'bg',   ('canvas', 'surface', 'raised'),   3.0, None),
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
    return PAGES.get(role) or COLOR[role]


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
        name = f'tooltip-{role}'
        alias[name] = ref
        if ref.startswith('#'):
            problems.append(f'{name}: hex solto ({ref})')
        elif ref not in SEM:
            problems.append(f'{name}: aponta para {ref}, que nao existe na camada semantica')
        else:
            resolved[name] = {'light': SEM[ref][0], 'dark': SEM[ref][1]}

    for role, ref in SHADOW.items():
        name = f'tooltip-{role}'
        alias[name] = ref
        try:
            v = resolve_foundation(ref)
            resolved[name] = {'light': v['light'], 'dark': v['dark']}
        except KeyError:
            problems.append(f'{name}: {ref} nao existe na Foundation')

    for group in (GEOM, TYPE, MOTION):
        for role, ref in group.items():
            name = f'tooltip-{role}'
            alias[name] = ref
            try:
                resolved[name] = resolve_foundation(ref)
            except KeyError:
                problems.append(f'{name}: {ref} nao existe na Foundation')

    # Excecoes nomeadas: valor solto so e aceito para estes nomes.
    for role, px in WIDTH.items():
        alias[f'tooltip-{role}'] = f'{px}px'
        resolved[f'tooltip-{role}'] = px
    for role, ms in DELAY.items():
        alias[f'tooltip-{role}'] = f'{ms}ms'
        resolved[f'tooltip-{role}'] = ms

    if problems:
        print(f'{len(problems)} TOKEN(S) REPROVAM O PORTAO DE ALIAS:')
        for p in problems:
            print('   ', p)
        return 1

    rows = contrast_rows()
    fails = [r for r in rows if not r['pass'] and not r['exception']]
    excs = [r for r in rows if not r['pass'] and r['exception']]

    print('=' * 74)
    print('CAMADA DE TOKENS DO TOOLTIP')
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
    n_lit = len(WIDTH) + len(DELAY)
    print(f'{len(alias)} tokens: {len(alias) - n_lit} alias da Foundation, {n_lit} com valor '
          f'declarado (largura maxima e os dois atrasos).')

    out = {
        'meta': {
            'component': 'Tooltip',
            'version': '0.1.0',
            'foundation': FOUND['meta']['version'],
            'figmaNode': '373:5340',
            'figmaCollection': '23. Tooltip',
            'nota': (
                'Fundo invertido (bg-inverse / text-inverse), icone 20 sempre presente seguindo '
                'o texto, Body/sm, padding 8 x 12, gap 8, raio lg, Elevation/3, sem borda e sem '
                'seta, a 4 do gatilho, largura maxima 280. Abre no hover depois de 500ms e no '
                'foco na hora; 100ms de folga para o ponteiro chegar ao tooltip. Sem excecao de '
                'contraste.'
            ),
        },
        'alias': alias,
        'resolved': resolved,
        'contrast': rows,
        'pending': PENDING,
    }
    json.dump(out, open(os.path.join(HERE, 'tokens.json'), 'w'), indent=2, ensure_ascii=False)
    print('\ncomponents/tooltip/tokens.json escrito')
    write_css(alias)
    return 0


# ---------------------------------------------------------------- css
def css_ref(ref):
    if ref.startswith('elevation.'):
        return f'var(--al-elevation-{ref.split(".")[1]})'
    if ref.startswith('space.'):
        return f'var(--al-space-{ref.split(".")[1]})'
    if ref.startswith('radius.'):
        return f'var(--al-radius-{ref.split(".")[1]})'
    if ref.startswith('motion.'):
        _, kind, key = ref.split('.')
        return f'var(--al-motion-{kind}-{key})'
    return f'var(--al-{ref})'          # semantico de cor


def _size_key(font_size):
    for key, v in FOUND['type']['size'].items():
        if v == font_size:
            return key
    raise KeyError(f'type.size com valor {font_size} nao existe na Foundation')


def write_css(alias):
    L = []
    w = L.append
    w('/* AL Design System - tokens do Tooltip')
    w(' * GERADO por components/tooltip/tokens.py. Nao editar a mao.')
    w(' */')
    w('')
    w(':root {')
    w('')
    w('  /* cor - fundo invertido; o tema troca no :root */')
    for role, ref in COLOR.items():
        w(f'  --al-tooltip-{role}: {css_ref(ref)};')
    w('')
    w('  /* elevacao - altura, nao estado */')
    for role, ref in SHADOW.items():
        w(f'  --al-tooltip-{role}: {css_ref(ref)};')
    w('')
    w('  /* geometria */')
    for role, ref in GEOM.items():
        w(f'  --al-tooltip-{role}: {css_ref(ref)};')
    w('')
    w('  /* largura maxima - valor declarado, sem escala na Foundation */')
    for role, px in WIDTH.items():
        w(f'  --al-tooltip-{role}: {px}px;')
    w('')
    w('  /* movimento */')
    for role, ref in MOTION.items():
        w(f'  --al-tooltip-{role}: {css_ref(ref)};')
    w('')
    w('  /* atraso - valor declarado, fica no componente (decisao 6). Lido pelo tooltip.js */')
    for role, ms in DELAY.items():
        w(f'  --al-tooltip-{role}: {ms}ms;')
    w('')
    w('  /* tipografia - um estilo vira quatro vars */')
    for role, ref in TYPE.items():
        style = resolve_foundation(ref)
        key = _size_key(style[1])
        prefix = f'--al-tooltip-{role}'.replace('-font', '')
        w(f'  {prefix}-font-size: var(--al-font-size-{key});')
        w(f'  {prefix}-line-height: var(--al-line-height-{key});')
        w(f'  {prefix}-font-weight: {style[3]};')
        w(f'  {prefix}-tracking: {style[4]};')
    w('}')
    w('')
    texto = '\n'.join(L)
    faltando = [n for n in alias if n != 'tooltip-font' and f'--al-{n}:' not in texto]
    if faltando:
        raise AssertionError(f'tokens fora do CSS: {faltando}')
    path = os.path.join(HERE, 'al-tooltip-tokens.css')
    open(path, 'w').write(texto)
    print(f'components/tooltip/al-tooltip-tokens.css escrito ({os.path.getsize(path)} bytes)')


if __name__ == '__main__':
    sys.exit(run())
