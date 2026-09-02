# -*- coding: utf-8 -*-
import json
from color import cr, hex_to_oklch, lum

T = json.load(open('tokens.json'))
P, SEM = T['color']['primitive'], T['color']['semantic']
N, O = P['neutral'], P['orange']
STEPS = ['50','100','200','300','400','500','600','700','800','900','950']
LAD = T['meta']['lLadder']
FAM_LABEL = {'neutral':'neutral','orange':'orange','red':'red','amber':'amber','green':'green','blue':'blue'}
FAM_ROLE = {'neutral':'superfície, texto, borda','orange':'marca · ação','red':'danger','amber':'warning','green':'success','blue':'info'}

def ink(bg):
    """texto legível sobre um swatch, escolhido por contraste real"""
    return N['950'] if cr(bg, N['950']) >= cr(bg, '#FFFFFF') else '#FFFFFF'

def esc(s): return s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

# ---------- grade de primitivas ----------
def swatch_grid():
    out = ['<div class="scroll-x"><table class="ramp">']
    out.append('<thead><tr><th class="ramp-fam"></th>')
    for s in STEPS:
        out.append(f'<th><span class="step">{s}</span><span class="lval">L {LAD[s]:.3f}</span></th>')
    out.append('</tr></thead><tbody>')
    for fam in ['neutral','orange','red','amber','green','blue']:
        out.append(f'<tr><th class="ramp-fam"><span class="fam-name">{FAM_LABEL[fam]}</span>'
                   f'<span class="fam-role">{FAM_ROLE[fam]}</span></th>')
        for s in STEPS:
            h = P[fam][s]
            ratio = cr(h, '#FFFFFF')
            out.append(f'<td><div class="sw" style="background:{h};color:{ink(h)}">'
                       f'<span class="sw-hex">{h[1:]}</span>'
                       f'<span class="sw-cr">{ratio:.2f}</span></div></td>')
        out.append('</tr>')
    out.append('</tbody></table></div>')
    return ''.join(out)

# ---------- diagrama: contraste do label por estado, nos dois temas ----------
def brand_window():
    BH = T['color']['brandHover']
    TRACKS = [
        ("tema claro", "tela branca", [(O['500'], "rest", "orange-500"), (O['600'], "hover", "orange-600"), (O['700'], "pressed", "orange-700")]),
        ("tema escuro", "tela #15181E", [(O['500'], "rest", "orange-500"), (BH, "hover", "orange-550"), (O['600'], "pressed", "orange-600")]),
    ]
    x0, x1, W = 3.0, 8.5, 880.0
    def X(v): return 132 + (v - x0) / (x1 - x0) * (W - 172)
    s = [f'<svg viewBox="0 0 {int(W)} 210" class="winsvg" role="img" '
         f'aria-label="Contraste do label branco em cada estado do botão primário, nos dois temas, contra a linha de 4.5 para 1 do AA">']
    # faixa de excecao
    s.append(f'<rect x="{X(3.0):.1f}" y="30" width="{X(4.5)-X(3.0):.1f}" height="128" class="win-exc"/>')
    s.append(f'<line x1="{X(4.5):.1f}" y1="30" x2="{X(4.5):.1f}" y2="158" class="win-bound"/>')
    s.append(f'<text x="{X(4.5)+8:.1f}" y="24" class="win-rule">4.5:1 — AA para texto normal</text>')
    s.append(f'<text x="{X(3.0):.1f}" y="24" class="win-rule">3:1 — piso: AA para texto grande</text>')
    for i, (theme, canvas, marks) in enumerate(TRACKS):
        y = 62 + i * 62
        s.append(f'<text x="12" y="{y+4:.0f}" class="win-track-name">{theme}</text>')
        s.append(f'<text x="12" y="{y+19:.0f}" class="win-track-sub">{canvas}</text>')
        s.append(f'<line x1="{X(x0):.1f}" y1="{y:.0f}" x2="{X(x1):.1f}" y2="{y:.0f}" class="win-rail"/>')
        for hexv, state, name in marks:
            v = cr(hexv, "#FFFFFF")
            ok = v >= 4.5
            s.append(f'<circle cx="{X(v):.1f}" cy="{y:.0f}" r="10" fill="{hexv}" class="win-dot"/>')
            s.append(f'<text x="{X(v):.1f}" y="{y-17:.0f}" class="win-name" text-anchor="middle">{state}</text>')
            s.append(f'<text x="{X(v):.1f}" y="{y+26:.0f}" class="win-role{"" if ok else " bad"}" text-anchor="middle">{v:.2f}:1</text>')
    s.append(f'<text x="{X(x0):.1f}" y="196" class="win-axis">contraste do label branco sobre o preenchimento →</text>')
    s.append('</svg>')
    return ''.join(s)

# ---------- semanticos ----------
GROUPS = [('bg/', 'Superfície e preenchimento'), ('text/', 'Texto'), ('border/', 'Borda')]
def semantic_tables():
    out = []
    for prefix, title in GROUPS:
        keys = [k for k in SEM if k.startswith(prefix)]
        out.append(f'<h3 class="sub">{title}</h3><div class="scroll-x"><table class="tok">')
        out.append('<thead><tr><th>token</th><th colspan="2">tema claro</th><th colspan="2">tema escuro</th></tr></thead><tbody>')
        for k in keys:
            l, d = SEM[k]
            out.append(f'<tr><td class="tok-name">{k}</td>'
                       f'<td class="chip-cell"><span class="chip" style="background:{l}"></span></td>'
                       f'<td class="tok-val">{l}</td>'
                       f'<td class="chip-cell"><span class="chip" style="background:{d}"></span></td>'
                       f'<td class="tok-val">{d}</td></tr>')
        out.append('</tbody></table></div>')
    return ''.join(out)

# ---------- contraste ----------
def contrast_tables():
    out = []
    for theme, label in [('light', 'Tema claro'), ('dark', 'Tema escuro')]:
        rows = [r for r in T['contrastReport'] if r['theme'] == theme]
        out.append(f'<h3 class="sub">{label} <span class="count">{len(rows)} pares</span></h3>')
        out.append('<div class="scroll-x"><table class="tok cr"><thead><tr>'
                   '<th>par</th><th>frente</th><th>fundo</th><th class="num">medido</th><th class="num">mín.</th><th></th>'
                   '</tr></thead><tbody>')
        for r in rows:
            out.append(f'<tr><td>{r["label"]}</td>'
                       f'<td class="tok-name"><span class="chip sm" style="background:{r["fgHex"]}"></span>{r["fg"]}</td>'
                       f'<td class="tok-name"><span class="chip sm" style="background:{r["bgHex"]}"></span>{r["bg"]}</td>'
                       f'<td class="num strong">{r["ratio"]:.2f}:1</td>'
                       f'<td class="num muted">{r["min"]}</td>'
                       f'<td><span class="{"exc" if r.get("exception") else "pass"}">{"MARCA" if r.get("exception") else "AA"}</span></td></tr>')
        out.append('</tbody></table></div>')
    return ''.join(out)

# ---------- tipografia ----------
def type_specimens():
    out = ['<div class="specimens">']
    for name, size, lead, wt, track, use in T['type']['styles']:
        mono = 'code' in name
        fam = "var(--mono)" if mono else "var(--sans)"
        out.append(
            f'<div class="spec"><div class="spec-meta">'
            f'<span class="spec-name">{name}</span>'
            f'<span class="spec-num">{size}/{lead}</span>'
            f'<span class="spec-num">w{wt}</span>'
            f'<span class="spec-num">{track}</span>'
            f'<span class="spec-use">{use}</span></div>'
            f'<div class="spec-sample" style="font-family:{fam};font-size:{size}px;line-height:{lead}px;'
            f'font-weight:{wt};letter-spacing:{track}">Foundation aberta do AL</div></div>')
    out.append('</div>')
    return ''.join(out)

def space_scale():
    out = ['<div class="bars">']
    for v in T['space']:
        out.append(f'<div class="bar-row"><span class="bar-name">space-{v}</span>'
                   f'<span class="bar" style="width:{max(int(v),1)}px"></span>'
                   f'<span class="bar-val">{v}px</span></div>')
    out.append('</div>')
    return ''.join(out)

def radius_scale():
    out = ['<div class="radii">']
    for k, v in T['radius'].items():
        shown = '999' if v == 9999 else str(v)
        out.append(f'<div class="rad"><div class="rad-box" style="border-radius:{min(v,48)}px"></div>'
                   f'<span class="rad-name">{k}</span><span class="rad-val">{shown}px</span></div>')
    out.append('</div>')
    return ''.join(out)

def elevation_scale():
    out = ['<div class="elevs">']
    for k in ['0','1','2','3','4','5']:
        e = T['elevation'][k]
        out.append(f'<div class="elev"><div class="elev-box" style="--sl:{e["light"]};--sd:{e["dark"]}">{k}</div>'
                   f'<span class="elev-name">elevation-{k}</span></div>')
    out.append('</div>')
    return ''.join(out)


# ---------- matriz do botao nos dois temas ----------
ICON = {
 "plus": "M12 5v14M5 12h14",
 "arrow-right": "M5 12h14M12 5l7 7-7 7",
}
def glyph(d, px=16):
    return (f'<svg class="ico" style="width:{px}px;height:{px}px" viewBox="0 0 24 24" fill="none" '
            f'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
            f'aria-hidden="true"><path d="{d}"/></svg>')
def spinner(px=16):
    return (f'<svg class="ico spin" style="width:{px}px;height:{px}px" viewBox="0 0 24 24" fill="none" '
            f'stroke="currentColor" stroke-width="2.4" stroke-linecap="round" aria-hidden="true">'
            f'<path d="M12 3a9 9 0 1 0 9 9"/></svg>')
SPIN = spinner(16)
SPIN20 = spinner(20)

def button_matrix():
    STATES = ["rest", "hover", "pressed"]
    def panel(i, label):
        g = lambda k: SEM[k][i]
        GROUPS = [
            ("Primary",   "ação principal da tela",  [g('bg/brand'), g('bg/brand-hover'), g('bg/brand-active')], g('text/on-brand'), None, "shadow"),
            ("Secondary", "ações menos relevantes",  [None, g('bg/hover'), g('bg/active')], g('text/primary'), g('border/strong'), "inset"),
            ("Ghost",     "ação terciária",          [None, g('bg/hover'), g('bg/active')], g('text/primary'), None, "outset"),
            ("Danger",    "ação destrutiva",         [g('bg/danger'), g('bg/danger-hover'), g('bg/danger-active')], g('text/on-solid'), None, "shadow"),
        ]
        out = [f'<div class="bm" style="background:{g("bg/canvas")};border-color:{g("border/subtle")}">'
               f'<div class="bm-tag" style="color:{g("text/secondary")};border-color:{g("border/subtle")}">{label}</div>'
               f'<div class="bm-body">']
        for name, use, fills, inkc, brd, focus in GROUPS:
            out.append(f'<div class="bm-grp"><span class="bm-name" style="color:{g("text/primary")}">{name}'
                       f'<span class="bm-use" style="color:{g("text/secondary")}">{use}</span></span><div class="bm-row">')
            ratios = []
            for st, bgc in zip(STATES, fills):
                base = bgc or g('bg/canvas')
                ratios.append(f'{st} {cr(inkc, base):.2f}:1')
                style = f'background:{bgc or "transparent"};color:{inkc}'
                if brd: style += f';box-shadow:inset 0 0 0 1px {brd}'
                out.append(f'<div class="bm-cell"><button class="bm-btn" style="{style}">Button</button>'
                           f'<span class="bm-lab" style="color:{g("text/secondary")}">{st}</span></div>')
            # o foco muda de mecanismo conforme haja ou nao preenchimento
            if focus == "shadow":
                fs = f'0 0 0 2px {g("bg/canvas")}, 0 0 0 4px {g("border/focus")}'
            elif focus == "inset":
                fs = f'inset 0 0 0 2px {g("border/focus")}'
            else:
                fs = f'0 0 0 2px {g("border/focus")}'
            out.append(f'<div class="bm-cell"><button class="bm-btn" style="background:{fills[0] or "transparent"};'
                       f'color:{inkc};box-shadow:{fs}">Button</button>'
                       f'<span class="bm-lab" style="color:{g("text/secondary")}">focus</span></div>')
            below = [1 for _, bgc in zip(STATES, fills) if cr(inkc, bgc or g('bg/canvas')) < 4.5]
            tone = g('text/warning') if below else g('text/secondary')
            note = ' · '.join(ratios) + ('   ← abaixo de 4.5:1' if below else '')
            out.append(f'</div><span class="bm-note" style="color:{tone}">{note}</span></div>')

        # slots de icone e loading
        out.append(f'<div class="bm-grp"><span class="bm-name" style="color:{g("text/primary")}">Ícone e loading</span><div class="bm-row">')
        for content, lab in [
            (glyph(ICON["plus"]) + "<span>Button</span>", "icon left"),
            ("<span>Button</span>" + glyph(ICON["arrow-right"]), "icon right"),
            (glyph(ICON["plus"]) + "<span>Button</span>" + glyph(ICON["arrow-right"]), "ambos"),
            (SPIN + "<span>Button</span>", "loading"),
        ]:
            out.append(f'<div class="bm-cell"><button class="bm-btn ico-btn" '
                       f'style="background:{g("bg/brand")};color:{g("text/on-brand")}">{content}</button>'
                       f'<span class="bm-lab" style="color:{g("text/secondary")}">{lab}</span></div>')
        out.append(f'</div><span class="bm-note" style="color:{g("text/secondary")}">'
                   f'o glifo herda a cor do label — currentColor no código, modo de variável no Figma</span></div>')

        # icon-only: quadrado, glifo de 20px, nome acessivel obrigatorio
        SQ = [("Primary", g('bg/brand'), g('text/on-brand'), None),
              ("Secondary", None, g('text/primary'), g('border/strong')),
              ("Ghost", None, g('text/primary'), None),
              ("Danger", g('bg/danger'), g('text/on-solid'), None)]
        out.append(f'<div class="bm-grp"><span class="bm-name" style="color:{g("text/primary")}">Icon only'
                   f'<span class="bm-use" style="color:{g("text/secondary")}">ícone inequívoco sozinho</span></span><div class="bm-row">')
        for nm, bgc, inkc, brd in SQ:
            style = f'background:{bgc or "transparent"};color:{inkc}'
            if brd: style += f';box-shadow:inset 0 0 0 1px {brd}'
            out.append(f'<div class="bm-cell"><button class="bm-btn sq" style="{style}" aria-label="Adicionar">'
                       f'{glyph(ICON["plus"], 20)}</button>'
                       f'<span class="bm-lab" style="color:{g("text/secondary")}">{nm.lower()}</span></div>')
        out.append(f'<div class="bm-cell"><button class="bm-btn sq" aria-label="Adicionar" '
                   f'style="background:{g("bg/brand")};color:{g("text/on-brand")};'
                   f'box-shadow:0 0 0 2px {g("bg/canvas")}, 0 0 0 4px {g("border/focus")}">{glyph(ICON["plus"], 20)}</button>'
                   f'<span class="bm-lab" style="color:{g("text/secondary")}">focus</span></div>')
        out.append(f'<div class="bm-cell"><button class="bm-btn sq" aria-label="Carregando" '
                   f'style="background:{g("bg/brand")};color:{g("text/on-brand")}">{SPIN20}</button>'
                   f'<span class="bm-lab" style="color:{g("text/secondary")}">loading</span></div>')
        out.append(f'</div><span class="bm-note" style="color:{g("text/secondary")}">'
                   f'32 / 40 / 48 quadrados — todos acima do mínimo 24x24 da WCAG 2.2</span></div>')
        out.append('</div></div>')
        return ''.join(out)
    return f'<div class="btn-matrix">{panel(0, "tema claro")}{panel(1, "tema escuro")}</div>'

# ---------- componentes de prova, renderizados nos dois temas ----------
def proof():
    def panel(i, label):
        g = lambda k: SEM[k][i]
        bh = T['color']['brandHover'] if i == 0 else P['orange']['400']
        return f'''
<div class="panel" style="background:{g('bg/canvas')};border-color:{g('border/subtle')}">
  <div class="panel-tag" style="color:{g('text/secondary')};border-color:{g('border/subtle')}">{label}</div>
  <div class="panel-body">
    <div class="btn-row">
      <button class="pb" style="background:{g('bg/brand')};color:{g('text/on-brand')}">Publicar</button>
      <button class="pb" style="background:{bh};color:{g('text/on-brand')}">Publicar<span class="st">hover</span></button>
      <button class="pb" style="background:{g('bg/danger')};color:{g('text/on-solid')}">Excluir</button>
      <button class="pb ghost" style="color:{g('text/primary')};border-color:{g('border/strong')}">Cancelar</button>
    </div>
    <div class="fld">
      <label style="color:{g('text/primary')}">Nome do projeto</label>
      <div class="inp" style="border-color:{g('border/strong')};background:{g('bg/canvas')};color:{g('text/placeholder')}">design-system</div>
    </div>
    <div class="fld">
      <label style="color:{g('text/primary')}">Slug</label>
      <div class="inp focus" style="border-color:{g('border/focus')};background:{g('bg/canvas')};color:{g('text/primary')};box-shadow:0 0 0 2px {g('bg/canvas')}, 0 0 0 4px {g('border/focus')}">al-ds</div>
    </div>
    <div class="fld">
      <label style="color:{g('text/danger')}">E-mail</label>
      <div class="inp" style="border-color:{g('border/danger')};background:{g('bg/canvas')};color:{g('text/primary')}">guilherme@</div>
      <span class="help" style="color:{g('text/danger')}">Falta o domínio depois do @.</span>
    </div>
    <div class="banners">
      <div class="bn" style="background:{g('bg/success-subtle')};border-color:{g('border/success')};color:{g('text/success')}"><b>Publicado.</b> A versão 0.1.0 está disponível.</div>
      <div class="bn" style="background:{g('bg/warning-subtle')};border-color:{g('border/warning')};color:{g('text/warning')}"><b>Token sem uso.</b> 3 tokens não são referenciados.</div>
      <div class="bn" style="background:{g('bg/danger-subtle')};border-color:{g('border/danger')};color:{g('text/danger')}"><b>Contraste reprovado.</b> 1 par abaixo de 4.5:1.</div>
      <div class="bn" style="background:{g('bg/info-subtle')};border-color:{g('border/info')};color:{g('text/info')}"><b>Sincronizado.</b> Figma atualizado há 2 minutos.</div>
    </div>
  </div>
</div>'''
    return f'<div class="panels">{panel(0, "tema claro")}{panel(1, "tema escuro")}</div>'

# ---------- montagem ----------
g = lambda k, i: SEM[k][i]
CSS = f'''
:root {{
  --canvas:{g('bg/canvas',0)}; --surface:{g('bg/surface',0)}; --subtle:{g('bg/subtle',0)};
  --ink:{g('text/primary',0)}; --ink2:{g('text/secondary',0)}; --ink3:{N['500']};
  --line:{g('border/subtle',0)}; --line2:{g('border/default',0)};
  --brand:{P['orange']['500']}; --brand-ink:{g('text/brand',0)}; --on-brand:{g('text/on-brand',0)};
  --ok:{g('text/success',0)}; --ok-bg:{g('bg/success-subtle',0)};
  --warn:{g('text/warning',0)}; --warn-bg:{g('bg/warning-subtle',0)};
  --sans:'Inter','Inter var',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
  --mono:'JetBrains Mono',ui-monospace,SFMono-Regular,Menlo,monospace;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --canvas:{g('bg/canvas',1)}; --surface:{g('bg/surface',1)}; --subtle:{g('bg/subtle',1)};
    --ink:{g('text/primary',1)}; --ink2:{g('text/secondary',1)}; --ink3:{N['500']};
    --line:{g('border/subtle',1)}; --line2:{g('border/default',1)};
    --brand-ink:{g('text/brand',1)}; --ok:{g('text/success',1)}; --ok-bg:{g('bg/success-subtle',1)};
    --warn:{g('text/warning',1)}; --warn-bg:{g('bg/warning-subtle',1)};
    --warn:{g('text/warning',1)}; --warn-bg:{g('bg/warning-subtle',1)};
  }}
}}
:root[data-theme="dark"] {{
  --canvas:{g('bg/canvas',1)}; --surface:{g('bg/surface',1)}; --subtle:{g('bg/subtle',1)};
  --ink:{g('text/primary',1)}; --ink2:{g('text/secondary',1)}; --ink3:{N['500']};
  --line:{g('border/subtle',1)}; --line2:{g('border/default',1)};
  --brand-ink:{g('text/brand',1)}; --ok:{g('text/success',1)}; --ok-bg:{g('bg/success-subtle',1)};
    --warn:{g('text/warning',1)}; --warn-bg:{g('bg/warning-subtle',1)};
    --warn:{g('text/warning',1)}; --warn-bg:{g('bg/warning-subtle',1)};
}}

* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--canvas); color:var(--ink);
  font-family:var(--sans); font-size:16px; line-height:24px;
  -webkit-font-smoothing:antialiased; font-feature-settings:'cv05' 1; }}
.wrap {{ max-width:1120px; margin:0 auto; padding:0 24px 128px; }}

/* ---- nav ---- */
nav {{ position:sticky; top:0; z-index:20; background:color-mix(in srgb, var(--canvas) 88%, transparent);
  backdrop-filter:blur(12px); border-bottom:1px solid var(--line); }}
.nav-in {{ max-width:1120px; margin:0 auto; padding:0 24px; display:flex; align-items:center;
  gap:24px; height:56px; overflow-x:auto; scrollbar-width:none; }}
.nav-in::-webkit-scrollbar {{ display:none; }}
.nav-mark {{ display:flex; align-items:center; gap:8px; font-weight:700; letter-spacing:-0.01em; flex:none; }}
.nav-mark i {{ width:14px; height:14px; border-radius:4px; background:var(--brand); display:block; }}
.nav-in a {{ color:var(--ink2); text-decoration:none; font-size:13px; font-weight:500; white-space:nowrap; flex:none; }}
.nav-in a:hover, .nav-in a:focus-visible {{ color:var(--brand-ink); }}

/* ---- hero ---- */
header {{ padding:88px 0 64px; border-bottom:1px solid var(--line); }}
.eyebrow {{ font-family:var(--mono); font-size:12px; letter-spacing:0.08em; text-transform:uppercase;
  color:var(--ink2); margin:0 0 20px; }}
h1 {{ font-size:60px; line-height:64px; font-weight:700; letter-spacing:-0.03em; margin:0 0 20px;
  text-wrap:balance; max-width:16ch; }}
h1 em {{ font-style:normal; color:var(--brand); }}
.lede {{ font-size:18px; line-height:28px; color:var(--ink2); max-width:62ch; margin:0 0 40px; }}
.stats {{ display:flex; flex-wrap:wrap; gap:0; border:1px solid var(--line); border-radius:12px; overflow:hidden; }}
.stat {{ flex:1 1 150px; padding:18px 20px; border-right:1px solid var(--line); }}
.stat:last-child {{ border-right:0; }}
.stat b {{ display:block; font-size:28px; line-height:34px; font-weight:700; letter-spacing:-0.02em;
  font-variant-numeric:tabular-nums; }}
.stat span {{ display:block; font-size:12px; line-height:16px; color:var(--ink2); margin-top:4px; }}
.stat.hl b {{ color:var(--brand); }}

/* ---- secoes ---- */
section {{ padding:72px 0 0; }}
h2 {{ font-size:30px; line-height:36px; font-weight:600; letter-spacing:-0.02em; margin:0 0 8px; text-wrap:balance; }}
.sec-note {{ color:var(--ink2); max-width:68ch; margin:0 0 32px; }}
.sec-note code {{ font-family:var(--mono); font-size:0.88em; background:var(--subtle); padding:1px 5px; border-radius:4px; }}
h3.sub {{ font-size:13px; font-weight:600; letter-spacing:0.06em; text-transform:uppercase;
  color:var(--ink2); margin:40px 0 14px; display:flex; align-items:baseline; gap:10px; }}
.count {{ font-family:var(--mono); font-size:11px; letter-spacing:0; text-transform:none; color:var(--ink3); }}
.scroll-x {{ overflow-x:auto; }}

/* ---- rampa ---- */
table.ramp {{ border-collapse:separate; border-spacing:3px; width:100%; min-width:900px; }}
table.ramp th {{ font-weight:500; padding:0 0 8px; }}
table.ramp thead th {{ text-align:center; }}
.step {{ display:block; font-family:var(--mono); font-size:12px; font-weight:600; color:var(--ink); }}
.lval {{ display:block; font-family:var(--mono); font-size:10px; color:var(--ink3); margin-top:1px; }}
.ramp-fam {{ text-align:left; width:112px; padding-right:12px; vertical-align:middle; }}
.fam-name {{ display:block; font-family:var(--mono); font-size:13px; font-weight:600; }}
.fam-role {{ display:block; font-size:11px; line-height:14px; color:var(--ink2); margin-top:2px; }}
.sw {{ height:62px; border-radius:6px; display:flex; flex-direction:column; justify-content:flex-end;
  padding:6px 7px; gap:1px; }}
.sw-hex {{ font-family:var(--mono); font-size:10px; font-weight:600; opacity:.92; }}
.sw-cr {{ font-family:var(--mono); font-size:9px; opacity:.6; font-variant-numeric:tabular-nums; }}

/* ---- janela da marca ---- */
.winsvg {{ width:100%; height:auto; margin:8px 0 4px; }}
.win-exc {{ fill:var(--brand); opacity:.09; }}
.win-rail {{ stroke:var(--line2); stroke-width:1.5; }}
.win-track-name {{ fill:var(--ink); font-family:var(--sans); font-size:12px; font-weight:600; }}
.win-track-sub {{ fill:var(--ink3); font-family:var(--mono); font-size:10px; }}
.win-bound {{ stroke:var(--brand); stroke-width:1.5; stroke-dasharray:3 3; }}
.win-bnum {{ fill:var(--brand-ink); font-family:var(--mono); font-size:12px; font-weight:600; }}
.win-rule {{ fill:var(--ink2); font-family:var(--sans); font-size:11px; }}
.win-dot {{ stroke:var(--canvas); stroke-width:2.5; }}
.win-dot.bad {{ opacity:.34; }}
.win-name {{ fill:var(--ink); font-family:var(--mono); font-size:11px; font-weight:600; }}
.win-role {{ fill:var(--ink2); font-family:var(--sans); font-size:10.5px; }}
.win-role.bad {{ fill:var(--ink3); }}
.win-axis {{ fill:var(--ink3); font-family:var(--sans); font-size:10.5px; }}

/* ---- tabelas ---- */
table.tok {{ border-collapse:collapse; width:100%; min-width:620px; font-size:13px; }}
table.tok th {{ text-align:left; font-size:11px; font-weight:600; letter-spacing:0.05em; text-transform:uppercase;
  color:var(--ink2); padding:0 12px 8px 0; border-bottom:1px solid var(--line); }}
table.tok td {{ padding:7px 12px 7px 0; border-bottom:1px solid var(--line); vertical-align:middle; }}
table.tok tr:last-child td {{ border-bottom:0; }}
.tok-name {{ font-family:var(--mono); font-size:12px; white-space:nowrap; }}
.tok-val {{ font-family:var(--mono); font-size:12px; color:var(--ink2); }}
.chip-cell {{ width:28px; padding-right:6px !important; }}
.chip {{ display:inline-block; width:20px; height:20px; border-radius:5px; border:1px solid var(--line2);
  vertical-align:middle; }}
.chip.sm {{ width:12px; height:12px; border-radius:3px; margin-right:7px; }}
.num {{ text-align:right; font-family:var(--mono); font-variant-numeric:tabular-nums; white-space:nowrap; }}
.num.strong {{ font-weight:600; }}
.num.muted {{ color:var(--ink3); }}
.pass, .exc {{ display:inline-block; font-family:var(--mono); font-size:10px; font-weight:600; letter-spacing:0.04em;
  padding:2px 6px; border-radius:4px; background:var(--ok-bg); color:var(--ok); white-space:nowrap; }}
.exc {{ background:var(--warn-bg); color:var(--warn); }}
.btn-matrix {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(330px,1fr)); gap:20px; }}
.bm {{ border:1px solid; border-radius:14px; overflow:hidden; }}
.bm-tag {{ font-family:var(--mono); font-size:10.5px; letter-spacing:0.07em; text-transform:uppercase;
  padding:11px 20px; border-bottom:1px solid; }}
.bm-body {{ padding:22px 20px; display:flex; flex-direction:column; gap:20px; }}
.bm-grp {{ display:flex; flex-direction:column; gap:9px; }}
.bm-name {{ font-size:12px; font-weight:600; }}
.bm-row {{ display:flex; flex-wrap:wrap; gap:10px; align-items:center; }}
.bm-cell {{ display:flex; flex-direction:column; gap:5px; align-items:center; }}
.bm-btn {{ font-family:var(--sans); font-size:14px; font-weight:500; line-height:20px; height:40px;
  padding:0 16px; border-radius:8px; border:0; display:inline-flex; align-items:center; }}
.bm-lab {{ font-family:var(--mono); font-size:9.5px; }}
.bm-use {{ font-family:var(--mono); font-size:9.5px; font-weight:400; margin-left:8px; }}
.bm-btn.ico-btn {{ gap:8px; }}
.bm-btn.sq {{ width:40px; padding:0; justify-content:center; }}
.ico {{ width:16px; height:16px; flex:none; }}
.spin {{ animation:sp 0.8s linear infinite; }}
@keyframes sp {{ to {{ transform:rotate(360deg); }} }}
@media (prefers-reduced-motion: reduce) {{ .spin {{ animation:none; }} }}
.bm-note {{ font-family:var(--mono); font-size:10px; }}

/* ---- tipografia ---- */
.specimens {{ display:flex; flex-direction:column; }}
.spec {{ padding:20px 0; border-bottom:1px solid var(--line); }}
.spec:last-child {{ border-bottom:0; }}
.spec-meta {{ display:flex; flex-wrap:wrap; align-items:baseline; gap:14px; margin-bottom:10px; }}
.spec-name {{ font-family:var(--mono); font-size:12px; font-weight:600; min-width:96px; }}
.spec-num {{ font-family:var(--mono); font-size:11px; color:var(--ink2); font-variant-numeric:tabular-nums; }}
.spec-use {{ font-size:11px; color:var(--ink3); margin-left:auto; }}
.spec-sample {{ color:var(--ink); text-wrap:balance; }}

/* ---- espaco / radius / elevacao ---- */
.grid3 {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:48px; }}
.bars {{ display:flex; flex-direction:column; gap:7px; }}
.bar-row {{ display:flex; align-items:center; gap:12px; }}
.bar-name {{ font-family:var(--mono); font-size:11.5px; color:var(--ink2); width:78px; flex:none; }}
.bar {{ height:14px; background:var(--brand); border-radius:3px; flex:none; min-width:1px; }}
.bar-val {{ font-family:var(--mono); font-size:11px; color:var(--ink3); font-variant-numeric:tabular-nums; }}
.radii {{ display:flex; flex-wrap:wrap; gap:16px; }}
.rad {{ display:flex; flex-direction:column; gap:6px; align-items:center; }}
.rad-box {{ width:56px; height:56px; background:var(--subtle); border:1.5px solid var(--brand); }}
.rad-name {{ font-family:var(--mono); font-size:11px; font-weight:600; }}
.rad-val {{ font-family:var(--mono); font-size:10px; color:var(--ink3); }}
.elevs {{ display:flex; flex-wrap:wrap; gap:22px; }}
.elev {{ display:flex; flex-direction:column; gap:10px; align-items:center; }}
.elev-box {{ width:82px; height:64px; border-radius:10px; background:var(--canvas); border:1px solid var(--line);
  box-shadow:var(--sl); display:flex; align-items:center; justify-content:center;
  font-family:var(--mono); font-size:15px; font-weight:600; color:var(--ink3); }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) .elev-box {{ box-shadow:var(--sd); }} }}
:root[data-theme="dark"] .elev-box {{ box-shadow:var(--sd); }}
.elev-name {{ font-family:var(--mono); font-size:10.5px; color:var(--ink2); }}

/* ---- prova ---- */
.panels {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(340px,1fr)); gap:20px; }}
.panel {{ border:1px solid; border-radius:14px; overflow:hidden; }}
.panel-tag {{ font-family:var(--mono); font-size:10.5px; letter-spacing:0.07em; text-transform:uppercase;
  padding:11px 20px; border-bottom:1px solid; }}
.panel-body {{ padding:24px 20px; display:flex; flex-direction:column; gap:22px; }}
.btn-row {{ display:flex; flex-wrap:wrap; gap:10px; }}
.pb {{ font-family:var(--sans); font-size:14px; font-weight:500; line-height:20px; border:0; cursor:pointer;
  padding:10px 16px; border-radius:8px; display:inline-flex; align-items:center; gap:7px; }}
.pb .st {{ font-family:var(--mono); font-size:9px; opacity:.62; }}
.pb.ghost {{ background:transparent; border:1px solid; }}
.fld {{ display:flex; flex-direction:column; gap:6px; }}
.fld label {{ font-size:14px; font-weight:500; line-height:20px; }}
.inp {{ border:1px solid; border-radius:8px; padding:9px 12px; font-size:14px; line-height:20px; }}
.help {{ font-size:12px; line-height:16px; }}
.banners {{ display:flex; flex-direction:column; gap:9px; }}
.bn {{ border-left:3px solid; border-radius:0 8px 8px 0; padding:10px 14px; font-size:13px; line-height:19px; }}
.bn b {{ font-weight:600; }}

/* ---- notas ---- */
.callout {{ border:1px solid var(--line); border-left:3px solid var(--brand); border-radius:0 10px 10px 0;
  padding:18px 22px; margin:28px 0 0; background:var(--surface); }}
.callout p {{ margin:0; color:var(--ink2); font-size:14px; line-height:22px; max-width:74ch; }}
.callout p + p {{ margin-top:10px; }}
.callout b {{ color:var(--ink); font-weight:600; }}
.callout code {{ font-family:var(--mono); font-size:0.88em; }}
footer {{ margin-top:88px; padding-top:28px; border-top:1px solid var(--line); color:var(--ink3); font-size:12.5px;
  display:flex; flex-wrap:wrap; gap:8px 20px; }}
footer code {{ font-family:var(--mono); }}
a {{ color:var(--brand-ink); }}
:focus-visible {{ outline:2px solid var(--brand); outline-offset:2px; border-radius:3px; }}
@media (prefers-reduced-motion: reduce) {{ * {{ animation:none !important; transition:none !important; }} }}
@media (max-width:640px) {{
  h1 {{ font-size:40px; line-height:44px; }}
  header {{ padding:56px 0 44px; }}
  h2 {{ font-size:24px; line-height:32px; }}
}}
'''

NAV = [('decisoes','Decisões'),('escada','Escada'),('primitivas','Primitivas'),('janela','Custo do label'),('button','Button'),
       ('semanticos','Semânticos'),('contraste','Contraste'),('tipografia','Tipografia'),
       ('medidas','Medidas'),('elevacao','Elevação'),('prova','Prova')]

HTML = f'''<title>AL Design System Foundation</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap">
<style>{CSS}</style>

<nav><div class="nav-in">
  <span class="nav-mark"><i></i>AL</span>
  {''.join(f'<a href="#{a}">{b}</a>' for a,b in NAV)}
</div></nav>

<div class="wrap">
<header>
  <p class="eyebrow">Foundation · v0.1.0 · MIT</p>
  <h1>Uma escala, uma âncora, <em>uma</em> exceção assumida.</h1>
  <p class="lede">A base do AL Design System deriva inteiramente de <code>#FC5000</code>. A lightness dessa
  cor define o degrau 500 de todas as seis famílias, e cada par que o sistema permite foi medido contra
  WCAG 2.1 AA antes de existir como token. Sessenta e nove passam em AA pleno. Três não passam, por
  decisão de marca — e estão nomeados, medidos e documentados em vez de escondidos.</p>
  <div class="stats">
    <div class="stat hl"><b>#FC5000</b><span>âncora de marca, preservada exata</span></div>
    <div class="stat"><b>208</b><span>tokens na Foundation</span></div>
    <div class="stat"><b>69</b><span>pares em AA pleno</span></div>
    <div class="stat hl"><b>3</b><span>exceções de marca, nenhuma abaixo de 3:1</span></div>
  </div>
</header>

<section id="decisoes">
  <h2>As cinco decisões que travam o resto</h2>
  <p class="sec-note">Tudo o que vem depois é consequência destas. Elas são fáceis de desfazer por engano
  numa contribuição, então estão registradas antes dos valores.</p>
  <div class="scroll-x"><table class="tok"><tbody>
    <tr><td class="tok-name">âncora</td><td><b>#FC5000 é imutável.</b> Ela fixa L 0.666 na escada compartilhada. Mudar a âncora é mudar a marca inteira.</td></tr>
    <tr><td class="tok-name">label</td><td><b>O botão primário usa texto claro.</b> Branco sobre #FC5000 dá 3.34:1 — abaixo dos 4.5:1 de texto normal, acima dos 3:1 de texto grande e de elemento não-textual. É uma escolha de identidade, tomada com o número na mão.</td></tr>
    <tr><td class="tok-name">neutro</td><td><b>O cinza é frio e constante</b> — hue 264° em toda a rampa, chroma entre 0.004 e 0.014. Nunca cinza puro no meio e azulado nas pontas.</td></tr>
    <tr><td class="tok-name">escuro</td><td><b>O tema escuro não é inversão.</b> Sólidos vão para o degrau 500 com texto escuro, tonalizados de 100 para 950, e elevação troca sombra por superfície que clareia.</td></tr>
    <tr><td class="tok-name">portão</td><td><b>Contraste é build gate.</b> Os 70 pares rodam a cada alteração de cor. Um par abaixo do mínimo quebra o build — nunca se afrouxa o mínimo.</td></tr>
  </tbody></table></div>
</section>

<section id="escada">
  <h2>Uma escada de lightness para todas as famílias</h2>
  <p class="sec-note">Cada degrau tem a mesma lightness OKLab em todas as seis famílias. O degrau 500 é
  0.666 porque é a lightness de <code>#FC5000</code>. Isso significa que trocar <code>green-600</code> por
  <code>red-600</code> num componente não muda o contraste — a acessibilidade sobrevive à troca de cor.
  A escada é comprimida nas duas pontas: os degraus claros ficam próximos porque é onde vivem superfície
  e borda, e os escuros também, porque é onde vive a elevação do tema escuro.</p>
  <div class="callout"><p><b>Por que 0.666 importa mais do que parece.</b> Um cinza nessa lightness dá
  exatamente 3.04:1 contra o branco — o piso do WCAG para elemento não-textual. A âncora de marca caiu,
  por coincidência, na fronteira exata entre "serve como borda" e "não serve". Todo o resto do sistema
  se organiza em volta desse ponto.</p></div>
</section>

<section id="primitivas">
  <h2>Primitivas</h2>
  <p class="sec-note">66 cores em 6 famílias, mais um degrau extra na marca. O número pequeno em cada
  amostra é o contraste contra o branco. Os quatro laranjas originais do Figma sobreviveram à
  regularização: <code>#FFBDA0</code>, <code>#FC5000</code>, <code>#992700</code> e <code>#4A1700</code>
  caem dentro de 0.011 de lightness dos seus degraus.</p>
  {swatch_grid()}
  <div class="callout">
    <p><b>Como o vermelho e o amarelo fogem da marca.</b> O laranja está em hue 38°. O amarelo de warning
    foi empurrado para 85° — 47° de distância, sem ambiguidade. O vermelho de danger ficou em 20°, e nos
    degraus claros ele vira levemente rosado justamente para se afastar do pêssego da marca.</p>
    <p><b>O que a distância não resolve.</b> Em tonalizados muito claros, <code>orange-100</code> e
    <code>red-100</code> ficam a 0.017 de distância perceptual — praticamente idênticos. Isso é física,
    não erro de projeto: no degrau 100 nenhum par de cores quentes se distingue. Por isso banner nenhum
    se identifica só pelo fundo — todos carregam ícone, borda colorida no degrau 500+ e texto. É o que a
    WCAG 1.4.1 exige de qualquer forma.</p>
  </div>
</section>

<section id="janela">
  <h2>O que o label claro custa, medido</h2>
  <p class="sec-note">O botão primário usa label branco — decisão de identidade. Branco sobre
  <code>#FC5000</code> dá <b>3.34:1</b>: fica abaixo dos 4.5:1 que a WCAG exige de texto normal e acima
  dos 3:1 que ela exige de texto grande e de elemento não-textual. O sistema não esconde isso; ele mede,
  nomeia e mostra onde cada estado cai.</p>
  {brand_window()}
  <div class="callout">
    <p><b>Com label claro a direção inverte — e isso simplifica o sistema.</b> Quando o label era escuro,
    escurecer o preenchimento piorava o texto e só cabiam dois estados de cor. Agora escurecer melhora o
    label, então o hover escurece nos dois temas e o pressed passa a existir como cor de verdade.</p>
    <p><b>O tema escuro tem um teto que o claro não tem.</b> No claro dá para escurecer até
    <code>orange-700</code> (7.94:1) sem penalidade. No escuro o preenchimento também precisa se separar
    da tela: <code>orange-600</code> já deixa a silhueta do botão em 3.37:1 e <code>orange-700</code>
    reprovaria em 2.24:1. Por isso o hover escuro para em <code>orange-550</code> — é o degrau que existe
    exatamente para esse ponto.</p>
    <p><b>Onde AA pleno for obrigatório</b> — texto legal, fluxo crítico, contexto regulado — use a
    variante <code>Secondary</code> ou <code>bg/brand-strong</code> (<code>orange-700</code>, 7.94:1 com
    label branco). Ambas mantêm o label claro e passam em AA no repouso.</p>
  </div>
</section>

<section id="button">
  <h2>Button</h2>
  <p class="sec-note">Primeiro componente do sistema, fechado. Dois component sets irmãos —
  <code>Button</code> e <code>Button Icon</code> — com 120 variantes no total: 4 variantes × 3 tamanhos ×
  5 estados cada, mais slots de ícone dos dois lados, estado de carregamento e a versão só de ícone.
  Alturas 32 / 40 / 48, todas da escala de espaçamento; padding e radius ligados a variáveis. Abaixo,
  tudo renderizado com os tokens reais nos dois temas — o número embaixo de cada grupo é o contraste do
  label medido em cada estado.</p>
  {button_matrix()}
  <div class="callout">
    <p><b>Cada variante tem um trabalho.</b> <code>Primary</code> é a ação principal da tela, uma por vez.
    <code>Secondary</code> é <b>outlined e sem preenchimento</b> — existe para ações menos relevantes, que
    precisam estar disponíveis sem competir com a principal. <code>Ghost</code> é ação terciária, de barra
    de ferramenta e linha de tabela. <code>Danger</code> é destrutiva e sempre pede confirmação.</p>
    <p><b>Tirar o preenchimento do Secondary consertou um bug silencioso.</b> Antes ele tinha fundo
    <code>bg/canvas</code>, o que é invisível sobre a tela branca e vira um retângulo branco em cima de
    qualquer superfície colorida. Sem preenchimento ele funciona sobre qualquer fundo. O tint sutil no
    hover e no pressed ficou: são feedback transitório, não a aparência do botão.</p>
    <p><b>O foco muda de mecanismo conforme haja ou não preenchimento.</b> Variante preenchida usa o anel
    duplo — 2px de <code>border/focus</code> com 2px de offset pintados de <code>bg/canvas</code>, sem o
    qual o anel laranja sumiria em cima do botão laranja. Já <code>Secondary</code> e <code>Ghost</code>
    não têm preenchimento, e no Figma um frame sem preenchimento não projeta sombra: neles o foco vive no
    contorno — 2px por dentro no Secondary, para o botão não mudar de tamanho, e 2px por fora no Ghost,
    que não tem contorno para engrossar.</p>
    <p><b>O ícone não é recolorido à mão.</b> No código ele herda <code>currentColor</code>. No Figma, onde
    isso não existe, o botão declara um modo da collection <code>3. Icon ink</code> e o ícone aninhado
    resolve a própria cor — mesmo efeito, e impossível de esquecer de aplicar.</p>
    <p><b>Loading mantém o label no lugar.</b> O spinner ocupa a posição do ícone esquerdo em vez de
    substituir o texto, para o botão não mudar de largura no meio da interação. Em código ele fica inerte
    e marcado com <code>aria-busy</code> enquanto carrega. No icon-only, ícone e spinner ficam
    empilhados em posição absoluta: se alguém ligar o loading sem desligar o ícone, eles se sobrepõem em
    vez de estourar o quadrado.</p>
    <p><b>O icon-only virou um set separado, não um quarto eixo.</b> Um eixo a mais levaria o
    <code>Button</code> a 120 variantes num set só — e, pior, o booleano <code>Icon left</code> nasce
    desligado, então toda variante só-de-ícone apareceria vazia por padrão. Como set irmão, o ícone é
    conteúdo obrigatório e não uma opção que se esquece de ligar.</p>
    <p><b>Nome acessível é obrigatório no icon-only</b>, e o componente força a lembrança: existe uma
    camada de texto oculta ligada à propriedade <code>Accessible name</code>, que vira
    <code>aria-label</code> no código. Um ícone sem nome é um botão mudo para leitor de tela. E se o ícone
    precisar de tooltip para ser entendido, ele não é inequívoco — nesse caso o certo é o Button com
    label. Os três tamanhos quadrados (32/40/48) passam no mínimo de 24×24 da WCAG 2.2.</p>
  </div>
</section>

<section id="semanticos">
  <h2>Tokens semânticos</h2>
  <p class="sec-note">46 tokens, cada um com um valor por tema. Componente nenhum consome primitiva
  direto — é esta camada que troca quando o tema muda, e é aqui que a intenção fica registrada.</p>
  {semantic_tables()}
</section>

<section id="contraste">
  <h2>O portão de contraste</h2>
  <p class="sec-note">Todo par que o sistema permite que se encontre na tela, medido. Texto em 4.5:1,
  elemento não-textual em 3:1. Estes 70 pares rodam como teste — se um cair, o build quebra.</p>
  {contrast_tables()}
</section>

<section id="tipografia">
  <h2>Tipografia</h2>
  <p class="sec-note">Inter variável, quatro pesos, 14 estilos. Os tamanhos não seguem múltiplos de 8 —
  isso daria 8/16/24/32 e não deixaria nada entre corpo e H3. Quem cai na malha é o line-height: todos
  são múltiplos de 4, e o corpo (16/24) é múltiplo de 8. O tracking negativo cresce com o tamanho porque
  a Inter é espacejada para texto pequeno e fica frouxa acima de 24px.</p>
  {type_specimens()}
</section>

<section id="medidas">
  <h2>Espaçamento, radius e borda</h2>
  <p class="sec-note">Base 4 com ritmo de 8. Múltiplo de 8 puro quebra dentro do componente — gap de
  ícone, padding de chip e offset de foco vivem em 4px. O valor 2 é exceção documentada, só para
  ajuste óptico.</p>
  <div class="grid3">
    <div><h3 class="sub">Espaçamento <span class="count">14 degraus</span></h3>{space_scale()}</div>
    <div><h3 class="sub">Radius <span class="count">9 degraus</span></h3>{radius_scale()}
      <div class="callout"><p><b>Radius aninhado = externo − padding.</b> Card com radius 16 e padding 8
      pede input com radius 8. Sem essa regra, canto aninhado sempre sai errado.</p></div></div>
  </div>
  <div class="callout"><p><b>Foco.</b> Anel de 2px em <code>border/focus</code> com offset de 2px pintado
  da cor do fundo. O offset não é estética: sem ele o anel laranja desaparece em cima do botão laranja.
  No tema escuro o anel troca para <code>orange-400</code>, porque <code>orange-500</code> sobre a tela
  escura tem menos folga.</p></div>
</section>

<section id="elevacao">
  <h2>Elevação</h2>
  <p class="sec-note">Sombra de duas camadas — uma ambiente difusa e uma direcional curta. Camada única
  parece adesivo. A sombra é tingida com o hue frio do neutro em vez de preto puro, que fica barrento.</p>
  {elevation_scale()}
  <div class="callout"><p><b>No tema escuro a sombra não é o cue principal.</b> <code>rgba(0,0,0,.12)</code>
  sobre <code>#15181E</code> é invisível. Quem comunica altura é a superfície clareando:
  <code>950 → 900 → 800</code>. A sombra continua existindo, mais opaca, só como reforço.</p></div>
</section>

<section id="prova">
  <h2>A prova</h2>
  <p class="sec-note">Os mesmos tokens, montados nos dois temas lado a lado. Nada aqui usa valor
  literal — tudo sai da camada semântica.</p>
  {proof()}
</section>

<footer>
  <span><b>AL Design System</b> · Foundation v0.1.0</span>
  <span>Licença MIT</span>
  <span>OKLCH · WCAG 2.1 AA</span>
  <span>Âncora <code>#FC5000</code></span>
</footer>
</div>
'''
open('foundation.html','w').write(HTML)
print("foundation.html:", len(HTML), "bytes")
