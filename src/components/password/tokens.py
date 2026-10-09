"""
Camada de tokens do Password.

Regra unica desta camada: nada aqui inventa valor. Todo token aponta para um
token da Foundation pelo NOME. O portao no fim do arquivo recusa qualquer
coisa que seja um valor solto - hex, px, numero.

Nomenclatura:
  codigo -> password-toggle-ring       (hifen)
  Figma  -> password/toggle/ring       (pasta)
Sao camadas diferentes. Nunca colapsar uma na outra.

CAMPO DE SENHA, NO LUGAR DO DATE PICKER

  E o Input sem o que o Figma do Password nao desenha, mais o botao do olho.
  Seis estados (Default, Hover, Error, focusError, Disabled, focusDefault),
  mesmas cores, mesmas duas excecoes de contraste. Sem Active e sem Typed pelo
  mesmo motivo do Input - ver o cabecalho de components/input/tokens.py.

  Fora, por decisao de Gui na etapa 1 (06/10/2026): read-only (senha "so para
  ler" expoe o dado), contador, prefixo e sufixo, a marca "(Opcional)" e o
  texto de apoio fora do erro. Por isso nao existem `bg-readonly`,
  `border-readonly`, `optional`, `counter*`, `affix` nem `help` - so
  `help-error`.

  O eixo `Type` do Figma (No / Visible / Hidden) NAO vira token: e o atributo
  `type` do <input> (password x text) e o icone que o botao mostra. A cor do
  valor e a mesma nos tres, inclusive no erro (`text-primary`, nunca vermelho).

O BOTAO DO OLHO

  E um <button> de verdade, focavel, depois do campo na ordem do Tab. O icone
  mostra a ACAO (eye = mostrar, eye-off = esconder), como Material e Carbon.

  - Anel so em volta do olho (opcao A da etapa 1, precedente Carbon), nunca no
    campo inteiro. Sempre o anel PADRAO, mesmo com o campo em erro: o anel diz
    onde esta o foco, e o erro e do campo, nao do botao. Mesma solucao do X do
    Tag (`tag-dismiss-ring`).
  - Formato do anel: `radius.full`, um circulo, como o X do Tag (Gui, etapa 3).
  - Sem hover: o Figma nao desenha, so o cursor muda.
  - A area clicavel E o icon-size: 24x24, o minimo EXATO do WCAG 2.5.8. Sem
    folga - se o icone encolher, o alvo reprova.
  - O respiro de 2px do anel e `bg-canvas`, nao o fundo do campo. No escuro
    isso desenha um contorno fino #181818 dentro do campo #3E3E3E. Aceito
    por Gui na etapa 3: o anel continua passando contra o fundo do campo e nao
    vale um anel novo na Foundation so para isso.

ALTURA NAO E TOKEN

  48 = padding-y x2 + entrelinha (12 + 24 + 12), borda de 1px sobreposta ao
  padding. Igual ao Input.

O GAP E UM SO EM DOIS LUGARES

  `password-gap` vale para a pilha vertical (rotulo -> campo -> erro) e para o
  espaco entre o texto e o olho. Os dois sao 8.

LARGURA NAO E TOKEN

  O campo ocupa 100% do conteiner. Formulario decide largura; componente nao.
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
    'bg':               'bg-surface-raised',
    'bg-disabled':      'bg-disabled',

    'border':           'border-default',
    'border-hover':     'border-strong',
    'border-focus':     'border-brand',
    'border-error':     'border-danger',
    'border-disabled':  'border-default',

    'text-placeholder': 'text-placeholder',
    'text-value':       'text-primary',     # pontos ou texto, inclusive no erro
    'text-disabled':    'text-disabled',

    'label':            'text-primary',
    'label-error':      'text-danger',
    'label-disabled':   'text-disabled',

    'help-error':       'text-danger',

    'toggle-icon':          'text-primary',   # glifo vetorial - piso 3:1
    'toggle-icon-disabled': 'text-disabled',
}

# O token aponta para a SOMBRA COMPOSTA, nao para a cor crua - mesma regra do
# `button-*-ring`. A cor so e extraida para medicao, no RING_INK abaixo.
RING = {
    'ring':        'focusRing.default',
    'ring-error':  'focusRing.error',
    'toggle-ring': 'focusRing.default',   # sempre o padrao, ver cabecalho
}

RING_INK = {
    'ring':        'shadow-focus-default',
    'ring-error':  'shadow-focus-error',
    'toggle-ring': 'shadow-focus-default',
}

# ------------------------------------------------------------ geometria
GEOM = {
    'padding-x':     'space.12',
    'padding-y':     'space.12',
    'gap':           'space.8',       # pilha, texto -> olho
    'radius':        'radius.lg',
    'border-width':  'border.width.1',
    'icon-size':     'iconSize.24',   # e tambem a area clicavel do olho
    'toggle-radius': 'radius.full',   # formato do anel do olho
}

TYPE = {
    'font':       'type.styles.body-md',
    'label-font': 'type.styles.body-md',
    'help-font':  'type.styles.caption',
}

PENDING = {
    'borda-abaixo-de-3-1': (
        'A borda em repouso usa `border-default` (1.57:1 no claro, 1.46:1 no escuro '
        'contra o fundo do campo). Abaixo dos 3:1 do WCAG 1.4.11. Mesma decisao '
        'consciente do Select, do Input e do Textarea. O criterio nao falha quando a '
        'borda nao e o unico meio de perceber o componente, e aqui nao e: o campo tem '
        'rotulo visivel acima e o olho dentro. NAO "corrigir" sem falar com ele.'
    ),
    'disabled-abaixo-de-aa': (
        'Rotulo, texto, borda e olho no disabled ficam abaixo do minimo. Isencao do '
        'WCAG 1.4.3 para componente inativo - mesma excecao permanente do Button, do '
        'Tag, do Select e do Input. Subir esse contraste faz o desabilitado parecer '
        'editavel.'
    ),
}

CANVAS = 'bg-canvas'   # nao e token do Password: e a tela onde ele e colocado

# (papel, token do password, fundo(s), piso, chave da excecao em PENDING)
# Rotulo, erro e anel do campo vivem FORA do campo e medem contra a tela; o que
# esta dentro (valor, olho, anel do olho) mede contra o fundo do campo daquele
# estado. A borda mede contra as DUAS superficies vizinhas e guarda a pior.
#
# Nao ha anel do olho no disabled: botao desabilitado nao recebe foco.
COMBOS = [
    ('rotulo',            'label',                'canvas',                   4.5, None),
    ('rotulo-erro',       'label-error',          'canvas',                   4.5, None),
    ('rotulo-disabled',   'label-disabled',       'canvas',                   4.5, 'disabled-abaixo-de-aa'),
    ('apoio-erro',        'help-error',           'canvas',                   4.5, None),
    ('placeholder',       'text-placeholder',     'bg',                       4.5, None),
    ('valor',             'text-value',           'bg',                       4.5, None),
    ('texto-disabled',    'text-disabled',        'bg-disabled',              4.5, 'disabled-abaixo-de-aa'),
    ('olho',              'toggle-icon',          'bg',                       3.0, None),
    ('olho-disabled',     'toggle-icon-disabled', 'bg-disabled',              3.0, 'disabled-abaixo-de-aa'),
    ('borda-repouso',     'border',               ('canvas', 'bg'),           3.0, 'borda-abaixo-de-3-1'),
    ('borda-hover',       'border-hover',         ('canvas', 'bg'),           3.0, None),
    ('borda-focus',       'border-focus',         ('canvas', 'bg'),           3.0, None),
    ('borda-erro',        'border-error',         ('canvas', 'bg'),           3.0, None),
    ('borda-disabled',    'border-disabled',      ('canvas', 'bg-disabled'),  3.0, 'disabled-abaixo-de-aa'),
    ('anel-foco',         'ring',                 'canvas',                   3.0, None),
    ('anel-foco-erro',    'ring-error',           'canvas',                   3.0, None),
    ('anel-olho',         'toggle-ring',          'bg',                       3.0, None),
]


# ---------------------------------------------------------------- portao
def ink(role):
    """O semantico de cor por tras de um papel - seguindo o anel ate a cor."""
    if role == 'canvas':
        return CANVAS
    if role in RING_INK:
        return RING_INK[role]
    return COLOR[role]


def contrast_rows():
    """Mede cada combinacao renderizada nos dois temas, cada uma contra o piso
    que e dela: texto 4.5:1 do 1.4.3, borda, icone e anel 3:1 do 1.4.11."""
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
        name = f'password-{role}'
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
        name = f'password-{role}'
        alias[name] = ref
        try:
            v = resolve_foundation(ref)
            resolved[name] = {'light': v['light'], 'dark': v['dark']}
        except KeyError:
            problems.append(f'{name}: {ref} nao existe na Foundation')

    for group in (GEOM, TYPE):
        for role, ref in group.items():
            name = f'password-{role}'
            alias[name] = ref
            try:
                resolved[name] = resolve_foundation(ref)
            except KeyError:
                problems.append(f'{name}: {ref} nao existe na Foundation')

    # derivadas - conferencia, nao token. Ver nota no cabecalho.
    pad_y = resolve_foundation(GEOM['padding-y'])
    gap = resolve_foundation(GEOM['gap'])
    field_line = resolve_foundation(TYPE['font'])[2]
    label_line = resolve_foundation(TYPE['label-font'])[2]
    help_line = resolve_foundation(TYPE['help-font'])[2]
    icon = resolve_foundation(GEOM['icon-size'])
    field_h = pad_y * 2 + field_line
    derived = {
        'field-height': field_h,
        'toggle-target': icon,
        'total-height': label_line + gap + field_h,
        'total-height-with-error': label_line + gap + field_h + gap + help_line,
    }
    if icon > field_line:
        problems.append(f'icon-size {icon} > entrelinha {field_line} - o olho mexe na altura do campo')
    if icon < 24:
        problems.append(f'alvo do olho {icon}px < 24px do WCAG 2.5.8')

    rows = contrast_rows()
    fails = [r for r in rows if not r['pass'] and not r['exception']]
    excs = [r for r in rows if not r['pass'] and r['exception']]

    print('=' * 74)
    print('CAMADA DE TOKENS DO PASSWORD')
    print('=' * 74)
    for name in sorted(alias):
        print(f'  {name:<28} -> {alias[name]}')
    print('-' * 74)
    print(f'altura do campo derivada: {derived["field-height"]}px  '
          f'(padding-y x2 + entrelinha; borda sobreposta ao padding)')
    print(f'altura total: {derived["total-height"]}px  '
          f'| com mensagem de erro: {derived["total-height-with-error"]}px')
    print(f'alvo do olho: {icon}x{icon}px (minimo do WCAG 2.5.8: 24)')
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

    if problems:
        print(f'{len(problems)} TOKEN(S) REPROVAM O PORTAO DE ALIAS:')
        for p in problems:
            print('   ', p)
        return 1
    if fails:
        print(f'{len(fails)} COMBINACAO(OES) REPROVAM O PORTAO DE CONTRASTE:')
        for f in fails:
            print(f'    {f["what"]} ({f["theme"]}): {f["ratio"]}:1 < {f["min"]}')
        return 1

    print(f'{len(alias)} tokens, todos alias da Foundation. 0 valores soltos.')

    out = {
        'meta': {
            'component': 'Password',
            'version': '0.1.0',
            'foundation': FOUND['meta']['version'],
            'figmaNode': '299:536',
            'variants': [],
            'sizes': ['md'],
            'states': ['default', 'hover', 'error', 'focus-error',
                       'disabled', 'focus'],
            'nota': (
                'Campo de senha com botao de mostrar/ocultar. E o Input sem read-only, '
                'contador, afixos, marca de opcional e apoio fora do erro, mais o olho. '
                'O eixo Type do Figma (No/Visible/Hidden) e o atributo type do input, '
                'nao token. O olho e um botao focavel com anel proprio, circular e '
                'sempre padrao; alvo de 24px. Duas excecoes de contraste declaradas '
                'em pending.'
            ),
        },
        'alias': alias,
        'resolved': resolved,
        'derived': derived,
        'contrast': rows,
        'pending': PENDING,
    }
    json.dump(out, open(comp_out('password', 'tokens.json'), 'w'), indent=2, ensure_ascii=False)
    print('\nbuild/components/password/tokens.json escrito')
    write_css(alias, derived)
    return 0


# ---------------------------------------------------------------- css
def write_css(alias, derived):
    L = []
    w = L.append
    w('/* AL Design System - tokens do Password')
    w(' * GERADO por src/components/password/tokens.py. Nao editar a mao.')
    w(' *')
    w(' * Nao ha bloco de tema aqui: cada token aponta para um semantico, e o tema')
    w(' * troca no :root - o mesmo elemento onde estes alias sao declarados.')
    w(' *')
    w(f' * Altura do campo: {derived["field-height"]}px derivados, sem token.')
    w(f' * Alvo do olho: {derived["toggle-target"]}px = icon-size, sem token proprio.')
    w(' */')
    w('')
    w(':root {')

    w('')
    w('  /* fundo - so o disabled muda */')
    for role in ('bg', 'bg-disabled'):
        w(f'  --al-password-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* borda - o eixo que carrega o estado */')
    for role in ('border', 'border-hover', 'border-focus', 'border-error',
                 'border-disabled'):
        w(f'  --al-password-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* texto dentro do campo - pontos e texto aberto usam a mesma cor */')
    for role in ('text-placeholder', 'text-value', 'text-disabled'):
        w(f'  --al-password-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* rotulo e erro - vivem fora do campo, sobre a tela */')
    for role in ('label', 'label-error', 'label-disabled', 'help-error'):
        w(f'  --al-password-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* botao do olho */')
    for role in ('toggle-icon', 'toggle-icon-disabled'):
        w(f'  --al-password-{role}: {css_ref(COLOR[role])};')

    w('')
    w('  /* aneis de foco - apontam para a sombra composta, nao para a cor crua */')
    for role, ref in RING.items():
        w(f'  --al-password-{role}: {css_ref(ref)};')

    w('')
    w('  /* geometria */')
    for role, ref in GEOM.items():
        w(f'  --al-password-{role}: {css_ref(ref)};')

    w('')
    w('  /* tipografia - um estilo vira quatro vars */')
    for role, ref in TYPE.items():
        style = resolve_foundation(ref)
        key = size_key(style[1])
        prefix = f'--al-password-{role}'.replace('-font', '')
        if role == 'font':
            prefix = '--al-password'
        w(f'  {prefix}-font-size: var(--al-font-size-{key});')
        w(f'  {prefix}-line-height: var(--al-line-height-{key});')
        w(f'  {prefix}-font-weight: {style[3]};')
        w(f'  {prefix}-tracking: {style[4]};')

    w('}')
    w('')

    # Trava herdada do Select: lista de grupo esquecida vira build quebrado,
    # nao variavel faltando em silencio.
    texto = '\n'.join(L)
    faltando = [r for r in COLOR if f'--al-password-{r}:' not in texto]
    if faltando:
        raise AssertionError(
            'papeis de cor fora do CSS (alguma lista de grupo em write_css nao '
            f'foi atualizada): {faltando}')

    save_css('password', texto)


if __name__ == '__main__':
    sys.exit(run())
