"""
Gera a visualizacao de QA do Switch (etapa 6) em site/switch-qa.html.

Mesmo arranjo do Checkbox e do Radio: a pagina INLINA os arquivos de CSS reais
do repositorio - foundation, tokens do Switch e switch.css. Ela nao pode
divergir do codigo porque ela E o codigo.

O QUE E DIFERENTE DO RADIO

  Nao ha formulario com "Enviar": o switch tem efeito imediato (regra 1). A
  secao "Tela de configuracoes" e uma lista de switches independentes dentro
  de um <fieldset> (regras 5 e 6), com um switch que depende de outro (regra
  17) e um que simula a acao falhando (regra 21, opcao A): a bolinha troca na
  hora e, se o "servidor" recusar, volta e a aplicacao avisa em texto.

O a11y.py ao lado le o HTML que este script emite e cobra ali o contrato de
marcacao.

Rodar: python3 qa.py     (escreve o proprio arquivo; nunca redirecionar stdout)
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(ROOT, 'site', 'switch-qa.html')

FOUND = json.load(open(os.path.join(ROOT, 'tokens.json')))
SWITCH = json.load(open(os.path.join(HERE, 'tokens.json')))

CSS_FILES = [
    ('foundation', os.path.join(ROOT, 'foundation', 'al-foundation.css')),
    ('switch - tokens', os.path.join(HERE, 'al-switch-tokens.css')),
    ('switch', os.path.join(HERE, 'switch.css')),
]


def switch(sid, rotulo, *, checked=False, disabled=False, sim=None, extra=''):
    """Um Switch completo.

    `sim` forca o hover, que so existe sob o ponteiro, escrevendo na MESMA
    variavel privada que o switch.css usa - nao e estilo paralelo."""
    attrs = [f'id="{sid}"', 'class="al-switch__input"', 'type="checkbox"', 'role="switch"']
    if checked:
        attrs.append('checked')
    if disabled:
        attrs.append('disabled')
    if sim == 'hover':
        attrs.append('style="--_border-state: var(--al-switch-border-hover)"')
    if extra:
        attrs.append(extra)
    return (f'<label class="al-switch">'
            f'<span class="al-switch__control"><input {" ".join(attrs)}>'
            f'<span class="al-switch__thumb" aria-hidden="true"></span></span>'
            f'<span class="al-switch__label">{rotulo}</span></label>')


# (titulo, origem, nota, html do cartao)
# origem: real = interaja; simulado = so existe sob o ponteiro; codigo = sem
# variante no Figma, pintado pelo switch.css com os tokens aprovados na etapa 3.
ESTADOS = [
    ('Default', 'real', 'desligado. A bolinha (1,96:1) e a borda (1,47:1) são as exceções declaradas; '
     'quem sustenta é o rótulo visível e o laranja do ligado.',
     switch('st-default', 'Notificações por e-mail')),
    ('Hover', 'simulado', 'só existe sob o ponteiro; a variável privada foi escrita direto no input. '
     'Passe o mouse no Default: acende a borda, e vale na linha inteira.',
     switch('st-hover', 'Notificações por e-mail', sim='hover')),
    ('Active (ligado)', 'real', 'trilho laranja, bolinha branca à direita. Clique: ela desliza de volta. '
     'Passe o mouse ligado: nada muda (regra 14).',
     switch('st-checked', 'Modo escuro automático', checked=True)),
    ('Focus', 'real', 'tabule até aqui: anel laranja com respiro, a borda fica a de repouso. '
     'Espaço alterna; Enter não (regra 24). Clique com o mouse: sem anel.',
     switch('st-focus', 'Legendas nos vídeos')),
    ('Disabled', 'real', 'atributo disabled nativo: o Tab pula. Contraste abaixo de AA de propósito.',
     switch('st-disabled', 'Resumo semanal', disabled=True)),
]

COMBINADOS = [
    ('Ligado + disabled', 'codigo', 'trilho cinza, bolinha à direita um tom mais escura '
     '(thumb-checked-disabled) — sem laranja. Único token sem variante no Figma.',
     switch('cb-dischk', 'Backup diário', checked=True, disabled=True)),
    ('Ligado + foco', 'codigo', 'tabule até aqui: o anel aparece por fora do trilho laranja.',
     switch('cb-chkfoc', 'Sincronizar contatos', checked=True)),
    ('Rótulo longo', 'real', 'o texto quebra e o trilho fica alinhado à primeira linha (regra 11).',
     switch('cb-long', 'Enviar a nota fiscal por e-mail ao contador assim que o pagamento for '
                       'confirmado', checked=True)),
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

    meta = SWITCH['meta']
    rows = SWITCH['contrast']
    n_exc = len([r for r in rows if not r['pass']])

    # tela de configuracoes: independentes (regra 5), grupo montado pela
    # aplicacao (regra 6), estado inicial = estado real (regra 12), um
    # dependente (regra 17) e um que falha (regra 21).
    cfg = ''.join([
        switch('cfg-email', 'Notificações por e-mail', checked=True),
        switch('cfg-resumo', 'Resumo semanal', checked=True),
        switch('cfg-push', 'Notificações no celular'),
        switch('cfg-contador', 'Enviar notas ao contador'),
    ])

    return f'''<meta charset="utf-8">
<title>AL Switch QA</title>
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
.qa-settings {{
  max-width: 560px;
  padding: var(--al-space-24);
  border: 1px solid var(--al-border-subtle); border-radius: var(--al-radius-xl);
  background: var(--al-bg-surface-raised);
  display: flex; flex-direction: column; gap: var(--al-space-16);
}}
.qa-settings .qa-hint {{ margin: calc(-1 * var(--al-space-8)) 0 0; color: var(--al-text-secondary); font-size: var(--al-font-size-xs); line-height: var(--al-line-height-xs); }}
.qa-toast {{ margin: 0; font-size: var(--al-font-size-sm); line-height: var(--al-line-height-sm); }}
.qa-toast--erro {{ padding: var(--al-space-12) var(--al-space-16); border-radius: var(--al-radius-md); background: var(--al-bg-danger-subtle); color: var(--al-text-danger); }}
.qa-toast--ok {{ color: var(--al-text-success); }}
</style>

<div class="qa-wrap">
  <header class="qa-head">
    <div>
      <h1>Switch — QA da etapa 6</h1>
      <p class="qa-sub">AL Design System {FOUND['meta']['version']} · componente {meta['version']} ·
      &lt;input type="checkbox" role="switch"&gt; nativo · {len(rows)} medições de token, {n_exc} exceções declaradas, 0 reprovas</p>
    </div>
    <button type="button" class="qa-btn" id="theme-toggle" aria-pressed="false">
      <span id="theme-label">Tema claro</span>
    </button>
  </header>

  <section>
    <h2>O que testar</h2>
    <ol class="qa-checks">
      <li><strong>Tabule pela página.</strong> Cada switch recebe o Tab uma vez; o desabilitado é pulado.</li>
      <li><strong>Espaço alterna, Enter não.</strong> É o comportamento do checkbox nativo (regra 24).</li>
      <li><strong>O anel só aparece no teclado.</strong> Chegue por Tab: anel laranja. Clique com o mouse: sem anel.</li>
      <li><strong>Clique no texto, não no trilho:</strong> também alterna, e o hover acende a borda na linha inteira — menos no ligado.</li>
      <li><strong>Na tela de configurações, desligue “Notificações por e-mail”:</strong> o “Resumo semanal” fica desabilitado, porque depende dele (regra 17).</li>
      <li><strong>Ligue “Enviar notas ao contador”:</strong> a bolinha troca na hora; um instante depois o servidor simulado recusa, ela volta e o aviso aparece em texto (regra 21).</li>
      <li><strong>Troque o tema</strong> no botão acima e refaça os itens 3 e 4.</li>
      <li><strong>Reduza a janela</strong> até a largura de telefone: rótulo longo quebra, nada corta.</li>
      <li><strong>Ative “reduzir movimento” no sistema:</strong> a bolinha passa a trocar de lado sem deslizar (regra 25).</li>
    </ol>
  </section>

  <section>
    <h2>Os cinco estados do Figma</h2>
    <p class="qa-lede">Um cartão por variante do component set. Só o Hover é simulado, porque só existe
    enquanto o ponteiro está em cima.</p>
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
    <h2>Tela de configurações</h2>
    <p class="qa-lede">Sem botão “Salvar”: cada switch vale na hora (regra 1). O título do grupo é da
    aplicação — um <code>fieldset</code> com <code>legend</code> (regra 6).</p>
    <div class="qa-settings">
      <fieldset class="qa-q">
        <legend>Notificações</legend>
        {cfg}
      </fieldset>
      <p class="qa-toast" id="cfg-status" role="status" aria-live="polite"></p>
    </div>
  </section>

  <section>
    <h2>Contraste medido no navegador</h2>
    <p class="qa-lede">Não são os números do <code>tokens.json</code>: o script lê a cor que o navegador
    realmente pintou, com <code>getComputedStyle</code>, depois de esperar a transição terminar — contra o
    fundo onde cada switch está de verdade (cartão em <code>bg-surface</code>).</p>
    <div class="qa-tablewrap">
      <table class="qa-measure">
        <thead><tr><th>papel</th><th>frente</th><th>fundo</th><th>medido</th><th>piso</th><th>veredito</th></tr></thead>
        <tbody id="measure-body"></tbody>
      </table>
    </div>
  </section>

  <p class="qa-foot">Gerado por <code>components/switch/qa.py</code> a partir do CSS commitado em
  <code>dev</code>. <code>al-foundation.css</code>, <code>al-switch-tokens.css</code> e
  <code>switch.css</code> estão embutidos como estão no repositório.</p>
</div>

<script>
(function () {{
  var root = document.documentElement;
  function r(id) {{ return document.getElementById(id); }}

  // ------------------------------------------- dependencia (regra 17)
  var email = r('cfg-email'), resumo = r('cfg-resumo');
  function dependencia() {{ resumo.disabled = !email.checked; }}
  email.addEventListener('change', dependencia);
  dependencia();

  // ------------------------------------------- falha, opcao A (regra 21)
  // Troca na hora; o "servidor" recusa; a bolinha volta ao estado real e a
  // aplicacao avisa em texto. O componente nao tem estado de carregamento.
  var contador = r('cfg-contador'), status = r('cfg-status');
  contador.addEventListener('change', function () {{
    var pedido = contador.checked;
    status.className = 'qa-toast';
    status.textContent = '';
    setTimeout(function () {{
      if (pedido) {{
        contador.checked = false;
        status.className = 'qa-toast qa-toast--erro';
        status.textContent = 'Não foi possível ativar o envio ao contador: nenhum contador cadastrado.';
      }} else {{
        status.className = 'qa-toast qa-toast--ok';
        status.textContent = 'Envio ao contador desativado.';
      }}
    }}, 700);
  }});

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
  function rotuloDe(id) {{ return r(id).closest('.al-switch').querySelector('.al-switch__label'); }}
  function bolinhaDe(id) {{ return r(id).parentNode.querySelector('.al-switch__thumb'); }}
  function fundoDe(id) {{ return cor(r(id).closest('.qa-card'), 'backgroundColor'); }}
  function trilho(id) {{ return cor(r(id), 'backgroundColor'); }}

  var TXT = 4.5, GRA = 3.0;

  function alvos() {{
    return [
      ['rótulo',                    cor(rotuloDe('st-default'), 'color'),               fundoDe('st-default'), TXT, false],
      ['borda em repouso',          cor(r('st-default'), 'borderTopColor'),             fundoDe('st-default'), GRA, true],
      ['borda em hover',            cor(r('st-hover'), 'borderTopColor'),               fundoDe('st-hover'),   GRA, false],
      ['bolinha desligada',         cor(bolinhaDe('st-default'), 'backgroundColor'),    trilho('st-default'),  GRA, true],
      ['trilho ligado',             trilho('st-checked'),                               fundoDe('st-checked'), GRA, false],
      ['bolinha ligada',            cor(bolinhaDe('st-checked'), 'backgroundColor'),    trilho('st-checked'),  GRA, false],
      ['rótulo desabilitado',       cor(rotuloDe('st-disabled'), 'color'),              fundoDe('st-disabled'), TXT, true],
      ['bolinha desabilitada',      cor(bolinhaDe('st-disabled'), 'backgroundColor'),   trilho('st-disabled'), GRA, true],
      ['bolinha ligada desabilit.', cor(bolinhaDe('cb-dischk'), 'backgroundColor'),     trilho('cb-dischk'),   GRA, true],
    ];
  }}

  function medir() {{
    var corpo = r('measure-body');
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
    print(f'site/switch-qa.html escrito ({len(html)} bytes)')
    print(f'  CSS embutido: {", ".join(n for n, _ in CSS_FILES)}')
    corpo = re.sub(r'<style\b[^>]*>.*?</style>', '', html, flags=re.S)
    corpo = re.sub(r'<script\b[^>]*>.*?</script>', '', corpo, flags=re.S)
    n = len(re.findall(r'<input\b[^>]*al-switch__input', corpo))
    print(f'  switches de verdade no documento: {n}')
