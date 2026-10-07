"""
Gera a visualizacao de QA do Card (etapa 6) em site/card-qa.html.

Mesmo arranjo dos outros componentes: a pagina INLINA os arquivos de CSS reais
do repositorio - foundation, tokens do Card, card.css, e o Icon (para a seta
recomendada da regra 14). Ela nao pode divergir do codigo porque ela E o codigo.

O QUE A PAGINA MOSTRA

  - a matriz estatica: 3 tipos x 3 paddings;
  - o card clicavel AO VIVO, para tabular, passar o ponteiro e apertar Enter;
  - os estados congelados (hover e foco), escritos direto nas camadas internas
    `--_edge`, `--_ring` e `--_lift` - as mesmas que o seletor escreve. Sao
    "simulado", como o hover do Input;
  - os tres tipos nas duas paginas do sistema, com o Filled sobre a tela como
    CONTRAEXEMPLO da regra 2;
  - usos reais tirados das regras de uso;
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
OUT = os.path.join(ROOT, 'site', 'card-qa.html')

FOUND = json.load(open(os.path.join(ROOT, 'tokens.json')))
CARD = json.load(open(os.path.join(HERE, 'tokens.json')))
ICON_DIR = os.path.join(ROOT, 'components', 'icon')

CSS_FILES = [
    ('foundation', os.path.join(ROOT, 'foundation', 'al-foundation.css')),
    ('icon - tokens', os.path.join(ICON_DIR, 'al-icon-tokens.css')),
    ('icon', os.path.join(ICON_DIR, 'icon.css')),
    ('card - tokens', os.path.join(HERE, 'al-card-tokens.css')),
    ('card', os.path.join(HERE, 'card.css')),
]

TIPOS = [('filled', 'Filled', ''), ('border', 'Border', ' al-card--border'),
         ('elevated', 'Elevated', ' al-card--elevated')]
PADDINGS = [('spaced', 'Spaced · 24', ' al-card--spaced'), ('default', 'Default · 16', ''),
            ('tight', 'Tight · 8', ' al-card--tight')]


def chevron():
    """A seta da regra 14: o chevron-right do Icon, decorativo."""
    svg = open(os.path.join(ICON_DIR, 'icons', 'chevron-right.svg'), encoding='utf-8').read()
    path = re.search(r'<svg[^>]*>(.*?)</svg>', svg, flags=re.S).group(1).strip()
    return (f'<svg class="al-icon al-icon--20 qa-chevron" viewBox="0 0 24 24" fill="none" '
            f'stroke="currentColor" stroke-width="2" stroke-linecap="round" '
            f'stroke-linejoin="round" aria-hidden="true" focusable="false">{path}</svg>')


def header(titulo, desc, h='h3', link=None):
    t = f'<a class="al-card__link" href="#{link}">{titulo}</a>' if link else titulo
    d = f'\n        <p class="al-card__description">{desc}</p>' if desc else ''
    return f'''<div class="al-card__header">
        <{h} class="al-card__title">{t}</{h}>{d}
      </div>'''


def static(mods, titulo='Pedido #1042', desc='Entregue em 3 de outubro.', tag='div', extra=''):
    return f'<{tag} class="al-card{mods}">\n      {header(titulo, desc)}{extra}\n    </{tag}>'


def clickable(mods, titulo, desc, slug, tag='div', style='', seta=True):
    st = f' style="{style}"' if style else ''
    corpo = header(titulo, desc, link=slug)
    if seta:
        corpo = f'<div class="qa-cardrow">\n      {corpo}\n      {chevron()}\n    </div>'
    return f'<{tag} class="al-card{mods} al-card--clickable"{st}>\n    {corpo}\n  </{tag}>'


def matriz():
    linhas = []
    for _, nome, mod in TIPOS:
        cels = ''.join(f'<div class="qa-cell">{static(mod + pmod)}</div>' for _, _, pmod in PADDINGS)
        linhas.append(f'<div class="qa-matrix__row"><p class="qa-matrix__label">{nome}</p>{cels}</div>')
    cab = ''.join(f'<p class="qa-matrix__label">{p}</p>' for _, p, _ in PADDINGS)
    return f'<div class="qa-matrix__row qa-matrix__row--head"><span></span>{cab}</div>' + ''.join(linhas)


# estados congelados: o que o seletor escreve, escrito a mao nas mesmas camadas
EDGE = '0 0 0 var(--al-card-border-width) var(--al-card-{})'
CONGELADOS = {
    'filled': {
        'hover': '--_lift: var(--al-card-filled-shadow-hover)',
        'foco': '--_ring: var(--al-card-ring)',
    },
    'border': {
        'hover': f'--_edge: {EDGE.format("border-hover")}',
        'foco': f'--_edge: {EDGE.format("border-focus")}; --_ring: var(--al-card-ring)',
    },
    'elevated': {
        'hover': '--_lift: var(--al-card-elevated-shadow-hover)',
        'foco': '--_ring: var(--al-card-ring)',
    },
}


def congelados():
    linhas = []
    for slug, nome, mod in TIPOS:
        cels = [f'<div class="qa-cell">{static(mod)}</div>']
        for estado in ('hover', 'foco'):
            st = CONGELADOS[slug][estado]
            cels.append(f'<div class="qa-cell"><div class="al-card{mod}" style="{st}">\n      '
                        f'{header("Pedido #1042", "Entregue em 3 de outubro.")}\n    </div></div>')
        linhas.append(f'<div class="qa-matrix__row"><p class="qa-matrix__label">{nome}</p>{"".join(cels)}</div>')
    cab = ''.join(f'<p class="qa-matrix__label">{e}</p>' for e in ('Repouso', 'Hover', 'Foco'))
    return f'<div class="qa-matrix__row qa-matrix__row--head"><span></span>{cab}</div>' + ''.join(linhas)


def paginas():
    blocos = []
    for token, nome in (('bg-canvas', 'Tela'), ('bg-surface', 'Superfície')):
        cards = []
        for slug, tnome, mod in TIPOS:
            proibido = slug == 'filled' and token == 'bg-canvas'
            nota = ('<p class="qa-pagenote qa-pagenote--bad">Contraexemplo: Filled direto na tela '
                    'some (regra 2).</p>' if proibido else f'<p class="qa-pagenote">{tnome}</p>')
            cards.append(f'<div class="qa-cell">{static(mod)}{nota}</div>')
        blocos.append(f'''<div class="qa-page" style="background: var(--al-{token})" data-page="{token}">
        <p class="qa-page__name">{nome} <code>{token}</code></p>
        <div class="qa-page__cards">{"".join(cards)}</div>
      </div>''')
    return '\n      '.join(blocos)


ATALHOS = [
    ('Pedidos', 'Acompanhe entregas e devoluções.', 'pedidos'),
    ('Clientes', 'Cadastro, histórico e contatos.', 'clientes'),
    ('Relatórios', 'Vendas por período e por canal.', 'relatorios'),
]


def build():
    css = []
    for nome, path in CSS_FILES:
        css.append(f'/* ================= {nome} ================= */')
        css.append(open(path, encoding='utf-8').read())
    css_inline = '\n'.join(css)

    vivos = '\n'.join(
        f'<div class="qa-cell">{clickable(mod, f"Pedido #10{42 + i}", "Entregue em 3 de outubro.", f"pedido-{slug}")}'
        f'<p class="qa-pagenote">{nome}</p></div>'
        for i, (slug, nome, mod) in enumerate(TIPOS))

    atalhos = '\n'.join(clickable(' al-card--border', t, d, s, tag='li') for t, d, s in ATALHOS)

    acoes = '''
      <div class="qa-actions">
        <button type="button" class="qa-btn">Ver detalhes</button>
        <button type="button" class="qa-btn qa-btn--primary">Assinar</button>
      </div>'''

    feed = '\n'.join(
        f'<li><article class="al-card al-card--border">\n      {header(t, d)}\n    </article></li>'
        for t, d in (('Nova política de frete', 'A partir de 1º de novembro, frete grátis acima de R$ 199.'),
                     ('Manutenção programada', 'O painel fica fora do ar no domingo, das 2h às 4h.')))

    metricas = '\n'.join(
        f'<li class="al-card al-card--tight">\n      {header(t, d, h="h4")}\n    </li>'
        for t, d in (('128', 'pedidos hoje'), ('R$ 24 mil', 'faturados'), ('3', 'devoluções')))

    meta = CARD['meta']
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
<title>AL Card QA</title>
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
.qa-btn--primary {{ background: var(--al-bg-brand); border-color: var(--al-bg-brand); color: var(--al-text-on-brand); }}
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

/* ---- especificos do Card ---- */
.qa-panel {{
  padding: var(--al-space-24); border-radius: var(--al-radius-xl);
  background: var(--al-bg-surface);
}}
.qa-matrix {{ display: flex; flex-direction: column; gap: var(--al-space-20); }}
.qa-matrix__row {{ display: grid; gap: var(--al-space-20); grid-template-columns: 88px repeat(3, minmax(0, 1fr)); align-items: start; }}
.qa-matrix__label {{ margin: 0; font-size: var(--al-font-size-xs); font-weight: 600; letter-spacing: 0.04em; text-transform: uppercase; color: var(--al-text-secondary); }}
.qa-matrix__row:not(.qa-matrix__row--head) > .qa-matrix__label {{ padding-top: var(--al-space-8); }}
.qa-cell {{ display: flex; flex-direction: column; gap: var(--al-space-8); min-width: 0; }}
.qa-cards {{ display: grid; gap: var(--al-space-20); grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); }}
.qa-cardrow {{ display: flex; align-items: flex-start; justify-content: space-between; gap: var(--al-space-12); }}
.qa-chevron {{ flex-shrink: 0; margin-top: var(--al-space-4); color: var(--al-text-secondary); }}
.qa-pages {{ display: grid; gap: var(--al-space-20); grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); }}
.qa-page {{ display: flex; flex-direction: column; gap: var(--al-space-16); padding: var(--al-space-24); border-radius: var(--al-radius-xl); outline: 1px dashed var(--al-border-default); }}
.qa-page__name {{ margin: 0; font-size: var(--al-font-size-sm); font-weight: 600; }}
.qa-page__cards {{ display: flex; flex-direction: column; gap: var(--al-space-16); }}
.qa-pagenote {{ margin: 0; color: var(--al-text-secondary); font-size: var(--al-font-size-xs); line-height: var(--al-line-height-xs); }}
.qa-pagenote--bad {{ color: var(--al-text-danger); }}
.qa-uses {{ display: grid; gap: var(--al-space-32); grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); }}
.qa-use {{ display: flex; flex-direction: column; gap: var(--al-space-12); }}
.qa-use > h3 {{ margin: 0; font-size: var(--al-font-size-sm); font-weight: 600; letter-spacing: 0.04em; text-transform: uppercase; }}
.qa-list {{ list-style: none; margin: 0; padding: 0; display: grid; gap: var(--al-space-16); }}
.qa-list--3 {{ grid-template-columns: repeat(3, minmax(0, 1fr)); gap: var(--al-space-8); }}
.qa-actions {{ display: flex; gap: var(--al-space-8); justify-content: flex-end; flex-wrap: wrap; }}
.qa-log {{ margin: var(--al-space-12) 0 0; font-size: var(--al-font-size-sm); color: var(--al-text-secondary); min-height: var(--al-line-height-sm); }}
@media (max-width: 720px) {{
  .qa-matrix__row {{ grid-template-columns: minmax(0, 1fr); }}
  .qa-matrix__row--head {{ display: none; }}
  .qa-list--3 {{ grid-template-columns: minmax(0, 1fr); }}
}}
</style>

<div class="qa-wrap">
  <header class="qa-head">
    <div>
      <h1>Card — QA da etapa 6</h1>
      <p class="qa-sub">AL Design System {FOUND['meta']['version']} · componente {meta['version']} ·
      3 tipos × 3 paddings × estático/clicável{resumo}</p>
    </div>
    <button type="button" class="qa-btn" id="theme-toggle" aria-pressed="false">
      <span id="theme-label">Tema claro</span>
    </button>
  </header>

  <section>
    <h2>O que testar</h2>
    <ol class="qa-checks">
      <li><strong>Tabule pela página.</strong> Cada card clicável é <em>uma</em> parada de Tab, e o anel laranja envolve o card inteiro, não só o título (regra 17). Os cards estáticos nunca recebem foco.</li>
      <li><strong>Aperte Enter num card focado</strong> ou clique em qualquer ponto dele (não só no título): a linha abaixo dos cards ao vivo diz qual abriu.</li>
      <li><strong>Passe o ponteiro</strong> nos cards ao vivo: Filled ganha sombra, Border escurece a borda (não fica laranja), Elevated sobe a sombra.</li>
      <li><strong>Tabule até o Elevated ao vivo</strong>: o anel aparece e a sombra continua (decisão D). No Figma ela some; aqui não pode sumir.</li>
      <li><strong>Troque o tema</strong>: no escuro o card clareia em relação à página, e é isso que o separa, não a sombra (regra 23). Confira as duas páginas e a tabela de contraste no fim.</li>
      <li><strong>Tente selecionar o texto de um card clicável</strong>: não dá. É o custo aceito do link esticado (regra 16) — o texto dos cards estáticos seleciona normalmente.</li>
      <li><strong>Com leitor de tela</strong> (VoiceOver: Ctrl+Opção+→), percorra os atalhos: ele diz “lista, 3 itens” e anuncia só o título como link, não o card inteiro.</li>
      <li><strong>Ative o alto contraste</strong> (Windows) ou “Aumentar contraste” (macOS): os três tipos ganham contorno e continuam visíveis.</li>
    </ol>
  </section>

  <section>
    <h2>Matriz estática <span class="qa-tag qa-tag--real">real</span></h2>
    <p class="qa-lede">Os três tipos nos três paddings, sobre <code>bg-surface</code> — onde o Filled pode
    ficar (regra 2). Repare que as três colunas medem igual em qualquer tipo: a borda do Border é
    desenhada fora da caixa (decisão F).</p>
    <div class="qa-panel"><div class="qa-matrix" id="matrix-static">{matriz()}</div></div>
  </section>

  <section>
    <h2>Clicável, ao vivo <span class="qa-tag qa-tag--real">real</span></h2>
    <p class="qa-lede">Tabule, passe o ponteiro e aperte Enter. O link é o título, esticado sobre o card;
    a seta à direita é a pista recomendada pela regra 14 (no toque não existe hover).</p>
    <div class="qa-panel">
      <div class="qa-cards">{vivos}</div>
      <p class="qa-log" id="qa-log" role="status" aria-live="polite"></p>
    </div>
  </section>

  <section>
    <h2>Estados congelados <span class="qa-tag qa-tag--simulado">simulado</span></h2>
    <p class="qa-lede">Hover e foco só existem sob o ponteiro e o teclado. Aqui as camadas internas do
    card (<code>--_edge</code>, <code>--_ring</code>, <code>--_lift</code>) foram escritas direto — as
    mesmas que o seletor escreve — para comparar lado a lado com o Figma.</p>
    <div class="qa-panel"><div class="qa-matrix">{congelados()}</div></div>
  </section>

  <section>
    <h2>Nas duas páginas <span class="qa-tag qa-tag--real">real</span></h2>
    <p class="qa-lede">O mesmo card sobre a tela e sobre superfície. Na tela clara o Filled fica 1,00:1 e
    some — por isso a regra 2. Border e Elevated funcionam nas duas.</p>
    <div class="qa-pages">
      {paginas()}
    </div>
  </section>

  <section>
    <h2>Usos reais</h2>
    <p class="qa-lede">Tirados das regras de uso, cada um com a marcação que a regra pede.</p>
    <div class="qa-uses">
      <div class="qa-use">
        <h3>Grade de atalhos</h3>
        <ul class="qa-list">
{atalhos}
        </ul>
        <p class="qa-pagenote">Border clicável sobre a tela (regra 3), em <code>&lt;ul&gt;</code> (regra 22),
        uma ação por card (regra 13), seta recomendada (regra 14).</p>
      </div>

      <div class="qa-use">
        <h3>Card com ações</h3>
        <div class="qa-panel">
          {static(' al-card--elevated al-card--spaced', 'Plano Pro', 'Cobrança mensal, cancele quando quiser.', extra=acoes)}
        </div>
        <p class="qa-pagenote">Mais de uma ação: o card é estático e as ações são botões no fim,
        uma primária (regras 12 e 13). Spaced: card isolado, de destaque (regra 8).</p>
      </div>

      <div class="qa-use">
        <h3>Avisos</h3>
        <ul class="qa-list">
{feed}
        </ul>
        <p class="qa-pagenote">Conteúdo autossuficiente: <code>&lt;article&gt;</code> dentro de
        <code>&lt;li&gt;</code> (regra 22). Estático: o texto seleciona.</p>
      </div>

      <div class="qa-use">
        <h3>Painel denso</h3>
        <div class="qa-panel">
          <ul class="qa-list qa-list--3">
{metricas}
          </ul>
        </div>
        <p class="qa-pagenote">Tight para cards pequenos e densos (regra 8), Filled sobre
        <code>bg-surface</code> (regra 2), mesmo tipo e padding na grade (regra 5).</p>
      </div>
    </div>
  </section>

  <section>
    <h2>Contraste medido no navegador</h2>
    <p class="qa-lede">Não são os números do <code>tokens.json</code>: o script lê a cor que o navegador
    pintou — o texto, a borda (primeira camada do <code>box-shadow</code>) e o fundo do card — contra o
    fundo efetivo, com <code>getComputedStyle</code>, depois da transição terminar.</p>
    <div class="qa-tablewrap">
      <table class="qa-measure">
        <thead><tr><th>onde</th><th>o quê</th><th>cor</th><th>fundo</th><th>medido</th><th>piso</th><th>veredito</th></tr></thead>
        <tbody id="measure-body"></tbody>
      </table>
    </div>
  </section>

  <p class="qa-foot">Gerado por <code>components/card/qa.py</code> a partir do CSS commitado em
  <code>dev</code>. <code>al-foundation.css</code>, <code>al-icon-tokens.css</code>, <code>icon.css</code>,
  <code>al-card-tokens.css</code> e <code>card.css</code> estão embutidos como estão no repositório.</p>
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
  btn.addEventListener('click', function () {{
    root.dataset.theme = escuro() ? 'light' : 'dark';
    pintarBotao();
    setTimeout(medir, 350);
  }});
  pintarBotao();

  // ------------------------------------------------- ativacao dos cards
  var log = r('qa-log');
  document.querySelectorAll('.al-card__link').forEach(function (a) {{
    a.addEventListener('click', function (e) {{
      e.preventDefault();
      log.textContent = 'Abriu: ' + a.textContent.trim() + ' (' + a.getAttribute('href') + ')';
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
  function tipo(el) {{
    return el.classList.contains('al-card--border') ? 'Border'
         : el.classList.contains('al-card--elevated') ? 'Elevated' : 'Filled';
  }}
  function onde(el) {{
    var s = el.closest('section');
    return (s ? s.querySelector('h2').firstChild.textContent.trim() : '—') + ' · ' + tipo(el);
  }}
  function css(c) {{ return 'rgb(' + c.slice(0, 3).join(', ') + ')'; }}
  function linha(where, what, fg, bg, piso, exc, invisivel) {{
    var v = cr(fg, bg);
    var classe = invisivel ? 'bad' : v >= piso ? 'ok' : exc ? 'exc' : 'bad';
    var texto = invisivel ? 'INVISÍVEL (contraexemplo da regra 2)' : v >= piso ? 'passa' : exc ? 'exceção declarada' : 'REPROVA';
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
    // so a matriz, as duas paginas e os ao vivo: o resto repete as mesmas cores
    document.querySelectorAll('#matrix-static .al-card, .qa-page .al-card, .qa-cards .al-card').forEach(function (el) {{
      var cs = getComputedStyle(el);
      var bg = rgb(cs.backgroundColor);
      var pg = fundo(el);
      var where = onde(el);
      var title = el.querySelector('.al-card__title');
      if (title) linha(where, 'título', rgb(getComputedStyle(title).color), bg, 4.5);
      var desc = el.querySelector('.al-card__description');
      if (desc) linha(where, 'descrição', rgb(getComputedStyle(desc).color), bg, 4.5);
      var edge = rgb(cs.boxShadow);
      var temBorda = edge && edge[3] > 0;
      var temSombra = el.classList.contains('al-card--elevated');
      if (temBorda) {{
        linha(where, 'borda × card', edge, bg, 3, true);
        linha(where, 'borda × página', edge, pg, 3, true);
      }} else {{
        var igual = bg[0] === pg[0] && bg[1] === pg[1] && bg[2] === pg[2];
        linha(where, 'fundo × página', bg, pg, 3, true, igual && !temSombra);
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
    print(f'site/card-qa.html escrito ({len(html)} bytes)')
    print(f'  CSS embutido: {", ".join(n for n, _ in CSS_FILES)}')
    corpo = re.sub(r'<style\b[^>]*>.*?</style>', '', html, flags=re.S)
    corpo = re.sub(r'<script\b[^>]*>.*?</script>', '', corpo, flags=re.S)
    n = len(re.findall(r'class="al-card\b(?!__)', corpo))
    print(f'  cards de verdade no documento: {n}')
