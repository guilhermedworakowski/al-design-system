"""
Gera a visualizacao de QA do Checkbox (etapa 6) em site/checkbox-qa.html.

Mesmo arranjo do Select: a pagina INLINA os arquivos de CSS reais do
repositorio - foundation, icon, tokens do Checkbox e checkbox.css. Ela nao pode
divergir do codigo porque ela E o codigo. Os dois glifos tambem nao sao
copiados a mao: o `d` de cada path e lido de components/icon/icons/.

O a11y.py ao lado le o HTML que este script emite e cobra ali o contrato de
marcacao.

Rodar: python3 qa.py     (escreve o proprio arquivo; nunca redirecionar stdout)
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(ROOT, 'site', 'checkbox-qa.html')

FOUND = json.load(open(os.path.join(ROOT, 'tokens.json')))
CHECKBOX = json.load(open(os.path.join(HERE, 'tokens.json')))
ICONS = os.path.join(ROOT, 'components', 'icon', 'icons')

CSS_FILES = [
    ('foundation', os.path.join(ROOT, 'foundation', 'al-foundation.css')),
    ('icon - tokens', os.path.join(ROOT, 'components', 'icon', 'al-icon-tokens.css')),
    ('icon', os.path.join(ROOT, 'components', 'icon', 'icon.css')),
    ('checkbox - tokens', os.path.join(HERE, 'al-checkbox-tokens.css')),
    ('checkbox', os.path.join(HERE, 'checkbox.css')),
]


def glifo(nome, classe):
    """SVG inline de um icone da Foundation, com o contrato decorativo."""
    src = open(os.path.join(ICONS, f'{nome}.svg'), encoding='utf-8').read()
    paths = ''.join(re.findall(r'<path\b[^>]*/>', src))
    return (f'<svg class="al-icon {classe}" viewBox="0 0 24 24" fill="none" '
            f'stroke="currentColor" stroke-width="2" stroke-linecap="round" '
            f'stroke-linejoin="round" aria-hidden="true" focusable="false">{paths}</svg>')


CHECK = glifo('check', 'al-checkbox__check')
DASH = glifo('minus', 'al-checkbox__dash')


def caixa(cid, rotulo, *, checked=False, indeterminate=False, disabled=False,
          erro=None, sim=None, extra=''):
    """Um Checkbox completo.

    `indeterminate` NAO vira atributo - ele nao existe em HTML. Vira
    `data-indeterminate`, e o script da pagina faz `el.indeterminate = true`,
    exatamente como a regra 8 manda.

    `sim` forca o hover, que so existe sob o ponteiro, escrevendo nas MESMAS
    variaveis privadas que o checkbox.css usa - nao e estilo paralelo."""
    attrs = [f'id="{cid}"', 'class="al-checkbox__input"', 'type="checkbox"', f'name="{cid}"']
    if checked:
        attrs.append('checked')
    if disabled:
        attrs.append('disabled')
    if indeterminate:
        attrs.append('data-indeterminate')
    if erro:
        attrs.append('aria-invalid="true"')
        attrs.append(f'aria-describedby="{erro}"')
    if sim == 'hover':
        attrs.append('style="--_bg-state: var(--al-checkbox-bg-hover); '
                     '--_border-state: var(--al-checkbox-border-hover)"')
    if extra:
        attrs.append(extra)
    return (f'<label class="al-checkbox">'
            f'<span class="al-checkbox__control"><input {" ".join(attrs)}>{CHECK}{DASH}</span>'
            f'<span class="al-checkbox__label">{rotulo}</span></label>')


# (titulo, origem, nota, html do cartao)
# origem: real = interaja; simulado = so existe sob o ponteiro; codigo = sem
# variante no Figma, pintado pelo checkbox.css com os tokens aprovados na etapa 3.
ESTADOS = [
    ('Default', 'real', 'o repouso. A borda aqui é a exceção de contraste declarada (1,57:1).',
     caixa('st-default', 'Receber novidades por e-mail')),
    ('Hover', 'simulado', 'só existe sob o ponteiro; a variável privada do componente foi escrita direto. '
     'Passe o mouse nos outros cartões para ver o real — vale na linha inteira.',
     caixa('st-hover', 'Receber novidades por e-mail', sim='hover')),
    ('Active (marcado)', 'real', 'clique para desmarcar e marcar de novo. O check é o ícone check da Foundation.',
     caixa('st-checked', 'Receber novidades por e-mail', checked=True)),
    ('Indeterminate', 'real', 'aplicado por JavaScript (input.indeterminate = true) — não existe atributo HTML. '
     'Clicar tira o misto, como no nativo.',
     caixa('st-indet', 'Todas as notificações', indeterminate=True)),
    ('Focus', 'real', 'tabule até aqui: anel laranja com respiro. Clique com o mouse: sem anel.',
     caixa('st-focus', 'Receber novidades por e-mail')),
    ('Error', 'real', 'vem de aria-invalid="true". A mensagem abaixo é do formulário, não do componente (regra 19).',
     caixa('st-error', 'Li e aceito os termos de uso', erro='st-error-msg')
     + '<p class="qa-formerror" id="st-error-msg">Aceite os termos para continuar.</p>'),
    ('Disabled', 'real', 'atributo disabled nativo: o Tab pula sozinho. Contraste abaixo de AA de propósito.',
     caixa('st-disabled', 'Receber novidades por e-mail', disabled=True)),
]

COMBINADOS = [
    ('Marcado + disabled', 'codigo', 'caixa cinza, check em icon-disabled — o único token sem variante no Figma.',
     caixa('cb-dischk', 'Alertas de segurança', checked=True, disabled=True)),
    ('Erro + marcado', 'codigo', 'a caixa segue laranja; só o rótulo avisa. Desmarque: a borda fica vermelha.',
     caixa('cb-errchk', 'Li e aceito os termos de uso', checked=True, erro='cb-errchk-msg')
     + '<p class="qa-formerror" id="cb-errchk-msg">Revise o aceite antes de enviar.</p>'),
    ('Marcado + foco', 'codigo', 'tabule até aqui: o anel aparece por cima da caixa laranja.',
     caixa('cb-chkfoc', 'Receber novidades por e-mail', checked=True)),
    ('Rótulo longo', 'real', 'o texto quebra alinhado ao topo da caixa, não centralizado nela (regra 11).',
     caixa('cb-long', 'Quero receber o resumo semanal com as notas emitidas, os pagamentos '
                      'recebidos e os lembretes de vencimento da semana seguinte')),
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


def build():
    css = []
    for nome, path in CSS_FILES:
        css.append(f'/* ================= {nome} ================= */')
        css.append(open(path, encoding='utf-8').read())
    css_inline = '\n'.join(css)

    cards = '\n    '.join(cartao(*e) for e in ESTADOS)
    combos = '\n    '.join(cartao(*e) for e in COMBINADOS)

    filhos = [('f-mail', 'E-mail', True), ('f-sms', 'SMS', True), ('f-push', 'Notificação no celular', False)]
    lista_filhos = '\n          '.join(
        caixa(cid, rot, checked=chk, extra='data-filho') for cid, rot, chk in filhos)

    meta = CHECKBOX['meta']
    rows = CHECKBOX['contrast']
    n_exc = len([r for r in rows if not r['pass']])

    return f'''<title>AL Checkbox QA</title>
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
.qa-formerror {{ margin: 0; color: var(--al-text-danger); font-size: var(--al-font-size-sm); line-height: var(--al-line-height-sm); }}
.qa-form {{
  display: flex; flex-direction: column; gap: var(--al-space-24);
  padding: var(--al-space-24);
  border: 1px solid var(--al-border-subtle); border-radius: var(--al-radius-xl);
  background: var(--al-bg-surface-raised);
  max-width: 560px;
}}
.qa-form fieldset {{ margin: 0; padding: 0; border: 0; display: flex; flex-direction: column; gap: var(--al-space-12); min-width: 0; }}
.qa-form legend {{ padding: 0; margin-bottom: var(--al-space-12); font-weight: 600; }}
.qa-children {{ display: flex; flex-direction: column; gap: var(--al-space-12); padding-inline-start: var(--al-space-32); }}
.qa-summary {{
  margin: 0; padding: var(--al-space-12) var(--al-space-16);
  border-radius: var(--al-radius-md);
  background: var(--al-bg-danger-subtle); color: var(--al-text-danger);
  font-size: var(--al-font-size-sm); line-height: var(--al-line-height-sm);
}}
.qa-ok {{ margin: 0; color: var(--al-text-success); font-size: var(--al-font-size-sm); }}
.qa-actions {{ display: flex; gap: var(--al-space-12); flex-wrap: wrap; align-items: center; }}
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
@media (prefers-reduced-motion: reduce) {{ * {{ transition: none !important; }} }}
</style>

<div class="qa-wrap">
  <header class="qa-head">
    <div>
      <h1>Checkbox — QA da etapa 6</h1>
      <p class="qa-sub">AL Design System {FOUND['meta']['version']} · componente {meta['version']} ·
      &lt;input type="checkbox"&gt; nativo · {len(rows)} medições de token, {n_exc} exceções declaradas, 0 reprovas</p>
    </div>
    <button type="button" class="qa-btn" id="theme-toggle" aria-pressed="false">
      <span id="theme-label">Tema claro</span>
    </button>
  </header>

  <section>
    <h2>O que testar</h2>
    <ol class="qa-checks">
      <li><strong>Tabule pela página.</strong> Cada checkbox recebe foco na ordem visual; os desabilitados são pulados.</li>
      <li><strong>Espaço marca e desmarca</strong> o checkbox focado. Enter não faz nada — é o comportamento nativo.</li>
      <li><strong>O anel só aparece no teclado.</strong> Chegue por Tab: anel laranja. Clique com o mouse: sem anel.</li>
      <li><strong>Clique no texto, não na caixa:</strong> também marca, e o hover acende a linha inteira.</li>
      <li><strong>No formulário, marque e desmarque os filhos</strong> e veja o pai passar por marcado, misto e vazio. Clique no pai misto: marca todos.</li>
      <li><strong>Envie o formulário sem aceitar os termos:</strong> a caixa fica com borda vermelha, o rótulo vermelho, e o erro aparece em texto no topo. Marque o aceite: tudo volta.</li>
      <li><strong>Troque o tema</strong> no botão acima e refaça os itens 3 e 6.</li>
      <li><strong>Reduza a janela</strong> até a largura de telefone: rótulo longo quebra, nada corta.</li>
    </ol>
  </section>

  <section>
    <h2>Os sete estados do Figma</h2>
    <p class="qa-lede">Um cartão por variante do component set. Só o Hover é simulado, porque só existe
    enquanto o ponteiro está em cima — os outros seis são reais: interaja neles.</p>
    <div class="qa-grid">
    {cards}
    </div>
  </section>

  <section>
    <h2>Combinações que só existem no código</h2>
    <p class="qa-lede">O Figma tem um eixo só de estado; o navegador produz combinações que ele não
    desenha. Estas foram decididas na etapa 3 e são pintadas pelos mesmos tokens.</p>
    <div class="qa-grid">
    {combos}
    </div>
  </section>

  <section>
    <h2>Formulário real</h2>
    <p class="qa-lede">Um grupo com pai e filhos (título em <code>fieldset</code> e <code>legend</code>
    nativos, regra 6), uma opção travada pela empresa e um aceite obrigatório. É aqui que a ordem de
    tabulação, o indeterminado e o erro em texto se provam.</p>
    <form class="qa-form" id="qa-form" novalidate>
      <p class="qa-summary" id="form-erro" hidden>Aceite os termos de uso para salvar as preferências.</p>
      <fieldset>
        <legend>Notificações</legend>
        {caixa('f-todas', 'Todas as notificações', extra='data-pai')}
        <div class="qa-children">
          {lista_filhos}
        </div>
        {caixa('f-seguranca', 'Alertas de segurança', checked=True, disabled=True)}
      </fieldset>
      {caixa('f-termos', 'Li e aceito os termos de uso', extra='required')}
      <div class="qa-actions">
        <button type="submit" class="qa-btn qa-btn--primary" id="f-enviar">Salvar preferências</button>
        <p class="qa-ok" id="form-ok" role="status"></p>
      </div>
    </form>
  </section>

  <section>
    <h2>Contraste medido no navegador</h2>
    <p class="qa-lede">Não são os números do <code>tokens.json</code>: o script lê a cor que o navegador
    realmente pintou, com <code>getComputedStyle</code>, depois de esperar a transição terminar — contra o
    fundo onde cada checkbox está de verdade (cartão em <code>bg-surface</code>).</p>
    <div class="qa-tablewrap">
      <table class="qa-measure">
        <thead><tr><th>papel</th><th>frente</th><th>fundo</th><th>medido</th><th>piso</th><th>veredito</th></tr></thead>
        <tbody id="measure-body"></tbody>
      </table>
    </div>
  </section>

  <p class="qa-foot">Gerado por <code>components/checkbox/qa.py</code> a partir do CSS commitado em
  <code>dev</code>. <code>al-foundation.css</code>, <code>icon.css</code>, <code>al-checkbox-tokens.css</code>
  e <code>checkbox.css</code> estão embutidos como estão no repositório; os glifos vêm de
  <code>components/icon/icons/</code>.</p>
</div>

<script>
(function () {{
  var root = document.documentElement;

  // ------------------------------------------------ indeterminado (regra 8)
  // So existe por JS. A marcacao carrega data-indeterminate, nunca o atributo.
  Array.prototype.forEach.call(document.querySelectorAll('[data-indeterminate]'), function (el) {{
    el.indeterminate = true;
  }});

  // ------------------------------------------------------ pai e filhos (7, 8)
  var pai = document.getElementById('f-todas');
  var filhos = Array.prototype.slice.call(document.querySelectorAll('[data-filho]'));
  function sincronizarPai() {{
    var n = filhos.filter(function (f) {{ return f.checked; }}).length;
    pai.checked = n === filhos.length;
    pai.indeterminate = n > 0 && n < filhos.length;
  }}
  filhos.forEach(function (f) {{ f.addEventListener('change', sincronizarPai); }});
  pai.addEventListener('change', function () {{
    // clicar no pai misto marca todos: o navegador ja limpou o indeterminate e
    // ligou o checked, entao basta propagar
    filhos.forEach(function (f) {{ f.checked = pai.checked; }});
    pai.indeterminate = false;
  }});
  sincronizarPai();

  // ------------------------------------------------------ erro em texto (19)
  var form = document.getElementById('qa-form');
  var termos = document.getElementById('f-termos');
  var resumo = document.getElementById('form-erro');
  var ok = document.getElementById('form-ok');
  function limparErro() {{
    termos.setAttribute('aria-invalid', 'false');
    termos.removeAttribute('aria-describedby');
    resumo.hidden = true;
  }}
  form.addEventListener('submit', function (e) {{
    e.preventDefault();
    ok.textContent = '';
    if (!termos.checked) {{
      termos.setAttribute('aria-invalid', 'true');
      termos.setAttribute('aria-describedby', 'form-erro');
      resumo.hidden = false;
      termos.focus();
      return;
    }}
    limparErro();
    ok.textContent = 'Preferências salvas.';
  }});
  termos.addEventListener('change', function () {{ if (termos.checked) limparErro(); }});

  // ------------------------------------------------------------------ tema
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

  // ------------------------------------------------------------- contraste
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
  function cor(el, prop) {{ return rgb(getComputedStyle(el)[prop]); }}
  function caixaDe(id) {{ return document.getElementById(id); }}
  function rotuloDe(id) {{ return caixaDe(id).closest('.al-checkbox').querySelector('.al-checkbox__label'); }}
  function checkDe(id) {{ return caixaDe(id).parentNode.querySelector('.al-checkbox__check'); }}
  function fundoDe(id) {{ return cor(caixaDe(id).closest('.qa-card'), 'backgroundColor'); }}

  var TXT = 4.5, GRA = 3.0;

  function alvos() {{
    return [
      ['rótulo',                cor(rotuloDe('st-default'), 'color'),   fundoDe('st-default'), TXT, false],
      ['rótulo em erro',        cor(rotuloDe('st-error'), 'color'),     fundoDe('st-error'),   TXT, false],
      ['borda em repouso',      cor(caixaDe('st-default'), 'borderTopColor'), fundoDe('st-default'), GRA, true],
      ['borda em erro',         cor(caixaDe('st-error'), 'borderTopColor'),   fundoDe('st-error'),   GRA, false],
      ['caixa marcada',         cor(caixaDe('st-checked'), 'backgroundColor'), fundoDe('st-checked'), GRA, false],
      ['check',                 cor(checkDe('st-checked'), 'color'), cor(caixaDe('st-checked'), 'backgroundColor'), GRA, false],
      ['check desabilitado',    cor(checkDe('cb-dischk'), 'color'),  cor(caixaDe('cb-dischk'), 'backgroundColor'),  GRA, true],
      ['rótulo desabilitado',   cor(rotuloDe('st-disabled'), 'color'), fundoDe('st-disabled'), TXT, true],
    ];
  }}

  function medir() {{
    var corpo = document.getElementById('measure-body');
    corpo.textContent = '';
    alvos().forEach(function (l) {{
      var fg = l[1], bg = l[2];
      if (!fg || !bg) return;
      var r = cr(fg, bg), passa = r >= l[3];
      var classe = passa ? 'ok' : (l[4] ? 'exc' : 'bad');
      var texto = passa ? 'passa' : (l[4] ? 'exceção declarada' : 'REPROVA');
      var tr = document.createElement('tr');
      [l[0], 'rgb(' + fg.join(', ') + ')', 'rgb(' + bg.join(', ') + ')',
       r.toFixed(2) + ':1', l[3].toFixed(1) + ':1'].forEach(function (v) {{
        var td = document.createElement('td'); td.textContent = v; tr.appendChild(td);
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
    print(f'site/checkbox-qa.html escrito ({len(html)} bytes)')
    print(f'  CSS embutido: {", ".join(n for n, _ in CSS_FILES)}')
    corpo = re.sub(r'<style\b[^>]*>.*?</style>', '', html, flags=re.S)
    corpo = re.sub(r'<script\b[^>]*>.*?</script>', '', corpo, flags=re.S)
    n = len(re.findall(r'<input\b[^>]*al-checkbox__input', corpo))
    print(f'  checkboxes de verdade no documento: {n}')
