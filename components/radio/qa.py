"""
Gera a visualizacao de QA do Radio (etapa 6) em site/radio-qa.html.

Mesmo arranjo do Checkbox: a pagina INLINA os arquivos de CSS reais do
repositorio - foundation, tokens do Radio e radio.css. Ela nao pode divergir
do codigo porque ela E o codigo.

TODO CARTAO E UMA PERGUNTA

  Radio sozinho nao existe (regra 3). Entao cada cartao de estado e um
  <fieldset> com <legend> e duas opcoes - a que mostra o estado e uma vizinha
  em repouso. E o que o a11y.py cobra (regras c e d), e e o que faz as setas
  funcionarem dentro de cada cartao.

O a11y.py ao lado le o HTML que este script emite e cobra ali o contrato de
marcacao.

Rodar: python3 qa.py     (escreve o proprio arquivo; nunca redirecionar stdout)
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(ROOT, 'site', 'radio-qa.html')

FOUND = json.load(open(os.path.join(ROOT, 'tokens.json')))
RADIO = json.load(open(os.path.join(HERE, 'tokens.json')))

CSS_FILES = [
    ('foundation', os.path.join(ROOT, 'foundation', 'al-foundation.css')),
    ('radio - tokens', os.path.join(HERE, 'al-radio-tokens.css')),
    ('radio', os.path.join(HERE, 'radio.css')),
]

# O erro e da pergunta: so o fieldset leva aria-invalid (regra 26). Ficou em
# True na primeira rodada da etapa 6, quando o radio.css ainda lia o erro no
# proprio radio - o a11y.py reprovou, e o CSS foi corrigido. Nao religar.
ERRO_NO_RADIO = False


def radio(rid, nome, valor, rotulo, *, checked=False, disabled=False,
          erro=False, sim=None, extra=''):
    """Um Radio completo.

    `sim` forca o hover, que so existe sob o ponteiro, escrevendo nas MESMAS
    variaveis privadas que o radio.css usa - nao e estilo paralelo."""
    attrs = [f'id="{rid}"', 'class="al-radio__input"', 'type="radio"',
             f'name="{nome}"', f'value="{valor}"']
    if checked:
        attrs.append('checked')
    if disabled:
        attrs.append('disabled')
    if erro and ERRO_NO_RADIO:
        attrs.append('aria-invalid="true"')
    if sim == 'hover':
        attrs.append('style="--_bg-state: var(--al-radio-bg-hover); '
                     '--_border-state: var(--al-radio-border-hover)"')
    if extra:
        attrs.append(extra)
    return (f'<label class="al-radio">'
            f'<span class="al-radio__control"><input {" ".join(attrs)}>'
            f'<span class="al-radio__dot" aria-hidden="true"></span></span>'
            f'<span class="al-radio__label">{rotulo}</span></label>')


def pergunta(nome, legenda, opcoes, *, erro=None, classe='qa-q'):
    """Um <fieldset> com <legend>: a pergunta que a aplicacao monta (regra 6).
    `erro` e o id da mensagem - o fieldset leva aria-invalid e describedby."""
    abre = f'<fieldset class="{classe}"'
    if erro:
        abre += f' aria-invalid="true" aria-describedby="{erro}"'
    abre += '>'
    corpo = ''.join(radio(f'{nome}-{i}', nome, v, r, erro=bool(erro), **kw)
                    for i, (v, r, kw) in enumerate(opcoes))
    return f'{abre}<legend>{legenda}</legend>{corpo}</fieldset>'


PLANO = 'Cobrança'

# (titulo, origem, nota, html do cartao)
# origem: real = interaja; simulado = so existe sob o ponteiro; codigo = sem
# variante no Figma, pintado pelo radio.css com os tokens aprovados na etapa 3.
ESTADOS = [
    ('Default', 'real', 'o repouso. A borda aqui é a exceção de contraste declarada (1,57:1).',
     pergunta('st-default', PLANO, [('m', 'Mensal', {}), ('a', 'Anual', {})])),
    ('Hover', 'simulado', 'só existe sob o ponteiro; a variável privada do componente foi escrita direto '
     'na primeira opção. Passe o mouse na segunda para ver o real — vale na linha inteira.',
     pergunta('st-hover', PLANO, [('m', 'Mensal', dict(sim='hover')), ('a', 'Anual', {})])),
    ('Active (marcado)', 'real', 'anel laranja com ponto de 14px. Clique em Anual: a seleção muda, '
     'e passar o mouse no marcado não muda nada (regra 15).',
     pergunta('st-checked', PLANO, [('m', 'Mensal', dict(checked=True)), ('a', 'Anual', {})])),
    ('Focus', 'real', 'tabule até aqui: anel laranja com respiro. Use as setas: foco e escolha andam juntos '
     '(regra 17). Clique com o mouse: sem anel.',
     pergunta('st-focus', PLANO, [('m', 'Mensal', {}), ('a', 'Anual', {})])),
    ('Error', 'real', 'o erro acende nas duas opções ao mesmo tempo (regra 21). A mensagem abaixo é do '
     'formulário, não do componente (regra 22).',
     pergunta('st-error', 'Forma de pagamento', [('p', 'Pix', {}), ('b', 'Boleto', {})], erro='st-error-msg')
     + '<p class="qa-formerror" id="st-error-msg">Escolha uma forma de pagamento.</p>'),
    ('Disabled', 'real', 'atributo disabled nativo: as setas e o Tab pulam a opção. '
     'Contraste abaixo de AA de propósito.',
     pergunta('st-disabled', PLANO, [('m', 'Mensal', {}), ('e', 'Empresarial', dict(disabled=True))])),
]

COMBINADOS = [
    ('Marcado + disabled', 'codigo', 'círculo cinza, ponto em dot-disabled — o único token sem variante no Figma.',
     pergunta('cb-dischk', 'Plano atual', [('e', 'Empresarial', dict(checked=True, disabled=True)),
                                           ('m', 'Mensal', dict(disabled=True))])),
    ('Erro + marcado', 'codigo', 'o marcado segue laranja; só o rótulo avisa. A vizinha vazia fica com borda vermelha.',
     pergunta('cb-errchk', 'Forma de pagamento', [('p', 'Pix', dict(checked=True)), ('b', 'Boleto', {})],
              erro='cb-errchk-msg')
     + '<p class="qa-formerror" id="cb-errchk-msg">Pix indisponível para este valor. Escolha outra forma.</p>'),
    ('Marcado + foco', 'codigo', 'tabule até aqui: o anel aparece por cima do anel laranja.',
     pergunta('cb-chkfoc', PLANO, [('m', 'Mensal', dict(checked=True)), ('a', 'Anual', {})])),
    ('Rótulo longo', 'real', 'o texto quebra alinhado ao topo do círculo, não centralizado nele (regra 13).',
     pergunta('cb-long', 'Envio da nota fiscal', [
         ('e', 'Enviar a nota fiscal por e-mail assim que o pagamento for confirmado, com cópia '
               'para o contador cadastrado', dict(checked=True)),
         ('n', 'Só disponibilizar no painel', {})])),
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

    meta = RADIO['meta']
    rows = RADIO['contrast']
    n_exc = len([r for r in rows if not r['pass']])

    # formulario: uma pergunta pre-selecionada com opcao "Nenhum" (regras 9 e
    # 10), uma sem pre-selecao porque envolve custo (regra 9), e uma opcional
    # marcada como tal no legend (regra 23).
    f_resumo = pergunta('f-resumo', 'Resumo das vendas por e-mail', [
        ('s', 'Semanal', dict(checked=True)), ('m', 'Mensal', {}), ('n', 'Nenhum', {})])
    f_pag = pergunta('f-pag', 'Forma de pagamento da assinatura', [
        ('c', 'Cartão de crédito', dict(extra='required')), ('p', 'Pix', dict(extra='required')),
        ('b', 'Boleto', dict(disabled=True, extra='required'))])
    f_tema = pergunta('f-origem', 'Como conheceu o AL (opcional)', [
        ('i', 'Indicação', {}), ('b', 'Busca', {}), ('r', 'Redes sociais', {})])

    return f'''<title>AL Radio QA</title>
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
/* a pergunta - fieldset nativo, montado pela aplicacao (regra 6) */
fieldset.qa-q {{ margin: 0; padding: 0; border: 0; min-width: 0; display: flex; flex-direction: column; gap: var(--al-space-12); }}
fieldset.qa-q legend {{ padding: 0; margin-bottom: var(--al-space-12); font-size: var(--al-font-size-sm); line-height: var(--al-line-height-sm); font-weight: 600; }}
.qa-form {{
  display: flex; flex-direction: column; gap: var(--al-space-32);
  padding: var(--al-space-24);
  border: 1px solid var(--al-border-subtle); border-radius: var(--al-radius-xl);
  background: var(--al-bg-surface-raised);
  max-width: 560px;
}}
.qa-form fieldset.qa-q legend {{ font-size: var(--al-font-size-md); line-height: var(--al-line-height-md); }}
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
      <h1>Radio — QA da etapa 6</h1>
      <p class="qa-sub">AL Design System {FOUND['meta']['version']} · componente {meta['version']} ·
      &lt;input type="radio"&gt; nativo · {len(rows)} medições de token, {n_exc} exceções declaradas, 0 reprovas</p>
    </div>
    <button type="button" class="qa-btn" id="theme-toggle" aria-pressed="false">
      <span id="theme-label">Tema claro</span>
    </button>
  </header>

  <section>
    <h2>O que testar</h2>
    <ol class="qa-checks">
      <li><strong>Tabule pela página.</strong> O Tab entra em cada pergunta uma vez só — na opção marcada, ou na primeira se nenhuma estiver.</li>
      <li><strong>Dentro da pergunta, use as setas.</strong> Elas movem o foco e a escolha juntos, e pulam a opção desabilitada. Espaço marca a opção focada que ainda não está marcada.</li>
      <li><strong>O anel só aparece no teclado.</strong> Chegue por Tab: anel laranja. Clique com o mouse: sem anel.</li>
      <li><strong>Clique no texto, não no círculo:</strong> também marca, e o hover acende a linha inteira — menos no radio já marcado.</li>
      <li><strong>Envie o formulário sem escolher a forma de pagamento:</strong> as opções da pergunta ficam vermelhas juntas e o erro aparece em texto no topo. Escolha uma: tudo volta.</li>
      <li><strong>Na pergunta do resumo, tente desmarcar:</strong> não dá — é por isso que existe a opção “Nenhum” (regra 10).</li>
      <li><strong>Troque o tema</strong> no botão acima e refaça os itens 3 e 5.</li>
      <li><strong>Reduza a janela</strong> até a largura de telefone: rótulo longo quebra, nada corta.</li>
    </ol>
  </section>

  <section>
    <h2>Os seis estados do Figma</h2>
    <p class="qa-lede">Um cartão por variante do component set, cada um montado como pergunta de verdade —
    radio sozinho não existe. Só o Hover é simulado, porque só existe enquanto o ponteiro está em cima.</p>
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
    <p class="qa-lede">Três perguntas: uma com resposta segura já marcada e a opção “Nenhum”, uma sem
    pré-seleção porque envolve custo, e uma opcional marcada como tal no título (regras 9, 10 e 23).
    É aqui que a ordem de tabulação, as setas e o erro em texto se provam.</p>
    <form class="qa-form" id="qa-form" novalidate>
      <p class="qa-summary" id="form-erro" hidden>Escolha uma forma de pagamento para assinar.</p>
      {f_resumo}
      {f_pag}
      {f_tema}
      <div class="qa-actions">
        <button type="submit" class="qa-btn qa-btn--primary" id="f-enviar">Assinar</button>
        <p class="qa-ok" id="form-ok" role="status"></p>
      </div>
    </form>
  </section>

  <section>
    <h2>Contraste medido no navegador</h2>
    <p class="qa-lede">Não são os números do <code>tokens.json</code>: o script lê a cor que o navegador
    realmente pintou, com <code>getComputedStyle</code>, depois de esperar a transição terminar — contra o
    fundo onde cada radio está de verdade (cartão em <code>bg-surface</code>).</p>
    <div class="qa-tablewrap">
      <table class="qa-measure">
        <thead><tr><th>papel</th><th>frente</th><th>fundo</th><th>medido</th><th>piso</th><th>veredito</th></tr></thead>
        <tbody id="measure-body"></tbody>
      </table>
    </div>
  </section>

  <p class="qa-foot">Gerado por <code>components/radio/qa.py</code> a partir do CSS commitado em
  <code>dev</code>. <code>al-foundation.css</code>, <code>al-radio-tokens.css</code> e
  <code>radio.css</code> estão embutidos como estão no repositório.</p>
</div>

<script>
(function () {{
  var root = document.documentElement;

  // ------------------------------------------ erro em texto (regras 21, 22, 26)
  // O erro e da pergunta: o fieldset leva aria-invalid e aria-describedby.
  var ERRO_NO_RADIO = {'true' if ERRO_NO_RADIO else 'false'};
  var form = document.getElementById('qa-form');
  var pag = form.querySelector('input[name="f-pag"]').closest('fieldset');
  var opcoes = Array.prototype.slice.call(pag.querySelectorAll('.al-radio__input'));
  var resumo = document.getElementById('form-erro');
  var ok = document.getElementById('form-ok');
  function marcarErro(sim) {{
    if (sim) {{
      pag.setAttribute('aria-invalid', 'true');
      pag.setAttribute('aria-describedby', 'form-erro');
    }} else {{
      pag.removeAttribute('aria-invalid');
      pag.removeAttribute('aria-describedby');
    }}
    if (ERRO_NO_RADIO) opcoes.forEach(function (o) {{
      if (sim) o.setAttribute('aria-invalid', 'true'); else o.removeAttribute('aria-invalid');
    }});
    resumo.hidden = !sim;
  }}
  form.addEventListener('submit', function (e) {{
    e.preventDefault();
    ok.textContent = '';
    var escolhida = opcoes.some(function (o) {{ return o.checked; }});
    if (!escolhida) {{
      marcarErro(true);
      opcoes.filter(function (o) {{ return !o.disabled; }})[0].focus();
      return;
    }}
    marcarErro(false);
    ok.textContent = 'Assinatura enviada.';
  }});
  opcoes.forEach(function (o) {{ o.addEventListener('change', function () {{ marcarErro(false); }}); }});

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
  function r(id) {{ return document.getElementById(id); }}
  function rotuloDe(id) {{ return r(id).closest('.al-radio').querySelector('.al-radio__label'); }}
  function pontoDe(id) {{ return r(id).parentNode.querySelector('.al-radio__dot'); }}
  function fundoDe(id) {{ return cor(r(id).closest('.qa-card'), 'backgroundColor'); }}

  var TXT = 4.5, GRA = 3.0;

  function alvos() {{
    return [
      ['rótulo',              cor(rotuloDe('st-default-0'), 'color'),  fundoDe('st-default-0'), TXT, false],
      ['rótulo em erro',      cor(rotuloDe('st-error-0'), 'color'),    fundoDe('st-error-0'),   TXT, false],
      ['borda em repouso',    cor(r('st-default-0'), 'borderTopColor'), fundoDe('st-default-0'), GRA, true],
      ['borda em erro',       cor(r('st-error-0'), 'borderTopColor'),   fundoDe('st-error-0'),   GRA, false],
      ['borda marcada',       cor(r('st-checked-0'), 'borderTopColor'), fundoDe('st-checked-0'), GRA, false],
      ['ponto',               cor(pontoDe('st-checked-0'), 'backgroundColor'), cor(r('st-checked-0'), 'backgroundColor'), GRA, false],
      ['ponto desabilitado',  cor(pontoDe('cb-dischk-0'), 'backgroundColor'),  cor(r('cb-dischk-0'), 'backgroundColor'),  GRA, true],
      ['rótulo desabilitado', cor(rotuloDe('st-disabled-1'), 'color'), fundoDe('st-disabled-1'), TXT, true],
    ];
  }}

  function medir() {{
    var corpo = document.getElementById('measure-body');
    corpo.textContent = '';
    alvos().forEach(function (l) {{
      var fg = l[1], bg = l[2];
      if (!fg || !bg) return;
      var v = cr(fg, bg), passa = v >= l[3];
      var classe = passa ? 'ok' : (l[4] ? 'exc' : 'bad');
      var texto = passa ? 'passa' : (l[4] ? 'exceção declarada' : 'REPROVA');
      var tr = document.createElement('tr');
      [l[0], 'rgb(' + fg.join(', ') + ')', 'rgb(' + bg.join(', ') + ')',
       v.toFixed(2) + ':1', l[3].toFixed(1) + ':1'].forEach(function (x) {{
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
    print(f'site/radio-qa.html escrito ({len(html)} bytes)')
    print(f'  CSS embutido: {", ".join(n for n, _ in CSS_FILES)}')
    corpo = re.sub(r'<style\b[^>]*>.*?</style>', '', html, flags=re.S)
    corpo = re.sub(r'<script\b[^>]*>.*?</script>', '', corpo, flags=re.S)
    n = len(re.findall(r'<input\b[^>]*al-radio__input', corpo))
    print(f'  radios de verdade no documento: {n}')
