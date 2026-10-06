"""
Gera a visualizacao de QA do Textarea (etapa 6) em site/textarea-qa.html.

Mesmo arranjo do Select e do Input: a pagina INLINA os arquivos de CSS reais
do repositorio - foundation, tokens do Textarea e textarea.css. Ela nao pode
divergir do codigo porque ela E o codigo.

O a11y.py ao lado le o HTML que este script emite e cobra ali o contrato de
marcacao.

O QUE E PROPRIO DO TEXTAREA AQUI
  - O contador e o mesmo do Input: limite sem `maxlength` (regra 16), o script
    da pagina liga `data-over-limit` e troca `aria-live` com o foco.
  - Uma segunda tabela mede GEOMETRIA no navegador: altura com rows=3 e rows=6,
    o piso de 3 linhas segurando rows=2, e o `resize` computado em cada estado
    (vertical / none no disabled / vertical no read-only).

Rodar: python3 qa.py     (escreve o proprio arquivo; nunca redirecionar stdout)
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(ROOT, 'site', 'textarea-qa.html')

FOUND = json.load(open(os.path.join(ROOT, 'tokens.json')))
TA = json.load(open(os.path.join(HERE, 'tokens.json')))

CSS_FILES = [
    ('foundation', os.path.join(ROOT, 'foundation', 'al-foundation.css')),
    ('textarea - tokens', os.path.join(HERE, 'al-textarea-tokens.css')),
    ('textarea', os.path.join(HERE, 'textarea.css')),
]


def campo(cid, rotulo, *, opcional=False, apoio=None, erro=None, rows=3,
          disabled=False, readonly=False, valor='', placeholder=None,
          limite=None, sim=None):
    """Um Textarea completo. `sim` forca o hover escrevendo na MESMA variavel
    privada que o textarea.css usa - o proprio mecanismo do componente."""
    attrs = ['class="al-textarea__field"', f'id="{cid}"', f'name="{cid}"', f'rows="{rows}"']
    if placeholder and not readonly:
        attrs.append(f'placeholder="{placeholder}"')
    if apoio or erro:
        attrs.append(f'aria-describedby="{cid}-help"')
    if erro:
        attrs.append('aria-invalid="true"')
    if limite:
        attrs.append(f'data-limit="{limite}" data-counter="{cid}-count"')
    if readonly:
        attrs.append('readonly')
    if disabled:
        attrs.append('disabled')
    if sim:
        attrs.append(f'style="--_border-state: var(--al-textarea-border-{sim})"')

    linha = [f'<label class="al-textarea__label" id="{cid}-label" for="{cid}">{rotulo}</label>']
    if opcional:
        linha.append('<span class="al-textarea__optional">(Opcional)</span>')
    if limite:
        n = len(valor)
        acima = ' data-over-limit' if n > limite else ''
        linha.append(f'<span class="al-textarea__counter" id="{cid}-count" '
                     f'aria-live="off"{acima}>{n}/{limite}</span>')

    mensagem = erro or apoio
    apoio_html = (f'\n      <p class="al-textarea__help" id="{cid}-help">{mensagem}</p>'
                  if mensagem else '')

    return f'''<div class="al-textarea">
      <div class="al-textarea__labelrow">
        {(chr(10) + "        ").join(linha)}
      </div>
      <textarea {" ".join(attrs)}>{valor}</textarea>{apoio_html}
    </div>'''


LONGO = ('O pedido chegou com a caixa amassada e dois itens soltos. Um deles, o '
         'copo de vidro, veio trincado na borda. Entrei em contato pelo chat no '
         'mesmo dia e me pediram fotos, que enviei. Desde entao nao tive retorno, '
         'e o prazo de troca termina na sexta-feira.')

# (titulo, origem, nota, kwargs)
ESTADOS = [
    ('Default', 'real', 'o repouso. A borda aqui é a exceção de contraste declarada.',
     dict(cid='st-default', rotulo='Descrição do problema', placeholder='O que aconteceu e quando')),
    ('Hover', 'simulado',
     'só existe sob o ponteiro, então a variável privada do componente foi escrita direto.',
     dict(cid='st-hover', rotulo='Descrição do problema', placeholder='O que aconteceu e quando', sim='hover')),
    ('Focus', 'real',
     'clique OU tabule: o anel laranja aparece nos dois casos. Não existe Active.',
     dict(cid='st-focus', rotulo='Descrição do problema', placeholder='O que aconteceu e quando')),
    ('Error', 'real',
     'vem de aria-invalid="true" na marcação. A mensagem é obrigatória.',
     dict(cid='st-error', rotulo='Descrição do problema', valor='Veio quebrado',
          erro='Conte o que aconteceu e quando, em pelo menos 20 caracteres')),
    ('Focus + Error', 'real',
     'tabule até aqui: o anel tem que vir vinho, não laranja.',
     dict(cid='st-focuserror', rotulo='Descrição do problema', valor='Veio quebrado',
          erro='Conte o que aconteceu e quando, em pelo menos 20 caracteres')),
    ('Disabled', 'real',
     'o Tab pula este campo, e o canto não tem puxador.',
     dict(cid='st-disabled', rotulo='Observações', opcional=True,
          placeholder='Liberado depois do envio', disabled=True)),
    ('Read-only', 'real',
     'o Tab chega aqui; role com as setas, selecione e copie. O puxador continua. O hover não muda a borda.',
     dict(cid='st-readonly', rotulo='Relato original', valor=LONGO, readonly=True)),
    ('Read-only vazio', 'real',
     'regra 24: mostra "—". Placeholder aqui não apareceria de qualquer jeito.',
     dict(cid='st-readonly-empty', rotulo='Resposta do suporte', valor='—', readonly=True)),
    ('Texto longo, 3 linhas', 'real',
     'o texto passa da altura: o campo rola, não cresce. Puxe o canto para baixo.',
     dict(cid='st-scroll', rotulo='Descrição do problema', valor=LONGO)),
    ('rows="6"', 'real',
     'regra 10: o formulário pede mais linhas quando a resposta esperada é longa. 6 linhas = 168px.',
     dict(cid='st-rows6', rotulo='Relato completo', rows=6, placeholder='Descreva com detalhes')),
    ('Contador acima do limite', 'real',
     'digite ou apague: passou de 80, o contador fica vermelho; o campo NÃO trava.',
     dict(cid='st-over', rotulo='Resumo', valor=LONGO[:96], limite=80)),
]


def build():
    css_inline = '\n'.join(
        f'/* ================= {nome} ================= */\n' + open(p, encoding='utf-8').read()
        for nome, p in CSS_FILES)

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
        campo(cid='f-desc', rotulo='Descrição do problema', placeholder='O que aconteceu e quando',
              apoio='Inclua o número do pedido, se tiver'),
        campo(cid='f-motivo', rotulo='Motivo da troca', valor='Não serviu',
              erro='Conte o motivo em pelo menos 20 caracteres'),
        campo(cid='f-obs', rotulo='Observações para a entrega', opcional=True, limite=140,
              apoio='Portaria, horário, ponto de referência'),
        campo(cid='f-relato', rotulo='Relato original', valor=LONGO, readonly=True),
        campo(cid='f-resposta', rotulo='Resposta do suporte', disabled=True,
              placeholder='Liberada depois do envio'),
    ])

    meta = TA['meta']
    n_contraste = len(TA['contrast'])
    n_exc = len([r for r in TA['contrast'] if not r['pass']])

    return f'''<meta charset="utf-8">
<title>AL Textarea QA</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap">
<style>
{css_inline}

/* ================= cromo da pagina de QA =================
   Usa os proprios tokens do AL, sem paleta paralela. */
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
  grid-template-columns: repeat(auto-fill, minmax(min(280px, 100%), 1fr));
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
  grid-template-columns: repeat(auto-fit, minmax(min(260px, 100%), 1fr));
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
      <h1>Textarea — QA da etapa 6</h1>
      <p class="qa-sub">AL Design System {FOUND['meta']['version']} · componente {meta['version']} ·
      &lt;textarea&gt; nativo · {n_contraste} medições de contraste, {n_exc} exceções declaradas, 0 reprovas</p>
    </div>
    <button type="button" class="qa-theme" id="theme-toggle" aria-pressed="false">
      <span id="theme-label">Tema claro</span>
    </button>
  </header>

  <section>
    <h2>O que testar</h2>
    <ol class="qa-checks">
      <li><strong>Tabule pelo formulário.</strong> Os campos recebem foco na ordem visual; o <strong>Relato original</strong> (read-only) recebe foco, a <strong>Resposta do suporte</strong> (desabilitada) é pulada.</li>
      <li><strong>Clique num campo com o mouse.</strong> O anel laranja aparece também no clique — não há estado Active.</li>
      <li><strong>Enter quebra a linha</strong> dentro de qualquer campo e nunca envia o formulário.</li>
      <li><strong>Motivo da troca</strong> está em erro: focado, o anel tem que ser vinho.</li>
      <li><strong>Puxe o canto</strong> de um campo: ele cresce só para baixo, nunca para o lado, e não encolhe abaixo de 3 linhas. A borda acompanha.</li>
      <li><strong>Relato original:</strong> tabule até ele e role o texto com as setas; selecione e copie. A borda não muda no hover.</li>
      <li><strong>Observações:</strong> digite mais de 140 caracteres. O contador fica vermelho e o campo continua aceitando texto.</li>
      <li><strong>Troque o tema</strong> no botão acima: o puxador e a barra de rolagem têm que acompanhar o tema (correção da Foundation nesta etapa). Refaça os itens 2, 4 e 6.</li>
      <li><strong>Reduza a janela</strong> até a largura de telefone: os campos esticam, nada corta.</li>
    </ol>
  </section>

  <section>
    <h2>Os estados</h2>
    <p class="qa-lede">Os sete estados do Figma, mais quatro casos que só existem no código: read-only
    vazio, texto longo rolando, <code>rows="6"</code> e contador acima do limite. O Hover escreve
    direto na variável privada que o próprio <code>textarea.css</code> usa; os demais são reais.</p>
    <div class="qa-grid">
    {chr(10).join('    ' + c for c in cards)}
    </div>
  </section>

  <section>
    <h2>Formulário real</h2>
    <p class="qa-lede">Cinco campos numa mesma tela, do jeito que o componente vai viver. É aqui que a
    ordem de tabulação, o read-only, o Enter e o contador se provam.</p>
    <form class="qa-form" id="qa-form" onsubmit="return false">
      {formulario}
    </form>
  </section>

  <section>
    <h2>Contraste medido no navegador</h2>
    <p class="qa-lede">Não são os números do <code>tokens.json</code>: o script lê a cor que o
    navegador realmente pintou, com <code>getComputedStyle</code>, depois de esperar a transição
    terminar.</p>
    <div class="qa-tablewrap">
      <table class="qa-measure">
        <thead><tr><th>papel</th><th>frente</th><th>fundo</th><th>medido</th><th>piso</th><th>veredito</th></tr></thead>
        <tbody id="measure-body"></tbody>
      </table>
    </div>
  </section>

  <section>
    <h2>Geometria medida no navegador</h2>
    <p class="qa-lede">Altura e redimensionamento lidos do que o navegador calculou. A altura vem de
    <code>rows</code>; o piso de 3 linhas segura até um <code>rows="2"</code> escrito por engano (esse campo é criado
    pelo script só para medir e removido em seguida - não faz parte da página).</p>
    <div class="qa-tablewrap">
      <table class="qa-measure">
        <thead><tr><th>caso</th><th>esperado</th><th>medido</th><th>veredito</th></tr></thead>
        <tbody id="geo-body"></tbody>
      </table>
    </div>
  </section>

  <p class="qa-foot">Gerado por <code>components/textarea/qa.py</code> a partir do CSS commitado em
  <code>dev</code>. <code>al-foundation.css</code>, <code>al-textarea-tokens.css</code> e
  <code>textarea.css</code> estão embutidos como estão no repositório.</p>
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
    // 350ms de folga para a transicao de 120ms terminar
    setTimeout(function () {{ medir(); geometria(); }}, 350);
  }});
  pintarBotao();

  // ------------------------------------------------------------ contador
  // O que a aplicacao faria: numero, data-over-limit e aria-live so com foco.
  document.querySelectorAll('.al-textarea__field[data-limit]').forEach(function (campo) {{
    var limite = +campo.dataset.limit;
    var cont = document.getElementById(campo.dataset.counter);
    function atualizar() {{
      var n = campo.value.length;
      cont.textContent = n + '/' + limite;
      if (n > limite) cont.setAttribute('data-over-limit', '');
      else cont.removeAttribute('data-over-limit');
    }}
    campo.addEventListener('input', atualizar);
    campo.addEventListener('focus', function () {{ cont.setAttribute('aria-live', 'polite'); }});
    campo.addEventListener('blur', function () {{ cont.setAttribute('aria-live', 'off'); }});
    atualizar();
  }});

  // ---------------------------------------------------------- contraste
  function rgb(str) {{
    var m = str.match(/-?[\\d.]+/g);
    return m ? [ +m[0], +m[1], +m[2] ] : null;
  }}
  function lin(c) {{ c /= 255; return c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4); }}
  function lum(c) {{ return 0.2126 * lin(c[0]) + 0.7152 * lin(c[1]) + 0.0722 * lin(c[2]); }}
  function cr(a, b) {{
    var la = lum(a), lb = lum(b);
    return (Math.max(la, lb) + 0.05) / (Math.min(la, lb) + 0.05);
  }}
  function corDe(el, prop, pseudo) {{ return rgb(getComputedStyle(el, pseudo || null)[prop]); }}
  function $(s) {{ return document.querySelector(s); }}
  function el(id) {{ return document.getElementById(id); }}

  var TXT = 4.5, GRAF = 3.0;

  function alvos() {{
    var form = corDe(el('qa-form'), 'backgroundColor');
    var fundo = corDe(el('f-desc'), 'backgroundColor');
    var fundoRo = corDe(el('f-relato'), 'backgroundColor');
    var fundoOff = corDe(el('f-resposta'), 'backgroundColor');
    var over = el('st-over-count');
    var overFundo = corDe(over.closest('.qa-card'), 'backgroundColor');
    return [
      ['rótulo',                corDe(el('f-desc-label'), 'color'),           form,     TXT,  false],
      ['rótulo em erro',        corDe(el('f-motivo-label'), 'color'),         form,     TXT,  false],
      ['marca (Opcional)',      corDe($('#qa-form .al-textarea__optional'), 'color'), form, TXT, false],
      ['contador',              corDe(el('f-obs-count'), 'color'),            form,     TXT,  false],
      ['contador acima do limite', corDe(over, 'color'),                      overFundo, TXT, false],
      ['texto de apoio',        corDe(el('f-desc-help'), 'color'),            form,     TXT,  false],
      ['mensagem de erro',      corDe(el('f-motivo-help'), 'color'),          form,     TXT,  false],
      ['placeholder',           corDe(el('f-desc'), 'color', '::placeholder'), fundo,   TXT,  false],
      ['valor',                 corDe(el('f-motivo'), 'color'),               fundo,    TXT,  false],
      ['valor read-only',       corDe(el('f-relato'), 'color'),               fundoRo,  TXT,  false],
      ['borda em repouso',      corDe(el('f-desc'), 'borderTopColor'),        form,     GRAF, true],
      ['borda em erro',         corDe(el('f-motivo'), 'borderTopColor'),      form,     GRAF, false],
      ['borda read-only',       corDe(el('f-relato'), 'borderTopColor'),      form,     GRAF, true],
      ['texto desabilitado',    corDe(el('f-resposta'), 'color', '::placeholder'), fundoOff, TXT, true],
    ];
  }}

  function geometria() {{
    var corpo = el('geo-body');
    corpo.textContent = '';
    function h(id) {{ return Math.round(el(id).getBoundingClientRect().height); }}
    function rz(id) {{ return getComputedStyle(el(id)).resize; }}
    // rows=2 de proposito, fora da marcacao: o a11y.py recusaria (regra h).
    var sonda = document.createElement('textarea');
    sonda.className = 'al-textarea__field';
    sonda.rows = 2;
    sonda.setAttribute('aria-hidden', 'true');
    sonda.tabIndex = -1;
    sonda.style.cssText = 'position:absolute; left:-9999px; width:300px';
    document.body.appendChild(sonda);
    var h2 = Math.round(sonda.getBoundingClientRect().height);
    sonda.remove();
    [
      ['rows="3" (Default)',       '96px',     h('st-default') + 'px'],
      ['rows="6"',                 '168px',    h('st-rows6') + 'px'],
      ['rows="2" (piso de 3)',     '96px',     h2 + 'px'],
      ['resize no Default',        'vertical', rz('st-default')],
      ['resize no Read-only',      'vertical', rz('st-readonly')],
      ['resize no Disabled',       'none',     rz('st-disabled')],
      ['texto longo rola',         'sim',      el('st-scroll').scrollHeight > el('st-scroll').clientHeight ? 'sim' : 'não'],
      ['color-scheme da página',   escuro() ? 'dark' : 'light',
        (getComputedStyle(root).colorScheme.indexOf('dark') >= 0 && getComputedStyle(root).colorScheme.indexOf('light') >= 0)
          ? (escuro() ? 'dark' : 'light') + ' (do sistema)' : getComputedStyle(root).colorScheme]
    ].forEach(function (l) {{
      var ok = l[2].indexOf(l[1]) === 0;
      var tr = document.createElement('tr');
      [l[0], l[1], l[2]].forEach(function (v) {{
        var td = document.createElement('td'); td.textContent = v; tr.appendChild(td);
      }});
      var td = document.createElement('td');
      td.textContent = ok ? 'passa' : 'REPROVA';
      td.className = 'qa-verdict qa-verdict--' + (ok ? 'ok' : 'bad');
      tr.appendChild(td);
      corpo.appendChild(tr);
    }});
  }}

  function medir() {{
    var corpo = document.getElementById('measure-body');
    corpo.textContent = '';
    alvos().forEach(function (l) {{
      var nome = l[0], fg = l[1], bg = l[2], piso = l[3], exc = l[4];
      if (!fg || !bg) return;
      var r = cr(fg, bg), passa = r >= piso;
      var classe = passa ? 'ok' : (exc ? 'exc' : 'bad');
      var tr = document.createElement('tr');
      [nome, 'rgb(' + fg.join(', ') + ')', 'rgb(' + bg.join(', ') + ')',
       r.toFixed(2) + ':1', piso.toFixed(1) + ':1'].forEach(function (v) {{
        var td = document.createElement('td'); td.textContent = v; tr.appendChild(td);
      }});
      var td = document.createElement('td');
      td.textContent = passa ? 'passa' : (exc ? 'exceção declarada' : 'REPROVA');
      td.className = 'qa-verdict qa-verdict--' + classe;
      tr.appendChild(td);
      corpo.appendChild(tr);
    }});
  }}

  if (document.fonts && document.fonts.ready) {{
    document.fonts.ready.then(function () {{ setTimeout(function () {{ medir(); geometria(); }}, 50); }});
  }} else {{
    setTimeout(function () {{ medir(); geometria(); }}, 200);
  }}
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function () {{
    pintarBotao(); setTimeout(function () {{ medir(); geometria(); }}, 350);
  }});
}})();
</script>
'''


if __name__ == '__main__':
    html = build()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, 'w', encoding='utf-8').write(html)
    print(f'site/textarea-qa.html escrito ({len(html)} bytes)')
    print(f'  CSS embutido: {", ".join(n for n, _ in CSS_FILES)}')
    corpo = re.sub(r'<style\b[^>]*>.*?</style>', '', html, flags=re.S)
    n = len(re.findall(r'<textarea\b[^>]*al-textarea__field', corpo))
    print(f'  campos de verdade no documento: {n}  '
          f'({len(ESTADOS)} cartoes de estado + 5 do formulario)')
