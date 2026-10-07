"""
Gera a visualizacao de QA do Accordion (etapa 6) em site/accordion-qa.html.

Mesmo arranjo dos outros componentes: a pagina INLINA os arquivos de CSS reais
do repositorio - foundation, Icon, tokens do Accordion e accordion.css. Ela nao
pode divergir do codigo porque ela E o codigo. O Accordion nao tem JS: o unico
script da pagina e o cromo (tema, registro de abertura, medicao).

O QUE A PAGINA MOSTRA

  - a matriz congelada: fechado/aberto x repouso/hover/pressed/foco. Hover,
    pressed e foco so existem sob ponteiro e teclado; aqui o fundo e o anel
    do <summary> foram escritos direto, com os MESMOS tokens que o seletor
    usa. Sao "simulado", como no Card e no Tab, e ficam `inert` +
    `aria-hidden` para nao virarem paradas de Tab falsas;
  - pilhas AO VIVO sobre `bg-surface`: varios abertos (padrao), exclusivo
    (`name=`), item sozinho e titulo longo;
  - o item sobre a tela como CONTRAEXEMPLO da regra 14;
  - o contraste lido do navegador, com getComputedStyle, depois da transicao.

O a11y.py ao lado le o HTML que este script emite e cobra ali o contrato de
marcacao.

Rodar: python3 qa.py     (escreve o proprio arquivo; nunca redirecionar stdout)
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(ROOT, 'site', 'accordion-qa.html')

FOUND = json.load(open(os.path.join(ROOT, 'tokens.json')))
ACC = json.load(open(os.path.join(HERE, 'tokens.json')))
ICON_DIR = os.path.join(ROOT, 'components', 'icon')

CSS_FILES = [
    ('foundation', os.path.join(ROOT, 'foundation', 'al-foundation.css')),
    ('icon - tokens', os.path.join(ICON_DIR, 'al-icon-tokens.css')),
    ('icon', os.path.join(ICON_DIR, 'icon.css')),
    ('accordion - tokens', os.path.join(HERE, 'al-accordion-tokens.css')),
    ('accordion', os.path.join(HERE, 'accordion.css')),
]


def svg(name, cls):
    src = open(os.path.join(ICON_DIR, 'icons', f'{name}.svg'), encoding='utf-8').read()
    path = re.search(r'<svg[^>]*>(.*?)</svg>', src, flags=re.S).group(1).strip()
    return (f'<svg class="al-icon {cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
            f'aria-hidden="true" focusable="false">{path}</svg>')


def item(titulo, corpo, aberto=False, icone=None, nome=None, head_style='', attrs=''):
    op = ' open' if aberto else ''
    nm = f' name="{nome}"' if nome else ''
    hs = f' style="{head_style}"' if head_style else ''
    ic = svg(icone, 'al-accordion__icon') if icone else ''
    paras = ''.join(f'<p class="qa-copy">{p}</p>' for p in corpo)
    return (f'<details class="al-accordion"{op}{nm}{attrs}>'
            f'<summary class="al-accordion__header"{hs}>{ic}'
            f'<span class="al-accordion__title">{titulo}</span>'
            f'{svg("chevron-down", "al-accordion__chevron")}</summary>'
            f'<div class="al-accordion__content">{paras}</div></details>')


CORPO = ['O reembolso cai no mesmo meio de pagamento da compra em até 7 dias úteis.']

# o que o seletor escreve, escrito a mao no <summary> - os mesmos tokens
CONGELADOS = [
    ('Repouso', ''),
    ('Hover', 'background-color: var(--al-accordion-bg-hover)'),
    ('Pressed', 'background-color: var(--al-accordion-bg-active)'),
    ('Foco', 'z-index: 1; background-color: var(--al-accordion-bg); box-shadow: var(--al-accordion-ring)'),
]


def matriz():
    """Linhas = estado, colunas = fechado/aberto. Quatro colunas apertavam o
    titulo em cinco linhas; duas deixam o item na largura de uso."""
    cab = ''.join(f'<p class="qa-matrix__label">{n}</p>' for n in ('Fechado', 'Aberto'))
    linhas = []
    for e, st in CONGELADOS:
        cels = ''.join(
            f'<div class="qa-cell" inert aria-hidden="true" data-state="{e.lower()}">'
            f'{item("Como funciona o reembolso?", CORPO, aberto, icone="house", head_style=st)}</div>'
            for aberto in (False, True))
        linhas.append(f'<div class="qa-matrix__row"><p class="qa-matrix__label">{e}</p>{cels}</div>')
    return f'<div class="qa-matrix__row qa-matrix__row--head"><span></span>{cab}</div>' + ''.join(linhas)


FAQ = [
    ('Como funciona o reembolso?', CORPO),
    ('Posso trocar o endereço depois da compra?',
     ['Sim, enquanto o pedido não sair para entrega. Depois disso, fale com o atendimento.']),
    ('Quais formas de pagamento são aceitas?',
     ['Cartão de crédito, Pix e boleto. O boleto leva até 2 dias úteis para compensar.']),
    ('Como cancelo minha assinatura?',
     ['Em Conta › Assinatura › Cancelar. O acesso continua até o fim do período pago.']),
]

PAGAMENTO = [
    ('Cartão de crédito', 'credit-card', ['Parcele em até 12 vezes sem juros acima de R$ 300.']),
    ('Pix', 'send', ['O pagamento é aprovado na hora e o pedido segue no mesmo dia.']),
    ('Boleto', 'file-text', ['Vence em 3 dias. O pedido só é separado depois da compensação.']),
]


def build():
    css = []
    for nome, path in CSS_FILES:
        css.append(f'/* ================= {nome} ================= */')
        css.append(open(path, encoding='utf-8').read())
    css_inline = '\n'.join(css)

    faq = '\n'.join(item(t, c) for t, c in FAQ)
    pag = '\n'.join(item(t, c, icone=i, nome='qa-pagamento', aberto=(k == 0))
                    for k, (t, i, c) in enumerate(PAGAMENTO))
    sozinho = item('Ver detalhes do pedido', ['Pedido #1042 · 3 itens · entregue em 3 de outubro.'])
    longo = item('O que acontece com os meus dados quando eu encerro a conta e peço a exclusão '
                 'definitiva de todo o histórico?',
                 ['Excluímos tudo em até 30 dias, exceto o que a lei manda guardar.'])
    contra = item('Como funciona o reembolso?', CORPO, attrs=' inert aria-hidden="true"')

    meta = ACC['meta']
    a11y_path = os.path.join(HERE, 'a11y.json')
    resumo = ''
    if os.path.exists(a11y_path):
        a = json.load(open(a11y_path))
        rs = a['rows']
        resumo = (f' · portão: {len(rs)} combinações, {sum(r["pass"] for r in rs)} passam, '
                  f'{sum(bool(r["exception"]) for r in rs)} exceções, '
                  f'{sum((not r["pass"]) and not r["exception"] for r in rs)} reprovas')

    return f'''<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AL Accordion QA</title>
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
  max-width: 1120px;
  margin: 0 auto;
  padding-inline: var(--al-space-16);
  padding-block: var(--al-space-32) var(--al-space-64);
  display: flex;
  flex-direction: column;
  gap: var(--al-space-48);
}}
.qa-head {{
  display: flex; flex-wrap: wrap; align-items: flex-end;
  justify-content: space-between; gap: var(--al-space-16);
  border-bottom: 1px solid var(--al-border-subtle);
  padding-bottom: var(--al-space-16);
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

/* ---- especificos do Accordion ---- */
.qa-panel {{
  padding: var(--al-space-24); border-radius: var(--al-radius-xl);
  background: var(--al-bg-surface);
}}
.qa-matrix {{ display: flex; flex-direction: column; gap: var(--al-space-20); }}
.qa-matrix__row {{ display: grid; gap: var(--al-space-16); grid-template-columns: 72px repeat(2, minmax(0, 1fr)); align-items: start; }}
.qa-matrix__label {{ margin: 0; font-size: var(--al-font-size-xs); font-weight: 600; letter-spacing: 0.04em; text-transform: uppercase; color: var(--al-text-secondary); }}
.qa-matrix__row:not(.qa-matrix__row--head) > .qa-matrix__label {{ padding-top: var(--al-space-24); }}
.qa-cell {{ min-width: 0; }}
.qa-copy {{ margin: 0; color: var(--al-text-secondary); }}
.qa-stack {{ display: flex; flex-direction: column; gap: var(--al-space-8); }}
.qa-uses {{ display: grid; gap: var(--al-space-32); grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); }}
.qa-use {{ display: flex; flex-direction: column; gap: var(--al-space-12); }}
.qa-use > h3 {{ margin: 0; font-size: var(--al-font-size-md); line-height: var(--al-line-height-md); font-weight: 600; }}
.qa-pagenote {{ margin: 0; color: var(--al-text-secondary); font-size: var(--al-font-size-xs); line-height: var(--al-line-height-xs); }}
.qa-pagenote--bad {{ color: var(--al-text-danger); }}
.qa-pages {{ display: grid; gap: var(--al-space-20); grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); }}
.qa-page {{ display: flex; flex-direction: column; gap: var(--al-space-16); padding: var(--al-space-24); border-radius: var(--al-radius-xl); outline: 1px dashed var(--al-border-default); }}
.qa-page__name {{ margin: 0; font-size: var(--al-font-size-sm); font-weight: 600; }}
.qa-log {{ margin: var(--al-space-12) 0 0; font-size: var(--al-font-size-sm); color: var(--al-text-secondary); min-height: var(--al-line-height-sm); }}
@media (max-width: 720px) {{
  .qa-matrix__row {{ grid-template-columns: minmax(0, 1fr); }}
  .qa-matrix__row--head {{ display: none; }}
  .qa-matrix__row:not(.qa-matrix__row--head) > .qa-matrix__label {{ padding-top: 0; }}
}}
</style>

<div class="qa-wrap">
  <header class="qa-head">
    <div>
      <h1>Accordion — QA da etapa 6</h1>
      <p class="qa-sub">AL Design System {FOUND['meta']['version']} · componente {meta['version']} ·
      fechado/aberto × 4 estados × 2 temas{resumo}</p>
    </div>
    <button type="button" class="qa-btn" id="theme-toggle" aria-pressed="false">
      <span id="theme-label">Tema claro</span>
    </button>
  </header>

  <section>
    <h2>O que testar</h2>
    <ol class="qa-checks">
      <li><strong>Tabule pela página.</strong> Cada cabeçalho é uma parada de Tab; o anel laranja envolve só o cabeçalho e aparece inteiro, inclusive embaixo, com o item aberto (regra 22). A matriz congelada não recebe foco.</li>
      <li><strong>Enter ou Espaço</strong> abre e fecha. O foco fica no cabeçalho e a página não rola (regra 23). A linha abaixo das pilhas diz o que abriu e fechou.</li>
      <li><strong>Passe o ponteiro e segure o clique</strong>: só o cabeçalho escurece; o conteúdo aberto nunca muda (regra 21).</li>
      <li><strong>Clique e depois passe o ponteiro de novo</strong>: depois de um clique de mouse, não aparece anel (foco só por teclado).</li>
      <li><strong>Na pilha de pagamento</strong>, abrir um item fecha o outro (exclusivo, <code>name=</code>). Na de perguntas, vários ficam abertos (regra 8).</li>
      <li><strong>Troque o tema</strong> e repita o hover: no escuro o cabeçalho agora clareia em relação ao item (decisão G). Confira a tabela de contraste no fim.</li>
      <li><strong>Ctrl+F por “compensação”</strong> com a pilha de pagamento fechada: no Chrome/Edge o item abre sozinho; nos outros ainda não (regra 26).</li>
      <li><strong>Com leitor de tela</strong> (VoiceOver: Ctrl+Opção+→): ele anuncia o título, “recolhido/expandido” e nada sobre os ícones.</li>
      <li><strong>Ative o alto contraste</strong> (Windows) ou “Aumentar contraste” (macOS): cada item ganha contorno e continua visível (regra 27).</li>
    </ol>
  </section>

  <section>
    <h2>Estados congelados <span class="qa-tag qa-tag--simulado">simulado</span></h2>
    <p class="qa-lede">Hover, pressed e foco só existem sob o ponteiro e o teclado. Aqui o fundo e o anel
    do <code>&lt;summary&gt;</code> foram escritos direto, com os mesmos tokens que o seletor usa, para
    comparar lado a lado com o Figma. Sobre <code>bg-surface</code>, onde o Accordion pode ficar (regra 14).</p>
    <div class="qa-panel"><div class="qa-matrix" id="matrix-frozen">{matriz()}</div></div>
  </section>

  <section>
    <h2>Ao vivo <span class="qa-tag qa-tag--real">real</span></h2>
    <p class="qa-lede">Marcação nativa, sem JS do componente. Cada pilha tem um título de verdade antes
    dela (regra 25); o título do item é visual.</p>
    <div class="qa-panel">
      <div class="qa-uses">
        <div class="qa-use">
          <h3>Perguntas frequentes</h3>
          <div class="qa-stack">
{faq}
          </div>
          <p class="qa-pagenote">Padrão: vários abertos, todos fechados ao carregar (regras 8 e 9).</p>
        </div>
        <div class="qa-use">
          <h3>Forma de pagamento</h3>
          <div class="qa-stack">
{pag}
          </div>
          <p class="qa-pagenote">Exclusivo com <code>name=</code>: as opções são alternativas.
          Ícone em todos os itens da pilha (regra 18). O primeiro começa aberto.</p>
        </div>
        <div class="qa-use">
          <h3>Item sozinho</h3>
          {sozinho}
          <p class="qa-pagenote">Válido: “ver detalhes” (regra 6).</p>
        </div>
        <div class="qa-use">
          <h3>Título longo</h3>
          {longo}
          <p class="qa-pagenote">Quebra em linhas, sem reticências; chevron alinhado à primeira linha (regra 12).</p>
        </div>
      </div>
      <p class="qa-log" id="qa-log" role="status" aria-live="polite"></p>
    </div>
  </section>

  <section>
    <h2>Onde ele pode ficar <span class="qa-tag qa-tag--real">real</span></h2>
    <p class="qa-lede">O mesmo item sobre superfície e sobre a tela. Na tela clara o item fica 1,00:1 e
    some — por isso a regra 14.</p>
    <div class="qa-pages">
      <div class="qa-page" style="background: var(--al-bg-surface)">
        <p class="qa-page__name">Superfície <code>bg-surface</code></p>
        {item("Como funciona o reembolso?", CORPO, attrs=' inert aria-hidden="true"')}
        <p class="qa-pagenote">Onde ele mora.</p>
      </div>
      <div class="qa-page" style="background: var(--al-bg-canvas)">
        <p class="qa-page__name">Tela <code>bg-canvas</code></p>
        {contra}
        <p class="qa-pagenote qa-pagenote--bad">Contraexemplo: direto na tela, o item some no claro (regra 14).</p>
      </div>
    </div>
  </section>

  <section>
    <h2>Contraste medido no navegador</h2>
    <p class="qa-lede">Não são os números do <code>tokens.json</code>: o script lê a cor que o navegador
    pintou — título, divisória e fundo — na matriz congelada, contra o fundo efetivo, com
    <code>getComputedStyle</code>, depois da transição terminar.</p>
    <div class="qa-tablewrap">
      <table class="qa-measure">
        <thead><tr><th>onde</th><th>o quê</th><th>cor</th><th>fundo</th><th>medido</th><th>piso</th><th>veredito</th></tr></thead>
        <tbody id="measure-body"></tbody>
      </table>
    </div>
  </section>

  <p class="qa-foot">Gerado por <code>components/accordion/qa.py</code> a partir do CSS commitado em
  <code>dev</code>. <code>al-foundation.css</code>, <code>al-icon-tokens.css</code>, <code>icon.css</code>,
  <code>al-accordion-tokens.css</code> e <code>accordion.css</code> estão embutidos como estão no repositório.</p>
</div>

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
  // mede so depois que toda transicao terminou: com o painel em segundo plano
  // o navegador segura a animacao, e um setTimeout fixo lia a cor no meio
  function depois() {{
    setTimeout(function () {{
      Promise.all(document.getAnimations().map(function (a) {{ return a.finished; }}))
        .then(medir, medir);
    }}, 50);
  }}
  btn.addEventListener('click', function () {{
    root.dataset.theme = escuro() ? 'light' : 'dark';
    pintarBotao();
    depois();
  }});
  pintarBotao();

  // ------------------------------------------- registro (so cromo de QA)
  var log = r('qa-log');
  document.querySelectorAll('.qa-use .al-accordion').forEach(function (d) {{
    d.addEventListener('toggle', function () {{
      var t = d.querySelector('.al-accordion__title').textContent.trim();
      log.textContent = (d.open ? 'Abriu: ' : 'Fechou: ') + t;
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
    for (var p = el.parentElement; p; p = p.parentElement) {{
      var c = rgb(getComputedStyle(p).backgroundColor);
      if (c && c[3] > 0) return c;
    }}
    return rgb(getComputedStyle(document.body).backgroundColor) || [255, 255, 255, 1];
  }}
  function css(c) {{ return 'rgb(' + c.slice(0, 3).join(', ') + ')'; }}
  function linha(where, what, fg, bg, piso, exc) {{
    var v = cr(fg, bg);
    var classe = v >= piso ? 'ok' : exc ? 'exc' : 'bad';
    var texto = v >= piso ? 'passa' : exc ? 'exceção declarada' : 'REPROVA';
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
    document.querySelectorAll('#matrix-frozen .qa-cell').forEach(function (cell) {{
      var d = cell.querySelector('.al-accordion');
      var head = d.querySelector('.al-accordion__header');
      var where = (d.open ? 'Aberto' : 'Fechado') + ' · ' + cell.dataset.state;
      var hb = rgb(getComputedStyle(head).backgroundColor);
      var db = rgb(getComputedStyle(d).backgroundColor);
      linha(where, 'título', rgb(getComputedStyle(head.querySelector('.al-accordion__title')).color), hb, 4.5);
      linha(where, 'chevron', rgb(getComputedStyle(head.querySelector('.al-accordion__chevron')).color), hb, 3);
      if (d.open) {{
        var line = rgb(getComputedStyle(d.querySelector('.al-accordion__content')).borderTopColor);
        var a = cr(line, hb), b = cr(line, db);
        linha(where, 'divisória', line, a < b ? hb : db, 3, true);
      }}
      if (cell.dataset.state === 'repouso') linha(where, 'item × página', db, fundo(d), 3, true);
    }});
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
'''


if __name__ == '__main__':
    html = build()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, 'w', encoding='utf-8').write(html)
    print(f'site/accordion-qa.html escrito ({len(html)} bytes)')
    print(f'  CSS embutido: {", ".join(n for n, _ in CSS_FILES)}')
    corpo = re.sub(r'<style\b[^>]*>.*?</style>', '', html, flags=re.S)
    corpo = re.sub(r'<script\b[^>]*>.*?</script>', '', corpo, flags=re.S)
    n = len(re.findall(r'class="al-accordion"', corpo))
    print(f'  accordions de verdade no documento: {n}')
