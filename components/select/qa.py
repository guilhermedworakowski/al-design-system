"""
Gera a visualizacao de QA do Select (etapa 6) em site/select-qa.html.

Por que um gerador e nao um HTML escrito a mao: a pagina INLINA os arquivos de
CSS reais do repositorio - foundation, icon, tokens do Select e select.css.
Ela nao pode divergir do codigo porque ela E o codigo; mexer no select.css e
rodar este script de novo basta. Uma copia escrita a mao envelheceria em
silencio, e QA feito sobre copia envelhecida nao e QA.

O a11y.py ao lado le o HTML que este script emite e cobra ali o contrato de
marcacao - mesmo arranjo que o Icon ja usa com o site.py: contraste se prova no
token, marcacao so existe na saida renderizada.

Rodar: python3 qa.py     (escreve o proprio arquivo; nunca redirecionar stdout)
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(ROOT, 'site', 'select-qa.html')

FOUND = json.load(open(os.path.join(ROOT, 'tokens.json')))
SELECT = json.load(open(os.path.join(HERE, 'tokens.json')))

CSS_FILES = [
    ('foundation', os.path.join(ROOT, 'foundation', 'al-foundation.css')),
    ('icon - tokens', os.path.join(ROOT, 'components', 'icon', 'al-icon-tokens.css')),
    ('icon', os.path.join(ROOT, 'components', 'icon', 'icon.css')),
    ('select - tokens', os.path.join(HERE, 'al-select-tokens.css')),
    ('select', os.path.join(HERE, 'select.css')),
]

CHEVRON = ('<svg class="al-icon al-select__chevron" viewBox="0 0 24 24" fill="none" '
           'stroke="currentColor" stroke-width="2" stroke-linecap="round" '
           'stroke-linejoin="round" aria-hidden="true" focusable="false">'
           '<path d="m6 9 6 6 6-6"/></svg>')

UFS = ['Acre', 'Bahia', 'Ceara', 'Minas Gerais', 'Parana', 'Sao Paulo']


def campo(cid, rotulo, *, opcional=False, apoio=None, erro=None,
          disabled=False, valor=None, sim=None):
    """Um Select completo. `sim` força um estado que so existe sob interacao
    (hover, active) escrevendo na MESMA variavel privada que o select.css usa -
    nao e um estilo paralelo, e o proprio mecanismo do componente."""
    classes = 'al-select__field'
    attrs = [f'id="{cid}"', f'class="{classes}"']
    desc = []
    if apoio or erro:
        desc.append(f'{cid}-help')
    if erro:
        attrs.append('aria-invalid="true"')
    if disabled:
        attrs.append('disabled')
    if desc:
        attrs.append(f'aria-describedby="{" ".join(desc)}"')
    if sim:
        attrs.append(f'style="--_border-state: var(--al-select-border-{sim})"')

    opcoes = [f'<option value="" disabled{"" if valor else " selected"}>Selecione o estado</option>']
    for uf in UFS:
        sel = ' selected' if valor == uf else ''
        opcoes.append(f'<option value="{uf}"{sel}>{uf}</option>')

    marca = (f'\n        <span class="al-select__optional">(Opcional)</span>'
             if opcional else '')
    mensagem = erro or apoio
    linha_apoio = (f'\n      <p class="al-select__help" id="{cid}-help">{mensagem}</p>'
                   if mensagem else '')

    return f'''<div class="al-select">
      <div class="al-select__labelrow">
        <label class="al-select__label" for="{cid}">{rotulo}</label>{marca}
      </div>
      <div class="al-select__control">
        <select {" ".join(attrs)}>
          {chr(10).join("          " + o for o in opcoes).strip()}
        </select>
        {CHEVRON}
      </div>{linha_apoio}
    </div>'''


# (titulo, origem, nota, kwargs do campo)
# A nota diz o que FAZER naquele cartao. "estado real - interaja" nao ajuda
# ninguem: cada estado se prova de um jeito diferente.
ESTADOS = [
    ('Default', 'real', 'o repouso. A borda aqui e a excecao de contraste declarada.',
     dict(cid='st-default', rotulo='Estado')),
    ('Hover', 'simulado',
     'so existe sob o ponteiro, entao a variavel privada do componente foi escrita direto.',
     dict(cid='st-hover', rotulo='Estado', sim='hover')),
    ('Active', 'simulado',
     'so existe no instante em que o botao do mouse esta pressionado - mesma escrita direta.',
     dict(cid='st-active', rotulo='Estado', sim='active')),
    ('Focus', 'real',
     'o anel laranja aparece por Tab E por clique - medido no Chromium na etapa 6. '
     'Focus e o estado que permanece; active e so o instante do botao pressionado.',
     dict(cid='st-focus', rotulo='Estado')),
    ('Error', 'real',
     'vem de aria-invalid="true" na marcacao, nunca de uma classe.',
     dict(cid='st-error', rotulo='Estado', erro='Escolha um estado para continuar')),
    ('Focus + Error', 'real',
     'tabule ate aqui: o anel tem que vir vinho, nao laranja.',
     dict(cid='st-focuserror', rotulo='Estado', erro='Escolha um estado para continuar')),
    ('Disabled', 'real',
     'atributo disabled nativo: o Tab pula este campo sozinho, sem tabindex.',
     dict(cid='st-disabled', rotulo='Estado', opcional=True, disabled=True)),
]


def build():
    css = []
    for nome, path in CSS_FILES:
        css.append(f'/* ================= {nome} ================= */')
        css.append(open(path, encoding='utf-8').read())
    css_inline = '\n'.join(css)

    cards = []
    for titulo, origem, nota, kw in ESTADOS:
        cards.append(f'''<article class="qa-card">
      <header class="qa-card__head">
        <h3 class="qa-card__title">{titulo}</h3>
        <span class="qa-tag qa-tag--{origem}">{origem}</span>
      </header>
      {campo(**kw)}
      <p class="qa-card__note">{nota}</p>
    </article>''')

    formulario = '\n      '.join([
        campo(cid='f-uf', rotulo='Estado', apoio='Onde a nota sera emitida'),
        campo(cid='f-tipo', rotulo='Tipo de frete', opcional=True),
        campo(cid='f-erro', rotulo='Transportadora',
              erro='Escolha uma transportadora para continuar'),
        campo(cid='f-off', rotulo='Cidade', disabled=True),
    ])

    meta = SELECT['meta']
    n_contraste = len(SELECT['contrast'])
    n_exc = len([r for r in SELECT['contrast'] if not r['pass']])

    return f'''<meta charset="utf-8">
<title>AL Select QA</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap">
<style>
{css_inline}

/* ================= cromo da pagina de QA =================
   Usa os proprios tokens do AL. Nao ha paleta paralela aqui de proposito:
   se a Foundation mudar, esta pagina muda junto - inclusive errado, se for o
   caso, que e exatamente o que se quer ver num QA. */
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
.qa-theme {{
  display: inline-flex; align-items: center; gap: var(--al-space-8);
  padding: var(--al-space-8) var(--al-space-12);
  border: 1px solid var(--al-border-strong); border-radius: var(--al-radius-full);
  background: var(--al-bg-surface-raised); color: var(--al-text-primary);
  font: inherit; font-size: var(--al-font-size-sm); cursor: pointer;
}}
.qa-theme:focus-visible {{ outline: none; box-shadow: var(--al-focus-ring-default); }}
section h2 {{
  margin: 0 0 var(--al-space-4);
  font-size: var(--al-font-size-xl); line-height: var(--al-line-height-xl);
  font-weight: 600; letter-spacing: -0.01em;
}}
section > p.qa-lede {{ margin: 0 0 var(--al-space-20); color: var(--al-text-secondary); max-width: 62ch; }}
.qa-grid {{
  display: grid; gap: var(--al-space-20);
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
}}
.qa-card {{
  display: flex; flex-direction: column; gap: var(--al-space-12);
  padding: var(--al-space-20);
  border: 1px solid var(--al-border-subtle); border-radius: var(--al-radius-xl);
  background: var(--al-bg-surface);
}}
.qa-card__head {{ display: flex; align-items: center; justify-content: space-between; gap: var(--al-space-8); }}
.qa-card__title {{ margin: 0; font-size: var(--al-font-size-sm); font-weight: 600; letter-spacing: 0.04em; text-transform: uppercase; }}
.qa-card__note {{ margin: 0; color: var(--al-text-secondary); font-size: var(--al-font-size-xs); line-height: var(--al-line-height-xs); }}
.qa-tag {{
  font-size: var(--al-font-size-xs); line-height: var(--al-line-height-xs);
  padding: 2px var(--al-space-8); border-radius: var(--al-radius-full);
  border: 1px solid var(--al-border-default); color: var(--al-text-secondary);
}}
.qa-tag--real {{ border-color: var(--al-border-success); color: var(--al-text-success); }}
.qa-form {{
  display: grid; gap: var(--al-space-20);
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  padding: var(--al-space-24);
  border: 1px solid var(--al-border-subtle); border-radius: var(--al-radius-xl);
  background: var(--al-bg-surface-raised);
}}
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
@media (prefers-reduced-motion: reduce) {{ * {{ transition: none !important; }} }}
</style>

<div class="qa-wrap">
  <header class="qa-head">
    <div>
      <h1>Select — QA da etapa 6</h1>
      <p class="qa-sub">AL Design System {FOUND['meta']['version']} · componente {meta['version']} ·
      &lt;select&gt; nativo · {n_contraste} medições de contraste, {n_exc} exceções declaradas, 0 reprovas</p>
    </div>
    <button type="button" class="qa-theme" id="theme-toggle" aria-pressed="false">
      <span id="theme-label">Tema claro</span>
    </button>
  </header>

  <section>
    <h2>O que testar</h2>
    <ol class="qa-checks">
      <li><strong>Tabule pelo formulário.</strong> Todos os campos devem receber foco na ordem visual, e o <strong>Cidade</strong> (desabilitado) deve ser pulado.</li>
      <li><strong>O anel só aparece no teclado.</strong> Chegue por Tab: anel laranja. Clique com o mouse: borda laranja de active, <em>sem</em> anel. Se o anel aparecer no clique, é o achado que a etapa 1 deixou agendado.</li>
      <li><strong>Campo em erro focado</strong> deve mostrar anel vinho, não laranja.</li>
      <li><strong>Escolha uma opção</strong> em qualquer campo: o texto passa de cinza para escuro sozinho, sem classe nenhuma.</li>
      <li><strong>Troque o tema</strong> no botão acima e refaça os itens 2 e 3.</li>
      <li><strong>Reduza a janela</strong> até a largura de telefone: os campos esticam, nada corta.</li>
    </ol>
  </section>

  <section>
    <h2>Os sete estados</h2>
    <p class="qa-lede">Hover e Active só existem enquanto o ponteiro age, então esses dois cartões
    escrevem direto na variável privada que o próprio <code>select.css</code> usa — é o mecanismo do
    componente, não um estilo paralelo. Os outros cinco são reais: interaja neles.</p>
    <div class="qa-grid">
    {chr(10).join('    ' + c for c in cards)}
    </div>
  </section>

  <section>
    <h2>Formulário real</h2>
    <p class="qa-lede">Quatro campos numa mesma tela, do jeito que o componente vai viver: um com
    texto de apoio, um opcional, um reprovado e um desabilitado. É aqui que a ordem de tabulação
    se prova.</p>
    <form class="qa-form" id="qa-form" onsubmit="return false">
      {formulario}
    </form>
  </section>

  <section>
    <h2>Contraste medido no navegador</h2>
    <p class="qa-lede">Não são os números do <code>tokens.json</code>: o script lê a cor que o
    navegador realmente pintou, com <code>getComputedStyle</code>, depois de esperar a transição
    terminar. Se divergir do portão, o portão está medindo a coisa errada.</p>
    <div class="qa-tablewrap">
      <table class="qa-measure">
        <thead><tr><th>papel</th><th>frente</th><th>fundo</th><th>medido</th><th>piso</th><th>veredito</th></tr></thead>
        <tbody id="measure-body"></tbody>
      </table>
    </div>
  </section>

  <p class="qa-foot">Gerado por <code>components/select/qa.py</code> a partir do CSS commitado em
  <code>dev</code>. Os arquivos <code>foundation/al-foundation.css</code>, <code>icon.css</code>,
  <code>al-select-tokens.css</code> e <code>select.css</code> estão embutidos nesta página como
  estão no repositório.</p>
</div>

<script>
(function () {{
  var root = document.documentElement;
  var btn = document.getElementById('theme-toggle');
  var label = document.getElementById('theme-label');

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
    // 350ms de folga para a transicao de 120ms terminar: ler antes disso
    // devolve a cor do meio do caminho, que e ruido, nao bug.
    setTimeout(medir, 350);
  }});
  pintarBotao();

  // ---------------------------------------------------------- contraste
  function rgb(str) {{
    var m = str.match(/-?[\\d.]+/g);
    return m ? [ +m[0], +m[1], +m[2] ] : null;
  }}
  function lin(c) {{ c /= 255; return c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4); }}
  function lum(c) {{ return 0.2126 * lin(c[0]) + 0.7152 * lin(c[1]) + 0.0722 * lin(c[2]); }}
  function cr(a, b) {{
    var la = lum(a), lb = lum(b);
    var hi = Math.max(la, lb), lo = Math.min(la, lb);
    return (hi + 0.05) / (lo + 0.05);
  }}
  function corDe(el, prop) {{ return rgb(getComputedStyle(el)[prop]); }}

  var PISO_TEXTO = 4.5, PISO_GRAFICO = 3.0;

  function alvos() {{
    var pagina = corDe(document.body, 'backgroundColor');
    var campoOk = document.getElementById('f-uf');
    var campoErro = document.getElementById('f-erro');
    var campoOff = document.getElementById('f-off');
    var fundoCampo = corDe(campoOk, 'backgroundColor');
    var fundoOff = corDe(campoOff, 'backgroundColor');
    var rotulo = document.querySelector('label[for="f-uf"]');
    var rotuloErro = document.querySelector('label[for="f-erro"]');
    var marca = document.querySelector('#qa-form .al-select__optional');
    var apoio = document.getElementById('f-uf-help');
    var apoioErro = document.getElementById('f-erro-help');
    var seta = document.querySelector('#qa-form .al-select__chevron');

    return [
      ['rótulo',            corDe(rotulo, 'color'),        pagina,     PISO_TEXTO,    false],
      ['rótulo em erro',    corDe(rotuloErro, 'color'),    pagina,     PISO_TEXTO,    false],
      ['marca (Opcional)',  corDe(marca, 'color'),         pagina,     PISO_TEXTO,    false],
      ['texto de apoio',    corDe(apoio, 'color'),         pagina,     PISO_TEXTO,    false],
      ['mensagem de erro',  corDe(apoioErro, 'color'),     pagina,     PISO_TEXTO,    false],
      ['placeholder',       corDe(campoOk, 'color'),       fundoCampo, PISO_TEXTO,    false],
      ['seta',              corDe(seta, 'color'),          fundoCampo, PISO_GRAFICO,  false],
      ['borda em repouso',  corDe(campoOk, 'borderTopColor'),   pagina, PISO_GRAFICO, true],
      ['borda em erro',     corDe(campoErro, 'borderTopColor'), pagina, PISO_GRAFICO, false],
      ['texto desabilitado', corDe(campoOff, 'color'),     fundoOff,   PISO_TEXTO,    true],
    ];
  }}

  function medir() {{
    var corpo = document.getElementById('measure-body');
    corpo.textContent = '';
    alvos().forEach(function (linha) {{
      var nome = linha[0], fg = linha[1], bg = linha[2], piso = linha[3], excecao = linha[4];
      if (!fg || !bg) return;
      var razao = cr(fg, bg);
      var passa = razao >= piso;
      var classe = passa ? 'ok' : (excecao ? 'exc' : 'bad');
      var texto = passa ? 'passa' : (excecao ? 'exceção declarada' : 'REPROVA');
      var tr = document.createElement('tr');
      [nome,
       'rgb(' + fg.join(', ') + ')',
       'rgb(' + bg.join(', ') + ')',
       razao.toFixed(2) + ':1',
       piso.toFixed(1) + ':1'
      ].forEach(function (v) {{
        var td = document.createElement('td');
        td.textContent = v;
        tr.appendChild(td);
      }});
      var td = document.createElement('td');
      td.textContent = texto;
      td.className = 'qa-verdict qa-verdict--' + classe;
      tr.appendChild(td);
      corpo.appendChild(tr);
    }});
  }}

  if (document.fonts && document.fonts.ready) {{
    document.fonts.ready.then(function () {{ setTimeout(medir, 50); }});
  }} else {{
    setTimeout(medir, 200);
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
    print(f'site/select-qa.html escrito ({len(html)} bytes)')
    print(f'  CSS embutido: {", ".join(n for n, _ in CSS_FILES)}')
    import re as _re
    # mesma limpeza que o a11y.py faz: o CSS inlinado traz um <select> de
    # exemplo no comentario de ANATOMIA do select.css, e ele nao e um campo.
    corpo = _re.sub(r'<style\b[^>]*>.*?</style>', '', html, flags=_re.S)
    n = len(_re.findall(r'<select\b[^>]*al-select__field', corpo))
    print(f'  campos de verdade no documento: {n}  '
          f'({len(ESTADOS)} cartoes de estado + 4 do formulario)')
