"""
Camada de tokens do Accordion.

Regra unica desta camada: nada aqui inventa valor. Todo token aponta para um
token da Foundation pelo NOME. O portao no fim do arquivo recusa qualquer
coisa que seja um valor solto - hex, px, numero.

Nomenclatura:
  codigo -> accordion-bg-hover      (hifen)
  Figma  -> bg/hover                (collection `18. Accordion`)
Sao camadas diferentes. Nunca colapsar uma na outra.

QUARTO COMPONENTE DO TIER 3 (07/10/2026)

  Component set `Accordion`, node 306:2643, pagina `Tier 3` do Figma. 8
  variantes: `State` (Default / Hover / Pressed / Focus) x `Type` (Closed /
  Opened). Um item so, um tamanho so, sem desabilitado. Fora por escolha:
  componente de grupo (decisao A - como o Radio, quem empilha decide o espaco),
  tamanhos (F) e desabilitado (E - painel que nao abre e conteudo escondido
  sem saida). Marcacao nativa `<details>`/`<summary>`, `name=` para o
  exclusivo (decisao B).

O CABECALHO E O UNICO QUE REAGE

  Hover, pressed e anel ficam no cabecalho - e o `<summary>`, a unica parte
  clicavel. O conteudo fica no fundo de repouso em todos os estados: pintar o
  conteudo sugeriria que ele tambem e clicavel.

HOVER E PRESSED SAO `-raised` - DECISAO G DE GUI

  O item mora em `bg-surface-raised` (como o Card). No escuro, `bg-hover` e o
  mesmo neutral-800 da superficie elevada, e o hover sumia (1,00:1). A
  Foundation ganhou `bg-hover-raised` e `bg-active-raised`, um degrau acima no
  escuro. O portao `estado-distinto` abaixo trava a regressao.

FOCO = REPOUSO + ANEL - DECISAO I DE GUI

  Como no Tab. Quem chega pelo teclado nao ve o fundo de hover sem o mouse.

DIVISORIA DE 1px EM `border-default` - DECISAO H DE GUI

  A mesma linha do Divider. Fica parada em todos os estados: so o fundo do
  cabecalho muda.

SEM TOKEN, DE PROPOSITO

  Cor do chevron e do icone: e a do titulo, entao e `currentColor` (regra do
  Button e do Tag; o Select so tem token de icone porque la a cor difere do
  rotulo). Altura: padding + entrelinha + padding = 76. Largura: do conteiner.
  Espaco entre itens empilhados: do layout (decisao A). Giro do chevron: a
  Foundation nao tem escala de movimento - os 120ms entram como pendencia no
  check.py, como nos outros componentes.

DUAS EXCECOES DECLARADAS DE CONTRASTE

  Ver PENDING.
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
    'bg':        'bg-surface-raised',   # item, cabecalho em repouso e foco, conteudo
    'bg-hover':  'bg-hover-raised',     # cabecalho
    'bg-active': 'bg-active-raised',    # cabecalho

    'title':     'text-primary',        # chevron e icone herdam (currentColor)

    'divider':   'border-default',
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
    'padding':       'space.24',        # cabecalho e conteudo
    'gap':           'space.8',         # icone -> titulo
    'content-gap':   'space.8',         # entre blocos dentro do conteudo
    'radius':        'radius.lg',
    'divider-width': 'border.width.1',
    'icon-size':     'iconSize.24',     # icone a esquerda e chevron
}

TYPE = {
    'title-font': 'type.styles.heading-xs',
}

PENDING = {
    'divisoria-decorativa': (
        'A linha entre cabecalho e conteudo usa `border-default`: entre 1.19:1 e 1.57:1 no '
        'claro e entre 1.00:1 e 1.50:1 no escuro contra o cabecalho. Ela so separa - quem diz '
        'que o item esta aberto e o chevron e o conteudo aparecendo. O 1.00 e o hover escuro '
        '(border-default e bg-hover-raised sao o mesmo neutral-700); ali o limite segue '
        'visivel porque o cabecalho se separa do conteudo pelo fundo (1.46:1). Mesma logica '
        'do Divider. NAO "corrigir" escurecendo.'
    ),
    'item-nao-se-separa-pelo-fundo': (
        'O fundo do item contra a pagina: 1.00:1 sobre a tela e 1.07:1 sobre superficie no '
        'claro; 1.66:1 e 1.36:1 no escuro. Mesmo caso do Card Filled (decisao C de Gui): '
        'quem sustenta a excecao e a regra de uso da etapa 4 - o Accordion vai sobre '
        '`bg-surface`, nunca direto sobre a tela.'
    ),
}

# Fundos onde o item e colocado. Nao sao tokens do Accordion.
PAGES = {
    'canvas':  'bg-canvas',
    'surface': 'bg-surface',
}

# (papel, token do accordion, fundo, piso, chave da excecao em PENDING)
# Titulo e chevron medem contra o cabecalho em cada estado. A divisoria mede
# contra o cabecalho em cada estado. O anel mede contra a pagina: a camada
# interna do anel e da cor da tela, entao ele nunca encosta no item.
COMBOS = [
    ('titulo-repouso',      'title',   'bg',        4.5, None),
    ('titulo-hover',        'title',   'bg-hover',  4.5, None),
    ('titulo-pressed',      'title',   'bg-active', 4.5, None),
    ('chevron-repouso',     'title',   'bg',        3.0, None),
    ('chevron-hover',       'title',   'bg-hover',  3.0, None),
    ('chevron-pressed',     'title',   'bg-active', 3.0, None),
    ('divisoria-repouso',   'divider', 'bg',        3.0, 'divisoria-decorativa'),
    ('divisoria-hover',     'divider', 'bg-hover',  3.0, 'divisoria-decorativa'),
    ('divisoria-pressed',   'divider', 'bg-active', 3.0, 'divisoria-decorativa'),
    ('item-na-tela',        'bg',      'canvas',    3.0, 'item-nao-se-separa-pelo-fundo'),
    ('item-em-superficie',  'bg',      'surface',   3.0, 'item-nao-se-separa-pelo-fundo'),
    ('anel-na-tela',        'ring',    'canvas',    3.0, None),
    ('anel-em-superficie',  'ring',    'surface',   3.0, None),
]

# Nao e piso WCAG: e a trava da decisao G. Hover e pressed precisam se
# distinguir do repouso nos dois temas, senao o cabecalho nao reage.
DISTINCT = [
    ('hover-vs-repouso',   'bg-hover',  'bg'),
    ('pressed-vs-repouso', 'bg-active', 'bg'),
    ('pressed-vs-hover',   'bg-active', 'bg-hover'),
]
DISTINCT_MIN = 1.1


# ---------------------------------------------------------------- portao
def ink(role):
    """O semantico de cor por tras de um papel - seguindo o anel ate a cor."""
    if role in PAGES:
        return PAGES[role]
    if role in RING_INK:
        return RING_INK[role]
    return COLOR[role]


def contrast_rows():
    """Mede cada combinacao renderizada nos dois temas, cada uma contra o piso
    que e dela: texto 4.5:1 do 1.4.3, glifo, linha, anel e fundo 3:1 do 1.4.11."""
    rows = []
    for what, fg_role, bg_role, min_ratio, exc in COMBOS:
        fg_ref, bg_ref = ink(fg_role), ink(bg_role)
        for theme, i in (('light', 0), ('dark', 1)):
            ratio = round(cr(SEM[fg_ref][i], SEM[bg_ref][i]), 2)
            rows.append({
                'theme': theme, 'what': what,
                'fg': fg_ref, 'bg': bg_ref,
                'ratio': ratio, 'min': min_ratio,
                'pass': ratio >= min_ratio,
                'exception': exc,
            })
    return rows


def distinct_rows():
    rows = []
    for what, a, b in DISTINCT:
        for theme, i in (('light', 0), ('dark', 1)):
            ratio = round(cr(SEM[ink(a)][i], SEM[ink(b)][i]), 2)
            rows.append({'theme': theme, 'what': what, 'ratio': ratio,
                         'pass': ratio >= DISTINCT_MIN})
    return rows


def run():
    alias, resolved, problems = {}, {}, []

    for role, ref in COLOR.items():
        name = f'accordion-{role}'
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
        name = f'accordion-{role}'
        alias[name] = ref
        try:
            v = resolve_foundation(ref)
            resolved[name] = {'light': v['light'], 'dark': v['dark']}
        except KeyError:
            problems.append(f'{name}: {ref} nao existe na Foundation')

    for group in (GEOM, TYPE):
        for role, ref in group.items():
            name = f'accordion-{role}'
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
    dist = distinct_rows()
    dist_fails = [r for r in dist if not r['pass']]

    print('=' * 74)
    print('CAMADA DE TOKENS DO ACCORDION')
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
    print(f'estado distinto (piso {DISTINCT_MIN}:1, trava da decisao G): '
          + '  '.join(f'{r["what"]} {r["theme"]} {r["ratio"]}' for r in dist))
    print('-' * 74)

    if fails:
        print(f'{len(fails)} COMBINACAO(OES) REPROVAM O PORTAO DE CONTRASTE:')
        for f in fails:
            print(f'    {f["what"]} ({f["theme"]}): {f["ratio"]}:1 < {f["min"]}')
        return 1
    if dist_fails:
        print(f'{len(dist_fails)} ESTADO(S) NAO SE DISTINGUEM DO VIZINHO:')
        for f in dist_fails:
            print(f'    {f["what"]} ({f["theme"]}): {f["ratio"]}:1 < {DISTINCT_MIN}')
        return 1

    print(f'{len(alias)} tokens, todos alias da Foundation. 0 valores soltos.')

    out = {
        'meta': {
            'component': 'Accordion',
            'version': '0.1.0',
            'foundation': FOUND['meta']['version'],
            'figmaNode': '306:2643',
            'figmaCollection': '18. Accordion',
            'variants': ['closed', 'opened'],
            'sizes': ['default'],
            'states': ['default', 'hover', 'pressed', 'focus'],
            'nota': (
                'Item de conteudo expansivel, nativo (<details>/<summary>). Um tamanho, sem '
                'desabilitado, sem componente de grupo. Fundo bg-surface-raised; so o cabecalho '
                'reage, com hover e pressed -raised (decisao G). Foco = repouso + anel. '
                'Divisoria 1px border-default. Duas excecoes de contraste declaradas em pending.'
            ),
        },
        'alias': alias,
        'resolved': resolved,
        'contrast': rows,
        'distinct': dist,
        'pending': PENDING,
    }
    json.dump(out, open(comp_out('accordion', 'tokens.json'), 'w'), indent=2, ensure_ascii=False)
    print('\nbuild/components/accordion/tokens.json escrito')
    write_css(alias)
    return 0


# ---------------------------------------------------------------- css
def write_css(alias):
    L = []
    w = L.append
    w('/* AL Design System - tokens do Accordion')
    w(' * GERADO por src/components/accordion/tokens.py. Nao editar a mao.')
    w(' *')
    w(' * Nao ha bloco de tema aqui: cada token aponta para um semantico, e o tema')
    w(' * troca no :root - o mesmo elemento onde estes alias sao declarados.')
    w(' */')
    w('')
    w(':root {')

    w('')
    w('  /* fundo - so o cabecalho reage; o conteudo fica no repouso */')
    for role in ('bg', 'bg-hover', 'bg-active'):
        w(f'  --al-accordion-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* titulo - chevron e icone herdam por currentColor */')
    w(f'  --al-accordion-title: {css_ref(COLOR["title"])};')

    w('')
    w('  /* divisoria entre cabecalho e conteudo - parada em todos os estados */')
    w(f'  --al-accordion-divider: {css_ref(COLOR["divider"])};')

    w('')
    w('  /* anel de foco - aponta para a sombra composta, nao para a cor crua */')
    for role, ref in RING.items():
        w(f'  --al-accordion-{role}: {css_ref(ref)};')

    w('')
    w('  /* geometria */')
    for role, ref in GEOM.items():
        w(f'  --al-accordion-{role}: {css_ref(ref)};')

    w('')
    w('  /* tipografia - um estilo vira quatro vars */')
    for role, ref in TYPE.items():
        style = resolve_foundation(ref)
        key = size_key(style[1])
        prefix = f'--al-accordion-{role}'.replace('-font', '')
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

    save_css('accordion', texto)


if __name__ == '__main__':
    sys.exit(run())
