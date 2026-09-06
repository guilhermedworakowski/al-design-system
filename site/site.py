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

Os icones do trilho e o switch de tema sao casca do site. NAO sao componentes
do AL - o Icon e o Switch ainda nao existem, e so nascem depois do Figma.

Rodar: python3 site/site.py     (escreve site/index.html)
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.join(ROOT, 'site')
sys.path.insert(0, os.path.join(ROOT, 'foundation'))

from color import cr  # noqa: E402  - contraste medido, nunca escrito a mao

T = json.load(open(os.path.join(ROOT, 'tokens.json')))
BTN = json.load(open(os.path.join(ROOT, 'components', 'button', 'tokens.json')))

FOUND_CSS = open(os.path.join(ROOT, 'foundation', 'al-foundation.css')).read()
BTN_TOKENS = open(os.path.join(ROOT, 'components', 'button', 'al-button-tokens.css')).read()
BTN_CSS = open(os.path.join(ROOT, 'components', 'button', 'button.css')).read()

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

assert N_FAIL == 0, f'{N_FAIL} pares reprovados - o portao de contraste deveria ter barrado antes'


# ════════════════════════════════════════════════════════════ tema no palco
def scope_themes(found_css, btn_tokens):
    """
    Producao troca o tema no :root, e ai a cadeia de alias resolve sozinha.
    Aqui nao: o playground troca o tema so no palco, e substituicao de custom
    property acontece no elemento onde ela e DECLARADA, nao no ponto de uso.
    Uma alias declarada no :root ja desce resolvida com o valor claro.

    Entao, para o container tematizado funcionar, tudo que aponta para um
    semantico precisa ser re-declarado dentro do bloco de tema: os aneis de
    foco compostos e a camada inteira do Button.
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
    mb = re.search(r':root\s*\{(.*?)\n\}', btn_tokens, re.S)
    btn = mb.group(1) if mb else ''

    css += '\n[data-theme="light"] {\n' + semantic_light + '\n}\n'
    css += ('\n/* Re-declaracao para container tematizado - so o playground precisa. */\n'
            '[data-theme="light"], [data-theme="dark"] {\n' + rings + '\n' + btn + '\n}\n')
    return css


CSS_REAL = scope_themes(FOUND_CSS, BTN_TOKENS) + '\n' + BTN_TOKENS + '\n' + BTN_CSS


def ink(bg):
    """Texto legivel sobre um swatch, escolhido por contraste real."""
    return N['950'] if cr(bg, N['950']) >= cr(bg, '#FFFFFF') else '#FFFFFF'


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

ICON_SVG = ('<svg viewBox="0 0 16 16" fill="none" aria-hidden="true">'
            '<path d="M8 2v9m0 0 3.5-3.5M8 11 4.5 7.5M2.5 13.5h11" stroke="currentColor" '
            'stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>')
ARROW_SVG = ('<svg viewBox="0 0 16 16" fill="none" aria-hidden="true">'
             '<path d="M6 3.5 10.5 8 6 12.5" stroke="currentColor" stroke-width="1.5" '
             'stroke-linecap="round" stroke-linejoin="round"/></svg>')


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
   Casca do site, não o componente. O AL ainda não tem um Switch, e inventar um
   aqui criaria um componente por acidente — sem Figma, sem tokens, sem portão.
   Quando o Switch existir de verdade, este vira consumo dele. */
/* O padding de 6px aqui existe só para o alvo de toque: ele leva a área
   clicável de 42×24 para 54×36 sem mudar o desenho, e o 18px do rodapé
   compensa para o track continuar alinhado com os ícones do menu, em 24px. */
.rail-foot{margin-top:auto; border-top:1px solid var(--al-border-subtle); padding:14px 18px}
.theme-switch{
  appearance:none; border:0; background:none; cursor:pointer;
  display:block; padding:6px; border-radius:9999px; color:var(--al-text-secondary);
}
.theme-switch:focus-visible{outline:2px solid var(--al-border-focus); outline-offset:2px}
.theme-switch:not([aria-checked="true"]):hover .ts-track{border-color:var(--al-border-strong)}
.theme-switch[aria-checked="true"]:hover .ts-track{
  background:var(--al-bg-brand-hover); border-color:var(--al-bg-brand-hover);
}
.ts-track{
  flex:none; width:42px; height:24px; border-radius:9999px; padding:2px; display:flex;
  background:var(--al-bg-subtle); border:1px solid var(--al-border-default);
  transition:background-color 160ms ease, border-color 160ms ease;
}
.theme-switch[aria-checked="true"] .ts-track{
  background:var(--al-bg-brand); border-color:var(--al-bg-brand);
}
.ts-thumb{
  width:18px; height:18px; border-radius:9999px; display:grid; place-items:center;
  background:var(--al-bg-canvas); box-shadow:var(--al-elevation-1);
  color:var(--al-text-secondary); transition:transform 160ms ease;
}
.theme-switch[aria-checked="true"] .ts-thumb{transform:translateX(18px)}
.ts-thumb svg{display:block; width:12px; height:12px}
.theme-switch[aria-checked="true"] .ts-sun{display:none}
.theme-switch:not([aria-checked="true"]) .ts-moon{display:none}
@media (prefers-reduced-motion: reduce){
  .ts-track, .ts-thumb, .nav-chev svg{transition:none}
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
SUN = ('<svg class="ts-sun" viewBox="0 0 16 16" fill="none" aria-hidden="true">'
       '<circle cx="8" cy="8" r="3.1" stroke="currentColor" stroke-width="1.5"/>'
       '<path d="M8 1v1.6M8 13.4V15M15 8h-1.6M2.6 8H1M12.9 3.1l-1.1 1.1M4.2 11.8l-1.1 1.1'
       'M12.9 12.9l-1.1-1.1M4.2 4.2 3.1 3.1" stroke="currentColor" stroke-width="1.5" '
       'stroke-linecap="round"/></svg>')
MOON = ('<svg class="ts-moon" viewBox="0 0 16 16" fill="none" aria-hidden="true">'
        '<path d="M13.5 9.6A5.9 5.9 0 0 1 6.4 2.5a5.9 5.9 0 1 0 7.1 7.1Z" '
        'stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/></svg>')

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
    <div><b>06 · Playground</b><span>A página instancia o CSS real, não uma cópia.</span></div>
    <div><b>07 · QA</b><span>Combinação renderizada — variante × estado × tema — contra o fundo efetivo.</span></div>
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
        <span class="al-btn__icon al-btn__icon--leading" aria-hidden="true" hidden>{ICON_SVG}</span>
        <span class="al-btn__label">Publicar</span>
        <span class="al-btn__icon al-btn__icon--trailing" aria-hidden="true" hidden>{ARROW_SVG}</span>
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


# ═══════════════════════════════════════════════════════════════════ páginas
LANDING_FUNDACAO = f'''
<section>
  <h2>Os cinco assuntos da Fundação</h2>
  <div class="cards">
    {card('principios', 'Princípios', 'As cinco decisões que travam o resto, o pipeline de oito etapas e os quatro portões de build.', TH_PRINCIPIOS)}
    {card('prova', 'A prova', 'Os mesmos tokens montados nos dois temas, lado a lado: botões, campos, foco e avisos.', TH_PROVA)}
    {card('cor', 'Cor', f'{N_PRIM} primitivas em OKLCH, {N_SEM} semânticos com dois temas e os {N_PAIRS} pares medidos do portão de contraste.', TH_COR)}
    {card('tipografia', 'Tipografia', f'Inter e JetBrains Mono em {len(T["type"]["styles"])} estilos fechados de tamanho, entrelinha, peso e tracking.', TH_TIPO)}
    {card('espacamento', 'Espaçamento e medidas', f'Base 4 com ritmo de 8, {len(T["radius"])} raios, 6 elevações e o anel de foco de duas camadas.', TH_ESPACO)}
  </div>
</section>'''

LANDING_COMPONENTES = f'''
<section>
  <h2>Publicados</h2>
  <div class="cards">
    {card('button', 'Button', 'Quatro variantes, dois tamanhos, cinco estados — com playground que instancia o CSS real.', TH_BUTTON)}
  </div>
</section>

<section>
  <h2>Tier 1, ainda não abertos</h2>
  <p>A ordem não é negociável enquanto o pipeline for de um componente por vez. Cada um destes
  começa pela etapa 1 — definir e auditar — e só entra na lista de cima depois das oito.</p>
  <div class="cards" style="margin-top:18px">
    {card('icon-button', 'Icon Button', 'O botão sem rótulo visível. Mesma pílula e mesmos estados do Button, com nome acessível obrigatório.', TH_SOON, soon=True)}
    {card('icon', 'Icon', 'Traz junto a escala de ícone, que o Button hoje resolve com um valor provisório de 16px.', TH_SOON, soon=True)}
    {card('badge', 'Badge / Tag', 'Rótulo curto de status ou contagem, sem ação associada.', TH_SOON, soon=True)}
    {card('avatar', 'Avatar', 'Identidade visual de uma pessoa ou entidade, com recurso a iniciais.', TH_SOON, soon=True)}
  </div>
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

    ('componentes', 'Componentes', simple_page(
        'componentes', 'Componentes', 'Componentes',
        'Peça pronta para usar, com desenho, tokens, código e QA já fechados. Um componente só '
        'aparece aqui depois de atravessar as oito etapas do pipeline — por isso a lista é curta e '
        'cresce devagar, um de cada vez.',
        [('1 publicado', True), ('5 no Tier 1', False), ('8 etapas por componente', False)],
        LANDING_COMPONENTES)),

    ('button', 'Componentes', page(
        'button', 'Componentes', 'Button',
        'Dispara a ação de uma tela. Quatro variantes que carregam pesos diferentes na hierarquia, '
        'dois tamanhos, cinco estados.',
        [('Estável', True), ('40 variantes no Figma', False), (f'{N_BTN_TOKENS} tokens', False),
         ('0 valores soltos', False)],
        [('overview', 'Visão geral', BTN_OVERVIEW), ('specs', 'Especificações', BTN_SPECS),
         ('guide', 'Diretrizes', BTN_GUIDE), ('a11y', 'Acessibilidade', BTN_A11Y)])),
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
      </div>
    </div>
    <div class="nav-group" id="g-componentes">
      <a class="nav-primary" href="#/componentes" data-page="componentes"
         aria-expanded="false" aria-controls="sub-componentes">
        <span class="nav-ico">{ICO_COMPONENTES}</span><span class="nav-label">Componentes</span>
        <span class="nav-chev" aria-hidden="true">{CARET}</span></a>
      <div class="nav-sub" id="sub-componentes" hidden>
        <a href="#/button" data-page="button">Button</a>
        <a class="soon" aria-disabled="true">Icon Button</a>
        <a class="soon" aria-disabled="true">Icon</a>
        <a class="soon" aria-disabled="true">Badge / Tag</a>
        <a class="soon" aria-disabled="true">Avatar</a>
      </div>
    </div>
  </div>

  <div class="rail-foot">
    <button type="button" class="theme-switch" id="themeswitch" role="switch" aria-checked="false"
            aria-label="Tema escuro">
      <span class="ts-track" aria-hidden="true"><span class="ts-thumb">{SUN}{MOON}</span></span>
    </button>
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
    sw.setAttribute('aria-checked', dark ? 'true' : 'false');
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
    sw.setAttribute('aria-checked', stamped === 'dark' ? 'true' : 'false');
  } else {
    sw.setAttribute('aria-checked', mq && mq.matches ? 'true' : 'false');
    if (mq && mq.addEventListener) {
      mq.addEventListener('change', function (e) {
        if (!root.getAttribute('data-theme')) {
          sw.setAttribute('aria-checked', e.matches ? 'true' : 'false');
        }
      });
    }
  }

  sw.addEventListener('click', function () {
    applyTheme(sw.getAttribute('aria-checked') !== 'true', true);
  });

  // Se o ambiente reescrever data-theme por fora (o visualizador tem o próprio
  // controle de tema), o switch acompanha em vez de ficar mentindo.
  if (window.MutationObserver) {
    new MutationObserver(function () {
      var dark = root.getAttribute('data-theme') === 'dark';
      if ((sw.getAttribute('aria-checked') === 'true') !== dark) {
        sw.setAttribute('aria-checked', dark ? 'true' : 'false');
      }
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
      lines.push('  &lt;span class="al-btn__icon al-btn__icon--leading" aria-hidden="true"&gt;&lt;svg …&gt;&lt;/svg&gt;&lt;/span&gt;');
    lines.push('  &lt;span class="al-btn__label"&gt;' +
      (input.value || 'Button').replace(/&/g, '&amp;').replace(/</g, '&lt;') + '&lt;/span&gt;');
    if (icon === 'trailing')
      lines.push('  &lt;span class="al-btn__icon al-btn__icon--trailing" aria-hidden="true"&gt;&lt;svg …&gt;&lt;/svg&gt;&lt;/span&gt;');
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

HTML = (
    '<title>AL Design System</title>\n'
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
    'family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap">\n\n'
    '<style>\n/* ═══ Foundation + tokens do Button + o componente, inline e reais ═══ */\n'
    + CSS_REAL +
    '\n/* ═══ Chrome do site ═══ */\n' + CHROME + '</style>\n\n'
    '<div class="shell">\n' + RAIL + '\n<main class="main"><div class="inner">\n'
    + '\n'.join(html for _, _, html in PAGES) + '\n' + FOOTER +
    '\n</div></main>\n</div>\n\n<script>' + JS + '</script>\n'
)

open(os.path.join(HERE, 'index.html'), 'w').write(HTML)

print(f'site/index.html escrito ({len(HTML):,} bytes)')
print(f'  páginas no trilho : {len(PAGES)} — ' + ', '.join(p[0] for p in PAGES))
print(f'  primitivas        : {N_PRIM}')
print(f'  semânticos        : {N_SEM} × 2 temas')
print(f'  pares de contraste: {N_PAIRS} — {N_AA} em AA pleno, {N_EXC} exceções, {N_FAIL} reprovas')
print(f'  tokens do Button  : {N_BTN_TOKENS}')
print(f'  CSS inline        : foundation + tokens do Button + button.css (os reais)')
