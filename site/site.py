"""
Monta o site do AL Design System: Foundation e componentes numa pagina so.

Substitui os dois HTML separados que existiam antes (foundation/page.py e
site/build.py, removidos - o git guarda os dois na tag v0.2.0). A diferenca de
fundo nao era visual:

  - o conteudo da Foundation era prosa com numeros escritos a mao, e eles
    envelheceram (a pagina antiga anunciava 72 pares e 46 semanticos quando o
    tokens.json ja estava em 80 e 49). Aqui TODA contagem sai do tokens.json,
    e ha uma trava que aborta se um semantico novo nao couber em nenhum grupo.
  - o CSS entra inline e real: foundation/al-foundation.css, os tokens do
    Button e o proprio button.css. A pagina nao reimplementa nada. Se um
    componente quebrar, a pagina quebra junto - que e o que se quer.

Navegacao em duas camadas, como Carbon e Material fazem:
  trilho a esquerda = assunto, em dois grupos que abrem um de cada vez
  abas no topo      = recorte do assunto
  paginas-indice    = um card por assunto interno, com a miniatura montada
                      com os proprios tokens que ela documenta

Interatividade so onde ela prova alguma coisa: o playground do Button, o
trilho, as abas e o switch de tema. As paginas da Foundation sao estaticas.

Os icones do trilho sao casca do site. O switch de tema NAO e: desde a etapa 7
do Switch (25/09/2026) ele e o componente do AL, com rotulo visivel - o portao
de marcacao do components/switch/a11y.py cobra isso no HTML emitido.

Rodar: python3 site/site.py     (escreve site/index.html)
"""
import base64, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.join(ROOT, 'site')
sys.path.insert(0, os.path.join(ROOT, 'foundation'))

from color import cr  # noqa: E402  - contraste medido, nunca escrito a mao

T = json.load(open(os.path.join(ROOT, 'tokens.json')))
BTN = json.load(open(os.path.join(ROOT, 'components', 'button', 'tokens.json')))

FOUND_CSS = open(os.path.join(ROOT, 'foundation', 'al-foundation.css')).read()
BTN_TOKENS = open(os.path.join(ROOT, 'components', 'button', 'al-button-tokens.css')).read()
BTN_CSS = open(os.path.join(ROOT, 'components', 'button', 'button.css')).read()
ICON_TOKENS = open(os.path.join(ROOT, 'components', 'icon', 'al-icon-tokens.css')).read()
ICON_CSS = open(os.path.join(ROOT, 'components', 'icon', 'icon.css')).read()
ICON_MANIFEST = json.load(open(os.path.join(ROOT, 'components', 'icon', 'icons.json')))
ICON_TOK = json.load(open(os.path.join(ROOT, 'components', 'icon', 'tokens.json')))
ICON_A11Y = json.load(open(os.path.join(ROOT, 'components', 'icon', 'a11y.json')))
IB = json.load(open(os.path.join(ROOT, 'components', 'icon-button', 'tokens.json')))
IB_TOKENS = open(os.path.join(ROOT, 'components', 'icon-button',
                              'al-icon-button-tokens.css')).read()
IB_CSS = open(os.path.join(ROOT, 'components', 'icon-button', 'icon-button.css')).read()
IB_A11Y = json.load(open(os.path.join(ROOT, 'components', 'icon-button', 'a11y.json')))

TAG = json.load(open(os.path.join(ROOT, 'components', 'tag', 'tokens.json')))
TAG_TOKENS = open(os.path.join(ROOT, 'components', 'tag', 'al-tag-tokens.css')).read()
TAG_CSS = open(os.path.join(ROOT, 'components', 'tag', 'tag.css')).read()
TAG_A11Y = json.load(open(os.path.join(ROOT, 'components', 'tag', 'a11y.json')))

AVATAR = json.load(open(os.path.join(ROOT, 'components', 'avatar', 'tokens.json')))
AVATAR_TOKENS = open(os.path.join(ROOT, 'components', 'avatar', 'al-avatar-tokens.css')).read()
AVATAR_CSS = open(os.path.join(ROOT, 'components', 'avatar', 'avatar.css')).read()
AVATAR_A11Y = json.load(open(os.path.join(ROOT, 'components', 'avatar', 'a11y.json')))

SELECT = json.load(open(os.path.join(ROOT, 'components', 'select', 'tokens.json')))
SELECT_TOKENS = open(os.path.join(ROOT, 'components', 'select',
                                  'al-select-tokens.css')).read()
SELECT_CSS = open(os.path.join(ROOT, 'components', 'select', 'select.css')).read()
SELECT_A11Y = json.load(open(os.path.join(ROOT, 'components', 'select', 'a11y.json')))

CHECKBOX = json.load(open(os.path.join(ROOT, 'components', 'checkbox', 'tokens.json')))
CHECKBOX_TOKENS = open(os.path.join(ROOT, 'components', 'checkbox',
                                    'al-checkbox-tokens.css')).read()
CHECKBOX_CSS = open(os.path.join(ROOT, 'components', 'checkbox', 'checkbox.css')).read()
CHECKBOX_A11Y = json.load(open(os.path.join(ROOT, 'components', 'checkbox', 'a11y.json')))
RADIO = json.load(open(os.path.join(ROOT, 'components', 'radio', 'tokens.json')))
RADIO_TOKENS = open(os.path.join(ROOT, 'components', 'radio', 'al-radio-tokens.css')).read()
RADIO_CSS = open(os.path.join(ROOT, 'components', 'radio', 'radio.css')).read()
RADIO_A11Y = json.load(open(os.path.join(ROOT, 'components', 'radio', 'a11y.json')))
SWITCH = json.load(open(os.path.join(ROOT, 'components', 'switch', 'tokens.json')))
SWITCH_TOKENS = open(os.path.join(ROOT, 'components', 'switch', 'al-switch-tokens.css')).read()
SWITCH_CSS = open(os.path.join(ROOT, 'components', 'switch', 'switch.css')).read()
SWITCH_A11Y = json.load(open(os.path.join(ROOT, 'components', 'switch', 'a11y.json')))

META = T['meta']
P, SEM = T['color']['primitive'], T['color']['semantic']
N, O = P['neutral'], P['orange']
STEPS = ['50', '100', '200', '300', '400', '500', '600', '700', '800', '900', '950']
LAD = META['lLadder']
VERSION = META['version']

# contagens - medidas, nunca digitadas
N_PRIM = sum(len(v) for v in P.values())
N_SEM = len(SEM)
N_PAIRS = len(T['contrastReport'])
N_EXC = sum(1 for r in T['contrastReport'] if r.get('exception'))
N_AA = N_PAIRS - N_EXC
N_FAIL = sum(1 for r in T['contrastReport'] if not r.get('pass', True))
N_BTN_TOKENS = len(BTN['alias'])
N_IB_TOKENS = len(IB['alias'])
N_TAG_TOKENS = len(TAG['alias'])
N_AVATAR_TOKENS = len(AVATAR['alias'])
N_SELECT_TOKENS = len(SELECT['alias'])
N_CHECKBOX_TOKENS = len(CHECKBOX['alias'])
N_RADIO_TOKENS = len(RADIO['alias'])
N_SWITCH_TOKENS = len(SWITCH['alias'])

assert N_FAIL == 0, f'{N_FAIL} pares reprovados - o portao de contraste deveria ter barrado antes'


# ════════════════════════════════════════════════════════════ tema no palco
def scope_themes(found_css, *token_blocks):
    """
    Producao troca o tema no :root, e ai a cadeia de alias resolve sozinha.
    Aqui nao: o playground troca o tema so no palco, e substituicao de custom
    property acontece no elemento onde ela e DECLARADA, nao no ponto de uso.
    Uma alias declarada no :root ja desce resolvida com o valor claro.

    Entao, para o container tematizado funcionar, tudo que aponta para um
    semantico precisa ser re-declarado dentro do bloco de tema: os aneis de
    foco compostos e a camada inteira de cada componente - Button e Icon.
    """
    css = found_css.replace(':root[data-theme="dark"] {', '[data-theme="dark"] {')
    m = re.search(r':root\s*\{(.*?)\n\}', css, re.S)
    root = m.group(1) if m else ''
    semantic_light = '\n'.join(
        l for l in root.split('\n')
        if re.match(r'\s*--al-(bg|text|border-(subtle|default|strong|focus|brand|danger|'
                    r'success|warning|info)|shadow|elevation)', l))
    rings = '\n'.join(l for l in root.split('\n') if '--al-focus-ring' in l or
                      (l.strip().startswith('0 0 0') and l.strip().endswith((',', ';'))))
    comps = []
    for block in token_blocks:
        mb = re.search(r':root\s*\{(.*?)\n\}', block, re.S)
        if mb:
            comps.append(mb.group(1))
    btn = '\n'.join(comps)

    css += '\n[data-theme="light"] {\n' + semantic_light + '\n}\n'
    css += ('\n/* Re-declaracao para container tematizado - so o playground precisa. */\n'
            '[data-theme="light"], [data-theme="dark"] {\n' + rings + '\n' + btn + '\n}\n')
    return css


CSS_REAL = (scope_themes(FOUND_CSS, BTN_TOKENS, ICON_TOKENS, IB_TOKENS, TAG_TOKENS,
                         AVATAR_TOKENS, SELECT_TOKENS, CHECKBOX_TOKENS, RADIO_TOKENS,
                         SWITCH_TOKENS)
            + '\n' + BTN_TOKENS + '\n' + BTN_CSS
            + '\n' + ICON_TOKENS + '\n' + ICON_CSS
            + '\n' + IB_TOKENS + '\n' + IB_CSS
            + '\n' + TAG_TOKENS + '\n' + TAG_CSS
            + '\n' + AVATAR_TOKENS + '\n' + AVATAR_CSS
            + '\n' + SELECT_TOKENS + '\n' + SELECT_CSS
            + '\n' + CHECKBOX_TOKENS + '\n' + CHECKBOX_CSS
            + '\n' + RADIO_TOKENS + '\n' + RADIO_CSS
            + '\n' + SWITCH_TOKENS + '\n' + SWITCH_CSS)


# ─────────────────────────────────────────────────────────────────── os icones
ICON_DIR = os.path.join(ROOT, 'components', 'icon', 'icons')
ICON_NAMES = ICON_MANIFEST['icons']


def al_icon(name, cls='al-icon', extra=''):
    """Devolve o SVG real do repositorio, com a classe e o contrato decorativo.

    A pagina nunca redesenha um icone: ela le components/icon/icons/<nome>.svg.
    """
    raw = open(os.path.join(ICON_DIR, name + '.svg')).read()
    body = raw[raw.find('<svg'):].strip()
    return body.replace('<svg ', f'<svg class="{cls}" aria-hidden="true" '
                                 f'focusable="false"{extra} ', 1)


# a mesma ordem e o mesmo agrupamento do component set no Figma
ICON_GROUPS = [
    ('Direção e navegação', ['chevron-up', 'chevron-down', 'chevron-left', 'chevron-right',
        'chevrons-left', 'chevrons-right', 'arrow-up', 'arrow-down', 'arrow-left', 'arrow-right',
        'arrow-up-right', 'menu', 'ellipsis', 'ellipsis-vertical', 'external-link', 'house']),
    ('Ação', ['plus', 'minus', 'x', 'check', 'search', 'pencil', 'trash', 'copy', 'download',
        'upload', 'share-2', 'link', 'refresh-cw', 'send']),
    ('Status', ['info', 'circle-check', 'circle-alert', 'triangle-alert', 'circle-x',
        'circle-help', 'loader-circle']),
    ('Formulário e dados', ['eye', 'eye-off', 'calendar', 'clock', 'filter', 'arrow-up-down']),
    ('Sistema e conta', ['settings', 'user', 'users', 'log-out', 'log-in', 'lock', 'bell',
        'shield-check']),
    ('Conteúdo', ['file-text', 'folder', 'image', 'paperclip', 'bookmark', 'star', 'heart',
        'mail', 'phone']),
    ('Mídia', ['play', 'pause', 'skip-forward', 'volume-2', 'maximize']),
    ('Comércio e local', ['shopping-cart', 'credit-card', 'chart-column', 'map-pin', 'globe']),
]
_grouped = [n for _, g in ICON_GROUPS for n in g]
assert sorted(_grouped) == sorted(ICON_NAMES), 'grupos fora de sincronia com icons.json'
N_ICONS = len(ICON_NAMES)


def ink(bg):
    """Texto legivel sobre um swatch, escolhido por contraste real."""
    return N['950'] if cr(bg, N['950']) >= cr(bg, '#FFFFFF') else '#FFFFFF'


# ── retratos de demonstracao ──────────────────────────────────────────────
# Casca do site, nao asset do componente. Sao ILUSTRACOES, nao fotos de gente
# de verdade - demonstrar recorte nao justifica publicar o rosto de ninguem.
#
# A moldura e 160x120, DEITADA, de proposito: o `object-fit: cover` do
# avatar.css so tem o que provar se a origem nao for quadrada. Se um dia o
# recorte quebrar, estes dois retratos entortam na hora.
#
# O fundo sai da propria rampa do sistema - o retrato de demonstracao tambem
# nao inventa cor.
def portrait(bg1, bg2, skin, hair, squarish=False):
    cabelo = ('M48 50 Q50 8 80 10 Q112 8 112 52 L104 52 Q108 22 80 22 Q52 22 56 52 Z'
              if squarish else 'M50 44 Q80 6 110 44 Q112 20 80 16 Q48 20 50 44 Z')
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 160 120">'
        '<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{bg1}"/><stop offset="1" stop-color="{bg2}"/>'
        '</linearGradient></defs>'
        '<rect width="160" height="120" fill="url(#g)"/>'
        f'<circle cx="80" cy="78" r="46" fill="{skin}"/>'
        f'<circle cx="80" cy="48" r="30" fill="{skin}"/>'
        f'<path d="{cabelo}" fill="{hair}"/>'
        '</svg>')
    return 'data:image/svg+xml;base64,' + base64.b64encode(svg.encode()).decode()


PHOTO_A = portrait(O['100'], O['200'], '#E8B08C', '#3E2417')
PHOTO_B = portrait(P['blue']['100'], P['blue']['200'], '#D9A579', N['950'], True)


def iniciais(nome):
    """Duas letras, maiusculas. E a regra 08 das Diretrizes morando no gerador:
    a pagina nao pode ensinar um contrato que ela mesma nao cumpre."""
    partes = [x for x in re.split(r'\s+', nome.strip()) if x]
    if not partes:
        return '?'
    return (partes[0][0] + (partes[-1][0] if len(partes) > 1 else '')).upper()


def av(tipo, size='md', nome='Maria Silva', foto=None, decorativo=True):
    """Um Avatar real.

    O contrato de a11y entra AQUI, e nao no chamador, porque ele e a parte
    deste componente que mais se erra: decorativo leva `aria-hidden`, sozinho
    leva `role="img"` + `aria-label`. O a11y.py confere cada um deles no HTML
    que esta pagina emite - entao o gerador tem que acertar sempre.
    """
    a11y = 'aria-hidden="true"' if decorativo else f'role="img" aria-label="{nome}"'
    if tipo == 'photo':
        filho = f'<img class="al-avatar__photo" src="{foto or PHOTO_A}" alt="">'
    elif tipo == 'icon':
        filho = al_icon('user')
    else:
        filho = f'<span class="al-avatar__initials">{iniciais(nome)}</span>'
    return f'<span class="al-avatar al-avatar--{size}" {a11y}>{filho}</span>'


def av_person(tipo, size, nome, papel, foto=None):
    """Avatar ao lado do nome escrito - o uso mais comum, e o caso decorativo."""
    return (f'<span class="av-person">{av(tipo, size, nome, foto)}'
            f'<span class="av-who"><b>{nome}</b><i>{papel}</i></span></span>')


# ════════════════════════════════════════════════════════════ FOUNDATION · cor
FAM_ROLE = {'neutral': 'superfície, texto, borda', 'orange': 'marca · ação', 'red': 'danger',
            'amber': 'warning', 'green': 'success', 'blue': 'info'}


def ramp_grid():
    out = ['<div class="scroll-x"><table class="ramp"><thead><tr><th class="fam"></th>']
    for s in STEPS:
        out.append(f'<th><span class="step">{s}</span><span class="lval">L {LAD[s]:.3f}</span></th>')
    out.append('</tr></thead><tbody>')
    for fam in ['neutral', 'orange', 'red', 'amber', 'green', 'blue']:
        out.append(f'<tr><th class="fam"><span class="fam-name">{fam}</span>'
                   f'<span class="fam-role">{FAM_ROLE[fam]}</span></th>')
        for s in STEPS:
            h = P[fam][s]
            out.append(f'<td><div class="ramp-cell" style="background:{h};color:{ink(h)}">'
                       f'<span class="ramp-hex">{h[1:]}</span>'
                       f'<span class="ramp-cr">{cr(h, "#FFFFFF"):.2f}</span></div></td>')
        out.append('</tr>')
    out.append('</tbody></table></div>')
    return ''.join(out)


def brand_window():
    """Onde o label branco cai, em cada estado do preenchimento de marca."""
    tracks = [
        ('tema claro', 'tela branca',
         [(O['500'], 'repouso', 'orange-500'), (SEM['bg-brand-hover'][0], 'hover', 'orange-600'),
          (SEM['bg-brand-active'][0], 'pressed', 'orange-700')]),
        ('tema escuro', 'tela #181818',
         [(O['500'], 'repouso', 'orange-500'), (SEM['bg-brand-hover'][1], 'hover', 'orange-550'),
          (SEM['bg-brand-active'][1], 'pressed', 'orange-600')]),
    ]
    x0, x1, W = 3.0, 8.5, 880.0

    def X(v):
        return 132 + (v - x0) / (x1 - x0) * (W - 172)

    s = [f'<svg viewBox="0 0 {int(W)} 210" class="winsvg" role="img" aria-label="Contraste do '
         'texto branco sobre cada estado do preenchimento de marca, nos dois temas, contra a '
         'linha de 4,5 para 1 do AA">']
    s.append(f'<rect x="{X(3.0):.1f}" y="30" width="{X(4.5) - X(3.0):.1f}" height="128" class="win-exc"/>')
    s.append(f'<line x1="{X(4.5):.1f}" y1="30" x2="{X(4.5):.1f}" y2="158" class="win-bound"/>')
    s.append(f'<text x="{X(4.5) + 8:.1f}" y="24" class="win-rule">4,5:1 — AA para texto normal</text>')
    s.append(f'<text x="{X(3.0):.1f}" y="24" class="win-rule">3:1 — piso: AA para texto grande</text>')
    for i, (theme, canvas, marks) in enumerate(tracks):
        y = 62 + i * 62
        s.append(f'<text x="12" y="{y + 4:.0f}" class="win-track-name">{theme}</text>')
        s.append(f'<text x="12" y="{y + 19:.0f}" class="win-track-sub">{canvas}</text>')
        s.append(f'<line x1="{X(x0):.1f}" y1="{y:.0f}" x2="{X(x1):.1f}" y2="{y:.0f}" class="win-rail"/>')
        for hexv, state, _name in marks:
            v = cr(hexv, '#FFFFFF')
            ok = v >= 4.5
            s.append(f'<circle cx="{X(v):.1f}" cy="{y:.0f}" r="10" fill="{hexv}" class="win-dot"/>')
            s.append(f'<text x="{X(v):.1f}" y="{y - 17:.0f}" class="win-name" text-anchor="middle">{state}</text>')
            s.append(f'<text x="{X(v):.1f}" y="{y + 26:.0f}" class="win-role{"" if ok else " bad"}" '
                     f'text-anchor="middle">{v:.2f}:1</text>')
    s.append(f'<text x="{X(x0):.1f}" y="196" class="win-axis">contraste do texto branco sobre o '
             'preenchimento de marca →</text>')
    s.append('</svg>')
    return ''.join(s)


GROUPS = [('bg-', 'Superfície e preenchimento'), ('text-', 'Texto'), ('border-', 'Borda'),
          ('shadow-', 'Cor do anel de foco')]

# Guarda: nenhum semantico pode ficar de fora dos grupos acima. Sem isto, um
# token novo simplesmente nao aparece na pagina e ninguem percebe - foi o que
# aconteceu com os dois shadow-focus-* na primeira versao desta pagina.
_orfaos = [k for k in SEM if not k.startswith(tuple(p for p, _ in GROUPS))]
assert not _orfaos, f'semanticos sem grupo na tabela: {_orfaos}'


def semantic_tables():
    out = []
    for prefix, title in GROUPS:
        keys = [k for k in SEM if k.startswith(prefix)]
        out.append(f'<h3 class="sub">{title} <span class="count">{len(keys)} tokens</span></h3>'
                   '<div class="scroller"><table><thead><tr><th>Token</th>'
                   '<th colspan="2">Tema claro</th><th colspan="2">Tema escuro</th>'
                   '</tr></thead><tbody>')
        for k in keys:
            l, d = SEM[k]
            out.append(f'<tr><td class="tok">--al-{k}</td>'
                       f'<td class="chipcell"><span class="chip" style="background:{l}"></span></td>'
                       f'<td class="tok dim">{l}</td>'
                       f'<td class="chipcell"><span class="chip" style="background:{d}"></span></td>'
                       f'<td class="tok dim">{d}</td></tr>')
        out.append('</tbody></table></div>')
    return ''.join(out)


def contrast_tables():
    out = []
    for theme, label in [('light', 'Tema claro'), ('dark', 'Tema escuro')]:
        rows = [r for r in T['contrastReport'] if r['theme'] == theme]
        exc = sum(1 for r in rows if r.get('exception'))
        out.append(f'<h3 class="sub">{label} <span class="count">{len(rows)} pares · '
                   f'{len(rows) - exc} em AA pleno · {exc} exceção{"" if exc == 1 else "es"} de marca'
                   '</span></h3>')
        out.append('<div class="scroller"><table><thead><tr><th>Par</th><th>Frente</th><th>Fundo</th>'
                   '<th class="num">Medido</th><th class="num">Mín.</th><th></th></tr></thead><tbody>')
        for r in rows:
            tag = 'exc' if r.get('exception') else 'pass'
            word = 'MARCA' if r.get('exception') else 'AA'
            out.append(f'<tr><td>{r["label"]}</td>'
                       f'<td class="tok"><span class="chip sm" style="background:{r["fgHex"]}"></span>{r["fg"]}</td>'
                       f'<td class="tok"><span class="chip sm" style="background:{r["bgHex"]}"></span>{r["bg"]}</td>'
                       f'<td class="num strong">{r["ratio"]:.2f}:1</td>'
                       f'<td class="num dim">{r["min"]}</td>'
                       f'<td><span class="{tag}">{word}</span></td></tr>')
        out.append('</tbody></table></div>')
    return ''.join(out)


# ════════════════════════════════════════════════════════ FOUNDATION · tipo
def type_specimens():
    out = ['<div class="types">']
    for name, size, lead, wt, track, use in T['type']['styles']:
        fam = 'var(--al-font-mono)' if 'code' in name else 'var(--al-font-sans)'
        out.append(
            f'<div class="type-row"><div class="type-meta">'
            f'<span class="type-name">{name}</span>'
            f'<span class="type-num">{size}/{lead}</span>'
            f'<span class="type-num">w{wt}</span>'
            f'<span class="type-num">{track}</span>'
            f'<span class="type-use">{use}</span></div>'
            f'<div class="type-sample" style="font-family:{fam};font-size:{size}px;'
            f'line-height:{lead}px;font-weight:{wt};letter-spacing:{track}">'
            'Foundation aberta do AL</div></div>')
    out.append('</div>')
    return ''.join(out)


def type_token_rows():
    sizes, leads, tracks = T['type']['size'], T['type']['leading'], T['type']['tracking']
    rows = []
    for k in sizes:
        rows.append(f'<tr><td class="tok">--al-font-size-{k}</td><td class="num">{sizes[k]}px</td>'
                    f'<td class="tok">--al-line-height-{k}</td><td class="num">{leads[k]}px</td>'
                    f'<td class="num dim">{tracks[k]}</td></tr>')
    return ''.join(rows)


def weight_rows():
    return ''.join(
        f'<tr><td class="tok">--al-font-weight-{k}</td><td class="num">{v}</td>'
        f'<td style="font-weight:{v}">Publicar alterações</td></tr>'
        for k, v in T['type']['weight'].items())


# ═════════════════════════════════════════════════════ FOUNDATION · medidas
def space_bars():
    out = ['<div class="bars">']
    for v in T['space']:
        out.append(f'<div class="bar-row"><span class="bar-name">space-{v}</span>'
                   f'<span class="bar" style="width:{max(int(v), 1)}px"></span>'
                   f'<span class="bar-val">{v}px</span></div>')
    out.append('</div>')
    return ''.join(out)


def radius_grid():
    out = ['<div class="radii">']
    for k, v in T['radius'].items():
        shown = '999' if v == 9999 else str(v)
        out.append(f'<div class="rad"><div class="rad-box" style="border-radius:{min(v, 48)}px"></div>'
                   f'<span class="rad-name">{k}</span><span class="rad-val">{shown}px</span></div>')
    out.append('</div>')
    return ''.join(out)


def border_rows():
    rows = ''.join(f'<tr><td class="tok">--al-border-width-{k}</td><td class="num">{v}px</td></tr>'
                   for k, v in T['border']['width'].items())
    rows += (f'<tr><td class="tok">--al-border-focus-offset</td>'
             f'<td class="num">{T["border"]["focusOffset"]}px</td></tr>')
    return rows


def elevation_grid():
    out = ['<div class="elevs">']
    for k in ['0', '1', '2', '3', '4', '5']:
        out.append(f'<div class="elev"><div class="elev-box" style="--_e:var(--al-elevation-{k})">{k}</div>'
                   f'<span class="elev-name">elevation-{k}</span></div>')
    out.append('</div>')
    return ''.join(out)


def focus_rows():
    rows = []
    for kind in ['default', 'error']:
        for theme, label in [('light', 'claro'), ('dark', 'escuro')]:
            rows.append(f'<tr><td class="name">{kind}</td><td>tema {label}</td>'
                        f'<td class="tok dim">{T["focusRing"][kind][theme]}</td></tr>')
    return ''.join(rows)


# ═════════════════════════════════════════════════════ FOUNDATION · a prova
def proof_panels():
    def panel(i, label):
        def g(k):
            return SEM[k][i]
        return f'''
<div class="proof-card" style="background:{g('bg-canvas')};border-color:{g('border-subtle')}">
  <div class="proof-tag" style="color:{g('text-secondary')};border-color:{g('border-subtle')}">{label}</div>
  <div class="proof-body">
    <div class="pb-row">
      <span class="pb" style="background:{g('bg-brand')};color:{g('text-on-brand')}">Publicar</span>
      <span class="pb" style="background:{g('bg-brand-hover')};color:{g('text-on-brand')}">Publicar<i>hover</i></span>
      <span class="pb" style="background:{g('bg-danger')};color:{g('text-on-solid')}">Excluir</span>
      <span class="pb ghost" style="color:{g('text-primary')};border-color:{g('border-strong')}">Cancelar</span>
    </div>
    <div class="fld">
      <span class="lbl" style="color:{g('text-primary')}">Nome do projeto</span>
      <span class="inp" style="border-color:{g('border-strong')};background:{g('bg-canvas')};color:{g('text-placeholder')}">design-system</span>
    </div>
    <div class="fld">
      <span class="lbl" style="color:{g('text-primary')}">Slug</span>
      <span class="inp" style="border-color:{g('border-focus')};background:{g('bg-canvas')};color:{g('text-primary')};box-shadow:0 0 0 2px {g('bg-canvas')}, 0 0 0 4px {g('border-focus')}">al-ds</span>
    </div>
    <div class="fld">
      <span class="lbl" style="color:{g('text-danger')}">E-mail</span>
      <span class="inp" style="border-color:{g('border-danger')};background:{g('bg-canvas')};color:{g('text-primary')}">guilherme@</span>
      <span class="help" style="color:{g('text-danger')}">Falta o domínio depois do @.</span>
    </div>
    <div class="banners">
      <div class="bn" style="background:{g('bg-success-subtle')};border-color:{g('border-success')};color:{g('text-success')}"><b>Publicado.</b> A versão {VERSION} está disponível.</div>
      <div class="bn" style="background:{g('bg-warning-subtle')};border-color:{g('border-warning')};color:{g('text-warning')}"><b>Token sem uso.</b> 3 tokens não são referenciados.</div>
      <div class="bn" style="background:{g('bg-danger-subtle')};border-color:{g('border-danger')};color:{g('text-danger')}"><b>Contraste reprovado.</b> 1 par abaixo de 4,5:1.</div>
      <div class="bn" style="background:{g('bg-info-subtle')};border-color:{g('border-info')};color:{g('text-info')}"><b>Sincronizado.</b> Figma atualizado há 2 minutos.</div>
    </div>
  </div>
</div>'''
    return f'<div class="proof">{panel(0, "tema claro")}{panel(1, "tema escuro")}</div>'


# ══════════════════════════════════════════════════════════════════ BUTTON
VARIANTS = [('primary', 'Primary'), ('secondary', 'Secondary'),
            ('ghost', 'Ghost'), ('danger', 'Danger')]
SIZES = [('sm', 'sm · 36px'), ('md', 'md · 48px')]
STATES = [('default', 'Default'), ('hover', 'Hover'), ('active', 'Pressed'),
          ('focus', 'Focus'), ('disabled', 'Disabled'), ('busy', 'Loading')]
ICONS = [('none', 'Sem ícone'), ('leading', 'À esquerda'), ('trailing', 'À direita')]

# Ate a versao 0.1.1 estes dois eram svg de 16 desenhados na unha aqui dentro -
# a ultima sobra dos icones antigos no codigo. Agora saem da biblioteca, lidos
# de components/icon/icons/, e o Button deixa de inventar desenho.
BTN_ICON_LEADING = 'download'
BTN_ICON_TRAILING = 'chevron-right'
ICON_SVG = al_icon(BTN_ICON_LEADING)
ARROW_SVG = al_icon(BTN_ICON_TRAILING)


def seg(name, options, checked):
    out = [f'<div class="seg" role="radiogroup" aria-label="{name}">']
    for value, label in options:
        cid = f'{name}-{value}'
        on = ' checked' if value == checked else ''
        out.append(f'<input type="radio" id="{cid}" name="{name}" value="{value}"{on}>'
                   f'<label for="{cid}">{label}</label>')
    out.append('</div>')
    return '\n'.join(out)


def token_rows():
    rows = []
    for v, _ in VARIANTS:
        for role in ['bg', 'bg-hover', 'bg-active', 'bg-disabled', 'label',
                     'label-disabled', 'border', 'border-disabled', 'ring']:
            name = f'button-{v}-{role}'
            ref = BTN['alias'][name]
            res = BTN['resolved'][name]
            lt = res['light'] if isinstance(res, dict) else res
            sw = (f'<span class="chip sm" style="background:{lt}"></span>'
                  if isinstance(lt, str) and lt.startswith('#') else '')
            rows.append(f'<tr data-variant="{v}"><td class="tok">--al-{name}</td>'
                        f'<td class="tok dim">{"transparente" if ref == "transparent" else ref}</td>'
                        f'<td class="tok">{sw}{lt}</td></tr>')
    return '\n'.join(rows)


def geo_rows():
    rows = []
    for s, _ in SIZES:
        for role in ['padding-x', 'padding-y', 'gap', 'font']:
            name = f'button-{s}-{role}'
            res = BTN['resolved'][name]
            val = res[0] if isinstance(res, list) else res
            rows.append(f'<tr><td class="name">{s}</td><td class="tok">--al-{name}</td>'
                        f'<td class="tok dim">{BTN["alias"][name]}</td><td class="num">{val}</td></tr>')
    for role in ['radius', 'border-width']:
        name = f'button-{role}'
        rows.append(f'<tr><td class="name">ambos</td><td class="tok">--al-{name}</td>'
                    f'<td class="tok dim">{BTN["alias"][name]}</td>'
                    f'<td class="num">{BTN["resolved"][name]}</td></tr>')
    return '\n'.join(rows)


def specimen_grid():
    out = []
    for v, vlabel in VARIANTS:
        out.append(f'<div class="spec-row"><div class="spec-name">{vlabel}</div><div class="spec-cells">')
        for state, slabel in STATES:
            cls = f'al-btn al-btn--{v} al-btn--md'
            attrs = ''
            inner = '<span class="al-btn__label">Button</span>'
            if state in ('hover', 'active', 'focus'):
                cls += f' is-{state}'
            elif state == 'disabled':
                attrs = ' aria-disabled="true"'
            elif state == 'busy':
                attrs = ' aria-busy="true" aria-disabled="true"'
                inner = ('<span class="al-btn__spinner" aria-hidden="true"></span>'
                         '<span class="al-btn__label">Button</span>')
            out.append(f'<div class="spec-cell"><span class="spec-label">{slabel}</span>'
                       f'<button type="button" class="{cls}"{attrs} tabindex="-1">{inner}</button></div>')
        out.append('</div></div>')
    return '\n'.join(out)


# ═══════════════════════════════════════════════════════════ chrome do site
CHROME = """
*{box-sizing:border-box}
/* O atributo hidden vale pela regra [hidden]{display:none} do navegador, que
   QUALQUER display declarado aqui derruba - e .nav-sub, .al-btn__icon e outros
   declaram. Sem esta linha a página só funciona onde o hospedeiro injeta a
   mesma regra com !important, e quebra servida direto do repositório. */
[hidden]{display:none !important}
body{
  margin:0; background:var(--al-bg-canvas); color:var(--al-text-primary);
  font-family:var(--al-font-sans); font-size:15px; line-height:1.6;
  -webkit-font-smoothing:antialiased;
}
.shell{display:grid; grid-template-columns:236px 1fr; min-height:100vh}

/* ── trilho ── */
.rail{
  border-right:1px solid var(--al-border-subtle); background:var(--al-bg-surface);
  padding:26px 0 0; position:sticky; top:0; height:100vh; overflow-y:auto;
  display:flex; flex-direction:column;
}
.brand{display:flex; align-items:center; gap:10px; padding:0 22px 22px; margin-bottom:6px;
  border-bottom:1px solid var(--al-border-subtle)}
.brand-mark{width:26px; height:26px; border-radius:7px; background:var(--al-bg-brand);
  display:grid; place-items:center; color:#fff; font-weight:700; font-size:13px; flex:none}
.brand-name{font-weight:600; font-size:14px; letter-spacing:-.01em; line-height:1.25}
.brand-name small{display:block; font-weight:400; font-size:11px; color:var(--al-text-secondary)}
/* Trilho no estilo do Material 3: o item primario e uma pilula com icone, e a
   lista de sub-itens abre embaixo dele. Sub-item nao tem icone - o recuo e o
   alinhamento com o rotulo do pai ja dizem a hierarquia. */
.rail-nav{padding:10px 10px 0; flex:1}
.nav-group + .nav-group{margin-top:4px}
.nav-primary{
  display:flex; align-items:center; gap:12px;
  padding:10px 14px; border-radius:9999px; text-decoration:none;
  color:var(--al-text-primary); font-size:14px; font-weight:500;
}
.nav-primary:hover{background:var(--al-bg-hover)}
.nav-primary[aria-current]{background:var(--al-bg-brand-subtle); color:var(--al-text-brand)}
.nav-primary:focus-visible{outline:2px solid var(--al-border-focus); outline-offset:2px}
.nav-ico{width:20px; height:20px; flex:none; display:block; color:currentColor}
.nav-ico svg{display:block; width:100%; height:100%}
.nav-label{flex:1; min-width:0}
/* o chevron mora dentro do proprio item: um alvo so, um clique so */
.nav-chev{flex:none; width:16px; height:16px; display:block; opacity:.75}
.nav-chev svg{display:block; width:100%; height:100%; transition:transform 160ms ease}
.nav-group.is-open .nav-chev svg{transform:rotate(180deg)}
.nav-sub{display:flex; flex-direction:column; gap:1px; padding:2px 0 4px}
.nav-sub a{
  display:block; padding:8px 14px 8px 46px; border-radius:9999px;
  color:var(--al-text-secondary); text-decoration:none; font-size:13.5px;
}
.nav-sub a:hover{background:var(--al-bg-hover); color:var(--al-text-primary)}
.nav-sub a[aria-current]{background:var(--al-bg-brand-subtle); color:var(--al-text-brand); font-weight:500}
.nav-sub a:focus-visible{outline:2px solid var(--al-border-focus); outline-offset:2px}
.nav-sub a.soon{opacity:.45; cursor:default}
.nav-sub a.soon:hover{background:none; color:var(--al-text-secondary)}

/* ── rodapé do trilho: o switch de tema ──
   É o Switch do AL, não uma imitação: até 25/09/2026 era um <button
   role="switch"> desenhado à mão, com sol e lua na bolinha, e o portão de
   marcação do Switch reprovou o próprio site. Agora o rótulo "Tema escuro" é
   visível (regra 23) e o ícone saiu (ícone na bolinha está fora do escopo). */
.rail-foot{margin-top:auto; border-top:1px solid var(--al-border-subtle); padding:18px 18px 14px}
@media (prefers-reduced-motion: reduce){
  .nav-chev svg{transition:none}
}

/* ── cards das páginas-índice ── */
.cards{display:grid; grid-template-columns:repeat(auto-fill,minmax(236px,1fr)); gap:16px}
.card{
  display:flex; flex-direction:column; overflow:hidden; text-decoration:none;
  color:inherit; background:var(--al-bg-canvas); border-radius:14px;
  border:1px solid var(--al-border-subtle);
  transition:border-color 120ms ease, box-shadow 120ms ease;
}
.card:hover{border-color:var(--al-border-strong); box-shadow:var(--al-elevation-2)}
.card:focus-visible{outline:2px solid var(--al-border-focus); outline-offset:2px}
.card-thumb{
  height:112px; display:grid; place-items:center; padding:14px; overflow:hidden;
  background:var(--al-bg-surface); border-bottom:1px solid var(--al-border-subtle);
}
.card-body{padding:14px 16px 16px; display:flex; flex-direction:column; gap:5px; flex:1}
.card-title{font-size:15px; font-weight:600; letter-spacing:-.012em}
.card-desc{font-size:13px; line-height:1.5; color:var(--al-text-secondary)}
.card-soon{
  margin-top:auto; padding-top:8px; font-family:var(--al-font-mono); font-size:9.5px;
  letter-spacing:.1em; text-transform:uppercase; color:var(--al-text-secondary);
}
.card.is-soon{opacity:.5; pointer-events:none}
.card.is-soon .card-thumb{
  background-image:repeating-linear-gradient(45deg, var(--al-bg-subtle) 0 6px, transparent 6px 12px);
}

/* miniaturas — cada uma é feita do próprio assunto que ela abre */
.th-ramp{display:flex; width:100%; height:56px; border-radius:8px; overflow:hidden}
.th-ramp span{flex:1}
.th-anchor{font-family:var(--al-font-mono); font-size:17px; font-weight:600;
  color:var(--al-text-on-brand); background:var(--al-bg-brand); padding:12px 16px; border-radius:9999px}
.th-aa{font-size:38px; font-weight:700; letter-spacing:-.03em; line-height:1;
  color:var(--al-text-primary)}
.th-aa small{display:block; font-size:10.5px; font-weight:400; letter-spacing:.1em;
  text-transform:uppercase; color:var(--al-text-secondary); margin-top:7px}
.th-bars{display:flex; flex-direction:column; gap:7px; align-items:flex-start; width:100%}
.th-bars i{display:block; height:9px; border-radius:3px; background:var(--al-bg-brand)}
.th-split{display:flex; width:100%; height:56px; border-radius:8px; overflow:hidden;
  border:1px solid var(--al-border-subtle)}
.th-split div{flex:1; display:grid; place-items:center}
.th-split b{width:38px; height:13px; border-radius:9999px; display:block}
.th-soon{width:44px; height:44px; border-radius:10px; border:1.5px dashed var(--al-border-default)}

/* ── conteúdo ── */
.main{min-width:0}
.inner{max-width:1000px; padding:0 40px 100px}
.phead{padding:44px 0 0}
.eyebrow{font-family:var(--al-font-mono); font-size:10.5px; font-weight:500; letter-spacing:.14em;
  text-transform:uppercase; color:var(--al-text-secondary); margin-bottom:12px}
h1{font-size:46px; line-height:1.03; letter-spacing:-.033em; font-weight:700; margin:0 0 12px}
h1 em{font-style:normal; color:var(--al-bg-brand)}
.lede{font-size:17px; color:var(--al-text-secondary); margin:0 0 8px; max-width:62ch}
.meta{display:flex; flex-wrap:wrap; gap:8px; margin-top:18px}
.badge{font-family:var(--al-font-mono); font-size:10.5px; font-weight:500; letter-spacing:.06em;
  padding:4px 10px; border-radius:9999px; background:var(--al-bg-subtle); color:var(--al-text-secondary)}
.badge.on{background:var(--al-bg-brand-subtle); color:var(--al-text-brand)}

/* ── abas ── */
.tabs{display:flex; gap:2px; border-bottom:1px solid var(--al-border-subtle);
  margin:32px 0 0; position:sticky; top:0; background:var(--al-bg-canvas); z-index:5;
  overflow-x:auto}
.tabs button{
  appearance:none; background:none; border:0; border-bottom:2px solid transparent;
  padding:13px 16px; font-family:inherit; font-size:14px; font-weight:500;
  color:var(--al-text-secondary); cursor:pointer; white-space:nowrap; margin-bottom:-1px;
}
.tabs button:hover{color:var(--al-text-primary)}
.tabs button[aria-selected="true"]{color:var(--al-bg-brand); border-bottom-color:var(--al-bg-brand)}
.tabs button:focus-visible{outline:2px solid var(--al-border-focus); outline-offset:-2px}
.panel{padding-top:36px}

section{margin-bottom:52px}
h2{font-size:12.5px; font-family:var(--al-font-mono); font-weight:500; letter-spacing:.13em;
  text-transform:uppercase; color:var(--al-text-secondary); margin:0 0 20px;
  padding-bottom:10px; border-bottom:1px solid var(--al-border-subtle)}
h3{font-size:18px; font-weight:600; letter-spacing:-.015em; margin:0 0 8px}
h3.sub{font-size:11px; font-family:var(--al-font-mono); font-weight:500; letter-spacing:.12em;
  text-transform:uppercase; color:var(--al-text-secondary); margin:30px 0 12px;
  display:flex; align-items:baseline; gap:10px; flex-wrap:wrap}
h3.sub:first-child{margin-top:0}
.count{font-family:var(--al-font-mono); font-size:10.5px; letter-spacing:0; text-transform:none;
  color:var(--al-text-secondary); opacity:.8; font-weight:400}
p{margin:0 0 13px; max-width:68ch}
p:last-child{margin-bottom:0}
code{font-family:var(--al-font-mono); font-size:.86em; background:var(--al-bg-subtle);
  padding:2px 5px; border-radius:4px; white-space:nowrap}

/* ── playground ── */
.pg{border:1px solid var(--al-border-subtle); border-radius:12px; overflow:hidden}
.stage{
  display:grid; place-items:center; min-height:230px; padding:44px 24px;
  background:var(--al-bg-surface);
  background-image:radial-gradient(var(--al-border-subtle) 1px, transparent 1px);
  background-size:16px 16px;
}
.stage[data-theme]{background-color:var(--al-bg-canvas)}
.controls{border-top:1px solid var(--al-border-subtle); background:var(--al-bg-canvas);
  padding:20px 22px; display:grid; gap:16px}
.ctl{display:grid; grid-template-columns:104px 1fr; gap:14px; align-items:center}
.ctl > label:first-child, .ctl > .ctl-name{
  font-family:var(--al-font-mono); font-size:10.5px; font-weight:500; letter-spacing:.1em;
  text-transform:uppercase; color:var(--al-text-secondary);
}
.seg{display:inline-flex; flex-wrap:wrap; gap:6px}
.seg input{position:absolute; opacity:0; width:1px; height:1px}
.seg label{
  padding:6px 13px; border-radius:9999px; border:1px solid var(--al-border-default);
  font-size:13px; cursor:pointer; color:var(--al-text-secondary); user-select:none;
}
.seg label:hover{background:var(--al-bg-hover); color:var(--al-text-primary)}
.seg input:checked + label{
  background:var(--al-bg-brand-subtle); border-color:var(--al-bg-brand);
  color:var(--al-text-brand); font-weight:500;
}
.seg input:focus-visible + label{outline:2px solid var(--al-border-focus); outline-offset:2px}
.txt{
  font-family:inherit; font-size:13.5px; padding:7px 11px; width:100%; max-width:280px;
  border:1px solid var(--al-border-default); border-radius:8px;
  background:var(--al-bg-canvas); color:var(--al-text-primary);
}
.txt:focus-visible{outline:2px solid var(--al-border-focus); outline-offset:1px; border-color:var(--al-border-focus)}

/* ── código ── */
.codewrap{border-top:1px solid var(--al-border-subtle)}
.codebar{display:flex; align-items:center; justify-content:space-between; gap:12px;
  padding:11px 22px; background:var(--al-bg-surface); border-bottom:1px solid var(--al-border-subtle)}
.codebar span{font-family:var(--al-font-mono); font-size:10.5px; font-weight:500;
  letter-spacing:.1em; text-transform:uppercase; color:var(--al-text-secondary)}
.copy{
  appearance:none; border:1px solid var(--al-border-default); background:var(--al-bg-canvas);
  color:var(--al-text-secondary); font-family:var(--al-font-mono); font-size:11px;
  padding:5px 12px; border-radius:9999px; cursor:pointer;
}
.copy:hover{color:var(--al-text-primary); border-color:var(--al-border-strong)}
.copy:focus-visible{outline:2px solid var(--al-border-focus); outline-offset:2px}
pre{margin:0; padding:18px 22px; overflow-x:auto; background:var(--al-bg-canvas)}
pre code{background:none; padding:0; font-size:12.5px; line-height:1.65; white-space:pre; color:var(--al-text-primary)}

/* ── tabelas ── */
.scroller{overflow-x:auto; border:1px solid var(--al-border-subtle); border-radius:10px}
.scroll-x{overflow-x:auto}
table{border-collapse:collapse; width:100%; font-size:13px; min-width:620px}
th,td{padding:9px 15px; text-align:left; border-bottom:1px solid var(--al-border-subtle)}
thead th{font-family:var(--al-font-mono); font-size:10px; font-weight:500; letter-spacing:.1em;
  text-transform:uppercase; color:var(--al-text-secondary); background:var(--al-bg-surface); white-space:nowrap}
tbody tr:last-child td{border-bottom:0}
td.tok{font-family:var(--al-font-mono); font-size:12px; white-space:nowrap}
td.tok.dim, td.num.dim{color:var(--al-text-secondary)}
td.name{font-weight:600}
td.num{font-family:var(--al-font-mono); text-align:right; font-variant-numeric:tabular-nums}
td.num.strong{font-weight:600}
td.chipcell{width:30px; padding-right:4px}
.chip{display:inline-block; width:18px; height:18px; border-radius:5px; vertical-align:middle;
  border:1px solid var(--al-border-subtle)}
.chip.sm{width:11px; height:11px; border-radius:3px; margin-right:7px; vertical-align:-1px}
.pass,.exc{display:inline-block; font-family:var(--al-font-mono); font-size:9.5px; font-weight:500;
  letter-spacing:.05em; padding:2px 8px; border-radius:9999px; white-space:nowrap;
  background:var(--al-bg-success-subtle); color:var(--al-text-success)}
.exc{background:var(--al-bg-warning-subtle); color:var(--al-text-warning)}

/* ── estatísticas ── */
.stats{display:flex; flex-wrap:wrap; border:1px solid var(--al-border-subtle);
  border-radius:12px; overflow:hidden; margin:22px 0 40px}
.stat{flex:1 1 168px; padding:16px 18px; border-right:1px solid var(--al-border-subtle)}
.stat:last-child{border-right:0}
.stat b{display:block; font-size:24px; line-height:30px; font-weight:700; letter-spacing:-.02em;
  font-variant-numeric:tabular-nums}
.stat span{display:block; font-size:12px; line-height:16px; color:var(--al-text-secondary); margin-top:4px}
.stat.hl b{color:var(--al-bg-brand)}

/* ── rampa de primitivas ── */
table.ramp{border-collapse:separate; border-spacing:3px; min-width:960px}
table.ramp th, table.ramp td{padding:0; border-bottom:0; background:none}
table.ramp thead th{text-align:center; padding-bottom:8px; text-transform:none; letter-spacing:0}
.step{display:block; font-family:var(--al-font-mono); font-size:11px; font-weight:600;
  color:var(--al-text-primary)}
.lval{display:block; font-family:var(--al-font-mono); font-size:9.5px;
  color:var(--al-text-secondary); margin-top:1px}
th.fam{text-align:left; width:120px; padding-right:12px; vertical-align:middle}
.fam-name{display:block; font-family:var(--al-font-mono); font-size:12.5px; font-weight:600;
  color:var(--al-text-primary); text-transform:none; letter-spacing:0}
.fam-role{display:block; font-size:11px; line-height:14px; color:var(--al-text-secondary);
  margin-top:2px; text-transform:none; letter-spacing:0; font-family:var(--al-font-sans)}
.ramp-cell{height:58px; border-radius:6px; display:flex; flex-direction:column;
  justify-content:flex-end; padding:6px 7px; gap:1px}
.ramp-hex{font-family:var(--al-font-mono); font-size:9.5px; font-weight:600; opacity:.92}
.ramp-cr{font-family:var(--al-font-mono); font-size:9px; opacity:.62; font-variant-numeric:tabular-nums}

/* ── janela da marca ── */
.winsvg{width:100%; height:auto; margin:6px 0 4px}
.win-exc{fill:var(--al-bg-brand); opacity:.09}
.win-rail{stroke:var(--al-border-default); stroke-width:1.5}
.win-bound{stroke:var(--al-bg-brand); stroke-width:1.5; stroke-dasharray:3 3}
.win-track-name{fill:var(--al-text-primary); font-family:var(--al-font-sans); font-size:12px; font-weight:600}
.win-track-sub{fill:var(--al-text-secondary); font-family:var(--al-font-mono); font-size:10px}
.win-rule{fill:var(--al-text-secondary); font-family:var(--al-font-sans); font-size:11px}
.win-dot{stroke:var(--al-bg-canvas); stroke-width:2.5}
.win-name{fill:var(--al-text-primary); font-family:var(--al-font-mono); font-size:11px; font-weight:600}
.win-role{fill:var(--al-text-secondary); font-family:var(--al-font-sans); font-size:10.5px}
.win-role.bad{fill:var(--al-text-disabled)}
.win-axis{fill:var(--al-text-secondary); font-family:var(--al-font-sans); font-size:10.5px}

/* ── espécimes de tipografia ── */
.types{display:flex; flex-direction:column}
.type-row{padding:18px 0; border-bottom:1px solid var(--al-border-subtle)}
.type-row:last-child{border-bottom:0}
.type-meta{display:flex; flex-wrap:wrap; align-items:baseline; gap:14px; margin-bottom:9px}
.type-name{font-family:var(--al-font-mono); font-size:11.5px; font-weight:600; min-width:92px}
.type-num{font-family:var(--al-font-mono); font-size:11px; color:var(--al-text-secondary);
  font-variant-numeric:tabular-nums}
.type-use{font-size:11px; color:var(--al-text-secondary); margin-left:auto}
.type-sample{color:var(--al-text-primary); text-wrap:balance}

/* ── espaço, radius, elevação ── */
.grid2{display:grid; grid-template-columns:repeat(auto-fit,minmax(290px,1fr)); gap:40px}
.bars{display:flex; flex-direction:column; gap:7px}
.bar-row{display:flex; align-items:center; gap:12px}
.bar-name{font-family:var(--al-font-mono); font-size:11.5px; color:var(--al-text-secondary);
  width:82px; flex:none}
.bar{height:14px; background:var(--al-bg-brand); border-radius:3px; flex:none; min-width:1px}
.bar-val{font-family:var(--al-font-mono); font-size:11px; color:var(--al-text-secondary);
  font-variant-numeric:tabular-nums}
.radii{display:flex; flex-wrap:wrap; gap:16px}
.rad{display:flex; flex-direction:column; gap:6px; align-items:center}
.rad-box{width:56px; height:56px; background:var(--al-bg-subtle); border:1.5px solid var(--al-bg-brand)}
.rad-name{font-family:var(--al-font-mono); font-size:11px; font-weight:600}
.rad-val{font-family:var(--al-font-mono); font-size:10px; color:var(--al-text-secondary)}
.elevs{display:flex; flex-wrap:wrap; gap:22px}
.elev{display:flex; flex-direction:column; gap:10px; align-items:center}
.elev-box{width:84px; height:64px; border-radius:10px; background:var(--al-bg-surface-raised);
  border:1px solid var(--al-border-subtle); box-shadow:var(--_e); display:grid; place-items:center;
  font-family:var(--al-font-mono); font-size:15px; font-weight:600; color:var(--al-text-secondary)}
.elev-name{font-family:var(--al-font-mono); font-size:10.5px; color:var(--al-text-secondary)}

/* ── a prova ── */
.proof{display:grid; grid-template-columns:repeat(auto-fit,minmax(320px,1fr)); gap:20px}
.proof-card{border:1px solid; border-radius:14px; overflow:hidden}
.proof-tag{font-family:var(--al-font-mono); font-size:10.5px; letter-spacing:.07em;
  text-transform:uppercase; padding:11px 20px; border-bottom:1px solid}
.proof-body{padding:22px 20px; display:flex; flex-direction:column; gap:20px}
.pb-row{display:flex; flex-wrap:wrap; gap:10px}
.pb{font-size:14px; font-weight:500; line-height:20px; padding:10px 16px; border-radius:8px;
  display:inline-flex; align-items:center; gap:7px}
.pb i{font-style:normal; font-family:var(--al-font-mono); font-size:9px; opacity:.62}
.pb.ghost{background:transparent; border:1px solid}
.fld{display:flex; flex-direction:column; gap:6px}
.fld .lbl{font-size:14px; font-weight:500; line-height:20px}
.inp{border:1px solid; border-radius:8px; padding:9px 12px; font-size:14px; line-height:20px}
.help{font-size:12px; line-height:16px}
.banners{display:flex; flex-direction:column; gap:9px}
.bn{border-left:3px solid; border-radius:0 8px 8px 0; padding:10px 14px; font-size:13px; line-height:19px}
.bn b{font-weight:600}

/* ── anatomia, notas, regras, do/don't ── */
.anat{display:grid; grid-template-columns:repeat(auto-fit,minmax(190px,1fr)); gap:1px;
  background:var(--al-border-subtle); border:1px solid var(--al-border-subtle);
  border-radius:10px; overflow:hidden}
.anat > div{background:var(--al-bg-canvas); padding:16px 18px}
.anat b{display:block; font-family:var(--al-font-mono); font-size:10px; letter-spacing:.1em;
  text-transform:uppercase; color:var(--al-bg-brand); margin-bottom:5px}
.anat span{font-size:13px; color:var(--al-text-secondary)}
.note{padding:15px 18px; background:var(--al-bg-surface); border-left:2px solid var(--al-bg-brand);
  border-radius:0 8px 8px 0; font-size:14px; margin-bottom:14px}
.note:last-child{margin-bottom:0}
.note b{display:block; margin-bottom:4px}
.note p{max-width:74ch; font-size:14px}
.note p + p{margin-top:9px}
.rule{display:grid; grid-template-columns:auto 1fr; gap:18px; padding:20px 0;
  border-top:1px solid var(--al-border-subtle)}
.rule:last-of-type{border-bottom:1px solid var(--al-border-subtle)}
.rn{font-family:var(--al-font-mono); font-size:11.5px; font-weight:500;
  color:var(--al-text-secondary); padding-top:3px}
.dd{display:grid; grid-template-columns:repeat(auto-fit,minmax(270px,1fr)); gap:1px;
  background:var(--al-border-subtle); border:1px solid var(--al-border-subtle);
  border-radius:10px; overflow:hidden; margin-bottom:14px}
.dd .cell{background:var(--al-bg-canvas); padding:18px 20px; display:flex; flex-direction:column; gap:13px}
.dd .lab{font-family:var(--al-font-mono); font-size:10px; font-weight:500; letter-spacing:.13em;
  text-transform:uppercase; display:flex; align-items:center; gap:7px}
.dd .do .lab{color:var(--al-text-success)}
.dd .no .lab{color:var(--al-text-danger)}
.dd .do .lab::before, .dd .no .lab::before{content:''; width:7px; height:7px; border-radius:50%;
  background:currentColor}
.dd .stage2{display:flex; flex-wrap:wrap; gap:11px; align-items:center; padding:18px 16px;
  background:var(--al-bg-surface); border-radius:8px; min-height:72px}
.dd .cap{font-size:13px; color:var(--al-text-secondary); margin:0}
.dd .cap b{color:var(--al-text-primary); font-weight:600}

/* ── estados forçados: SÓ para o playground e as folhas de espécimes.
      Repetem as declarações reais do button.css, porque :hover e :active
      não podem ser simulados sem ponteiro. ── */
.al-btn.is-hover{background-color:var(--_bg-hover)}
.al-btn.is-active{background-color:var(--_bg-active)}
.al-btn.is-focus{box-shadow:var(--_ring); outline:none}

/* O mesmo andaime para o Icon Button. Estas três pseudo-classes só acendem com
   ponteiro ou teclado, e a folha de espécimes precisa mostrar os seis estados
   ao mesmo tempo. Cada linha repete a declaração do icon-button.css - nenhuma
   inventa valor. */
.al-icon-btn.is-hover{background-color:var(--_bg-hover)}
.al-icon-btn.is-active{background-color:var(--_bg-active)}
.al-icon-btn.is-focus{box-shadow:var(--_ring); outline:none}
/* O anel do Tag mora no X, nao na tag - entao o especime forca o filho. */
.al-tag.is-focus .al-tag__dismiss{box-shadow:var(--al-tag-dismiss-ring); outline:none}
/* faixa de especimes de tag: o .stage2 ja da o fundo, aqui so o ritmo */
.tagrow{display:flex; flex-wrap:wrap; gap:9px; align-items:center}
.tagrow + .tagrow{margin-top:11px}

footer{margin-top:64px; padding-top:24px; border-top:1px solid var(--al-border-subtle);
  color:var(--al-text-secondary); font-size:12.5px; display:flex; flex-wrap:wrap; gap:8px 20px}
footer code{background:none; padding:0}

@media (max-width:900px){
  .shell{grid-template-columns:1fr}
  .rail{position:static; height:auto; padding-bottom:14px}
  .inner{padding:0 20px 72px}
  h1{font-size:34px}
  .ctl{grid-template-columns:1fr; gap:8px}
  .spec-row{grid-template-columns:1fr}
  .spec-name{padding-top:0}
}
"""

# ── folha de espécimes do Button (compartilhada com a aba Especificações) ──
CHROME += """
.spec-row{display:grid; grid-template-columns:96px 1fr; gap:18px; align-items:start;
  padding:20px 0; border-top:1px solid var(--al-border-subtle)}
.spec-row:last-child{border-bottom:1px solid var(--al-border-subtle)}
.spec-name{font-weight:600; font-size:14px; padding-top:20px}
.spec-cells{display:flex; flex-wrap:wrap; gap:22px}
.spec-cell{display:flex; flex-direction:column; gap:8px; align-items:flex-start}
.spec-label{font-family:var(--al-font-mono); font-size:9.5px; letter-spacing:.1em;
  text-transform:uppercase; color:var(--al-text-secondary)}
"""


# ══════════════════════════════════════════════════════════ montagem da página
def simple_page(pid, eyebrow, title, lede, badges, body, first=False):
    """Pagina sem abas - para assunto que nao tem mais de um recorte."""
    meta = ''
    if badges:
        meta = ('<div class="meta">' + ''.join(
            f'<span class="badge{" on" if on else ""}">{b}</span>' for b, on in badges) + '</div>')
    return (f'<div class="page" id="pg-{pid}"{"" if first else " hidden"}>'
            f'<header class="phead"><div class="eyebrow">{eyebrow}</div><h1>{title}</h1>'
            f'<p class="lede">{lede}</p>{meta}</header>'
            f'<div class="panel">{body}</div></div>')


def card(pid, title, desc, thumb, soon=False):
    """Card da pagina-indice. A miniatura e feita do assunto que ela abre."""
    if soon:
        return (f'<div class="card is-soon"><div class="card-thumb">{thumb}</div>'
                f'<div class="card-body"><span class="card-title">{title}</span>'
                f'<span class="card-desc">{desc}</span>'
                f'<span class="card-soon">Em breve</span></div></div>')
    return (f'<a class="card" href="#/{pid}" data-page="{pid}">'
            f'<div class="card-thumb">{thumb}</div>'
            f'<div class="card-body"><span class="card-title">{title}</span>'
            f'<span class="card-desc">{desc}</span></div></a>')


# ── miniaturas ────────────────────────────────────────────────────────────
TH_PRINCIPIOS = f'<span class="th-anchor">{META["brandAnchor"]}</span>'
TH_PROVA = ('<div class="th-split">'
            f'<div style="background:{SEM["bg-canvas"][0]}">'
            f'<b style="background:{SEM["bg-brand"][0]}"></b></div>'
            f'<div style="background:{SEM["bg-canvas"][1]}">'
            f'<b style="background:{SEM["bg-brand"][1]}"></b></div></div>')
TH_COR = ('<div class="th-ramp">'
          + ''.join(f'<span style="background:{O[s]}"></span>' for s in STEPS)
          + '</div>')
TH_TIPO = '<div class="th-aa">Aa<small>Inter · 14 estilos</small></div>'
TH_ESPACO = ('<div class="th-bars">'
             + ''.join(f'<i style="width:{w}%"></i>' for w in (14, 26, 48, 84))
             + '</div>')
TH_BUTTON = ('<button type="button" class="al-btn al-btn--primary al-btn--sm" tabindex="-1">'
             '<span class="al-btn__label">Publicar</span></button>')
TH_ICONBUTTON = ('<div class="th-icons">'
                 + ''.join(
                     f'<button type="button" class="al-icon-btn al-icon-btn--{v} al-icon-btn--sm"'
                     f' aria-label="{lab}" tabindex="-1">'
                     f'<span class="al-icon-btn__spinner" aria-hidden="true"></span>'
                     f'{al_icon(ic)}</button>'
                     for v, ic, lab in (('primary', 'search', 'Buscar'),
                                        ('secondary', 'pencil', 'Editar'),
                                        ('ghost', 'ellipsis-vertical', 'Mais opções')))
                 + '</div>')
TH_ICON = ('<div class="th-icons">'
           + ''.join(al_icon(n) for n in
                     ['search', 'heart', 'settings', 'bell', 'star', 'trash'])
           + '</div>')
TH_TAG = ('<div class="th-icons">'
          '<span class="al-tag al-tag--filled al-tag--success al-tag--sm">Pago</span>'
          '<span class="al-tag al-tag--outlined al-tag--info al-tag--sm">Novo</span>'
          '</div>')
TH_AVATAR = ('<div class="th-icons">'
             + av('photo', 'sm', 'Maria Silva')
             + av('initials', 'sm', 'Diego Costa')
             + av('icon', 'sm')
             + '</div>')
TH_SOON = '<div class="th-soon"></div>'

ICO_FUNDACAO = ('<svg viewBox="0 0 24 24" fill="none" aria-hidden="true">'
                '<path d="M12 3 3 7.5 12 12l9-4.5L12 3Z" stroke="currentColor" stroke-width="1.6" '
                'stroke-linejoin="round"/><path d="m3 12.5 9 4.5 9-4.5" stroke="currentColor" '
                'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>'
                '<path d="m3 17.5 9 4.5 9-4.5" stroke="currentColor" stroke-width="1.6" '
                'stroke-linecap="round" stroke-linejoin="round"/></svg>')
ICO_COMPONENTES = ('<svg viewBox="0 0 24 24" fill="none" aria-hidden="true">'
                   '<rect x="3" y="3" width="7.5" height="7.5" rx="2" stroke="currentColor" stroke-width="1.6"/>'
                   '<rect x="13.5" y="3" width="7.5" height="7.5" rx="2" stroke="currentColor" stroke-width="1.6"/>'
                   '<rect x="3" y="13.5" width="7.5" height="7.5" rx="2" stroke="currentColor" stroke-width="1.6"/>'
                   '<rect x="13.5" y="13.5" width="7.5" height="7.5" rx="3.75" stroke="currentColor" '
                   'stroke-width="1.6" stroke-dasharray="2.6 2.4"/></svg>')
CARET = ('<svg viewBox="0 0 16 16" fill="none" aria-hidden="true">'
         '<path d="m4 6 4 4 4-4" stroke="currentColor" stroke-width="1.6" '
         'stroke-linecap="round" stroke-linejoin="round"/></svg>')


def page(pid, eyebrow, title, lede, badges, tabs, extra_head='', first=False):
    """Uma entrada do trilho. `tabs` = [(slug, rótulo, html)]."""
    bar = [f'<div class="tabs" role="tablist" aria-label="Seções de {title}">']
    panels = []
    for i, (slug, label, html) in enumerate(tabs):
        tid, panid = f't-{pid}-{slug}', f'p-{pid}-{slug}'
        on = i == 0
        bar.append(f'<button role="tab" id="{tid}" aria-controls="{panid}" '
                   f'aria-selected="{"true" if on else "false"}"'
                   f'{"" if on else " tabindex=-1"}>{label}</button>')
        panels.append(f'<div class="panel" id="{panid}" role="tabpanel" aria-labelledby="{tid}" '
                      f'tabindex="0"{"" if on else " hidden"}>{html}</div>')
    bar.append('</div>')
    badge_html = ''.join(f'<span class="badge{" on" if on else ""}">{b}</span>' for b, on in badges)
    return (f'<div class="page" id="pg-{pid}"{"" if first else " hidden"}>'
            f'<header class="phead"><div class="eyebrow">{eyebrow}</div><h1>{title}</h1>'
            f'<p class="lede">{lede}</p><div class="meta">{badge_html}</div>{extra_head}</header>'
            + ''.join(bar) + ''.join(panels) + '</div>')


# ─────────────────────────────────────────────────────── Fundação · princípios
STATS = f'''<div class="stats">
  <div class="stat hl"><b>{META['brandAnchor']}</b><span>âncora de marca, preservada exata</span></div>
  <div class="stat"><b>{N_PRIM}</b><span>primitivas em 6 famílias</span></div>
  <div class="stat"><b>{N_SEM}</b><span>semânticos, cada um com dois temas</span></div>
  <div class="stat hl"><b>{N_AA} / {N_PAIRS}</b><span>pares em AA pleno · {N_EXC} exceções de marca</span></div>
</div>'''

TAB_PRINCIPIOS = f'''
<section>
  <h2>As cinco decisões que travam o resto</h2>
  <p>Tudo o que vem depois é consequência destas. São fáceis de desfazer por engano numa
  contribuição, então ficam registradas antes de qualquer valor.</p>
  <div class="scroller" style="margin-top:18px"><table><tbody>
    <tr><td class="tok" style="width:96px">âncora</td><td><b>{META['brandAnchor']} é imutável.</b>
      Ela fixa L 0,666 na escada compartilhada. Mudar a âncora é mudar a marca inteira.</td></tr>
    <tr><td class="tok">rótulo</td><td><b>Texto claro sobre a marca.</b> Branco sobre
      <code>{META['brandAnchor']}</code> dá {cr(O['500'], '#FFFFFF'):.2f}:1 — abaixo dos 4,5:1 de texto
      normal, acima dos 3:1 de texto grande e de elemento não-textual. É escolha de identidade,
      tomada com o número na mão.</td></tr>
    <tr><td class="tok">neutro</td><td><b>O cinza é acromático.</b> Chroma zero em toda a rampa —
      <code>r = g = b</code> nos onze degraus. A escala fria anterior saiu junto com a atualização
      da marca.</td></tr>
    <tr><td class="tok">escuro</td><td><b>O tema escuro não é inversão.</b> Sólidos vão para o degrau
      500 com texto escuro, tonalizados de 100 para 950, e elevação troca sombra por superfície que
      clareia.</td></tr>
    <tr><td class="tok">portão</td><td><b>Contraste é portão de build.</b> Os {N_PAIRS} pares rodam a
      cada alteração de cor. Um par abaixo do mínimo quebra o build — nunca se afrouxa o
      mínimo.</td></tr>
  </tbody></table></div>
</section>

<section>
  <h2>Como um componente entra no sistema</h2>
  <p>Oito etapas, uma fechada antes de a próxima abrir. O Button percorreu as oito; é por isso
  que ele é o único componente publicado até aqui.</p>
  <div class="anat" style="margin-top:18px">
    <div><b>01 · Definir</b><span>Escopo, precedentes em Carbon, Primer, Polaris, Material e Spectrum, auditoria do que já existe.</span></div>
    <div><b>02 · Desenhar</b><span>Forma e composição no Figma. Etapa humana, por escolha.</span></div>
    <div><b>03 · Tokenizar</b><span>Cada decisão do desenho vira alias para a camada semântica. Nenhum valor cru.</span></div>
    <div><b>04 · Documentar</b><span>Regras de uso e dos/don'ts ancorados no que os sistemas de referência publicam.</span></div>
    <div><b>05 · Codar</b><span>CSS sem literal. O <code>check.py</code> recusa o arquivo se um escapar.</span></div>
    <div><b>06 · QA</b><span>Combinação renderizada — variante × estado × tema — contra o fundo efetivo.</span></div>
    <div><b>07 · Playground</b><span>A página instancia o CSS real, não uma cópia.</span></div>
    <div><b>08 · Versionar</b><span>PR de <code>dev</code> para <code>main</code>, tag no merge. Componente novo sobe MINOR.</span></div>
  </div>
</section>

<section>
  <h2>Os quatro portões</h2>
  <p>Validação aqui é portão de build, nunca revisão manual. Cada script aborta com saída
  diferente de zero, e um portão vermelho impede o commit de virar release.</p>
  <div class="scroller" style="margin-top:18px"><table>
    <thead><tr><th>Portão</th><th>Script</th><th>O que ele recusa</th></tr></thead>
    <tbody>
      <tr><td class="name">Contraste</td><td class="tok">foundation/export.py</td>
        <td>Qualquer par abaixo do mínimo WCAG que não esteja nomeado como exceção.</td></tr>
      <tr><td class="name">Alias</td><td class="tok">components/&lt;c&gt;/tokens.py</td>
        <td>Token de componente que aponte para primitiva em vez de semântico.</td></tr>
      <tr><td class="name">Literal no CSS</td><td class="tok">components/&lt;c&gt;/check.py</td>
        <td>Cor, espaço, raio ou tipografia escrita direto no arquivo do componente.</td></tr>
      <tr><td class="name">Acessibilidade</td><td class="tok">components/&lt;c&gt;/a11y.py</td>
        <td>Combinação renderizada que reprove — não par de token solto.</td></tr>
    </tbody>
  </table></div>
</section>'''

TAB_PROVA = f'''
<section>
  <h2>Os mesmos tokens, os dois temas</h2>
  <p>Nada aqui usa valor literal: cada cor destes dois painéis sai da camada semântica, lida do
  <code>tokens.json</code> no momento em que esta página foi gerada. É a prova de que a troca de
  tema não é retrabalho — é a mesma árvore de tokens resolvendo diferente.</p>
  <div style="margin-top:20px">{proof_panels()}</div>
</section>'''

# ─────────────────────────────────────────────────────────────── Fundação · cor
TAB_ESCALA = f'''
<section>
  <h2>Uma escada de lightness para todas as famílias</h2>
  <p>Cada degrau tem a mesma lightness OKLab nas seis famílias. O degrau 500 é <b>0,666</b> porque
  é a lightness de <code>{META['brandAnchor']}</code>. Isso significa que trocar
  <code>green-600</code> por <code>red-600</code> num componente não muda o contraste — a
  acessibilidade sobrevive à troca de cor.</p>
  <p>A escada é comprimida nas duas pontas: os degraus claros ficam próximos porque é onde vivem
  superfície e borda, e os escuros também, porque é onde vive a elevação do tema escuro.</p>
  <div class="note" style="margin-top:18px">
    <b>Por que 0,666 importa mais do que parece</b>
    <p>Um cinza nessa lightness dá exatamente 3,03:1 contra o branco — o piso do WCAG para elemento
    não-textual. A âncora de marca caiu, por coincidência, na fronteira exata entre "serve como
    borda" e "não serve". Todo o resto do sistema se organiza em volta desse ponto.</p>
  </div>
</section>

<section>
  <h2>Primitivas <span class="count">{N_PRIM} cores</span></h2>
  <p>O número pequeno em cada amostra é o contraste contra o branco. A rampa é conferida contra os
  swatches da página <code>Assets</code> do Figma, que é a fonte da verdade da marca.</p>
  <div style="margin-top:18px">{ramp_grid()}</div>
  <div class="note" style="margin-top:20px">
    <b>Como o vermelho e o amarelo fogem da marca</b>
    <p>O laranja está em hue 38°. O amarelo de warning foi empurrado para 85° — 47° de distância,
    sem ambiguidade. O vermelho de danger ficou em 20°, e nos degraus claros ele vira levemente
    rosado justamente para se afastar do pêssego da marca.</p>
    <p><b>O que a distância não resolve.</b> Em tonalizados muito claros, <code>orange-100</code> e
    <code>red-100</code> ficam a 0,017 de distância perceptual — praticamente idênticos. Isso é
    física, não erro de projeto: no degrau 100 nenhum par de cores quentes se distingue. Por isso
    banner nenhum se identifica só pelo fundo — todos carregam ícone, borda colorida no degrau 500+
    e texto. É o que a WCAG 1.4.1 exige de qualquer forma.</p>
  </div>
  <div class="note">
    <b>Componente nenhum consome primitiva direto</b>
    <p>Esta camada existe para ser referenciada pela camada semântica, e só por ela. Usar
    <code>--al-color-orange-500</code> dentro de um componente é o erro que o portão de alias
    recusa: o componente deixaria de acompanhar o tema.</p>
  </div>
</section>'''

TAB_SEMANTICOS = f'''
<section>
  <h2>A camada que troca com o tema</h2>
  <p>{N_SEM} tokens, cada um com um valor por tema. É esta camada que muda quando o tema vira, e é
  aqui que a intenção fica registrada: <code>bg-danger</code> diz o que a cor <i>significa</i>,
  <code>red-700</code> diz apenas o que ela <i>é</i>.</p>
  <div style="margin-top:22px">{semantic_tables()}</div>
</section>'''

TAB_CONTRASTE = f'''
<section>
  <h2>O que o texto claro sobre a marca custa, medido</h2>
  <p>Superfície de marca carrega texto branco — decisão de identidade. Branco sobre
  <code>{META['brandAnchor']}</code> dá <b>{cr(O['500'], '#FFFFFF'):.2f}:1</b>: abaixo dos 4,5:1 que
  a WCAG exige de texto normal, acima dos 3:1 que ela exige de texto grande e de elemento
  não-textual. O sistema não esconde isso; ele mede, nomeia e mostra onde cada estado cai.</p>
  {brand_window()}
  <div class="note" style="margin-top:16px">
    <b>Com texto claro a direção inverte — e isso simplifica o sistema</b>
    <p>Quando o texto era escuro, escurecer o preenchimento piorava o texto e só cabiam dois
    estados de cor. Agora escurecer melhora o rótulo, então o hover escurece nos dois temas e o
    pressed passa a existir como cor de verdade.</p>
    <p><b>O tema escuro tem um teto que o claro não tem.</b> No claro dá para escurecer até
    <code>orange-700</code> ({cr(O['700'], '#FFFFFF'):.2f}:1) sem penalidade. No escuro o
    preenchimento também precisa se separar da tela, então o hover para em
    <code>orange-550</code> — o degrau que existe exatamente para esse ponto.</p>
    <p><b>Onde AA pleno for obrigatório</b> — texto legal, fluxo crítico, contexto regulado — use
    <code>bg-brand-strong</code> (<code>orange-700</code>, {cr(O['700'], '#FFFFFF'):.2f}:1 com texto
    branco). Ele existe exatamente para isso e passa em AA pleno no repouso.</p>
  </div>
</section>

<section>
  <h2>O portão de contraste <span class="count">{N_PAIRS} pares · {N_AA} em AA · {N_EXC} exceções · 0 reprovas</span></h2>
  <p>Todo par que o sistema permite que se encontre na tela, medido. Texto em 4,5:1, elemento
  não-textual em 3:1. Estes {N_PAIRS} pares rodam como teste a cada alteração de cor — se um cair,
  o build quebra. As três exceções são de marca, estão nomeadas e nenhuma fica abaixo de 3:1.</p>
  <div style="margin-top:22px">{contrast_tables()}</div>
</section>'''

# ───────────────────────────────────────────────────────── Fundação · tipografia
TAB_TIPO_ESCALA = f'''
<section>
  <h2>Espécimes <span class="count">{len(T['type']['styles'])} estilos</span></h2>
  <p>Inter variável para texto, JetBrains Mono para código. Quatro pesos. Cada estilo abaixo é uma
  combinação fechada de tamanho, entrelinha, peso e tracking — o produto escolhe o estilo, não os
  quatro valores separados.</p>
  <div style="margin-top:10px">{type_specimens()}</div>
</section>'''

TAB_TIPO_TOKENS = f'''
<section>
  <h2>Tamanho, entrelinha e tracking</h2>
  <p>Os tamanhos não seguem múltiplos de 8 — isso daria 8/16/24/32 e não deixaria nada entre corpo
  e H3. Quem cai na malha é a entrelinha: todas são múltiplos de 4, e o corpo (16/24) é múltiplo de
  8. O tracking negativo cresce com o tamanho porque a Inter é espacejada para texto pequeno e fica
  frouxa acima de 24px.</p>
  <div class="scroller" style="margin-top:18px"><table>
    <thead><tr><th>Token de tamanho</th><th class="num">Valor</th><th>Token de entrelinha</th>
      <th class="num">Valor</th><th class="num">Tracking</th></tr></thead>
    <tbody>{type_token_rows()}</tbody>
  </table></div>
</section>

<section>
  <h2>Pesos</h2>
  <div class="scroller"><table>
    <thead><tr><th>Token</th><th class="num">Valor</th><th>Amostra</th></tr></thead>
    <tbody>{weight_rows()}</tbody>
  </table></div>
  <div class="note" style="margin-top:18px">
    <b>Peso não é ênfase de conteúdo</b>
    <p>O <code>semibold</code> marca hierarquia estrutural — título, rótulo de campo. Para ênfase
    dentro de um parágrafo, o elemento é <code>&lt;strong&gt;</code>, que carrega significado para
    o leitor de tela. Peso sozinho não é anunciado.</p>
  </div>
</section>'''

# ────────────────────────────────────────────────────────── Fundação · medidas
TAB_ESPACO = f'''
<section>
  <h2>Espaçamento <span class="count">{len(T['space'])} degraus</span></h2>
  <p>Base 4 com ritmo de 8. Múltiplo de 8 puro quebra dentro do componente — gap de ícone, padding
  de chip e offset de foco vivem em 4px. O valor 2 é exceção documentada, só para ajuste óptico.</p>
  <div style="margin-top:20px">{space_bars()}</div>
  <div class="note" style="margin-top:22px">
    <b>Espaçamento é escolha de token, não de pixel</b>
    <p>Um valor fora da escala é o sintoma mais comum de sistema que começou a vazar. Se nenhum
    degrau serve, a pergunta é sobre o layout — não sobre acrescentar um degrau.</p>
  </div>
</section>'''

TAB_RADIUS = f'''
<section>
  <h2>Radius <span class="count">{len(T['radius'])} degraus</span></h2>
  <div style="margin-top:6px">{radius_grid()}</div>
  <div class="note" style="margin-top:22px">
    <b>Radius aninhado = externo − padding</b>
    <p>Card com radius 16 e padding 8 pede input com radius 8. Sem essa regra, canto aninhado
    sempre sai errado — o interno parece apertado demais ou frouxo demais em relação ao externo.</p>
  </div>
  <div class="note">
    <b>O <code>full</code> não é um número grande, é um comportamento</b>
    <p>9999px sempre resolve na pílula, independente da altura. É o que o Button usa, e é por isso
    que o botão continua uma pílula perfeita nos dois tamanhos sem token por tamanho.</p>
  </div>
</section>

<section>
  <h2>Borda</h2>
  <div class="scroller"><table>
    <thead><tr><th>Token</th><th class="num">Valor</th></tr></thead>
    <tbody>{border_rows()}</tbody>
  </table></div>
</section>'''

TAB_ELEVACAO = f'''
<section>
  <h2>Elevação <span class="count">6 degraus</span></h2>
  <p>Sombra de duas camadas — uma ambiente difusa e uma direcional curta. Camada única parece
  adesivo. Com o neutro acromático a sombra virou cinza puro
  (<code>rgba(24,24,24,α)</code>) — não há mais hue para tingir.</p>
  <div style="margin-top:22px">{elevation_grid()}</div>
  <div class="note" style="margin-top:24px">
    <b>No tema escuro a sombra não é o sinal principal</b>
    <p><code>rgba(0,0,0,.12)</code> sobre <code>#181818</code> é invisível. Quem comunica altura é a
    superfície clareando: <code>950 → 900 → 800</code>. A sombra continua existindo, mais opaca, só
    como reforço. Os quadrados acima já mostram isso: mude o tema do seu sistema e eles trocam de
    estratégia sozinhos.</p>
  </div>
</section>'''

TAB_FOCO = f'''
<section>
  <h2>O anel de foco</h2>
  <p>Duas camadas: 2px de respiro pintado na cor do fundo, e 2px na cor do foco. O respiro não é
  estética — sem ele o anel laranja encostaria no preenchimento laranja do botão e daria 1,00:1.</p>
  <div class="dd" style="margin-top:20px">
    <div class="cell"><span class="lab" style="color:var(--al-text-secondary)">Anel padrão</span>
      <div class="stage2">
        <button type="button" class="al-btn al-btn--primary al-btn--md is-focus" tabindex="-1"><span class="al-btn__label">Publicar</span></button>
        <button type="button" class="al-btn al-btn--secondary al-btn--md is-focus" tabindex="-1"><span class="al-btn__label">Cancelar</span></button>
      </div>
      <p class="cap">Aparece no <code>:focus-visible</code> — teclado sim, clique de mouse não.</p>
    </div>
    <div class="cell"><span class="lab" style="color:var(--al-text-secondary)">Anel de erro</span>
      <div class="stage2">
        <button type="button" class="al-btn al-btn--danger al-btn--md is-focus" tabindex="-1"><span class="al-btn__label">Excluir</span></button>
      </div>
      <p class="cap">O destrutivo usa o anel de erro, para o foco não brigar com o vermelho do preenchimento.</p>
    </div>
  </div>
  <div class="scroller" style="margin-top:20px"><table>
    <thead><tr><th>Anel</th><th>Tema</th><th>Valor composto</th></tr></thead>
    <tbody>{focus_rows()}</tbody>
  </table></div>
</section>

<section>
  <h2>Onde a cor do anel mora</h2>
  <div class="note">
    <b>Na camada semântica de cor, não junto da elevação</b>
    <p>O anel é sombra em CSS, mas não é elevação: elevação comunica altura, o anel comunica foco
    de teclado. Guardá-lo junto da elevação o tiraria do portão de contraste — e foi justamente o
    portão que reprovou os valores <code>orange-300</code>/<code>red-300</code> testados antes, a
    1,61:1 no tema claro.</p>
    <p>No tema escuro o anel troca para <code>orange-400</code>, porque
    <code>orange-500</code> sobre a tela escura tem menos folga.</p>
  </div>
  <div class="note">
    <b>Alto contraste do sistema descarta sombra</b>
    <p>Em <code>forced-colors: active</code> o <code>box-shadow</code> some, e o anel sumiria junto.
    Todo componente do AL devolve o foco como <code>outline</code> nativo dentro desse modo — o
    Button já faz isso.</p>
  </div>
</section>'''

# ═══════════════════════════════════════════════════════════════ Button · abas
BTN_OVERVIEW = f'''
<section>
  <h2>Playground</h2>
  <div class="pg">
    <div class="stage" id="stage">
      <button type="button" class="al-btn al-btn--primary al-btn--md" id="demo">
        <span class="al-btn__spinner" aria-hidden="true"></span>
        <span class="al-btn__icon al-btn__icon--leading" hidden>{ICON_SVG}</span>
        <span class="al-btn__label">Publicar</span>
        <span class="al-btn__icon al-btn__icon--trailing" hidden>{ARROW_SVG}</span>
      </button>
    </div>

    <div class="controls">
      <div class="ctl"><span class="ctl-name">Variante</span>{seg('variant', VARIANTS, 'primary')}</div>
      <div class="ctl"><span class="ctl-name">Tamanho</span>{seg('size', SIZES, 'md')}</div>
      <div class="ctl"><span class="ctl-name">Estado</span>{seg('state', STATES, 'default')}</div>
      <div class="ctl"><span class="ctl-name">Ícone</span>{seg('icon', ICONS, 'none')}</div>
      <div class="ctl"><span class="ctl-name">Tema</span>{seg('theme', [('auto', 'Do sistema'), ('light', 'Claro'), ('dark', 'Escuro')], 'auto')}</div>
      <div class="ctl"><label for="labeltext">Rótulo</label>
        <input class="txt" id="labeltext" type="text" value="Publicar" maxlength="40"></div>
    </div>

    <div class="codewrap">
      <div class="codebar"><span>Marcação</span>
        <button type="button" class="copy" id="copy">Copiar</button></div>
      <pre><code id="code"></code></pre>
    </div>
  </div>
  <p style="margin-top:14px; font-size:13.5px; color:var(--al-text-secondary)">
    O botão acima é o componente real: esta página carrega o mesmo <code>button.css</code> que vai
    para produção. Hover, pressed e focus são forçados por classe, porque não dá para simular
    ponteiro — as declarações são as mesmas.
  </p>
</section>

<section>
  <h2>As quatro variantes</h2>
  <div class="dd">
    <div class="cell">
      <span class="lab" style="color:var(--al-text-secondary)">Ação principal e alternativa</span>
      <div class="stage2">
        <button type="button" class="al-btn al-btn--ghost al-btn--md" tabindex="-1"><span class="al-btn__label">Cancelar</span></button>
        <button type="button" class="al-btn al-btn--secondary al-btn--md" tabindex="-1"><span class="al-btn__label">Salvar rascunho</span></button>
        <button type="button" class="al-btn al-btn--primary al-btn--md" tabindex="-1"><span class="al-btn__label">Publicar</span></button>
      </div>
      <p class="cap">Um Primary só, e ele fecha o grupo. Ghost e Secondary abrem caminho sem competir.</p>
    </div>
    <div class="cell">
      <span class="lab" style="color:var(--al-text-secondary)">Ação destrutiva</span>
      <div class="stage2">
        <button type="button" class="al-btn al-btn--secondary al-btn--md" tabindex="-1"><span class="al-btn__label">Manter conta</span></button>
        <button type="button" class="al-btn al-btn--danger al-btn--md" tabindex="-1"><span class="al-btn__label">Excluir conta</span></button>
      </div>
      <p class="cap">Danger só quando a ação destrói e é difícil de desfazer. Nunca para algo reversível.</p>
    </div>
  </div>
</section>'''

BTN_SPECS = f'''
<section>
  <h2>Anatomia</h2>
  <div class="anat">
    <div><b>Contêiner</b><span>Pílula. Raio total, borda de 1px sempre presente — transparente quando a variante não tem borda.</span></div>
    <div><b>Spinner</b><span>16px, ocupa o lugar do ícone da esquerda quando <code>aria-busy</code> está ligado.</span></div>
    <div><b>Ícone à esquerda</b><span>16px. Reforça a ação. Opcional, sempre <code>aria-hidden</code>.</span></div>
    <div><b>Rótulo</b><span>Obrigatório. É também o nome acessível do botão.</span></div>
    <div><b>Ícone à direita</b><span>16px. Indica movimento ou que algo abre.</span></div>
  </div>
</section>

<section>
  <h2>Todos os estados</h2>
  {specimen_grid()}
</section>

<section>
  <h2>Medidas</h2>
  <div class="scroller">
    <table>
      <thead><tr><th>Tamanho</th><th>Token</th><th>Aponta para</th><th>Valor</th></tr></thead>
      <tbody>{geo_rows()}</tbody>
    </table>
  </div>
  <div class="note" style="margin-top:16px">
    <b>Não existe token de altura</b>
    Altura é consequência: <code>padding-y</code> × 2 mais a entrelinha. Dá
    {BTN['derived']['height']['sm']}px no <code>sm</code> e {BTN['derived']['height']['md']}px no
    <code>md</code> — conferido no navegador contra o Figma. Um token de altura fixaria a mesma
    decisão em dois lugares.
  </div>
</section>

<section>
  <h2>Tokens de cor</h2>
  <div class="ctl" style="margin-bottom:14px"><span class="ctl-name">Filtrar</span>
    {seg('tokfilter', [('all', 'Todas')] + VARIANTS, 'all')}</div>
  <div class="scroller">
    <table>
      <thead><tr><th>Token do Button</th><th>Aponta para</th><th>Resolve em (claro)</th></tr></thead>
      <tbody id="tokbody">{token_rows()}</tbody>
    </table>
  </div>
</section>'''

BTN_GUIDE = '''
<section>
  <h2>Hierarquia</h2>
  <div class="dd">
    <div class="cell do"><span class="lab">Faça</span>
      <div class="stage2">
        <button type="button" class="al-btn al-btn--ghost al-btn--md" tabindex="-1"><span class="al-btn__label">Cancelar</span></button>
        <button type="button" class="al-btn al-btn--primary al-btn--md" tabindex="-1"><span class="al-btn__label">Publicar</span></button>
      </div>
      <p class="cap">Uma ação principal, <b>no fim do grupo</b>.</p>
    </div>
    <div class="cell no"><span class="lab">Não faça</span>
      <div class="stage2">
        <button type="button" class="al-btn al-btn--primary al-btn--md" tabindex="-1"><span class="al-btn__label">Publicar</span></button>
        <button type="button" class="al-btn al-btn--primary al-btn--md" tabindex="-1"><span class="al-btn__label">Salvar</span></button>
      </div>
      <p class="cap">Dois Primary se anulam. Se as duas são principais, nenhuma é.</p>
    </div>
  </div>
  <div class="rule"><div class="rn">01</div><div>
    <h3>Um Primary por tela</h3>
    <p>É a regra mais unânime que existe em documentação de botão — Carbon, Primer e Red Hat dizem o mesmo. Precisa de duas ações de mesmo peso? As duas viram Secondary.</p>
  </div></div>
  <div class="rule"><div class="rn">02</div><div>
    <h3>O Primary fecha o grupo</h3>
    <p>Em linha, da menor para a maior ênfase. Em coluna — comum no mobile — o Primary vai no topo, porque ali a leitura desce.</p>
  </div></div>
  <div class="rule"><div class="rn">03</div><div>
    <h3>Danger longe da saída</h3>
    <p>Separe o destrutivo do resto. Clique errado em "Excluir" custa caro, e distância é a proteção mais barata.</p>
  </div></div>
</section>

<section>
  <h2>O rótulo</h2>
  <div class="dd">
    <div class="cell do"><span class="lab">Faça</span>
      <div class="stage2">
        <button type="button" class="al-btn al-btn--primary al-btn--md" tabindex="-1"><span class="al-btn__label">Criar projeto</span></button>
      </div>
      <p class="cap">Verbo na frente e o substantivo que diz sobre o quê.</p>
    </div>
    <div class="cell no"><span class="lab">Não faça</span>
      <div class="stage2">
        <button type="button" class="al-btn al-btn--primary al-btn--md" tabindex="-1"><span class="al-btn__label">OK</span></button>
        <button type="button" class="al-btn al-btn--secondary al-btn--md" tabindex="-1"><span class="al-btn__label">CLIQUE AQUI</span></button>
      </div>
      <p class="cap">"OK" não diz o que confirma. Caixa alta derruba a velocidade de leitura.</p>
    </div>
  </div>
  <div class="rule"><div class="rn">04</div><div>
    <h3>Capitalização de frase, nunca caixa alta</h3>
    <p>"Salvar alterações", não "Salvar Alterações" nem "SALVAR ALTERAÇÕES". É o padrão do Material 3 para todo rótulo, e o Primer proíbe caixa alta explicitamente.</p>
  </div></div>
  <div class="rule"><div class="rn">05</div><div>
    <h3>Curto, e nunca em duas linhas</h3>
    <p>Uma a três palavras. A pílula de raio total se destrói com rótulo em duas linhas — se não couber, o problema é o texto.</p>
  </div></div>
</section>

<section>
  <h2>Fora de escopo, de propósito</h2>
  <div class="scroller">
    <table>
      <thead><tr><th>O quê</th><th>Situação</th><th>Se aparecer demanda</th></tr></thead>
      <tbody>
        <tr><td class="name">Largura total</td><td>Não existe</td><td>Vira propriedade, não variante.</td></tr>
        <tr><td class="name">Danger contornado</td><td>Não existe</td><td>Secondary com rótulo explícito de consequência.</td></tr>
        <tr><td class="name">Tamanho lg</td><td>Não existe</td><td>Fechado em dois tamanhos.</td></tr>
        <tr><td class="name">Só ícone</td><td>Set irmão</td><td><code>Icon Button</code>, com nome acessível obrigatório.</td></tr>
      </tbody>
    </table>
  </div>
</section>'''

BTN_A11Y = '''
<section>
  <h2>Foco</h2>
  <p>O anel tem duas camadas: 2px de respiro na cor do fundo e 2px na cor do foco. O respiro é o que impede o anel de encostar no preenchimento — sem ele, laranja sobre laranja daria 1,00:1.</p>
  <div class="dd" style="margin-top:16px">
    <div class="cell"><span class="lab" style="color:var(--al-text-secondary)">Anel padrão · 3,34:1 no claro, 8,08:1 no escuro</span>
      <div class="stage2">
        <button type="button" class="al-btn al-btn--primary al-btn--md is-focus" tabindex="-1"><span class="al-btn__label">Publicar</span></button>
        <button type="button" class="al-btn al-btn--secondary al-btn--md is-focus" tabindex="-1"><span class="al-btn__label">Cancelar</span></button>
      </div>
      <p class="cap">Aparece no <code>:focus-visible</code> — teclado sim, clique de mouse não.</p>
    </div>
    <div class="cell"><span class="lab" style="color:var(--al-text-secondary)">Anel de erro · 8,12:1 no claro</span>
      <div class="stage2">
        <button type="button" class="al-btn al-btn--danger al-btn--md is-focus" tabindex="-1"><span class="al-btn__label">Excluir</span></button>
      </div>
      <p class="cap">Danger usa o anel de erro, para o foco não brigar com o vermelho do preenchimento.</p>
    </div>
  </div>
  <div class="note" style="margin-top:16px">
    <b>O anel do Ghost só aparece em código</b>
    No Figma o estado <code>Focus</code> do Ghost não mostra o anel: sombra projetada precisa de forma pintada, e o Ghost não tem preenchimento nem borda. Em CSS o <code>box-shadow</code> é lançado pela caixa, então o Ghost recebe exatamente o mesmo anel — como dá para ver ligando Ghost + Focus no playground.
  </div>
</section>

<section>
  <h2>Estados que enganam</h2>
  <div class="rule"><div class="rn">06</div><div>
    <h3>Carregando: <code>aria-busy</code>, não <code>disabled</code></h3>
    <p>Marque <code>aria-busy="true"</code> e <code>aria-disabled="true"</code>, e trave o handler no JS. O atributo <code>disabled</code> tiraria o botão da ordem de foco no meio da interação, sem anunciar nada. Anuncie o progresso por região viva (<code>role="status"</code>, <code>aria-live="polite"</code>) e segure o estado por um piso de ~400ms.</p>
  </div></div>
  <div class="rule"><div class="rn">07</div><div>
    <h3>Desabilitado é exceção</h3>
    <p>Um botão desabilitado não explica por que está desabilitado. Em formulário, deixe habilitado e mostre o erro ao tentar enviar. Quando for mesmo necessário, use <code>aria-disabled</code>: continua focável e um tooltip pode dizer o motivo.</p>
  </div></div>
  <div class="rule"><div class="rn">08</div><div>
    <h3>O contraste baixo do desabilitado é intencional</h3>
    <p>1,59:1 no tema claro. O WCAG isenta componentes inativos do critério 1.4.3 — não é reprova, é sinal. Subir esse contraste faz o desabilitado parecer clicável.</p>
  </div></div>
  <div class="rule"><div class="rn">09</div><div>
    <h3>Alvo de toque</h3>
    <p>Os dois tamanhos passam o mínimo do WCAG 2.5.8 (24×24px). Só o <code>md</code>, com 48px, alcança o que Apple e Google recomendam para toque — por isso ele é o padrão e o <code>sm</code> precisa de justificativa de densidade.</p>
  </div></div>
  <div class="rule"><div class="rn">10</div><div>
    <h3>Alto contraste do sistema</h3>
    <p>O modo de alto contraste descarta <code>box-shadow</code> — o anel sumiria junto. O componente devolve o foco como <code>outline</code> nativo dentro de <code>@media (forced-colors: active)</code>.</p>
  </div></div>
</section>

<section>
  <h2>Marcação mínima</h2>
  <pre><code>&lt;button type="button" class="al-btn al-btn--primary al-btn--md"&gt;
  &lt;span class="al-btn__label"&gt;Publicar&lt;/span&gt;
&lt;/button&gt;</code></pre>
  <p style="margin-top:14px"><code>type="button"</code> não é opcional: dentro de <code>&lt;form&gt;</code>, o padrão do HTML é <code>submit</code>. E o rótulo visível é o nome acessível — não coloque um <code>aria-label</code> dizendo outra coisa, ou o comando de voz para de funcionar.</p>
</section>'''


# ═══════════════════════════════════════════════════════════════ Icon · abas
ICON_BOXES = [('16', '16'), ('20', '20'), ('24', '24'), ('32', '32'), ('free', 'Livre')]
ICON_INKS = [('inherit', 'Herda'), ('default', 'default'), ('on-brand', 'on-brand'),
             ('on-solid', 'on-solid'), ('disabled', 'disabled')]


def icon_options():
    """O select do playground, agrupado igual ao component set do Figma."""
    out = []
    for title, names in ICON_GROUPS:
        out.append(f'<optgroup label="{title}">')
        for n in names:
            on = ' selected' if n == 'settings' else ''
            out.append(f'<option value="{n}"{on}>{n}</option>')
        out.append('</optgroup>')
    return '\n'.join(out)


def icon_library():
    """Os 70, lidos do repositorio. O playground clona daqui - nao ha segunda copia."""
    out = []
    for title, names in ICON_GROUPS:
        cells = '\n'.join(
            f'<button type="button" class="icon-tile" data-name="{n}">'
            f'{al_icon(n)}<span>{n}</span></button>' for n in names)
        out.append(f'<h3 class="sub">{title}<span class="count">{len(names)}</span></h3>'
                   f'<div class="icon-grid">{cells}</div>')
    return '\n'.join(out)


def icon_token_rows():
    rows = []
    for name in sorted(ICON_TOK['alias']):
        ref = ICON_TOK['alias'][name]
        res = ICON_TOK['resolved'].get(name)
        if isinstance(res, dict):
            val = f'{res["light"]} / {res["dark"]}'
            chip = (f'<span class="chip sm" style="background:{res["light"]}"></span>'
                    f'<span class="chip sm" style="background:{res["dark"]}"></span>')
        else:
            val = f'{res}px'
            chip = ''
        rows.append(f'<tr><td class="tok">--al-{name}</td><td class="tok dim">{ref}</td>'
                    f'<td class="tok dim">{chip}{val}</td></tr>')
    return '\n'.join(rows)


ICON_OVERVIEW = f'''
<section>
  <h2>Playground</h2>
  <div class="pg">
    <div class="stage" id="icon-stage">
      <span id="icon-slot">{al_icon('settings')}</span>
    </div>

    <div class="controls">
      <div class="ctl"><label for="icon-name">Ícone</label>
        <select class="txt" id="icon-name">{icon_options()}</select></div>
      <div class="ctl"><span class="ctl-name">Caixa</span>{seg('iconbox', ICON_BOXES, '24')}</div>
      <div class="ctl"><label for="icon-free">Livre</label>
        <input class="txt" id="icon-free" type="number" min="8" max="160" step="1" value="40"
               style="max-width:120px" disabled></div>
      <div class="ctl"><span class="ctl-name">Tinta</span>{seg('iconink', ICON_INKS, 'inherit')}</div>
      <div class="ctl"><span class="ctl-name">Tema</span>{seg('icontheme', [('auto', 'Do sistema'), ('light', 'Claro'), ('dark', 'Escuro')], 'auto')}</div>
    </div>

    <div class="codewrap">
      <div class="codebar"><span>Marcação</span>
        <button type="button" class="copy" id="icon-copy">Copiar</button></div>
      <pre><code id="icon-code"></code></pre>
    </div>
  </div>
  <p style="margin-top:14px; font-size:13.5px; color:var(--al-text-secondary)">
    Escolha <b>Livre</b> na caixa e digite qualquer número: 40, 96, 17. Nada quebra, e o traço
    engrossa junto — é a diferença entre escala fixa e escala nomeada. As tintas
    <code>on-brand</code> e <code>on-solid</code> trocam o fundo do palco, porque elas só existem
    sobre preenchimento.
  </p>
</section>

<section>
  <h2>Dentro de um acionável</h2>
  <p>O caso que importa, e o motivo de o padrão ser <code>currentColor</code>: nenhum ícone abaixo
  declara cor. Eles herdam a do rótulo, e é por isso que acertam os quatro estados do Button sem
  uma linha a mais. No Figma isso precisa da collection <code>3. Icon ink</code> com quatro modes,
  porque o Figma não tem essa palavra-chave.</p>
  <div class="pb-row" style="margin-top:18px">
    <button type="button" class="al-btn al-btn--primary al-btn--md">
      <span class="al-btn__icon al-btn__icon--leading">{al_icon('check')}</span>
      <span class="al-btn__label">Salvar</span></button>
    <button type="button" class="al-btn al-btn--secondary al-btn--md">
      <span class="al-btn__icon al-btn__icon--leading">{al_icon('download')}</span>
      <span class="al-btn__label">Exportar</span></button>
    <button type="button" class="al-btn al-btn--ghost al-btn--md">
      <span class="al-btn__icon al-btn__icon--leading">{al_icon('filter')}</span>
      <span class="al-btn__label">Filtrar</span></button>
    <button type="button" class="al-btn al-btn--danger al-btn--md">
      <span class="al-btn__icon al-btn__icon--leading">{al_icon('trash')}</span>
      <span class="al-btn__label">Excluir</span></button>
    <button type="button" class="al-btn al-btn--primary al-btn--md" aria-disabled="true">
      <span class="al-btn__icon al-btn__icon--leading">{al_icon('lock')}</span>
      <span class="al-btn__label">Indisponível</span></button>
  </div>
</section>

<section>
  <h2>A biblioteca · {N_ICONS} ícones</h2>
  <p>Desenho Lucide, grid de 24, traço de 2, cantos e junções redondos. O portão
  <code>icons.py</code> recusa qualquer arquivo que fuja disso — o risco desta pasta não é um valor
  errado, é um ícone de outra família entrando sem ninguém ver. Clique para copiar o nome.</p>
  <div style="margin-top:24px">{icon_library()}</div>
</section>'''

def icon_a11y_rows(group):
    out = []
    for r in ICON_A11Y['rows']:
        if r['group'] != group:
            continue
        if r['exempt']:
            verdict = '<span class="exc">isento</span>'
        else:
            verdict = '<span class="pass">passa</span>'
        out.append(
            f'<tr><td class="tok dim">{r["theme"]}</td><td class="name">{r["label"]}</td>'
            f'<td class="chipcell"><span class="chip sm" style="background:{r["fg"]}"></span>'
            f'<span class="chip sm" style="background:{r["bg"]}"></span></td>'
            f'<td class="tok dim">{r["fg"]} / {r["bg"]}</td>'
            f'<td class="num strong">{r["ratio"]:.2f}:1</td><td>{verdict}</td></tr>')
    return '\n'.join(out)


ICON_A11Y_TAB = f'''
<section>
  <h2>O critério é outro</h2>
  <p>Ícone não é texto. O piso dele é o <b>3:1</b> do WCAG 1.4.11 — contraste não-textual — e não
  o 4,5:1 que vale para rótulo. É a mesma cor medida contra um mínimo diferente, e isso tem uma
  consequência prática que aparece logo abaixo: branco sobre a marca <b>reprova</b> como texto
  normal e <b>passa</b> como ícone. Não é uma exceção aberta aqui; é aprovação com folga.</p>
  <div class="stats">
    <div class="stat hl"><b>{len([r for r in ICON_A11Y['rows'] if not r['exempt']]) + ICON_A11Y['markupChecked']}</b><span>verificações</span></div>
    <div class="stat"><b>{ICON_A11Y['fails']}</b><span>reprovas</span></div>
    <div class="stat"><b>{ICON_A11Y['markupChecked']}</b><span>elementos com contrato conferido</span></div>
    <div class="stat"><b>{ICON_A11Y['floor']}:1</b><span>piso não-textual</span></div>
  </div>
</section>

<section>
  <h2>Tinta explícita contra a superfície</h2>
  <p>Cada tinta é medida só onde ela faz sentido: <code>on-brand</code> contra a tela seria um
  cenário que o design system não produz. O <code>disabled</code> aparece medido e isento — o WCAG
  dispensa componente inativo, e subir esse contraste faria o desabilitado parecer clicável.</p>
  <div class="scroller" style="margin-top:20px"><table>
    <thead><tr><th>Tema</th><th>Combinação</th><th></th><th>Tinta / fundo</th><th>Razão</th><th></th></tr></thead>
    <tbody>{icon_a11y_rows('tinta')}</tbody>
  </table></div>
</section>

<section>
  <h2>Tinta herdada dentro do Button</h2>
  <p>O padrão do componente é <code>currentColor</code>, então dentro de um acionável o ícone veste
  a cor do rótulo. Vale aqui a mesma lógica que o Button já usa: variante sem preenchimento herda a
  tela, então Ghost e Secondary são medidos contra a <b>tela</b>, nunca contra "transparente".</p>
  <div class="scroller" style="margin-top:20px"><table>
    <thead><tr><th>Tema</th><th>Variante · estado</th><th></th><th>Tinta / fundo</th><th>Razão</th><th></th></tr></thead>
    <tbody>{icon_a11y_rows('herda')}</tbody>
  </table></div>
</section>

<section>
  <h2>Contrato de marcação, medido</h2>
  <p>A regra de ícone decorativo versus ícone com sentido não virou documento — virou portão.
  O <code>a11y.py</code> lê o HTML que este site emite e cobra o contrato de cada
  <code>.al-icon</code>: {ICON_A11Y['markupChecked']} elementos nesta página, nenhum fora.
  Ele reprova três coisas: ícone sem contrato nenhum, <code>role="img"</code> sem
  <code>aria-label</code>, e <code>aria-hidden</code> junto de um rótulo — que é contradição,
  porque o rótulo nunca seria lido.</p>
  <div class="note" style="margin-top:20px">
    <b>Por que medir no HTML e não na folha de estilo</b>
    <p>Contraste se prova no token; marcação, não. Um contrato de <code>aria-*</code> só existe
    quando alguém escreve o atributo — então o único lugar onde ele pode ser verificado é a saída
    renderizada. Regra escrita numa página envelhece; regra medida quebra o build.</p>
  </div>
</section>'''


ICON_SPECS = f'''
<section>
  <h2>Sem escala fixa</h2>
  <p>O desenho é vetorizado no grid de 24, então a mesma marcação vale em qualquer tamanho e o
  traço escala junto. Os quatro degraus abaixo são os recorrentes, não um teto.</p>
  <div class="scroller" style="margin-top:20px"><table>
    <thead><tr><th>Como escrever</th><th>Caixa</th><th>Onde costuma aparecer</th></tr></thead>
    <tbody>
      <tr><td class="tok">.al-icon--16</td><td class="num">16px</td><td>rótulo auxiliar, texto de 12</td></tr>
      <tr><td class="tok">.al-icon--20</td><td class="num">20px</td><td>Button <code>sm</code>, Icon Button, item de navegação</td></tr>
      <tr><td class="tok">.al-icon (padrão)</td><td class="num">24px</td><td>Button <code>md</code>, ícone solto, ação de cabeçalho</td></tr>
      <tr><td class="tok">.al-icon--32</td><td class="num">32px</td><td>estado vazio, destaque</td></tr>
      <tr><td class="tok">style="--al-icon-box: 40px"</td><td class="num dim">qualquer</td><td>fora da escala, sem classe nova</td></tr>
    </tbody>
  </table></div>
  <div class="note" style="margin-top:20px">
    <b>Por que a caixa se chama <code>box</code> e não <code>size</code></b>
    <p><code>--al-icon-size-16</code> já existe e é a primitiva da Foundation. Se o token do
    componente tivesse o mesmo nome, ele apontaria para si mesmo e a custom property morreria em
    ciclo. <code>box</code> é o papel dentro do componente; <code>size</code> é o degrau na escala.</p>
  </div>
</section>

<section>
  <h2>Os {len(ICON_TOK['alias'])} tokens</h2>
  <p>Todos alias, nenhum valor próprio. As quatro tintas espelham uma a uma as modes da collection
  <code>3. Icon ink</code> do Figma — mas o padrão do componente não é nenhuma delas, é
  <code>currentColor</code>. Elas são a saída explícita, para ícone que não tenha de quem herdar.</p>
  <div class="scroller" style="margin-top:20px"><table>
    <thead><tr><th>Token</th><th>Aponta para</th><th>Resolve em claro / escuro</th></tr></thead>
    <tbody>{icon_token_rows()}</tbody>
  </table></div>
</section>

<section>
  <h2>Contrato de marcação</h2>
  <p>Ícone do AL vive dentro de acionável, e nesse lugar ele é quase sempre decorativo: quem carrega
  o sentido é o rótulo. Ícone decorativo anunciado por leitor de tela vira ruído duplicado.</p>
  <h3 class="sub">Decorativo — o caso padrão</h3>
  <pre><code>&lt;svg class="al-icon al-icon--16" aria-hidden="true" focusable="false"&gt;…&lt;/svg&gt;</code></pre>
  <p style="margin-top:12px">Os dois atributos fazem coisas diferentes:
  <code>aria-hidden</code> tira do leitor de tela, <code>focusable="false"</code> tira da ordem de
  tabulação — SVG inline entra nela sozinho em alguns navegadores.</p>
  <h3 class="sub">Quando o ícone carrega o sentido</h3>
  <pre><code>&lt;svg class="al-icon" role="img" aria-label="Erro de validação"&gt;…&lt;/svg&gt;</code></pre>
  <p style="margin-top:12px">Botão só de ícone é o caso limite e não é este: ali o nome acessível
  vai no <code>&lt;button&gt;</code>, nunca no <code>svg</code>. Quem resolve isso é o Icon Button.</p>
</section>

<section>
  <h2>Arquivos e portões</h2>
  <div class="scroller"><table>
    <thead><tr><th>Arquivo</th><th>O que faz</th><th>Resultado</th></tr></thead>
    <tbody>
      <tr><td class="tok">icons/*.svg</td><td>{N_ICONS} desenhos · Lucide · ISC</td><td><span class="pass">70/70</span></td></tr>
      <tr><td class="tok">icon.css</td><td>o componente: caixa e tinta, escrito à mão</td><td><span class="pass">0 literais</span></td></tr>
      <tr><td class="tok">tokens.py</td><td>portão de alias · gera al-icon-tokens.css</td><td><span class="pass">0 valores soltos</span></td></tr>
      <tr><td class="tok">check.py</td><td>portão de CSS literal</td><td><span class="pass">0 pendências</span></td></tr>
      <tr><td class="tok">icons.py</td><td>portão de desenho · recusa ícone fora da família</td><td><span class="pass">70/70</span></td></tr>
      <tr><td class="tok">NOTICE</td><td>ISC do Lucide — o resto do AL segue {META['license']}</td><td></td></tr>
    </tbody>
  </table></div>
  <div class="note" style="margin-top:20px">
    <b>O <code>stroke-width</code> não está no CSS, e isso é intencional</b>
    <p>A espessura do traço — 2 no grid de 24 — é parte do desenho e viaja dentro do próprio
    arquivo <code>.svg</code>. Cor e caixa mudam com o contexto e com o tema; o desenho, não.</p>
  </div>
</section>'''


# ═══════════════════════════════════════════════════════════════════ páginas
LANDING_FUNDACAO = f'''
<section>
  <h2>Os seis assuntos da Fundação</h2>
  <div class="cards">
    {card('principios', 'Princípios', 'As cinco decisões que travam o resto, o pipeline de oito etapas e os quatro portões de build.', TH_PRINCIPIOS)}
    {card('prova', 'A prova', 'Os mesmos tokens montados nos dois temas, lado a lado: botões, campos, foco e avisos.', TH_PROVA)}
    {card('cor', 'Cor', f'{N_PRIM} primitivas em OKLCH, {N_SEM} semânticos com dois temas e os {N_PAIRS} pares medidos do portão de contraste.', TH_COR)}
    {card('tipografia', 'Tipografia', f'Inter e JetBrains Mono em {len(T["type"]["styles"])} estilos fechados de tamanho, entrelinha, peso e tracking.', TH_TIPO)}
    {card('espacamento', 'Espaçamento e medidas', f'Base 4 com ritmo de 8, {len(T["radius"])} raios, 6 elevações e o anel de foco de duas camadas.', TH_ESPACO)}
    {card('icon', 'Ícones', f'{N_ICONS} ícones no grid de 24, sem escala fixa: o mesmo componente serve de 16 a 96 e o traço acompanha.', TH_ICON)}
  </div>
</section>'''

# ═════════════════════════════════════════════════════════ ICON BUTTON · abas
# Reaproveita VARIANTS e STATES do Button de propósito: o recorte é o mesmo, e
# duplicar as listas seria abrir espaço para elas divergirem sem ninguém ver.
IB_SIZES = [('sm', 'sm · 36px'), ('md', 'md · 48px')]
IB_ICON_CHOICES = [('search', 'Buscar'), ('x', 'Fechar'),
                   ('trash', 'Excluir'), ('ellipsis-vertical', 'Mais opções')]
IB_ROLES = ['bg', 'bg-hover', 'bg-active', 'bg-disabled', 'ink',
            'ink-disabled', 'border', 'border-disabled', 'ring']


def ib(variant, size, label, name, extra='', cls=''):
    """Um Icon Button real. O aria-label nunca é opcional - nem numa vitrine."""
    return (f'<button type="button" class="al-icon-btn al-icon-btn--{variant} '
            f'al-icon-btn--{size}{cls}" aria-label="{label}" tabindex="-1"{extra}>'
            f'<span class="al-icon-btn__spinner" aria-hidden="true"></span>'
            f'{al_icon(name)}</button>')


def ib_token_rows():
    rows = []
    for v, _ in VARIANTS:
        for role in IB_ROLES:
            name = f'icon-button-{v}-{role}'
            ref = IB['alias'][name]
            res = IB['resolved'][name]
            lt = res['light'] if isinstance(res, dict) else res
            sw = (f'<span class="chip sm" style="background:{lt}"></span>'
                  if isinstance(lt, str) and lt.startswith('#') else '')
            rows.append(f'<tr data-variant="{v}"><td class="tok">--al-{name}</td>'
                        f'<td class="tok dim">{"transparente" if ref == "transparent" else ref}</td>'
                        f'<td class="tok">{sw}{lt}</td></tr>')
    return '\n'.join(rows)


def ib_geo_rows():
    rows = []
    for s, _ in IB_SIZES:
        for role in ['padding', 'icon-size']:
            name = f'icon-button-{s}-{role}'
            rows.append(f'<tr><td class="name">{s}</td><td class="tok">--al-{name}</td>'
                        f'<td class="tok dim">{IB["alias"][name]}</td>'
                        f'<td class="num">{IB["resolved"][name]}</td></tr>')
    for role in ['radius', 'border-width']:
        name = f'icon-button-{role}'
        rows.append(f'<tr><td class="name">ambos</td><td class="tok">--al-{name}</td>'
                    f'<td class="tok dim">{IB["alias"][name]}</td>'
                    f'<td class="num">{IB["resolved"][name]}</td></tr>')
    return '\n'.join(rows)


def ib_specimen_grid():
    out = []
    for v, vlabel in VARIANTS:
        out.append(f'<div class="spec-row"><div class="spec-name">{vlabel}</div>'
                   f'<div class="spec-cells">')
        for state, slabel in STATES:
            cls, attrs = '', ''
            if state in ('hover', 'active', 'focus'):
                cls = f' is-{state}'
            elif state == 'disabled':
                attrs = ' aria-disabled="true"'
            elif state == 'busy':
                attrs = ' aria-busy="true" aria-disabled="true"'
            out.append(f'<div class="spec-cell"><span class="spec-label">{slabel}</span>'
                       + ib(v, 'md', f'{vlabel} {slabel}', 'search', attrs, cls) + '</div>')
        out.append('</div></div>')
    return '\n'.join(out)


def ib_a11y_rows(group):
    out = []
    for r in IB_A11Y['rows']:
        if r['group'] != group:
            continue
        verdict = ('<span class="exc">isento</span>' if r['exempt']
                   else '<span class="pass">passa</span>')
        chips = ''
        if str(r['fg']).startswith('#'):
            chips = (f'<span class="chip sm" style="background:{r["fg"]}"></span>'
                     f'<span class="chip sm" style="background:{r["bg"]}"></span>')
        out.append(
            f'<tr><td class="tok dim">{r["theme"]}</td><td class="name">{r["label"]}</td>'
            f'<td class="chipcell">{chips}</td>'
            f'<td class="tok dim">{r["fg"]} / {r["bg"]}</td>'
            f'<td class="num strong">{r["ratio"]:.2f}:1</td><td>{verdict}</td></tr>')
    return '\n'.join(out)


N_IB_MEDIDAS = len([r for r in IB_A11Y['rows'] if not r['exempt']])

IB_OVERVIEW = f'''
<section>
  <h2>Playground</h2>
  <div class="pg">
    <div class="stage" id="ib-stage">
      <button type="button" class="al-icon-btn al-icon-btn--primary al-icon-btn--md"
              id="ib-demo" aria-label="Buscar">
        <span class="al-icon-btn__spinner" aria-hidden="true"></span>
        {al_icon('search')}
      </button>
    </div>

    <div class="controls" id="ib-controls">
      <div class="ctl"><span class="ctl-name">Variante</span>{seg('ibvariant', VARIANTS, 'primary')}</div>
      <div class="ctl"><span class="ctl-name">Tamanho</span>{seg('ibsize', IB_SIZES, 'md')}</div>
      <div class="ctl"><span class="ctl-name">Estado</span>{seg('ibstate', STATES, 'default')}</div>
      <div class="ctl"><span class="ctl-name">Ícone</span>{seg('ibicon', IB_ICON_CHOICES, 'search')}</div>
      <div class="ctl"><span class="ctl-name">Tema</span>{seg('ibtheme', [('auto', 'Do sistema'), ('light', 'Claro'), ('dark', 'Escuro')], 'auto')}</div>
    </div>

    <div class="codewrap">
      <div class="codebar"><span>Marcação</span>
        <button type="button" class="copy" id="ib-copy">Copiar</button></div>
      <pre><code id="ib-code"></code></pre>
    </div>
  </div>
  <p style="margin-top:14px; font-size:13.5px; color:var(--al-text-secondary)">
    O botão acima é o componente real: esta página carrega o mesmo
    <code>icon-button.css</code> que vai para produção. Hover, pressed e focus são forçados por
    classe, porque não dá para simular ponteiro — as declarações são as mesmas. Repare que o
    <code>aria-label</code> acompanha o ícone escolhido: sem ele, o botão fica mudo.
  </p>
</section>

<section>
  <h2>O que muda em relação ao Button</h2>
  <div class="dd">
    <div class="cell">
      <span class="lab" style="color:var(--al-text-secondary)">Mesma barra, mesma altura</span>
      <div class="stage2">
        {ib('ghost', 'md', 'Editar', 'pencil')}
        {ib('ghost', 'md', 'Duplicar', 'copy')}
        {ib('ghost', 'md', 'Excluir', 'trash')}
        <button type="button" class="al-btn al-btn--primary al-btn--md" tabindex="-1"><span class="al-btn__label">Publicar</span></button>
      </div>
      <p class="cap">48px nos dois. É o que faz Icon Button e Button conviverem numa toolbar sem
      desalinhar — e a razão de o <code>md</code> usar ícone 24 com padding 12.</p>
    </div>
    <div class="cell">
      <span class="lab" style="color:var(--al-text-secondary)">O carregando não move nada</span>
      <div class="stage2">
        {ib('primary', 'md', 'Salvar', 'refresh-cw')}
        {ib('primary', 'md', 'Salvando', 'refresh-cw', ' aria-busy="true" aria-disabled="true"')}
      </div>
      <p class="cap">O spinner ocupa a caixa exata do ícone. No Button a largura pode pular e o
      rótulo muda junto; aqui não há rótulo para trocar.</p>
    </div>
  </div>
</section>

<section>
  <h2>As quatro variantes</h2>
  <div class="dd">
    <div class="cell">
      <span class="lab" style="color:var(--al-text-secondary)">Barra de ferramentas</span>
      <div class="stage2">
        {ib('ghost', 'md', 'Buscar', 'search')}
        {ib('ghost', 'md', 'Filtrar', 'filter')}
        {ib('ghost', 'md', 'Mais opções', 'ellipsis-vertical')}
      </div>
      <p class="cap">Ghost é o padrão em grupo denso: uma variante só para o grupo inteiro.</p>
    </div>
    <div class="cell">
      <span class="lab" style="color:var(--al-text-secondary)">Ação destrutiva em contexto</span>
      <div class="stage2">
        {ib('secondary', 'md', 'Editar linha', 'pencil')}
        {ib('danger', 'md', 'Excluir linha', 'trash')}
      </div>
      <p class="cap">Danger só quando a linha ou o card ao redor já diz <b>o quê</b> está sendo
      excluído — o ícone sozinho não identifica o alvo.</p>
    </div>
  </div>
</section>'''

IB_SPECS = f'''
<section>
  <h2>Anatomia</h2>
  <div class="anat">
    <div><b>Contêiner</b><span>Círculo. Raio total, borda de 1px sempre presente — transparente quando a variante não tem borda.</span></div>
    <div><b>Spinner</b><span>A mesma caixa do ícone, {IB['resolved']['icon-button-sm-icon-size']}px no <code>sm</code> e {IB['resolved']['icon-button-md-icon-size']}px no <code>md</code>. Entra com <code>aria-busy</code>.</span></div>
    <div><b>Ícone</b><span>Obrigatório e único. Sempre <code>aria-hidden</code>: quem carrega o sentido é o nome acessível.</span></div>
    <div><b>Nome acessível</b><span><code>aria-label</code> no botão. Não é opcional — é o contrato do componente.</span></div>
  </div>
  <div class="note" style="margin-top:16px">
    <b>Não há rótulo, e é isso que muda tudo</b>
    O Button tem cinco partes; este tem três. A que falta — o rótulo — é justamente a que
    carregava o sentido, o nome acessível e o piso de contraste de 4,5:1. Sem ela, esses três
    papéis se mudam de lugar: sentido vai para o ícone, nome vai para o <code>aria-label</code>,
    e o piso cai para 3:1 porque o portador deixou de ser texto.
  </div>
</section>

<section>
  <h2>Todos os estados</h2>
  {ib_specimen_grid()}
</section>

<section>
  <h2>Medidas</h2>
  <div class="scroller">
    <table>
      <thead><tr><th>Tamanho</th><th>Token</th><th>Aponta para</th><th>Valor</th></tr></thead>
      <tbody>{ib_geo_rows()}</tbody>
    </table>
  </div>
  <div class="note" style="margin-top:16px">
    <b>Não existe token de caixa</b>
    A caixa é consequência: <code>padding</code> × 2 mais o ícone. Dá
    {IB['derived']['box']['sm']}×{IB['derived']['box']['sm']}px no <code>sm</code> e
    {IB['derived']['box']['md']}×{IB['derived']['box']['md']}px no <code>md</code> — exatamente as
    alturas do Button. E é um padding só por tamanho, nos quatro lados: o botão é quadrado, então
    separar <code>padding-x</code> de <code>padding-y</code> fixaria a mesma decisão duas vezes.
  </div>
</section>

<section>
  <h2>Tokens de cor</h2>
  <div class="ctl" style="margin-bottom:14px"><span class="ctl-name">Filtrar</span>
    {seg('ibtokfilter', [('all', 'Todas')] + VARIANTS, 'all')}</div>
  <div class="scroller">
    <table>
      <thead><tr><th>Token do Icon Button</th><th>Aponta para</th><th>Resolve em (claro)</th></tr></thead>
      <tbody id="ibtokbody">{ib_token_rows()}</tbody>
    </table>
  </div>
  <div class="note" style="margin-top:16px">
    <b>{N_IB_TOKENS} tokens no código, 28 variáveis no Figma</b>
    A diferença não é esquecimento. As oito tintas vêm da collection <code>3. Icon ink</code>, que
    resolve por <b>modo</b> — um mecanismo que o CSS não tem, e por isso no código cada tinta
    precisa ser uma custom property concreta. Os quatro anéis são <i>effect styles</i>, porque
    sombra não pode ser variável no Figma. E os dois <code>icon-size</code> ligam direto à
    Fundação, como no Button.
  </div>
</section>'''

IB_GUIDE = f'''
<section>
  <h2>Quando usar</h2>
  <div class="dd">
    <div class="cell do"><span class="lab">Faça</span>
      <div class="stage2">
        {ib('ghost', 'md', 'Buscar', 'search')}
        {ib('ghost', 'md', 'Fechar', 'x')}
        {ib('ghost', 'md', 'Mais opções', 'ellipsis-vertical')}
      </div>
      <p class="cap">Buscar, fechar, mais opções — reconhecíveis <b>sem legenda</b>.</p>
    </div>
    <div class="cell no"><span class="lab">Não faça</span>
      <div class="stage2">
        {ib('ghost', 'md', 'Filtrar por status', 'filter')}
        {ib('ghost', 'md', 'Exportar relatório', 'share-2')}
        {ib('ghost', 'md', 'Arquivar conversa', 'bookmark')}
      </div>
      <p class="cap">Filtrar, exportar, arquivar: o desenho não resolve sozinho. Estes pedem Button
      com rótulo.</p>
    </div>
  </div>
  <div class="rule"><div class="rn">01</div><div>
    <h3>Só para ações universalmente reconhecíveis</h3>
    <p>Aqui o ícone é o único portador do sentido: se ele não for reconhecido, a ação não fica
    difícil — ela some. A NN/G é direta em dizer que ícones raramente substituem rótulos, e que o
    usuário só internaliza o desenho depois de uso repetido.</p>
  </div></div>
  <div class="rule"><div class="rn">02</div><div>
    <h3>Nunca na ação principal da tela</h3>
    <p>Ação primária pede Button com rótulo visível. O Polaris manda dar texto sempre que
    possível e tratar o rótulo acessível como recurso, não como padrão.</p>
  </div></div>
  <div class="rule"><div class="rn">03</div><div>
    <h3>Não use quando a ação depende do rótulo para identificar o alvo</h3>
    <p>“Excluir” só funciona quando a linha ou o card ao redor já diz <i>o quê</i>. Sem isso o
    <code>aria-label</code> teria que carregar o alvo inteiro — “Excluir pedido 4471” — e passa do
    tamanho que um tooltip comporta, na definição do Spectrum.</p>
  </div></div>
</section>

<section>
  <h2>Hierarquia</h2>
  <div class="dd">
    <div class="cell do"><span class="lab">Faça</span>
      <div class="stage2">
        {ib('ghost', 'sm', 'Editar', 'pencil')}
        {ib('ghost', 'sm', 'Duplicar', 'copy')}
        {ib('ghost', 'sm', 'Excluir', 'trash')}
      </div>
      <p class="cap">Uma variante para o grupo inteiro.</p>
    </div>
    <div class="cell no"><span class="lab">Não faça</span>
      <div class="stage2">
        {ib('primary', 'sm', 'Editar', 'pencil')}
        {ib('secondary', 'sm', 'Duplicar', 'copy')}
        {ib('danger', 'sm', 'Excluir', 'trash')}
      </div>
      <p class="cap">Três variantes sugerem uma hierarquia que não existe entre três ações irmãs.</p>
    </div>
  </div>
  <div class="rule"><div class="rn">04</div><div>
    <h3>Um grupo, uma variante</h3>
    <p>A diferença entre os botões vem da posição e do ícone, não da variante. É assim que o
    Primer monta seus grupos de icon button.</p>
  </div></div>
  <div class="rule"><div class="rn">05</div><div>
    <h3>No máximo um Primary por região</h3>
    <p>A conta é por região, não por componente: um Primary entre Icon Buttons e Buttons somados.</p>
  </div></div>
</section>

<section>
  <h2>O nome acessível</h2>
  <div class="dd">
    <div class="cell do"><span class="lab">Faça</span>
      <div class="stage2">{ib('secondary', 'md', 'Buscar', 'search')}</div>
      <p class="cap"><code>aria-label="Buscar"</code> — a <b>ação</b>.</p>
    </div>
    <div class="cell no"><span class="lab">Não faça</span>
      <div class="stage2">{ib('secondary', 'md', 'Lupa', 'search')}</div>
      <p class="cap"><code>aria-label="Lupa"</code> — o desenho. Quem ouve precisa saber o que vai
      acontecer, não o que está na tela.</p>
    </div>
  </div>
  <div class="rule"><div class="rn">06</div><div>
    <h3>O rótulo descreve a ação, nunca o ícone</h3>
    <p>“Buscar”, nunca “Lupa”. “Fechar”, nunca “X”. A formulação é literalmente a do Primer.</p>
  </div></div>
  <div class="rule"><div class="rn">07</div><div>
    <h3>Tooltip com o mesmo texto, quando existir</h3>
    <p>Idêntico, não parecido: divergência entre rótulo visível e programático quebra comando de
    voz — quem fala “clicar em Buscar” não ativa um botão rotulado de outro jeito. O Polaris é
    explícito nisso.</p>
  </div></div>
  <div class="rule"><div class="rn">08</div><div>
    <h3>Divergência consciente: o tooltip ainda não existe aqui</h3>
    <p>Primer sempre renderiza um, Polaris diz que deve ser fornecido, e o Spectrum define o
    tooltip justamente como o lugar de mostrar o rótulo de um botão só de ícone. Como o
    componente ainda não existe no AL, o <code>aria-label</code> vai sozinho: <b>ele atende o
    leitor de tela, mas não o usuário vidente que não reconhece o ícone</b>. É por isso que a
    regra 01 é restritiva — enquanto não há tooltip, o reconhecimento é a única rede.</p>
  </div></div>
</section>

<section>
  <h2>Fora de escopo, de propósito</h2>
  <div class="scroller">
    <table>
      <thead><tr><th>O quê</th><th>Situação</th><th>Se aparecer demanda</th></tr></thead>
      <tbody>
        <tr><td class="name">Tamanho lg</td><td>Não existe</td><td>Fechado em dois tamanhos, como o Button.</td></tr>
        <tr><td class="name">Danger contornado</td><td>Não existe</td><td>Mesma ausência deliberada do Button.</td></tr>
        <tr><td class="name">Selecionado / toggle</td><td>Não existe</td><td>Componente novo, não variante: precisa de <code>aria-pressed</code> e contrato de estado próprio. Primer e Spectrum tratam como separado.</td></tr>
        <tr><td class="name">Com rótulo visível</td><td>Set irmão</td><td><code>Button</code>, que já resolve ícone à esquerda e à direita.</td></tr>
      </tbody>
    </table>
  </div>
</section>'''

IB_A11Y = f'''
<section>
  <h2>O piso é 3:1, não 4,5:1</h2>
  <p>Esta é a única diferença conceitual entre o Icon Button e o Button, e ela explica quase tudo
  nesta aba. Lá o portador do sentido é um rótulo de <b>texto</b>: critério 1.4.3, piso 4,5:1.
  Aqui é um <b>ícone</b>, conteúdo não-textual: critério 1.4.11, piso 3:1.</p>
  <p style="margin-top:12px">A consequência é concreta. Branco sobre a marca dá 3,34:1 — no Button
  isso é uma <b>exceção de marca nomeada</b>; aqui é <b>aprovação</b>. Por isso este componente
  tem zero exceções de marca, e o laranja do Primary ficou como está.</p>
  <div class="stats">
    <div class="stat hl"><b>{N_IB_MEDIDAS}</b><span>combinações medidas</span></div>
    <div class="stat"><b>{IB_A11Y['fails']}</b><span>reprovas</span></div>
    <div class="stat"><b>0</b><span>exceções de marca</span></div>
    <div class="stat"><b>{IB_A11Y['floor']}:1</b><span>piso não-textual</span></div>
  </div>
</section>

<section>
  <h2>Tinta do ícone contra o fundo efetivo</h2>
  <p>Variante sem preenchimento encosta na <b>tela</b>, nunca em “transparente” — por isso Ghost e
  Secondary são medidos contra o fundo que aparece por trás deles. O <code>disabled</code> entra
  medido e isento: o WCAG dispensa componente inativo, e subir esse contraste faria o desabilitado
  parecer clicável.</p>
  <div class="scroller" style="margin-top:20px"><table>
    <thead><tr><th>Tema</th><th>Variante · estado</th><th></th><th>Tinta / fundo</th><th>Razão</th><th></th></tr></thead>
    <tbody>{ib_a11y_rows('tinta')}</tbody>
  </table></div>
</section>

<section>
  <h2>O limite do componente</h2>
  <p>No Button, a variante sem preenchimento e sem borda não precisa de limite próprio: ela é
  texto, e vale como texto. <b>Aqui essa frase seria falsa</b> — não existe texto. No Ghost, o
  próprio ícone é o limite visível do componente, e é ele que o portão mede contra a tela.</p>
  <div class="scroller" style="margin-top:20px"><table>
    <thead><tr><th>Tema</th><th>Variante</th><th></th><th>Frente / tela</th><th>Razão</th><th></th></tr></thead>
    <tbody>{ib_a11y_rows('limite')}</tbody>
  </table></div>
</section>

<section>
  <h2>Foco</h2>
  <p>O anel tem duas camadas: 2px de respiro na cor do fundo e 2px na cor do foco. O respiro é o
  que impede o anel de encostar no preenchimento — sem ele, laranja sobre laranja daria 1,00:1.
  Danger usa o anel de erro, para o foco não brigar com o vermelho.</p>
  <div class="dd" style="margin-top:16px">
    <div class="cell"><span class="lab" style="color:var(--al-text-secondary)">Anel padrão</span>
      <div class="stage2">
        {ib('primary', 'md', 'Buscar', 'search', '', ' is-focus')}
        {ib('secondary', 'md', 'Editar', 'pencil', '', ' is-focus')}
        {ib('ghost', 'md', 'Mais opções', 'ellipsis-vertical', '', ' is-focus')}
      </div>
      <p class="cap">Aparece no <code>:focus-visible</code> — teclado sim, clique de mouse não.</p>
    </div>
    <div class="cell"><span class="lab" style="color:var(--al-text-secondary)">Anel de erro</span>
      <div class="stage2">{ib('danger', 'md', 'Excluir', 'trash', '', ' is-focus')}</div>
      <p class="cap">Danger aponta para <code>focusRing.error</code>, não para o padrão.</p>
    </div>
  </div>
  <div class="scroller" style="margin-top:20px"><table>
    <thead><tr><th>Tema</th><th>Variante</th><th></th><th>Anel / tela</th><th>Razão</th><th></th></tr></thead>
    <tbody>{ib_a11y_rows('foco')}</tbody>
  </table></div>
</section>

<section>
  <h2>Estados que enganam</h2>
  <div class="rule"><div class="rn">09</div><div>
    <h3>Carregando: <code>aria-busy</code>, não <code>disabled</code></h3>
    <p>Marque <code>aria-busy="true"</code> e <code>aria-disabled="true"</code>, e trave o handler
    no JS. O atributo <code>disabled</code> tiraria o botão da ordem de foco no meio da interação,
    sem anunciar nada.</p>
  </div></div>
  <div class="rule"><div class="rn">10</div><div>
    <h3>O progresso se anuncia fora do botão</h3>
    <p>No Button, trocar o rótulo de “Publicar” para “Publicando…” já dá o aviso.
    <b>Aqui não existe rótulo para trocar</b>, então a região viva
    (<code>role="status"</code>, <code>aria-live="polite"</code>) deixa de ser complemento e passa
    a ser o único canal que informa que algo começou.</p>
  </div></div>
  <div class="rule"><div class="rn">11</div><div>
    <h3>O contraste baixo do desabilitado é intencional</h3>
    <p>O WCAG isenta componente inativo do 1.4.3 — não é reprova, é sinal. Subir esse contraste
    faz o desabilitado parecer clicável.</p>
  </div></div>
  <div class="rule"><div class="rn">12</div><div>
    <h3>Alvo de toque</h3>
    <p>Os dois passam o mínimo do WCAG 2.5.8 (24×24px):
    {IB_A11Y['targets'][0]['box']}px no <code>sm</code> e {IB_A11Y['targets'][1]['box']}px no
    <code>md</code>. Só o <code>md</code> alcança os 44 que o Carbon recomenda para alvo de ícone —
    por decisão registrada não há expansão de área por CSS, e a contrapartida é a regra de uso: o
    <code>sm</code> só entra em densidade alta, nunca em interface primariamente de toque.</p>
  </div></div>
  <div class="rule"><div class="rn">13</div><div>
    <h3>Alto contraste do sistema</h3>
    <p>O modo de alto contraste descarta <code>box-shadow</code> — o anel sumiria junto. O
    componente devolve o foco como <code>outline</code> nativo dentro de
    <code>@media (forced-colors: active)</code>.</p>
  </div></div>
</section>

<section>
  <h2>Contrato de marcação, medido</h2>
  <p>O <code>aria-label</code> não vive no CSS, então o portão de literal não alcança. Ele vive na
  marcação — e é aqui que o <code>a11y.py</code> o cobra, lendo o HTML que este site emite:
  <b>{IB_A11Y['markupChecked'] or 0} elementos</b> <code>.al-icon-btn</code> nesta página, nenhum
  fora do contrato. Ele reprova quatro coisas: botão sem <code>aria-label</code>,
  <code>aria-hidden</code> no próprio botão, <code>aria-busy</code> sem
  <code>aria-disabled</code>, e o atributo <code>disabled</code> no lugar de
  <code>aria-disabled</code>.</p>
  <pre style="margin-top:20px"><code>&lt;button type="button" class="al-icon-btn al-icon-btn--ghost al-icon-btn--md"
        aria-label="Buscar"&gt;
  &lt;span class="al-icon-btn__spinner" aria-hidden="true"&gt;&lt;/span&gt;
  &lt;svg class="al-icon" aria-hidden="true" focusable="false"&gt;…&lt;/svg&gt;
&lt;/button&gt;</code></pre>
  <div class="note" style="margin-top:20px">
    <b>Os dois atributos do svg fazem coisas diferentes</b>
    <p><code>aria-hidden</code> tira o ícone do leitor de tela; <code>focusable="false"</code> tira
    da ordem de tabulação, porque SVG inline entra nela sozinho em alguns navegadores. O nome vai
    no <b>botão</b>, nunca no svg — anunciar os dois seria ruído duplicado.</p>
  </div>
</section>'''


# ═══════════════════════════════════════════════════════════════════════ TAG
TAG_TYPES = [('filled', 'Filled'), ('outlined', 'Outlined')]
TAG_STATUSES = [('success', 'Success'), ('warning', 'Warning'), ('error', 'Error'),
                ('info', 'Info'), ('neutral', 'Neutral')]
TAG_SIZES = [('sm', 'sm · 20px'), ('md', 'md · 28px')]
TAG_LABELS = {'success': 'Pago', 'warning': 'Pendente', 'error': 'Recusado',
              'info': 'Processando', 'neutral': 'Rascunho'}
TAG_ROLES = ['bg', 'label', 'border']


def tg(tipo, status, size='md', label=None, x=False, cls=''):
    """Uma Tag real.

    `cls=' is-focus'` congela o anel para o especime - e ai o X sai da ordem de
    tabulacao com tabindex="-1", porque especime nao pode virar parada de tab de
    mentira. Mesmo cuidado dos especimes de Button.
    """
    label = TAG_LABELS[status] if label is None else label
    c = f'al-tag al-tag--{tipo} al-tag--{status} al-tag--{size}{cls}'
    if not x:
        return f'<span class="{c}">{label}</span>'
    ti = ' tabindex="-1"' if 'is-focus' in cls else ''
    return (f'<span class="{c}">{label}<button type="button" class="al-tag__dismiss"'
            f'{ti} aria-label="Remover {label}">{al_icon("x")}</button></span>')


def tag_specimens():
    """Os dois tipos, os cinco status, os dois tamanhos - parados, lado a lado."""
    cells = []
    for tipo, nome in TAG_TYPES:
        linhas = ''.join(
            '<div class="tagrow">'
            + ''.join(tg(tipo, st, size) for st, _ in TAG_STATUSES)
            + '</div>'
            for size, _ in TAG_SIZES)
        cells.append(
            f'<div class="cell"><span class="lab" style="color:var(--al-text-secondary)">'
            f'{nome}</span><div class="stage2" style="display:block">{linhas}</div>'
            f'<p class="cap">Acima <code>sm</code>, abaixo <code>md</code>. As duas linhas '
            f'do {nome} têm a mesma altura das do outro tipo — a borda não cresce a caixa.</p>'
            f'</div>')
    return '<div class="dd">' + ''.join(cells) + '</div>'


def tag_geo_rows():
    rows = []
    for size, _ in TAG_SIZES:
        for role in ['padding-x', 'padding-y', 'gap', 'font', 'icon-size']:
            name = f'tag-{size}-{role}'
            res = TAG['resolved'][name]
            val = f'{res[1]}/{res[2]} · peso {res[3]}' if isinstance(res, list) else f'{res}px'
            rows.append(f'<tr><td class="tok dim">{size}</td><td class="tok">--al-{name}</td>'
                        f'<td class="tok dim">{TAG["alias"][name]}</td>'
                        f'<td class="num">{val}</td></tr>')
    for role in ['radius', 'border-width']:
        name = f'tag-{role}'
        rows.append(f'<tr><td class="tok dim">ambos</td><td class="tok">--al-{name}</td>'
                    f'<td class="tok dim">{TAG["alias"][name]}</td>'
                    f'<td class="num">{TAG["resolved"][name]}px</td></tr>')
    return '\n'.join(rows)


def tag_token_rows():
    rows = []
    for tipo, _ in TAG_TYPES:
        nomes = [n for n in TAG['alias'] if n.startswith(f'tag-{tipo}-')]
        for name in nomes:
            ref = TAG['alias'][name]
            res = TAG['resolved'][name]
            lt = res['light'] if isinstance(res, dict) else res
            sw = (f'<span class="chip sm" style="background:{lt}"></span>'
                  if isinstance(lt, str) and lt.startswith('#') else '')
            rows.append(f'<tr data-type="{tipo}"><td class="tok">--al-{name}</td>'
                        f'<td class="tok dim">{ref}</td>'
                        f'<td class="tok dim">{sw}{lt}</td></tr>')
    return '\n'.join(rows)


def tag_a11y_rows(group):
    out = []
    for r in TAG_A11Y['rows']:
        if r['group'] != group:
            continue
        verdict = ('<span class="exc">isento</span>' if r['exempt']
                   else '<span class="pass">passa</span>')
        chips = (f'<span class="chip sm" style="background:{r["fg"]}"></span>'
                 f'<span class="chip sm" style="background:{r["bg"]}"></span>')
        out.append(
            f'<tr><td class="tok dim">{"claro" if r["theme"] == "light" else "escuro"}</td>'
            f'<td class="name">{r["label"]}</td><td class="chipcell">{chips}</td>'
            f'<td class="tok dim">{r["fg"]} / {r["bg"]}</td>'
            f'<td class="num strong">{r["ratio"]:.2f}:1</td><td>{verdict}</td></tr>')
    return '\n'.join(out)


N_TAG_MEDIDAS = len([r for r in TAG_A11Y['rows'] if not r['exempt']])
N_TAG_ISENTAS = len(TAG_A11Y['rows']) - N_TAG_MEDIDAS
TAG_SM_BOX = TAG_A11Y['targets'][0]['box']
TAG_MD_BOX = TAG_A11Y['targets'][1]['box']

TAG_OVERVIEW = f'''
<section>
  <h2>Playground</h2>
  <div class="pg">
    <div class="stage" id="tag-stage">{tg('filled', 'success')}</div>

    <div class="controls" id="tag-controls">
      <div class="ctl"><span class="ctl-name">Tipo</span>{seg('tagtype', TAG_TYPES, 'filled')}</div>
      <div class="ctl"><span class="ctl-name">Status</span>{seg('tagstatus', TAG_STATUSES, 'success')}</div>
      <div class="ctl"><span class="ctl-name">Tamanho</span>{seg('tagsize', TAG_SIZES, 'md')}</div>
      <div class="ctl"><span class="ctl-name">Dismissible</span>{seg('tagdis', [('no', 'Só leitura'), ('yes', 'Com X')], 'no')}</div>
      <div class="ctl"><span class="ctl-name">Tema</span>{seg('tagtheme', [('auto', 'Do sistema'), ('light', 'Claro'), ('dark', 'Escuro')], 'auto')}</div>
      <div class="ctl"><label for="tag-label" class="ctl-name">Rótulo</label>
        <input class="txt" id="tag-label" type="text" value="Pago" maxlength="28"></div>
    </div>

    <div class="codewrap">
      <div class="codebar"><span>Marcação</span>
        <button type="button" class="copy" id="tag-copy">Copiar</button></div>
      <pre><code id="tag-code"></code></pre>
    </div>
  </div>
  <p style="margin-top:14px; font-size:13.5px; color:var(--al-text-secondary)">
    A tag acima é o componente real: esta página carrega o mesmo <code>tag.css</code> que vai
    para produção. Repare que o <code>aria-label</code> do X acompanha o rótulo — sem isso,
    numa lista de seis filtros, seis botões chamados “Remover” são indistinguíveis por leitor
    de tela.
  </p>
</section>

<section>
  <h2>Os dois tipos</h2>
  <div class="dd">
    <div class="cell">
      <span class="lab" style="color:var(--al-text-secondary)">Uma entidade, um estado</span>
      <div class="stage2">{tg('filled', 'success')}{tg('filled', 'error')}</div>
      <p class="cap"><b>Filled</b> quando a tag é o único indicador de estado de algo — status
      de pedido numa linha de tabela. É o preenchimento que faz ela ser notada sem depender do
      que está em volta. Precedente: Spectrum, o único dos cinco com sólido como padrão.</p>
    </div>
    <div class="cell">
      <span class="lab" style="color:var(--al-text-secondary)">Três ou mais, juntas</span>
      <div class="stage2">{tg('outlined', 'info', 'md', 'Livros', True)}{tg('outlined', 'neutral', 'md', 'Usados', True)}{tg('outlined', 'warning', 'md', 'Em estoque', True)}</div>
      <p class="cap"><b>Outlined</b> em grupo: cinco preenchimentos saturados lado a lado
      competem entre si e nenhum ganha. Precedente: Carbon, Primer e Polaris usam baixa ênfase
      como padrão, porque tag quase sempre aparece em grupo.</p>
    </div>
  </div>
</section>

<section>
  <h2>Onde ela vive</h2>
  <div class="dd">
    <div class="cell">
      <span class="lab" style="color:var(--al-text-secondary)">Dentro de uma frase</span>
      <div class="stage2">
        <span>O pedido <b>#48213</b> está {tg('filled', 'success', 'sm')} desde ontem.</span>
      </div>
      <p class="cap">O <code>sm</code> existe para isto: espaço condensado e inline. Precedente:
      Carbon. A tag alinha pelo meio da linha, não pela base.</p>
    </div>
    <div class="cell">
      <span class="lab" style="color:var(--al-text-secondary)">Numa barra de filtros</span>
      <div class="stage2">{tg('outlined', 'neutral', 'md', 'Últimos 30 dias', True)}{tg('outlined', 'neutral', 'md', 'Pagos', True)}</div>
      <p class="cap">Filtro aplicado é o caso canônico do <code>Dismissible</code>: remover tem
      efeito real e o usuário consegue aplicar de novo. Precedente: Carbon.</p>
    </div>
  </div>
</section>'''

TAG_SPECS = f'''
<section>
  <h2>Anatomia</h2>
  <div class="anat">
    <div><b>Contêiner</b><span><code>span</code>, não <code>div</code> nem <code>button</code>. Pílula de raio total, borda de 1px sempre presente — transparente no <code>filled</code>.</span></div>
    <div><b>Rótulo</b><span>Texto direto, sem elemento próprio. É ele que carrega o sentido; a cor apenas reforça.</span></div>
    <div><b>X</b><span>Opcional, {TAG_SM_BOX}px no <code>sm</code> e {TAG_MD_BOX}px no <code>md</code>. É o único filho focável, e o único acionável.</span></div>
    <div><b>Nome acessível do X</b><span><code>aria-label</code> que <b>inclui o rótulo</b>: “Remover Pago”, nunca só “Remover”.</span></div>
  </div>
  <div class="note" style="margin-top:16px">
    <b>A tag é conteúdo, não controle</b>
    Ela fica fora da ordem de tabulação e não recebe foco — é a mesma regra do Carbon para a
    read-only, e é por isso que clicar no rótulo não faz nada. Quando o <code>Dismissible</code>
    liga, quem entra na ordem de tabulação é só o X. <code>span</code> também é o que deixa a
    tag viver dentro de uma frase sem quebrar o fluxo do texto.
  </div>
</section>

<section>
  <h2>As vinte combinações</h2>
  {tag_specimens()}
</section>

<section>
  <h2>Medidas</h2>
  <div class="scroller">
    <table>
      <thead><tr><th>Tamanho</th><th>Token</th><th>Aponta para</th><th>Valor</th></tr></thead>
      <tbody>{tag_geo_rows()}</tbody>
    </table>
  </div>
  <div class="note" style="margin-top:16px">
    <b>Não existe token de altura</b>
    Ela é consequência: <code>padding-y</code> × 2 mais a entrelinha. Dá
    {TAG['derived']['height']['sm']}px no <code>sm</code> e {TAG['derived']['height']['md']}px no
    <code>md</code>. A borda de 1px existe nos dois tipos e o padding desconta a espessura —
    <code>calc(padding − border-width)</code> — e é isso que faz <code>filled</code> e
    <code>outlined</code> ocuparem a mesma caixa. Trocar o tipo de uma tag nunca move o que
    está em volta.
  </div>
</section>

<section>
  <h2>Tokens de cor</h2>
  <div class="ctl" style="margin-bottom:14px"><span class="ctl-name">Filtrar</span>
    {seg('tagtokfilter', [('all', 'Todos')] + TAG_TYPES, 'all')}</div>
  <div class="scroller">
    <table>
      <thead><tr><th>Token do Tag</th><th>Aponta para</th><th>Resolve em (claro)</th></tr></thead>
      <tbody id="tagtokbody">{tag_token_rows()}</tbody>
    </table>
  </div>
  <div class="note" style="margin-top:16px">
    <b>{N_TAG_TOKENS} tokens no código, 34 variáveis no Figma</b>
    A diferença é deliberada, e é a mesma regra do Icon Button. As duas fontes são
    <i>estilos de texto</i> (<code>Label/sm</code> e <code>Label/md</code>), o anel do X reusa o
    <i>effect style</i> <code>Focus-ring/Default</code> porque sombra não pode ser variável no
    Figma, e os dois <code>icon-size</code> ligam direto à Fundação.
  </div>
  <div class="note">
    <b>O tipo vem antes do status no nome</b>
    Não é estilo, é a estrutura da decisão. O tipo define <b>quais papéis existem</b> — o
    <code>filled</code> tem preenchimento, o <code>outlined</code> tem borda colorida — e o
    status define <b>qual cor entra em cada papel</b>. É o mesmo lugar que
    <code>primary</code> e <code>ghost</code> ocupam no Button. O único token que vive só no
    tipo é <code>--al-tag-outlined-bg</code>, que não varia por status: cinco tokens idênticos
    seriam cinco lugares para errar a mesma coisa.
  </div>
</section>'''

TAG_GUIDE = f'''
<section>
  <h2>Quando usar</h2>
  <div class="dd">
    <div class="cell do">
      <span class="lab">Estado ou categoria</span>
      <div class="stage2">{tg('filled', 'success')}{tg('outlined', 'neutral', 'md', 'Interno')}</div>
      <p class="cap">Rotular o estado de uma entidade, ou etiquetá-la sem carga de estado.</p>
    </div>
    <div class="cell no">
      <span class="lab">Ação</span>
      <div class="stage2"><button type="button" class="al-btn al-btn--secondary al-btn--sm" tabindex="-1"><span class="al-btn__label">Ver detalhes</span></button></div>
      <p class="cap">Se clicar faz algo além de remover a própria tag, é <b>Button</b>.
      Precedente: Spectrum — badges não são interativos; se precisar de interação, use botão,
      tag ou link.</p>
    </div>
  </div>
</section>

<section>
  <h2>O rótulo carrega o sentido</h2>
  <p>Esta é a regra mais importante do componente, e é o critério que mais reprova este tipo de
  peça em qualquer sistema. A diferença entre os status é <b>puramente visual</b>: ela não chega
  a quem não distingue as cores, e não chega a leitor de tela nenhum.</p>
  <div class="dd" style="margin-top:16px">
    <div class="cell no">
      <span class="lab">A cor fazendo o trabalho</span>
      <div class="stage2">{tg('filled', 'error', 'md', 'Pagamento')}</div>
      <p class="cap">Vermelho escrito “Pagamento” não comunica nada sozinho.</p>
    </div>
    <div class="cell do">
      <span class="lab">O texto fazendo o trabalho</span>
      <div class="stage2">{tg('filled', 'error', 'md', 'Pagamento recusado')}</div>
      <p class="cap">Precedente: Primer — se você lista sucessos e falhas, prefixe cada rótulo
      em vez de confiar no esquema de cor.</p>
    </div>
  </div>
</section>

<section>
  <h2>As regras</h2>

  <div class="rule"><div class="rn">01</div><div>
    <h3>Sentence case, uma palavra</h3>
    <p>Duas só quando o estado for composto e uma não resolver — “Reembolsado parcialmente”.
    Precedente: Polaris, literalmente essa regra.</p></div></div>

  <div class="rule"><div class="rn">02</div><div>
    <h3>Passado para concluído, gerúndio para processo</h3>
    <p>“Pago”, “Enviado”, “Cancelado” contra “Processando”, “Enviando”. Precedente: Polaris.</p></div></div>

  <div class="rule"><div class="rn">03</div><div>
    <h3>Rótulo longo se resolve na origem, não no truncamento</h3>
    <p>O Carbon trunca e revela o texto completo por tooltip. <b>Aqui não</b>: o Tooltip ainda
    não existe no AL, e truncar esconderia informação sem devolver caminho para recuperá-la.
    Então a regra é o passo anterior — encurte antes de chegar na tag. Quando o Tooltip
    existir, esta regra é revisitada.</p></div></div>

  <div class="rule"><div class="rn">04</div><div>
    <h3>Não misture os dois tipos no mesmo grupo</h3>
    <p>A diferença de tratamento vira uma hierarquia que ninguém quis criar: o olho lê o sólido
    como mais importante. Escolha um tipo por grupo.</p></div></div>

  <div class="rule"><div class="rn">05</div><div>
    <h3>Uma tag de status por entidade</h3>
    <p>Se um pedido é “Pago” e “Enviado”, isso são dois campos. Duas tags lado a lado disputam
    qual é o estado real.</p></div></div>

  <div class="rule"><div class="rn">06</div><div>
    <h3>Tag não substitui banner</h3>
    <p>Um erro que exige ação precisa de um lugar onde caiba a explicação e o próximo passo.
    Precedente: Polaris — não use badge vermelho como única forma de comunicar estado crítico.</p></div></div>

  <div class="rule"><div class="rn">07</div><div>
    <h3><code>sm</code> dismissível só em interface de ponteiro</h3>
    <p>O X do <code>sm</code> tem {TAG_SM_BOX}px de alvo, contra os 24 mínimos do WCAG 2.5.8.
    Em contexto de toque, use <code>md</code>. É a mesma família de decisão do <code>sm</code>
    do Button — 36px contra os 44 recomendados pelo Carbon — e a saída é a mesma: regra de uso,
    não geometria.</p></div></div>

  <div class="rule"><div class="rn">08</div><div>
    <h3>Depois de remover, o foco vai para a tag anterior</h3>
    <p>Sem isso o foco cai no <code>body</code> e quem navega por teclado se perde no meio da
    lista. Precedente: Primer, na acessibilidade do Token. Isso é JS — o CSS não alcança.</p></div></div>

  <div class="rule"><div class="rn">09</div><div>
    <h3>Prefira <code>Outlined</code> para a tag dismissível</h3>
    <p>A borda sinaliza “isto responde a interação” antes de o usuário passar o mouse.
    Precedente: o Carbon dá borda de contêiner às variantes selectable e operational
    exatamente para indicar interatividade aumentada, e deixa a read-only sem borda.</p></div></div>

  <div class="rule"><div class="rn">10</div><div>
    <h3>Sem hover no X — só o cursor muda</h3>
    <p><b>Divergência consciente</b>: o Carbon muda o fundo do ícone de fechar no hover. Aqui
    não. A consequência a assumir é que, em tela de toque, não há hover nenhum — e aí o alvo
    pequeno da regra 07 fica sem qualquer reforço. É também por isso que este componente não
    tem transição nem animação alguma, e é o único do AL sem pendência de escala de motion.</p></div></div>
</section>

<section>
  <h2>Fora de escopo, de propósito</h2>
  <div class="anat">
    <div><b>Status brand</b><span>Marca não é status, e branco sobre <code>bg-brand</code> dá 3,34:1 — abaixo do piso de texto. Se voltar, é v2, com <code>bg-brand-strong</code>.</span></div>
    <div><b>Selectable · operational</b><span>Tag que filtra ao clicar é outro componente, não uma variante deste.</span></div>
    <div><b>Desabilitado</b><span>Tag é conteúdo. Conteúdo não desabilita.</span></div>
    <div><b>Tamanho lg</b><span>O Carbon tem três. O AL tem dois, mesma decisão do Button.</span></div>
    <div><b>Ícone à esquerda</b><span>Spectrum e Polaris têm. Aqui o único slot é o X, à direita.</span></div>
  </div>
</section>'''

TAG_A11Y_TAB = f'''
<section>
  <h2>O piso é 4,5:1, não 3:1</h2>
  <p>Esta é a diferença conceitual entre o Tag e o Icon Button, e ela explica quase tudo nesta
  aba. Lá o portador do sentido é um <b>ícone</b>, conteúdo não-textual: critério 1.4.11, piso
  3:1. Aqui é um <b>rótulo de texto</b>: critério 1.4.3, piso 4,5:1.</p>
  <p style="margin-top:12px">A consequência foi concreta e mudou o escopo. Branco sobre a marca
  dá 3,34:1 — no Icon Button isso é <b>aprovação</b>; aqui seria <b>reprova</b>. Foi por isso que
  o status Brand ficou de fora desta versão, e é por isso que este componente tem
  <b>zero exceções</b> — o primeiro do AL a fechar em zero carregando texto.</p>
  <div class="stats">
    <div class="stat hl"><b>{N_TAG_MEDIDAS}</b><span>combinações medidas</span></div>
    <div class="stat"><b>{TAG_A11Y['fails']}</b><span>reprovas</span></div>
    <div class="stat"><b>{N_TAG_ISENTAS}</b><span>isentas medidas</span></div>
    <div class="stat"><b>{TAG_A11Y['floors']['text']}:1</b><span>piso do rótulo</span></div>
  </div>
</section>

<section>
  <h2>Rótulo contra o fundo efetivo</h2>
  <p>O <code>outlined</code> não tem preenchimento, então o rótulo não está sobre um sólido —
  está sobre a tela. Por isso ele é medido contra os <b>dois</b> fundos: a tela e a superfície,
  porque tag quase sempre vive dentro de card, tabela ou painel. O <code>filled</code> cobre o
  fundo, e uma medição basta.</p>
  <div class="scroller" style="margin-top:20px"><table>
    <thead><tr><th>Tema</th><th>Combinação</th><th></th><th>Rótulo / fundo</th><th>Razão</th><th></th></tr></thead>
    <tbody>{tag_a11y_rows('rotulo')}</tbody>
  </table></div>
</section>

<section>
  <h2>O limite do pill</h2>
  <p>Medido e listado, mas <b>isento</b> — e a razão importa. O 1.4.11 cobra contraste de
  elemento gráfico <b>necessário para entender o conteúdo</b>. No Icon Button o desenho é a única
  coisa que informa que existe um acionável ali, então o limite é portão. Aqui quem informa é o
  texto, e o contorno é decoração. É o que faz o <code>filled neutral</code> aparecer em 1,32:1
  sem reprovar — e ele fica medido para ninguém “corrigir” achando que escapou.</p>
  <div class="scroller" style="margin-top:20px"><table>
    <thead><tr><th>Tema</th><th>Combinação</th><th></th><th>Limite / fundo</th><th>Razão</th><th></th></tr></thead>
    <tbody>{tag_a11y_rows('limite')}</tbody>
  </table></div>
</section>

<section>
  <h2>Foco</h2>
  <p>Só o X recebe foco — a tag é conteúdo, não controle. O anel tem duas camadas: 2px de
  respiro na cor do fundo e 2px na cor do foco, e é o respiro que impede o anel de encostar no
  preenchimento. Ele é sombra, então não empurra layout, e não anima.</p>
  <div class="dd" style="margin-top:16px">
    <div class="cell"><span class="lab" style="color:var(--al-text-secondary)">Anel no X</span>
      <div class="stage2">
        {tg('filled', 'success', 'md', None, True, ' is-focus')}
        {tg('outlined', 'info', 'md', None, True, ' is-focus')}
      </div>
      <p class="cap">Aparece no <code>:focus-visible</code> — teclado sim, clique de mouse não.
      Aqui está forçado por classe, para dar para ver parado.</p>
    </div>
    <div class="cell"><span class="lab" style="color:var(--al-text-secondary)">O que não existe</span>
      <div class="stage2">{tg('outlined', 'neutral', 'md', 'Interno', True)}</div>
      <p class="cap">Sem hover no X e sem estado na tag. <b>Nenhuma transição neste
      componente</b> — é o único do AL sem duração literal esperando a escala de motion.</p>
    </div>
  </div>
  <div class="scroller" style="margin-top:20px"><table>
    <thead><tr><th>Tema</th><th>Combinação</th><th></th><th>Anel / fundo</th><th>Razão</th><th></th></tr></thead>
    <tbody>{tag_a11y_rows('foco')}</tbody>
  </table></div>
</section>

<section>
  <h2>O contrato de marcação</h2>
  <p>Dois contratos deste componente não vivem no CSS, então o portão de literal não os alcança.
  O primeiro não tem portão possível — <b>o rótulo carregar o sentido</b> é regra de uso, e está
  nas Diretrizes. O segundo é verificável de verdade, e é aqui que o <code>a11y.py</code> o
  cobra, lendo o HTML que este site emite: <b>{TAG_A11Y['markupChecked'] or 0} elementos</b>
  <code>.al-tag</code> nesta página, nenhum fora.</p>
  <div class="anat" style="margin-top:16px">
    <div><b>Sem foco na tag</b><span>Nada de <code>button</code>, <code>role="button"</code> ou <code>tabindex</code> no <code>.al-tag</code>.</span></div>
    <div><b>aria-label com o rótulo</b><span>O portão extrai o texto da tag e confere se ele aparece dentro do <code>aria-label</code> do X.</span></div>
    <div><b>type="button"</b><span>Dentro de <code>form</code>, o padrão do HTML é submit.</span></div>
    <div><b>svg decorativo</b><span><code>aria-hidden</code> no desenho: o nome vive no botão, anunciar os dois é ruído duplicado.</span></div>
  </div>
</section>

<section>
  <h2>Alvo de toque</h2>
  <p>O X tem <b>{TAG_SM_BOX}px</b> no <code>sm</code> e <b>{TAG_MD_BOX}px</b> no <code>md</code>,
  contra os 24 mínimos do WCAG 2.5.8. Exceção consciente, sem expansão de área por
  pseudo-elemento — a mesma decisão do <code>sm</code> do Button, 36px contra os 44 recomendados
  pelo Carbon. A saída é a regra 07, não geometria.</p>
</section>'''



# ══════════════════════════════════════════════════════════ COMPONENTE · Avatar
AVATAR_TYPES = [('initials', 'Initials'), ('icon', 'Icon'), ('photo', 'Photo')]
AVATAR_SIZES = [('sm', 'sm'), ('md', 'md'), ('lg', 'lg')]

AVATAR_DIAM = AVATAR['derived']['diameter']
N_AV_MEDIDAS = len(AVATAR_A11Y['rows'])


def avatar_specimens():
    """As nove combinacoes, paradas, na mesma grade do Figma."""
    linhas = []
    for tipo, nome in AVATAR_TYPES:
        celulas = ''.join(
            f'<div class="av-cell">{av(tipo, size, "Maria Silva" if tipo != "photo" else "Maria Silva", PHOTO_A if size != "md" else PHOTO_B)}'
            f'<span>{size} · {AVATAR_DIAM[size]}px</span></div>'
            for size, _ in AVATAR_SIZES)
        linhas.append(f'<div class="av-grid-row"><div class="av-grid-name">{nome}</div>'
                      f'<div class="av-grid-cells">{celulas}</div></div>')
    return '<div class="av-grid">' + ''.join(linhas) + '</div>'


def avatar_geo_rows():
    rows = []
    for size, _ in AVATAR_SIZES:
        for role in ['padding', 'icon-size', 'font']:
            name = f'avatar-{size}-{role}'
            res = AVATAR['resolved'][name]
            val = (f'{res[1]}/{res[2]} · peso {res[3]}' if isinstance(res, list)
                   else f'{res}px')
            rows.append(f'<tr><td class="tok dim">{size}</td><td class="tok">--al-{name}</td>'
                        f'<td class="tok dim">{AVATAR["alias"][name]}</td>'
                        f'<td class="num">{val}</td></tr>')
    name = 'avatar-radius'
    rows.append(f'<tr><td class="tok dim">os três</td><td class="tok">--al-{name}</td>'
                f'<td class="tok dim">{AVATAR["alias"][name]}</td>'
                f'<td class="num">{AVATAR["resolved"][name]}px</td></tr>')
    return '\n'.join(rows)


def avatar_token_rows():
    rows = []
    for role in ['bg', 'label', 'icon']:
        name = f'avatar-{role}'
        res = AVATAR['resolved'][name]
        rows.append(
            f'<tr><td class="tok">--al-{name}</td>'
            f'<td class="tok dim">{AVATAR["alias"][name]}</td>'
            f'<td class="tok dim"><span class="chip sm" style="background:{res["light"]}"></span>'
            f'{res["light"]}</td>'
            f'<td class="tok dim"><span class="chip sm" style="background:{res["dark"]}"></span>'
            f'{res["dark"]}</td></tr>')
    return '\n'.join(rows)


def avatar_a11y_rows():
    out = []
    papel = {'label': 'Iniciais · texto', 'icon': 'Ícone · não-textual'}
    for r in AVATAR_A11Y['rows']:
        chips = (f'<span class="chip sm" style="background:{r["fg"]}"></span>'
                 f'<span class="chip sm" style="background:{r["bg"]}"></span>')
        out.append(
            f'<tr><td class="tok dim">{"claro" if r["theme"] == "light" else "escuro"}</td>'
            f'<td class="name">{papel[r["what"]]}</td><td class="chipcell">{chips}</td>'
            f'<td class="tok dim">{r["fg"]} / {r["bg"]}</td>'
            f'<td class="num strong">{r["ratio"]:.2f}:1</td>'
            f'<td class="tok dim">{r["floor"]}:1</td>'
            f'<td><span class="pass">passa</span></td></tr>')
    return '\n'.join(out)



AVATAR_OVERVIEW = f'''
<section>
  <h2>Playground</h2>
  <div class="pg">
    <div class="stage" id="avatar-stage">{av_person('initials', 'md', 'Maria Silva', 'Comentou há 2 horas')}</div>

    <div class="controls" id="avatar-controls">
      <div class="ctl"><span class="ctl-name">Tipo</span>{seg('avtype', AVATAR_TYPES, 'initials')}</div>
      <div class="ctl"><span class="ctl-name">Tamanho</span>{seg('avsize', AVATAR_SIZES, 'md')}</div>
      <div class="ctl"><span class="ctl-name">Contexto</span>{seg('avctx', [('deco', 'Ao lado do nome'), ('solo', 'Sozinho')], 'deco')}</div>
      <div class="ctl"><span class="ctl-name">Tema</span>{seg('avtheme', [('auto', 'Do sistema'), ('light', 'Claro'), ('dark', 'Escuro')], 'auto')}</div>
      <div class="ctl"><label for="avatar-name" class="ctl-name">Nome</label>
        <input class="txt" id="avatar-name" type="text" value="Maria Silva" maxlength="40"></div>
    </div>

    <div class="codewrap">
      <div class="codebar"><span>Marcação</span>
        <button type="button" class="copy" id="avatar-copy">Copiar</button></div>
      <pre><code id="avatar-code"></code></pre>
    </div>
  </div>
  <p style="margin-top:14px; font-size:13.5px; color:var(--al-text-secondary)">
    Troque o <b>Contexto</b> e veja a marcação mudar: ao lado de um nome escrito o avatar sai
    da árvore de acessibilidade (<code>aria-hidden</code>); sozinho, ele vira a informação e
    precisa de <code>role="img"</code> com o nome. É o mesmo componente — muda o contrato, não
    o CSS. As iniciais saem do nome que você digitar, cortadas em duas letras maiúsculas.
  </p>
</section>

<section>
  <h2>Os três tipos são uma cadeia, não um menu</h2>
  <p>Esta é a diferença entre o Avatar e todo o resto do sistema. No Button você <b>escolhe</b>
  a variante; aqui você não escolhe o tipo — ele é o primeiro da fila que tem material para
  existir. Foto se houver foto; iniciais se houver nome; ícone quando não há nem um nem outro.</p>
  <div class="av-chain">
    <div class="av-chain-step">
      {av('photo', 'lg', 'Maria Silva')}
      <b>Photo</b>
      <span>Tem foto. É a opção mais informativa, e nenhum sistema promove as outras duas
      havendo foto. <i>Polaris, Material.</i></span>
    </div>
    <div class="av-chain-arrow" aria-hidden="true">{CARET}</div>
    <div class="av-chain-step">
      {av('initials', 'lg', 'Diego Costa')}
      <b>Iniciais</b>
      <span>Sem foto, nome conhecido. A imagem falhou, demorou ou nunca existiu.
      <i>Polaris: a URL cai para iniciais se a imagem não carregar.</i></span>
    </div>
    <div class="av-chain-arrow" aria-hidden="true">{CARET}</div>
    <div class="av-chain-step">
      {av('icon', 'lg')}
      <b>Icon</b>
      <span>Nem foto nem nome: anônimo, convidado, usuário removido. O fim da fila —
      nunca uma caixa vazia. <i>Material: “never leave the avatar blank”.</i></span>
    </div>
  </div>
</section>

<section>
  <h2>Onde ele vive</h2>
  <div class="dd">
    <div class="cell">
      <span class="lab" style="color:var(--al-text-secondary)">Linha de lista · sm</span>
      <div class="stage2" style="display:block">
        <div class="av-list">
          <div>{av_person('photo', 'sm', 'Maria Silva', 'Aprovou o orçamento')}</div>
          <div>{av_person('initials', 'sm', 'Diego Costa', 'Pediu revisão')}</div>
          <div>{av_person('icon', 'sm', 'Usuário removido', 'Comentário arquivado')}</div>
        </div>
      </div>
      <p class="cap">O <code>sm</code> existe para isto: lista, tabela, comentário — onde o
      avatar acompanha texto denso e não pode roubar a linha. Precedente: Polaris usa o menor
      quando “o médio é grande demais para o layout”.</p>
    </div>
    <div class="cell">
      <span class="lab" style="color:var(--al-text-secondary)">Topo de perfil · lg</span>
      <div class="stage2" style="display:block">
        <div class="av-profile">
          {av('photo', 'lg', 'Maria Silva', PHOTO_B, decorativo=False)}
          <div><b>Maria Silva</b><span>Design Ops · São Paulo</span></div>
        </div>
      </div>
      <p class="cap">Aqui o avatar é o foco, não o acompanhante. Precedente: Material usa
      64–96px em cabeçalho de perfil; o Primer fecha a escala dele em 64.</p>
    </div>
  </div>
</section>'''


AVATAR_SPECS = f'''
<section>
  <h2>Anatomia</h2>
  <div class="anat">
    <div><b>Involucro</b><span><code>span</code>, nunca <code>button</code>. Círculo de raio total, tamanho fixo nos dois eixos, <code>overflow:hidden</code> para recortar a foto.</span></div>
    <div><b>Filho único</b><span>Um <code>img.al-avatar__photo</code>, um <code>span.al-avatar__initials</code> ou um <code>svg.al-icon</code>. É ele que define o tipo — não há classe de tipo.</span></div>
    <div><b>Iniciais</b><span>Duas letras, maiúsculas. O CSS força <code>text-transform</code> como rede de segurança da regra de conteúdo.</span></div>
    <div><b>Nome acessível</b><span>Mora no involucro. A foto leva <code>alt=""</code> sempre, e o ícone leva <code>aria-hidden</code> sempre.</span></div>
  </div>
  <div class="note" style="margin-top:16px">
    <b>O tipo não tem classe modificadora</b>
    Isso não é economia de CSS, é a cadeia de fallback virando código. A foto se posiciona
    sobre a caixa inteira por conta própria (<code>position:absolute; inset:0</code>), ignorando
    o padding do involucro — então ela não precisa de um <code>--photo</code> zerando padding.
    A consequência: cair de Photo para Iniciais é <b>trocar um nó filho</b>, com o involucro
    parado. Quem implementa o <code>onerror</code> da imagem substitui um elemento e mais nada.
  </div>
</section>

<section>
  <h2>As nove combinações</h2>
  {avatar_specimens()}
</section>

<section>
  <h2>Medidas</h2>
  <div class="scroller">
    <table>
      <thead><tr><th>Tamanho</th><th>Token</th><th>Aponta para</th><th>Valor</th></tr></thead>
      <tbody>{avatar_geo_rows()}</tbody>
    </table>
  </div>
  <div class="note" style="margin-top:16px">
    <b>Não existe token de diâmetro</b>
    Ele é consequência: <code>padding × 2 + icon-size</code>. Dá {AVATAR_DIAM['sm']}px no
    <code>sm</code>, {AVATAR_DIAM['md']}px no <code>md</code> e {AVATAR_DIAM['lg']}px no
    <code>lg</code> — a mesma conta nos três tipos, porque os três ocupam a mesma caixa quadrada.
  </div>
  <div class="note">
    <b>Por que o <code>icon-size</code> é a âncora, e não a entrelinha</b>
    Aqui o Avatar diverge do Button e do Tag, onde a altura nasce da tipografia. Se o diâmetro
    derivasse do texto, o <code>Initials md</code> fecharia em 12+28+12 = <b>52px</b> e o
    <code>Icon md</code> em <b>48px</b> — dois tipos do mesmo tamanho com caixas diferentes,
    e, com raio total, uma caixa não-quadrada deixa de ser círculo. O <code>icon-size</code> é
    o único token de conteúdo com valor fixo por tamanho, então é ele que ancora.
  </div>
</section>

<section>
  <h2>Tokens de cor</h2>
  <div class="scroller">
    <table>
      <thead><tr><th>Token do Avatar</th><th>Aponta para</th><th>Claro</th><th>Escuro</th></tr></thead>
      <tbody>{avatar_token_rows()}</tbody>
    </table>
  </div>
  <div class="note" style="margin-top:16px">
    <b>Três tokens de cor, não nove</b>
    O tamanho não muda cor nenhuma — os três tamanhos usam o mesmo fundo e a mesma tinta.
    Nove tokens repetindo o mesmo valor seriam nove lugares para o mesmo valor divergir por
    engano.
  </div>
  <div class="note">
    <b><code>avatar-label</code> e <code>avatar-icon</code> resolvem igual, e mesmo assim são
    dois tokens</b>
    Os dois apontam para <code>text-primary</code> hoje, então ficam idênticos na tela. Mas são
    papéis diferentes — um é texto, o outro é tinta de vetor — e foi exatamente por colapsar
    essa distinção que a tinta do ícone tinha ficado presa num token de <i>fundo</i>
    (<code>bg-inverse</code>) até a auditoria pegar. Nomes separados são o que impede a mesma
    armadilha de voltar.
  </div>
  <div class="note">
    <b>{N_AVATAR_TOKENS} tokens no código, 10 variáveis no Figma</b>
    A diferença são as três fontes, que são <i>estilos de texto</i>
    (<code>Label/sm</code>, <code>Heading/xs</code>, <code>Heading/sm</code>) e não variáveis —
    a mesma regra do Icon Button e do Tag.
  </div>
</section>'''


AVATAR_GUIDE = f'''
<section>
  <h2>Quando usar</h2>
  <div class="dd">
    <div class="cell do">
      <span class="lab">Identidade de uma pessoa</span>
      <div class="stage2">{av_person('photo', 'md', 'Maria Silva', 'Autora')}</div>
      <p class="cap">Dizer <b>quem</b> — autor de um comentário, dono de uma tarefa,
      participante de uma conversa.</p>
    </div>
    <div class="cell no">
      <span class="lab">Decoração ao lado de qualquer coisa</span>
      <div class="stage2">{av('icon', 'md')}</div>
      <p class="cap">Avatar sem pessoa por trás é um ícone com fundo redondo. Se não há
      identidade, o componente certo é o <b>Icon</b>.</p>
    </div>
  </div>
</section>

<section>
  <h2>A cadeia decide, você não</h2>
  <p>A regra mais importante do componente, e a que mais some numa implementação apressada: o
  tipo do avatar não é uma preferência de tela, é o resultado de quanto material existe sobre
  aquela pessoa. Invertendo a ordem, a interface fica mostrando um ícone genérico para alguém
  que tem foto.</p>
  <div class="dd" style="margin-top:16px">
    <div class="cell no">
      <span class="lab">Ícone porque é mais discreto</span>
      <div class="stage2">{av_person('icon', 'md', 'Maria Silva', 'Tem foto no perfil')}</div>
      <p class="cap">Escolher o tipo pelo gosto visual joga fora informação que existia.</p>
    </div>
    <div class="cell do">
      <span class="lab">Foto porque existe foto</span>
      <div class="stage2">{av_person('photo', 'md', 'Maria Silva', 'Tem foto no perfil')}</div>
      <p class="cap">E se ela falhar ao carregar, cai sozinha para <b>MS</b> — não para vazio.</p>
    </div>
  </div>
</section>

<section>
  <h2>As regras</h2>

  <div class="rule"><div class="rn">01</div><div>
    <h3>Photo sempre que existir foto real</h3>
    <p>É a opção mais informativa das três. Precedente: Polaris e Material — nenhum promove
    iniciais ou ícone havendo foto.</p></div></div>

  <div class="rule"><div class="rn">02</div><div>
    <h3>Iniciais quando não há foto mas o nome é conhecido</h3>
    <p>Nunca deixar o avatar vazio: as iniciais preservam a estrutura da interface mesmo sem
    imagem. Precedente: Material, literalmente “never leave the avatar blank”.</p></div></div>

  <div class="rule"><div class="rn">03</div><div>
    <h3>Icon como último recurso — sem foto e sem nome</h3>
    <p>Anônimo, convidado, usuário removido, placeholder de sistema. Precedente: Polaris usa
    esse padrão exato.</p></div></div>

  <div class="rule"><div class="rn">04</div><div>
    <h3>A cadeia é fixa: Photo → Iniciais → Icon, sem pular etapa</h3>
    <p>Imagem que falha ou demora cai para Iniciais; ausência de nome cai para Icon. Precedente:
    Polaris — a URL cai para iniciais se a imagem falhar ou demorar a carregar. No código isso
    é uma troca de nó filho, com o involucro parado.</p></div></div>

  <div class="rule"><div class="rn">05</div><div>
    <h3>Um tamanho só por grupo</h3>
    <p>Lista, tabela ou empilhamento usam tamanho fixo do início ao fim. O tamanho descreve o
    contexto, não a importância de cada pessoa.</p></div></div>

  <div class="rule"><div class="rn">06</div><div>
    <h3>Stack e indicador de presença não são variantes</h3>
    <p>Ficaram fora desta versão. Quando vierem, cada um é uma composição <b>sobre</b> o Avatar
    — anel de contorno na cor da tela para o stack, badge para presença — nunca uma variante do
    componente. Precedente: Primer, no AvatarStack.</p></div></div>

  <div class="rule"><div class="rn">07</div><div>
    <h3>O tamanho sai do papel na tela, nunca do gosto</h3>
    <p><code>sm</code> em linha (tabela, lista, comentário), <code>md</code> como padrão (card,
    navegação), <code>lg</code> para destaque (topo de perfil). Precedentes: Polaris para o
    menor e o padrão, Material e Primer para o maior.</p></div></div>

  <div class="rule"><div class="rn">08</div><div>
    <h3>Iniciais: no máximo 2 caracteres, maiúsculas</h3>
    <p>Nome e sobrenome, ou as duas primeiras letras se só houver um nome. Nunca minúscula,
    número solto ou emoji. Se o cálculo produzir mais de duas, corte para as duas relevantes —
    contar com o recorte da caixa não é regra de conteúdo.</p></div></div>

  <div class="rule"><div class="rn">09</div><div>
    <h3>O glifo do tipo Icon é fixo em <code>user</code></h3>
    <p>Diferente do Button e do Icon Button, que aceitam qualquer ícone da biblioteca, aqui o
    papel é único: “pessoa sem informação”. Nenhum sistema de referência trata o glifo do avatar
    como escolha livre.</p></div></div>

  <div class="rule"><div class="rn">10</div><div>
    <h3>Imagem quebrada cai para Iniciais ou Icon — nunca para caixa vazia</h3>
    <p>É comportamento de quem implementa, não geometria: o Figma só modela os três tipos
    finais, e esta regra é o que os amarra em sequência. O fundo <code>avatar-bg</code> é o chão
    enquanto a imagem carrega, então nunca há um buraco na interface.</p></div></div>

  <div class="rule"><div class="rn">11</div><div>
    <h3>Sem estado de carregamento nesta versão</h3>
    <p>Sem skeleton, sem shimmer — consequência de o Avatar ser estático. Se carregamento
    assíncrono virar necessidade real, é escopo novo a auditar, não algo a improvisar no
    código.</p></div></div>

  <div class="rule"><div class="rn">12</div><div>
    <h3>Avatar clicável é um acionável por fora</h3>
    <p>Ele nunca entra na ordem de tabulação e nunca ganha <code>tabindex</code> ou
    <code>role="button"</code> por conta própria. Quem precisa de avatar clicável embrulha num
    elemento acionável que já tem anel de foco — Icon Button ou link. Sem essa regra escrita,
    alguém cola o avatar dentro de um <code>button</code> e o anel simplesmente não existe.</p>
    </div></div>
</section>

<section>
  <h2>Fora de escopo, de propósito</h2>
  <div class="anat">
    <div><b>Forma quadrada</b><span><b>Divergência consciente do Primer</b>, onde círculo é pessoa e quadrado é organização, time ou bot. O AL não tem conceito de organização em lugar nenhum — criar a forma antes do conceito inventa um estado que nada usa.</span></div>
    <div><b>Stack (+N)</b><span>Composição sobre o Avatar, não variante dele. Precisa de um anel na cor da tela para separar avatares vizinhos — um token a mais, quando a hora chegar.</span></div>
    <div><b>Indicador de presença</b><span>A bolinha de online/offline é um badge sobreposto, e badge posicionado é outro componente.</span></div>
    <div><b>Cor de fundo por pessoa</b><span>Vários sistemas derivam uma cor do nome. Aqui o fundo é um só: cor derivada de string escapa do portão de contraste por definição.</span></div>
    <div><b>Avatar interativo</b><span>Sem hover, sem foco, sem disabled. Avatar é conteúdo; conteúdo não desabilita — a mesma decisão do Tag.</span></div>
  </div>
</section>'''


AVATAR_A11Y_TAB = f'''
<section>
  <h2>Dois pisos, no mesmo par de cor</h2>
  <p>As iniciais são <b>texto</b>: critério 1.4.3, piso 4,5:1. O glifo do tipo Icon é
  <b>não-textual</b>: critério 1.4.11, piso 3:1. Os dois resolvem no mesmo hex hoje, porque os
  dois apontam para <code>text-primary</code> — mas cada um é medido contra o piso que é dele,
  nunca contra o mais fácil.</p>
  <p style="margin-top:12px">O resultado é o portão mais curto do sistema até agora: o fundo do
  Avatar <b>não varia</b>. É sempre <code>avatar-bg</code>, sólido, nos três tipos — inclusive
  no Photo, onde ele é o chão enquanto a imagem carrega. Sem tipo × status a multiplicar,
  sobram quatro medições.</p>
  <div class="stats">
    <div class="stat hl"><b>{N_AV_MEDIDAS}</b><span>combinações medidas</span></div>
    <div class="stat"><b>{AVATAR_A11Y['fails']}</b><span>reprovas</span></div>
    <div class="stat"><b>0</b><span>exceções</span></div>
    <div class="stat"><b>9,98:1</b><span>pior margem</span></div>
  </div>
</section>

<section>
  <h2>Contraste contra o fundo efetivo</h2>
  <div class="scroller" style="margin-top:20px"><table>
    <thead><tr><th>Tema</th><th>Papel</th><th></th><th>Cor / fundo</th><th>Razão</th><th>Piso</th><th></th></tr></thead>
    <tbody>{avatar_a11y_rows()}</tbody>
  </table></div>
</section>

<section>
  <h2>O contrato de marcação</h2>
  <p>Este é o coração da acessibilidade do Avatar, e é o que nenhum portão de CSS alcança — ele
  vive na marcação que quem consome escreve. O <code>a11y.py</code> o cobra lendo o HTML que
  este site emite: <b>{AVATAR_A11Y['markupChecked'] or 0} elementos</b> <code>.al-avatar</code>
  nesta página, nenhum fora do contrato.</p>
  <div class="dd" style="margin-top:16px">
    <div class="cell do">
      <span class="lab">Ao lado do nome → decorativo</span>
      <div class="stage2">{av_person('photo', 'md', 'Maria Silva', 'Comentou há 2 horas')}</div>
      <p class="cap"><code>aria-hidden="true"</code> no involucro. O nome já está escrito na
      tela: anunciá-lo de novo pelo avatar é ruído duplicado. Precedente: PatternFly — imagem é
      decorativa se puder sair sem afetar a informação da página; o Spectrum tem um
      <code>is-decorative</code> explícito para isso.</p>
    </div>
    <div class="cell do">
      <span class="lab">Sozinho → carrega o sentido</span>
      <div class="stage2">{av('photo', 'md', 'Maria Silva', PHOTO_B, decorativo=False)}</div>
      <p class="cap"><code>role="img"</code> + <code>aria-label="Maria Silva"</code>. Sem nome
      escrito ao lado, o avatar É a informação. Precedente: o Carbon levou issue de
      acessibilidade exatamente por avatar de usuário sem alternativa textual.</p>
    </div>
  </div>
  <div class="anat" style="margin-top:16px">
    <div><b>Um dos dois, nunca os dois</b><span><code>aria-hidden</code> e <code>role="img"</code> juntos são contraditórios, e nenhum dos dois deixa o avatar mudo. O portão reprova os dois casos.</span></div>
    <div><b><code>alt=""</code> sempre na foto</b><span>O nome mora no involucro. Um <code>alt</code> preenchido faria o leitor de tela anunciar a pessoa duas vezes.</span></div>
    <div><b>Ícone sempre decorativo</b><span><code>aria-hidden</code> e <code>focusable="false"</code> no <code>svg</code>: o sentido, se houver, está no involucro — nunca no glifo.</span></div>
    <div><b>Sem nome inventado no Icon</b><span>O tipo Icon nunca recebe nome de pessoa. Ou é decorativo, ou leva um rótulo genérico como “Usuário sem foto”.</span></div>
  </div>
</section>

<section>
  <h2>O que não existe aqui, e por quê</h2>
  <p>Duas seções que todo outro componente acionável do AL tem estão <b>declaradamente vazias</b>
  no portão deste — e isso é resultado, não esquecimento.</p>
  <div class="anat" style="margin-top:16px">
    <div><b>Sem anel de foco</b><span>O Avatar nunca recebe foco, então não há anel para medir. Quem recebe é o acionável que o embrulha, e o anel é dele.</span></div>
    <div><b>Sem alvo de toque</b><span>O piso de 24px do WCAG 2.5.8 vale para controle. O Avatar não é um — não há o que medir.</span></div>
  </div>
  <div class="note" style="margin-top:16px">
    <b>Alto contraste forçado: decisão em aberto, registrada</b>
    No modo de alto contraste do sistema operacional o fundo é substituído, e o círculo perde o
    limite visível. O Tag recolore uma borda que <b>já existia</b>; o Avatar não tem borda em
    variante nenhuma, e acrescentar uma só nesse modo seria inventar geometria fora do Figma.
    Fica medido e anotado aqui em vez de resolvido às pressas.
  </div>
</section>'''


# ═══════════════════════════════════════════════════════════════ Select · abas
# 7 estados, um tamanho, sem variante. O que varia e quase sempre so a borda -
# por isso a tabela de token nao tem coluna de variante, diferente do Tag.
SELECT_STATES = [
    ('default', 'Default'), ('hover', 'Hover'), ('active', 'Active'),
    ('focus', 'Focus'), ('error', 'Error'), ('focus-error', 'Focus + Error'),
    ('disabled', 'Disabled'),
]

SELECT_UFS = ['Acre', 'Bahia', 'Ceará', 'Minas Gerais', 'Paraná', 'São Paulo']

SELECT_CHEVRON = al_icon('chevron-down', cls='al-icon al-select__chevron')


def sel(cid, rotulo='Estado', *, opcional=False, apoio=None, erro=None,
        disabled=False, valor=None, sim=None, placeholder='Selecione o estado'):
    """Um Select real. `sim` escreve na MESMA variavel privada que o select.css
    usa para hover e active - nao e estilo paralelo, e o mecanismo do
    componente. So existe porque esses dois estados so vivem sob o ponteiro."""
    attrs = [f'id="{cid}"', 'class="al-select__field"']
    if erro:
        attrs.append('aria-invalid="true"')
    if disabled:
        attrs.append('disabled')
    if apoio or erro:
        attrs.append(f'aria-describedby="{cid}-help"')
    if sim:
        attrs.append(f'style="--_border-state: var(--al-select-border-{sim})"')

    opcoes = [f'<option value="" disabled{"" if valor else " selected"}>{placeholder}</option>']
    for uf in SELECT_UFS:
        opcoes.append(f'<option value="{uf}"{" selected" if valor == uf else ""}>{uf}</option>')

    marca = '<span class="al-select__optional">(Opcional)</span>' if opcional else ''
    msg = erro or apoio
    linha = f'<p class="al-select__help" id="{cid}-help">{msg}</p>' if msg else ''

    return (f'<div class="al-select">'
            f'<div class="al-select__labelrow">'
            f'<label class="al-select__label" for="{cid}">{rotulo}</label>{marca}</div>'
            f'<div class="al-select__control">'
            f'<select {" ".join(attrs)}>{"".join(opcoes)}</select>{SELECT_CHEVRON}</div>'
            f'{linha}</div>')


def select_specimens():
    """Os sete estados parados, lado a lado. Hover e Active levam a nota de que
    sao escritos direto - a vitrine nao pode fingir que o ponteiro esta la."""
    cells = []
    for i, (slug, nome) in enumerate(SELECT_STATES):
        kw = dict(cid=f'sp-{slug}', rotulo='Estado')
        if slug in ('hover', 'active'):
            kw['sim'] = slug
        if slug in ('error', 'focus-error'):
            kw['erro'] = 'Escolha um estado para continuar'
        if slug == 'disabled':
            kw['disabled'] = True
            kw['opcional'] = True
        nota = {
            'default': 'O repouso. A borda aqui é a exceção de contraste declarada.',
            'hover': 'Só existe sob o ponteiro: a variável privada foi escrita direto.',
            'active': 'Só o instante do botão pressionado — mesma escrita direta.',
            'focus': 'Tabule até o campo: o anel aparece. Por clique também, ver Acessibilidade.',
            'error': 'Vem de <code>aria-invalid="true"</code>, nunca de uma classe.',
            'focus-error': 'Focado, o anel troca para vinho — <code>focusRing.error</code>.',
            'disabled': 'Atributo nativo <code>disabled</code>: o Tab pula sozinho.',
        }[slug]
        cells.append(f'<div class="cell"><span class="lab" '
                     f'style="color:var(--al-text-secondary)">{nome}</span>'
                     f'<div class="stage2" style="display:block">{sel(**kw)}</div>'
                     f'<p class="cap">{nota}</p></div>')
    return '<div class="dd">' + ''.join(cells) + '</div>'


def select_token_rows():
    """So os tokens de cor. Um estado por linha, sem coluna de variante."""
    rows = []
    for name in SELECT['alias']:
        res = SELECT['resolved'].get(name)
        if not isinstance(res, dict) or 'light' not in res:
            continue
        lt = res['light']
        sw = (f'<span class="chip sm" style="background:{lt}"></span>'
              if isinstance(lt, str) and lt.startswith('#') else '')
        rows.append(f'<tr><td class="tok">--al-{name}</td>'
                    f'<td class="tok dim">{SELECT["alias"][name]}</td>'
                    f'<td class="tok dim">{sw}{lt}</td></tr>')
    return '\n'.join(rows)


def select_geo_rows():
    rows = []
    for role in ['padding-x', 'padding-y', 'gap', 'radius', 'border-width', 'icon-size']:
        name = f'select-{role}'
        rows.append(f'<tr><td class="tok">--al-{name}</td>'
                    f'<td class="tok dim">{SELECT["alias"][name]}</td>'
                    f'<td class="num">{SELECT["resolved"][name]}px</td></tr>')
    for role in ['font', 'label-font', 'optional-font', 'help-font']:
        name = f'select-{role}'
        res = SELECT['resolved'][name]
        rows.append(f'<tr><td class="tok">--al-{name}</td>'
                    f'<td class="tok dim">{SELECT["alias"][name]}</td>'
                    f'<td class="num">{res[1]}/{res[2]} · peso {res[3]}</td></tr>')
    return '\n'.join(rows)


def select_a11y_rows(papeis):
    """Uma linha por medicao, filtrada pelo papel. Excecao declarada aparece
    como excecao, nunca como reprova e nunca escondida."""
    out = []
    for r in SELECT_A11Y['rows']:
        if r['papel'] not in papeis:
            continue
        if r['pass']:
            verdict = '<span class="pass">passa</span>'
        elif r['exc']:
            verdict = '<span class="exc">exceção</span>'
        else:
            verdict = '<span class="fail">reprova</span>'
        chips = (f'<span class="chip sm" style="background:{r["fgHex"]}"></span>'
                 f'<span class="chip sm" style="background:{r["bgHex"]}"></span>')
        out.append(
            f'<tr><td class="tok dim">{"claro" if r["theme"] == "light" else "escuro"}</td>'
            f'<td class="name">{r["state"]}</td>'
            f'<td class="tok dim">{r["papel"]}</td><td class="chipcell">{chips}</td>'
            f'<td class="tok dim">--al-{r["token"]}</td>'
            f'<td class="tok dim">{r["contra"]}</td>'
            f'<td class="num strong">{r["ratio"]:.2f}:1</td>'
            f'<td class="num dim">{r["floor"]}:1</td><td>{verdict}</td></tr>')
    return '\n'.join(out)


N_SEL_MEDIDAS = len(SELECT_A11Y['rows'])
N_SEL_EXC = sum(SELECT_A11Y['exceptions'].values())
N_SEL_PASSA = N_SEL_MEDIDAS - N_SEL_EXC
SEL_LAYER = {d['theme']: d for d in SELECT_A11Y['layerEffect']}

TH_SELECT = ('<div class="th-select" aria-hidden="true">'
             '<span class="th-select__field">Selecione a opção'
             + al_icon('chevron-down') + '</span></div>')

SELECT_OVERVIEW = f'''
<section>
  <h2>Playground</h2>
  <div class="pg">
    <div class="stage" id="select-stage">{sel('pg-select')}</div>

    <div class="controls" id="select-controls">
      <div class="ctl"><span class="ctl-name">Estado</span>{seg('selstate', [('rest', 'Repouso'), ('error', 'Erro'), ('disabled', 'Desabilitado')], 'rest')}</div>
      <div class="ctl"><span class="ctl-name">Valor</span>{seg('selvalue', [('none', 'Placeholder'), ('picked', 'Escolhido')], 'none')}</div>
      <div class="ctl"><span class="ctl-name">Obrigatoriedade</span>{seg('selopt', [('req', 'Obrigatório'), ('opt', 'Opcional')], 'req')}</div>
      <div class="ctl"><span class="ctl-name">Texto de apoio</span>{seg('selhelp', [('off', 'Sem'), ('on', 'Com')], 'off')}</div>
      <div class="ctl"><span class="ctl-name">Tema</span>{seg('seltheme', [('auto', 'Do sistema'), ('light', 'Claro'), ('dark', 'Escuro')], 'auto')}</div>
      <div class="ctl"><label for="select-label" class="ctl-name">Rótulo</label>
        <input class="txt" id="select-label" type="text" value="Estado" maxlength="28"></div>
    </div>

    <div class="codewrap">
      <div class="codebar"><span>Marcação</span>
        <button type="button" class="copy" id="select-copy">Copiar</button></div>
      <pre><code id="select-code"></code></pre>
    </div>
  </div>
  <p style="margin-top:14px; font-size:13.5px; color:var(--al-text-secondary)">
    O campo acima é o componente real: esta página carrega o mesmo
    <code>select.css</code> que vai para produção. Tabule até ele para ver o anel, e repare que
    o estado de erro nasce de <code>aria-invalid</code> na marcação — não há classe de erro
    neste componente, de propósito: se a cor viesse de uma classe, ela poderia divergir do que
    o leitor de tela anuncia.
  </p>
</section>

<section>
  <h2>É o nativo, e isso é uma decisão</h2>
  <div class="dd">
    <div class="cell">
      <span class="lab" style="color:var(--al-text-secondary)">O que entregamos</span>
      <div class="stage2" style="display:block">{sel('ov-nativo', 'Estado', apoio='Onde a nota será emitida')}</div>
      <p class="cap">O gatilho fechado. A lista aberta é desenhada pelo navegador e pelo sistema
      operacional — por isso não há token de painel, de opção nem de item selecionado. Precedente:
      é a distinção que o <b>Carbon</b> faz entre <i>Select</i> (nativo) e
      <i>Dropdown</i>/<i>ComboBox</i> (desenhados).</p>
    </div>
    <div class="cell">
      <span class="lab" style="color:var(--al-text-secondary)">O que isso compra</span>
      <div class="stage2" style="display:block">{sel('ov-mobile', 'Transportadora', opcional=True)}</div>
      <p class="cap">Teclado, leitor de tela e o seletor nativo do celular, sem uma linha de
      JavaScript. O preço é não controlar a lista aberta — e o Carbon recomenda exatamente esse
      troco quando a experiência é de formulário e muito usada em mobile.</p>
    </div>
  </div>
</section>

<section>
  <h2>Os sete estados</h2>
  {select_specimens()}
</section>

<section>
  <h2>Num formulário de verdade</h2>
  <div class="cell" style="max-width:none">
    <div class="stage2" style="display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:20px; align-items:start">
      {sel('fm-uf', 'Estado', apoio='Onde a nota será emitida')}
      {sel('fm-frete', 'Tipo de frete', opcional=True)}
      {sel('fm-transp', 'Transportadora', erro='Escolha uma transportadora para continuar')}
      {sel('fm-cidade', 'Cidade', disabled=True)}
    </div>
    <p class="cap">Quatro campos lado a lado, do jeito que o componente vai viver. Tabule por
    eles: o <b>Cidade</b> é pulado sozinho, sem <code>tabindex</code> — é o atributo nativo
    <code>disabled</code> fazendo o trabalho.</p>
  </div>
</section>'''

SELECT_SPECS = f'''
<section>
  <h2>Anatomia</h2>
  <div class="anat">
    <div><b>Rótulo</b><span><code>&lt;label for&gt;</code> ligado ao <code>id</code> do campo. Sempre visível — e a regra que sustenta a exceção de contraste da borda.</span></div>
    <div><b>Marca “(Opcional)”</b><span>Uma entrelinha menor que o rótulo, em <code>text-secondary</code>. O AL marca o <b>opcional</b>: quem não tem a marca é obrigatório.</span></div>
    <div><b>Campo</b><span><code>&lt;select&gt;</code> nativo com <code>appearance: none</code>, para a seta do navegador sair e a nossa entrar.</span></div>
    <div><b>Seta</b><span>Irmã do campo, não filha: <code>&lt;select&gt;</code> só aceita <code>&lt;option&gt;</code>. Posicionada por cima, com <code>pointer-events: none</code> devolvendo o clique.</span></div>
    <div><b>Texto de apoio</b><span>Opcional, e o mesmo slot da mensagem de erro — no erro um substitui o outro, e volta quando o erro é resolvido.</span></div>
  </div>
</section>

<section>
  <h2>A altura é consequência</h2>
  <p>Não existe <code>height</code> neste componente. O campo fecha em
  <b>{SELECT['derived']['field-height']}px</b> porque é <code>padding-y</code> × 2 mais a
  entrelinha do texto, com a borda de 1px descontada do padding — a mesma convenção do Button e
  do Tag. A caixa inteira soma <b>{SELECT['derived']['total-height']}px</b>, e
  <b>{SELECT['derived']['total-height-with-help']}px</b> quando o texto de apoio aparece.</p>
  <p style="margin-top:12px">Tokenizar a altura seria guardar a mesma decisão em dois lugares,
  com duas chances de divergir. E a borda existe em <b>todos</b> os estados — por isso o campo
  nunca “pula” quando um estado troca a cor dela.</p>
  <div class="stats">
    <div class="stat hl"><b>{N_SELECT_TOKENS}</b><span>tokens, todos alias</span></div>
    <div class="stat"><b>0</b><span>valores soltos</span></div>
    <div class="stat"><b>7</b><span>estados</span></div>
    <div class="stat"><b>1</b><span>tamanho, por escolha</span></div>
  </div>
</section>

<section>
  <h2>Cor — um token por papel e estado</h2>
  <div class="scroller" style="margin-top:20px"><table>
    <thead><tr><th>Token</th><th>Aponta para</th><th>Resolve (claro)</th></tr></thead>
    <tbody>{select_token_rows()}</tbody>
  </table></div>
  <div class="note" style="margin-top:16px">
    <b>A seta não herda a cor do texto — e é o único componente assim</b>
    No Button e no Tag o ícone é <code>currentColor</code> e acerta todos os estados sozinho.
    Aqui não dá: no repouso o texto do campo é <code>text-placeholder</code> e a seta é
    <code>text-primary</code>, duas cores na mesma caixa. Daí existirem
    <code>select-icon</code> e <code>select-icon-disabled</code>.
  </div>
</section>

<section>
  <h2>Geometria e tipografia</h2>
  <div class="scroller" style="margin-top:20px"><table>
    <thead><tr><th>Token</th><th>Aponta para</th><th>Valor</th></tr></thead>
    <tbody>{select_geo_rows()}</tbody>
  </table></div>
</section>

<section>
  <h2>Precedência por variável, não por especificidade</h2>
  <p>A borda é <code>var(--_border-force, var(--_border-state))</code>. Os estados de interação
  escrevem em <code>--_border-state</code>; erro e desabilitado escrevem em
  <code>--_border-force</code>, que vence sempre por ser <b>outra propriedade</b> — não por ter
  seletor mais pesado.</p>
  <p style="margin-top:12px">Sem isso haveria um bug silencioso:
  <code>:hover:not(:disabled)</code> pesa (0,3,0) e <code>[aria-invalid="true"]</code> pesa
  (0,2,0), então o campo reprovado ficaria cinza ao passar o mouse. Entre erro e desabilitado
  decide a ordem do arquivo — desabilitado vem depois e ganha, que é o correto.</p>
</section>'''

SELECT_GUIDE = f'''
<section>
  <h2>Quando usar</h2>
  <div class="anat">
    <div><b>A partir de 4 opções</b><span>Com 3 ou menos, radio: o Select esconde as opções atrás de um clique, e abaixo de 4 o custo de esconder é maior que o de mostrar. <i>Polaris fixa 4+; Carbon desaconselha dropdown com duas.</i></span></div>
    <div><b>Escolha única</b><span>Não há múltipla escolha no AL. <i>Carbon separa Select de Dropdown e ComboBox.</i></span></div>
    <div><b>Nunca para disparar ação</b><span>Ele coleta um dado num formulário. Menu que executa, filtra ou ordena é outro componente. <i>Carbon.</i></span></div>
    <div><b>Acima de ~15 opções, atrapalha</b><span>O nativo não tem busca. Não é impedimento, é limite conhecido: essa demanda abre ComboBox, não estica o Select.</span></div>
  </div>
</section>

<section>
  <h2>Rótulo e a marca de opcional</h2>
  <div class="dd">
    <div class="cell">
      <span class="lab" style="color:var(--al-text-success)">Faça</span>
      <div class="stage2" style="display:block">{sel('gd-ok', 'Estado', opcional=True)}</div>
      <p class="cap">Rótulo visível sempre, curto, em sentence case, descrevendo <b>o dado</b> —
      “Estado”, não “Selecione o estado”. A instrução de escolher já está no placeholder.
      A marca “(Opcional)” assinala a minoria: quem não tem a marca é obrigatório.</p>
    </div>
    <div class="cell">
      <span class="lab" style="color:var(--al-text-danger)">Não faça</span>
      <div class="stage2" style="display:block">{sel('gd-bad', 'Estado', placeholder='Estado')}</div>
      <p class="cap">Usar o placeholder como rótulo. Ele desaparece no instante em que alguém
      escolhe algo, e quem voltar ao formulário perdeu a única pista do que o campo pede.
      <i>Polaris exige o label mesmo quando visualmente oculto.</i></p>
    </div>
  </div>
  <div class="note" style="margin-top:16px">
    <b>O AL marca o opcional, não o obrigatório</b>
    É a escola oposta à do asterisco do Polaris, e ela ganha quando a maioria dos campos de um
    formulário é obrigatória — marca-se a minoria. Consequência: <b>não existe token nem estilo
    de “obrigatório”</b>, porque a ausência da marca é o obrigatório, e ausência não se tokeniza.
  </div>
</section>

<section>
  <h2>Placeholder e opção padrão</h2>
  <div class="anat">
    <div><b>Havendo um padrão que serve à maioria, ele já vem selecionado</b><span>Sem placeholder. Placeholder obrigatório força todo mundo a um clique que a maioria não precisaria dar. <i>NN/g.</i></span></div>
    <div><b>Sem padrão bom, descreva</b><span>“Selecione o estado”, não “Selecione…”.</span></div>
    <div><b>É uma <code>&lt;option&gt;</code>, não um atributo</b><span><code>value=""</code>, <code>disabled</code> e <code>selected</code> — <code>&lt;select&gt;</code> não tem placeholder nativo. É também o que aciona a troca de cor do texto.</span></div>
    <div><b><code>optgroup</code> pode</b><span>O nativo agrupa de graça e não há nada para desenhar do nosso lado.</span></div>
  </div>
</section>

<section>
  <h2>Apoio e erro dividem o mesmo slot</h2>
  <div class="dd">
    <div class="cell">
      <span class="lab" style="color:var(--al-text-secondary)">Sem erro</span>
      <div class="stage2" style="display:block">{sel('gd-help', 'Estado', apoio='Onde a nota será emitida')}</div>
      <p class="cap">O apoio explica o campo.</p>
    </div>
    <div class="cell">
      <span class="lab" style="color:var(--al-text-secondary)">Com erro</span>
      <div class="stage2" style="display:block">{sel('gd-err', 'Estado', erro='Escolha um estado para emitir a nota')}</div>
      <p class="cap">O erro <b>substitui</b> o apoio, e volta quando for resolvido.
      <i>Spectrum documenta exatamente esse comportamento.</i> Por isso os dois textos precisam
      carregar a mesma informação essencial — senão a instrução some justamente na hora em que
      a pessoa mais precisa dela.</p>
    </div>
  </div>
  <div class="anat" style="margin-top:16px">
    <div><b>O erro diz como corrigir</b><span>“Escolha um estado para continuar”, não “Campo inválido”. <i>Spectrum.</i></span></div>
    <div><b>O erro aparece depois</b><span>Depois do envio ou de a pessoa sair do campo — nunca enquanto ela ainda escolhe. Marcar de vermelho um campo que ela não terminou de preencher é acusá-la de um erro que não cometeu.</span></div>
  </div>
</section>

<section>
  <h2>Fora de escopo, de propósito</h2>
  <div class="anat">
    <div><b>Múltipla escolha, busca e filtro</b><span>Abre ComboBox, não estica o Select.</span></div>
    <div><b>Um tamanho só (48px)</b><span>Escolha declarada, como o <code>lg</code> que ficou de fora do Button.</span></div>
    <div><b>Ícone à esquerda e read-only</b><span>Não foram desenhados. Campo que precisa ser lido mas não editado usa <code>disabled</code> hoje, com a limitação conhecida de que o valor não pode ser copiado. <i>Spectrum resolve com read-only; o AL ainda não tem.</i></span></div>
    <div><b>A lista aberta</b><span>É do navegador. Não estilizar <code>&lt;option&gt;</code>, altura de item nem scroll: varia por sistema operacional e quebra sem avisar.</span></div>
  </div>
</section>'''

SELECT_A11Y_TAB = f'''
<section>
  <h2>O fundo efetivo muda com a camada</h2>
  <p>O portão mede <b>combinação renderizada</b> — cada papel contra o fundo que ele realmente
  tem na tela, não contra um par de token no vácuo. Duas consequências que a camada de tokens
  não podia enxergar sozinha:</p>
  <p style="margin-top:12px"><b>A borda troca de vizinho quando o campo recebe foco.</b> Em
  repouso ela toca a página — que pode ser <code>bg-canvas</code> ou
  <code>bg-surface-raised</code>, se o campo estiver dentro de um card, e o portão mede a pior
  das duas. Com foco, o anel desenha um respiro de 2px em <code>bg-canvas</code> colado nela, e
  a vizinha externa passa a ser sempre <code>bg-canvas</code>.</p>
  <div class="scroller" style="margin-top:16px"><table>
    <thead><tr><th>Tema</th><th>Borda em repouso</th><th>Borda com foco</th></tr></thead>
    <tbody>
      <tr><td class="tok dim">claro</td><td class="num">{SEL_LAYER['light']['rest']:.2f}:1</td><td class="num strong">{SEL_LAYER['light']['focused']:.2f}:1</td></tr>
      <tr><td class="tok dim">escuro</td><td class="num">{SEL_LAYER['dark']['rest']:.2f}:1</td><td class="num strong">{SEL_LAYER['dark']['focused']:.2f}:1</td></tr>
    </tbody>
  </table></div>
  <p style="margin-top:12px">Ou seja: no momento em que o campo está em uso, a borda passa dos
  3:1 sozinha. A exceção declarada vale só para o repouso.</p>
  <p style="margin-top:12px"><b>A cor do anel sai do próprio <code>box-shadow</code>.</b> O
  portão lê o último hex da sombra composta — a cor que de fato pinta o anel. Não há definição
  paralela para divergir do CSS.</p>
  <div class="stats">
    <div class="stat hl"><b>{N_SEL_MEDIDAS}</b><span>combinações medidas</span></div>
    <div class="stat"><b>{N_SEL_PASSA}</b><span>passam</span></div>
    <div class="stat"><b>{N_SEL_EXC}</b><span>em exceção declarada</span></div>
    <div class="stat"><b>{SELECT_A11Y['fails']}</b><span>reprovas</span></div>
  </div>
</section>

<section>
  <h2>As duas exceções, nomeadas</h2>
  <div class="note">
    <b>Borda em repouso abaixo de 3:1 — decisão consciente</b>
    <code>border-default</code> dá {SEL_LAYER['light']['rest']:.2f}:1 no claro e
    {SEL_LAYER['dark']['rest']:.2f}:1 no escuro, abaixo do piso do 1.4.11. O critério não falha
    quando a borda não é o único meio de perceber o componente — e aqui não é: o campo tem
    rótulo visível acima e texto dentro. Hover, active, foco e erro passam todos. <b>É por isso
    que “nunca use o Select sem rótulo visível” é regra de uso, e não sugestão:</b> é ela que
    sustenta esta exceção.
  </div>
  <div class="note" style="margin-top:16px">
    <b>Disabled abaixo de AA — isenção do 1.4.3</b>
    Rótulo, texto e seta ficam entre 1,59:1 e 2,19:1. O WCAG 1.4.3 isenta componente inativo, e
    subir esse contraste faz o desabilitado parecer clicável. Mesma exceção permanente que o
    Button e o Tag já carregam.
  </div>
</section>

<section>
  <h2>Borda e anel — o não-textual, piso 3:1</h2>
  <div class="scroller" style="margin-top:20px"><table>
    <thead><tr><th>Tema</th><th>Estado</th><th>Papel</th><th></th><th>Token</th><th>Medido contra</th><th>Razão</th><th>Piso</th><th></th></tr></thead>
    <tbody>{select_a11y_rows(['borda', 'anel de foco', 'seta'])}</tbody>
  </table></div>
</section>

<section>
  <h2>Texto — piso 4,5:1</h2>
  <div class="scroller" style="margin-top:20px"><table>
    <thead><tr><th>Tema</th><th>Estado</th><th>Papel</th><th></th><th>Token</th><th>Medido contra</th><th>Razão</th><th>Piso</th><th></th></tr></thead>
    <tbody>{select_a11y_rows(['rotulo', 'marca opcional', 'placeholder', 'valor', 'apoio', 'texto'])}</tbody>
  </table></div>
</section>

<section>
  <h2>O contrato de marcação</h2>
  <p>Num campo de formulário quase tudo que dá errado é <b>marcação</b>, não estilo — e
  marcação só existe na saída renderizada. Por isso estas cinco regras não estão escritas numa
  página: elas são medidas por <code>components/select/a11y.py</code> no HTML que este site
  emite, e quebram o build.</p>
  <div class="anat" style="margin-top:16px">
    <div><b>Rótulo ligado</b><span>Todo campo tem <code>id</code>, e existe um <code>&lt;label for&gt;</code> apontando para ele.</span></div>
    <div><b>Erro descrito</b><span>Campo com <code>aria-invalid="true"</code> tem <code>aria-describedby</code>, e o id apontado existe de verdade no documento.</span></div>
    <div><b>Placeholder de verdade</b><span>É a primeira <code>&lt;option value=""&gt;</code> e ela está <code>selected</code>.</span></div>
    <div><b>Seta decorativa</b><span><code>aria-hidden="true"</code> e <code>focusable="false"</code> na própria tag — o sentido mora no rótulo.</span></div>
    <div><b>Sem <code>aria-label</code> redundante</b><span>Havendo rótulo visível, o nome anunciado tem que ser ele.</span></div>
  </div>
  <div class="stats" style="margin-top:16px">
    <div class="stat hl"><b>{SELECT_A11Y['markupChecked']}</b><span>campos conferidos no HTML</span></div>
    <div class="stat"><b>5</b><span>regras por campo</span></div>
    <div class="stat"><b>{'pendente' if SELECT_A11Y['markupPending'] else 'medido'}</b><span>estado do contrato</span></div>
  </div>
  <p style="margin-top:12px; font-size:13.5px; color:var(--al-text-secondary)">
    O portão remove <code>&lt;style&gt;</code> e <code>&lt;script&gt;</code> antes de procurar
    marcação. Sem isso ele media o <code>&lt;select&gt;</code> de exemplo que vive no comentário
    de anatomia do <code>select.css</code> como se fosse um campo de verdade — e
    <b>passava</b>, porque o exemplo está correto. Portão que aprova lendo comentário também
    reprova lendo comentário.
  </p>
</section>

<section>
  <h2>Active e foco: a leitura que caiu na medição</h2>
  <p>A auditoria da etapa 1 fechou que “active é o clique e foco é a chegada por Tab”. A etapa 6
  derrubou isso <b>medindo</b>: cliquei no campo pelo navegador e li o estado computado — o
  Chromium casa <code>:focus-visible</code> num <code>&lt;select&gt;</code> clicado com o mouse,
  porque a plataforma o trata como controle que recebe teclado depois de aberto. O anel aparece
  no clique.</p>
  <p style="margin-top:12px">Não existe seletor de “foco só por teclado” além do próprio
  <code>:focus-visible</code>, e forçar por JavaScript tornaria condicional justamente o
  indicador de foco — a última coisa que se deve condicionar. A leitura foi reinterpretada, sem
  mexer em código: <b>active é o instante em que o botão do mouse está pressionado; foco é o
  estado que permanece</b> enquanto o campo estiver focado, tenha chegado como tiver chegado.
  É o que Carbon, Material e Polaris já usam, e o que sobrevive em qualquer navegador.</p>
</section>'''


# ═══════════════════════════════════════════════════════════════ Checkbox · abas
# 7 estados no Figma, num eixo so. O input nativo produz combinacoes que o Figma
# nao desenha (marcado + foco, marcado + disabled, erro + marcado) - a pagina as
# mostra como o que sao: pintadas pelo codigo, com os tokens aprovados na etapa 3.
CBX_CHECK = al_icon('check', cls='al-icon al-checkbox__check')
CBX_DASH = al_icon('minus', cls='al-icon al-checkbox__dash')


def cbx(cid, rotulo='Receber novidades por e-mail', *, checked=False, indeterminate=False,
        disabled=False, erro=None, sim=None, extra=''):
    """Um Checkbox real. `indeterminate` vira `data-indeterminate` e o JS da pagina
    faz `el.indeterminate = true` - o atributo HTML nao existe (regra 8).
    `sim` escreve nas MESMAS variaveis privadas que o checkbox.css usa para o
    hover, o unico estado que so vive sob o ponteiro."""
    attrs = [f'id="{cid}"', 'class="al-checkbox__input"', 'type="checkbox"']
    if checked:
        attrs.append('checked')
    if disabled:
        attrs.append('disabled')
    if indeterminate:
        attrs.append('data-indeterminate')
    if erro:
        attrs.append('aria-invalid="true"')
        attrs.append(f'aria-describedby="{erro}"')
    lab_style = ''
    if sim == 'hover':
        attrs.append('style="--_bg-state: var(--al-checkbox-bg-hover); '
                     '--_border-state: var(--al-checkbox-border-hover)"')
    if sim == 'error':
        # so para o "Nao faca": o visual do erro SEM aria-invalid, porque o
        # exemplo e justamente um erro que nao foi descrito em texto
        attrs.append('style="--_border-force: var(--al-checkbox-border-error)"')
        lab_style = ' style="color: var(--al-checkbox-label-error)"'
    if extra:
        attrs.append(extra)
    return (f'<label class="al-checkbox">'
            f'<span class="al-checkbox__control"><input {" ".join(attrs)}>{CBX_CHECK}{CBX_DASH}</span>'
            f'<span class="al-checkbox__label"{lab_style}>{rotulo}</span></label>')


def cbx_msg(mid, texto):
    """A mensagem de erro e do FORMULARIO, nao do componente (regra 19)."""
    return f'<p class="cbx-formerror" id="{mid}">{texto}</p>'


CBX_STATES = [
    ('default', 'Default', 'O repouso. A borda aqui é a exceção de contraste declarada.',
     dict()),
    ('hover', 'Hover', 'Só existe sob o ponteiro: a variável privada foi escrita direto. '
     'O real vale na linha inteira — passe o mouse no texto dos outros.', dict(sim='hover')),
    ('active', 'Active (marcado)', 'O check é o ícone <code>check</code> da Fundação.',
     dict(checked=True)),
    ('indeterminate', 'Indeterminate', 'Só por JavaScript: <code>input.indeterminate = true</code>. '
     'Não existe atributo HTML.', dict(indeterminate=True, rotulo='Todas as notificações')),
    ('focus', 'Focus', 'Tabule até aqui: anel laranja. Pelo mouse o anel não aparece.', dict()),
    ('error', 'Error', 'Vem de <code>aria-invalid="true"</code>. A mensagem é do formulário, '
     'não do componente.', dict(erro='sp-cbx-error-msg', rotulo='Li e aceito os termos de uso')),
    ('disabled', 'Disabled', 'Atributo nativo <code>disabled</code>: o Tab pula sozinho.',
     dict(disabled=True)),
]

CBX_COMBOS = [
    ('dischk', 'Marcado + disabled', 'Caixa cinza, check em <code>icon-disabled</code> — o único '
     'token sem variante no Figma.', dict(checked=True, disabled=True, rotulo='Alertas de segurança')),
    ('errchk', 'Erro + marcado', 'A caixa segue laranja; só o rótulo avisa. Desmarque e a borda '
     'fica vermelha.', dict(checked=True, erro='sp-cbx-errchk-msg', rotulo='Li e aceito os termos de uso')),
    ('chkfoc', 'Marcado + foco', 'O anel aparece por cima da caixa laranja — ele não depende do '
     'preenchimento.', dict(checked=True)),
]


def checkbox_specimens(lista):
    cells = []
    for slug, nome, nota, kw in lista:
        kw = dict(kw)
        corpo = cbx(f'sp-cbx-{slug}', **kw)
        if kw.get('erro'):
            corpo += cbx_msg(kw['erro'], 'Aceite os termos para continuar.')
        cells.append(f'<div class="cell"><span class="lab" '
                     f'style="color:var(--al-text-secondary)">{nome}</span>'
                     f'<div class="stage2 cbx-stage">{corpo}</div>'
                     f'<p class="cap">{nota}</p></div>')
    return '<div class="dd">' + ''.join(cells) + '</div>'


def checkbox_token_rows():
    rows = []
    for name in CHECKBOX['alias']:
        res = CHECKBOX['resolved'].get(name)
        if not isinstance(res, dict) or 'light' not in res:
            continue
        lt = res['light']
        sw = (f'<span class="chip sm" style="background:{lt}"></span>'
              if isinstance(lt, str) and lt.startswith('#') else '')
        rows.append(f'<tr><td class="tok">--al-{name}</td>'
                    f'<td class="tok dim">{CHECKBOX["alias"][name]}</td>'
                    f'<td class="tok dim">{sw}{lt}</td></tr>')
    return '\n'.join(rows)


def checkbox_geo_rows():
    rows = []
    for role in ['box-size', 'padding', 'gap', 'radius', 'border-width']:
        name = f'checkbox-{role}'
        rows.append(f'<tr><td class="tok">--al-{name}</td>'
                    f'<td class="tok dim">{CHECKBOX["alias"][name]}</td>'
                    f'<td class="num">{CHECKBOX["resolved"][name]}px</td></tr>')
    res = CHECKBOX['resolved']['checkbox-label-font']
    rows.append(f'<tr><td class="tok">--al-checkbox-label-font</td>'
                f'<td class="tok dim">{CHECKBOX["alias"]["checkbox-label-font"]}</td>'
                f'<td class="num">{res[1]}/{res[2]} · peso {res[3]}</td></tr>')
    return '\n'.join(rows)


def checkbox_a11y_rows(papeis):
    out = []
    for r in CHECKBOX_A11Y['rows']:
        if r['papel'] not in papeis:
            continue
        if r['pass']:
            verdict = '<span class="pass">passa</span>'
        elif r['exc']:
            verdict = '<span class="exc">exceção</span>'
        else:
            verdict = '<span class="fail">reprova</span>'
        chips = (f'<span class="chip sm" style="background:{r["fgHex"]}"></span>'
                 f'<span class="chip sm" style="background:{r["bgHex"]}"></span>')
        estado = r['state'] + (' <span class="tok dim">(código)</span>' if r['soNoCodigo'] else '')
        out.append(
            f'<tr><td class="tok dim">{"claro" if r["theme"] == "light" else "escuro"}</td>'
            f'<td class="name">{estado}</td>'
            f'<td class="tok dim">{r["papel"]}</td><td class="chipcell">{chips}</td>'
            f'<td class="tok dim">--al-{r["token"]}</td>'
            f'<td class="tok dim">{r["contra"]}</td>'
            f'<td class="num strong">{r["ratio"]:.2f}:1</td>'
            f'<td class="num dim">{r["floor"]}:1</td><td>{verdict}</td></tr>')
    return '\n'.join(out)


N_CBX_MEDIDAS = len(CHECKBOX_A11Y['rows'])
N_CBX_EXC = sum(CHECKBOX_A11Y['exceptions'].values())
N_CBX_PASSA = N_CBX_MEDIDAS - N_CBX_EXC


def _cbx_borda(state, theme):
    return next(r['ratio'] for r in CHECKBOX_A11Y['rows']
                if r['state'] == state and r['theme'] == theme and r['papel'] == 'borda')


CBX_LAYER = {t: {'rest': _cbx_borda('default', t), 'focused': _cbx_borda('focus', t)}
             for t in ('light', 'dark')}
CBX_DERIVED = CHECKBOX['derived']

TH_CHECKBOX = ('<div class="th-cbx" aria-hidden="true">'
               '<span class="th-cbx__row"><span class="th-cbx__box is-on">' + al_icon('check')
               + '</span>E-mail</span>'
               '<span class="th-cbx__row"><span class="th-cbx__box is-on">' + al_icon('minus')
               + '</span>Notificações</span>'
               '<span class="th-cbx__row"><span class="th-cbx__box"></span>SMS</span></div>')

CHECKBOX_OVERVIEW = f'''
<section>
  <h2>Playground</h2>
  <div class="pg">
    <div class="stage" id="cbx-stage">{cbx('pg-cbx')}</div>

    <div class="controls" id="cbx-controls">
      <div class="ctl"><span class="ctl-name">Valor</span>{seg('cbxvalue', [('off', 'Desmarcado'), ('on', 'Marcado'), ('mixed', 'Misto')], 'off')}</div>
      <div class="ctl"><span class="ctl-name">Estado</span>{seg('cbxstate', [('rest', 'Normal'), ('error', 'Erro'), ('disabled', 'Desabilitado')], 'rest')}</div>
      <div class="ctl"><span class="ctl-name">Tema</span>{seg('cbxtheme', [('auto', 'Do sistema'), ('light', 'Claro'), ('dark', 'Escuro')], 'auto')}</div>
      <div class="ctl"><label for="cbx-label" class="ctl-name">Rótulo</label>
        <input class="txt" id="cbx-label" type="text" value="Receber novidades por e-mail" maxlength="60"></div>
    </div>

    <div class="codewrap">
      <div class="codebar"><span>Marcação</span>
        <button type="button" class="copy" id="cbx-copy">Copiar</button></div>
      <pre><code id="cbx-code"></code></pre>
    </div>
  </div>
  <p style="margin-top:14px; font-size:13.5px; color:var(--al-text-secondary)">
    O checkbox acima é o componente real: esta página carrega o mesmo <code>checkbox.css</code>
    que vai para produção. Clique no texto e não só na caixa — também marca. No erro, a mensagem
    em vermelho abaixo dele <b>não faz parte do componente</b>: é o formulário descrevendo o erro
    em texto, e o componente aponta para ela com <code>aria-describedby</code>.
  </p>
</section>

<section>
  <h2>Pai, filhos e o estado misto</h2>
  <div class="cell" style="max-width:none">
    <fieldset class="stage2 cbx-group">
      <legend>Notificações</legend>
      {cbx('ov-todas', 'Todas as notificações', extra='data-cbx-pai')}
      <div class="cbx-children">
        {cbx('ov-mail', 'E-mail', checked=True, extra='data-cbx-filho')}
        {cbx('ov-sms', 'SMS', checked=True, extra='data-cbx-filho')}
        {cbx('ov-push', 'Notificação no celular', extra='data-cbx-filho')}
      </div>
    </fieldset>
    <p class="cap">Marque e desmarque os filhos: o pai fica <b>marcado</b> com todos,
    <b>vazio</b> com nenhum e <b>misto</b> com alguns. Clicar no pai misto marca todos.
    Ninguém escolhe o misto — ele é consequência. <i>Carbon e Material, com a mesma regra.</i>
    O título do grupo é <code>fieldset</code> e <code>legend</code> nativos: o componente de
    grupo do AL ainda vai existir, e até lá é isso que faz o leitor de tela dizer a que pergunta
    cada opção responde.</p>
  </div>
</section>

<section>
  <h2>Os sete estados do Figma</h2>
  {checkbox_specimens(CBX_STATES)}
</section>

<section>
  <h2>O que só existe no código</h2>
  <p>O Figma tem um eixo só de estado. O navegador produz combinações que ele não desenha — e
  elas foram decididas na etapa 3, pintadas pelos mesmos tokens, sem nenhum a mais além do
  check desabilitado.</p>
  <div style="margin-top:16px">{checkbox_specimens(CBX_COMBOS)}</div>
</section>'''

CHECKBOX_SPECS = f'''
<section>
  <h2>Anatomia</h2>
  <div class="anat">
    <div><b><code>&lt;label class="al-checkbox"&gt;</code></b><span>Envolve tudo. É o que faz clicar no texto marcar a caixa, e o que transforma a linha inteira em área de clique — também é onde mora o hover.</span></div>
    <div><b>Caixa</b><span><code>&lt;input type="checkbox"&gt;</code> nativo com <code>appearance: none</code>: a caixa do navegador sai e a do AL entra. Teclado, anúncio e estado misto continuam do navegador.</span></div>
    <div><b>Check e traço</b><span>Os ícones <code>check</code> e <code>minus</code> da Fundação, irmãos do input — <code>&lt;input&gt;</code> não tem filho. Posicionados por cima, com <code>pointer-events: none</code> devolvendo o clique.</span></div>
    <div><b>Rótulo</b><span>Sempre visível, à direita. É a regra que sustenta a exceção de contraste da borda.</span></div>
  </div>
</section>

<section>
  <h2>A geometria é consequência</h2>
  <p>A caixa é <code>box-size</code>: <b>24px</b>, o mesmo grid de 24 do desenho Lucide e a
  mesma entrelinha do rótulo — é isso que alinha a caixa com a primeira linha do texto quando
  ele quebra, sem ajuste nenhum. O glifo não tem token: são
  <b>{CBX_DERIVED['icon-size']}px</b>, caixa − 2 × borda − 2 × respiro, e a conta está
  escrita no CSS em vez de um número. <code>18</code> nem existe na escala de ícone.</p>
  <p style="margin-top:12px">A borda de 1px existe em todos os estados, inclusive no laranja —
  por isso a caixa nunca “pula” quando o estado troca a cor dela.</p>
  <div class="stats">
    <div class="stat hl"><b>{N_CHECKBOX_TOKENS}</b><span>tokens, todos alias</span></div>
    <div class="stat"><b>0</b><span>valores soltos</span></div>
    <div class="stat"><b>7</b><span>estados no Figma</span></div>
    <div class="stat"><b>1</b><span>tamanho — regra do Tier 2</span></div>
  </div>
</section>

<section>
  <h2>Cor — um token por papel e estado</h2>
  <div class="scroller" style="margin-top:20px"><table>
    <thead><tr><th>Token</th><th>Aponta para</th><th>Resolve (claro)</th></tr></thead>
    <tbody>{checkbox_token_rows()}</tbody>
  </table></div>
  <div class="note" style="margin-top:16px">
    <b>Marcado e indeterminado dividem a mesma caixa</b>
    <code>bg-checked</code> e <code>border-checked</code> valem para os dois. O que diferencia é o
    glifo — check ou traço —, nunca a cor. E o glifo tem token próprio (<code>checkbox-icon</code>)
    porque não pode herdar a cor do rótulo: o rótulo é escuro, o check é branco.
  </div>
</section>

<section>
  <h2>Geometria e tipografia</h2>
  <div class="scroller" style="margin-top:20px"><table>
    <thead><tr><th>Token</th><th>Aponta para</th><th>Valor</th></tr></thead>
    <tbody>{checkbox_geo_rows()}</tbody>
  </table></div>
</section>

<section>
  <h2>Quem ganha quando dois estados acontecem juntos</h2>
  <p>A mesma técnica do Select: fundo e borda são
  <code>var(--_*-force, var(--_*-state))</code>. Hover e foco escrevem em
  <code>--_*-state</code>; marcado, erro e desabilitado escrevem em <code>--_*-force</code>,
  que vence por ser <b>outra propriedade</b>, não por ter seletor mais pesado. Daí sai cada
  combinação que o Figma não desenha:</p>
  <div class="anat" style="margin-top:16px">
    <div><b>Marcado + hover</b><span>A caixa laranja não muda. O hover só existe na caixa vazia.</span></div>
    <div><b>Marcado + foco</b><span>O anel aparece por cima da caixa laranja.</span></div>
    <div><b>Erro + marcado</b><span>Caixa laranja, rótulo vermelho — a borda de erro só vale na caixa vazia, que é onde o erro mora.</span></div>
    <div><b>Erro + foco</b><span>Anel padrão: não há anel de erro desenhado para este componente.</span></div>
    <div><b>Desabilitado</b><span>Vem por último no arquivo e ganha de todos. Marcado e desabilitado mostra o check em <code>icon-disabled</code>.</span></div>
  </div>
</section>'''

CHECKBOX_GUIDE = f'''
<section>
  <h2>Quando usar</h2>
  <div class="anat">
    <div><b>Várias opções de uma lista</b><span>Ou uma opção isolada que só vale depois de confirmar — enviar, salvar. <i>Carbon, Primer, NN/g.</i></span></div>
    <div><b>Nunca para escolha única</b><span>Se só uma opção pode ser escolhida, é radio: com o Checkbox a pessoa não tem como saber que as opções se excluem. <i>Carbon.</i></span></div>
    <div><b>Nunca para ação imediata</b><span>Ativar modo escuro, ligar notificações: quem clica numa caixa espera confirmar depois. Ação imediata pede o <a href="#/switch">Switch</a>. <i>Carbon, Primer.</i></span></div>
    <div><b>Aceite</b><span>Checkbox isolado serve para “Li e aceito os termos”, em primeira pessoa. <i>Primer.</i></span></div>
  </div>
</section>

<section>
  <h2>Grupo e indeterminado</h2>
  <div class="anat">
    <div><b>Uma por linha, na vertical</b><span>Na horizontal fica difícil dizer qual caixa é de qual rótulo. <i>NN/g, Carbon.</i></span></div>
    <div><b>Título do grupo em <code>fieldset</code> + <code>legend</code></b><span>O componente de grupo do AL é separado e ainda vai existir. Até lá, os nativos — sem eles o leitor de tela anuncia a opção sem a pergunta.</span></div>
    <div><b>Misto só no pai</b><span>Todos os filhos marcados → pai marcado; nenhum → vazio; alguns → misto. <i>Carbon, Material.</i></span></div>
    <div><b>Clicar no pai misto marca todos</b><span>Ninguém escolhe o misto: ele é consequência. Aplicado por JavaScript — não existe atributo HTML. <i>Material.</i></span></div>
  </div>
</section>

<section>
  <h2>Rótulo</h2>
  <div class="dd">
    <div class="cell">
      <span class="lab" style="color:var(--al-text-success)">Faça</span>
      <div class="stage2 cbx-stage">{cbx('gd-cbx-ok', 'Receber novidades por e-mail', checked=True)}</div>
      <p class="cap">Curto, em sentence case, sem ponto final, <b>afirmativo</b>. O texto também é
      clicável, e o hover acende a linha inteira. <i>Primer, Carbon.</i></p>
    </div>
    <div class="cell">
      <span class="lab" style="color:var(--al-text-danger)">Não faça</span>
      <div class="stage2 cbx-stage">{cbx('gd-cbx-bad', 'Não quero deixar de receber novidades.')}</div>
      <p class="cap">Negação obriga a pensar duas vezes para saber o que marcar — e aqui marcar
      significa <i>receber</i>, o oposto do que a frase parece dizer. <i>Primer.</i></p>
    </div>
  </div>
  <div class="anat" style="margin-top:16px">
    <div><b>Rótulo longo quebra alinhado ao topo</b><span>A caixa fica na altura da primeira linha, não centralizada no bloco. <i>Carbon.</i> No AL sai de graça: caixa e entrelinha medem os mesmos 24px.</span></div>
  </div>
</section>

<section>
  <h2>Estados</h2>
  <div class="anat">
    <div><b>Desabilitado só quando depende de outra escolha na mesma tela</b><span>Se nunca vai poder ser usado, esconda. Mesma regra do Select.</span></div>
    <div><b>O desabilitado fica abaixo de AA de propósito</b><span>O WCAG 1.4.3 isenta controle inativo, e subir esse contraste faz a caixa parecer clicável.</span></div>
    <div><b>Marcado e desabilitado existe</b><span>Caixa cinza, check apagado — aparece em qualquer tela de configuração travada, então existe no código mesmo sem variante no Figma.</span></div>
  </div>
</section>

<section>
  <h2>Erro — o componente não tem mensagem</h2>
  <div class="dd">
    <div class="cell">
      <span class="lab" style="color:var(--al-text-success)">Faça</span>
      <div class="stage2 cbx-stage">{cbx_msg('gd-cbx-sum', 'Aceite os termos de uso para continuar.')}{cbx('gd-cbx-err', 'Li e aceito os termos de uso', erro='gd-cbx-sum')}</div>
      <p class="cap">O formulário descreve o erro em texto — aqui, um resumo acima — e o
      checkbox aponta para ele com <code>aria-describedby</code>.</p>
    </div>
    <div class="cell">
      <span class="lab" style="color:var(--al-text-danger)">Não faça</span>
      <div class="stage2 cbx-stage">{cbx('gd-cbx-nomsg', 'Li e aceito os termos de uso', sim='error')}</div>
      <p class="cap">Só a borda e o rótulo vermelhos. Isso é <b>só cor</b>, e o WCAG exige o erro
      descrito em texto (3.3.1) e não comunicado só por cor (1.4.1).</p>
    </div>
  </div>
  <div class="note" style="margin-top:16px">
    <b>Divergência consciente</b>
    Carbon e Polaris colocam a mensagem dentro do componente. O AL deixa o texto para o
    formulário — e é por isso que esta regra é obrigatória, não sugestão: ela cobre a lacuna.
    O rótulo vermelho também é escolha nossa, coerente com o Select e com o Material; Carbon e
    Polaris deixam o rótulo neutro. O erro aparece <b>depois do envio</b>, nunca enquanto a
    pessoa ainda escolhe.
  </div>
</section>

<section>
  <h2>Fora de escopo, de propósito</h2>
  <div class="anat">
    <div><b>Um tamanho só</b><span>Regra de todo input do Tier 2.</span></div>
    <div><b>Texto de apoio e mensagem de erro</b><span>Não fazem parte do componente — são do formulário.</span></div>
    <div><b>Variantes combinadas no Figma</b><span>Marcado + hover e companhia são cobertos pelo código com os mesmos tokens; as variantes entram se uma atualização pedir.</span></div>
    <div><b>Checkbox sem rótulo visível</b><span>Fica reservado para a seleção de linha do futuro componente de tabela, que resolve o nome com <code>aria-label</code>. Até lá, não use.</span></div>
    <div><b>Read-only</b><span>Ainda não aberto. Ação imediata é o <a href="#/switch">Switch</a>.</span></div>
  </div>
</section>'''

CHECKBOX_A11Y_TAB = f'''
<section>
  <h2>Quem desenha o limite muda com o estado</h2>
  <p>O portão mede <b>combinação renderizada</b>, e aqui ela mostra uma coisa que o par de
  token sozinho esconde: <b>desmarcada, quem desenha a caixa é a borda; marcada, é o
  preenchimento inteiro</b>, porque borda e fundo viram a mesma cor. Medir a borda da caixa
  marcada contra o próprio fundo daria 1:1 e reprovaria uma caixa perfeitamente visível —
  então o portão mede o laranja contra a página.</p>
  <p style="margin-top:12px">E a página não é uma só: o Checkbox vive em listas de
  configuração, que costumam morar em faixa de seção (<code>bg-surface</code>). O portão mede
  contra tela, faixa e card, e guarda a pior.</p>
  <div class="stats">
    <div class="stat hl"><b>{N_CBX_MEDIDAS}</b><span>combinações medidas</span></div>
    <div class="stat"><b>{N_CBX_PASSA}</b><span>passam</span></div>
    <div class="stat"><b>{N_CBX_EXC}</b><span>em exceção declarada</span></div>
    <div class="stat"><b>{CHECKBOX_A11Y['fails']}</b><span>reprovas</span></div>
  </div>
</section>

<section>
  <h2>Com foco, a borda passa sozinha</h2>
  <p>O anel desenha um respiro de 2px em <code>bg-canvas</code> colado na caixa, e a vizinha
  externa da borda passa a ser ele — independente de onde o checkbox foi colocado.</p>
  <div class="scroller" style="margin-top:16px"><table>
    <thead><tr><th>Tema</th><th>Borda em repouso</th><th>Borda com foco</th></tr></thead>
    <tbody>
      <tr><td class="tok dim">claro</td><td class="num">{CBX_LAYER['light']['rest']:.2f}:1</td><td class="num strong">{CBX_LAYER['light']['focused']:.2f}:1</td></tr>
      <tr><td class="tok dim">escuro</td><td class="num">{CBX_LAYER['dark']['rest']:.2f}:1</td><td class="num strong">{CBX_LAYER['dark']['focused']:.2f}:1</td></tr>
    </tbody>
  </table></div>
  <p style="margin-top:12px">A borda fraca existe só em repouso, nunca durante a navegação por
  teclado. E, diferente do Select, o anel <b>não</b> aparece no clique do mouse: medido no
  Chromium, um checkbox clicado não casa <code>:focus-visible</code>.</p>
</section>

<section>
  <h2>As duas exceções, nomeadas</h2>
  <div class="note">
    <b>Borda em repouso abaixo de 3:1 — decisão consciente</b>
    <code>border-default</code> fica em {CBX_LAYER['light']['rest']:.2f}:1 no claro e
    {CBX_LAYER['dark']['rest']:.2f}:1 no escuro, no pior fundo. Foi decidido para seguir o padrão
    dos inputs do AL. <b>O argumento do Select não vale aqui</b>: no Checkbox a borda é o único
    desenho do controle vazio. O que sustenta a exceção é o rótulo visível ao lado — por isso
    “nunca use checkbox sem rótulo visível” é regra de uso, e não sugestão. Hover, foco, erro e
    a caixa marcada passam todos.
  </div>
  <div class="note" style="margin-top:16px">
    <b>Desabilitado abaixo de AA — isenção do 1.4.3</b>
    Rótulo, borda e check desabilitados ficam abaixo do piso. O WCAG isenta componente inativo,
    e subir esse contraste faz a caixa parecer clicável. No tema escuro, a caixa desabilitada e
    a normal chegam a ser idênticas (<code>#3E3E3E</code>): só o rótulo apagado diferencia —
    outra razão para o rótulo visível ser obrigatório.
  </div>
</section>

<section>
  <h2>Não-textual — piso 3:1</h2>
  <div class="scroller" style="margin-top:20px"><table>
    <thead><tr><th>Tema</th><th>Estado</th><th>Papel</th><th></th><th>Token</th><th>Medido contra</th><th>Razão</th><th>Piso</th><th></th></tr></thead>
    <tbody>{checkbox_a11y_rows(['borda', 'caixa marcada', 'anel de foco', 'check', 'traco'])}</tbody>
  </table></div>
</section>

<section>
  <h2>Texto — piso 4,5:1</h2>
  <div class="scroller" style="margin-top:20px"><table>
    <thead><tr><th>Tema</th><th>Estado</th><th>Papel</th><th></th><th>Token</th><th>Medido contra</th><th>Razão</th><th>Piso</th><th></th></tr></thead>
    <tbody>{checkbox_a11y_rows(['rotulo'])}</tbody>
  </table></div>
</section>

<section>
  <h2>O contrato de marcação</h2>
  <p>Estas cinco regras não estão escritas numa página: elas são medidas por
  <code>components/checkbox/a11y.py</code> no HTML que este site emite, e quebram o build.</p>
  <div class="anat" style="margin-top:16px">
    <div><b>Nativo, dentro do rótulo</b><span><code>&lt;input type="checkbox"&gt;</code> dentro de <code>&lt;label class="al-checkbox"&gt;</code>. Nenhum <code>role="checkbox"</code> na página.</span></div>
    <div><b>Rótulo visível</b><span>Texto não-vazio em <code>.al-checkbox__label</code>, e nada de <code>aria-label</code>.</span></div>
    <div><b>Erro descrito</b><span>Com <code>aria-invalid="true"</code>, tem <code>aria-describedby</code>, e o id apontado existe no documento.</span></div>
    <div><b>Glifos decorativos</b><span><code>aria-hidden="true"</code> e <code>focusable="false"</code> no check e no traço — o estado quem anuncia é o input.</span></div>
    <div><b>Sem atributo <code>indeterminate</code></b><span>Ele não existe em HTML e o navegador o ignora em silêncio. O misto é só por JavaScript.</span></div>
  </div>
  <div class="stats" style="margin-top:16px">
    <div class="stat hl"><b>{CHECKBOX_A11Y['markupChecked']}</b><span>checkboxes conferidos no HTML</span></div>
    <div class="stat"><b>5</b><span>regras por checkbox</span></div>
    <div class="stat"><b>{'pendente' if CHECKBOX_A11Y['markupPending'] else 'medido'}</b><span>estado do contrato</span></div>
  </div>
</section>'''


# ═══════════════════════════════════════════════════════════════ Radio · abas
# 6 estados no Figma, num eixo so. Radio sozinho nao existe (regra 3): todo
# exemplo desta pagina e uma PERGUNTA - <fieldset> + <legend> + duas opcoes ou
# mais com o mesmo `name`. E o que o components/radio/a11y.py cobra no HTML.
# O erro e da pergunta: `aria-invalid` vai no fieldset, nunca no radio (regra 26).
def rd(rid, nome, valor, rotulo, *, checked=False, disabled=False, sim=None, extra=''):
    """Um Radio real. `sim` escreve nas MESMAS variaveis privadas que o radio.css
    usa: 'hover' (so vive sob o ponteiro) e 'error' (so para o "Nao faca": o
    visual do erro SEM aria-invalid, porque o exemplo e um erro nao descrito)."""
    attrs = [f'id="{rid}"', 'class="al-radio__input"', 'type="radio"',
             f'name="{nome}"', f'value="{valor}"']
    if checked:
        attrs.append('checked')
    if disabled:
        attrs.append('disabled')
    lab_style = ''
    if sim == 'hover':
        attrs.append('style="--_bg-state: var(--al-radio-bg-hover); '
                     '--_border-state: var(--al-radio-border-hover)"')
    if sim == 'error':
        if not checked:
            attrs.append('style="--_border-force: var(--al-radio-border-error)"')
        lab_style = ' style="color: var(--al-radio-label-error)"'
    if extra:
        attrs.append(extra)
    return (f'<label class="al-radio">'
            f'<span class="al-radio__control"><input {" ".join(attrs)}>'
            f'<span class="al-radio__dot" aria-hidden="true"></span></span>'
            f'<span class="al-radio__label"{lab_style}>{rotulo}</span></label>')


def rq(nome, legenda, opcoes, *, erro=None, sim=None, horizontal=False, attrs=''):
    """Uma pergunta: o <fieldset> que a APLICACAO monta (regra 6). `opcoes` =
    [(valor, rotulo, kwargs)]. `erro` = id da mensagem do formulario."""
    abre = f'<fieldset class="rd-group{" rd-group--row" if horizontal else ""}"'
    if erro:
        abre += f' aria-invalid="true" aria-describedby="{erro}"'
    if attrs:
        abre += ' ' + attrs
    corpo = ''.join(rd(f'{nome}-{i}', nome, v, r, **{'sim': sim, **kw})
                    for i, (v, r, kw) in enumerate(opcoes))
    return f'{abre}><legend>{legenda}</legend><div class="rd-opts">{corpo}</div></fieldset>'


def rd_msg(mid, texto):
    """A mensagem de erro e do FORMULARIO, nao do componente (regra 22)."""
    return f'<p class="rd-formerror" id="{mid}">{texto}</p>'


RD_COBRANCA = [('mensal', 'Mensal', {}), ('anual', 'Anual', {})]

RD_STATES = [
    ('default', 'Default', 'O repouso. A borda aqui é a exceção de contraste declarada.',
     'Cobrança', [('mensal', 'Mensal', {}), ('anual', 'Anual', {})], {}),
    ('hover', 'Hover', 'Só existe sob o ponteiro: a variável privada foi escrita direto na primeira '
     'opção. O real vale na linha inteira — passe o mouse na segunda.',
     'Cobrança', [('mensal', 'Mensal', dict(sim='hover')), ('anual', 'Anual', {})], {}),
    ('active', 'Active (marcado)', 'Anel laranja com ponto de 14px. Passar o mouse no marcado '
     'não muda nada: ele não desmarca com clique.',
     'Cobrança', [('mensal', 'Mensal', dict(checked=True)), ('anual', 'Anual', {})], {}),
    ('focus', 'Focus', 'Tabule até aqui e use as setas: foco e escolha andam juntos. '
     'Pelo mouse o anel não aparece.', 'Cobrança', RD_COBRANCA, {}),
    ('error', 'Error', 'Vem de <code>aria-invalid="true"</code> no <code>fieldset</code>: acende '
     'as duas opções de uma vez. A mensagem é do formulário.',
     'Forma de pagamento', [('pix', 'Pix', {}), ('boleto', 'Boleto', {})],
     dict(erro='sp-rd-error-msg')),
    ('disabled', 'Disabled', 'Atributo nativo <code>disabled</code>: setas e Tab pulam a opção.',
     'Cobrança', [('mensal', 'Mensal', {}), ('empresa', 'Empresarial', dict(disabled=True))], {}),
]

RD_COMBOS = [
    ('dischk', 'Marcado + disabled', 'Círculo cinza, ponto em <code>dot-disabled</code> — o único '
     'token sem variante no Figma.', 'Plano atual',
     [('empresa', 'Empresarial', dict(checked=True, disabled=True)),
      ('mensal', 'Mensal', dict(disabled=True))], {}),
    ('errchk', 'Erro + marcado', 'O marcado segue laranja e só o rótulo avisa; a vizinha vazia '
     'fica com borda vermelha.', 'Forma de pagamento',
     [('pix', 'Pix', dict(checked=True)), ('boleto', 'Boleto', {})],
     dict(erro='sp-rd-errchk-msg')),
    ('chkfoc', 'Marcado + foco', 'O anel aparece por cima do anel laranja — ele não depende do '
     'estado.', 'Cobrança', [('mensal', 'Mensal', dict(checked=True)), ('anual', 'Anual', {})], {}),
]

RD_MSGS = {'sp-rd-error-msg': 'Escolha uma forma de pagamento.',
           'sp-rd-errchk-msg': 'Pix indisponível para este valor. Escolha outra forma.'}


def radio_specimens(lista):
    cells = []
    for slug, nome, nota, legenda, opcoes, kw in lista:
        corpo = rq(f'sp-rd-{slug}', legenda, opcoes, **kw)
        if kw.get('erro'):
            corpo += rd_msg(kw['erro'], RD_MSGS[kw['erro']])
        cells.append(f'<div class="cell"><span class="lab" '
                     f'style="color:var(--al-text-secondary)">{nome}</span>'
                     f'<div class="stage2 rd-stage">{corpo}</div>'
                     f'<p class="cap">{nota}</p></div>')
    return '<div class="dd">' + ''.join(cells) + '</div>'


def radio_token_rows():
    rows = []
    for name in RADIO['alias']:
        res = RADIO['resolved'].get(name)
        if not isinstance(res, dict) or 'light' not in res:
            continue
        lt = res['light']
        sw = (f'<span class="chip sm" style="background:{lt}"></span>'
              if isinstance(lt, str) and lt.startswith('#') else '')
        rows.append(f'<tr><td class="tok">--al-{name}</td>'
                    f'<td class="tok dim">{RADIO["alias"][name]}</td>'
                    f'<td class="tok dim">{sw}{lt}</td></tr>')
    return '\n'.join(rows)


def radio_geo_rows():
    rows = []
    for role in ['box-size', 'padding', 'gap', 'radius', 'border-width']:
        name = f'radio-{role}'
        rows.append(f'<tr><td class="tok">--al-{name}</td>'
                    f'<td class="tok dim">{RADIO["alias"][name]}</td>'
                    f'<td class="num">{RADIO["resolved"][name]}px</td></tr>')
    res = RADIO['resolved']['radio-label-font']
    rows.append(f'<tr><td class="tok">--al-radio-label-font</td>'
                f'<td class="tok dim">{RADIO["alias"]["radio-label-font"]}</td>'
                f'<td class="num">{res[1]}/{res[2]} · peso {res[3]}</td></tr>')
    return '\n'.join(rows)


def radio_a11y_rows(papeis):
    out = []
    for r in RADIO_A11Y['rows']:
        if r['papel'] not in papeis:
            continue
        if r['pass']:
            verdict = '<span class="pass">passa</span>'
        elif r['exc']:
            verdict = '<span class="exc">exceção</span>'
        else:
            verdict = '<span class="fail">reprova</span>'
        chips = (f'<span class="chip sm" style="background:{r["fgHex"]}"></span>'
                 f'<span class="chip sm" style="background:{r["bgHex"]}"></span>')
        estado = r['state'] + (' <span class="tok dim">(código)</span>' if r['soNoCodigo'] else '')
        out.append(
            f'<tr><td class="tok dim">{"claro" if r["theme"] == "light" else "escuro"}</td>'
            f'<td class="name">{estado}</td>'
            f'<td class="tok dim">{r["papel"]}</td><td class="chipcell">{chips}</td>'
            f'<td class="tok dim">--al-{r["token"]}</td>'
            f'<td class="tok dim">{r["contra"]}</td>'
            f'<td class="num strong">{r["ratio"]:.2f}:1</td>'
            f'<td class="num dim">{r["floor"]}:1</td><td>{verdict}</td></tr>')
    return '\n'.join(out)


N_RD_MEDIDAS = len(RADIO_A11Y['rows'])
N_RD_EXC = sum(RADIO_A11Y['exceptions'].values())
N_RD_PASSA = N_RD_MEDIDAS - N_RD_EXC


def _rd_borda(state, theme):
    return next(r['ratio'] for r in RADIO_A11Y['rows']
                if r['state'] == state and r['theme'] == theme and r['papel'] == 'borda')


RD_LAYER = {t: {'rest': _rd_borda('default', t), 'focused': _rd_borda('focus', t)}
            for t in ('light', 'dark')}
RD_DERIVED = RADIO['derived']
RD_PIOR = min((r for r in RADIO_A11Y['rows'] if r['pass']), key=lambda r: r['ratio'] / r['floor'])

TH_RADIO = ('<div class="th-rd" aria-hidden="true">'
            '<span class="th-rd__row"><span class="th-rd__dot is-on"></span>Mensal</span>'
            '<span class="th-rd__row"><span class="th-rd__dot"></span>Anual</span>'
            '<span class="th-rd__row"><span class="th-rd__dot"></span>Empresarial</span></div>')

RADIO_OVERVIEW = f'''
<section>
  <h2>Playground</h2>
  <div class="pg">
    <div class="stage" id="rd-stage">{rq('pg-rd', 'Cobrança', [('mensal', 'Mensal', dict(checked=True)), ('anual', 'Anual', {}), ('empresa', 'Empresarial', {})])}</div>

    <div class="controls" id="rd-controls">
      <div class="ctl"><span class="ctl-name">Seleção inicial</span>{seg('rdvalue', [('first', 'Primeira marcada'), ('none', 'Nenhuma')], 'first')}</div>
      <div class="ctl"><span class="ctl-name">Estado</span>{seg('rdstate', [('rest', 'Normal'), ('error', 'Erro'), ('disabled', 'Uma desabilitada')], 'rest')}</div>
      <div class="ctl"><span class="ctl-name">Tema</span>{seg('rdtheme', [('auto', 'Do sistema'), ('light', 'Claro'), ('dark', 'Escuro')], 'auto')}</div>
      <div class="ctl"><label for="rd-legend" class="ctl-name">Pergunta</label>
        <input class="txt" id="rd-legend" type="text" value="Cobrança" maxlength="60"></div>
    </div>

    <div class="codewrap">
      <div class="codebar"><span>Marcação</span>
        <button type="button" class="copy" id="rd-copy">Copiar</button></div>
      <pre><code id="rd-code"></code></pre>
    </div>
  </div>
  <p style="margin-top:14px; font-size:13.5px; color:var(--al-text-secondary)">
    Os radios acima são o componente real: esta página carrega o mesmo <code>radio.css</code> que
    vai para produção. Tabule até eles e use as setas — foco e escolha andam juntos. O
    <code>fieldset</code> e o <code>legend</code> <b>não fazem parte do componente</b>: são a
    pergunta, que a aplicação monta. No erro, o <code>aria-invalid</code> vai nela, e a mensagem
    em vermelho é o formulário descrevendo o erro em texto.
  </p>
</section>

<section>
  <h2>Uma pergunta de verdade</h2>
  <div class="cell" style="max-width:none">
    <form class="rd-form" id="rd-form" novalidate>
      <p class="rd-summary" id="rd-form-erro" hidden>Escolha uma forma de pagamento para assinar.</p>
      {rq('ov-rd-pag', 'Forma de pagamento da assinatura', [('cartao', 'Cartão de crédito', dict(extra='required')), ('pix', 'Pix', dict(extra='required')), ('boleto', 'Boleto', dict(disabled=True, extra='required'))])}
      <div class="rd-actions">
        <button type="submit" class="al-btn al-btn--primary al-btn--sm" id="rd-form-enviar"><span class="al-btn__label">Assinar</span></button>
        <p class="rd-ok" id="rd-form-ok" role="status"></p>
      </div>
    </form>
    <p class="cap">Envie sem escolher: as opções ficam vermelhas <b>juntas</b>, porque o erro é da
    pergunta e não de uma opção, e o erro aparece em texto no topo. Escolha uma e tudo volta. Não há
    pré-seleção aqui de propósito: forma de pagamento tem custo, e a escolha precisa ser consciente.
    <i>Primer, Spectrum, Carbon e Polaris põem o erro no grupo.</i></p>
  </div>
</section>

<section>
  <h2>Os seis estados do Figma</h2>
  {radio_specimens(RD_STATES)}
</section>

<section>
  <h2>O que só existe no código</h2>
  <p>O Figma tem um eixo só de estado. O navegador produz combinações que ele não desenha — e
  elas foram decididas na etapa 3, pintadas pelos mesmos tokens, sem nenhum a mais além do
  ponto desabilitado.</p>
  <div style="margin-top:16px">{radio_specimens(RD_COMBOS)}</div>
</section>'''

RADIO_SPECS = f'''
<section>
  <h2>Anatomia</h2>
  <div class="anat">
    <div><b><code>&lt;label class="al-radio"&gt;</code></b><span>Envolve tudo. É o que faz clicar no texto marcar a opção, e o que transforma a linha inteira em área de clique — também é onde mora o hover.</span></div>
    <div><b>Círculo</b><span><code>&lt;input type="radio"&gt;</code> nativo com <code>appearance: none</code>: o círculo do navegador sai e o do AL entra. Setas, Tab e “marcar um desmarca o outro” continuam do navegador.</span></div>
    <div><b>Ponto</b><span>Um <code>&lt;span&gt;</code> irmão do input, com <code>aria-hidden</code> — <code>&lt;input&gt;</code> não tem filho, e pseudo-elemento em input não é garantido em todo navegador. <code>pointer-events: none</code> devolve o clique.</span></div>
    <div><b>Rótulo</b><span>Sempre visível, à direita. É a regra que sustenta a exceção de contraste da borda.</span></div>
    <div><b>A pergunta — fora do componente</b><span><code>&lt;fieldset&gt;</code> + <code>&lt;legend&gt;</code>, montados pela aplicação. Todos os radios dela dividem o mesmo <code>name</code>. O AL não tem componente de grupo, de propósito.</span></div>
  </div>
</section>

<section>
  <h2>A geometria é consequência</h2>
  <p>O círculo é <code>box-size</code>: <b>24px</b>, a mesma caixa do Checkbox e a mesma
  entrelinha do rótulo — é isso que alinha o círculo com a primeira linha do texto quando ele
  quebra. O ponto não tem token: são <b>{RD_DERIVED['dot-size']}px</b>, círculo − 2 × borda −
  2 × respiro, e a conta está escrita no CSS em vez de um número.</p>
  <p style="margin-top:12px">O respiro é <code>space-4</code>, não o <code>space-2</code> do
  Checkbox. Com 18px o ponto enchia o círculo, e o marcado desabilitado virava um disco cinza igual
  ao desmarcado desabilitado. A borda de 1px existe em todos os estados, então o círculo nunca
  “pula” quando o estado troca a cor dela.</p>
  <div class="stats">
    <div class="stat hl"><b>{N_RADIO_TOKENS}</b><span>tokens, todos alias</span></div>
    <div class="stat"><b>0</b><span>valores soltos</span></div>
    <div class="stat"><b>6</b><span>estados no Figma</span></div>
    <div class="stat"><b>1</b><span>tamanho — regra do Tier 2</span></div>
  </div>
</section>

<section>
  <h2>Cor — um token por papel e estado</h2>
  <div class="scroller" style="margin-top:20px"><table>
    <thead><tr><th>Token</th><th>Aponta para</th><th>Resolve (claro)</th></tr></thead>
    <tbody>{radio_token_rows()}</tbody>
  </table></div>
  <div class="note" style="margin-top:16px">
    <b>Marcado não pinta o fundo — a diferença para o Checkbox</b>
    No Checkbox, marcado é a caixa laranja. No Radio, marcado é borda laranja + ponto laranja, e o
    fundo continua <code>radio-bg</code>: o anel branco entre os dois <i>é</i> o fundo. Por isso não
    existe <code>bg-checked</code>, e existem <code>dot</code> e <code>dot-disabled</code>.
  </div>
</section>

<section>
  <h2>Geometria e tipografia</h2>
  <div class="scroller" style="margin-top:20px"><table>
    <thead><tr><th>Token</th><th>Aponta para</th><th>Valor</th></tr></thead>
    <tbody>{radio_geo_rows()}</tbody>
  </table></div>
</section>

<section>
  <h2>Quem ganha quando dois estados acontecem juntos</h2>
  <p>A mesma técnica do Checkbox: fundo e borda são
  <code>var(--_*-force, var(--_*-state))</code>. Hover e foco escrevem em
  <code>--_*-state</code>; marcado, erro e desabilitado escrevem em <code>--_*-force</code>,
  que vence por ser <b>outra propriedade</b>, não por ter seletor mais pesado.</p>
  <div class="anat" style="margin-top:16px">
    <div><b>Marcado + hover</b><span>Nada muda: o marcado força o fundo de volta a <code>radio-bg</code>. Radio marcado não desmarca com clique, e o hover prometeria uma ação que não existe.</span></div>
    <div><b>Marcado + foco</b><span>O anel aparece por cima do anel laranja.</span></div>
    <div><b>Erro + marcado</b><span>Borda e ponto laranja, rótulo vermelho — a borda de erro só vale no círculo vazio, que é onde o erro mora.</span></div>
    <div><b>Erro + foco</b><span>Anel padrão: não há anel de erro desenhado para este componente.</span></div>
    <div><b>Desabilitado</b><span>Vem por último no arquivo e ganha de todos. Marcado e desabilitado mostra o ponto em <code>dot-disabled</code>.</span></div>
  </div>
</section>

<section>
  <h2>O erro é lido da pergunta</h2>
  <p>O <code>radio.css</code> não procura <code>aria-invalid</code> no radio: procura em
  qualquer elemento <b>acima</b> dele — na prática, o <code>fieldset</code>. Marcar a pergunta uma
  vez acende todas as opções, e não há como esquecer uma. Foi um achado da etapa 6: a primeira
  versão lia o erro no próprio radio, copiando o Checkbox, e o portão de marcação reprovou.</p>
</section>'''

RADIO_GUIDE = f'''
<section>
  <h2>Quando usar</h2>
  <div class="anat">
    <div><b>Uma única opção de uma lista curta</b><span>Todas visíveis, para a pessoa comparar antes de escolher. <i>Primer, Spectrum, Material.</i></span></div>
    <div><b>Até cinco ou seis opções</b><span>Acima disso, use o Select. <i>Material (5), Primer e Spectrum (6).</i></span></div>
    <div><b>Nunca para várias escolhas, nunca sozinho</b><span>Várias escolhas é Checkbox. Uma pergunta tem sempre duas opções ou mais; um sim/não de aceite isolado também é Checkbox. <i>Polaris, Carbon.</i></span></div>
    <div><b>Nunca para ação imediata</b><span>A escolha só vale quando a pessoa envia ou salva — as setas mudam a escolha enquanto ela navega. Ação imediata pede o <a href="#/switch">Switch</a>. <i>Primer, Material.</i></span></div>
  </div>
</section>

<section>
  <h2>A pergunta</h2>
  <div class="anat">
    <div><b>Mesmo <code>name</code> em todas as opções</b><span>É o que faz marcar uma desmarcar a outra, e as setas andarem entre elas.</span></div>
    <div><b><code>fieldset</code> + <code>legend</code>, montados pela aplicação</b><span>Sem eles o leitor de tela anuncia “Mensal, botão de opção” sem dizer qual é a pergunta. <i>Carbon, Polaris, Primer.</i></span></div>
    <div><b>Uma por linha, na vertical</b><span>Horizontal só com duas ou três opções curtas, e com o espaço entre uma e outra claramente maior que os 8px entre círculo e rótulo. <i>Spectrum.</i></span></div>
    <div><b>Ordem lógica</b><span>A mais comum primeiro, crescente, ou a ordem natural — não alfabética sem motivo. <i>Polaris, Spectrum.</i></span></div>
  </div>
</section>

<section>
  <h2>Seleção inicial</h2>
  <div class="dd">
    <div class="cell">
      <span class="lab" style="color:var(--al-text-success)">Marque de início</span>
      <div class="stage2 rd-stage">{rq('gd-rd-resumo', 'Resumo das vendas por e-mail', [('semanal', 'Semanal', dict(checked=True)), ('mensal', 'Mensal', {}), ('nenhum', 'Nenhum', {})])}</div>
      <p class="cap">Quando há uma resposta segura e mais provável, e ela vem primeiro. Como
      radio marcado não desmarca, “nenhum” vira uma opção. <i>Spectrum, Polaris; Carbon para o
      “Nenhum”.</i></p>
    </div>
    <div class="cell">
      <span class="lab" style="color:var(--al-text-secondary)">Não marque nada</span>
      <div class="stage2 rd-stage">{rq('gd-rd-plano', 'Plano da assinatura', [('basico', 'Básico — R$ 49/mês', {}), ('pro', 'Pro — R$ 129/mês', {})])}</div>
      <p class="cap">Quando a escolha precisa ser consciente: dado sensível, consentimento, algo
      com custo. <i>Carbon, que hoje recomenda nenhuma pré-seleção.</i> As referências divergem, e
      o AL decide pelo contexto.</p>
    </div>
  </div>
</section>

<section>
  <h2>Rótulo</h2>
  <div class="dd">
    <div class="cell">
      <span class="lab" style="color:var(--al-text-success)">Faça</span>
      <div class="stage2 rd-stage">{rq('gd-rd-ok', 'Funcionários', [('p', '1 a 5', dict(checked=True)), ('m', '6 a 20', {}), ('g', 'Mais de 20', {})])}</div>
      <p class="cap">Curto, só a primeira letra maiúscula, sem ponto final. As opções têm a mesma
      estrutura e não se sobrepõem. <i>Polaris.</i></p>
    </div>
    <div class="cell">
      <span class="lab" style="color:var(--al-text-danger)">Não faça</span>
      <div class="stage2 rd-stage">{rq('gd-rd-bad', 'Funcionários', [('p', '1 a 5', {}), ('m', '5 a 20', {}), ('g', 'Uma empresa grande.', {})])}</div>
      <p class="cap">Quem tem 5 funcionários cabe em duas opções — as faixas se sobrepõem. E a
      terceira quebra o paralelo: frase com ponto, sem número. <i>Polaris.</i></p>
    </div>
  </div>
  <div class="anat" style="margin-top:16px">
    <div><b>Rótulo longo quebra alinhado ao topo</b><span>O círculo fica na altura da primeira linha. <i>Carbon.</i> No AL sai de graça: círculo e entrelinha medem os mesmos 24px.</span></div>
  </div>
</section>

<section>
  <h2>Estados</h2>
  <div class="anat">
    <div><b>A forma diferencia, não só a cor</b><span>Marcado é anel com ponto; vazio é anel sem ponto. Foi por isso que o ponto diminuiu para 14px na etapa 1.</span></div>
    <div><b>Desabilitado só quando depende de outra escolha na mesma tela</b><span>Se nunca vai estar disponível, esconda. Se todas ficariam desabilitadas, repense a pergunta.</span></div>
    <div><b>O desabilitado fica abaixo de AA de propósito</b><span>O WCAG isenta controle inativo, e subir esse contraste faz a opção parecer clicável.</span></div>
    <div><b>Marcado e desabilitado existe</b><span>Círculo cinza, ponto apagado — aparece em qualquer plano travado, então existe no código mesmo sem variante no Figma.</span></div>
  </div>
</section>

<section>
  <h2>Erro — é da pergunta, e o componente não tem mensagem</h2>
  <div class="dd">
    <div class="cell">
      <span class="lab" style="color:var(--al-text-success)">Faça</span>
      <div class="stage2 rd-stage">{rq('gd-rd-err', 'Forma de pagamento', [('pix', 'Pix', {}), ('boleto', 'Boleto', {})], erro='gd-rd-err-msg')}{rd_msg('gd-rd-err-msg', 'Escolha uma forma de pagamento.')}</div>
      <p class="cap">O erro vai no <code>fieldset</code> e acende todas as opções juntas. O
      formulário descreve o erro em texto, e a pergunta aponta para ele com
      <code>aria-describedby</code>. <i>Primer, Carbon, Polaris.</i></p>
    </div>
    <div class="cell">
      <span class="lab" style="color:var(--al-text-danger)">Não faça</span>
      <div class="stage2 rd-stage">{rq('gd-rd-nomsg', 'Forma de pagamento', [('pix', 'Pix', {}), ('boleto', 'Boleto', {})], sim='error')}</div>
      <p class="cap">Só bordas e rótulos vermelhos. Isso é <b>só cor</b>, e o WCAG exige o erro
      descrito em texto (3.3.1) e não comunicado só por cor (1.4.1).</p>
    </div>
  </div>
  <div class="note" style="margin-top:16px">
    <b>Divergência consciente</b>
    Carbon, Polaris e Primer colocam a mensagem no grupo. O AL não tem componente de grupo e
    deixa o texto para o formulário — por isso esta regra é obrigatória, não sugestão. O rótulo
    vermelho também é escolha nossa, coerente com o Select, o Checkbox e o Material. A
    obrigatoriedade se indica na pergunta, e o AL marca o opcional: “(opcional)” no
    <code>legend</code>. O erro aparece <b>depois do envio</b>, nunca enquanto a pessoa escolhe.
  </div>
</section>

<section>
  <h2>Fora de escopo, de propósito</h2>
  <div class="anat">
    <div><b>Um tamanho só</b><span>Regra de todo input do Tier 2.</span></div>
    <div><b>Componente de grupo</b><span>Nem agora nem no roadmap: a pergunta é <code>fieldset</code> + <code>legend</code> nativos.</span></div>
    <div><b>Texto de apoio e mensagem de erro</b><span>Não fazem parte do componente — são do formulário.</span></div>
    <div><b>Variantes combinadas no Figma</b><span>Cobertas pelo código com os mesmos tokens.</span></div>
    <div><b>Radio em card e read-only</b><span>Ainda não abertos. Ação imediata é o <a href="#/switch">Switch</a>.</span></div>
  </div>
</section>'''

RADIO_A11Y_TAB = f'''
<section>
  <h2>No Radio, quem desenha o limite é sempre a borda</h2>
  <p>O portão mede <b>combinação renderizada</b>. No Checkbox marcado, o limite passava a ser o
  preenchimento inteiro; aqui não: o marcado não pinta o fundo, então a borda laranja fica entre
  a página por fora e o anel branco por dentro, e é medida contra os dois. O ponto é medido contra
  o anel que o cerca.</p>
  <p style="margin-top:12px">E a página não é uma só: o portão mede contra tela, faixa de seção e
  card, e guarda a pior. A menor margem entre as que passam é
  <b>{RD_PIOR['papel']}</b> em <code>{RD_PIOR['state']}</code>, {RD_PIOR['ratio']:.2f}:1 contra o
  piso de {RD_PIOR['floor']}:1 — na faixa cinza, que a etapa 3 não conseguia ver.</p>
  <div class="stats">
    <div class="stat hl"><b>{N_RD_MEDIDAS}</b><span>combinações medidas</span></div>
    <div class="stat"><b>{N_RD_PASSA}</b><span>passam</span></div>
    <div class="stat"><b>{N_RD_EXC}</b><span>em exceção declarada</span></div>
    <div class="stat"><b>{RADIO_A11Y['fails']}</b><span>reprovas</span></div>
  </div>
</section>

<section>
  <h2>Com foco, a borda passa sozinha</h2>
  <p>O anel desenha um respiro de 2px em <code>bg-canvas</code> colado no círculo, e a vizinha
  externa da borda passa a ser ele — independente de onde o radio foi colocado.</p>
  <div class="scroller" style="margin-top:16px"><table>
    <thead><tr><th>Tema</th><th>Borda em repouso</th><th>Borda com foco</th></tr></thead>
    <tbody>
      <tr><td class="tok dim">claro</td><td class="num">{RD_LAYER['light']['rest']:.2f}:1</td><td class="num strong">{RD_LAYER['light']['focused']:.2f}:1</td></tr>
      <tr><td class="tok dim">escuro</td><td class="num">{RD_LAYER['dark']['rest']:.2f}:1</td><td class="num strong">{RD_LAYER['dark']['focused']:.2f}:1</td></tr>
    </tbody>
  </table></div>
  <p style="margin-top:12px">A borda fraca existe só em repouso, nunca durante a navegação por
  teclado. No teclado, o Tab entra na pergunta uma vez só — na opção marcada, ou na primeira se
  nenhuma estiver — e as setas movem foco e escolha juntos, pulando a desabilitada.</p>
</section>

<section>
  <h2>As duas exceções, nomeadas</h2>
  <div class="note">
    <b>Borda em repouso abaixo de 3:1 — decisão consciente</b>
    <code>border-default</code> fica em {RD_LAYER['light']['rest']:.2f}:1 no claro e
    {RD_LAYER['dark']['rest']:.2f}:1 no escuro, no pior fundo — a mesma decisão do Checkbox, para
    seguir o padrão dos inputs do AL. A borda é o único desenho do radio vazio; o que sustenta a
    exceção é o rótulo visível ao lado, e por isso “nunca sem rótulo visível” é regra de uso.
    Hover, foco, marcado e erro passam todos.
  </div>
  <div class="note" style="margin-top:16px">
    <b>Desabilitado abaixo de AA — isenção do 1.4.3</b>
    Rótulo, borda e ponto desabilitados ficam abaixo do piso. O WCAG isenta componente inativo, e
    subir esse contraste faz a opção parecer clicável. No tema escuro o círculo desabilitado e o
    normal chegam a ser idênticos (<code>#3E3E3E</code>): só o rótulo apagado diferencia.
  </div>
</section>

<section>
  <h2>Não-textual — piso 3:1</h2>
  <div class="scroller" style="margin-top:20px"><table>
    <thead><tr><th>Tema</th><th>Estado</th><th>Papel</th><th></th><th>Token</th><th>Medido contra</th><th>Razão</th><th>Piso</th><th></th></tr></thead>
    <tbody>{radio_a11y_rows(['borda', 'anel de foco', 'ponto'])}</tbody>
  </table></div>
</section>

<section>
  <h2>Texto — piso 4,5:1</h2>
  <div class="scroller" style="margin-top:20px"><table>
    <thead><tr><th>Tema</th><th>Estado</th><th>Papel</th><th></th><th>Token</th><th>Medido contra</th><th>Razão</th><th>Piso</th><th></th></tr></thead>
    <tbody>{radio_a11y_rows(['rotulo'])}</tbody>
  </table></div>
</section>

<section>
  <h2>O contrato de marcação</h2>
  <p>Estas seis regras não estão escritas numa página: elas são medidas por
  <code>components/radio/a11y.py</code> no HTML que este site emite, e quebram o build.</p>
  <div class="anat" style="margin-top:16px">
    <div><b>Nativo, dentro do rótulo</b><span><code>&lt;input type="radio"&gt;</code> dentro de <code>&lt;label class="al-radio"&gt;</code>. Nenhum <code>role="radio"</code> na página.</span></div>
    <div><b>Rótulo visível</b><span>Texto não-vazio em <code>.al-radio__label</code>, e nada de <code>aria-label</code>.</span></div>
    <div><b>Duas opções ou mais</b><span>Todo radio tem <code>name</code>, e cada <code>name</code> junta duas opções ou mais.</span></div>
    <div><b>A pergunta existe</b><span>As opções de um <code>name</code> moram num só <code>fieldset</code>, com <code>legend</code> visível.</span></div>
    <div><b>Erro na pergunta, descrito</b><span><code>aria-invalid="true"</code> no <code>fieldset</code>, com <code>aria-describedby</code> para um id que existe — e nunca no radio.</span></div>
    <div><b>Ponto decorativo</b><span><code>aria-hidden="true"</code> — o estado quem anuncia é o input.</span></div>
  </div>
  <div class="stats" style="margin-top:16px">
    <div class="stat hl"><b>{RADIO_A11Y['markupChecked']}</b><span>radios conferidos no HTML</span></div>
    <div class="stat"><b>6</b><span>regras por radio</span></div>
    <div class="stat"><b>{'pendente' if RADIO_A11Y['markupPending'] else 'medido'}</b><span>estado do contrato</span></div>
  </div>
</section>'''


# ═══════════════════════════════════════════════════════════════ Switch · abas
# 5 estados no Figma, num eixo so. Efeito imediato: nao ha formulario com
# "Enviar" nesta pagina (regra 1) - a demonstracao e uma tela de configuracoes.
# O components/switch/a11y.py cobra o contrato de marcacao no HTML emitido.
def sw(sid, rotulo, *, checked=False, disabled=False, sim=None, extra=''):
    """Um Switch real. `sim='hover'` escreve na MESMA variavel privada que o
    switch.css usa - o hover so vive sob o ponteiro."""
    attrs = [f'id="{sid}"', 'class="al-switch__input"', 'type="checkbox"', 'role="switch"']
    if checked:
        attrs.append('checked')
    if disabled:
        attrs.append('disabled')
    if sim == 'hover':
        attrs.append('style="--_border-state: var(--al-switch-border-hover)"')
    if extra:
        attrs.append(extra)
    return (f'<label class="al-switch">'
            f'<span class="al-switch__control"><input {" ".join(attrs)}>'
            f'<span class="al-switch__thumb" aria-hidden="true"></span></span>'
            f'<span class="al-switch__label">{rotulo}</span></label>')


SW_STATES = [
    ('default', 'Default', 'Desligado. A bolinha e a borda são as exceções de contraste declaradas; '
     'quem sustenta é o rótulo visível e o laranja do ligado.',
     sw('sp-sw-default', 'Notificações por e-mail')),
    ('hover', 'Hover', 'Só existe sob o ponteiro: a variável privada foi escrita direto no input. '
     'O real acende a borda na linha inteira — passe o mouse no Default.',
     sw('sp-sw-hover', 'Notificações por e-mail', sim='hover')),
    ('active', 'Active (ligado)', 'Trilho laranja, bolinha branca à direita. Clique: ela desliza de '
     'volta. Com o mouse em cima do ligado nada muda.',
     sw('sp-sw-active', 'Modo escuro automático', checked=True)),
    ('focus', 'Focus', 'Tabule até aqui: anel laranja com respiro, e a borda fica a de repouso. '
     'Espaço alterna; Enter não.',
     sw('sp-sw-focus', 'Legendas nos vídeos')),
    ('disabled', 'Disabled', 'Atributo nativo <code>disabled</code>: o Tab pula. Contraste abaixo '
     'de AA de propósito.',
     sw('sp-sw-disabled', 'Resumo semanal', disabled=True)),
]

SW_COMBOS = [
    ('dischk', 'Ligado + disabled', 'Trilho cinza, bolinha à direita um tom mais escura '
     '(<code>thumb-checked-disabled</code>) — sem laranja. O único token sem variante no Figma.',
     sw('sp-sw-dischk', 'Backup diário', checked=True, disabled=True)),
    ('chkfoc', 'Ligado + foco', 'O anel aparece por fora do trilho laranja — ele não depende do estado.',
     sw('sp-sw-chkfoc', 'Sincronizar contatos', checked=True)),
    ('long', 'Rótulo longo', 'O texto quebra e o trilho fica na altura da primeira linha: '
     'trilho e entrelinha medem os mesmos 24px.',
     sw('sp-sw-long', 'Enviar a nota fiscal por e-mail ao contador assim que o pagamento for '
                      'confirmado', checked=True)),
]


def switch_specimens(lista):
    cells = []
    for slug, nome, nota, corpo in lista:
        cells.append(f'<div class="cell"><span class="lab" '
                     f'style="color:var(--al-text-secondary)">{nome}</span>'
                     f'<div class="stage2 sw-stage">{corpo}</div>'
                     f'<p class="cap">{nota}</p></div>')
    return '<div class="dd">' + ''.join(cells) + '</div>'


def switch_token_rows():
    rows = []
    for name in SWITCH['alias']:
        res = SWITCH['resolved'].get(name)
        if not isinstance(res, dict) or 'light' not in res:
            continue
        lt = res['light']
        sw_ = (f'<span class="chip sm" style="background:{lt}"></span>'
               if isinstance(lt, str) and lt.startswith('#') else '')
        rows.append(f'<tr><td class="tok">--al-{name}</td>'
                    f'<td class="tok dim">{SWITCH["alias"][name]}</td>'
                    f'<td class="tok dim">{sw_}{lt}</td></tr>')
    return '\n'.join(rows)


def switch_geo_rows():
    rows = []
    for role in ['track-height', 'padding', 'gap', 'radius', 'border-width']:
        name = f'switch-{role}'
        rows.append(f'<tr><td class="tok">--al-{name}</td>'
                    f'<td class="tok dim">{SWITCH["alias"][name]}</td>'
                    f'<td class="num">{SWITCH["resolved"][name]}px</td></tr>')
    res = SWITCH['resolved']['switch-label-font']
    rows.append(f'<tr><td class="tok">--al-switch-label-font</td>'
                f'<td class="tok dim">{SWITCH["alias"]["switch-label-font"]}</td>'
                f'<td class="num">{res[1]}/{res[2]} · peso {res[3]}</td></tr>')
    return '\n'.join(rows)


def switch_a11y_rows(papeis):
    out = []
    for r in SWITCH_A11Y['rows']:
        if r['papel'] not in papeis:
            continue
        if r['pass']:
            verdict = '<span class="pass">passa</span>'
        elif r['exc']:
            verdict = '<span class="exc">exceção</span>'
        else:
            verdict = '<span class="fail">reprova</span>'
        chips = (f'<span class="chip sm" style="background:{r["fgHex"]}"></span>'
                 f'<span class="chip sm" style="background:{r["bgHex"]}"></span>')
        estado = r['state'] + (' <span class="tok dim">(código)</span>' if r['soNoCodigo'] else '')
        out.append(
            f'<tr><td class="tok dim">{"claro" if r["theme"] == "light" else "escuro"}</td>'
            f'<td class="name">{estado}</td>'
            f'<td class="tok dim">{r["papel"]}</td><td class="chipcell">{chips}</td>'
            f'<td class="tok dim">--al-{r["token"]}</td>'
            f'<td class="tok dim">{r["contra"]}</td>'
            f'<td class="num strong">{r["ratio"]:.2f}:1</td>'
            f'<td class="num dim">{r["floor"]}:1</td><td>{verdict}</td></tr>')
    return '\n'.join(out)


N_SW_MEDIDAS = len(SWITCH_A11Y['rows'])
N_SW_EXC = sum(SWITCH_A11Y['exceptions'].values())
N_SW_PASSA = N_SW_MEDIDAS - N_SW_EXC
SW_DERIVED = SWITCH['derived']
SW_PIOR = min((r for r in SWITCH_A11Y['rows'] if r['pass']), key=lambda r: r['ratio'] / r['floor'])


def _sw(state, theme, papel):
    return next(r['ratio'] for r in SWITCH_A11Y['rows']
                if r['state'] == state and r['theme'] == theme and r['papel'] == papel)


SW_THUMB = {t: _sw('default', t, 'bolinha') for t in ('light', 'dark')}
SW_BORDA = {t: _sw('default', t, 'borda') for t in ('light', 'dark')}
SW_ON = {t: _sw('checked', t, 'bolinha') for t in ('light', 'dark')}

TH_SWITCH = ('<div class="th-sw" aria-hidden="true">'
             '<span class="th-sw__row"><span class="th-sw__track is-on"><span class="th-sw__thumb"></span></span>E-mail</span>'
             '<span class="th-sw__row"><span class="th-sw__track"><span class="th-sw__thumb"></span></span>Celular</span>'
             '<span class="th-sw__row"><span class="th-sw__track is-on"><span class="th-sw__thumb"></span></span>Resumo</span></div>')

SWITCH_OVERVIEW = f'''
<section>
  <h2>Playground</h2>
  <div class="pg">
    <div class="stage" id="sw-stage">{sw('pg-sw', 'Notificações por e-mail', checked=True)}</div>

    <div class="controls" id="sw-controls">
      <div class="ctl"><span class="ctl-name">Estado inicial</span>{seg('swvalue', [('on', 'Ligado'), ('off', 'Desligado')], 'on')}</div>
      <div class="ctl"><span class="ctl-name">Disponível</span>{seg('swstate', [('rest', 'Sim'), ('disabled', 'Desabilitado')], 'rest')}</div>
      <div class="ctl"><span class="ctl-name">Tema</span>{seg('swtheme', [('auto', 'Do sistema'), ('light', 'Claro'), ('dark', 'Escuro')], 'auto')}</div>
      <div class="ctl"><label for="sw-label" class="ctl-name">Rótulo</label>
        <input class="txt" id="sw-label" type="text" value="Notificações por e-mail" maxlength="60"></div>
    </div>

    <div class="codewrap">
      <div class="codebar"><span>Marcação</span>
        <button type="button" class="copy" id="sw-copy">Copiar</button></div>
      <pre><code id="sw-code"></code></pre>
    </div>
  </div>
  <p style="margin-top:14px; font-size:13.5px; color:var(--al-text-secondary)">
    O switch acima é o componente real: esta página carrega o mesmo <code>switch.css</code> que vai
    para produção. Tabule até ele e aperte Espaço. Por baixo é um
    <code>&lt;input type="checkbox"&gt;</code> com <code>role="switch"</code>, e é isso que faz o leitor
    de tela anunciar “chave, ligada” em vez de “caixa de seleção, marcada”.
  </p>
</section>

<section>
  <h2>Uma tela de configurações de verdade</h2>
  <div class="cell" style="max-width:none">
    <div class="sw-settings">
      <fieldset class="sw-group">
        <legend>Notificações</legend>
        <div class="sw-opts">
          {sw('ov-sw-email', 'Notificações por e-mail', checked=True)}
          {sw('ov-sw-resumo', 'Resumo semanal', checked=True)}
          {sw('ov-sw-push', 'Notificações no celular')}
          {sw('ov-sw-contador', 'Enviar notas ao contador')}
        </div>
      </fieldset>
      <p class="sw-status" id="ov-sw-status" role="status" aria-live="polite"></p>
    </div>
    <p class="cap">Não há botão “Salvar”: cada switch vale na hora. Desligue as notificações por
    e-mail e o resumo semanal fica desabilitado, porque depende delas. Ligue o envio ao contador: a
    bolinha troca no clique e, quando o servidor simulado recusa, volta ao estado real e a aplicação
    avisa em texto. <i>Primer, Polaris e Material: o switch aplica na hora e mostra o estado real.</i></p>
  </div>
</section>

<section>
  <h2>Os cinco estados do Figma</h2>
  {switch_specimens(SW_STATES)}
</section>

<section>
  <h2>O que só existe no código</h2>
  <p>O Figma tem um eixo só de estado. O navegador produz combinações que ele não desenha — e
  elas foram decididas na etapa 3, pintadas pelos mesmos tokens, sem nenhum a mais além da
  bolinha do ligado desabilitado.</p>
  <div style="margin-top:16px">{switch_specimens(SW_COMBOS)}</div>
</section>'''

SWITCH_SPECS = f'''
<section>
  <h2>Anatomia</h2>
  <div class="anat">
    <div><b><code>&lt;label class="al-switch"&gt;</code></b><span>Envolve tudo. É o que faz clicar no texto alternar, e o que transforma a linha inteira em área de clique — também é onde mora o hover.</span></div>
    <div><b>Trilho</b><span>É o próprio <code>&lt;input type="checkbox" role="switch"&gt;</code>, com <code>appearance: none</code>: a caixa do navegador sai e o trilho do AL entra. Espaço, clique no rótulo e o valor no formulário continuam do navegador.</span></div>
    <div><b>Bolinha</b><span>Um <code>&lt;span&gt;</code> irmão do input, com <code>aria-hidden</code> — <code>&lt;input&gt;</code> não tem filho. <code>pointer-events: none</code> devolve o clique ao input.</span></div>
    <div><b>Rótulo</b><span>Sempre visível, à direita, e nunca muda com o estado. É a regra que sustenta as duas exceções de contraste.</span></div>
    <div><b>O grupo — fora do componente</b><span>Quando há vários switches, o título é da aplicação: um título de seção, ou <code>fieldset</code> + <code>legend</code>. Cada switch continua independente.</span></div>
  </div>
</section>

<section>
  <h2>A geometria é consequência</h2>
  <p>O trilho tem <code>track-height</code>: <b>24px</b>, a mesma altura do círculo do Radio e da
  entrelinha do rótulo. Todo o resto sai dele: a bolinha são <b>{SW_DERIVED['thumb-size']}px</b>
  (altura − 2 × borda − 2 × respiro), a largura são <b>{SW_DERIVED['track-width']}px</b> (a bolinha
  cabe duas vezes, mais respiro e borda) e o curso é a própria bolinha. Nenhum desses números tem
  token — as contas estão escritas no CSS.</p>
  <p style="margin-top:12px">A bolinha anda por <code>inset-inline-start</code>, não por
  <code>transform</code>: numa página escrita da direita para a esquerda, o ligado fica à esquerda
  sozinho. A borda de 1px existe em todos os estados e fica dentro dos 38×24, então o trilho nunca
  “pula” quando o estado troca a cor dela.</p>
  <div class="stats">
    <div class="stat hl"><b>{N_SWITCH_TOKENS}</b><span>tokens, todos alias</span></div>
    <div class="stat"><b>0</b><span>valores soltos</span></div>
    <div class="stat"><b>5</b><span>estados no Figma</span></div>
    <div class="stat"><b>1</b><span>tamanho — regra do Tier 2</span></div>
  </div>
</section>

<section>
  <h2>Cor — um token por papel e estado</h2>
  <div class="scroller" style="margin-top:20px"><table>
    <thead><tr><th>Token</th><th>Aponta para</th><th>Resolve (claro)</th></tr></thead>
    <tbody>{switch_token_rows()}</tbody>
  </table></div>
  <div class="note" style="margin-top:16px">
    <b>Dois semânticos nasceram para o Switch</b>
    <code>bg-thumb</code> e <code>bg-thumb-disabled</code> entraram na Fundação, com claro e escuro
    — o escuro é o espelho do claro na escada de neutros. O nome serve a qualquer peça que desliza
    sobre um trilho, como um Slider no futuro. O resto reaproveita semânticos que já existiam:
    o trilho desligado é <code>bg-surface</code> e a bolinha ligada é <code>text-on-brand</code>.
  </div>
</section>

<section>
  <h2>Geometria e tipografia</h2>
  <div class="scroller" style="margin-top:20px"><table>
    <thead><tr><th>Token</th><th>Aponta para</th><th>Valor</th></tr></thead>
    <tbody>{switch_geo_rows()}</tbody>
  </table></div>
</section>

<section>
  <h2>Quem ganha quando dois estados acontecem juntos</h2>
  <p>A mesma técnica do Checkbox e do Radio: fundo e borda são
  <code>var(--_*-force, var(--_*-state))</code>. O hover escreve em <code>--_border-state</code>;
  ligado e desabilitado escrevem em <code>--_*-force</code>, que vence por ser <b>outra
  propriedade</b>, não por ter seletor mais pesado.</p>
  <div class="anat" style="margin-top:16px">
    <div><b>Ligado + hover</b><span>Nada muda: o ligado força a borda laranja. O laranja já é o sinal mais forte.</span></div>
    <div><b>Foco</b><span>Só o anel. A borda fica a de repouso — é assim no Figma.</span></div>
    <div><b>Ligado + foco</b><span>O anel aparece por fora do trilho laranja.</span></div>
    <div><b>Desabilitado</b><span>Vem por último no arquivo e ganha de todos. Ligado e desabilitado mostra a bolinha à direita em <code>thumb-checked-disabled</code>, sem laranja.</span></div>
  </div>
</section>

<section>
  <h2>Sem erro, sem carregamento</h2>
  <p>O switch tem efeito imediato, então não valida e não tem estado de erro. Quando a ação falha,
  quem age é a aplicação: ela desmarca o input de volta e avisa em texto. O componente não tem
  estado de carregamento — a bolinha troca no clique e só volta se o sistema recusar.</p>
</section>'''

SWITCH_GUIDE = f'''
<section>
  <h2>Quando usar</h2>
  <div class="anat">
    <div><b>Ligar ou desligar algo que vale na hora</b><span>Sem botão “Salvar”: quem aciona um switch espera que a mudança já tenha acontecido. <i>Carbon, Primer, Polaris, Spectrum, Material.</i></span></div>
    <div><b>Se só vale depois de enviar, é Checkbox</b><span>Um switch num formulário com “Enviar” dá a impressão de que já aplicou — e não aplicou. <i>Polaris, Primer.</i></span></div>
    <div><b>Só dois estados opostos</b><span>Se as opções não são um liga/desliga simples — “Diário / Semanal” —, é Radio ou Select. <i>Polaris, Carbon.</i></span></div>
    <div><b>Nunca para aceite de termos</b><span>Aceite depende de envio e costuma ser obrigatório: é Checkbox. <i>Primer, Polaris.</i></span></div>
  </div>
</section>

<section>
  <h2>Mais de um switch</h2>
  <div class="anat">
    <div><b>Lista vertical, um por linha, cada um independente</b><span>Ligar um nunca desliga outro. Se precisa desligar, a pergunta é de escolha única — e é Radio. <i>Material, Carbon.</i></span></div>
    <div><b>O título do grupo é da aplicação</b><span>Um título de seção, ou <code>fieldset</code> + <code>legend</code>. Não há componente de grupo. <i>Carbon.</i></span></div>
  </div>
</section>

<section>
  <h2>Rótulo</h2>
  <div class="dd">
    <div class="cell">
      <span class="lab" style="color:var(--al-text-success)">Faça</span>
      <div class="stage2 sw-stage">{sw('gd-sw-ok', 'Notificações por e-mail', checked=True)}</div>
      <p class="cap">Nomeia a configuração. Teste: leia em voz alta e some “ligado” ou
      “desligado” no fim — “Notificações por e-mail, ligado” faz sentido. <i>NN/g, Primer.</i></p>
    </div>
    <div class="cell">
      <span class="lab" style="color:var(--al-text-danger)">Não faça</span>
      <div class="stage2 sw-stage">{sw('gd-sw-bad', 'Deseja receber notificações?')}</div>
      <p class="cap">Pergunta não é rótulo: “Deseja receber notificações?, desligado” não faz
      sentido. Também não use o estado como rótulo (“Notificações ativadas”), porque ele teria de
      mudar a cada clique. <i>NN/g, Carbon.</i></p>
    </div>
  </div>
  <div class="anat" style="margin-top:16px">
    <div><b>Visível, à direita, e clicar nele alterna</b><span>O <code>&lt;label&gt;</code> envolve o controle: a área de clique é a linha inteira, não só os 38×24 do trilho. <i>Carbon, Material; WCAG 2.5.8.</i></span></div>
    <div><b>Nunca muda com o estado</b><span>Quem mostra o estado é o controle. <i>Carbon.</i></span></div>
    <div><b>Sem “Ligado/Desligado” ao lado</b><span>O switch sozinho basta. <i>Material.</i> Divergência consciente do Primer, que mostra esse texto.</span></div>
    <div><b>Curto, sem ponto final</b><span>Rótulo longo quebra, e o trilho fica na altura da primeira linha. <i>NN/g, Carbon.</i></span></div>
  </div>
</section>

<section>
  <h2>Estado inicial e estados</h2>
  <div class="anat">
    <div><b>O estado inicial é o estado real</b><span>Se a notificação está ativa no sistema, o switch nasce ligado. Nunca pré-ligue “porque é o recomendado” — o switch não propõe, ele mostra. <i>Material.</i></span></div>
    <div><b>Posição e cor mudam juntas</b><span>Ligado é trilho laranja com a bolinha à direita; nunca só a cor (WCAG 1.4.1).</span></div>
    <div><b>Aplica no clique, sem confirmação</b><span>Nunca pergunte “Tem certeza?” para algo que se desfaz com outro clique. Ação grave não é switch. <i>Primer, Polaris, Material.</i></span></div>
    <div><b>Desabilitado só quando depende de outra configuração</b><span>Se nunca vai estar disponível, esconda. <i>Mesma regra do Select, do Checkbox e do Radio.</i></span></div>
    <div><b>O desabilitado fica abaixo de AA de propósito</b><span>O WCAG isenta controle inativo, e subir esse contraste faz o switch parecer clicável.</span></div>
  </div>
</section>

<section>
  <h2>Quando a ação falha</h2>
  <div class="anat">
    <div><b>Sem erro e nunca obrigatório</b><span>Se uma configuração precisa estar ligada para a pessoa seguir, é um aceite — e aceite é Checkbox. <i>Spectrum, Polaris.</i></span></div>
    <div><b>Troca na hora, e volta se falhar</b><span>A bolinha muda no clique. Se o sistema recusar, ela volta ao estado real e a aplicação avisa em texto o que falhou. O switch nunca mostra um estado que o sistema não tem.</span></div>
  </div>
  <div class="note" style="margin-top:16px">
    <b>Divergência consciente</b>
    O Primer pede para esperar a resposta com um indicador de carregamento. O AL não tem esse
    estado, e sem indicador a pessoa clica e parece que nada aconteceu — por isso a troca é
    imediata e o recuo é da aplicação. <i>Material: o switch mostra o status real.</i>
  </div>
</section>

<section>
  <h2>Fora de escopo, de propósito</h2>
  <div class="anat">
    <div><b>Um tamanho só</b><span>Regra de todo input do Tier 2.</span></div>
    <div><b>Erro, texto de status e somente-leitura</b><span>O switch tem efeito imediato; somente-leitura só existe no Carbon — se aparecer, mostre o valor como texto.</span></div>
    <div><b>Ícone dentro da bolinha</b><span>Existe no Material; o AL não usa.</span></div>
    <div><b>Texto de apoio abaixo do rótulo</b><span>O Primer tem. Se a demanda aparecer, abre uma rodada nova do componente.</span></div>
    <div><b>Componente de grupo e estado de carregamento</b><span>O grupo é da aplicação; a espera é coberta pela troca imediata.</span></div>
  </div>
</section>'''

SWITCH_A11Y_TAB = f'''
<section>
  <h2>A bolinha mede contra o trilho em que está</h2>
  <p>O portão mede <b>combinação renderizada</b>: a borda contra a página por fora e o trilho por
  dentro, a bolinha contra o trilho, o rótulo contra a página. E a página não é uma só: tela,
  faixa de seção e card, guardando a pior. A menor margem entre as que passam é
  <b>{SW_PIOR['papel']}</b> em <code>{SW_PIOR['state']}</code>, {SW_PIOR['ratio']:.2f}:1 contra o piso
  de {SW_PIOR['floor']}:1.</p>
  <div class="stats">
    <div class="stat hl"><b>{N_SW_MEDIDAS}</b><span>combinações medidas</span></div>
    <div class="stat"><b>{N_SW_PASSA}</b><span>passam</span></div>
    <div class="stat"><b>{N_SW_EXC}</b><span>em exceção declarada</span></div>
    <div class="stat"><b>{SWITCH_A11Y['fails']}</b><span>reprovas</span></div>
  </div>
</section>

<section>
  <h2>O que a etapa 3 não conseguia ver</h2>
  <p>O trilho desligado é <code>bg-surface</code>. Numa faixa de seção em <code>bg-surface</code>,
  trilho e página são <b>a mesma cor</b> — nos dois temas. Ali, o switch desligado é desenhado só
  pela borda e pela bolinha. Não é uma falha nova: é exatamente o caso que a regra do rótulo
  visível cobre.</p>
</section>

<section>
  <h2>As três exceções, nomeadas</h2>
  <div class="note">
    <b>Bolinha desligada abaixo de 3:1 — decisão consciente</b>
    <code>bg-thumb</code> fica em {SW_THUMB['light']:.2f}:1 no claro e {SW_THUMB['dark']:.2f}:1 no
    escuro contra o trilho. O <code>neutral-400</code> é o teto decidido na etapa 1. O que sustenta:
    o ligado é trilho laranja, que passa, e o rótulo visível ao lado. A bolinha ligada passa com
    {SW_ON['light']:.2f}:1.
  </div>
  <div class="note" style="margin-top:16px">
    <b>Borda em repouso abaixo de 3:1 — o padrão dos inputs</b>
    <code>border-default</code> fica em {SW_BORDA['light']:.2f}:1 no claro e
    {SW_BORDA['dark']:.2f}:1 no escuro, no pior fundo — a mesma decisão do Checkbox e do Radio. O
    hover passa, e o foco é sinalizado pelo anel.
  </div>
  <div class="note" style="margin-top:16px">
    <b>Desabilitado abaixo de AA — isenção do 1.4.3</b>
    Rótulo, borda e bolinha desabilitados ficam abaixo do piso. O WCAG isenta componente inativo, e
    subir esse contraste faz o switch parecer clicável.
  </div>
</section>

<section>
  <h2>Teclado</h2>
  <p>O Tab entra em cada switch uma vez e pula o desabilitado. <b>Espaço alterna; Enter não</b> — é
  o comportamento do checkbox nativo, e é o que o leitor de tela ensina para “chave”. O anel só
  aparece quando o foco chega pelo teclado. Com “reduzir movimento” ligado no sistema, a bolinha
  troca de lado sem deslizar.</p>
</section>

<section>
  <h2>Não-textual — piso 3:1</h2>
  <div class="scroller" style="margin-top:20px"><table>
    <thead><tr><th>Tema</th><th>Estado</th><th>Papel</th><th></th><th>Token</th><th>Medido contra</th><th>Razão</th><th>Piso</th><th></th></tr></thead>
    <tbody>{switch_a11y_rows(['borda', 'anel de foco', 'bolinha'])}</tbody>
  </table></div>
</section>

<section>
  <h2>Texto — piso 4,5:1</h2>
  <div class="scroller" style="margin-top:20px"><table>
    <thead><tr><th>Tema</th><th>Estado</th><th>Papel</th><th></th><th>Token</th><th>Medido contra</th><th>Razão</th><th>Piso</th><th></th></tr></thead>
    <tbody>{switch_a11y_rows(['rotulo'])}</tbody>
  </table></div>
</section>

<section>
  <h2>O contrato de marcação</h2>
  <p>Estas cinco regras não estão escritas numa página: elas são medidas por
  <code>components/switch/a11y.py</code> no HTML que este site emite, e quebram o build.</p>
  <div class="anat" style="margin-top:16px">
    <div><b>Nativo, dentro do rótulo</b><span><code>&lt;input type="checkbox" role="switch"&gt;</code> dentro de <code>&lt;label class="al-switch"&gt;</code>. Nenhum outro elemento com <code>role="switch"</code>, nada de <code>aria-pressed</code>.</span></div>
    <div><b>Rótulo visível</b><span>Texto não-vazio em <code>.al-switch__label</code>, e nada de <code>aria-label</code>.</span></div>
    <div><b>Estado nativo</b><span>Sem <code>aria-checked</code>: o estado é o <code>checked</code> do input, e um atributo paralelo diverge do que a tela pinta.</span></div>
    <div><b>Sem erro</b><span>Nada de <code>required</code> nem <code>aria-invalid</code>.</span></div>
    <div><b>Bolinha decorativa</b><span><code>aria-hidden="true"</code> — o estado quem anuncia é o input.</span></div>
  </div>
  <div class="stats" style="margin-top:16px">
    <div class="stat hl"><b>{SWITCH_A11Y['markupChecked']}</b><span>switches conferidos no HTML</span></div>
    <div class="stat"><b>5</b><span>regras por switch</span></div>
    <div class="stat"><b>{'pendente' if SWITCH_A11Y['markupPending'] else 'medido'}</b><span>estado do contrato</span></div>
  </div>
</section>'''



LANDING_COMPONENTES = f'''
<section>
  <h2>Publicados</h2>
  <div class="cards">
    {card('button', 'Button', 'Quatro variantes, dois tamanhos, cinco estados — com playground que instancia o CSS real.', TH_BUTTON)}
    {card('icon-button', 'Icon Button', 'O botão sem rótulo visível. Mesma pílula e mesmos estados do Button, com nome acessível obrigatório.', TH_ICONBUTTON)}
    {card('tag', 'Tag', 'Rótulo curto de estado ou categoria. Conteúdo, não controle — e o primeiro do AL a fechar em zero exceções carregando texto.', TH_TAG)}
    {card('avatar', 'Avatar', 'Quem é a pessoa, em três tipos que são uma cadeia: foto, iniciais, ícone — nessa ordem, nunca uma caixa vazia.', TH_AVATAR)}
    {card('select', 'Select', 'Escolha única num formulário. É o &lt;select&gt; nativo: a lista é do navegador, e é isso que compra teclado e mobile de graça.', TH_SELECT)}
    {card('checkbox', 'Checkbox', 'Várias opções, ou uma que só vale depois de confirmar. Input nativo com a caixa do AL pintada por cima — com o estado misto para o checkbox pai.', TH_CHECKBOX)}
    {card('radio', 'Radio', 'Uma opção de uma lista curta. Input nativo com o círculo do AL pintado por cima — e o erro é da pergunta, não da opção.', TH_RADIO)}
    {card('switch', 'Switch', 'Liga ou desliga algo que vale na hora, sem “Salvar”. Checkbox nativo com role="switch" e o trilho do AL pintado por cima.', TH_SWITCH)}
  </div>
</section>

<section>
  <h2>O Tier 1 fechou</h2>
  <p>Os quatro primitivos atravessaram as oito etapas, um de cada vez — e a disciplina de fechar
  um antes de abrir o outro é a resposta à dívida de “componente pronto sem documentação”. O
  próximo tier é o de <b>formulário</b>, e ele começa como todos os outros: pela etapa 1,
  definir e auditar.</p>
</section>'''

PAGES = [
    ('fundacao', 'Fundação', simple_page(
        'fundacao', 'Fundação', 'Fundação',
        'A camada que decide antes de qualquer componente existir: a cor, a tipografia, a medida e '
        'a prova de que tudo isso atravessa o portão. Nenhum componente inventa valor — todos '
        'consomem daqui, e é por isso que trocar o tema não é retrabalho.',
        [], STATS + LANDING_FUNDACAO, first=True)),

    ('principios', 'Fundação', simple_page(
        'principios', 'Fundação', 'Princípios',
        'O que está decidido antes dos valores: as cinco escolhas que sustentam o sistema, as oito '
        'etapas que um componente percorre e os quatro portões que recusam o que não passa.',
        [('5 decisões', True), ('8 etapas', False), ('4 portões', False)],
        TAB_PRINCIPIOS)),

    ('prova', 'Fundação', simple_page(
        'prova', 'Fundação', 'A prova',
        'A mesma interface montada com os mesmos tokens, nos dois temas, lado a lado. Se a camada '
        'semântica estiver certa, nada aqui precisou ser escrito duas vezes.',
        [('Dois temas', True), (f'{N_SEM} semânticos', False), ('0 valores literais', False)],
        TAB_PROVA)),

    ('cor', 'Fundação', page(
        'cor', 'Fundação', 'Cor',
        f'{N_PRIM} primitivas geradas em OKLCH a partir de {META["brandAnchor"]}, {N_SEM} semânticos '
        f'com dois temas cada, e {N_PAIRS} pares medidos antes de qualquer um virar token.',
        [(f'{N_PRIM} primitivas', False), (f'{N_SEM} semânticos', True), ('OKLCH', False),
         ('WCAG 2.1 AA', False)],
        [('escala', 'Escala', TAB_ESCALA), ('semanticos', 'Semânticos', TAB_SEMANTICOS),
         ('contraste', 'Contraste', TAB_CONTRASTE)])),

    ('tipografia', 'Fundação', page(
        'tipografia', 'Fundação', 'Tipografia',
        f'Inter variável e JetBrains Mono. {len(T["type"]["styles"])} estilos fechados — o produto '
        'escolhe um estilo, não quatro valores soltos.',
        [(f'{len(T["type"]["styles"])} estilos', True), ('4 pesos', False),
         (f'{len(T["type"]["size"])} tamanhos', False)],
        [('escala', 'Escala', TAB_TIPO_ESCALA), ('tokens', 'Tokens', TAB_TIPO_TOKENS)])),

    ('espacamento', 'Fundação', page(
        'espacamento', 'Fundação', 'Espaçamento e medidas',
        'Base 4 com ritmo de 8, nove raios, seis degraus de elevação e um anel de foco que passa '
        'pelo mesmo portão de contraste que as cores.',
        [(f'{len(T["space"])} degraus de espaço', True), (f'{len(T["radius"])} raios', False),
         ('6 elevações', False)],
         [('espaco', 'Espaçamento', TAB_ESPACO), ('radius', 'Radius e borda', TAB_RADIUS),
         ('elevacao', 'Elevação', TAB_ELEVACAO), ('foco', 'Foco', TAB_FOCO)])),

    ('icon', 'Fundação', page(
        'icon', 'Fundação', 'Ícones',
        f'{N_ICONS} ícones no grid de 24, com o traço vetorizado. Não há escala fixa: o mesmo '
        'componente serve em 16 ou em 96, e o peso da linha acompanha em vez de ficar para trás.',
        [(f'{N_ICONS} ícones', True), ('Grid 24 · traço 2', False),
         (f'{len(ICON_TOK["alias"])} tokens', False), ('0 valores soltos', False)],
        [('overview', 'Visão geral', ICON_OVERVIEW), ('specs', 'Especificações', ICON_SPECS),
         ('a11y', 'Acessibilidade', ICON_A11Y_TAB)])),

    ('componentes', 'Componentes', simple_page(
        'componentes', 'Componentes', 'Componentes',
        'Peça pronta para usar, com desenho, tokens, código e QA já fechados. Um componente só '
        'aparece aqui depois de atravessar as oito etapas do pipeline — por isso a lista é curta e '
        'cresce devagar, um de cada vez.',
        [('6 publicados', True), ('Tier 1 fechado', False), ('8 etapas por componente', False)],
        LANDING_COMPONENTES)),

    ('button', 'Componentes', page(
        'button', 'Componentes', 'Button',
        'Dispara a ação de uma tela. Quatro variantes que carregam pesos diferentes na hierarquia, '
        'dois tamanhos, cinco estados.',
        [('Estável', True), ('40 variantes no Figma', False), (f'{N_BTN_TOKENS} tokens', False),
         ('0 valores soltos', False)],
        [('overview', 'Visão geral', BTN_OVERVIEW), ('specs', 'Especificações', BTN_SPECS),
         ('guide', 'Diretrizes', BTN_GUIDE), ('a11y', 'Acessibilidade', BTN_A11Y)])),

    ('icon-button', 'Componentes', page(
        'icon-button', 'Componentes', 'Icon Button',
        'A mesma ação do Button, sem rótulo visível. O ícone passa a ser o único portador do '
        'sentido — e é daí que vêm o nome acessível obrigatório e o piso de contraste de 3:1.',
        [('Estável', True), ('40 variantes no Figma', False), (f'{N_IB_TOKENS} tokens', False),
         ('0 exceções de marca', False)],
        [('overview', 'Visão geral', IB_OVERVIEW), ('specs', 'Especificações', IB_SPECS),
         ('guide', 'Diretrizes', IB_GUIDE), ('a11y', 'Acessibilidade', IB_A11Y)])),

    ('tag', 'Componentes', page(
        'tag', 'Componentes', 'Tag',
        'Rótulo curto de estado ou categoria. Não dispara nada: é conteúdo, fica fora da ordem '
        'de tabulação, e quem carrega o sentido é o texto — a cor apenas reforça.',
        [('Estável', True), ('20 variantes no Figma', False), (f'{N_TAG_TOKENS} tokens', False),
         ('0 exceções', False)],
        [('overview', 'Visão geral', TAG_OVERVIEW), ('specs', 'Especificações', TAG_SPECS),
         ('guide', 'Diretrizes', TAG_GUIDE), ('a11y', 'Acessibilidade', TAG_A11Y_TAB)])),

    ('avatar', 'Componentes', page(
        'avatar', 'Componentes', 'Avatar',
        'Diz quem é a pessoa. Os três tipos não são um menu: são uma cadeia — foto, iniciais, '
        'ícone — e o tipo é o primeiro da fila que tem material para existir.',
        [('Estável', True), ('9 variantes no Figma', False),
         (f'{N_AVATAR_TOKENS} tokens', False), ('0 exceções', False)],
        [('overview', 'Visão geral', AVATAR_OVERVIEW), ('specs', 'Especificações', AVATAR_SPECS),
         ('guide', 'Diretrizes', AVATAR_GUIDE), ('a11y', 'Acessibilidade', AVATAR_A11Y_TAB)])),
    ('select', 'Componentes', page(
        'select', 'Componentes', 'Select',
        'Escolha única dentro de um formulário. É o <code>&lt;select&gt;</code> nativo: a lista '
        'aberta é desenhada pelo navegador, e o componente entrega o gatilho fechado — que é o '
        'que compra teclado, leitor de tela e comportamento mobile sem uma linha de JavaScript.',
        [('Estável', True), ('7 estados no Figma', False),
         (f'{N_SELECT_TOKENS} tokens', False), ('2 exceções declaradas', False)],
        [('overview', 'Visão geral', SELECT_OVERVIEW), ('specs', 'Especificações', SELECT_SPECS),
         ('guide', 'Diretrizes', SELECT_GUIDE), ('a11y', 'Acessibilidade', SELECT_A11Y_TAB)])),
    ('checkbox', 'Componentes', page(
        'checkbox', 'Componentes', 'Checkbox',
        'Várias opções de uma lista, ou uma opção isolada que só vale depois de confirmar. É o '
        '<code>&lt;input type="checkbox"&gt;</code> nativo com a caixa do AL pintada por cima — '
        'Espaço, leitor de tela e o estado misto vêm do navegador.',
        [('Estável', True), ('7 estados no Figma', False),
         (f'{N_CHECKBOX_TOKENS} tokens', False), ('2 exceções declaradas', False)],
        [('overview', 'Visão geral', CHECKBOX_OVERVIEW), ('specs', 'Especificações', CHECKBOX_SPECS),
         ('guide', 'Diretrizes', CHECKBOX_GUIDE), ('a11y', 'Acessibilidade', CHECKBOX_A11Y_TAB)])),
    ('radio', 'Componentes', page(
        'radio', 'Componentes', 'Radio',
        'Uma única opção de uma lista curta, com todas à vista para comparar. É o '
        '<code>&lt;input type="radio"&gt;</code> nativo com o círculo do AL pintado por cima — '
        'setas, Tab e “marcar um desmarca o outro” vêm do navegador. A pergunta em volta é da aplicação.',
        [('Estável', True), ('6 estados no Figma', False),
         (f'{N_RADIO_TOKENS} tokens', False), ('2 exceções declaradas', False)],
        [('overview', 'Visão geral', RADIO_OVERVIEW), ('specs', 'Especificações', RADIO_SPECS),
         ('guide', 'Diretrizes', RADIO_GUIDE), ('a11y', 'Acessibilidade', RADIO_A11Y_TAB)])),
    ('switch', 'Componentes', page(
        'switch', 'Componentes', 'Switch',
        'Liga ou desliga uma configuração que vale na hora, sem botão “Salvar”. É o '
        '<code>&lt;input type="checkbox" role="switch"&gt;</code> nativo com o trilho do AL pintado por '
        'cima — Espaço, clique no rótulo e o anúncio “chave, ligada” vêm do navegador.',
        [('Estável', True), ('5 estados no Figma', False),
         (f'{N_SWITCH_TOKENS} tokens', False), ('3 exceções declaradas', False)],
        [('overview', 'Visão geral', SWITCH_OVERVIEW), ('specs', 'Especificações', SWITCH_SPECS),
         ('guide', 'Diretrizes', SWITCH_GUIDE), ('a11y', 'Acessibilidade', SWITCH_A11Y_TAB)])),
]

RAIL = f'''<nav class="rail" aria-label="Navegação do design system">
  <div class="brand">
    <span class="brand-mark">AL</span>
    <span class="brand-name">AL Design System<small>v{VERSION} · {META['license']}</small></span>
  </div>
  <div class="rail-nav">
    <div class="nav-group is-open" id="g-fundacao">
      <a class="nav-primary" href="#/fundacao" data-page="fundacao" aria-current="page"
         aria-expanded="true" aria-controls="sub-fundacao">
        <span class="nav-ico">{ICO_FUNDACAO}</span><span class="nav-label">Fundação</span>
        <span class="nav-chev" aria-hidden="true">{CARET}</span></a>
      <div class="nav-sub" id="sub-fundacao">
        <a href="#/principios" data-page="principios">Princípios</a>
        <a href="#/prova" data-page="prova">A prova</a>
        <a href="#/cor" data-page="cor">Cor</a>
        <a href="#/tipografia" data-page="tipografia">Tipografia</a>
        <a href="#/espacamento" data-page="espacamento">Espaçamento</a>
        <a href="#/icon" data-page="icon">Ícones</a>
      </div>
    </div>
    <div class="nav-group" id="g-componentes">
      <a class="nav-primary" href="#/componentes" data-page="componentes"
         aria-expanded="false" aria-controls="sub-componentes">
        <span class="nav-ico">{ICO_COMPONENTES}</span><span class="nav-label">Componentes</span>
        <span class="nav-chev" aria-hidden="true">{CARET}</span></a>
      <div class="nav-sub" id="sub-componentes" hidden>
        <a href="#/button" data-page="button">Button</a>
        <a href="#/icon-button" data-page="icon-button">Icon Button</a>
        <a href="#/tag" data-page="tag">Tag</a>
        <a href="#/avatar" data-page="avatar">Avatar</a>
        <a href="#/select" data-page="select">Select</a>
        <a href="#/checkbox" data-page="checkbox">Checkbox</a>
        <a href="#/radio" data-page="radio">Radio</a>
        <a href="#/switch" data-page="switch">Switch</a>
      </div>
    </div>
  </div>

  <div class="rail-foot">
    {sw('themeswitch', 'Tema escuro')}
  </div>
</nav>'''

FOOTER = f'''<footer>
  <span><b>AL Design System</b> · v{VERSION}</span>
  <span>Licença {META['license']}</span>
  <span>{META['colorSpace']} · WCAG {META['wcag']}</span>
  <span>Âncora <code>{META['brandAnchor']}</code></span>
  <span>Gerado por <code>site/site.py</code></span>
</footer>'''

JS = r"""
(function () {
  // ── trilho: uma página por vez, endereçável pelo hash ──
  var pages = [].slice.call(document.querySelectorAll('.page'));
  var links = [].slice.call(document.querySelectorAll('.rail a[data-page]'));
  // os cards das páginas-índice navegam pelo mesmo roteador que o trilho
  var cards = [].slice.call(document.querySelectorAll('a.card[data-page]'));

  var groups = [].slice.call(document.querySelectorAll('.nav-group'));

  function setOpen(group, on) {
    if (!group) return;
    group.classList.toggle('is-open', on);
    var primary = group.querySelector('.nav-primary');
    var sub = group.querySelector('.nav-sub');
    if (primary) primary.setAttribute('aria-expanded', on ? 'true' : 'false');
    if (sub) sub.hidden = !on;
  }

  // Acordeão: um aberto por vez. Abrir um fecha o outro, sempre.
  function openOnly(group) {
    groups.forEach(function (g) { setOpen(g, g === group); });
  }

  function show(id) {
    var found = false;
    pages.forEach(function (p) {
      var on = p.id === 'pg-' + id;
      p.hidden = !on;
      if (on) found = true;
    });
    if (!found) return false;
    var owner = null;
    links.forEach(function (a) {
      if (a.getAttribute('data-page') === id) {
        a.setAttribute('aria-current', 'page');
        owner = a.closest('.nav-group');
      } else {
        a.removeAttribute('aria-current');
      }
    });
    // abre o grupo dono da página e fecha o outro
    if (owner && owner.classList.contains('nav-group')) openOnly(owner);
    return true;
  }

  function fromHash() {
    var id = (location.hash || '').replace(/^#\/?/, '');
    if (!id || !show(id)) show('fundacao');
    window.scrollTo(0, 0);
  }

  // O clique troca a página direto, sem depender do hashchange: em contexto
  // com o hash bloqueado (preview, sandbox, arquivo aberto local) o evento não
  // dispara, e o trilho ficaria morto. O hash continua sendo escrito para o
  // endereço permanecer copiável.
  links.concat(cards).forEach(function (a) {
    a.addEventListener('click', function (e) {
      e.preventDefault();
      var id = a.getAttribute('data-page');
      var group = a.closest('.nav-group');
      // Clicar de novo no item primário que já está aberto recolhe a lista, sem
      // sair da página. É o único jeito de fechar os dois grupos agora que o
      // chevron não é mais um alvo separado.
      if (group && a.classList.contains('nav-primary') &&
          group.classList.contains('is-open') &&
          !document.getElementById('pg-' + id).hidden) {
        setOpen(group, false);
        return;
      }
      if (!show(id)) return;
      window.scrollTo(0, 0);
      try { history.replaceState(null, '', '#/' + id); } catch (err) { /* sandbox */ }
    });
  });

  window.addEventListener('hashchange', fromHash);

  // ── switch de tema ──
  // Carimba data-theme na raiz, que é onde a Foundation resolve o tema. Só a
  // raiz serve: a substituição de custom property acontece no elemento onde o
  // alias é DECLARADO, e toda a camada semântica é declarada no :root.
  var root = document.documentElement;
  var sw = document.getElementById('themeswitch');

  function applyTheme(dark, remember) {
    root.setAttribute('data-theme', dark ? 'dark' : 'light');
    sw.checked = dark;
    if (remember) {
      try { localStorage.setItem('al-theme', dark ? 'dark' : 'light'); } catch (e) { /* sem storage */ }
    }
  }

  // Estado inicial. A Foundation tem TRÊS estados, não dois: sem carimbo, quem
  // decide é o sistema. Carimbar na carga mataria o terceiro estado, então
  // enquanto o leitor não tocar no switch a página continua seguindo o sistema
  // e o switch apenas reflete o que está na tela.
  var saved = null;
  try { saved = localStorage.getItem('al-theme'); } catch (e) { /* sem storage */ }
  var mq = window.matchMedia ? window.matchMedia('(prefers-color-scheme: dark)') : null;
  var stamped = root.getAttribute('data-theme');

  if (saved) {
    applyTheme(saved === 'dark', false);          // escolha anterior: carimba
  } else if (stamped) {
    sw.checked = stamped === 'dark';
  } else {
    sw.checked = !!(mq && mq.matches);
    if (mq && mq.addEventListener) {
      mq.addEventListener('change', function (e) {
        if (!root.getAttribute('data-theme')) {
          sw.checked = e.matches;
        }
      });
    }
  }

  // O input nativo ja trocou o `checked` quando o evento chega: so carimbar.
  sw.addEventListener('change', function () {
    applyTheme(sw.checked, true);
  });

  // Se o ambiente reescrever data-theme por fora (o visualizador tem o próprio
  // controle de tema), o switch acompanha em vez de ficar mentindo.
  if (window.MutationObserver) {
    new MutationObserver(function () {
      var dark = root.getAttribute('data-theme') === 'dark';
      if (sw.checked !== dark) sw.checked = dark;
    }).observe(root, { attributes: true, attributeFilter: ['data-theme'] });
  }

  // ── abas, com navegação por seta como manda o padrão ──
  [].slice.call(document.querySelectorAll('.tabs')).forEach(function (bar) {
    var tabs = [].slice.call(bar.querySelectorAll('[role="tab"]'));
    function select(tab) {
      tabs.forEach(function (t) {
        var on = t === tab;
        t.setAttribute('aria-selected', on ? 'true' : 'false');
        t.tabIndex = on ? 0 : -1;
        document.getElementById(t.getAttribute('aria-controls')).hidden = !on;
      });
    }
    tabs.forEach(function (tab, i) {
      tab.addEventListener('click', function () { select(tab); });
      tab.addEventListener('keydown', function (e) {
        var next = null;
        if (e.key === 'ArrowRight') next = tabs[(i + 1) % tabs.length];
        if (e.key === 'ArrowLeft') next = tabs[(i - 1 + tabs.length) % tabs.length];
        if (e.key === 'Home') next = tabs[0];
        if (e.key === 'End') next = tabs[tabs.length - 1];
        if (next) { e.preventDefault(); select(next); next.focus(); }
      });
    });
  });

  // ── playground do Button ──
  var demo = document.getElementById('demo');
  var stage = document.getElementById('stage');
  var code = document.getElementById('code');
  var lead = demo.querySelector('.al-btn__icon--leading');
  var trail = demo.querySelector('.al-btn__icon--trailing');
  var label = demo.querySelector('.al-btn__label');
  var input = document.getElementById('labeltext');

  function pick(name) {
    var el = document.querySelector('input[name="' + name + '"]:checked');
    return el ? el.value : null;
  }

  function render() {
    var variant = pick('variant'), size = pick('size');
    var state = pick('state'), icon = pick('icon'), theme = pick('theme');

    demo.className = 'al-btn al-btn--' + variant + ' al-btn--' + size
      + (state === 'hover' || state === 'active' || state === 'focus' ? ' is-' + state : '');

    demo.removeAttribute('aria-disabled');
    demo.removeAttribute('aria-busy');
    if (state === 'disabled') demo.setAttribute('aria-disabled', 'true');
    if (state === 'busy') {
      demo.setAttribute('aria-busy', 'true');
      demo.setAttribute('aria-disabled', 'true');
    }

    lead.hidden = !(icon === 'leading');
    trail.hidden = !(icon === 'trailing');
    label.textContent = input.value || 'Button';

    if (theme === 'auto') stage.removeAttribute('data-theme');
    else stage.setAttribute('data-theme', theme);

    // marcação gerada, na ordem em que o contrato pede
    var cls = 'al-btn al-btn--' + variant + ' al-btn--' + size;
    var attrs = '';
    if (state === 'disabled') attrs = ' aria-disabled="true"';
    if (state === 'busy') attrs = ' aria-busy="true" aria-disabled="true"';
    var lines = ['&lt;button type="button" class="' + cls + '"' + attrs + '&gt;'];
    if (state === 'busy') lines.push('  &lt;span class="al-btn__spinner" aria-hidden="true"&gt;&lt;/span&gt;');
    if (icon === 'leading' && state !== 'busy')
      lines.push('  &lt;span class="al-btn__icon al-btn__icon--leading"&gt;')
      lines.push('    &lt;svg class="al-icon" aria-hidden="true" focusable="false"&gt;&lt;!-- LEADING --&gt;&lt;/svg&gt;')
      lines.push('  &lt;/span&gt;');
    lines.push('  &lt;span class="al-btn__label"&gt;' +
      (input.value || 'Button').replace(/&/g, '&amp;').replace(/</g, '&lt;') + '&lt;/span&gt;');
    if (icon === 'trailing')
      lines.push('  &lt;span class="al-btn__icon al-btn__icon--trailing"&gt;')
      lines.push('    &lt;svg class="al-icon" aria-hidden="true" focusable="false"&gt;&lt;!-- TRAILING --&gt;&lt;/svg&gt;')
      lines.push('  &lt;/span&gt;');
    lines.push('&lt;/button&gt;');
    code.innerHTML = lines.join('\n');
  }

  document.querySelectorAll('.controls input').forEach(function (el) {
    el.addEventListener('change', render);
    el.addEventListener('input', render);
  });

  // filtro da tabela de tokens
  document.querySelectorAll('input[name="tokfilter"]').forEach(function (el) {
    el.addEventListener('change', function () {
      var v = pick('tokfilter');
      document.querySelectorAll('#tokbody tr').forEach(function (tr) {
        tr.hidden = (v !== 'all' && tr.getAttribute('data-variant') !== v);
      });
    });
  });

  // copiar marcação
  document.getElementById('copy').addEventListener('click', function () {
    var btn = this;
    var text = code.textContent;
    var done = function () {
      btn.textContent = 'Copiado';
      setTimeout(function () { btn.textContent = 'Copiar'; }, 1600);
    };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(done, function () { btn.textContent = 'Não deu'; });
    } else {
      var ta = document.createElement('textarea');
      ta.value = text; document.body.appendChild(ta); ta.select();
      try { document.execCommand('copy'); done(); } catch (e) { btn.textContent = 'Não deu'; }
      document.body.removeChild(ta);
    }
  });

  render();
  fromHash();
})();
"""

JS_ICON = r"""
(function () {
  // ── playground do Icon ──
  var stage = document.getElementById('icon-stage');
  if (!stage) return;

  var slot = document.getElementById('icon-slot');
  var code = document.getElementById('icon-code');
  var sel = document.getElementById('icon-name');
  var free = document.getElementById('icon-free');
  var copyBtn = document.getElementById('icon-copy');

  function pick(name) {
    var el = document.querySelector('input[name="' + name + '"]:checked');
    return el ? el.value : null;
  }

  function render() {
    var name = sel.value;
    var box = pick('iconbox');
    var ink = pick('iconink');
    var theme = pick('icontheme');

    free.disabled = box !== 'free';

    // clona o SVG da biblioteca desta mesma pagina: nao existe segunda copia
    var src = document.querySelector('.icon-tile[data-name="' + name + '"] svg');
    if (!src) return;
    var svg = src.cloneNode(true);

    var cls = 'al-icon';
    if (box !== 'free' && box !== '24') cls += ' al-icon--' + box;
    if (ink !== 'inherit') cls += ' al-icon--ink-' + ink;
    svg.setAttribute('class', cls);

    var style = '';
    if (box === 'free') {
      var v = parseInt(free.value, 10);
      if (!v || v < 8 || v > 160) v = 40;
      style = '--al-icon-box: ' + v + 'px';
      svg.setAttribute('style', style);
    }

    slot.innerHTML = '';
    slot.appendChild(svg);

    if (ink === 'on-brand' || ink === 'on-solid') stage.setAttribute('data-ink', ink);
    else stage.removeAttribute('data-ink');

    if (theme === 'auto') stage.removeAttribute('data-theme');
    else stage.setAttribute('data-theme', theme);

    var attrs = ' class="' + cls + '"';
    if (style) attrs += ' style="' + style + '"';
    code.textContent = '<svg' + attrs + ' aria-hidden="true" focusable="false">\n'
      + '  <!-- ' + name + ' \u00b7 components/icon/icons/' + name + '.svg -->\n'
      + '</svg>';
  }

  sel.addEventListener('change', render);
  free.addEventListener('input', render);
  document.querySelectorAll('input[name="iconbox"], input[name="iconink"], input[name="icontheme"]')
    .forEach(function (el) { el.addEventListener('change', render); });

  // clicar num icone da biblioteca leva ele para o palco e copia o nome
  document.querySelectorAll('.icon-tile').forEach(function (t) {
    t.addEventListener('click', function () {
      sel.value = t.dataset.name;
      render();
      if (navigator.clipboard) navigator.clipboard.writeText(t.dataset.name).catch(function () {});
      t.classList.add('is-copied');
      setTimeout(function () { t.classList.remove('is-copied'); }, 900);
    });
  });

  if (copyBtn) {
    copyBtn.addEventListener('click', function () {
      if (navigator.clipboard) navigator.clipboard.writeText(code.textContent);
      copyBtn.textContent = 'Copiado';
      setTimeout(function () { copyBtn.textContent = 'Copiar'; }, 1200);
    });
  }

  render();
})();
"""


# Os rótulos saem da mesma lista que monta os controles - uma fonte só, senão o
# aria-label do playground e o texto do botão podem divergir sem ninguém ver.
JS_IB_DATA = ('var ROTULOS = '
              + json.dumps([[v, l] for v, l in IB_ICON_CHOICES], ensure_ascii=False) + ';\n')

JS_ICONBUTTON = r"""
(function () {
  // ── playground do Icon Button ──
  var demo = document.getElementById('ib-demo');
  if (!demo) return;

  var stage = document.getElementById('ib-stage');
  var code = document.getElementById('ib-code');

  // Os desenhos saem da própria página: o playground clona o svg que já está
  // nas Diretrizes, em vez de carregar uma segunda cópia de cada ícone.
  var SVG = {};
  ROTULOS.forEach(function (par) {
    var achado = document.querySelector('.al-icon-btn[aria-label="' + par[1] + '"] svg');
    if (achado) SVG[par[0]] = achado.outerHTML;
  });

  function pick(name) {
    var el = document.querySelector('input[name="' + name + '"]:checked');
    return el ? el.value : null;
  }

  function rotulo(nome) {
    for (var i = 0; i < ROTULOS.length; i++) {
      if (ROTULOS[i][0] === nome) return ROTULOS[i][1];
    }
    return nome;
  }

  function render() {
    var variant = pick('ibvariant'), size = pick('ibsize');
    var state = pick('ibstate'), icone = pick('ibicon'), theme = pick('ibtheme');
    var rot = rotulo(icone);

    demo.className = 'al-icon-btn al-icon-btn--' + variant + ' al-icon-btn--' + size
      + (state === 'hover' || state === 'active' || state === 'focus' ? ' is-' + state : '');

    // O nome acessível acompanha o ícone. Não é enfeite do playground: um
    // Icon Button com aria-label de outro desenho é exatamente o erro que a
    // regra 06 descreve, e a vitrine não pode ensinar isso.
    demo.setAttribute('aria-label', rot);

    demo.removeAttribute('aria-disabled');
    demo.removeAttribute('aria-busy');
    if (state === 'disabled') demo.setAttribute('aria-disabled', 'true');
    if (state === 'busy') {
      demo.setAttribute('aria-busy', 'true');
      demo.setAttribute('aria-disabled', 'true');
    }

    var svg = demo.querySelector('svg');
    if (svg && SVG[icone]) svg.outerHTML = SVG[icone];

    if (theme === 'auto') stage.removeAttribute('data-theme');
    else stage.setAttribute('data-theme', theme);

    var cls = 'al-icon-btn al-icon-btn--' + variant + ' al-icon-btn--' + size;
    var attrs = '';
    if (state === 'disabled') attrs = ' aria-disabled="true"';
    if (state === 'busy') attrs = ' aria-busy="true" aria-disabled="true"';
    var lines = [
      '&lt;button type="button" class="' + cls + '"',
      '        aria-label="' + rot + '"' + attrs + '&gt;',
      '  &lt;span class="al-icon-btn__spinner" aria-hidden="true"&gt;&lt;/span&gt;',
      '  &lt;svg class="al-icon" aria-hidden="true" focusable="false"&gt;&lt;!-- ' +
        icone.toUpperCase() + ' --&gt;&lt;/svg&gt;',
      '&lt;/button&gt;'
    ];
    if (state === 'busy') {
      lines.push('');
      lines.push('&lt;!-- sem rótulo para trocar: o aviso vai aqui --&gt;');
      lines.push('&lt;p role="status" aria-live="polite" class="vh"&gt;' + rot + '…&lt;/p&gt;');
    }
    code.innerHTML = lines.join('\n');
  }

  document.querySelectorAll('#ib-controls input').forEach(function (el) {
    el.addEventListener('change', render);
  });

  document.querySelectorAll('input[name="ibtokfilter"]').forEach(function (el) {
    el.addEventListener('change', function () {
      var v = pick('ibtokfilter');
      document.querySelectorAll('#ibtokbody tr').forEach(function (tr) {
        tr.hidden = (v !== 'all' && tr.getAttribute('data-variant') !== v);
      });
    });
  });

  document.getElementById('ib-copy').addEventListener('click', function () {
    var btn = this;
    var text = code.textContent;
    var done = function () {
      btn.textContent = 'Copiado';
      setTimeout(function () { btn.textContent = 'Copiar'; }, 1600);
    };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(done, function () { btn.textContent = 'Não deu'; });
    } else {
      var ta = document.createElement('textarea');
      ta.value = text; document.body.appendChild(ta); ta.select();
      try { document.execCommand('copy'); done(); } catch (e) { btn.textContent = 'Não deu'; }
      document.body.removeChild(ta);
    }
  });

  render();
})();
"""

JS_TAG_DATA = ('var TAG_X = ' + json.dumps(al_icon('x')) + ';\n')

JS_TAG = r"""
(function () {
  // ── playground do Tag ──
  var stage = document.getElementById('tag-stage');
  if (!stage) return;
  var code = document.getElementById('tag-code');
  var labelInput = document.getElementById('tag-label');

  function pick(name) {
    var el = document.querySelector('input[name="' + name + '"]:checked');
    return el ? el.value : null;
  }

  function render() {
    var tipo = pick('tagtype'), status = pick('tagstatus'), size = pick('tagsize');
    var dis = pick('tagdis') === 'yes', theme = pick('tagtheme');
    var texto = (labelInput.value || '').trim() || 'Tag';

    if (theme === 'auto') stage.removeAttribute('data-theme');
    else stage.setAttribute('data-theme', theme);

    var cls = 'al-tag al-tag--' + tipo + ' al-tag--' + status + ' al-tag--' + size;

    // O nome acessível do X inclui o rótulo. Não é enfeite do playground: é a
    // regra 08 das Diretrizes, e a vitrine não pode ensinar o contrário.
    // tabindex="-1" porque esta é uma vitrine — a tag do playground não deve
    // virar uma parada de tab no meio da leitura da página.
    var x = dis
      ? '<button type="button" class="al-tag__dismiss" aria-label="Remover ' + texto +
        '" tabindex="-1">' + TAG_X + '</button>'
      : '';
    stage.innerHTML = '<span class="' + cls + '">' + texto + x + '</span>';

    var lines = dis
      ? ['&lt;span class="' + cls + '"&gt;',
         '  ' + texto,
         '  &lt;button type="button" class="al-tag__dismiss"',
         '          aria-label="Remover ' + texto + '"&gt;',
         '    &lt;svg class="al-icon" aria-hidden="true" focusable="false"&gt;&lt;!-- X --&gt;&lt;/svg&gt;',
         '  &lt;/button&gt;',
         '&lt;/span&gt;',
         '',
         '&lt;!-- ao remover, mova o foco para a tag anterior do grupo --&gt;']
      : ['&lt;span class="' + cls + '"&gt;' + texto + '&lt;/span&gt;'];
    code.innerHTML = lines.join('\n');
  }

  document.querySelectorAll('#tag-controls input').forEach(function (i) {
    i.addEventListener('input', render);
  });

  document.querySelectorAll('input[name="tagtokfilter"]').forEach(function (i) {
    i.addEventListener('change', function () {
      var v = pick('tagtokfilter');
      document.querySelectorAll('#tagtokbody tr').forEach(function (tr) {
        tr.hidden = (v !== 'all' && tr.getAttribute('data-type') !== v);
      });
    });
  });

  document.getElementById('tag-copy').addEventListener('click', function () {
    var btn = this;
    var text = code.textContent;
    var done = function () {
      btn.textContent = 'Copiado';
      setTimeout(function () { btn.textContent = 'Copiar'; }, 1600);
    };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(done, function () { btn.textContent = 'Não deu'; });
    } else {
      var ta = document.createElement('textarea');
      ta.value = text; document.body.appendChild(ta); ta.select();
      try { document.execCommand('copy'); done(); } catch (e) { btn.textContent = 'Não deu'; }
      document.body.removeChild(ta);
    }
  });

  render();
})();
"""


CHROME_ICON = """
/* ── biblioteca de ícones ──
   Casca do site. O componente em si é o .al-icon, que vem do icon.css real. */
.th-icons{display:flex; gap:11px; color:var(--al-text-primary)}
.icon-grid{display:grid; grid-template-columns:repeat(auto-fill,minmax(118px,1fr)); gap:4px;
  margin-bottom:6px}
.icon-tile{
  appearance:none; border:0; background:none; font:inherit; cursor:pointer;
  display:flex; flex-direction:column; align-items:center; gap:11px;
  padding:18px 8px 13px; border-radius:10px; color:var(--al-text-primary);
}
.icon-tile:hover{background:var(--al-bg-hover)}
.icon-tile:focus-visible{outline:2px solid var(--al-border-focus); outline-offset:-2px}
.icon-tile.is-copied{background:var(--al-bg-brand-subtle); color:var(--al-text-brand)}
.icon-tile span{
  font-family:var(--al-font-mono); font-size:10.5px; line-height:14px;
  color:var(--al-text-secondary); text-align:center; word-break:break-word;
}
.icon-tile.is-copied span{color:var(--al-text-brand)}
/* as duas tintas que só existem sobre preenchimento levam o palco junto */
#icon-stage[data-ink="on-brand"]{background-color:var(--al-bg-brand)}
#icon-stage[data-ink="on-solid"]{background-color:var(--al-bg-danger)}
#icon-slot{display:grid; place-items:center; min-height:96px}
"""


JS_AVATAR_DATA = ('var AV_ICON = ' + json.dumps(al_icon('user')) + ';\n'
                  'var AV_PHOTO = ' + json.dumps(PHOTO_A) + ';\n')

JS_AVATAR = r"""
(function () {
  // ── playground do Avatar ──
  var stage = document.getElementById('avatar-stage');
  if (!stage) return;
  var code = document.getElementById('avatar-code');
  var nameInput = document.getElementById('avatar-name');

  function pick(name) {
    var el = document.querySelector('input[name="' + name + '"]:checked');
    return el ? el.value : null;
  }

  // A regra 08 das Diretrizes, do lado do JS: duas letras, maiúsculas. A
  // vitrine não pode ensinar um contrato que ela mesma não cumpre.
  function iniciais(nome) {
    var partes = nome.split(/\s+/).filter(Boolean);
    if (!partes.length) return '?';
    var duas = partes[0].charAt(0) + (partes.length > 1 ? partes[partes.length - 1].charAt(0) : '');
    return duas.toUpperCase();
  }

  function render() {
    var tipo = pick('avtype'), size = pick('avsize');
    var solo = pick('avctx') === 'solo', theme = pick('avtheme');
    var nome = (nameInput.value || '').trim() || 'Maria Silva';

    if (theme === 'auto') stage.removeAttribute('data-theme');
    else stage.setAttribute('data-theme', theme);

    var cls = 'al-avatar al-avatar--' + size;

    // O contrato inteiro do componente mora nestas duas linhas: sozinho o
    // avatar É a informação e precisa de nome; ao lado do nome escrito ele
    // sai da árvore de acessibilidade.
    var a11y = solo ? 'role="img" aria-label="' + nome + '"' : 'aria-hidden="true"';

    var filho, filhoCode;
    if (tipo === 'photo') {
      filho = '<img class="al-avatar__photo" src="' + AV_PHOTO + '" alt="">';
      filhoCode = '&lt;img class="al-avatar__photo" src="…" alt=""&gt;';
    } else if (tipo === 'icon') {
      filho = AV_ICON;
      filhoCode = '&lt;svg class="al-icon" aria-hidden="true" focusable="false"&gt;'
                + '&lt;!-- user --&gt;&lt;/svg&gt;';
    } else {
      filho = '<span class="al-avatar__initials">' + iniciais(nome) + '</span>';
      filhoCode = '&lt;span class="al-avatar__initials"&gt;' + iniciais(nome) + '&lt;/span&gt;';
    }

    var avatar = '<span class="' + cls + '" ' + a11y + '>' + filho + '</span>';
    stage.innerHTML = solo
      ? avatar
      : '<span class="av-person">' + avatar +
        '<span class="av-who"><b>' + nome + '</b><i>Comentou há 2 horas</i></span></span>';

    var a11yCode = solo
      ? 'role="img" aria-label="' + nome + '"'
      : 'aria-hidden="true"';
    var lines = ['&lt;span class="' + cls + '" ' + a11yCode + '&gt;',
                 '  ' + filhoCode,
                 '&lt;/span&gt;'];
    if (!solo) {
      lines.push('&lt;!-- o nome está escrito ao lado, então o avatar é decorativo --&gt;');
    }
    code.innerHTML = lines.join('\n');
  }

  document.querySelectorAll('#avatar-controls input').forEach(function (i) {
    i.addEventListener('input', render);
  });

  document.getElementById('avatar-copy').addEventListener('click', function () {
    var btn = this;
    var text = code.textContent;
    var done = function () {
      btn.textContent = 'Copiado';
      setTimeout(function () { btn.textContent = 'Copiar'; }, 1600);
    };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(done, function () { btn.textContent = 'Não deu'; });
    } else {
      var ta = document.createElement('textarea');
      ta.value = text; document.body.appendChild(ta); ta.select();
      try { document.execCommand('copy'); done(); } catch (e) { btn.textContent = 'Não deu'; }
      document.body.removeChild(ta);
    }
  });

  render();
})();
"""


CHROME_AVATAR = """
/* ── páginas do Avatar ──
   Casca do site. O componente em si é o .al-avatar, que vem do avatar.css real. */
.av-person{display:inline-flex; align-items:center; gap:12px}
.av-who{display:flex; flex-direction:column; line-height:1.3}
.av-who b{font-size:14px; font-weight:500; color:var(--al-text-primary)}
.av-who i{font-size:12px; font-style:normal; color:var(--al-text-secondary)}

.av-list{display:flex; flex-direction:column; gap:14px; align-items:flex-start}
.av-profile{display:flex; align-items:center; gap:16px}
.av-profile b{display:block; font-size:18px; font-weight:600; color:var(--al-text-primary)}
.av-profile span{font-size:13px; color:var(--al-text-secondary)}

.av-chain{display:flex; align-items:flex-start; gap:10px; flex-wrap:wrap; margin-top:18px}
.av-chain-step{
  flex:1 1 190px; display:flex; flex-direction:column; align-items:center; gap:10px;
  padding:22px 16px; border-radius:12px; background:var(--al-bg-surface); text-align:center;
}
.av-chain-step b{font-size:14px; font-weight:600}
.av-chain-step span{font-size:12.5px; line-height:18px; color:var(--al-text-secondary)}
.av-chain-step i{font-style:normal; color:var(--al-text-placeholder)}
.av-chain-arrow{
  align-self:center; display:grid; place-items:center; width:22px; height:22px;
  color:var(--al-text-placeholder); transform:rotate(-90deg); flex:none;
}
.av-chain-arrow svg{width:16px; height:16px}

.av-grid{display:flex; flex-direction:column; gap:6px}
.av-grid-row{display:flex; align-items:center; gap:18px; padding:14px 0;
  border-bottom:1px solid var(--al-border-subtle)}
.av-grid-row:last-child{border-bottom:0}
.av-grid-name{width:80px; flex:none; font-size:13px; font-weight:500;
  color:var(--al-text-secondary)}
.av-grid-cells{display:flex; align-items:flex-end; gap:28px; flex-wrap:wrap}
.av-cell{display:flex; flex-direction:column; align-items:center; gap:8px}
.av-cell span{font-family:var(--al-font-mono); font-size:10.5px;
  color:var(--al-text-secondary)}
"""

CHROME_SELECT = """
/* ── miniatura do card do Select ── */
.th-select{display:flex; justify-content:center; width:100%}
.th-select__field{
  display:flex; align-items:center; justify-content:space-between; gap:10px;
  width:100%; max-width:200px;
  padding:8px 10px;
  border:1px solid var(--al-border-default); border-radius:var(--al-radius-lg);
  background:var(--al-bg-surface-raised);
  color:var(--al-text-placeholder);
  font-size:12.5px; line-height:16px;
}
.th-select__field .al-icon{--al-icon-box:16px; color:var(--al-text-primary)}
/* o palco do playground precisa de largura: o campo ocupa 100% do contêiner */
#select-stage{display:block; padding-inline:8px}
#select-stage .al-select{max-width:360px; margin-inline:auto}
"""

JS_SELECT_DATA = ('var SEL_CHEVRON = ' + json.dumps(SELECT_CHEVRON) + ';\n'
                  'var SEL_UFS = ' + json.dumps(SELECT_UFS) + ';\n')

JS_SELECT = r"""
(function () {
  // ── playground do Select ──
  var stage = document.getElementById('select-stage');
  if (!stage) return;
  var code = document.getElementById('select-code');
  var labelInput = document.getElementById('select-label');

  function pick(name) {
    var el = document.querySelector('input[name="' + name + '"]:checked');
    return el ? el.value : null;
  }

  function esc(s) {
    return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  function render() {
    var estado = pick('selstate');
    var comValor = pick('selvalue') === 'picked';
    var opcional = pick('selopt') === 'opt';
    var comApoio = pick('selhelp') === 'on';
    var theme = pick('seltheme');
    var rotulo = (labelInput.value || '').trim() || 'Estado';

    if (theme === 'auto') stage.removeAttribute('data-theme');
    else stage.setAttribute('data-theme', theme);

    var erro = estado === 'error';
    var off = estado === 'disabled';
    // O erro SUBSTITUI o apoio, nunca empilha - regra do Spectrum, e a mesma
    // razao de haver um unico slot no componente.
    var msg = erro ? 'Escolha um estado para continuar'
                   : (comApoio ? 'Onde a nota será emitida' : null);

    var attrs = ['id="pg-select"', 'class="al-select__field"'];
    if (erro) attrs.push('aria-invalid="true"');
    if (off) attrs.push('disabled');
    if (msg) attrs.push('aria-describedby="pg-select-help"');

    var opts = ['<option value="" disabled' + (comValor ? '' : ' selected')
                + '>Selecione o estado</option>'];
    SEL_UFS.forEach(function (uf) {
      opts.push('<option value="' + uf + '"'
                + (comValor && uf === 'Bahia' ? ' selected' : '') + '>' + uf + '</option>');
    });

    var marca = opcional ? '<span class="al-select__optional">(Opcional)</span>' : '';
    var linha = msg ? '<p class="al-select__help" id="pg-select-help">' + msg + '</p>' : '';

    stage.innerHTML =
      '<div class="al-select">'
      + '<div class="al-select__labelrow">'
      + '<label class="al-select__label" for="pg-select">' + esc(rotulo) + '</label>'
      + marca + '</div>'
      + '<div class="al-select__control">'
      + '<select ' + attrs.join(' ') + '>' + opts.join('') + '</select>'
      + SEL_CHEVRON + '</div>'
      + linha + '</div>';

    // A marcação mostrada é a que importa: o que muda entre estados é atributo,
    // nunca classe. Se um dia aparecer uma classe de erro aqui, é regressão.
    var lines = ['&lt;div class="al-select"&gt;',
                 '  &lt;div class="al-select__labelrow"&gt;',
                 '    &lt;label class="al-select__label" for="uf"&gt;' + esc(rotulo) + '&lt;/label&gt;'];
    if (opcional) lines.push('    &lt;span class="al-select__optional"&gt;(Opcional)&lt;/span&gt;');
    lines.push('  &lt;/div&gt;');
    lines.push('  &lt;div class="al-select__control"&gt;');
    var sattrs = 'class="al-select__field" id="uf"';
    if (erro) sattrs += ' aria-invalid="true"';
    if (off) sattrs += ' disabled';
    if (msg) sattrs += ' aria-describedby="uf-help"';
    lines.push('    &lt;select ' + sattrs + '&gt;');
    lines.push('      &lt;option value="" disabled' + (comValor ? '' : ' selected')
               + '&gt;Selecione o estado&lt;/option&gt;');
    lines.push('      &lt;!-- … --&gt;');
    lines.push('    &lt;/select&gt;');
    lines.push('    &lt;svg class="al-icon al-select__chevron" aria-hidden="true" '
               + 'focusable="false"&gt;&lt;!-- chevron-down --&gt;&lt;/svg&gt;');
    lines.push('  &lt;/div&gt;');
    if (msg) {
      lines.push('  &lt;p class="al-select__help" id="uf-help"&gt;' + msg + '&lt;/p&gt;');
    }
    lines.push('&lt;/div&gt;');
    if (erro) {
      lines.push('&lt;!-- o erro vem de aria-invalid, nunca de uma classe --&gt;');
    }
    code.innerHTML = lines.join('\n');
  }

  document.querySelectorAll('#select-controls input').forEach(function (i) {
    i.addEventListener('input', render);
  });

  document.getElementById('select-copy').addEventListener('click', function () {
    var btn = this;
    var text = code.textContent;
    navigator.clipboard.writeText(text).then(function () {
      btn.textContent = 'Copiado';
      setTimeout(function () { btn.textContent = 'Copiar'; }, 1400);
    });
  });

  render();
})();
"""


CHROME_CHECKBOX = """
/* ── miniatura do card do Checkbox ── */
.th-cbx{display:flex; flex-direction:column; gap:8px; font-size:12.5px; line-height:16px;
  color:var(--al-text-primary)}
.th-cbx__row{display:flex; align-items:center; gap:8px}
.th-cbx__box{display:inline-flex; align-items:center; justify-content:center;
  width:16px; height:16px; box-sizing:border-box;
  border:1px solid var(--al-border-default); border-radius:var(--al-radius-sm);
  background:var(--al-bg-surface-raised)}
.th-cbx__box.is-on{background:var(--al-bg-brand); border-color:var(--al-bg-brand);
  color:var(--al-text-on-brand)}
.th-cbx__box .al-icon{--al-icon-box:12px}
/* palcos: o checkbox e inline-flex; aqui ele empilha com a mensagem do formulario */
.cbx-stage{display:flex !important; flex-direction:column; align-items:flex-start; gap:8px}
#cbx-stage{display:flex; flex-direction:column; align-items:center; gap:8px; padding-inline:16px}
.cbx-formerror{margin:0; color:var(--al-text-danger); font-size:13.5px; line-height:20px}
.cbx-group{display:flex; flex-direction:column; gap:12px; margin:0; padding:0; border:0; min-width:0}
.cbx-group legend{padding:0; margin-bottom:12px; font-weight:600}
.cbx-children{display:flex; flex-direction:column; gap:12px; padding-inline-start:32px}
"""

JS_CHECKBOX_DATA = ('var CBX_CHECK = ' + json.dumps(CBX_CHECK) + ';\n'
                    'var CBX_DASH = ' + json.dumps(CBX_DASH) + ';\n')

JS_CHECKBOX = r"""
(function () {
  // ── Checkbox: o misto so existe por JS (regra 8) ──
  [].slice.call(document.querySelectorAll('[data-indeterminate]')).forEach(function (el) {
    el.indeterminate = true;
  });

  // ── pai e filhos da Visao geral ──
  var pai = document.querySelector('[data-cbx-pai]');
  var filhos = [].slice.call(document.querySelectorAll('[data-cbx-filho]'));
  if (pai && filhos.length) {
    var sync = function () {
      var n = filhos.filter(function (f) { return f.checked; }).length;
      pai.checked = n === filhos.length;
      pai.indeterminate = n > 0 && n < filhos.length;
    };
    filhos.forEach(function (f) { f.addEventListener('change', sync); });
    pai.addEventListener('change', function () {
      filhos.forEach(function (f) { f.checked = pai.checked; });
      pai.indeterminate = false;
    });
    sync();
  }

  // ── playground ──
  var stage = document.getElementById('cbx-stage');
  if (!stage) return;
  var code = document.getElementById('cbx-code');
  var labelInput = document.getElementById('cbx-label');

  function pick(name) {
    var el = document.querySelector('input[name="' + name + '"]:checked');
    return el ? el.value : null;
  }
  function esc(s) {
    return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  function render() {
    var valor = pick('cbxvalue');
    var estado = pick('cbxstate');
    var theme = pick('cbxtheme');
    var rotulo = (labelInput.value || '').trim() || 'Receber novidades por e-mail';

    if (theme === 'auto') stage.removeAttribute('data-theme');
    else stage.setAttribute('data-theme', theme);

    var erro = estado === 'error';
    var off = estado === 'disabled';
    var attrs = ['id="pg-cbx"', 'class="al-checkbox__input"', 'type="checkbox"'];
    if (valor === 'on') attrs.push('checked');
    if (off) attrs.push('disabled');
    if (erro) attrs.push('aria-invalid="true"', 'aria-describedby="pg-cbx-erro"');

    stage.innerHTML =
      '<label class="al-checkbox"><span class="al-checkbox__control">'
      + '<input ' + attrs.join(' ') + '>' + CBX_CHECK + CBX_DASH + '</span>'
      + '<span class="al-checkbox__label">' + esc(rotulo) + '</span></label>'
      + (erro ? '<p class="cbx-formerror" id="pg-cbx-erro">Aceite para continuar.</p>' : '');
    if (valor === 'mixed') document.getElementById('pg-cbx').indeterminate = true;

    // O que muda entre estados e atributo, nunca classe.
    var iattrs = 'class="al-checkbox__input" type="checkbox" name="news"';
    if (valor === 'on') iattrs += ' checked';
    if (off) iattrs += ' disabled';
    if (erro) iattrs += ' aria-invalid="true" aria-describedby="news-erro"';
    var lines = [];
    if (erro) {
      lines.push('&lt;!-- a mensagem e do FORMULARIO, nao do componente --&gt;');
      lines.push('&lt;p id="news-erro"&gt;Aceite para continuar.&lt;/p&gt;');
    }
    lines.push('&lt;label class="al-checkbox"&gt;');
    lines.push('  &lt;span class="al-checkbox__control"&gt;');
    lines.push('    &lt;input ' + iattrs + '&gt;');
    lines.push('    &lt;svg class="al-icon al-checkbox__check" aria-hidden="true" focusable="false"&gt;&lt;!-- check --&gt;&lt;/svg&gt;');
    lines.push('    &lt;svg class="al-icon al-checkbox__dash" aria-hidden="true" focusable="false"&gt;&lt;!-- minus --&gt;&lt;/svg&gt;');
    lines.push('  &lt;/span&gt;');
    lines.push('  &lt;span class="al-checkbox__label"&gt;' + esc(rotulo) + '&lt;/span&gt;');
    lines.push('&lt;/label&gt;');
    if (valor === 'mixed') {
      lines.push('&lt;script&gt;');
      lines.push('  // o misto nao tem atributo HTML: so por JavaScript');
      lines.push('  input.indeterminate = true;');
      lines.push('&lt;/script&gt;');
    }
    code.innerHTML = lines.join('\n');
  }

  document.querySelectorAll('#cbx-controls input').forEach(function (i) {
    i.addEventListener('input', render);
  });
  document.getElementById('cbx-copy').addEventListener('click', function () {
    var btn = this;
    navigator.clipboard.writeText(code.textContent).then(function () {
      btn.textContent = 'Copiado';
      setTimeout(function () { btn.textContent = 'Copiar'; }, 1400);
    }).catch(function () {});
  });
  render();
})();
"""


CHROME_RADIO = """
/* ── miniatura do card do Radio ── */
.th-rd{display:flex; flex-direction:column; gap:8px; font-size:12.5px; line-height:16px;
  color:var(--al-text-primary)}
.th-rd__row{display:flex; align-items:center; gap:8px}
.th-rd__dot{position:relative; width:16px; height:16px; box-sizing:border-box;
  border:1px solid var(--al-border-default); border-radius:var(--al-radius-full);
  background:var(--al-bg-surface-raised)}
.th-rd__dot.is-on{border-color:var(--al-border-brand)}
.th-rd__dot.is-on::after{content:""; position:absolute; inset:3px; border-radius:inherit;
  background:var(--al-bg-brand)}
/* a pergunta: fieldset nativo, montado pela aplicacao (regra 6) */
.rd-stage{display:flex !important; flex-direction:column; align-items:flex-start; gap:8px}
#rd-stage{display:flex; flex-direction:column; align-items:center; gap:8px; padding-inline:16px}
.rd-group{margin:0; padding:0; border:0; min-width:0}
.rd-group legend{padding:0; margin-bottom:12px; font-weight:600}
.rd-opts{display:flex; flex-direction:column; gap:12px}
.rd-group--row .rd-opts{flex-direction:row; flex-wrap:wrap; column-gap:32px}
.rd-formerror{margin:0; color:var(--al-text-danger); font-size:13.5px; line-height:20px}
.rd-form{display:flex; flex-direction:column; gap:20px; align-items:flex-start}
.rd-summary{margin:0; padding:12px 16px; border-radius:var(--al-radius-md);
  background:var(--al-bg-danger-subtle); color:var(--al-text-danger); font-size:13.5px; line-height:20px}
.rd-actions{display:flex; gap:12px; flex-wrap:wrap; align-items:center}
.rd-ok{margin:0; color:var(--al-text-success); font-size:13.5px}
"""

JS_RADIO = r"""
(function () {
  // ── Radio: a pergunta de verdade da Visao geral (regras 21, 22, 26) ──
  // O erro e da pergunta: o fieldset leva aria-invalid e aria-describedby.
  var form = document.getElementById('rd-form');
  if (form) {
    var fs = form.querySelector('fieldset');
    var opcoes = [].slice.call(fs.querySelectorAll('.al-radio__input'));
    var resumo = document.getElementById('rd-form-erro');
    var ok = document.getElementById('rd-form-ok');
    var marcar = function (sim) {
      if (sim) {
        fs.setAttribute('aria-invalid', 'true');
        fs.setAttribute('aria-describedby', 'rd-form-erro');
      } else {
        fs.removeAttribute('aria-invalid');
        fs.removeAttribute('aria-describedby');
      }
      resumo.hidden = !sim;
    };
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      ok.textContent = '';
      if (!opcoes.some(function (o) { return o.checked; })) {
        marcar(true);
        opcoes.filter(function (o) { return !o.disabled; })[0].focus();
        return;
      }
      marcar(false);
      ok.textContent = 'Assinatura enviada.';
    });
    opcoes.forEach(function (o) { o.addEventListener('change', function () { marcar(false); }); });
  }

  // ── playground ──
  var stage = document.getElementById('rd-stage');
  if (!stage) return;
  var code = document.getElementById('rd-code');
  var legendInput = document.getElementById('rd-legend');
  var OPCOES = [['mensal', 'Mensal'], ['anual', 'Anual'], ['empresa', 'Empresarial']];

  function pick(name) {
    var el = document.querySelector('input[name="' + name + '"]:checked');
    return el ? el.value : null;
  }
  function esc(s) {
    return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  function render() {
    var valor = pick('rdvalue');
    var estado = pick('rdstate');
    var theme = pick('rdtheme');
    var pergunta = (legendInput.value || '').trim() || 'Cobrança';

    if (theme === 'auto') stage.removeAttribute('data-theme');
    else stage.setAttribute('data-theme', theme);

    var erro = estado === 'error';
    var fsAttrs = 'class="rd-group"' + (erro ? ' aria-invalid="true" aria-describedby="pg-rd-erro"' : '');
    var html = '<fieldset ' + fsAttrs + '><legend>' + esc(pergunta) + '</legend><div class="rd-opts">';
    var linhas = [];
    if (erro) {
      linhas.push('&lt;!-- o erro e da PERGUNTA: aria-invalid no fieldset, nunca no radio --&gt;');
      linhas.push('&lt;fieldset aria-invalid="true" aria-describedby="cobranca-erro"&gt;');
    } else {
      linhas.push('&lt;fieldset&gt;');
    }
    linhas.push('  &lt;legend&gt;' + esc(pergunta) + '&lt;/legend&gt;');
    OPCOES.forEach(function (o, i) {
      var marcado = valor === 'first' && i === 0;
      var off = estado === 'disabled' && i === OPCOES.length - 1;
      var a = 'class="al-radio__input" type="radio" name="pg-rd" value="' + o[0] + '"'
        + (marcado ? ' checked' : '') + (off ? ' disabled' : '');
      html += '<label class="al-radio"><span class="al-radio__control"><input id="pg-rd-' + i + '" ' + a + '>'
        + '<span class="al-radio__dot" aria-hidden="true"></span></span>'
        + '<span class="al-radio__label">' + o[1] + '</span></label>';
      var ia = 'class="al-radio__input" type="radio" name="cobranca" value="' + o[0] + '"'
        + (marcado ? ' checked' : '') + (off ? ' disabled' : '');
      linhas.push('  &lt;label class="al-radio"&gt;');
      linhas.push('    &lt;span class="al-radio__control"&gt;');
      linhas.push('      &lt;input ' + ia + '&gt;');
      linhas.push('      &lt;span class="al-radio__dot" aria-hidden="true"&gt;&lt;/span&gt;');
      linhas.push('    &lt;/span&gt;');
      linhas.push('    &lt;span class="al-radio__label"&gt;' + o[1] + '&lt;/span&gt;');
      linhas.push('  &lt;/label&gt;');
    });
    html += '</div></fieldset>';
    linhas.push('&lt;/fieldset&gt;');
    if (erro) {
      html += '<p class="rd-formerror" id="pg-rd-erro">Escolha uma forma de cobrança.</p>';
      linhas.push('&lt;!-- a mensagem e do FORMULARIO, nao do componente --&gt;');
      linhas.push('&lt;p id="cobranca-erro"&gt;Escolha uma forma de cobrança.&lt;/p&gt;');
    }
    stage.innerHTML = html;
    code.innerHTML = linhas.join('\n');
  }

  document.querySelectorAll('#rd-controls input').forEach(function (i) {
    i.addEventListener('input', render);
  });
  document.getElementById('rd-copy').addEventListener('click', function () {
    var btn = this;
    navigator.clipboard.writeText(code.textContent).then(function () {
      btn.textContent = 'Copiado';
      setTimeout(function () { btn.textContent = 'Copiar'; }, 1400);
    }).catch(function () {});
  });
  render();
})();
"""

CHROME_SWITCH = """
/* ── miniatura do card do Switch ── */
.th-sw{display:flex; flex-direction:column; gap:8px; font-size:12.5px; line-height:16px;
  color:var(--al-text-primary)}
.th-sw__row{display:flex; align-items:center; gap:8px}
.th-sw__track{position:relative; width:26px; height:16px; box-sizing:border-box;
  border:1px solid var(--al-border-default); border-radius:var(--al-radius-full);
  background:var(--al-bg-surface)}
.th-sw__thumb{position:absolute; top:3px; left:3px; width:8px; height:8px;
  border-radius:inherit; background:var(--al-bg-thumb)}
.th-sw__track.is-on{background:var(--al-bg-brand); border-color:var(--al-border-brand)}
.th-sw__track.is-on .th-sw__thumb{left:13px; background:var(--al-text-on-brand)}
/* grupo de configuracoes: montado pela aplicacao (regra 6) */
.sw-stage{display:flex !important; flex-direction:column; align-items:flex-start; gap:8px}
#sw-stage{display:flex; flex-direction:column; align-items:center; gap:8px; padding-inline:16px}
.sw-settings{display:flex; flex-direction:column; gap:16px; align-items:flex-start}
.sw-group{margin:0; padding:0; border:0; min-width:0}
.sw-group legend{padding:0; margin-bottom:12px; font-weight:600}
.sw-opts{display:flex; flex-direction:column; gap:16px}
.sw-status{margin:0; font-size:13.5px; line-height:20px}
.sw-status:empty{display:none}
.sw-status.is-erro{padding:12px 16px; border-radius:var(--al-radius-md);
  background:var(--al-bg-danger-subtle); color:var(--al-text-danger)}
.sw-status.is-ok{color:var(--al-text-success)}
"""

JS_SWITCH = r"""
(function () {
  // ── Switch: a tela de configuracoes da Visao geral ──
  // Dependencia (regra 17) e falha com recuo, opcao A (regra 21).
  var email = document.getElementById('ov-sw-email');
  if (email) {
    var resumo = document.getElementById('ov-sw-resumo');
    var contador = document.getElementById('ov-sw-contador');
    var status = document.getElementById('ov-sw-status');
    var dep = function () { resumo.disabled = !email.checked; };
    email.addEventListener('change', dep);
    dep();
    contador.addEventListener('change', function () {
      var pedido = contador.checked;
      status.className = 'sw-status';
      status.textContent = '';
      setTimeout(function () {
        if (pedido) {
          contador.checked = false;
          status.className = 'sw-status is-erro';
          status.textContent = 'Não foi possível ativar o envio ao contador: nenhum contador cadastrado.';
        } else {
          status.className = 'sw-status is-ok';
          status.textContent = 'Envio ao contador desativado.';
        }
      }, 700);
    });
  }

  // ── playground ──
  var stage = document.getElementById('sw-stage');
  if (!stage) return;
  var code = document.getElementById('sw-code');
  var labelInput = document.getElementById('sw-label');

  function pick(name) {
    var el = document.querySelector('input[name="' + name + '"]:checked');
    return el ? el.value : null;
  }
  function esc(s) {
    return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  function render() {
    var ligado = pick('swvalue') === 'on';
    var off = pick('swstate') === 'disabled';
    var theme = pick('swtheme');
    var rotulo = (labelInput.value || '').trim() || 'Notificações por e-mail';

    if (theme === 'auto') stage.removeAttribute('data-theme');
    else stage.setAttribute('data-theme', theme);

    var a = 'class="al-switch__input" type="checkbox" role="switch"'
      + (ligado ? ' checked' : '') + (off ? ' disabled' : '');
    stage.innerHTML = '<label class="al-switch"><span class="al-switch__control">'
      + '<input id="pg-sw" ' + a + '>'
      + '<span class="al-switch__thumb" aria-hidden="true"></span></span>'
      + '<span class="al-switch__label">' + esc(rotulo) + '</span></label>';
    code.innerHTML = [
      '&lt;label class="al-switch"&gt;',
      '  &lt;span class="al-switch__control"&gt;',
      '    &lt;input ' + a + '&gt;',
      '    &lt;span class="al-switch__thumb" aria-hidden="true"&gt;&lt;/span&gt;',
      '  &lt;/span&gt;',
      '  &lt;span class="al-switch__label"&gt;' + esc(esc(rotulo)) + '&lt;/span&gt;',
      '&lt;/label&gt;'
    ].join('\n');
  }

  document.querySelectorAll('#sw-controls input').forEach(function (i) {
    i.addEventListener('input', render);
  });
  document.getElementById('sw-copy').addEventListener('click', function () {
    var btn = this;
    navigator.clipboard.writeText(code.textContent).then(function () {
      btn.textContent = 'Copiado';
      setTimeout(function () { btn.textContent = 'Copiar'; }, 1400);
    }).catch(function () {});
  });
  render();
})();
"""


HTML = (
    '<meta charset="utf-8">\n'
    '<title>AL Design System</title>\n'
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
    'family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap">\n\n'
    '<style>\n/* ═══ Foundation + tokens do Button + o componente, inline e reais ═══ */\n'
    + CSS_REAL +
    '\n/* ═══ Chrome do site ═══ */\n' + CHROME + CHROME_ICON + CHROME_AVATAR + CHROME_SELECT
    + CHROME_CHECKBOX + CHROME_RADIO + CHROME_SWITCH
    + '</style>\n\n'
    '<div class="shell">\n' + RAIL + '\n<main class="main"><div class="inner">\n'
    + '\n'.join(html for _, _, html in PAGES) + '\n' + FOOTER +
    '\n</div></main>\n</div>\n\n<script>'
    + JS + JS_ICON + JS_IB_DATA + JS_ICONBUTTON + JS_TAG_DATA + JS_TAG
    + JS_AVATAR_DATA + JS_AVATAR + JS_SELECT_DATA + JS_SELECT
    + JS_CHECKBOX_DATA + JS_CHECKBOX + JS_RADIO + JS_SWITCH + '</script>\n'
)

open(os.path.join(HERE, 'index.html'), 'w', encoding='utf-8').write(HTML)

print(f'site/index.html escrito ({len(HTML):,} bytes)')
print(f'  páginas no trilho : {len(PAGES)} — ' + ', '.join(p[0] for p in PAGES))
print(f'  primitivas        : {N_PRIM}')
print(f'  semânticos        : {N_SEM} × 2 temas')
print(f'  pares de contraste: {N_PAIRS} — {N_AA} em AA pleno, {N_EXC} exceções, {N_FAIL} reprovas')
print(f'  tokens do Button  : {N_BTN_TOKENS}')
print(f'  tokens do IconBtn : {N_IB_TOKENS}')
print(f'  tokens do Tag     : {N_TAG_TOKENS}  '
      f'({N_TAG_MEDIDAS} combinacoes medidas, {TAG_A11Y["fails"]} reprovas, 0 excecoes)')
print(f'  tokens do Avatar  : {N_AVATAR_TOKENS}  '
      f'({N_AV_MEDIDAS} combinacoes medidas, {AVATAR_A11Y["fails"]} reprovas, 0 excecoes)')
print(f'  tokens do Select  : {N_SELECT_TOKENS}  '
      f'({len(SELECT_A11Y["rows"])} combinacoes medidas, {SELECT_A11Y["fails"]} reprovas, '
      f'{sum(SELECT_A11Y["exceptions"].values())} medicoes em excecao declarada)')
print(f'  tokens do Checkbox: {N_CHECKBOX_TOKENS}  '
      f'({len(CHECKBOX_A11Y["rows"])} combinacoes medidas, {CHECKBOX_A11Y["fails"]} reprovas, '
      f'{sum(CHECKBOX_A11Y["exceptions"].values())} medicoes em excecao declarada)')
print(f'  tokens do Radio   : {N_RADIO_TOKENS}  '
      f'({len(RADIO_A11Y["rows"])} combinacoes medidas, {RADIO_A11Y["fails"]} reprovas, '
      f'{sum(RADIO_A11Y["exceptions"].values())} medicoes em excecao declarada)')
print(f'  tokens do Switch  : {N_SWITCH_TOKENS}  '
      f'({len(SWITCH_A11Y["rows"])} combinacoes medidas, {SWITCH_A11Y["fails"]} reprovas, '
      f'{sum(SWITCH_A11Y["exceptions"].values())} medicoes em excecao declarada)')
print(f'  ícones            : {N_ICONS} (Lucide · ISC · lidos de components/icon/icons/)')
print(f'  CSS inline        : foundation + Button + Icon (tokens e componentes, os reais)')
