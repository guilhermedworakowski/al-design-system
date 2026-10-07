"""
Gera a visualizacao de QA do Divider (etapa 6) em site/divider-qa.html.

Mesmo arranjo dos outros componentes: a pagina INLINA os arquivos de CSS reais
do repositorio - foundation, tokens do Divider e divider.css. Ela nao pode
divergir do codigo porque ela E o codigo.

O QUE E DIFERENTE DOS CONTROLES

  O Divider nao tem estado, entao nao ha cartao por variante de estado. A
  pagina mostra as duas orientacoes e os tres jeitos de marcar (anunciado,
  vertical anunciado, decorativo), a linha sobre as TRES superficies do
  sistema - foi assim que a etapa 6 achou a linha invisivel no card escuro com
  `border-subtle`, trocado por `border-default` (opcao A de Gui) - e
  quatro usos reais tirados das regras de uso: secoes de pagina, rodape de
  card, lista em grupos e barra de acoes.

O a11y.py ao lado le o HTML que este script emite e cobra ali o contrato de
marcacao.

Rodar: python3 qa.py     (escreve o proprio arquivo; nunca redirecionar stdout)
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(ROOT, 'site', 'divider-qa.html')

FOUND = json.load(open(os.path.join(ROOT, 'tokens.json')))
DIVIDER = json.load(open(os.path.join(HERE, 'tokens.json')))

CSS_FILES = [
    ('foundation', os.path.join(ROOT, 'foundation', 'al-foundation.css')),
    ('divider - tokens', os.path.join(HERE, 'al-divider-tokens.css')),
    ('divider', os.path.join(HERE, 'divider.css')),
]

HR = '<hr class="al-divider">'
HR_DECOR = '<hr class="al-divider" aria-hidden="true">'
HR_V = '<hr class="al-divider al-divider--vertical" aria-orientation="vertical">'
HR_V_DECOR = '<hr class="al-divider al-divider--vertical" aria-hidden="true">'
LI_SEP = '<li class="al-divider" role="separator"></li>'

SUPERFICIES = [
    ('bg-canvas', 'Tela', 'a página nua'),
    ('bg-surface', 'Faixa de seção', 'fundo de seção, o mesmo dos cartões desta página'),
    ('bg-surface-raised', 'Card ou modal', 'onde o divisor mais aparece: rodapé de card, grupos de menu'),
]


def cartao(titulo, origem, nota, corpo):
    return f'''<article class="qa-card">
      <header class="qa-card__head">
        <h3 class="qa-card__title">{titulo}</h3>
        <span class="qa-tag qa-tag--{origem}">{origem}</span>
      </header>
      <div class="qa-card__stage">{corpo}</div>
      <p class="qa-card__note">{nota}</p>
    </article>'''


ORIENTACOES = [
    ('Horizontal, anunciada', 'real',
     'o padrão (opção A). O leitor de tela diz “separador”. Regra 12.',
     f'<p class="qa-txt">Dados pessoais</p>{HR}<p class="qa-txt">Endereço</p>'),
    ('Vertical, anunciada', 'real',
     'aria-orientation="vertical" — sem ele o leitor entenderia horizontal. Estica na altura da linha. Regra 14.',
     f'<div class="qa-row qa-row--panels"><p class="qa-txt">Entrada</p>{HR_V}<p class="qa-txt">Saída</p></div>'),
    ('Decorativa', 'real',
     'aria-hidden="true": mesma linha, o leitor de tela não ouve nada. Regra 13.',
     f'<p class="qa-txt">Total</p>{HR_DECOR}<p class="qa-txt">R$ 120,00</p>'),
]


def superficie(token, nome, nota):
    return f'''<div class="qa-surface" style="background: var(--al-{token})" data-bg="{token}">
        <p class="qa-surface__name">{nome} <code>{token}</code></p>
        <p class="qa-txt">Bloco de cima</p>
        {HR}
        <p class="qa-txt">Bloco de baixo</p>
        <p class="qa-surface__note">{nota}</p>
      </div>'''


def build():
    css = []
    for nome, path in CSS_FILES:
        css.append(f'/* ================= {nome} ================= */')
        css.append(open(path, encoding='utf-8').read())
    css_inline = '\n'.join(css)

    orient = '\n    '.join(cartao(*o) for o in ORIENTACOES)
    sups = '\n      '.join(superficie(*s) for s in SUPERFICIES)

    meta = DIVIDER['meta']
    rows = DIVIDER['contrast']

    return f'''<meta charset="utf-8">
<title>AL Divider QA</title>
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
section h2 {{
  margin: 0 0 var(--al-space-4);
  font-size: var(--al-font-size-xl); line-height: var(--al-line-height-xl);
  font-weight: 600; letter-spacing: -0.01em;
}}
section > p.qa-lede {{ margin: 0 0 var(--al-space-20); color: var(--al-text-secondary); max-width: 62ch; }}
.qa-grid {{
  display: grid; gap: var(--al-space-20);
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
}}
.qa-card {{
  display: flex; flex-direction: column; gap: var(--al-space-12);
  padding: var(--al-space-20);
  border: 1px solid var(--al-border-subtle); border-radius: var(--al-radius-xl);
  background: var(--al-bg-surface);
}}
.qa-card__head {{ display: flex; align-items: center; justify-content: space-between; gap: var(--al-space-8); }}
.qa-card__title {{ margin: 0; font-size: var(--al-font-size-sm); font-weight: 600; letter-spacing: 0.04em; text-transform: uppercase; }}
.qa-card__stage {{ display: flex; flex-direction: column; gap: var(--al-space-8); min-height: var(--al-space-48); }}
.qa-card__note {{ margin: 0; margin-top: auto; color: var(--al-text-secondary); font-size: var(--al-font-size-xs); line-height: var(--al-line-height-xs); }}
.qa-tag {{
  font-size: var(--al-font-size-xs); line-height: var(--al-line-height-xs);
  padding: 2px var(--al-space-8); border-radius: var(--al-radius-full);
  border: 1px solid var(--al-border-default); color: var(--al-text-secondary);
  white-space: nowrap;
}}
.qa-tag--real {{ border-color: var(--al-border-success); color: var(--al-text-success); }}
.qa-tag--codigo {{ border-color: var(--al-border-info); color: var(--al-text-info); }}
.qa-checks {{ margin: 0; padding-left: var(--al-space-20); display: grid; gap: var(--al-space-8); max-width: 68ch; }}
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

/* ---- especificos do Divider ---- */
.qa-txt {{ margin: 0; }}
.qa-row {{ display: flex; align-items: center; gap: var(--al-space-12); flex-wrap: wrap; }}
.qa-row--panels {{ align-items: stretch; }}
.qa-row--panels > .qa-txt {{ flex: 1; padding-block: var(--al-space-12); }}
.qa-surfaces {{ display: grid; gap: var(--al-space-20); grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); }}
.qa-surface {{
  display: flex; flex-direction: column; gap: var(--al-space-12);
  padding: var(--al-space-20); border-radius: var(--al-radius-xl);
  box-shadow: var(--al-elevation-1);
}}
.qa-surface__name {{ margin: 0; font-size: var(--al-font-size-sm); font-weight: 600; }}
.qa-surface__note {{ margin: 0; color: var(--al-text-secondary); font-size: var(--al-font-size-xs); line-height: var(--al-line-height-xs); }}
.qa-uses {{ display: grid; gap: var(--al-space-20); grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); }}
.qa-use {{ display: flex; flex-direction: column; gap: var(--al-space-8); }}
.qa-use > h3 {{ margin: 0; font-size: var(--al-font-size-sm); font-weight: 600; letter-spacing: 0.04em; text-transform: uppercase; }}
.qa-use > .qa-card__note {{ margin-top: 0; }}
.qa-page {{ display: flex; flex-direction: column; gap: var(--al-space-16); padding: var(--al-space-20); background: var(--al-bg-canvas); border: 1px solid var(--al-border-subtle); border-radius: var(--al-radius-xl); }}
.qa-page h4 {{ margin: 0 0 var(--al-space-4); font-size: var(--al-font-size-md); font-weight: 600; }}
.qa-page p {{ margin: 0; color: var(--al-text-secondary); font-size: var(--al-font-size-sm); }}
.qa-elev {{ display: flex; flex-direction: column; gap: var(--al-space-16); padding: var(--al-space-20); background: var(--al-bg-surface-raised); border-radius: var(--al-radius-xl); box-shadow: var(--al-elevation-2); }}
.qa-elev h4 {{ margin: 0; font-size: var(--al-font-size-md); font-weight: 600; }}
.qa-elev p {{ margin: 0; color: var(--al-text-secondary); font-size: var(--al-font-size-sm); }}
.qa-elev .qa-actions {{ display: flex; gap: var(--al-space-8); justify-content: flex-end; }}
.qa-menu {{ list-style: none; margin: 0; padding: var(--al-space-4) 0; background: var(--al-bg-surface-raised); border-radius: var(--al-radius-lg); box-shadow: var(--al-elevation-2); display: flex; flex-direction: column; }}
.qa-menu > li:not(.al-divider) {{ padding: var(--al-space-8) var(--al-space-16); font-size: var(--al-font-size-sm); }}
.qa-menu > .al-divider {{ margin-block: var(--al-space-4); }}
.qa-menu .qa-danger {{ color: var(--al-text-danger); }}
.qa-toolbar {{ display: flex; align-items: stretch; gap: var(--al-space-8); padding: var(--al-space-8); background: var(--al-bg-surface-raised); border-radius: var(--al-radius-lg); box-shadow: var(--al-elevation-2); flex-wrap: wrap; }}
</style>

<div class="qa-wrap">
  <header class="qa-head">
    <div>
      <h1>Divider — QA da etapa 6</h1>
      <p class="qa-sub">AL Design System {FOUND['meta']['version']} · componente {meta['version']} ·
      &lt;hr&gt; nativo · {len(rows)} medições de token na etapa 3, todas exceção declarada</p>
    </div>
    <button type="button" class="qa-btn" id="theme-toggle" aria-pressed="false">
      <span id="theme-label">Tema claro</span>
    </button>
  </header>

  <section>
    <h2>O que testar</h2>
    <ol class="qa-checks">
      <li><strong>Tabule pela página inteira.</strong> O foco passa pelos botões e nunca para num divisor (regra 16).</li>
      <li><strong>Troque o tema</strong> no botão acima e olhe a seção “Nas três superfícies”: a linha aparece nas três, inclusive no card escuro, onde antes sumia.</li>
      <li><strong>Reduza a janela</strong> até a largura de telefone: a horizontal acompanha, a vertical da barra de ações quebra junto com os botões.</li>
      <li><strong>Com leitor de tela</strong> (VoiceOver: Ctrl+Opção+→), percorra “Usos reais”: as seções e o menu dizem “separador”; o card e a barra de ações, não.</li>
      <li><strong>Ative o alto contraste do sistema</strong> (Windows) ou “Aumentar contraste” (macOS): a linha continua visível, porque é borda.</li>
    </ol>
  </section>

  <section>
    <h2>Orientação e marcação</h2>
    <p class="qa-lede">A mesma linha, três contratos. Visualmente idênticos; o que muda é o que o
    leitor de tela ouve.</p>
    <div class="qa-grid">
    {orient}
    </div>
  </section>

  <section>
    <h2>Nas três superfícies</h2>
    <p class="qa-lede">A etapa 3 mediu a tela e a faixa de seção. Aqui entra a terceira superfície do
    sistema — card e modal. Com <code>border-subtle</code> a linha sumia ali no escuro (mesma cor do card); com <code>border-default</code> ela fica em 1,46:1.</p>
    <div class="qa-surfaces">
      {sups}
    </div>
  </section>

  <section>
    <h2>Usos reais</h2>
    <p class="qa-lede">Tirados das regras de uso. Cada um com o contrato que a regra pede.</p>
    <div class="qa-uses">
      <div class="qa-use">
        <h3>Seções de página</h3>
        <div class="qa-page">
          <div><h4>Dados pessoais</h4><p>Nome, documento e data de nascimento.</p></div>
          {HR}
          <div><h4>Endereço</h4><p>Onde entregamos as notas e os cartões.</p></div>
        </div>
        <p class="qa-card__note">Anunciado: muda o assunto (regra 12). O título também separa (regra 8).</p>
      </div>

      <div class="qa-use">
        <h3>Rodapé de card</h3>
        <div class="qa-elev">
          <div><h4>Plano Pro</h4><p>Cobrança mensal, cancele quando quiser.</p></div>
          {HR_DECOR}
          <div class="qa-actions">
            <button type="button" class="qa-btn">Cancelar</button>
            <button type="button" class="qa-btn qa-btn--primary">Assinar</button>
          </div>
        </div>
        <p class="qa-card__note">Decorativo: os botões já são outra região (regra 13). Card em
        <code>bg-surface-raised</code>: troque o tema e confira que a linha continua lá.</p>
      </div>

      <div class="qa-use">
        <h3>Lista em grupos</h3>
        <ul class="qa-menu" aria-label="Ações do arquivo">
          <li>Editar</li>
          <li>Duplicar</li>
          <li>Mover para…</li>
          {LI_SEP}
          <li class="qa-danger">Excluir</li>
        </ul>
        <p class="qa-card__note">Entre grupos, não entre itens (regra 2). Em lista, a linha é
        <code>&lt;li role="separator"&gt;</code> (regra 15).</p>
      </div>

      <div class="qa-use">
        <h3>Barra de ações</h3>
        <div class="qa-toolbar">
          <button type="button" class="qa-btn">Negrito</button>
          <button type="button" class="qa-btn">Itálico</button>
          {HR_V_DECOR}
          <button type="button" class="qa-btn">Lista</button>
          <button type="button" class="qa-btn">Citação</button>
        </div>
        <p class="qa-card__note">Vertical entre itens lado a lado (regra 5), decorativa: o grupo
        já se vê pelo espaço (regra 13).</p>
      </div>
    </div>
  </section>

  <section>
    <h2>Contraste medido no navegador</h2>
    <p class="qa-lede">Não são os números do <code>tokens.json</code>: o script lê a cor que o navegador
    realmente pintou na borda de cada linha, com <code>getComputedStyle</code>, contra o fundo da caixa
    onde ela está.</p>
    <div class="qa-tablewrap">
      <table class="qa-measure">
        <thead><tr><th>onde</th><th>linha</th><th>fundo</th><th>medido</th><th>piso</th><th>veredito</th></tr></thead>
        <tbody id="measure-body"></tbody>
      </table>
    </div>
  </section>

  <p class="qa-foot">Gerado por <code>components/divider/qa.py</code> a partir do CSS commitado em
  <code>dev</code>. <code>al-foundation.css</code>, <code>al-divider-tokens.css</code> e
  <code>divider.css</code> estão embutidos como estão no repositório.</p>
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

  // ------------------------------------------------------------- contraste
  function rgb(str) {{
    var m = str.match(/-?[\\d.]+/g);
    return m ? [ +m[0], +m[1], +m[2], m[3] === undefined ? 1 : +m[3] ] : null;
  }}
  function lin(c) {{ c /= 255; return c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4); }}
  function lum(c) {{ return 0.2126 * lin(c[0]) + 0.7152 * lin(c[1]) + 0.0722 * lin(c[2]); }}
  function cr(a, b) {{
    var la = lum(a), lb = lum(b);
    return (Math.max(la, lb) + 0.05) / (Math.min(la, lb) + 0.05);
  }}
  // primeiro ancestral com fundo opaco - o fundo EFETIVO da linha
  function fundo(el) {{
    for (var p = el.parentElement; p; p = p.parentElement) {{
      var c = rgb(getComputedStyle(p).backgroundColor);
      if (c && c[3] > 0) return c;
    }}
    return [255, 255, 255, 1];
  }}
  function onde(el) {{
    var s = el.closest('.qa-surface');
    if (s) return s.querySelector('.qa-surface__name').firstChild.textContent.trim();
    var u = el.closest('.qa-use');
    if (u) return u.querySelector('h3').textContent;
    var c = el.closest('.qa-card');
    return c ? c.querySelector('.qa-card__title').textContent : '—';
  }}

  function medir() {{
    var corpo = r('measure-body');
    corpo.textContent = '';
    document.querySelectorAll('.al-divider').forEach(function (el) {{
      var vertical = el.classList.contains('al-divider--vertical');
      var fg = rgb(getComputedStyle(el)[vertical ? 'borderLeftColor' : 'borderTopColor']);
      var bg = fundo(el);
      var v = cr(fg, bg);
      var igual = fg[0] === bg[0] && fg[1] === bg[1] && fg[2] === bg[2];
      var classe = v >= 3 ? 'ok' : (igual ? 'bad' : 'exc');
      var texto = v >= 3 ? 'passa' : (igual ? 'INVISÍVEL' : 'exceção declarada');
      var tr = document.createElement('tr');
      [onde(el), 'rgb(' + fg.slice(0, 3).join(', ') + ')', 'rgb(' + bg.slice(0, 3).join(', ') + ')',
       v.toFixed(2) + ':1', '3.0:1'].forEach(function (x) {{
        var td = document.createElement('td'); td.textContent = x; tr.appendChild(td);
      }});
      var td = document.createElement('td');
      td.textContent = texto;
      td.className = 'qa-verdict qa-verdict--' + classe;
      tr.appendChild(td);
      corpo.appendChild(tr);
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
    print(f'site/divider-qa.html escrito ({len(html)} bytes)')
    print(f'  CSS embutido: {", ".join(n for n, _ in CSS_FILES)}')
    corpo = re.sub(r'<style\b[^>]*>.*?</style>', '', html, flags=re.S)
    corpo = re.sub(r'<script\b[^>]*>.*?</script>', '', corpo, flags=re.S)
    n = len(re.findall(r'class="al-divider\b', corpo))
    print(f'  divisores de verdade no documento: {n}')
