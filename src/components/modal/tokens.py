"""
Camada de tokens do Modal.

Regra desta camada: nada aqui inventa valor. Todo token aponta para um token da
Foundation pelo NOME. A UNICA excecao sao as tres larguras (WIDTH, abaixo), e
ela e declarada, nomeada e travada pelo portao.

Nomenclatura:
  codigo -> modal-bg                (hifen)
  Figma  -> bg                      (collection `19. Modal`)
Sao camadas diferentes. Nunca colapsar uma na outra.

QUINTO COMPONENTE DO TIER 3 (07/10/2026)

  Frame `modal`, node 305:1703, pagina `Tier 3` do Figma. 3 variantes, eixo
  `Size` (sm 320 / md 480 / lg 640). Props: `Title`, `actions` (bool) e o slot
  `content`. Marcacao nativa `<dialog>` com `showModal()` (decisao A). Fora por
  escolha: botao de fechar (B - o AL exige ao menos um botao no rodape, e o
  secundario ja fecha), divisoria entre miolo e titulo/rodape (E).

SCRIM

  `bg-scrim` nasceu na Foundation para este componente (decisao D) e serve ao
  Drawer. E o unico semantico com transparencia (#RRGGBBAA). Por isso nao entra
  em PAIRS da Foundation: o contraste dele so existe COMPOSTO sobre a pagina, e
  quem mede e este arquivo.

SEM TOKEN, DE PROPOSITO

  Entrada e saida: o card sobe ao abrir e desce ao fechar (Gui, 07/10/2026),
  `modal-offset` = space.96. A Foundation nao tem escala de deslocamento de
  movimento; o espacamento serve de alias.

  Altura: hug com maximo (decisao E: so o miolo rola). Largura no celular:
  100vw - 2 x modal-margin (decisao F/H). Botoes do rodape: tokens do Button.
  Alinhamento das acoes: layout. Easing: easing-enter na abertura, easing-exit
  no fechamento, direto da Foundation.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'tools'))
from paths import FOUNDATION_SRC, TOKENS_JSON, comp_out  # noqa: E402
sys.path.insert(0, FOUNDATION_SRC)

from palette import SEM                     # noqa: E402
from color import cr                      # noqa: E402
from contrast import composite            # noqa: E402

FOUND = json.load(open(TOKENS_JSON))   # noqa: E402

# --------------------------------------------------------------- cor
COLOR = {
    'bg':     'bg-surface-raised',
    'title':  'text-primary',
    'scrim':  'bg-scrim',               # com transparencia - ver nota SCRIM
}

# Elevacao e altura, nao estado: fica fora da camada de cor.
SHADOW = {
    'shadow': 'elevation.5',
}

# ------------------------------------------------------------ geometria
GEOM = {
    'padding': 'space.24',
    'gap':     'space.24',              # titulo / miolo / acoes
    'margin':  'space.16',              # contra a borda da tela (decisao H)
    'offset':  'space.96',              # quanto o card sobe ao abrir e desce ao fechar
    'radius':  'radius.2xl',
}

# Movimento: o token aponta para a duracao da Foundation (panel = o que cobre
# a tela). O easing nao vira token do componente.
MOTION = {
    'duration': 'motion.duration.panel',
}

TYPE = {
    'title-font': 'type.styles.heading-sm',
}

# UNICA excecao a "todo token e alias" (decisao G de Gui, 07/10/2026): a
# Foundation nao tem escala de largura de container (o espaco acaba em 96).
# Os valores vem do Figma. Quando a escala existir, estes tres viram alias.
WIDTH = {
    'width-sm': 320,
    'width-md': 480,
    'width-lg': 640,
}

PENDING = {
    'card-nao-se-separa-do-scrim-no-escuro': (
        'No escuro o card (bg-surface-raised, neutral-800) contra a pagina escurecida pelo '
        'scrim fica em ~1.8:1, abaixo dos 3:1 do 1.4.11. Quem sustenta a separacao e o card '
        'CLAREAR (cue primario da Foundation no escuro) mais a sombra. Subir a opacidade nao '
        'resolve: a 72% o par vai a 1.88:1, porque o fundo ja e quase preto. Decisao G de Gui '
        '(sem contorno no escuro) e excecao aprovada em 07/10/2026. NAO "corrigir" escurecendo.'
    ),
}

# Fundos sobre os quais o Modal abre. Nao sao tokens do Modal.
PAGES = {
    'canvas':  'bg-canvas',
    'surface': 'bg-surface',
}

# (papel, fg, bg, piso, excecao). `scrim:<pagina>` = pagina com o scrim composto.
COMBOS = [
    ('titulo',                   'title', 'bg',             4.5, None),
    ('card-na-tela-escurecida',  'bg',    'scrim:canvas',   3.0, 'card-nao-se-separa-do-scrim-no-escuro'),
    ('card-em-superficie-escurecida', 'bg', 'scrim:surface', 3.0, 'card-nao-se-separa-do-scrim-no-escuro'),
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


def color_of(role, i):
    """Cor renderizada de um papel no tema i (0 claro, 1 escuro)."""
    if role.startswith('scrim:'):
        page = PAGES[role.split(':')[1]]
        return composite(SEM[COLOR['scrim']][i], SEM[page][i])
    return SEM[COLOR[role]][i]


def contrast_rows():
    rows = []
    for what, fg, bg, min_ratio, exc in COMBOS:
        for theme, i in (('light', 0), ('dark', 1)):
            a, b = color_of(fg, i), color_of(bg, i)
            ratio = round(cr(a, b), 2)
            rows.append({'theme': theme, 'what': what, 'fg': a, 'bg': b,
                         'ratio': ratio, 'min': min_ratio,
                         'pass': ratio >= min_ratio, 'exception': exc})
    return rows


def run():
    alias, resolved, problems = {}, {}, []

    for role, ref in COLOR.items():
        name = f'modal-{role}'
        alias[name] = ref
        if ref.startswith('#'):
            problems.append(f'{name}: hex solto ({ref})')
        elif ref not in SEM:
            problems.append(f'{name}: aponta para {ref}, que nao existe na camada semantica')
        else:
            resolved[name] = {'light': SEM[ref][0], 'dark': SEM[ref][1]}

    for group in (SHADOW, GEOM, MOTION, TYPE):
        for role, ref in group.items():
            name = f'modal-{role}'
            alias[name] = ref
            try:
                resolved[name] = resolve_foundation(ref)
            except KeyError:
                problems.append(f'{name}: {ref} nao existe na Foundation')

    # Excecao nomeada: valor solto so e aceito para estes tres nomes.
    for role, px in WIDTH.items():
        name = f'modal-{role}'
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
    print('CAMADA DE TOKENS DO MODAL')
    print('=' * 74)
    for name in sorted(alias):
        print(f'  {name:<22} -> {alias[name]}')
    print('-' * 74)
    for r in rows:
        tag = 'OK  ' if r['pass'] else ('EXCE' if r['exception'] else 'FALHA')
        print(f'  {tag} {r["what"]:<32} {r["theme"]:<5} {r["fg"]} / {r["bg"]}  {r["ratio"]}:1 (piso {r["min"]})')
    print(f'contraste: {len(rows)} medicoes  |  passam: {len(rows) - len(fails) - len(excs)}  |  '
          f'excecoes declaradas: {len(excs)}  |  reprovas: {len(fails)}')
    if fails:
        print(f'{len(fails)} COMBINACAO(OES) REPROVAM O PORTAO DE CONTRASTE')
        return 1
    n_lit = len(WIDTH)
    print(f'{len(alias)} tokens: {len(alias) - n_lit} alias da Foundation, {n_lit} larguras com valor '
          f'declarado (decisao G).')

    out = {
        'meta': {
            'component': 'Modal',
            'version': '0.1.0',
            'foundation': FOUND['meta']['version'],
            'figmaNode': '305:1703',
            'figmaCollection': '19. Modal',
            'sizes': ['sm', 'md', 'lg'],
            'nota': (
                '<dialog> nativo com showModal(). Fundo bg-surface-raised, sombra elevation.5, '
                'scrim bg-scrim (novo, com transparencia). Sem botao de fechar, sem divisorias; so '
                'o miolo rola. Tres larguras com valor declarado. Uma excecao de contraste em pending.'
            ),
        },
        'alias': alias,
        'resolved': resolved,
        'contrast': rows,
        'pending': PENDING,
    }
    json.dump(out, open(comp_out('modal', 'tokens.json'), 'w'), indent=2, ensure_ascii=False)
    print('\nbuild/components/modal/tokens.json escrito')
    write_css(alias)
    return 0


# ---------------------------------------------------------------- css
def css_ref(ref):
    if ref.startswith('space.'):
        return f'var(--al-space-{ref.split(".")[1]})'
    if ref.startswith('radius.'):
        return f'var(--al-radius-{ref.split(".")[1]})'
    if ref.startswith('elevation.'):
        return f'var(--al-elevation-{ref.split(".")[1]})'
    if ref.startswith('motion.duration.'):
        return f'var(--al-motion-duration-{ref.split(".")[2]})'
    return f'var(--al-{ref})'


def _size_key(font_size):
    for key, v in FOUND['type']['size'].items():
        if v == font_size:
            return key
    raise KeyError(f'type.size com valor {font_size} nao existe na Foundation')


def write_css(alias):
    L = []
    w = L.append
    w('/* AL Design System - tokens do Modal')
    w(' * GERADO por components/modal/tokens.py. Nao editar a mao.')
    w(' */')
    w('')
    w(':root {')
    w('')
    w('  /* cor - o scrim tem transparencia; o tema troca no :root */')
    for role in COLOR:
        w(f'  --al-modal-{role}: {css_ref(COLOR[role])};')
    w('')
    w('  /* elevacao */')
    for role, ref in SHADOW.items():
        w(f'  --al-modal-{role}: {css_ref(ref)};')
    w('')
    w('  /* geometria */')
    for role, ref in GEOM.items():
        w(f'  --al-modal-{role}: {css_ref(ref)};')
    w('')
    w('  /* largura - valor declarado, sem escala na Foundation (decisao G) */')
    for role, px in WIDTH.items():
        w(f'  --al-modal-{role}: {px}px;')
    w('')
    w('  /* movimento - easing vem direto da Foundation */')
    for role, ref in MOTION.items():
        w(f'  --al-modal-{role}: {css_ref(ref)};')
    w('')
    w('  /* tipografia - um estilo vira quatro vars */')
    for role, ref in TYPE.items():
        style = resolve_foundation(ref)
        key = _size_key(style[1])
        prefix = f'--al-modal-{role}'.replace('-font', '')
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
    path = comp_out('modal', 'al-modal-tokens.css')
    open(path, 'w').write(texto)
    print(f'build/components/modal/al-modal-tokens.css escrito ({os.path.getsize(path)} bytes)')


if __name__ == '__main__':
    sys.exit(run())
