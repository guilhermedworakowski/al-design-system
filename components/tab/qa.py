"""
Gera a visualizacao de QA do Tab (etapa 6) em site/tab-qa.html.

Mesmo arranjo dos outros componentes: a pagina INLINA os arquivos reais do
repositorio - foundation, tokens do Tab, tab.css e tab.js. Ela nao pode
divergir do codigo porque ela E o codigo.

O QUE A PAGINA MOSTRA

  - a matriz congelada: Line e Square x repouso/hover/pressed/foco, cada
    celula com uma aba nao selecionada e uma selecionada, sobre a tela E sobre
    a superficie. Os estados sao escritos direto no __label com os mesmos
    tokens que o seletor usa - "simulado", como no Card. As amostras sao
    `aria-hidden` + `inert`: nao existem para o teclado nem para o leitor;
  - abas de painel AO VIVO com o tab.js de verdade: Line automatica, Square
    manual (data-activation="manual"), e o aninhamento Line > Square
    (decisao I). Um painel tem um campo, para provar a regra 20;
  - navegacao com links: navbar Line e sidebar Square (regra 22);
  - o contraste lido do navegador, com getComputedStyle, depois da transicao.

O a11y.py ao lado le o HTML que este script emite e cobra ali o contrato de
marcacao.

Rodar: python3 qa.py     (escreve o proprio arquivo; nunca redirecionar stdout)
"""
import json
import os
import re
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(ROOT, 'site', 'tab-qa.html')

FOUND = json.load(open(os.path.join(ROOT, 'tokens.json')))
TAB = json.load(open(os.path.join(HERE, 'tokens.json')))

CSS_FILES = [
    ('foundation', os.path.join(ROOT, 'foundation', 'al-foundation.css')),
    ('tab - tokens', os.path.join(HERE, 'al-tab-tokens.css')),
    ('tab', os.path.join(HERE, 'tab.css')),
]
JS_FILE = os.path.join(HERE, 'tab.js')

TIPOS = [('line', 'Line', ''), ('square', 'Square', ' al-tabs--square')]
ESTADOS = [('repouso', 'Repouso'), ('hover', 'Hover'), ('pressed', 'Pressed'), ('foco', 'Foco')]


def congelado(tipo, sel, estado):
    """O que o seletor escreve naquele estado, escrito a mao no __label."""
    if estado == 'repouso':
        return ''
    if estado == 'foco':
        return 'box-shadow: var(--al-tab-ring)'
    if tipo == 'square' and sel:
        suf = 'hover' if estado == 'hover' else 'active'
        return (f'background-color: var(--al-tab-square-bg-selected-{suf}); '
                f'color: var(--al-tab-square-label-selected-{suf})')
    suf = 'hover' if estado == 'hover' else 'active'
    cor = 'line-label-selected' if sel else f'label-{suf}'
    return f'background-color: var(--al-tab-bg-{suf}); color: var(--al-tab-{cor})'


def amostra(tipo, mod, estado):
    abas = []
    for sel, rot in ((False, 'Itens'), (True, 'Resumo')):
        st = congelado(tipo, sel, estado)
        st = f' style="{st}"' if st else ''
        abas.append(f'<span class="al-tab" aria-selected="{"true" if sel else "false"}" '
                    f'data-type="{tipo}" data-state="{estado}">'
                    f'<span class="al-tab__label"{st}>{rot}</span></span>')
    return f'<div class="al-tabs{mod}" aria-hidden="true" inert>{"".join(abas)}</div>'


def matriz(pagina):
    cab = ''.join(f'<p class="qa-matrix__label">{n}</p>' for _, n in ESTADOS)
    linhas = [f'<div class="qa-matrix__row qa-matrix__row--head"><span></span>{cab}</div>']
    for tipo, nome, mod in TIPOS:
        cels = ''.join(f'<div class="qa-cell">{amostra(tipo, mod, e)}</div>' for e, _ in ESTADOS)
        linhas.append(f'<div class="qa-matrix__row"><p class="qa-matrix__label">{nome}</p>{cels}</div>')
    return ''.join(linhas)


def paginas():
    blocos = []
    for token, nome in (('bg-canvas', 'Tela'), ('bg-surface', 'Superfície')):
        blocos.append(f'''<div class="qa-page" style="background: var(--al-{token})" data-page="{token}">
        <p class="qa-page__name">{nome} <code>{token}</code></p>
        <div class="qa-matrix">{matriz(token)}</div>
      </div>''')
    return '\n      '.join(blocos)


def painel_grupo(gid, nome, abas, mod='', manual=False, corpo=None):
    """Grupo de abas de painel completo: tablist + paineis, cada painel
    comecando com titulo igual ao rotulo (regra 25)."""
    corpo = corpo or {}
    bt, pn = [], []
    for i, rot in enumerate(abas):
        slug = re.sub(r'[^a-z0-9]+', '-', unicodedata.normalize('NFKD', rot.lower()).encode('ascii', 'ignore').decode()).strip('-')
        tid, pid = f'{gid}-t-{slug}', f'{gid}-p-{slug}'
        on = i == 0
        ti = '' if on else ' tabindex="-1"'
        bt.append(f'<button class="al-tab" role="tab" type="button" id="{tid}" '
                  f'aria-selected="{"true" if on else "false"}" aria-controls="{pid}"'
                  f'{ti}><span class="al-tab__label">{rot}</span></button>')
        extra = corpo.get(rot, f'<p>Conteúdo de {rot.lower()}.</p>')
        pn.append(f'<div class="qa-tabpanel" role="tabpanel" id="{pid}" aria-labelledby="{tid}" '
                  f'tabindex="0"{"" if on else " hidden"}>\n          <h4 class="qa-panel-title">{rot}</h4>\n'
                  f'          {extra}\n        </div>')
    act = ' data-activation="manual"' if manual else ''
    return (f'<div class="al-tabs{mod}" role="tablist" aria-label="{nome}"{act}>\n        '
            + '\n        '.join(bt) + '\n      </div>\n      ' + '\n      '.join(pn))


def build():
    css_inline = '\n'.join(f'/* ================= {n} ================= */\n'
                           + open(p, encoding='utf-8').read() for n, p in CSS_FILES)
    # O cabecalho do tab.js mostra `<script src="tab.js"></script>` como exemplo
    # de uso: embutido cru, esse texto fecharia a tag <script> da pagina e o
    # comportamento nunca rodaria. `<\/` e o mesmo texto para o JS.
    js_inline = open(JS_FILE, encoding='utf-8').read().replace('</', '<\\/')

    pedido = painel_grupo('ped', 'Pedido #1042', ['Resumo', 'Itens', 'Entrega', 'Histórico'], corpo={
        'Resumo': '<p>3 itens · R$ 412,00 · pago no cartão.</p>',
        'Entrega': ('<p>Anote algo, troque de aba e volte: o texto continua aqui (regra 20).</p>\n'
                    '          <label class="qa-field">Observação para o entregador '
                    '<input type="text" id="obs-entrega" class="qa-input"></label>'),
    })
    relatorio = painel_grupo('rel', 'Relatório de vendas', ['Diário', 'Semanal', 'Mensal'],
                             mod=' al-tabs--square', manual=True, corpo={
        'Semanal': '<p>Com ativação manual, as setas só movem o foco: Enter ou Espaço abrem.</p>',
    })
    interno = painel_grupo('cli-dados', 'Dados do cliente', ['Pessoais', 'Endereço', 'Pagamento'],
                           mod=' al-tabs--square')
    aninhado = painel_grupo('cli', 'Cliente', ['Cadastro', 'Pedidos', 'Notas'], corpo={
        'Cadastro': interno,
    })

    navbar = '''<nav aria-label="Seções da conta">
        <ul class="al-tabs">
          <li><a class="al-tab" href="#perfil" aria-current="page"><span class="al-tab__label">Perfil</span></a></li>
          <li><a class="al-tab" href="#seguranca"><span class="al-tab__label">Segurança</span></a></li>
          <li><a class="al-tab" href="#faturas"><span class="al-tab__label">Faturas</span></a></li>
        </ul>
      </nav>'''
    sidebar = '''<nav aria-label="Configurações">
        <ul class="al-tabs al-tabs--square qa-stack">
          <li><a class="al-tab" href="#geral"><span class="al-tab__label">Geral</span></a></li>
          <li><a class="al-tab" href="#equipe" aria-current="page"><span class="al-tab__label">Equipe</span></a></li>
          <li><a class="al-tab" href="#integracoes"><span class="al-tab__label">Integrações</span></a></li>
          <li><a class="al-tab" href="#cobranca"><span class="al-tab__label">Cobrança</span></a></li>
        </ul>
      </nav>'''

    meta = TAB['meta']
    resumo = ''
    a11y_path = os.path.join(HERE, 'a11y.json')
    if os.path.exists(a11y_path):
        rs = json.load(open(a11y_path))['rows']
        resumo = (f' · portão: {len(rs)} combinações, {sum(r["pass"] for r in rs)} passam, '
                  f'{sum(bool(r["exception"]) for r in rs)} exceções, '
                  f'{sum((not r["pass"]) and not r["exception"] for r in rs)} reprovas')

    return f'''<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AL Tab QA</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap">
<style>
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
.qa-wrap {{
  max-width: 1120px; margin: 0 auto;
  padding-inline: var(--al-space-16);
  padding-block: var(--al-space-32) var(--al-space-64);
  display: flex; flex-direction: column; gap: var(--al-space-48);
}}
.qa-head {{
  display: flex; flex-wrap: wrap; align-items: flex-end;
  justify-content: space-between; gap: var(--al-space-16);
  border-bottom: 1px solid var(--al-border-subtle); padding-bottom: var(--al-space-16);
}}
.qa-head h1 {{
  margin: 0; font-size: var(--al-font-size-3xl); line-height: var(--al-line-height-3xl);
  font-weight: 600; letter-spacing: -0.02em; text-wrap: balance;
}}
.qa-sub {{ margin: var(--al-space-4) 0 0; color: var(--al-text-secondary); font-size: var(--al-font-size-sm); }}
.qa-btn {{
  display: inline-flex; align-items: center; gap: var(--al-space-8);
  padding: var(--al-space-8) var(--al-space-16);
  border: 1px solid var(--al-border-strong); border-radius: var(--al-radius-full);
  background: var(--al-bg-surface-raised); color: var(--al-text-primary);
  font: inherit; font-size: var(--al-font-size-sm); cursor: pointer;
}}
.qa-btn:focus-visible {{ outline: none; box-shadow: var(--al-focus-ring-default); }}
section > h2 {{
  margin: 0 0 var(--al-space-4);
  font-size: var(--al-font-size-xl); line-height: var(--al-line-height-xl);
  font-weight: 600; letter-spacing: -0.01em;
}}
section > p.qa-lede {{ margin: 0 0 var(--al-space-20); color: var(--al-text-secondary); max-width: 66ch; }}
.qa-tag {{
  font-size: var(--al-font-size-xs); line-height: var(--al-line-height-xs);
  padding: 2px var(--al-space-8); border-radius: var(--al-radius-full);
  border: 1px solid var(--al-border-default); color: var(--al-text-secondary);
  white-space: nowrap; vertical-align: middle; margin-left: var(--al-space-8);
  font-weight: 400; letter-spacing: 0;
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

/* ---- especificos do Tab ---- */
.qa-panel {{ padding: var(--al-space-24); border-radius: var(--al-radius-xl); background: var(--al-bg-surface); }}
.qa-panel--canvas {{ background: var(--al-bg-canvas); outline: 1px dashed var(--al-border-default); }}
.qa-pages {{ display: grid; gap: var(--al-space-20); }}
.qa-page {{ display: flex; flex-direction: column; gap: var(--al-space-16); padding: var(--al-space-24); border-radius: var(--al-radius-xl); outline: 1px dashed var(--al-border-default); overflow-x: auto; }}
.qa-page__name {{ margin: 0; font-size: var(--al-font-size-sm); font-weight: 600; }}
.qa-matrix {{ display: flex; flex-direction: column; gap: var(--al-space-20); }}
.qa-matrix__row {{ display: grid; gap: var(--al-space-20); grid-template-columns: 72px repeat(4, minmax(170px, 1fr)); align-items: end; }}
.qa-matrix__label {{ margin: 0; font-size: var(--al-font-size-xs); font-weight: 600; letter-spacing: 0.04em; text-transform: uppercase; color: var(--al-text-secondary); align-self: center; }}
.qa-cell {{ display: flex; min-width: 0; }}
.qa-live {{ display: grid; gap: var(--al-space-32); grid-template-columns: repeat(auto-fit, minmax(360px, 1fr)); }}
.qa-use {{ display: flex; flex-direction: column; gap: var(--al-space-12); min-width: 0; }}
.qa-use > h3 {{ margin: 0; font-size: var(--al-font-size-sm); font-weight: 600; letter-spacing: 0.04em; text-transform: uppercase; }}
.qa-tabpanel {{ padding-top: var(--al-space-16); }}
.qa-tabpanel:focus-visible {{ outline: none; box-shadow: var(--al-focus-ring-default); border-radius: var(--al-radius-md); }}
.qa-tabpanel p {{ margin: var(--al-space-4) 0 0; color: var(--al-text-secondary); }}
.qa-panel-title {{ margin: 0; font-size: var(--al-font-size-md); line-height: var(--al-line-height-md); font-weight: 600; }}
.qa-field {{ display: flex; flex-direction: column; gap: var(--al-space-4); margin-top: var(--al-space-12); font-size: var(--al-font-size-sm); color: var(--al-text-primary); }}
.qa-input {{ font: inherit; padding: var(--al-space-8) var(--al-space-12); border: 1px solid var(--al-border-strong); border-radius: var(--al-radius-md); background: var(--al-bg-canvas); color: var(--al-text-primary); }}
.qa-input:focus-visible {{ outline: none; box-shadow: var(--al-focus-ring-default); }}
.qa-stack {{ flex-direction: column; align-items: flex-start; }}
.qa-pagenote {{ margin: 0; color: var(--al-text-secondary); font-size: var(--al-font-size-xs); line-height: var(--al-line-height-xs); }}
.qa-sidebar {{ display: grid; grid-template-columns: 200px minmax(0, 1fr); gap: var(--al-space-24); }}
@media (max-width: 720px) {{
  .qa-sidebar {{ grid-template-columns: minmax(0, 1fr); }}
}}
</style>

<div class="qa-wrap">
  <header class="qa-head">
    <div>
      <h1>Tab — QA da etapa 6</h1>
      <p class="qa-sub">AL Design System {FOUND['meta']['version']} · componente {meta['version']} ·
      Line e Square × 4 estados × selecionada{resumo}</p>
    </div>
    <button type="button" class="qa-btn" id="theme-toggle" aria-pressed="false">
      <span id="theme-label">Tema claro</span>
    </button>
  </header>

  <section>
    <h2>O que testar</h2>
    <ol class="qa-checks">
      <li><strong>Tabule até o grupo “Pedido”.</strong> O Tab para <em>uma</em> vez no grupo, na aba selecionada. As setas ← → passam de aba e já abrem o painel; Home e End vão para a primeira e a última. Mais um Tab vai para o painel, não para a próxima aba.</li>
      <li><strong>Escreva na aba Entrega</strong>, vá para outra aba e volte: o texto continua lá (regra 20).</li>
      <li><strong>No grupo “Relatório” (Square, manual)</strong>, as setas só movem o foco; Enter ou Espaço abrem. Saia do grupo com Tab e volte: a entrada é de novo a aba aberta.</li>
      <li><strong>Clique na aba que já está aberta</strong>: nada acontece (regra 19).</li>
      <li><strong>Passe o ponteiro e segure o clique</strong>: a não selecionada escurece o rótulo; a Square selecionada vai para o laranja de hover e, apertada, para o mais escuro.</li>
      <li><strong>No aninhado “Cliente”</strong>, o primeiro nível é Line e o de dentro é Square (decisão I).</li>
      <li><strong>Na navegação</strong>, o Tab passa por todos os links e as setas não fazem nada: é lista de links, não grupo de abas (regra 22).</li>
      <li><strong>Troque o tema</strong> e confira a matriz nas duas páginas e a tabela de contraste no fim. No escuro, a Square selecionada em repouso se distingue pelo matiz (exceção <code>selecao-tonal</code>).</li>
      <li><strong>Com leitor de tela</strong> (VoiceOver: Ctrl+Opção+→): “Resumo, selecionada, aba 1 de 4” no painel; “Perfil, página atual, link” na navegação.</li>
      <li><strong>Ative o alto contraste</strong> (Windows) ou “Aumentar contraste” (macOS): a linha da selecionada fica na cor de destaque do sistema e a Square selecionada ganha contorno.</li>
    </ol>
  </section>

  <section>
    <h2>Painel, ao vivo <span class="qa-tag qa-tag--real">real</span></h2>
    <p class="qa-lede">Com o <code>tab.js</code> do componente. Cada painel começa com um título igual ao
    rótulo da aba (regra 25).</p>
    <div class="qa-live">
      <div class="qa-use">
        <h3>Line · ativação automática</h3>
        <div class="qa-panel qa-panel--canvas">
      {pedido}
        </div>
      </div>
      <div class="qa-use">
        <h3>Square · ativação manual</h3>
        <div class="qa-panel qa-panel--canvas">
      {relatorio}
        </div>
      </div>
      <div class="qa-use">
        <h3>Aninhado · Line &gt; Square</h3>
        <div class="qa-panel qa-panel--canvas">
      {aninhado}
        </div>
        <p class="qa-pagenote">No máximo dois níveis: Line fora, Square dentro (decisão I).</p>
      </div>
    </div>
  </section>

  <section>
    <h2>Navegação, ao vivo <span class="qa-tag qa-tag--real">real</span></h2>
    <p class="qa-lede">O mesmo visual, marcação de links: <code>&lt;nav&gt;</code> com nome e
    <code>aria-current="page"</code> no atual (regra 22). A sidebar empilha as abas por layout da página
    (decisão J: o item de largura cheia fica para o Tier 4) e fica sobre a superfície.</p>
    <div class="qa-live">
      <div class="qa-use">
        <h3>Navbar · Line</h3>
        <div class="qa-panel qa-panel--canvas">
      {navbar}
        </div>
      </div>
      <div class="qa-use">
        <h3>Sidebar · Square</h3>
        <div class="qa-panel">
      {sidebar}
        </div>
      </div>
    </div>
  </section>

  <section>
    <h2>Estados nas duas páginas <span class="qa-tag qa-tag--simulado">simulado</span></h2>
    <p class="qa-lede">Em cada célula, “Itens” é a não selecionada e “Resumo” a selecionada. Hover, pressed
    e foco foram escritos direto na caixa do rótulo, com os mesmos tokens que o seletor usa, para comparar
    lado a lado com o Figma.</p>
    <div class="qa-pages">
      {paginas()}
    </div>
  </section>

  <section>
    <h2>Contraste medido no navegador</h2>
    <p class="qa-lede">Não são os números do <code>tokens.json</code>: o script lê a cor que o navegador
    pintou — rótulo, linha e fundo da selecionada — contra o fundo efetivo, com
    <code>getComputedStyle</code>, depois da transição terminar.</p>
    <div class="qa-tablewrap">
      <table class="qa-measure">
        <thead><tr><th>onde</th><th>o quê</th><th>cor</th><th>fundo</th><th>medido</th><th>piso</th><th>veredito</th></tr></thead>
        <tbody id="measure-body"></tbody>
      </table>
    </div>
  </section>

  <p class="qa-foot">Gerado por <code>components/tab/qa.py</code> a partir do código commitado em
  <code>dev</code>. <code>al-foundation.css</code>, <code>al-tab-tokens.css</code>, <code>tab.css</code> e
  <code>tab.js</code> estão embutidos como estão no repositório.</p>
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
  function escuro() {{
    if (root.dataset.theme) return root.dataset.theme === 'dark';
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  }}
  function pintarBotao() {{
    var d = escuro();
    label.textContent = d ? 'Tema escuro' : 'Tema claro';
    btn.setAttribute('aria-pressed', String(d));
  }}
  btn.addEventListener('click', function () {{
    root.dataset.theme = escuro() ? 'light' : 'dark';
    pintarBotao();
    setTimeout(medir, 350);
  }});
  pintarBotao();

  // a navegacao de exemplo nao sai da pagina
  document.querySelectorAll('nav a.al-tab').forEach(function (a) {{
    a.addEventListener('click', function (e) {{
      e.preventDefault();
      a.closest('ul').querySelectorAll('a.al-tab').forEach(function (x) {{
        if (x === a) x.setAttribute('aria-current', 'page'); else x.removeAttribute('aria-current');
      }});
    }});
  }});

  // ------------------------------------------------------------- contraste
  function rgb(str) {{
    var m = str && str.match(/rgba?\\(([^)]+)\\)/);
    if (!m) return null;
    var p = m[1].split(',').map(function (x) {{ return +x.trim(); }});
    return [p[0], p[1], p[2], p[3] === undefined ? 1 : p[3]];
  }}
  function lin(c) {{ c /= 255; return c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4); }}
  function lum(c) {{ return 0.2126 * lin(c[0]) + 0.7152 * lin(c[1]) + 0.0722 * lin(c[2]); }}
  function cr(a, b) {{
    var la = lum(a), lb = lum(b);
    return (Math.max(la, lb) + 0.05) / (Math.min(la, lb) + 0.05);
  }}
  function fundo(el) {{
    for (var p = el; p; p = p.parentElement) {{
      var c = rgb(getComputedStyle(p).backgroundColor);
      if (c && c[3] > 0) return c;
    }}
    return rgb(getComputedStyle(document.body).backgroundColor) || [255, 255, 255, 1];
  }}
  function css(c) {{ return 'rgb(' + c.slice(0, 3).join(', ') + ')'; }}
  function linha(where, what, fg, bg, piso, exc) {{
    var v = cr(fg, bg);
    var classe = v >= piso ? 'ok' : exc ? 'exc' : 'bad';
    var texto = v >= piso ? 'passa' : exc ? 'exceção "' + exc + '"' : 'REPROVA';
    var tr = document.createElement('tr');
    [where, what, css(fg), css(bg), v.toFixed(2) + ':1', piso.toFixed(1) + ':1'].forEach(function (x) {{
      var td = document.createElement('td'); td.textContent = x; tr.appendChild(td);
    }});
    var td = document.createElement('td');
    td.textContent = texto; td.className = 'qa-verdict qa-verdict--' + classe;
    tr.appendChild(td);
    r('measure-body').appendChild(tr);
  }}

  function medir() {{
    r('measure-body').textContent = '';
    var dark = escuro();
    document.querySelectorAll('.qa-page .al-tab').forEach(function (tab) {{
      var page = tab.closest('.qa-page');
      var pg = rgb(getComputedStyle(page).backgroundColor);
      var lab = tab.querySelector('.al-tab__label');
      var sel = tab.getAttribute('aria-selected') === 'true';
      var tipo = tab.dataset.type, estado = tab.dataset.state;
      var where = (page.dataset.page === 'bg-canvas' ? 'Tela' : 'Superfície') + ' · '
        + (tipo === 'line' ? 'Line' : 'Square') + ' · ' + estado + (sel ? ' · selecionada' : '');
      var ls = getComputedStyle(lab);
      var bg = rgb(ls.backgroundColor);
      var efetivo = bg && bg[3] > 0 ? bg : pg;
      var excMarca = dark && tipo === 'square' && sel && estado === 'hover' ? 'marca-no-hover-escuro' : null;
      linha(where, 'rótulo', rgb(ls.color), efetivo, 4.5, excMarca);
      if (tipo === 'line' && estado === 'repouso') {{
        linha(where, 'linha', rgb(getComputedStyle(tab).borderBottomColor), pg, 3,
              sel ? null : 'trilho-decorativo');
      }}
      if (tipo === 'square' && sel) {{
        linha(where, 'fundo × página', bg, pg, 3,
              estado === 'repouso' || estado === 'foco' ? 'selecao-tonal'
              : estado === 'pressed' ? 'pressed-na-superficie-escura' : null);
      }}
    }});
  }}

  if (document.fonts && document.fonts.ready) {{
    document.fonts.ready.then(function () {{ setTimeout(medir, 350); }});
  }} else {{
    setTimeout(medir, 350);
  }}
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function () {{
    pintarBotao(); setTimeout(medir, 350);
  }});
}})();
</script>
'''


if __name__ == '__main__':
    html = build()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, 'w', encoding='utf-8').write(html)
    print(f'site/tab-qa.html escrito ({len(html)} bytes)')
    print(f'  CSS embutido: {", ".join(n for n, _ in CSS_FILES)} + tab.js')
    corpo = re.sub(r'<style\b[^>]*>.*?</style>', '', html, flags=re.S)
    corpo = re.sub(r'<script\b[^>]*>.*?</script>', '', corpo, flags=re.S)
    n = len(re.findall(r'class="al-tabs\b', corpo))
    print(f'  grupos de abas no documento: {n}')
