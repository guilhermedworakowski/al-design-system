"""
Camada de tokens do Alert.

Regra desta camada: nada aqui inventa valor. Todo token aponta para um token da
Foundation pelo NOME. Nao ha excecao de valor declarado: o Alert ocupa a
largura do conteudo e nao tem tempo na tela.

Nomenclatura:
  codigo -> alert-danger-border   (hifen)
  Figma  -> danger/border         (collection `25. Alert`)
Sao camadas diferentes. Nunca colapsar uma na outra.

TERCEIRO COMPONENTE DO TIER 5 E ULTIMO DA V1 (09/10/2026)

  Component set `alert`, node 373:5186. 4 variantes `Status` (Success /
  Warning / Danger / Info) e os booleanos `actions` e `close`. Icone 24 no
  topo + titulo 16/24 bold + descricao Body/md (sempre presente) + X (Icon
  Button Ghost sm). Linha de acoes a direita: Button Ghost md + Primary md.
  Fundo bg-surface-raised (o mesmo do Card), borda 1px na cor do status, raio
  xl, padding 16, sem sombra: o Alert mora no fluxo da pagina, no topo,
  abaixo do header.

  Decisoes da etapa 1: Danger NAO e Error - e cuidado, nao falha (2); a
  descricao e sempre visivel (3); titulo em 16 bold (A); acoes Ghost +
  Primary md, alinhadas a direita (B, C); X opcional, Warning e Danger sem X
  enquanto a situacao existir (D).

O STATUS "danger" USA O SEMANTICO "danger"

  Diferente do Toast, onde o status se chama "error". No Alert o nome e o da
  Foundation porque o sentido e outro (decisao 2 de Gui).

O TITULO NAO E UM ESTILO DA FOUNDATION

  16/24 bold nao existe em type.styles (Label/lg e medium). O titulo e montado
  com tres tokens soltos da escala - tamanho md, entrelinha md, peso bold -
  em vez de um estilo novo na Foundation (decisao F: so o Alert usaria).

MOVIMENTO

  Decisao E: entra e sai com a transicao rapida dos controles (duration-
  feedback, 120ms), so opacidade. Entrar usa easing-enter, sair easing-exit.

SEM TOKEN, DE PROPOSITO

  Altura: sai do conteudo. Largura: a do conteudo da pagina. Icone:
  `icon-size-24` direto da Foundation (regra do Tag e do Tooltip). Sombra:
  nenhuma. Botoes e X: os componentes Button e Icon Button; sobre
  bg-surface-raised o Ghost e o X usam `bg-hover-raised` / `bg-active-raised`
  (licao do Modal 0.18.1), sem token novo. O rotulo branco do Primary em
  repouso (3.34:1) e a excecao de marca do Button, herdada, nao nova.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'tools'))
from paths import FOUNDATION_SRC, TOKENS_JSON, comp_out  # noqa: E402
sys.path.insert(0, FOUNDATION_SRC)

from palette import SEM                     # noqa: E402
from tokenlib import resolve_foundation, css_ref, save_css  # noqa: E402
from color import cr                      # noqa: E402

FOUND = json.load(open(TOKENS_JSON))   # noqa: E402

# --------------------------------------------------------------- cor
COLOR = {
    'bg':          'bg-surface-raised',
    'title':       'text-primary',
    'description': 'text-secondary',
}

# O icone e a borda carregam o status; o icone e a pista que nao depende de
# cor (Spectrum), a borda passa no 3:1 contra o fundo e contra a pagina.
STATUS = ('success', 'warning', 'danger', 'info')
for status in STATUS:
    COLOR[f'{status}-icon'] = f'text-{status}'
    COLOR[f'{status}-border'] = f'border-{status}'

# ------------------------------------------------------------ geometria
GEOM = {
    'padding':      'space.16',
    'gap':          'space.16',             # icone -> texto -> X
    'text-gap':     'space.4',              # titulo -> descricao
    'section-gap':  'space.24',             # texto -> linha de acoes
    'actions-gap':  'space.16',             # botao -> botao
    'radius':       'radius.xl',
    'border-width': 'border.width.1',
}

# Titulo montado da escala (decisao F); descricao e um estilo inteiro.
TITLE = {
    'title-font-size':   'type.size.md',
    'title-line-height': 'type.leading.md',
    'title-font-weight': 'type.weight.bold',
}
TYPE = {
    'description-font': 'type.styles.body-md',
}

# Decisao E: a transicao rapida dos controles.
MOTION = {
    'duration':     'motion.duration.feedback',
    'easing-enter': 'motion.easing.enter',
    'easing-exit':  'motion.easing.exit',
}

PENDING = {}

# Telas sobre as quais o alert aparece. Nao sao tokens do Alert.
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
        name = f'alert-{role}'
        alias[name] = ref
        if ref.startswith('#'):
            problems.append(f'{name}: hex solto ({ref})')
        elif ref not in SEM:
            problems.append(f'{name}: aponta para {ref}, que nao existe na camada semantica')
        else:
            resolved[name] = {'light': SEM[ref][0], 'dark': SEM[ref][1]}

    for group in (GEOM, TITLE, TYPE, MOTION):
        for role, ref in group.items():
            name = f'alert-{role}'
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
    print('CAMADA DE TOKENS DO ALERT')
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
    print(f'{len(alias)} tokens, todos alias da Foundation.')

    out = {
        'meta': {
            'component': 'Alert',
            'version': '0.1.0',
            'foundation': FOUND['meta']['version'],
            'figmaNode': '373:5186',
            'figmaCollection': '25. Alert',
            'nota': (
                'Fundo bg-surface-raised, borda 1px e icone 24 na cor do status, titulo '
                '16/24 bold montado da escala, descricao Body/md sempre visivel, padding 16, '
                'gap 16, 24 ate a linha de acoes, raio xl, sem sombra. No topo da pagina, '
                'abaixo do header, na largura do conteudo. Entra e sai com opacidade em '
                'duration-feedback. Sem excecao de contraste.'
            ),
        },
        'alias': alias,
        'resolved': resolved,
        'contrast': rows,
        'pending': PENDING,
    }
    json.dump(out, open(comp_out('alert', 'tokens.json'), 'w'), indent=2, ensure_ascii=False)
    print('\nbuild/components/alert/tokens.json escrito')
    write_css(alias)
    return 0


# ---------------------------------------------------------------- css
def _scale_key(scale, v, what):
    for key, val in FOUND['type'][scale].items():
        if val == v:
            return key
    raise KeyError(f'type.{scale} com valor {v} nao existe na Foundation ({what})')


def write_css(alias):
    L = []
    w = L.append
    w('/* AL Design System - tokens do Alert')
    w(' * GERADO por src/components/alert/tokens.py. Nao editar a mao.')
    w(' */')
    w('')
    w(':root {')
    w('')
    w('  /* cor - caixa e texto */')
    for role in ('bg', 'title', 'description'):
        w(f'  --al-alert-{role}: {css_ref(COLOR[role])};')
    w('')
    w('  /* cor - status: icone e borda */')
    for status in STATUS:
        for part in ('icon', 'border'):
            role = f'{status}-{part}'
            w(f'  --al-alert-{role}: {css_ref(COLOR[role])};')
    w('')
    w('  /* geometria */')
    for role, ref in GEOM.items():
        w(f'  --al-alert-{role}: {css_ref(ref)};')
    w('')
    w('  /* movimento - a transicao rapida dos controles (decisao E) */')
    for role, ref in MOTION.items():
        w(f'  --al-alert-{role}: {css_ref(ref)};')
    w('')
    w('  /* tipografia - titulo montado da escala (decisao F), descricao = Body/md */')
    for role, ref in TITLE.items():
        w(f'  --al-alert-{role}: {css_ref(ref)};')
    w('  --al-alert-title-tracking: 0em;')
    for role, ref in TYPE.items():
        style = resolve_foundation(ref)
        prefix = f'--al-alert-{role}'.replace('-font', '')
        w(f'  {prefix}-font-size: var(--al-font-size-{_scale_key("size", style[1], role)});')
        w(f'  {prefix}-line-height: var(--al-line-height-{_scale_key("leading", style[2], role)});')
        w(f'  {prefix}-font-weight: var(--al-font-weight-{_weight_key(style[3])});')
        w(f'  {prefix}-tracking: {style[4]};')
    w('}')
    w('')
    texto = '\n'.join(L)
    faltando = [n for n in alias if not n.endswith('-font') and f'--al-{n}:' not in texto]
    if faltando:
        raise AssertionError(f'tokens fora do CSS: {faltando}')
    save_css('alert', texto)


def _weight_key(v):
    for key, val in FOUND['type']['weight'].items():
        if val == v:
            return key
    raise KeyError(f'type.weight com valor {v} nao existe na Foundation')


if __name__ == '__main__':
    sys.exit(run())
