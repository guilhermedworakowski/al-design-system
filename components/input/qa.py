"""
Gera a visualizacao de QA do Input (etapa 6) em site/input-qa.html.

Mesmo arranjo do Select: a pagina INLINA os arquivos de CSS reais do
repositorio - foundation, tokens do Input e input.css. Ela nao pode divergir do
codigo porque ela E o codigo; mexer no input.css e rodar este script de novo
basta.

O a11y.py ao lado le o HTML que este script emite e cobra ali o contrato de
marcacao.

O CONTADOR PRECISA DE JAVASCRIPT, E ELE MORA AQUI
  O limite nao trava a digitacao (regra 14, sem `maxlength`), entao o
  navegador nao sabe quando passou. O script da pagina faz o que a aplicacao
  que consome o AL faria: atualiza "n/limite", liga `data-over-limit` quando
  passa, e troca `aria-live` entre `polite` (com foco) e `off` (sem foco) -
  regra 30, solucao do Polaris.

Rodar: python3 qa.py     (escreve o proprio arquivo; nunca redirecionar stdout)
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(ROOT, 'site', 'input-qa.html')

FOUND = json.load(open(os.path.join(ROOT, 'tokens.json')))
INPUT = json.load(open(os.path.join(HERE, 'tokens.json')))

CSS_FILES = [
    ('foundation', os.path.join(ROOT, 'foundation', 'al-foundation.css')),
    ('input - tokens', os.path.join(HERE, 'al-input-tokens.css')),
    ('input', os.path.join(HERE, 'input.css')),
]


def campo(cid, rotulo, *, tipo='text', opcional=False, apoio=None, erro=None,
          disabled=False, readonly=False, valor=None, placeholder=None,
          prefixo=None, sufixo=None, limite=None, autocomplete=None, sim=None):
    """Um Input completo. `sim` forca o hover escrevendo na MESMA variavel
    privada que o input.css usa - e o proprio mecanismo do componente, nao um
    estilo paralelo."""
    attrs = [f'class="al-input__field"', f'id="{cid}"', f'name="{cid}"', f'type="{tipo}"']
    if autocomplete:
        attrs.append(f'autocomplete="{autocomplete}"')
    if valor is not None:
        attrs.append(f'value="{valor}"')
    if placeholder and not readonly:
        attrs.append(f'placeholder="{placeholder}"')
    if prefixo or sufixo:
        nomes = [f'{cid}-label']
        if prefixo:
            nomes.append(f'{cid}-prefix')
        if sufixo:
            nomes.append(f'{cid}-suffix')
        attrs.append(f'aria-labelledby="{" ".join(nomes)}"')
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

    linha = [f'<label class="al-input__label" id="{cid}-label" for="{cid}">{rotulo}</label>']
    if opcional:
        linha.append('<span class="al-input__optional">(Opcional)</span>')
    if limite:
        n = len(valor or '')
        acima = ' data-over-limit' if n > limite else ''
        linha.append(f'<span class="al-input__counter" id="{cid}-count" '
                     f'aria-live="off"{acima}>{n}/{limite}</span>')

    caixa = []
    if prefixo:
        caixa.append(f'<label class="al-input__affix" id="{cid}-prefix" for="{cid}">{prefixo}</label>')
    caixa.append(f'<input {" ".join(attrs)}>')
    if sufixo:
        caixa.append(f'<label class="al-input__affix" id="{cid}-suffix" for="{cid}">{sufixo}</label>')

    estilo = f' style="--_border-state: var(--al-input-border-{sim})"' if sim else ''
    mensagem = erro or apoio
    apoio_html = (f'\n      <p class="al-input__help" id="{cid}-help">{mensagem}</p>'
                  if mensagem else '')

    return f'''<div class="al-input">
      <div class="al-input__labelrow">
        {(chr(10) + "        ").join(linha)}
      </div>
      <div class="al-input__control"{estilo}>
        {(chr(10) + "        ").join(caixa)}
      </div>{apoio_html}
    </div>'''


# (titulo, origem, nota, kwargs)
ESTADOS = [
    ('Default', 'real', 'o repouso. A borda aqui é a exceção de contraste declarada.',
     dict(cid='st-default', rotulo='E-mail', tipo='email', placeholder='nome@empresa.com')),
    ('Hover', 'simulado',
     'só existe sob o ponteiro, então a variável privada do componente foi escrita direto.',
     dict(cid='st-hover', rotulo='E-mail', tipo='email', placeholder='nome@empresa.com', sim='hover')),
    ('Focus', 'real',
     'clique OU tabule: o anel laranja aparece nos dois casos. Não existe Active.',
     dict(cid='st-focus', rotulo='E-mail', tipo='email', placeholder='nome@empresa.com')),
    ('Error', 'real',
     'vem de aria-invalid="true" na marcação. A mensagem é obrigatória.',
     dict(cid='st-error', rotulo='E-mail', tipo='email', valor='nome@empresa',
          erro='Use um e-mail no formato nome@empresa.com')),
    ('Focus + Error', 'real',
     'tabule até aqui: o anel tem que vir vinho, não laranja.',
     dict(cid='st-focuserror', rotulo='E-mail', tipo='email', valor='nome@empresa',
          erro='Use um e-mail no formato nome@empresa.com')),
    ('Disabled', 'real',
     'atributo disabled nativo: o Tab pula este campo sozinho.',
     dict(cid='st-disabled', rotulo='E-mail', tipo='email', opcional=True,
          placeholder='nome@empresa.com', disabled=True)),
    ('Read-only', 'real',
     'o Tab chega aqui e dá para selecionar e copiar. O hover não escurece a borda.',
     dict(cid='st-readonly', rotulo='CPF', valor='123.456.789-09', readonly=True)),
    ('Read-only vazio', 'real',
     'regra 22: mostra "—" como valor. Placeholder aqui não apareceria de qualquer jeito.',
     dict(cid='st-readonly-empty', rotulo='Inscrição estadual', valor='—', readonly=True)),
    ('Prefixo + sufixo', 'real',
     'clique em "www." ou ".com": o cursor vai para o campo. O leitor de tela lê "Site, www., .com".',
     dict(cid='st-affix', rotulo='Site', tipo='url', opcional=True, prefixo='www.',
          sufixo='.com', placeholder='empresa')),
    ('Contador acima do limite', 'real',
     'digite ou apague: passou de 20, o contador fica vermelho; o campo NÃO trava.',
     dict(cid='st-over', rotulo='Apelido', valor='Maria Eduarda Albuquerque', limite=20)),
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
        campo(cid='f-nome', rotulo='Nome completo', autocomplete='name',
              apoio='Como aparece no documento'),
        campo(cid='f-email', rotulo='E-mail', tipo='email', autocomplete='email',
              placeholder='nome@empresa.com'),
        campo(cid='f-site', rotulo='Site', tipo='url', opcional=True,
              prefixo='www.', sufixo='.com', placeholder='empresa'),
        campo(cid='f-tel', rotulo='Telefone', tipo='tel', autocomplete='tel',
              valor='1199', erro='Use DDD e número, como 11 91234-5678'),
        campo(cid='f-bio', rotulo='Descrição curta', opcional=True, limite=40,
              apoio='Aparece no seu perfil'),
        campo(cid='f-cpf', rotulo='CPF', valor='123.456.789-09', readonly=True),
        campo(cid='f-empresa', rotulo='Empresa', disabled=True,
              placeholder='Preenchida pelo convite'),
    ])

    meta = INPUT['meta']
    n_contraste = len(INPUT['contrast'])
    n_exc = len([r for r in INPUT['contrast'] if not r['pass']])

    return f'''<meta charset="utf-8">
<title>AL Input QA</title>
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
      <h1>Input — QA da etapa 6</h1>
      <p class="qa-sub">AL Design System {FOUND['meta']['version']} · componente {meta['version']} ·
      &lt;input&gt; nativo · {n_contraste} medições de contraste, {n_exc} exceções declaradas, 0 reprovas</p>
    </div>
    <button type="button" class="qa-theme" id="theme-toggle" aria-pressed="false">
      <span id="theme-label">Tema claro</span>
    </button>
  </header>

  <section>
    <h2>O que testar</h2>
    <ol class="qa-checks">
      <li><strong>Tabule pelo formulário.</strong> Os campos recebem foco na ordem visual; o <strong>CPF</strong> (read-only) recebe foco, a <strong>Empresa</strong> (desabilitada) é pulada.</li>
      <li><strong>Clique num campo com o mouse.</strong> O anel laranja aparece também no clique — é o comportamento certo, não há estado Active.</li>
      <li><strong>Telefone</strong> está em erro: focado, o anel tem que ser vinho.</li>
      <li><strong>Site:</strong> clique em “www.” ou “.com” — o cursor vai para o campo.</li>
      <li><strong>Descrição curta:</strong> digite mais de 40 caracteres. O contador fica vermelho e o campo continua aceitando texto.</li>
      <li><strong>CPF:</strong> passe o mouse (a borda não muda), tabule até ele e selecione o texto para copiar.</li>
      <li><strong>Troque o tema</strong> no botão acima e refaça os itens 2, 3 e 6.</li>
      <li><strong>Reduza a janela</strong> até a largura de telefone: os campos esticam, nada corta.</li>
    </ol>
  </section>

  <section>
    <h2>Os estados</h2>
    <p class="qa-lede">Os sete estados do Figma, mais três casos que só existem no código: read-only
    vazio, prefixo com sufixo e contador acima do limite. O Hover escreve direto na variável privada
    que o próprio <code>input.css</code> usa; os demais são reais.</p>
    <div class="qa-grid">
    {chr(10).join('    ' + c for c in cards)}
    </div>
  </section>

  <section>
    <h2>Formulário real</h2>
    <p class="qa-lede">Sete campos numa mesma tela, do jeito que o componente vai viver. É aqui que a
    ordem de tabulação, o read-only e o contador se provam.</p>
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

  <p class="qa-foot">Gerado por <code>components/input/qa.py</code> a partir do CSS commitado em
  <code>dev</code>. <code>al-foundation.css</code>, <code>al-input-tokens.css</code> e
  <code>input.css</code> estão embutidos como estão no repositório.</p>
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
    setTimeout(medir, 350);
  }});
  pintarBotao();

  // ------------------------------------------------------------ contador
  // O que a aplicacao faria: numero, data-over-limit e aria-live so com foco.
  document.querySelectorAll('.al-input__field[data-limit]').forEach(function (campo) {{
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
  function caixa(id) {{ return document.getElementById(id).closest('.al-input__control'); }}
  function $(s) {{ return document.querySelector(s); }}

  var TXT = 4.5, GRAF = 3.0;

  function alvos() {{
    var form = corDe(document.getElementById('qa-form'), 'backgroundColor');
    var fundo = corDe(caixa('f-email'), 'backgroundColor');
    var fundoRo = corDe(caixa('f-cpf'), 'backgroundColor');
    var fundoOff = corDe(caixa('f-empresa'), 'backgroundColor');
    var over = document.getElementById('st-over-count');
    var overFundo = corDe(over.closest('.qa-card'), 'backgroundColor');
    return [
      ['rótulo',                corDe($('#f-nome-label'), 'color'),            form,     TXT,  false],
      ['rótulo em erro',        corDe($('#f-tel-label'), 'color'),             form,     TXT,  false],
      ['marca (Opcional)',      corDe($('#qa-form .al-input__optional'), 'color'), form, TXT,  false],
      ['contador',              corDe(document.getElementById('f-bio-count'), 'color'), form, TXT, false],
      ['contador acima do limite', corDe(over, 'color'),                       overFundo, TXT, false],
      ['texto de apoio',        corDe($('#f-nome-help'), 'color'),             form,     TXT,  false],
      ['mensagem de erro',      corDe($('#f-tel-help'), 'color'),              form,     TXT,  false],
      ['placeholder',           corDe($('#f-email'), 'color', '::placeholder'), fundo,   TXT,  false],
      ['valor',                 corDe($('#f-tel'), 'color'),                   fundo,    TXT,  false],
      ['prefixo',               corDe($('#f-site-prefix'), 'color'),           fundo,    TXT,  false],
      ['valor read-only',       corDe($('#f-cpf'), 'color'),                   fundoRo,  TXT,  false],
      ['borda em repouso',      corDe(caixa('f-email'), 'borderTopColor'),     form,     GRAF, true],
      ['borda em erro',         corDe(caixa('f-tel'), 'borderTopColor'),       form,     GRAF, false],
      ['borda read-only',       corDe(caixa('f-cpf'), 'borderTopColor'),       form,     GRAF, true],
      ['texto desabilitado',    corDe($('#f-empresa'), 'color', '::placeholder'), fundoOff, TXT, true],
    ];
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
    print(f'site/input-qa.html escrito ({len(html)} bytes)')
    print(f'  CSS embutido: {", ".join(n for n, _ in CSS_FILES)}')
    corpo = re.sub(r'<style\b[^>]*>.*?</style>', '', html, flags=re.S)
    n = len(re.findall(r'<input\b[^>]*al-input__field', corpo))
    print(f'  campos de verdade no documento: {n}  '
          f'({len(ESTADOS)} cartoes de estado + 7 do formulario)')
