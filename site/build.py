"""
Monta a pagina do Button: sidebar, abas e playground interativo.

O CSS do componente entra INLINE, lido de components/button/button.css. O
playground nao reimplementa o botao - ele instancia o mesmo arquivo que vai
para producao. Se o componente quebrar, o playground quebra junto, que e
exatamente o que se quer de um playground.

Rodar: python3 site/build.py     (escreve site/button.html)
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.join(ROOT, 'site')

FOUND_CSS = open(os.path.join(ROOT, 'foundation', 'al-foundation.css')).read()
BTN_TOKENS = open(os.path.join(ROOT, 'components', 'button', 'al-button-tokens.css')).read()
BTN_CSS = open(os.path.join(ROOT, 'components', 'button', 'button.css')).read()
BTN_JSON = json.load(open(os.path.join(ROOT, 'components', 'button', 'tokens.json')))


def declarations(css, selector_re):
    """Extrai as linhas de declaracao de um bloco, pelo seletor."""
    m = re.search(selector_re + r'\s*\{(.*?)\n\}', css, re.S)
    return m.group(1) if m else ''


def scope_themes(found_css, btn_tokens):
    """
    Producao troca o tema no :root, e ai a cadeia de alias resolve sozinha.
    Aqui nao: o playground troca o tema so no palco, e substituicao de custom
    property acontece no elemento onde ela e DECLARADA, nao no ponto de uso.
    Uma alias declarada no :root ja desce resolvida com o valor claro.

    Entao, para o container tematizado funcionar, tudo que aponta para um
    semantico precisa ser re-declarado dentro do bloco de tema: os aneis de
    foco compostos e a camada inteira do Button. Isso e necessidade do
    playground - o CSS que vai para producao nao precisa disso.
    """
    css = found_css.replace(':root[data-theme="dark"] {', '[data-theme="dark"] {')

    root = declarations(css, r':root')
    semantic_light = '\n'.join(
        l for l in root.split('\n')
        if re.match(r'\s*--al-(bg|text|border-(subtle|default|strong|focus|brand|danger|success|warning|info)|shadow|elevation)', l)
    )
    # os compostos: dependem de semanticos, entao re-substituem junto
    rings = '\n'.join(l for l in root.split('\n') if '--al-focus-ring' in l or
                      (l.strip().startswith('0 0 0') and l.strip().endswith((',', ';'))))

    btn = declarations(btn_tokens, r':root')

    css += '\n[data-theme="light"] {\n' + semantic_light + '\n}\n'
    css += ('\n/* Re-declaracao para container tematizado - so o playground precisa.\n'
            '   Ver o comentario em scope_themes(), no site/build.py. */\n'
            '[data-theme="light"], [data-theme="dark"] {\n' + rings + '\n' + btn + '\n}\n')
    return css


CSS = scope_themes(FOUND_CSS, BTN_TOKENS) + '\n' + BTN_TOKENS + '\n' + BTN_CSS

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
        is_on = ' checked' if value == checked else ''
        out.append(
            f'<input type="radio" id="{cid}" name="{name}" value="{value}"{is_on}>'
            f'<label for="{cid}">{label}</label>')
    out.append('</div>')
    return '\n'.join(out)


def token_rows():
    rows = []
    for v, _ in VARIANTS:
        for role in ['bg', 'bg-hover', 'bg-active', 'bg-disabled', 'label',
                     'label-disabled', 'border', 'border-disabled', 'ring']:
            name = f'button-{v}-{role}'
            ref = BTN_JSON['alias'][name]
            res = BTN_JSON['resolved'][name]
            lt = res['light'] if isinstance(res, dict) else res
            sw = (f'<span class="sw" style="background:{lt}"></span>'
                  if isinstance(lt, str) and lt.startswith('#') else '')
            rows.append(
                f'<tr data-variant="{v}"><td class="tok">--al-{name}</td>'
                f'<td class="tok dim">{"transparente" if ref == "transparent" else ref}</td>'
                f'<td class="tok">{sw}{lt if isinstance(lt, str) else lt}</td></tr>')
    return '\n'.join(rows)


def geo_rows():
    rows = []
    for s, _ in SIZES:
        for role in ['padding-x', 'padding-y', 'gap', 'font']:
            name = f'button-{s}-{role}'
            ref = BTN_JSON['alias'][name]
            res = BTN_JSON['resolved'][name]
            val = res[0] if isinstance(res, list) else res
            rows.append(f'<tr><td class="name">{s}</td><td class="tok">--al-{name}</td>'
                        f'<td class="tok dim">{ref}</td><td class="num">{val}</td></tr>')
    for role in ['radius', 'border-width']:
        name = f'button-{role}'
        rows.append(f'<tr><td class="name">ambos</td><td class="tok">--al-{name}</td>'
                    f'<td class="tok dim">{BTN_JSON["alias"][name]}</td>'
                    f'<td class="num">{BTN_JSON["resolved"][name]}</td></tr>')
    return '\n'.join(rows)


def specimen_grid():
    """Todas as combinacoes, estaticas - a folha de especimes."""
    out = []
    for v, vlabel in VARIANTS:
        out.append(f'<div class="spec-row"><div class="spec-name">{vlabel}</div>'
                   f'<div class="spec-cells">')
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


HTML = f"""<title>Button — AL Design System</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap">

<style>
/* ═══ Foundation + tokens do Button + o componente, inline e reais ═══ */
{CSS}

/* ═══ Chrome do site ═══ */
*{{box-sizing:border-box}}
body{{
  margin:0; background:var(--al-bg-canvas); color:var(--al-text-primary);
  font-family:var(--al-font-sans); font-size:15px; line-height:1.6;
  -webkit-font-smoothing:antialiased;
}}
.shell{{display:grid; grid-template-columns:236px 1fr; min-height:100vh}}

/* ── rail ── */
.rail{{
  border-right:1px solid var(--al-border-subtle); background:var(--al-bg-surface);
  padding:26px 0 40px; position:sticky; top:0; height:100vh; overflow-y:auto;
}}
.brand{{display:flex; align-items:center; gap:10px; padding:0 22px 22px; margin-bottom:6px;
  border-bottom:1px solid var(--al-border-subtle)}}
.brand-mark{{width:26px; height:26px; border-radius:7px; background:var(--al-bg-brand);
  display:grid; place-items:center; color:#fff; font-weight:700; font-size:13px; flex:none}}
.brand-name{{font-weight:600; font-size:14px; letter-spacing:-.01em; line-height:1.25}}
.brand-name small{{display:block; font-weight:400; font-size:11px; color:var(--al-text-secondary)}}
.rail-group{{padding:18px 22px 6px; font-family:var(--al-font-mono); font-size:10px;
  font-weight:500; letter-spacing:.14em; text-transform:uppercase; color:var(--al-text-secondary)}}
.rail a{{display:block; padding:7px 22px; color:var(--al-text-secondary); text-decoration:none;
  font-size:13.5px; border-left:2px solid transparent}}
.rail a:hover{{color:var(--al-text-primary); background:var(--al-bg-hover)}}
.rail a[aria-current]{{color:var(--al-bg-brand); border-left-color:var(--al-bg-brand); font-weight:500}}
.rail a.soon{{opacity:.45}}

/* ── conteúdo ── */
.main{{min-width:0}}
.inner{{max-width:1000px; padding:0 40px 100px}}
.phead{{padding:44px 0 0}}
.eyebrow{{font-family:var(--al-font-mono); font-size:10.5px; font-weight:500; letter-spacing:.14em;
  text-transform:uppercase; color:var(--al-text-secondary); margin-bottom:12px}}
h1{{font-size:46px; line-height:1.03; letter-spacing:-.033em; font-weight:700; margin:0 0 12px}}
.lede{{font-size:17px; color:var(--al-text-secondary); margin:0 0 8px; max-width:60ch}}
.meta{{display:flex; flex-wrap:wrap; gap:8px; margin-top:18px}}
.badge{{font-family:var(--al-font-mono); font-size:10.5px; font-weight:500; letter-spacing:.06em;
  padding:4px 10px; border-radius:9999px; background:var(--al-bg-subtle); color:var(--al-text-secondary)}}
.badge.on{{background:var(--al-bg-brand-subtle); color:var(--al-text-brand)}}

/* ── abas ── */
.tabs{{display:flex; gap:2px; border-bottom:1px solid var(--al-border-subtle);
  margin:32px 0 0; position:sticky; top:0; background:var(--al-bg-canvas); z-index:5;
  overflow-x:auto}}
.tabs button{{
  appearance:none; background:none; border:0; border-bottom:2px solid transparent;
  padding:13px 16px; font-family:inherit; font-size:14px; font-weight:500;
  color:var(--al-text-secondary); cursor:pointer; white-space:nowrap; margin-bottom:-1px;
}}
.tabs button:hover{{color:var(--al-text-primary)}}
.tabs button[aria-selected="true"]{{color:var(--al-bg-brand); border-bottom-color:var(--al-bg-brand)}}
.tabs button:focus-visible{{outline:2px solid var(--al-border-focus); outline-offset:-2px}}
.panel[hidden]{{display:none}}
.panel{{padding-top:36px}}

section{{margin-bottom:52px}}
h2{{font-size:12.5px; font-family:var(--al-font-mono); font-weight:500; letter-spacing:.13em;
  text-transform:uppercase; color:var(--al-text-secondary); margin:0 0 20px;
  padding-bottom:10px; border-bottom:1px solid var(--al-border-subtle)}}
h3{{font-size:18px; font-weight:600; letter-spacing:-.015em; margin:0 0 8px}}
p{{margin:0 0 13px; max-width:68ch}}
p:last-child{{margin-bottom:0}}
code{{font-family:var(--al-font-mono); font-size:.86em; background:var(--al-bg-subtle);
  padding:2px 5px; border-radius:4px; white-space:nowrap}}

/* ── playground ── */
.pg{{border:1px solid var(--al-border-subtle); border-radius:12px; overflow:hidden}}
.stage{{
  display:grid; place-items:center; min-height:230px; padding:44px 24px;
  background:var(--al-bg-surface);
  background-image:radial-gradient(var(--al-border-subtle) 1px, transparent 1px);
  background-size:16px 16px;
}}
.stage[data-theme]{{background-color:var(--al-bg-canvas)}}
.controls{{border-top:1px solid var(--al-border-subtle); background:var(--al-bg-canvas);
  padding:20px 22px; display:grid; gap:16px}}
.ctl{{display:grid; grid-template-columns:104px 1fr; gap:14px; align-items:center}}
.ctl > label:first-child, .ctl > .ctl-name{{
  font-family:var(--al-font-mono); font-size:10.5px; font-weight:500; letter-spacing:.1em;
  text-transform:uppercase; color:var(--al-text-secondary);
}}
.seg{{display:inline-flex; flex-wrap:wrap; gap:6px}}
.seg input{{position:absolute; opacity:0; width:1px; height:1px}}
.seg label{{
  padding:6px 13px; border-radius:9999px; border:1px solid var(--al-border-default);
  font-size:13px; cursor:pointer; color:var(--al-text-secondary); user-select:none;
}}
.seg label:hover{{background:var(--al-bg-hover); color:var(--al-text-primary)}}
.seg input:checked + label{{
  background:var(--al-bg-brand-subtle); border-color:var(--al-bg-brand);
  color:var(--al-text-brand); font-weight:500;
}}
.seg input:focus-visible + label{{outline:2px solid var(--al-border-focus); outline-offset:2px}}
.txt{{
  font-family:inherit; font-size:13.5px; padding:7px 11px; width:100%; max-width:280px;
  border:1px solid var(--al-border-default); border-radius:8px;
  background:var(--al-bg-canvas); color:var(--al-text-primary);
}}
.txt:focus-visible{{outline:2px solid var(--al-border-focus); outline-offset:1px; border-color:var(--al-border-focus)}}

/* ── código gerado ── */
.codewrap{{border-top:1px solid var(--al-border-subtle)}}
.codebar{{display:flex; align-items:center; justify-content:space-between; gap:12px;
  padding:11px 22px; background:var(--al-bg-surface); border-bottom:1px solid var(--al-border-subtle)}}
.codebar span{{font-family:var(--al-font-mono); font-size:10.5px; font-weight:500;
  letter-spacing:.1em; text-transform:uppercase; color:var(--al-text-secondary)}}
.copy{{
  appearance:none; border:1px solid var(--al-border-default); background:var(--al-bg-canvas);
  color:var(--al-text-secondary); font-family:var(--al-font-mono); font-size:11px;
  padding:5px 12px; border-radius:9999px; cursor:pointer;
}}
.copy:hover{{color:var(--al-text-primary); border-color:var(--al-border-strong)}}
.copy:focus-visible{{outline:2px solid var(--al-border-focus); outline-offset:2px}}
pre{{margin:0; padding:18px 22px; overflow-x:auto; background:var(--al-bg-canvas)}}
pre code{{background:none; padding:0; font-size:12.5px; line-height:1.65; white-space:pre; color:var(--al-text-primary)}}

/* ── tabelas ── */
.scroller{{overflow-x:auto; border:1px solid var(--al-border-subtle); border-radius:10px}}
table{{border-collapse:collapse; width:100%; font-size:13px; min-width:620px}}
th,td{{padding:9px 15px; text-align:left; border-bottom:1px solid var(--al-border-subtle)}}
thead th{{font-family:var(--al-font-mono); font-size:10px; font-weight:500; letter-spacing:.1em;
  text-transform:uppercase; color:var(--al-text-secondary); background:var(--al-bg-surface); white-space:nowrap}}
tbody tr:last-child td{{border-bottom:0}}
td.tok{{font-family:var(--al-font-mono); font-size:12px; white-space:nowrap}}
td.tok.dim{{color:var(--al-text-secondary)}}
td.name{{font-weight:600}}
td.num{{font-family:var(--al-font-mono); text-align:right; font-variant-numeric:tabular-nums}}
.sw{{display:inline-block; width:11px; height:11px; border-radius:3px; vertical-align:-1px;
  margin-right:7px; border:1px solid var(--al-border-subtle)}}

/* ── folha de espécimes ── */
.spec-row{{display:grid; grid-template-columns:96px 1fr; gap:18px; align-items:start;
  padding:20px 0; border-top:1px solid var(--al-border-subtle)}}
.spec-row:last-child{{border-bottom:1px solid var(--al-border-subtle)}}
.spec-name{{font-weight:600; font-size:14px; padding-top:20px}}
.spec-cells{{display:flex; flex-wrap:wrap; gap:22px}}
.spec-cell{{display:flex; flex-direction:column; gap:8px; align-items:flex-start}}
.spec-label{{font-family:var(--al-font-mono); font-size:9.5px; letter-spacing:.1em;
  text-transform:uppercase; color:var(--al-text-secondary)}}

/* ── anatomia ── */
.anat{{display:grid; grid-template-columns:repeat(auto-fit,minmax(190px,1fr)); gap:1px;
  background:var(--al-border-subtle); border:1px solid var(--al-border-subtle); border-radius:10px; overflow:hidden}}
.anat > div{{background:var(--al-bg-canvas); padding:16px 18px}}
.anat b{{display:block; font-family:var(--al-font-mono); font-size:10px; letter-spacing:.1em;
  text-transform:uppercase; color:var(--al-bg-brand); margin-bottom:5px}}
.anat span{{font-size:13px; color:var(--al-text-secondary)}}

.note{{padding:15px 18px; background:var(--al-bg-surface); border-left:2px solid var(--al-bg-brand);
  border-radius:0 8px 8px 0; font-size:14px; margin-bottom:14px}}
.note b{{display:block; margin-bottom:4px}}
.rule{{display:grid; grid-template-columns:auto 1fr; gap:18px; padding:20px 0;
  border-top:1px solid var(--al-border-subtle)}}
.rule:last-of-type{{border-bottom:1px solid var(--al-border-subtle)}}
.rn{{font-family:var(--al-font-mono); font-size:11.5px; font-weight:500; color:var(--al-text-secondary); padding-top:3px}}
.dd{{display:grid; grid-template-columns:repeat(auto-fit,minmax(270px,1fr)); gap:1px;
  background:var(--al-border-subtle); border:1px solid var(--al-border-subtle);
  border-radius:10px; overflow:hidden; margin-bottom:14px}}
.dd .cell{{background:var(--al-bg-canvas); padding:18px 20px; display:flex; flex-direction:column; gap:13px}}
.dd .lab{{font-family:var(--al-font-mono); font-size:10px; font-weight:500; letter-spacing:.13em;
  text-transform:uppercase; display:flex; align-items:center; gap:7px}}
.dd .do .lab{{color:var(--al-text-success)}}
.dd .no .lab{{color:var(--al-text-danger)}}
.dd .lab::before{{content:''; width:7px; height:7px; border-radius:50%; background:currentColor}}
.dd .stage2{{display:flex; flex-wrap:wrap; gap:11px; align-items:center; padding:18px 16px;
  background:var(--al-bg-surface); border-radius:8px; min-height:72px}}
.dd .cap{{font-size:13px; color:var(--al-text-secondary); margin:0}}
.dd .cap b{{color:var(--al-text-primary); font-weight:600}}

/* ── estados forçados: SÓ para o playground e a folha de espécimes.
      Repetem as declarações reais do button.css, porque :hover e :active
      não podem ser simulados sem ponteiro. ── */
.al-btn.is-hover{{background-color:var(--_bg-hover)}}
.al-btn.is-active{{background-color:var(--_bg-active)}}
.al-btn.is-focus{{box-shadow:var(--_ring); outline:none}}

@media (max-width:900px){{
  .shell{{grid-template-columns:1fr}}
  .rail{{position:static; height:auto; padding-bottom:18px}}
  .rail-nav{{display:flex; flex-wrap:wrap; gap:2px; padding:0 14px}}
  .rail-group{{padding:12px 22px 4px}}
  .inner{{padding:0 20px 72px}}
  h1{{font-size:34px}}
  .ctl{{grid-template-columns:1fr; gap:8px}}
  .spec-row{{grid-template-columns:1fr}}
  .spec-name{{padding-top:0}}
}}
</style>

<div class="shell">
  <nav class="rail" aria-label="Navegação do design system">
    <div class="brand">
      <span class="brand-mark">AL</span>
      <span class="brand-name">AL Design System<small>v0.1.0 · MIT</small></span>
    </div>
    <div class="rail-nav">
      <div class="rail-group">Fundação</div>
      <a href="#" class="soon">Cor</a>
      <a href="#" class="soon">Tipografia</a>
      <a href="#" class="soon">Espaçamento</a>
      <div class="rail-group">Componentes</div>
      <a href="#" aria-current="page">Button</a>
      <a href="#" class="soon">Icon</a>
      <a href="#" class="soon">Badge</a>
      <a href="#" class="soon">Avatar</a>
    </div>
  </nav>

  <main class="main">
    <div class="inner">
      <header class="phead">
        <div class="eyebrow">Componentes</div>
        <h1>Button</h1>
        <p class="lede">Dispara a ação de uma tela. Quatro variantes que carregam pesos diferentes na hierarquia, dois tamanhos, cinco estados.</p>
        <div class="meta">
          <span class="badge on">Estável</span>
          <span class="badge">40 variantes no Figma</span>
          <span class="badge">46 tokens</span>
          <span class="badge">0 valores soltos</span>
        </div>
      </header>

      <div class="tabs" role="tablist" aria-label="Seções do Button">
        <button role="tab" id="t-overview" aria-controls="p-overview" aria-selected="true">Visão geral</button>
        <button role="tab" id="t-specs" aria-controls="p-specs" aria-selected="false" tabindex="-1">Especificações</button>
        <button role="tab" id="t-guide" aria-controls="p-guide" aria-selected="false" tabindex="-1">Diretrizes</button>
        <button role="tab" id="t-a11y" aria-controls="p-a11y" aria-selected="false" tabindex="-1">Acessibilidade</button>
      </div>

      <!-- ═══════════ VISÃO GERAL ═══════════ -->
      <div class="panel" id="p-overview" role="tabpanel" aria-labelledby="t-overview" tabindex="0">
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
              <div class="ctl"><span class="ctl-name">Tema</span>{seg('theme', [('auto','Do sistema'),('light','Claro'),('dark','Escuro')], 'auto')}</div>
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
            O botão acima é o componente real: esta página carrega o mesmo <code>button.css</code> que vai para produção.
            Hover, pressed e focus são forçados por classe, porque não dá para simular ponteiro — as declarações são as mesmas.
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
        </section>
      </div>

      <!-- ═══════════ ESPECIFICAÇÕES ═══════════ -->
      <div class="panel" id="p-specs" role="tabpanel" aria-labelledby="t-specs" tabindex="0" hidden>
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
            Altura é consequência: <code>padding-y</code> × 2 mais a entrelinha. Dá {BTN_JSON['derived']['height']['sm']}px no <code>sm</code> e {BTN_JSON['derived']['height']['md']}px no <code>md</code> — conferido no navegador contra o Figma. Um token de altura fixaria a mesma decisão em dois lugares.
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
        </section>
      </div>

      <!-- ═══════════ DIRETRIZES ═══════════ -->
      <div class="panel" id="p-guide" role="tabpanel" aria-labelledby="t-guide" tabindex="0" hidden>
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
                <tr><td class="name">Só ícone</td><td>Set irmão</td><td><code>Button Icon</code>, com nome acessível obrigatório.</td></tr>
              </tbody>
            </table>
          </div>
        </section>
      </div>

      <!-- ═══════════ ACESSIBILIDADE ═══════════ -->
      <div class="panel" id="p-a11y" role="tabpanel" aria-labelledby="t-a11y" tabindex="0" hidden>
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
        </section>
      </div>
    </div>
  </main>
</div>

<script>
(function () {{
  var demo  = document.getElementById('demo');
  var stage = document.getElementById('stage');
  var code  = document.getElementById('code');
  var lead  = demo.querySelector('.al-btn__icon--leading');
  var trail = demo.querySelector('.al-btn__icon--trailing');
  var label = demo.querySelector('.al-btn__label');
  var input = document.getElementById('labeltext');

  function pick(name) {{
    var el = document.querySelector('input[name="' + name + '"]:checked');
    return el ? el.value : null;
  }}

  function render() {{
    var variant = pick('variant'), size = pick('size');
    var state = pick('state'), icon = pick('icon'), theme = pick('theme');

    demo.className = 'al-btn al-btn--' + variant + ' al-btn--' + size
      + (state === 'hover' || state === 'active' || state === 'focus' ? ' is-' + state : '');

    demo.removeAttribute('aria-disabled');
    demo.removeAttribute('aria-busy');
    if (state === 'disabled') demo.setAttribute('aria-disabled', 'true');
    if (state === 'busy') {{
      demo.setAttribute('aria-busy', 'true');
      demo.setAttribute('aria-disabled', 'true');
    }}

    lead.hidden  = !(icon === 'leading');
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
    code.innerHTML = lines.join('\\n');
  }}

  document.querySelectorAll('.controls input').forEach(function (el) {{
    el.addEventListener('change', render);
    el.addEventListener('input', render);
  }});

  // filtro da tabela de tokens
  document.querySelectorAll('input[name="tokfilter"]').forEach(function (el) {{
    el.addEventListener('change', function () {{
      var v = pick('tokfilter');
      document.querySelectorAll('#tokbody tr').forEach(function (tr) {{
        tr.hidden = (v !== 'all' && tr.getAttribute('data-variant') !== v);
      }});
    }});
  }});

  // copiar marcação
  document.getElementById('copy').addEventListener('click', function () {{
    var btn = this;
    var text = code.textContent;
    var done = function () {{ btn.textContent = 'Copiado'; setTimeout(function () {{ btn.textContent = 'Copiar'; }}, 1600); }};
    if (navigator.clipboard && navigator.clipboard.writeText) {{
      navigator.clipboard.writeText(text).then(done, function () {{ btn.textContent = 'Não deu'; }});
    }} else {{
      var ta = document.createElement('textarea');
      ta.value = text; document.body.appendChild(ta); ta.select();
      try {{ document.execCommand('copy'); done(); }} catch (e) {{ btn.textContent = 'Não deu'; }}
      document.body.removeChild(ta);
    }}
  }});

  // abas, com navegação por seta como manda o padrão
  var tabs = Array.prototype.slice.call(document.querySelectorAll('[role="tab"]'));
  function select(tab) {{
    tabs.forEach(function (t) {{
      var on = t === tab;
      t.setAttribute('aria-selected', on ? 'true' : 'false');
      t.tabIndex = on ? 0 : -1;
      document.getElementById(t.getAttribute('aria-controls')).hidden = !on;
    }});
  }}
  tabs.forEach(function (tab, i) {{
    tab.addEventListener('click', function () {{ select(tab); }});
    tab.addEventListener('keydown', function (e) {{
      var next = null;
      if (e.key === 'ArrowRight') next = tabs[(i + 1) % tabs.length];
      if (e.key === 'ArrowLeft') next = tabs[(i - 1 + tabs.length) % tabs.length];
      if (e.key === 'Home') next = tabs[0];
      if (e.key === 'End') next = tabs[tabs.length - 1];
      if (next) {{ e.preventDefault(); select(next); next.focus(); }}
    }});
  }});

  render();
}})();
</script>
"""

open(os.path.join(HERE, 'button.html'), 'w').write(HTML)
print(f'site/button.html escrito ({len(HTML)} bytes)')
print(f'  CSS inline        : foundation + tokens do Button + button.css (o real)')
print(f'  abas              : 4')
print(f'  combinacoes vivas : {len(VARIANTS)} variantes x {len(SIZES)} tamanhos x {len(STATES)} estados x {len(ICONS)} icones')
