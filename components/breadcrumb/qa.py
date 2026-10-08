"""
Gera a visualizacao de QA do Breadcrumb (etapa 6) em site/breadcrumb-qa.html.

Mesmo arranjo dos outros componentes: a pagina INLINA os arquivos reais do
repositorio - foundation, Icon, Tab (os itens do menu sao Tab Square),
tokens do Breadcrumb, breadcrumb.css e breadcrumb.js. Ela nao pode divergir do
codigo porque ela E o codigo.

O QUE A PAGINA MOSTRA

  - UM breadcrumb vivo (regra 7: um por pagina), Large com 6 niveis: e nele
    que se tabula, abre o `…`, aperta Esc, clica fora.
  - As quatro profundidades (Short, Medium, 4 niveis, Large) sobre a tela e
    sobre `bg-surface` - os dois fundos medidos (regra 7).
  - O menu ABERTO congelado, para ver a posicao e a sombra sem clicar.
  - A quebra de linha numa coluna de 320 (regra 12).
  Tudo que nao e o vivo fica sob `inert` (o a11y.py isenta). O `…` congelado
  ja nasce com `data-al-breadcrumb`: o breadcrumb.js trata como ja ligado e
  nao o fecha no primeiro clique da pagina.

O a11y.py ao lado le o HTML que este script emite e cobra ali o contrato de
marcacao; a tabela de contraste desta pagina e a mesma funcao que ele roda.

Rodar: python3 qa.py     (escreve o proprio arquivo; nunca redirecionar stdout)
"""
import html
import importlib.util
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(ROOT, 'site', 'breadcrumb-qa.html')

BC = json.load(open(os.path.join(HERE, 'tokens.json')))

CSS_FILES = [
    os.path.join(ROOT, 'foundation', 'al-foundation.css'),
    os.path.join(ROOT, 'components', 'icon', 'al-icon-tokens.css'),
    os.path.join(ROOT, 'components', 'icon', 'icon.css'),
    os.path.join(ROOT, 'components', 'tab', 'al-tab-tokens.css'),
    os.path.join(ROOT, 'components', 'tab', 'tab.css'),
    os.path.join(HERE, 'al-breadcrumb-tokens.css'),
    os.path.join(HERE, 'breadcrumb.css'),
]
JS_FILE = os.path.join(HERE, 'breadcrumb.js')

SEP = ('<svg class="al-icon al-icon--16 al-breadcrumb__separator" viewBox="0 0 24 24" '
       'aria-hidden="true" focusable="false"><path d="m9 18 6-6-6-6"/></svg>')


def slug(s):
    return ''.join(c if c.isalnum() else '-' for c in s.lower()).strip('-')


def trail(levels, menu_id, aria='Trilha de navegação', frozen_open=False):
    """Monta a marcacao do contrato. Ate 4 niveis: tudo. 5+: Large (regra 5)."""
    e = html.escape
    li = []

    def link(label, path):
        return (f'<li class="al-breadcrumb__item"><a class="al-breadcrumb__link" '
                f'href="#{path}">{e(label)}</a>{SEP}</li>')

    *parents, current = levels
    if len(levels) >= 5:
        li.append(link(parents[0], slug(parents[0])))
        li.append(link(parents[1], slug(parents[1])))
        hidden = parents[2:]
        items = ''.join(f'<li><a class="al-tab" href="#{slug(h)}"><span class="al-tab__label">'
                        f'{e(h)}</span></a></li>' for h in hidden)
        exp = 'true' if frozen_open else 'false'
        bound = ' data-al-breadcrumb' if frozen_open else ''
        li.append(
            f'<li class="al-breadcrumb__item al-breadcrumb__more">'
            f'<button class="al-breadcrumb__more-button" type="button" aria-label="Mostrar mais páginas" '
            f'aria-expanded="{exp}" aria-controls="{menu_id}"{bound}>…</button>'
            f'<ul class="al-tabs al-tabs--square al-breadcrumb__menu" id="{menu_id}"'
            f'{"" if frozen_open else " hidden"}>{items}</ul>{SEP}</li>')
    else:
        li.extend(link(p, slug(p)) for p in parents)
    li.append(f'<li class="al-breadcrumb__item"><span class="al-breadcrumb__current" '
              f'aria-current="page">{e(current)}</span></li>')
    return (f'<nav class="al-breadcrumb" aria-label="{e(aria)}"><ol class="al-breadcrumb__list">'
            + ''.join(li) + '</ol></nav>')


SEIS = ['Início', 'Vendas', 'Pedidos', 'Março de 2026', 'Loja Centro', 'Pedido 1042']
CASOS = [
    ('Short', '2 níveis', ['Início', 'Vendas']),
    ('Medium', '3 níveis', ['Início', 'Vendas', 'Pedidos']),
    ('Medium + 1', '4 níveis — ainda sem “…” (regra 5)', ['Início', 'Vendas', 'Pedidos', 'Pedido 1042']),
    ('Large', '6 níveis — primeiro, segundo, “…”, atual (regra 6)', SEIS),
]
LONGOS = ['Início', 'Configurações da conta', 'Integrações e aplicativos',
          'Notificações por e-mail']


def contrast_table():
    spec = importlib.util.spec_from_file_location('bc_a11y', os.path.join(HERE, 'a11y.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    rows = mod.contrast_rows()
    out = []
    for r in rows:
        if r['invisible']:
            v, cls = 'invisível', 'bad'
        elif r['pass']:
            v, cls = 'passa', 'ok'
        elif r['exception']:
            v, cls = f'exceção “{r["exception"]}”', 'exc'
        else:
            v, cls = 'reprova', 'bad'
        ratio = '—' if r['floor'] == 1.0 else f'{r["ratio"]:.2f}'
        floor = 'diferente' if r['floor'] == 1.0 else f'{r["floor"]}'
        tema = 'claro' if r['theme'] == 'light' else 'escuro'
        out.append(f'<tr><td>{tema}</td><td>{html.escape(r["what"])}</td><td><code>{r["fg"]}</code></td>'
                   f'<td><code>{r["bg"]}</code></td><td>{ratio}</td><td>{floor}</td>'
                   f'<td class="qa-verdict qa-verdict--{cls}">{v}</td></tr>')
    n_ok = sum(r['pass'] for r in rows)
    n_exc = sum(bool(r['exception']) for r in rows)
    n_bad = len(rows) - n_ok - n_exc
    return ''.join(out), len(rows), n_ok, n_exc, n_bad


CHROME = '''
body { margin: 0; background: var(--al-bg-canvas); color: var(--al-text-primary);
  font-family: var(--al-font-sans); font-size: var(--al-font-size-md); line-height: var(--al-line-height-md); }
.qa-wrap { max-width: 1120px; margin: 0 auto; padding-inline: var(--al-space-16);
  padding-block: var(--al-space-32) var(--al-space-64); display: flex; flex-direction: column; gap: var(--al-space-48); }
.qa-head { display: flex; flex-wrap: wrap; align-items: flex-end; justify-content: space-between;
  gap: var(--al-space-16); border-bottom: 1px solid var(--al-border-subtle); padding-bottom: var(--al-space-16); }
.qa-head h1 { margin: 0; font-size: var(--al-font-size-3xl); line-height: var(--al-line-height-3xl);
  font-weight: 600; letter-spacing: -0.02em; }
.qa-sub { margin: var(--al-space-4) 0 0; color: var(--al-text-secondary); font-size: var(--al-font-size-sm); }
.qa-btn { display: inline-flex; align-items: center; gap: var(--al-space-8); padding: var(--al-space-8) var(--al-space-16);
  border: 1px solid var(--al-border-strong); border-radius: var(--al-radius-full); background: var(--al-bg-surface-raised);
  color: var(--al-text-primary); font: inherit; font-size: var(--al-font-size-sm); cursor: pointer; }
.qa-btn:focus-visible { outline: none; box-shadow: var(--al-focus-ring-default); }
section h2 { margin: 0 0 var(--al-space-4); font-size: var(--al-font-size-xl); line-height: var(--al-line-height-xl);
  font-weight: 600; letter-spacing: -0.01em; }
section > p.qa-lede { margin: 0 0 var(--al-space-20); color: var(--al-text-secondary); max-width: 66ch; }
.qa-live { padding: var(--al-space-24); border: 1px dashed var(--al-border-default); border-radius: var(--al-radius-xl);
  display: flex; flex-direction: column; gap: var(--al-space-16); }
.qa-live h3 { margin: 0; font-size: var(--al-font-size-2xl); line-height: var(--al-line-height-2xl); font-weight: 600; }
.qa-live a.qa-after { color: var(--al-text-secondary); font-size: var(--al-font-size-sm); }
.qa-grid { display: grid; gap: var(--al-space-20); grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); }
.qa-card { display: flex; flex-direction: column; gap: var(--al-space-12); padding: var(--al-space-20);
  border: 1px solid var(--al-border-subtle); border-radius: var(--al-radius-xl); }
.qa-card--canvas { background: var(--al-bg-canvas); }
.qa-card--surface { background: var(--al-bg-surface); }
.qa-card__title { margin: 0; font-size: var(--al-font-size-xs); font-weight: 600; letter-spacing: 0.04em;
  text-transform: uppercase; color: var(--al-text-secondary); }
.qa-card__note { margin: 0; color: var(--al-text-secondary); font-size: var(--al-font-size-xs); line-height: var(--al-line-height-xs); }
.qa-open { min-height: 240px; display: flex; justify-content: center; padding-top: var(--al-space-16); }
.qa-narrow { width: 320px; max-width: 100%; box-sizing: border-box; }
.qa-checks { margin: 0; padding-left: var(--al-space-20); display: grid; gap: var(--al-space-8); max-width: 72ch; }
.qa-checks li { color: var(--al-text-secondary); }
.qa-checks strong { color: var(--al-text-primary); font-weight: 500; }
.qa-tablewrap { overflow-x: auto; }
table.qa-measure { border-collapse: collapse; width: 100%; font-size: var(--al-font-size-sm); font-variant-numeric: tabular-nums; }
table.qa-measure th, table.qa-measure td { text-align: left; padding: var(--al-space-8) var(--al-space-12);
  border-bottom: 1px solid var(--al-border-subtle); white-space: nowrap; }
table.qa-measure th { font-weight: 600; font-size: var(--al-font-size-xs); text-transform: uppercase;
  letter-spacing: 0.04em; color: var(--al-text-secondary); }
.qa-verdict { font-weight: 600; }
.qa-verdict--ok { color: var(--al-text-success); }
.qa-verdict--exc { color: var(--al-text-warning); }
.qa-verdict--bad { color: var(--al-text-danger); }
code { font-family: var(--al-font-mono); font-size: 0.9em; }
.qa-foot { color: var(--al-text-secondary); font-size: var(--al-font-size-sm); border-top: 1px solid var(--al-border-subtle);
  padding-top: var(--al-space-16); }
'''


def build():
    css = '\n'.join(open(p, encoding='utf-8').read() for p in CSS_FILES)
    # o cabecalho do breadcrumb.js cita `<script src=...></script>`: inline, isso
    # fecharia a tag no meio do comentario
    js = open(JS_FILE, encoding='utf-8').read().replace('</script', '<\\/script')
    rows, n, ok, exc, bad = contrast_table()

    cards = []
    for fundo, nome in (('canvas', 'tela'), ('surface', 'bg-surface')):
        for titulo, nota, levels in CASOS:
            mid = f'qa-m-{fundo}-{slug(titulo)}'
            cards.append(f'<article class="qa-card qa-card--{fundo}"><p class="qa-card__title">{titulo} · {nome}</p>'
                         f'{trail(levels, mid, aria=f"Exemplo {titulo}")}<p class="qa-card__note">{nota}</p></article>')

    page = f'''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Breadcrumb QA</title>
<style>
{css}
{CHROME}
</style>
</head>
<body>
<main class="qa-wrap">
  <header class="qa-head">
    <div>
      <h1>Breadcrumb — QA e acessibilidade</h1>
      <p class="qa-sub">Etapa 6 · CSS e JS reais do repositório · breadcrumb + _breadcrumb-more · {len(BC["alias"])} tokens</p>
    </div>
    <button type="button" class="qa-btn" id="theme-toggle" aria-pressed="false"><span id="theme-label">Tema claro</span></button>
  </header>

  <section aria-labelledby="h-vivo">
    <h2 id="h-vivo">O breadcrumb vivo</h2>
    <p class="qa-lede">O único desta página que reage (regra 7: um por página). Large com 6 níveis — Pedidos, Março de 2026 e Loja Centro estão no “…”. Tabule a partir do botão de tema.</p>
    <div class="qa-live">
      {trail(SEIS, 'bc-mais')}
      <h3>Pedido 1042</h3>
      <a class="qa-after" href="#h-casos">Link depois da trilha — para conferir que o Tab sai do menu e ele fecha</a>
    </div>
  </section>

  <section aria-labelledby="h-casos">
    <h2 id="h-casos">As quatro profundidades, nos dois fundos medidos</h2>
    <p class="qa-lede">Exemplos congelados (inert). Até 4 níveis a trilha mostra tudo; com 5 ou mais vira a Large.</p>
    <div class="qa-grid" inert>{''.join(cards)}</div>
  </section>

  <section aria-labelledby="h-aberto">
    <h2 id="h-aberto">Menu aberto, congelado</h2>
    <p class="qa-lede">8 abaixo do “…”, centralizado, largura mínima 108 crescendo com o rótulo, Elevation/3. No Figma: x −48, y +28 em relação ao “…”.</p>
    <div class="qa-grid" inert>
      <article class="qa-card qa-card--canvas"><p class="qa-card__title">Aberto · tela</p>
        <div class="qa-open">{trail(SEIS, 'qa-open-c', aria='Exemplo aberto', frozen_open=True)}</div></article>
      <article class="qa-card qa-card--surface"><p class="qa-card__title">Aberto · bg-surface</p>
        <div class="qa-open">{trail(['Início', 'Vendas', 'Relatórios', 'Configurações da conta', 'Pedido 1042'], 'qa-open-s', aria='Exemplo aberto, rótulo longo', frozen_open=True)}</div>
        <p class="qa-card__note">Rótulo longo: o menu passa de 108 e cresce (decisão A).</p></article>
    </div>
  </section>

  <section aria-labelledby="h-estreita">
    <h2 id="h-estreita">Tela estreita</h2>
    <p class="qa-lede">Coluna de 320. A trilha quebra para a linha de baixo; nenhum rótulo é cortado, e link e setinha andam juntos (regra 12).</p>
    <div class="qa-card qa-card--canvas qa-narrow" inert>{trail(LONGOS, 'qa-narrow', aria='Exemplo estreito')}</div>
  </section>

  <section aria-labelledby="h-teste">
    <h2 id="h-teste">O que testar</h2>
    <ol class="qa-checks">
      <li><strong>Tab a partir do botão de tema:</strong> Início → Vendas → “…” → link depois da trilha. A página atual não recebe foco (regra 15).</li>
      <li><strong>Anel de foco</strong> em cada link e no “…”, com canto arredondado (decisão C). Só por teclado — clicando com o mouse não aparece.</li>
      <li><strong>Enter ou Espaço no “…”:</strong> o menu abre e o foco <em>fica</em> no “…” (decisão B). Tab entra em Pedidos, Março de 2026, Loja Centro.</li>
      <li><strong>Esc</strong> com o foco no menu: fecha e o foco volta ao “…”.</li>
      <li><strong>Tab depois de Loja Centro:</strong> o foco vai para o link de baixo e o menu fecha sozinho.</li>
      <li><strong>Clique fora</strong> com o menu aberto: fecha. <strong>Clique num item:</strong> fecha e navega.</li>
      <li><strong>Mouse sobre a trilha:</strong> nada muda além do cursor (regra 14). <strong>Sobre os itens do menu:</strong> hover e clique pressionado aparecem — inclusive no escuro (regra 26).</li>
      <li><strong>Tema escuro:</strong> repita o hover no menu; antes do <code>-raised</code> ele sumia.</li>
      <li><strong>Leitor de tela (VoiceOver):</strong> “Trilha de navegação, navegação”, lista de 4 itens, “Mostrar mais páginas, recolhido/expandido”, “Pedido 1042, página atual”. As setinhas não são lidas.</li>
    </ol>
  </section>

  <section aria-labelledby="h-medidas">
    <h2 id="h-medidas">Contraste por combinação renderizada</h2>
    <p class="qa-lede">{n} medições · {ok} passam · {exc} exceções declaradas · {bad} reprovas. Mesma função do <code>a11y.py</code>; fundo efetivo de cada estado.</p>
    <div class="qa-tablewrap"><table class="qa-measure">
      <thead><tr><th>Tema</th><th>O quê</th><th>Cor</th><th>Fundo</th><th>Razão</th><th>Piso</th><th>Veredito</th></tr></thead>
      <tbody>{rows}</tbody></table></div>
  </section>

  <footer class="qa-foot">Gerado por <code>components/breadcrumb/qa.py</code>. Exceção herdada: <code>borda-de-regiao</code> — a borda do menu fica abaixo de 3:1 contra a página; o menu é caixa de conteúdo e se separa pela sombra Elevation/3 (etapa 3).</footer>
</main>
<script>
{js}
</script>
<script>
(function () {{
  var root = document.documentElement;
  var btn = document.getElementById('theme-toggle');
  var label = document.getElementById('theme-label');
  function escuro() {{
    if (root.dataset.theme) return root.dataset.theme === 'dark';
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  }}
  function sync() {{
    var d = escuro();
    btn.setAttribute('aria-pressed', d ? 'true' : 'false');
    label.textContent = d ? 'Tema escuro' : 'Tema claro';
  }}
  btn.addEventListener('click', function () {{
    root.dataset.theme = escuro() ? 'light' : 'dark';
    sync();
  }});
  sync();
}})();
</script>
</body>
</html>
'''
    open(OUT, 'w', encoding='utf-8').write(page)
    print(f'{os.path.relpath(OUT, ROOT)} escrito ({os.path.getsize(OUT)} bytes)')


if __name__ == '__main__':
    build()
