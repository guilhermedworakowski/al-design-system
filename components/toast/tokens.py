"""
Camada de tokens do Toast.

Regra desta camada: nada aqui inventa valor. Todo token aponta para um token da
Foundation pelo NOME. As UNICAS excecoes sao a largura maxima (WIDTH) e o tempo
na tela (TIMEOUT), declarados, nomeados e travados pelo portao: a Foundation
nao tem escala de largura de container nem de tempo de espera.

Nomenclatura:
  codigo -> toast-success-border   (hifen)
  Figma  -> success/border         (collection `24. Toast`)
Sao camadas diferentes. Nunca colapsar uma na outra.

SEGUNDO COMPONENTE DO TIER 5 (08/10/2026)

  Component set `Toast`, node 373:5287. 4 variantes `Status` (Success /
  Warning / Error / Info) e o booleano da descricao. Icone 20 alinhado ao topo
  + titulo Label/md + descricao Body/sm opcional + X (Icon Button Ghost sm).
  Fundo bg-surface-raised, borda 1px na cor do status, raio lg, Elevation/3,
  padding 12, gap 8, 4 entre titulo e descricao, largura maxima 380.

  Decisoes da etapa 1: icone no topo e 20 (1, 2), triangulo no Warning e
  circulo com exclamacao no Error (3), descricao opcional (4), sem acao (5),
  sem Neutral (6), Success/Info somem em 6s e Warning/Error ficam (7), um por
  vez, canto inferior direito a 16 das bordas (8), fila (D).

O STATUS "error" USA O SEMANTICO "danger"

  Mesmo mapeamento do Tag: o nome do status e o do produto, a cor e a da
  Foundation.

A BORDA E INSIDE

  No Figma o stroke nao entra no layout: 12 + 20 + 4 + 20 + 12 = 68 com a
  borda por cima do padding. O CSS reproduz com `calc(padding - border-width)`,
  como o Button e o Input.

SEM TOKEN, DE PROPOSITO

  Altura: sai da conta (68 com descricao, 60 sem - o X de 36 manda). Icone:
  `icon-size-20` direto da Foundation (regra do Tag e do Tooltip). X: e o Icon
  Button Ghost sm; sobre bg-surface-raised o hover usa `bg-hover-raised` /
  `bg-active-raised` (licao do Modal 0.18.1), sem token novo. Empilhamento:
  o toast mora na top layer (popover), entao nao ha z-index.
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
    'bg':          'bg-surface-raised',
    'title':       'text-primary',
    'description': 'text-secondary',
}

# Status -> semantico. O icone e a borda carregam o status; o icone e a pista
# que nao depende de cor (Spectrum), a borda e decorativa e passa no 3:1 igual.
STATUS = {
    'success': 'success',
    'warning': 'warning',
    'error':   'danger',
    'info':    'info',
}
for status, sem in STATUS.items():
    COLOR[f'{status}-icon'] = f'text-{sem}'
    COLOR[f'{status}-border'] = f'border-{sem}'

# Elevacao: altura, nao estado. Mesma do Tooltip.
SHADOW = {
    'shadow': 'elevation.3',
}

# ------------------------------------------------------------ geometria
GEOM = {
    'padding':      'space.12',
    'gap':          'space.8',              # icone -> texto -> X
    'text-gap':     'space.4',              # titulo -> descricao
    'radius':       'radius.lg',
    'border-width': 'border.width.1',
    'offset':       'space.16',             # caixa -> borda da tela (decisao 8)
}

TYPE = {
    'title-font':       'type.styles.label-md',
    'description-font': 'type.styles.body-sm',
}

# Movimento: popup = o que aparece pequeno por cima da tela (Tooltip e Toast).
MOTION = {
    'duration':     'motion.duration.popup',
    'easing-enter': 'motion.easing.enter',
    'easing-exit':  'motion.easing.exit',
}

# Excecao 1 (mesma da Sidebar, do Modal, do Drawer e do Tooltip): a Foundation
# nao tem escala de largura de container. Maxima, nao fixa - no celular a
# caixa encolhe ate sobrar o offset dos dois lados.
WIDTH = {
    'max-width': 380,
}

# Excecao 2 (decisao 7 de Gui, 08/10/2026): o tempo na tela de Success e Info
# fica no componente, como os atrasos do Tooltip. Warning e Error nao somem.
TIMEOUT = {
    'timeout': 6000,
}

PENDING = {}

# Telas sobre as quais o toast aparece. Nao sao tokens do Toast.
PAGES = {
    'canvas':  'bg-canvas',
    'surface': 'bg-surface',
}

# (papel, fg, fundo(s), piso, excecao)
COMBOS = [
    ('titulo',    'title',       'bg', 4.5, None),
    ('descricao', 'description', 'bg', 4.5, None),
]
for status in STATUS:
    COMBOS.append((f'{status}/icone', f'{status}-icon', 'bg', 3.0, None))
    COMBOS.append((f'{status}/borda', f'{status}-border', ('bg', 'canvas', 'surface'), 3.0, None))


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
        name = f'toast-{role}'
        alias[name] = ref
        if ref.startswith('#'):
            problems.append(f'{name}: hex solto ({ref})')
        elif ref not in SEM:
            problems.append(f'{name}: aponta para {ref}, que nao existe na camada semantica')
        else:
            resolved[name] = {'light': SEM[ref][0], 'dark': SEM[ref][1]}

    for role, ref in SHADOW.items():
        name = f'toast-{role}'
        alias[name] = ref
        try:
            v = resolve_foundation(ref)
            resolved[name] = {'light': v['light'], 'dark': v['dark']}
        except KeyError:
            problems.append(f'{name}: {ref} nao existe na Foundation')

    for group in (GEOM, TYPE, MOTION):
        for role, ref in group.items():
            name = f'toast-{role}'
            alias[name] = ref
            try:
                resolved[name] = resolve_foundation(ref)
            except KeyError:
                problems.append(f'{name}: {ref} nao existe na Foundation')

    # Excecoes nomeadas: valor solto so e aceito para estes nomes.
    for role, px in WIDTH.items():
        alias[f'toast-{role}'] = f'{px}px'
        resolved[f'toast-{role}'] = px
    for role, ms in TIMEOUT.items():
        alias[f'toast-{role}'] = f'{ms}ms'
        resolved[f'toast-{role}'] = ms

    if problems:
        print(f'{len(problems)} TOKEN(S) REPROVAM O PORTAO DE ALIAS:')
        for p in problems:
            print('   ', p)
        return 1

    rows = contrast_rows()
    fails = [r for r in rows if not r['pass'] and not r['exception']]
    excs = [r for r in rows if not r['pass'] and r['exception']]

    print('=' * 74)
    print('CAMADA DE TOKENS DO TOAST')
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
    n_lit = len(WIDTH) + len(TIMEOUT)
    print(f'{len(alias)} tokens: {len(alias) - n_lit} alias da Foundation, {n_lit} com valor '
          f'declarado (largura maxima e tempo na tela).')

    out = {
        'meta': {
            'component': 'Toast',
            'version': '0.1.0',
            'foundation': FOUND['meta']['version'],
            'figmaNode': '373:5287',
            'figmaCollection': '24. Toast',
            'nota': (
                'Fundo bg-surface-raised, borda 1px e icone 20 na cor do status (error usa o '
                'semantico danger), titulo Label/md, descricao Body/sm opcional, padding 12, '
                'gap 8, raio lg, Elevation/3, largura maxima 380, a 16 das bordas da tela. '
                'Success e Info somem em 6s (pausa em hover e foco); Warning e Error ficam. '
                'Um por vez, em fila. Sem excecao de contraste.'
            ),
        },
        'alias': alias,
        'resolved': resolved,
        'contrast': rows,
        'pending': PENDING,
    }
    json.dump(out, open(os.path.join(HERE, 'tokens.json'), 'w'), indent=2, ensure_ascii=False)
    print('\ncomponents/toast/tokens.json escrito')
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
    if ref.startswith('border.width.'):
        return f'var(--al-border-width-{ref.split(".")[2]})'
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
    w('/* AL Design System - tokens do Toast')
    w(' * GERADO por components/toast/tokens.py. Nao editar a mao.')
    w(' */')
    w('')
    w(':root {')
    w('')
    w('  /* cor - caixa e texto */')
    for role in ('bg', 'title', 'description'):
        w(f'  --al-toast-{role}: {css_ref(COLOR[role])};')
    w('')
    w('  /* cor - status: icone e borda */')
    for status in STATUS:
        for part in ('icon', 'border'):
            role = f'{status}-{part}'
            w(f'  --al-toast-{role}: {css_ref(COLOR[role])};')
    w('')
    w('  /* elevacao - altura, nao estado */')
    for role, ref in SHADOW.items():
        w(f'  --al-toast-{role}: {css_ref(ref)};')
    w('')
    w('  /* geometria */')
    for role, ref in GEOM.items():
        w(f'  --al-toast-{role}: {css_ref(ref)};')
    w('')
    w('  /* largura maxima - valor declarado, sem escala na Foundation */')
    for role, px in WIDTH.items():
        w(f'  --al-toast-{role}: {px}px;')
    w('')
    w('  /* movimento */')
    for role, ref in MOTION.items():
        w(f'  --al-toast-{role}: {css_ref(ref)};')
    w('')
    w('  /* tempo na tela de Success e Info - valor declarado (decisao 7). Lido pelo toast.js */')
    for role, ms in TIMEOUT.items():
        w(f'  --al-toast-{role}: {ms}ms;')
    w('')
    w('  /* tipografia - cada estilo vira quatro vars */')
    for role, ref in TYPE.items():
        style = resolve_foundation(ref)
        key = _size_key(style[1])
        prefix = f'--al-toast-{role}'.replace('-font', '')
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
    path = os.path.join(HERE, 'al-toast-tokens.css')
    open(path, 'w').write(texto)
    print(f'components/toast/al-toast-tokens.css escrito ({os.path.getsize(path)} bytes)')


if __name__ == '__main__':
    sys.exit(run())
