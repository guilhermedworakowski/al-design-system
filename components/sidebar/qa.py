"""
Gera a visualizacao de QA do Sidebar (etapa 6) em site/sidebar-qa.html.

Mesmo arranjo dos outros componentes: a pagina INLINA os arquivos reais do
repositorio - foundation, Icon, Tab, Avatar, Icon Button, tokens do Sidebar,
sidebar.css e sidebar.js. Ela nao pode divergir do codigo porque ela E o
codigo. O unico script a mais e o cromo (tema, troca de pagina atual, medicao).

O QUE A PAGINA MOSTRA

  - a propria pagina E um layout com Sidebar: ela fica a esquerda, presa no
    topo enquanto a pagina rola, com "Pular para o conteudo" antes dela.
    Estreitando a janela abaixo de 1024px ela some e aparece o botao Menu;
  - um quadro de celular (iframe de 375px) com o MESMO codigo, para testar o
    painel modal sem mexer na janela;
  - duas Sidebars CONGELADAS (inert, altura de exemplo) para comparar com o
    Figma: nome longo com reticencias e sem Ajuda; e a do Figma, com Ajuda;
  - o contraste lido do navegador, com getComputedStyle, depois da transicao.

O a11y.py ao lado le o HTML que este script emite e cobra ali o contrato de
marcacao.

Rodar: python3 qa.py     (escreve o proprio arquivo; nunca redirecionar stdout)
"""
import html as H
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(ROOT, 'site', 'sidebar-qa.html')

FOUND = json.load(open(os.path.join(ROOT, 'tokens.json')))
SBR = json.load(open(os.path.join(HERE, 'tokens.json')))
COMP = os.path.join(ROOT, 'components')

CSS_FILES = [
    ('foundation', os.path.join(ROOT, 'foundation', 'al-foundation.css')),
    ('icon - tokens', os.path.join(COMP, 'icon', 'al-icon-tokens.css')),
    ('icon', os.path.join(COMP, 'icon', 'icon.css')),
    ('icon-button - tokens', os.path.join(COMP, 'icon-button', 'al-icon-button-tokens.css')),
    ('icon-button', os.path.join(COMP, 'icon-button', 'icon-button.css')),
    ('avatar - tokens', os.path.join(COMP, 'avatar', 'al-avatar-tokens.css')),
    ('avatar', os.path.join(COMP, 'avatar', 'avatar.css')),
    ('tab - tokens', os.path.join(COMP, 'tab', 'al-tab-tokens.css')),
    ('tab', os.path.join(COMP, 'tab', 'tab.css')),
    ('sidebar - tokens', os.path.join(HERE, 'al-sidebar-tokens.css')),
    ('sidebar', os.path.join(HERE, 'sidebar.css')),
]
JS_FILES = [os.path.join(HERE, 'sidebar.js')]


def icon(name):
    svg = open(os.path.join(COMP, 'icon', 'icons', f'{name}.svg'), encoding='utf-8').read()
    path = re.search(r'<svg[^>]*>(.*?)</svg>', svg, flags=re.S).group(1).strip()
    return ('<svg class="al-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
            f'aria-hidden="true" focusable="false">{path}</svg>')


def item(rotulo, atual=False):
    slug = re.sub(r'[^a-z0-9]+', '-', rotulo.lower().encode('ascii', 'ignore').decode()).strip('-')
    cur = ' aria-current="page"' if atual else ''
    return (f'<li><a class="al-tab" href="#{slug}"{cur}>'
            f'<span class="al-tab__label">{rotulo}</span></a></li>')


def lista(itens, atual, labelledby=None):
    lab = f' aria-labelledby="{labelledby}"' if labelledby else ''
    return (f'<ul class="al-tabs al-tabs--square"{lab}>'
            + ''.join(item(i, i == atual) for i in itens) + '</ul>')


def grupo(pid, rotulo, itens, atual, extra=''):
    gid = f'{pid}-g-{re.sub(r"[^a-z]+", "-", rotulo.lower())}'
    return (f'<div class="al-sidebar__group{extra}">'
            f'<p class="al-sidebar__group-label" id="{gid}">{rotulo}</p>'
            f'{lista(itens, atual, gid)}</div>')


def avatar(kind, ini):
    if kind == 'icon':
        inner = icon('user')
    else:
        inner = f'<span class="al-avatar__initials">{ini}</span>'
    return f'<span class="al-avatar al-avatar--md" aria-hidden="true">{inner}</span>'


def sidebar(pid, nome, email, ini, grupos, soltos=(), atual=None, ajuda=True, av='initials'):
    miolo = ''
    if soltos:
        miolo += lista(soltos, atual)
    miolo += ''.join(grupo(pid, r, its, atual) for r, its in grupos)
    sup = grupo(pid, 'Ajuda', ['Central de ajuda', 'Documentação', 'Enviar feedback'], atual,
                ' al-sidebar__support') if ajuda else ''
    return (f'<aside class="al-sidebar" id="{pid}" aria-label="Barra lateral">'
            f'<div class="al-sidebar__profile">{avatar(av, ini)}'
            f'<div class="al-sidebar__details"><div class="al-sidebar__user">'
            f'<p class="al-sidebar__name">{nome}</p><p class="al-sidebar__email">{email}</p></div>'
            f'<a class="al-icon-btn al-icon-btn--ghost al-icon-btn--sm" href="#conta" '
            f'aria-label="Abrir minha conta">{icon("chevron-right")}</a></div></div>'
            f'<nav class="al-sidebar__nav" aria-label="Principal">'
            f'<div class="al-sidebar__content">{miolo}</div>{sup}</nav></aside>')


GRUPOS_VIVOS = [
    ('Vendas', ['Pedidos', 'Clientes', 'Produtos', 'Cupons']),
    ('Financeiro', ['Faturas', 'Pagamentos', 'Relatórios']),
    ('Operação', ['Estoque', 'Entregas', 'Fornecedores', 'Devoluções']),
    ('Conta', ['Equipe', 'Integrações', 'Preferências']),
]


def menu_btn():
    return ('<button type="button" class="al-icon-btn al-icon-btn--ghost al-icon-btn--md" '
            'aria-label="Menu" aria-controls="sb" aria-expanded="false" '
            f'data-al-sidebar-open="sb">{icon("menu")}</button>')


def viva():
    return sidebar('sb', 'Jane Doe', 'jane.doe@gmail.com', 'JD', GRUPOS_VIVOS,
                   soltos=['Início', 'Caixa de entrada'], atual='Início')


def congeladas():
    a = sidebar('frz-a', 'Maria Eduarda Albuquerque Cavalcanti',
                'maria.eduarda.albuquerque@empresaexemplo.com.br', 'MA',
                [('Vendas', ['Pedidos', 'Clientes', 'Produtos'])], soltos=['Início'],
                atual='Clientes', ajuda=False)
    b = sidebar('frz-b', 'Jane Doe', 'jane.doe@gmail.com', 'JD', [], soltos=[], ajuda=True, av='icon')
    cel = []
    for rot, s in (('nome longo · item atual · sem Ajuda', a), ('como no Figma · slot vazio · Ajuda', b)):
        cel.append(f'<div class="qa-cell" inert aria-hidden="true"><p class="qa-matrix__label">{rot}</p>{s}</div>')
    return ''.join(cel)


def style(css_inline):
    return f'''<style>
{css_inline}

/* ================= cromo da pagina de QA =================
   Usa os proprios tokens do AL. Nao ha paleta paralela aqui de proposito. */
html, body {{ background: var(--al-bg-canvas); }}
body {{
  margin: 0;
  color: var(--al-text-primary);
  font-family: var(--al-font-sans);
  font-size: var(--al-font-size-md);
  line-height: var(--al-line-height-md);
}}
.qa-skip {{
  position: absolute; inset-inline-start: var(--al-space-8); inset-block-start: var(--al-space-8);
  z-index: 10; padding: var(--al-space-8) var(--al-space-16); border-radius: var(--al-radius-md);
  background: var(--al-bg-brand); color: var(--al-text-on-brand); font-weight: 600;
  translate: 0 -200%;
}}
.qa-skip:focus {{ translate: none; outline: none; box-shadow: var(--al-focus-ring-default); }}
.qa-shell {{ display: flex; min-height: 100dvh; }}
.qa-main {{ flex: 1 1 auto; min-width: 0; outline: none; }}
.qa-topbar {{
  position: sticky; top: 0; z-index: 2;
  display: flex; align-items: center; gap: var(--al-space-12);
  padding: var(--al-space-12) var(--al-space-24);
  background: var(--al-bg-canvas); border-bottom: 1px solid var(--al-border-subtle);
}}
.qa-topbar .qa-where {{ flex: 1; margin: 0; font-size: var(--al-font-size-sm); color: var(--al-text-secondary); }}
.qa-topbar .qa-where strong {{ color: var(--al-text-primary); font-weight: 600; }}
.qa-wrap {{
  max-width: 1040px;
  padding-inline: var(--al-space-24);
  padding-block: var(--al-space-32) var(--al-space-64);
  display: flex; flex-direction: column; gap: var(--al-space-48);
}}
.qa-head h1 {{ margin: 0; font-size: var(--al-font-size-3xl); line-height: var(--al-line-height-3xl); font-weight: 600; letter-spacing: -0.02em; text-wrap: balance; }}
.qa-sub {{ margin: var(--al-space-4) 0 0; color: var(--al-text-secondary); font-size: var(--al-font-size-sm); }}
.qa-btn {{
  display: inline-flex; align-items: center; gap: var(--al-space-8);
  padding: var(--al-space-8) var(--al-space-16);
  border: 1px solid var(--al-border-strong); border-radius: var(--al-radius-full);
  background: var(--al-bg-surface-raised); color: var(--al-text-primary);
  font: inherit; font-size: var(--al-font-size-sm); cursor: pointer;
}}
.qa-btn:focus-visible {{ outline: none; box-shadow: var(--al-focus-ring-default); }}
section > h2 {{ margin: 0 0 var(--al-space-4); font-size: var(--al-font-size-xl); line-height: var(--al-line-height-xl); font-weight: 600; letter-spacing: -0.01em; }}
section > p.qa-lede {{ margin: 0 0 var(--al-space-20); color: var(--al-text-secondary); max-width: 66ch; }}
.qa-tag {{
  font-size: var(--al-font-size-xs); line-height: var(--al-line-height-xs);
  padding: 2px var(--al-space-8); border-radius: var(--al-radius-full);
  border: 1px solid var(--al-border-default); color: var(--al-text-secondary);
  white-space: nowrap; vertical-align: middle; margin-left: var(--al-space-8); font-weight: 400; letter-spacing: 0;
}}
.qa-tag--real {{ border-color: var(--al-border-success); color: var(--al-text-success); }}
.qa-tag--simulado {{ border-color: var(--al-border-warning); color: var(--al-text-warning); }}
.qa-checks {{ margin: 0; padding-left: var(--al-space-20); display: grid; gap: var(--al-space-8); max-width: 72ch; }}
.qa-checks li {{ color: var(--al-text-secondary); }}
.qa-checks strong {{ color: var(--al-text-primary); font-weight: 500; }}
.qa-tablewrap {{ overflow-x: auto; }}
table.qa-measure {{ border-collapse: collapse; width: 100%; font-size: var(--al-font-size-sm); font-variant-numeric: tabular-nums; }}
table.qa-measure th, table.qa-measure td {{ text-align: left; padding: var(--al-space-8) var(--al-space-12); border-bottom: 1px solid var(--al-border-subtle); white-space: nowrap; }}
table.qa-measure th {{ font-weight: 600; font-size: var(--al-font-size-xs); text-transform: uppercase; letter-spacing: 0.04em; color: var(--al-text-secondary); }}
.qa-verdict {{ font-weight: 600; }}
.qa-verdict--ok {{ color: var(--al-text-success); }}
.qa-verdict--exc {{ color: var(--al-text-warning); }}
.qa-verdict--bad {{ color: var(--al-text-danger); }}
.qa-foot {{ color: var(--al-text-secondary); font-size: var(--al-font-size-sm); border-top: 1px solid var(--al-border-subtle); padding-top: var(--al-space-16); }}
code {{ font-family: var(--al-font-mono); font-size: 0.9em; }}

/* ---- especificos do Sidebar ---- */
.qa-panel {{ padding: var(--al-space-24); border-radius: var(--al-radius-xl); background: var(--al-bg-surface); }}
.qa-matrix {{ display: flex; flex-wrap: wrap; gap: var(--al-space-24); align-items: flex-start; }}
.qa-matrix__label {{ margin: 0 0 var(--al-space-8); font-size: var(--al-font-size-xs); font-weight: 600; letter-spacing: 0.04em; text-transform: uppercase; color: var(--al-text-secondary); }}
/* congeladas: caixa comum com altura de exemplo, visiveis em qualquer largura */
.qa-cell .al-sidebar {{ display: flex; position: static; block-size: 560px; }}
.qa-phone {{
  display: block; inline-size: 375px; max-inline-size: 100%; block-size: 667px;
  border: 1px solid var(--al-border-default); border-radius: var(--al-radius-xl);
  background: var(--al-bg-canvas);
}}
.qa-copy {{ margin: 0 0 var(--al-space-12); color: var(--al-text-secondary); max-width: 66ch; }}
</style>'''


def phone_doc(css_block, js_inline):
    corpo = (
        '<a class="qa-skip" href="#m-main">Pular para o conteúdo</a>'
        '<div class="qa-shell">'
        + sidebar('sb', 'Jane Doe', 'jane.doe@gmail.com', 'JD', GRUPOS_VIVOS[:2],
                  soltos=['Início'], atual='Pedidos')
        + '<main class="qa-main" id="m-main" tabindex="-1"><div class="qa-topbar">'
        + menu_btn() + '<p class="qa-where">Página: <strong>Pedidos</strong></p></div>'
        '<div class="qa-wrap"><p class="qa-copy">Toque em Menu. O painel entra pela esquerda; '
        'o foco cai em “Pedidos”, o item atual. Escolher um destino, tocar fora ou apertar Esc '
        'fecha.</p></div></main></div>'
    )
    return (f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width, initial-scale=1">'
            f'{css_block}</head><body>{corpo}<script>{js_inline}</script></body></html>')


def build():
    css = []
    for nome, path in CSS_FILES:
        css.append(f'/* ================= {nome} ================= */')
        css.append(open(path, encoding='utf-8').read())
    css_block = style('\n'.join(css))
    js_inline = '\n'.join(open(f, encoding='utf-8').read() for f in JS_FILES)
    phone = H.escape(phone_doc(css_block, js_inline), quote=True)

    meta = SBR['meta']
    a11y_path = os.path.join(HERE, 'a11y.json')
    resumo = ''
    if os.path.exists(a11y_path):
        a = json.load(open(a11y_path))
        rs = a['rows']
        resumo = (f' · portão: {len(rs)} combinações, {sum(r["pass"] for r in rs)} passam, '
                  f'{sum(bool(r["exception"]) for r in rs)} exceções, '
                  f'{sum((not r["pass"]) and not r["exception"] for r in rs)} reprovas')

    return f'''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AL Sidebar QA</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400&display=swap">
{css_block}
</head>
<body>
<a class="qa-skip" href="#qa-main">Pular para o conteúdo</a>
<div class="qa-shell">
{viva()}
<main class="qa-main" id="qa-main" tabindex="-1">
  <div class="qa-topbar">
    {menu_btn()}
    <p class="qa-where">Página atual: <strong id="qa-current">Início</strong></p>
    <button type="button" class="qa-btn" id="theme-toggle" aria-pressed="false">
      <span id="theme-label">Tema claro</span>
    </button>
  </div>
  <div class="qa-wrap">
    <header class="qa-head">
      <h1>Sidebar — QA da etapa 6</h1>
      <p class="qa-sub">AL Design System {FOUND['meta']['version']} · componente {meta['version']} ·
      tela larga + celular × 2 temas{resumo}</p>
    </header>

    <section>
      <h2>O que testar</h2>
      <ol class="qa-checks">
        <li><strong>Recarregue e aperte Tab uma vez</strong>: aparece “Pular para o conteúdo”. Enter leva o foco direto para esta área, sem passar pela Sidebar (regra 29).</li>
        <li><strong>Tab pela Sidebar</strong>: botão do perfil, depois cada item na ordem, grupo a grupo, e a Ajuda por último. Setas não fazem nada (regra 28). O anel aparece em cada um.</li>
        <li><strong>Clique em um item</strong>: ele vira o atual (tonal laranja) e o anterior volta ao normal; a barra de cima diz a página. Só um atual por vez (regra 12).</li>
        <li><strong>Passe o mouse e aperte</strong> nos itens e no botão do perfil, nos dois temas: o fundo do hover e do pressionado tem que aparecer sobre a Sidebar.</li>
        <li><strong>Role esta página</strong>: a Sidebar fica parada. <strong>Role sobre o miolo da Sidebar</strong>: só os grupos rolam; perfil e Ajuda ficam (regra 5).</li>
        <li><strong>Estreite a janela abaixo de 1024px</strong>: a Sidebar some e aparece o botão Menu à esquerda da barra de cima. Abra: o painel entra pela esquerda, o foco cai no item atual, Tab fica preso nele. Esc fecha e devolve o foco ao Menu; clicar fora fecha; escolher um item fecha. Alargue a janela com o painel aberto: ele fecha e a Sidebar volta ao lugar (regras 24 e 25).</li>
        <li><strong>No quadro de celular abaixo</strong> o mesmo, sem mexer na janela.</li>
        <li><strong>Troque o tema</strong> com o painel aberto: no escuro ele quase não se separa do fundo escurecido pela cor; quem separa é a borda e a sombra (achado 2).</li>
        <li><strong>Leitor de tela</strong> (VoiceOver: Ctrl+Opção+U, Pontos de referência): “Barra lateral” e “Principal, navegação”. Nos grupos: “Vendas, lista, 4 itens”. O item atual: “página atual”. O botão do perfil: “Abrir minha conta”.</li>
        <li><strong>“Reduzir movimento”</strong> ligado no sistema: o painel abre e fecha sem deslizar.</li>
      </ol>
    </section>

    <section>
      <h2>Celular <span class="qa-tag qa-tag--real">real</span></h2>
      <p class="qa-lede">Um quadro de 375px com o mesmo CSS e o mesmo <code>sidebar.js</code>: abaixo de
      1024px a Sidebar vira painel modal pela esquerda, aberto pelo botão Menu.</p>
      <iframe class="qa-phone" id="qa-phone" title="Sidebar no celular, 375px" srcdoc="{phone}"></iframe>
    </section>

    <section>
      <h2>Congeladas <span class="qa-tag qa-tag--simulado">simulado</span></h2>
      <p class="qa-lede">Mesmo CSS, com uma altura de exemplo no lugar da altura da tela, para comparar
      com o Figma. A da esquerda testa as reticências no nome e no e-mail (regra 20); a da direita é o
      desenho do Figma, com o slot vazio. Não recebem foco.</p>
      <div class="qa-panel"><div class="qa-matrix" id="matrix-frozen">{congeladas()}</div></div>
    </section>

    <section>
      <h2>Contraste medido no navegador</h2>
      <p class="qa-lede">Não são os números do <code>tokens.json</code>: o script lê a cor que o navegador
      pintou na Sidebar viva, com <code>getComputedStyle</code>, depois da transição terminar.</p>
      <div class="qa-tablewrap">
        <table class="qa-measure">
          <thead><tr><th>onde</th><th>o quê</th><th>cor</th><th>fundo</th><th>medido</th><th>piso</th><th>veredito</th></tr></thead>
          <tbody id="measure-body"></tbody>
        </table>
      </div>
    </section>

    <p class="qa-foot">Gerado por <code>components/sidebar/qa.py</code> a partir do CSS e do JS em
    <code>dev</code>. Foundation, Icon, Icon Button, Avatar, Tab, <code>al-sidebar-tokens.css</code>,
    <code>sidebar.css</code> e <code>sidebar.js</code> estão embutidos como estão no repositório.</p>
  </div>
</main>
</div>

<script>
{js_inline}
</script>
<script>
(function () {{
  var root = document.documentElement;
  function r(id) {{ return document.getElementById(id); }}

  // ------------------------------------------------------------------ tema
  var btn = r('theme-toggle');
  var label = r('theme-label');
  var phone = r('qa-phone');
  function escuro() {{
    if (root.dataset.theme) return root.dataset.theme === 'dark';
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  }}
  function sincronizar() {{
    try {{
      var d = phone.contentDocument;
      if (d && d.documentElement) d.documentElement.dataset.theme = escuro() ? 'dark' : 'light';
    }} catch (e) {{}}
  }}
  function pintarBotao() {{
    var d = escuro();
    label.textContent = d ? 'Tema escuro' : 'Tema claro';
    btn.setAttribute('aria-pressed', String(d));
    sincronizar();
  }}
  function depois() {{
    setTimeout(function () {{
      Promise.all(document.getAnimations().map(function (a) {{ return a.finished; }}))
        .then(medir, medir);
    }}, 400);
  }}
  btn.addEventListener('click', function () {{
    root.dataset.theme = escuro() ? 'light' : 'dark';
    pintarBotao();
    depois();
  }});
  phone.addEventListener('load', sincronizar);
  pintarBotao();

  // ------------------- pagina atual (simula a navegacao; so cromo de QA)
  function trocarAtual(doc, a) {{
    doc.querySelectorAll('.al-sidebar .al-tab[aria-current]').forEach(function (x) {{
      x.removeAttribute('aria-current');
    }});
    a.setAttribute('aria-current', 'page');
  }}
  document.addEventListener('click', function (e) {{
    var a = e.target.closest && e.target.closest('.al-sidebar .al-tab, .al-sidebar__profile a');
    if (!a) return;
    e.preventDefault();
    if (a.classList.contains('al-tab')) {{
      trocarAtual(document, a);
      r('qa-current').textContent = a.textContent.trim();
    }} else {{
      document.querySelectorAll('.al-sidebar .al-tab[aria-current]').forEach(function (x) {{
        x.removeAttribute('aria-current');
      }});
      r('qa-current').textContent = 'Minha conta (nenhum item atual)';
    }}
  }});
  phone.addEventListener('load', function () {{
    var d = phone.contentDocument;
    if (!d) return;
    d.addEventListener('click', function (e) {{
      var a = e.target.closest && e.target.closest('.al-sidebar .al-tab, .al-sidebar__profile a');
      if (!a) return;
      e.preventDefault();
      if (a.classList.contains('al-tab')) {{
        trocarAtual(d, a);
        d.querySelector('.qa-where strong').textContent = a.textContent.trim();
      }}
    }});
  }});

  // ------------------------------------------------------------- contraste
  function rgb(str) {{
    var m = str && str.match(/rgba?\\(([^)]+)\\)/);
    if (!m) return null;
    var p = m[1].split(/[ ,\\/]+/).filter(Boolean).map(function (x) {{ return +x; }});
    return [p[0], p[1], p[2], p[3] === undefined ? 1 : p[3]];
  }}
  function lin(c) {{ c /= 255; return c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4); }}
  function lum(c) {{ return 0.2126 * lin(c[0]) + 0.7152 * lin(c[1]) + 0.0722 * lin(c[2]); }}
  function cr(a, b) {{
    var la = lum(a), lb = lum(b);
    return (Math.max(la, lb) + 0.05) / (Math.min(la, lb) + 0.05);
  }}
  function sobre(fg, base) {{
    var a = fg[3];
    return [0, 1, 2].map(function (i) {{ return Math.round(fg[i] * a + base[i] * (1 - a)); }}).concat([1]);
  }}
  function css(c) {{ return 'rgb(' + c.slice(0, 3).join(', ') + ')'; }}
  function cor(tokenVar) {{
    var t = document.createElement('div');
    t.style.cssText = 'position:absolute;visibility:hidden;background-color:var(' + tokenVar + ')';
    document.body.appendChild(t);
    var v = rgb(getComputedStyle(t).backgroundColor);
    t.remove();
    return v;
  }}
  function linha(where, what, fg, bg, piso, exc, modo) {{
    var v = cr(fg, bg);
    var distinto = css(fg) !== css(bg);
    var ok = modo === 'distinto' ? distinto : v >= piso;
    var classe = ok ? 'ok' : exc ? 'exc' : 'bad';
    var texto = ok ? (modo === 'distinto' ? 'diferente da Sidebar' : 'passa') : exc ? 'exceção declarada' : (modo === 'distinto' ? 'IGUAL À SIDEBAR' : 'REPROVA');
    var tr = document.createElement('tr');
    [where, what, css(fg), css(bg), v.toFixed(2) + ':1', modo === 'distinto' ? '≠' : piso.toFixed(1) + ':1'].forEach(function (x) {{
      var td = document.createElement('td'); td.textContent = x; tr.appendChild(td);
    }});
    var td = document.createElement('td');
    td.textContent = texto; td.className = 'qa-verdict qa-verdict--' + classe;
    tr.appendChild(td);
    r('measure-body').appendChild(tr);
  }}

  function medir() {{
    r('measure-body').textContent = '';
    var tema = escuro() ? 'escuro' : 'claro';
    var sb = r('sb');
    if (!sb) return;
    var cs = getComputedStyle(sb);
    var bg = rgb(cs.backgroundColor);
    var onde = 'Sidebar · ' + tema;
    linha(onde, 'nome', rgb(getComputedStyle(sb.querySelector('.al-sidebar__name')).color), bg, 4.5);
    linha(onde, 'e-mail', rgb(getComputedStyle(sb.querySelector('.al-sidebar__email')).color), bg, 4.5);
    linha(onde, 'rótulo de grupo', rgb(getComputedStyle(sb.querySelector('.al-sidebar__group-label')).color), bg, 4.5);
    var comum = sb.querySelector('.al-tab:not([aria-current]) .al-tab__label');
    linha(onde, 'item em repouso', rgb(getComputedStyle(comum).color), bg, 4.5);
    var atual = sb.querySelector('.al-tab[aria-current] .al-tab__label');
    if (atual) {{
      var ac = getComputedStyle(atual);
      linha(onde, 'item atual (texto)', rgb(ac.color), rgb(ac.backgroundColor), 4.5);
      linha(onde, 'item atual (fundo)', rgb(ac.backgroundColor), bg, 3, true);
    }}
    linha(onde, 'ícone do perfil', rgb(getComputedStyle(sb.querySelector('.al-sidebar__profile .al-icon')).color), bg, 3);
    linha(onde, 'hover do item', cor('--al-tab-bg-hover'), bg, 1, false, 'distinto');
    linha(onde, 'pressionado do item', cor('--al-tab-bg-active'), bg, 1, false, 'distinto');
    var borda = rgb(cs.borderInlineEndColor || cs.borderRightColor);
    linha(onde, 'borda', borda, bg, 3, true);
    linha(onde, 'borda × página em surface', borda, cor('--al-bg-surface'), 3, true);
    var scrim = cor('--al-bg-scrim');
    linha('Painel modal · ' + tema, 'painel × página escurecida', bg, sobre(scrim, cor('--al-bg-canvas')), 3, true);
    linha('Painel modal · ' + tema, 'borda × página escurecida', borda, sobre(scrim, cor('--al-bg-canvas')), 3, true);
  }}

  if (document.fonts && document.fonts.ready) {{
    document.fonts.ready.then(depois);
  }} else {{
    depois();
  }}
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function () {{
    pintarBotao(); depois();
  }});
}})();
</script>
</body>
</html>
'''


if __name__ == '__main__':
    html = build()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, 'w', encoding='utf-8').write(html)
    print(f'site/sidebar-qa.html escrito ({len(html)} bytes)')
    print(f'  CSS embutido: {", ".join(n for n, _ in CSS_FILES)}')
