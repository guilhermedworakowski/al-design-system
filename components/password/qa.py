"""
Gera a visualizacao de QA do Password (etapa 6) em site/password-qa.html.

Mesmo arranjo do Input: a pagina INLINA os arquivos reais do repositorio -
foundation, icon, tokens do Password, password.css E password.js. Ela nao pode
divergir do codigo porque ela E o codigo; mexer no componente e rodar este
script de novo basta.

O a11y.py ao lado le o HTML que este script emite e cobra ali o contrato de
marcacao.

O OLHO E O PROPRIO password.js
  Diferente do contador do Input, cujo script morava na pagina, o
  comportamento do olho e parte do componente (decisao de Gui, etapa 5,
  opcao A). A pagina so inlina o arquivo. O formulario de teste tem um botao
  "Entrar" para provar a regra 16: enviar esconde a senha de novo.

Rodar: python3 qa.py     (escreve o proprio arquivo; nunca redirecionar stdout)
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(ROOT, 'site', 'password-qa.html')

FOUND = json.load(open(os.path.join(ROOT, 'tokens.json')))
PW = json.load(open(os.path.join(HERE, 'tokens.json')))

CSS_FILES = [
    ('foundation', os.path.join(ROOT, 'foundation', 'al-foundation.css')),
    ('icon - tokens', os.path.join(ROOT, 'components', 'icon', 'al-icon-tokens.css')),
    ('icon', os.path.join(ROOT, 'components', 'icon', 'icon.css')),
    ('password - tokens', os.path.join(HERE, 'al-password-tokens.css')),
    ('password', os.path.join(HERE, 'password.css')),
]
JS_FILE = os.path.join(HERE, 'password.js')


def icone(nome, classe):
    """O svg do Icon, inline, com o contrato decorativo - o nome acessivel e
    do botao, nunca do icone."""
    svg = open(os.path.join(ROOT, 'components', 'icon', 'icons', f'{nome}.svg')).read()
    corpo = re.search(r'<svg\b[^>]*>(.*)</svg>', svg, flags=re.S).group(1)
    return (f'<svg class="al-icon {classe}" viewBox="0 0 24 24" aria-hidden="true" '
            f'focusable="false">{corpo}</svg>')


EYE = icone('eye', 'al-password__show')
EYE_OFF = icone('eye-off', 'al-password__hide')


def campo(cid, rotulo, *, novo=False, erro=None, disabled=False, valor=None,
          placeholder='Digite sua senha', requisitos=None, show=None, hide=None,
          sim=None, visivel=False):
    """Um Password completo. `sim` forca o hover escrevendo na MESMA variavel
    privada que o password.css usa. `visivel` so serve aos cartoes de estado:
    o JS reescreve para escondido no carregamento (regra 13), entao o cartao
    marca `data-qa-visible` e a pagina abre o olho depois."""
    attrs = ['class="al-password__field"', f'id="{cid}"', f'name="{cid}"', 'type="password"',
             f'autocomplete="{"new-password" if novo else "current-password"}"',
             'spellcheck="false"', 'autocapitalize="none"']
    if valor is not None:
        attrs.append(f'value="{valor}"')
    if placeholder:
        attrs.append(f'placeholder="{placeholder}"')
    desc = []
    if requisitos:
        desc.append(f'{cid}-req')
    if erro:
        desc.append(f'{cid}-erro')
    if desc:
        attrs.append(f'aria-describedby="{" ".join(desc)}"')
    if erro:
        attrs.append('aria-invalid="true"')
    if disabled:
        attrs.append('disabled')
    if visivel:
        attrs.append('data-qa-visible')

    battrs = ['class="al-password__toggle"', 'type="button"', f'aria-controls="{cid}"',
              'aria-label="Mostrar senha"']
    if show:
        battrs.append(f'data-label-show="{show}" data-label-hide="{hide}"')
    if disabled:
        battrs.append('disabled')
    battrs.append('hidden')

    estilo = f' style="--_border-state: var(--al-password-border-{sim})"' if sim else ''
    req = (f'<p class="qa-req" id="{cid}-req">{requisitos}</p>\n    ' if requisitos else '')
    msg = (f'\n      <p class="al-password__help" id="{cid}-erro">{erro}</p>' if erro else '')

    return f'''{req}<div class="al-password">
      <label class="al-password__label" for="{cid}">{rotulo}</label>
      <div class="al-password__control"{estilo}>
        <input {" ".join(attrs)}>
        <button {" ".join(battrs)}>
          {EYE}
          {EYE_OFF}
        </button>
      </div>{msg}
    </div>'''


SENHA = 'pa$$w0rd123'

# (titulo, origem, nota, kwargs)
ESTADOS = [
    ('Default · vazio', 'real', 'o repouso com o placeholder. A borda é a exceção de contraste declarada.',
     dict(cid='st-default', rotulo='Senha')),
    ('Default · escondida', 'real', 'pontos desenhados pelo navegador; o ícone é o olho (ação: mostrar).',
     dict(cid='st-hidden', rotulo='Senha', valor=SENHA)),
    ('Default · visível', 'real', 'o texto aparece; o ícone vira o olho cortado (ação: esconder).',
     dict(cid='st-visible', rotulo='Senha', valor=SENHA, visivel=True)),
    ('Hover', 'simulado', 'só existe sob o ponteiro, então a variável privada do componente foi escrita direto.',
     dict(cid='st-hover', rotulo='Senha', valor=SENHA, sim='hover')),
    ('Focus no campo', 'real', 'clique ou tabule até o campo: borda e anel laranja na caixa inteira.',
     dict(cid='st-focus', rotulo='Senha', valor=SENHA)),
    ('Focus no olho', 'real', 'tabule mais uma vez: anel circular só no olho, a caixa não acende (opção A).',
     dict(cid='st-focus-eye', rotulo='Senha', valor=SENHA)),
    ('Error', 'real', 'aria-invalid="true". O valor mantém a cor normal; só rótulo, borda e mensagem ficam vermelhos.',
     dict(cid='st-error', rotulo='Senha', valor=SENHA, erro='A senha precisa ter pelo menos 8 caracteres')),
    ('Focus + Error', 'real', 'tabule até o campo: anel vinho. Até o olho: anel laranja, porque o erro é do campo.',
     dict(cid='st-focuserror', rotulo='Senha', valor=SENHA, erro='A senha precisa ter pelo menos 8 caracteres')),
    ('Disabled · vazio', 'real', 'campo e olho desabilitados: o Tab pula os dois.',
     dict(cid='st-disabled', rotulo='Senha', disabled=True)),
    ('Disabled · escondida', 'real', 'sempre escondida: a variante Visible do desabilitado não existe.',
     dict(cid='st-disabled-val', rotulo='Senha', valor=SENHA, disabled=True)),
]


CHROME = r'''/* ================= cromo da pagina de QA =================
   Usa os proprios tokens do AL, sem paleta paralela. */
html, body { background: var(--al-bg-canvas); }
body {
  margin: 0;
  color: var(--al-text-primary);
  font-family: var(--al-font-sans);
  font-size: var(--al-font-size-md);
  line-height: var(--al-line-height-md);
}
.qa-wrap {
  max-width: 1120px; margin: 0 auto;
  padding-inline: var(--al-space-16);
  padding-block: var(--al-space-32) var(--al-space-64);
  display: flex; flex-direction: column; gap: var(--al-space-48);
}
.qa-head {
  display: flex; flex-wrap: wrap; align-items: flex-end;
  justify-content: space-between; gap: var(--al-space-16);
  border-bottom: 1px solid var(--al-border-subtle);
  padding-bottom: var(--al-space-16);
}
.qa-head h1 {
  margin: 0; font-size: var(--al-font-size-3xl); line-height: var(--al-line-height-3xl);
  font-weight: 600; letter-spacing: -0.02em; text-wrap: balance;
}
.qa-sub { margin: var(--al-space-4) 0 0; color: var(--al-text-secondary); font-size: var(--al-font-size-sm); }
.qa-theme {
  display: inline-flex; align-items: center; gap: var(--al-space-8);
  padding: var(--al-space-8) var(--al-space-12);
  border: 1px solid var(--al-border-strong); border-radius: var(--al-radius-full);
  background: var(--al-bg-surface-raised); color: var(--al-text-primary);
  font: inherit; font-size: var(--al-font-size-sm); cursor: pointer;
}
.qa-theme:focus-visible { outline: none; box-shadow: var(--al-focus-ring-default); }
section h2 {
  margin: 0 0 var(--al-space-4);
  font-size: var(--al-font-size-xl); line-height: var(--al-line-height-xl);
  font-weight: 600; letter-spacing: -0.01em;
}
section > p.qa-lede { margin: 0 0 var(--al-space-20); color: var(--al-text-secondary); max-width: 62ch; }
.qa-grid {
  display: grid; gap: var(--al-space-20);
  grid-template-columns: repeat(auto-fill, minmax(min(280px, 100%), 1fr));
}
.qa-card {
  display: flex; flex-direction: column; gap: var(--al-space-12);
  padding: var(--al-space-20);
  border: 1px solid var(--al-border-subtle); border-radius: var(--al-radius-xl);
  background: var(--al-bg-surface);
}
.qa-card__head { display: flex; align-items: center; justify-content: space-between; gap: var(--al-space-8); }
.qa-card__title { margin: 0; font-size: var(--al-font-size-sm); font-weight: 600; letter-spacing: 0.04em; text-transform: uppercase; }
.qa-card__note { margin: 0; color: var(--al-text-secondary); font-size: var(--al-font-size-xs); line-height: var(--al-line-height-xs); }
.qa-tag {
  font-size: var(--al-font-size-xs); line-height: var(--al-line-height-xs);
  padding: 2px var(--al-space-8); border-radius: var(--al-radius-full);
  border: 1px solid var(--al-border-default); color: var(--al-text-secondary);
}
.qa-tag--real { border-color: var(--al-border-success); color: var(--al-text-success); }
.qa-form {
  display: grid; gap: var(--al-space-20);
  grid-template-columns: repeat(auto-fit, minmax(min(260px, 100%), 1fr));
  padding: var(--al-space-24);
  border: 1px solid var(--al-border-subtle); border-radius: var(--al-radius-xl);
  background: var(--al-bg-surface-raised);
}
.qa-checks { margin: 0; padding-left: var(--al-space-20); display: grid; gap: var(--al-space-8); max-width: 68ch; }
.qa-checks li { color: var(--al-text-secondary); }
.qa-checks strong { color: var(--al-text-primary); font-weight: 500; }
.qa-tablewrap { overflow-x: auto; }
table.qa-measure { border-collapse: collapse; width: 100%; font-size: var(--al-font-size-sm); font-variant-numeric: tabular-nums; }
table.qa-measure th, table.qa-measure td { text-align: left; padding: var(--al-space-8) var(--al-space-12); border-bottom: 1px solid var(--al-border-subtle); white-space: nowrap; }
table.qa-measure th { font-weight: 600; font-size: var(--al-font-size-xs); text-transform: uppercase; letter-spacing: 0.04em; color: var(--al-text-secondary); }
.qa-verdict { font-weight: 600; }
.qa-verdict--ok { color: var(--al-text-success); }
.qa-verdict--exc { color: var(--al-text-warning); }
.qa-verdict--bad { color: var(--al-text-danger); }
.qa-foot { color: var(--al-text-secondary); font-size: var(--al-font-size-sm); border-top: 1px solid var(--al-border-subtle); padding-top: var(--al-space-16); }
@media (prefers-reduced-motion: reduce) { * { transition: none !important; } }
'''


def build():
    css_inline = '\n'.join(
        f'/* ================= {nome} ================= */\n' + open(p, encoding='utf-8').read()
        for nome, p in CSS_FILES)
    js = open(JS_FILE, encoding='utf-8').read()

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

    login = '\n      '.join([
        '<div class="qa-field"><label class="qa-label" for="f-email">E-mail</label>'
        '<input class="qa-input" id="f-email" name="f-email" type="email" autocomplete="username" '
        'value="ana@empresa.com"></div>',
        campo(cid='f-senha', rotulo='Senha'),
    ])
    cadastro = '\n      '.join([
        campo(cid='f-atual', rotulo='Senha atual', valor=SENHA,
              show='Mostrar senha atual', hide='Ocultar senha atual'),
        campo(cid='f-nova', rotulo='Nova senha', novo=True,
              requisitos='Use pelo menos 8 caracteres. Frases longas são mais seguras que símbolos.',
              show='Mostrar nova senha', hide='Ocultar nova senha'),
        campo(cid='f-curta', rotulo='Confirmar nova senha', novo=True, valor='abc',
              erro='A senha precisa ter pelo menos 8 caracteres',
              show='Mostrar confirmação', hide='Ocultar confirmação'),
        campo(cid='f-bloq', rotulo='Senha do administrador', disabled=True,
              placeholder=None, valor=SENHA),
    ])

    meta = PW['meta']
    n_contraste = len(PW['contrast'])
    n_exc = len([r for r in PW['contrast'] if not r['pass']])

    return f'''<meta charset="utf-8">
<title>AL Password QA</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap">
<style>
{css_inline}

{CHROME}
/* campo de e-mail do formulario de login - so cenario, nao e o Input do AL */
.qa-field {{ display: flex; flex-direction: column; gap: var(--al-space-8); }}
.qa-label {{ color: var(--al-text-primary); }}
.qa-input {{
  box-sizing: border-box; width: 100%;
  padding: calc(var(--al-space-12) - 1px);
  border: 1px solid var(--al-border-default); border-radius: var(--al-radius-lg);
  background: var(--al-bg-surface-raised); color: var(--al-text-primary);
  font: inherit;
}}
.qa-input:focus-visible {{ outline: none; border-color: var(--al-border-brand); box-shadow: var(--al-focus-ring-default); }}
.qa-req {{ margin: 0 0 calc(-1 * var(--al-space-8)); color: var(--al-text-secondary); font-size: var(--al-font-size-sm); line-height: var(--al-line-height-sm); }}
.qa-submit {{
  justify-self: start; align-self: end;
  padding: var(--al-space-12) var(--al-space-20);
  border: 0; border-radius: var(--al-radius-lg);
  background: var(--al-bg-brand); color: var(--al-text-on-brand);
  font: inherit; font-weight: 500; cursor: pointer;
}}
.qa-submit:focus-visible {{ outline: none; box-shadow: var(--al-focus-ring-default); }}
.qa-log {{ grid-column: 1 / -1; margin: 0; color: var(--al-text-secondary); font-size: var(--al-font-size-sm); }}
.qa-col {{ display: flex; flex-direction: column; gap: var(--al-space-20); }}
</style>

<div class="qa-wrap">
  <header class="qa-head">
    <div>
      <h1>Password — QA da etapa 6</h1>
      <p class="qa-sub">AL Design System {FOUND['meta']['version']} · componente {meta['version']} ·
      &lt;input type="password"&gt; nativo + botão do olho · {n_contraste} medições de contraste,
      {n_exc} exceções declaradas, 0 reprovas</p>
    </div>
    <button type="button" class="qa-theme" id="theme-toggle" aria-pressed="false">
      <span id="theme-label">Tema claro</span>
    </button>
  </header>

  <section>
    <h2>O que testar</h2>
    <ol class="qa-checks">
      <li><strong>Tabule pelo login.</strong> E-mail → Senha → olho → Entrar. O foco no campo acende a caixa; o foco no olho desenha só o círculo em volta dele.</li>
      <li><strong>Com o foco no olho, aperte Espaço ou Enter.</strong> A senha aparece, o ícone vira o olho cortado e o foco continua no botão. De novo: esconde.</li>
      <li><strong>Clique no olho com o mouse</strong> e confira que o texto digitado não se perde.</li>
      <li><strong>Deixe a senha visível e clique em Entrar.</strong> Ela volta a ficar escondida (regra 16).</li>
      <li><strong>Alteração de senha:</strong> três campos, cada um com o próprio olho. Com leitor de tela, o nome muda: “Mostrar nova senha”, “Mostrar confirmação”.</li>
      <li><strong>Confirmar nova senha</strong> está em erro: no campo o anel é vinho; no olho, laranja.</li>
      <li><strong>Senha do administrador</strong> está desabilitada: o Tab pula o campo e o olho.</li>
      <li><strong>Cole uma senha</strong> em qualquer campo: colar sempre funciona (regra 27).</li>
      <li><strong>Troque o tema</strong> e refaça 1, 2 e 6. No escuro, o anel do olho tem um contorno fino escuro por dentro — aceito na etapa 3.</li>
      <li><strong>Reduza a janela</strong> até a largura de telefone: os campos esticam e o olho não sai da caixa.</li>
    </ol>
  </section>

  <section>
    <h2>Os estados</h2>
    <p class="qa-lede">As 17 variantes do Figma reduzidas ao que muda no código: vazio, escondida e
    visível são o mesmo campo com outro conteúdo ou outro <code>type</code>. O Hover escreve direto na
    variável privada que o <code>password.css</code> usa; os demais são reais.</p>
    <div class="qa-grid">
    {chr(10).join('    ' + c for c in cards)}
    </div>
  </section>

  <section>
    <h2>Login</h2>
    <p class="qa-lede">O caso mais comum. “Entrar” não envia nada: só prova que a senha volta a ficar
    escondida no envio.</p>
    <form class="qa-form" id="qa-login" action="#" novalidate>
      {login}
      <button type="submit" class="qa-submit">Entrar</button>
      <p class="qa-log" id="qa-login-log" aria-live="polite"></p>
    </form>
  </section>

  <section>
    <h2>Alteração de senha</h2>
    <p class="qa-lede">Vários campos de senha numa tela: cada olho tem nome próprio, e os requisitos
    ficam no formulário, acima do campo, ligados por <code>aria-describedby</code> (regra 7, opção B).</p>
    <form class="qa-form" id="qa-troca" action="#" novalidate>
      {cadastro}
      <button type="submit" class="qa-submit">Salvar</button>
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

  <p class="qa-foot">Gerado por <code>components/password/qa.py</code> a partir do código commitado em
  <code>dev</code>. <code>al-foundation.css</code>, <code>icon.css</code>,
  <code>al-password-tokens.css</code>, <code>password.css</code> e <code>password.js</code> estão
  embutidos como estão no repositório.</p>
</div>

<script>
/* ================= password.js, como esta no repositorio ================= */
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
  function pintarBotao() {{
    var d = escuro();
    label.textContent = d ? 'Tema escuro' : 'Tema claro';
    btn.setAttribute('aria-pressed', String(d));
  }}
  btn.addEventListener('click', function () {{
    root.dataset.theme = escuro() ? 'light' : 'dark';
    pintarBotao();
    setTimeout(medir, 350);   // folga para a transicao de 120ms
  }});
  pintarBotao();

  // cartao "visivel": o JS do componente abriu escondido (regra 13); a
  // pagina abre o olho como a pessoa faria, pelo proprio botao.
  // init() antes: o password.js espera o DOMContentLoaded, e este script
  // roda antes dele. init e idempotente (data-al-ready).
  window.alPassword.init();
  document.querySelectorAll('.al-password__field[data-qa-visible]').forEach(function (c) {{
    c.closest('.al-password').querySelector('.al-password__toggle').click();
  }});

  // os formularios nao saem da pagina - o password.js ja escondeu no submit
  ['qa-login', 'qa-troca'].forEach(function (id) {{
    document.getElementById(id).addEventListener('submit', function (e) {{
      e.preventDefault();
      if (id === 'qa-login') {{
        document.getElementById('qa-login-log').textContent =
          'Enviado. O campo está como type="' + document.getElementById('f-senha').type + '".';
      }}
    }});
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
  function caixa(id) {{ return document.getElementById(id).closest('.al-password__control'); }}
  function olho(id) {{ return caixa(id).querySelector('.al-password__toggle'); }}
  function $(s) {{ return document.querySelector(s); }}
  // o ultimo rgb() do box-shadow composto e a cor do anel
  function anel(str) {{
    var m = str.match(/rgba?\\([^)]*\\)/g);
    return m ? rgb(m[m.length - 1]) : null;
  }}
  function anelDoOlho() {{
    var s = getComputedStyle(document.documentElement).getPropertyValue('--al-password-toggle-ring');
    var probe = document.createElement('div');
    probe.style.boxShadow = s; document.body.appendChild(probe);
    var cor = anel(getComputedStyle(probe).boxShadow); probe.remove();
    return cor;
  }}

  var TXT = 4.5, GRAF = 3.0;

  function alvos() {{
    var form = corDe(document.getElementById('qa-troca'), 'backgroundColor');
    var fundo = corDe(caixa('f-atual'), 'backgroundColor');
    var fundoOff = corDe(caixa('f-bloq'), 'backgroundColor');
    return [
      ['rótulo',              corDe($('label[for="f-atual"]'), 'color'),     form,     TXT,  false],
      ['rótulo em erro',      corDe($('label[for="f-curta"]'), 'color'),     form,     TXT,  false],
      ['mensagem de erro',    corDe($('#f-curta-erro'), 'color'),            form,     TXT,  false],
      ['placeholder',         corDe($('#f-nova'), 'color', '::placeholder'), fundo,    TXT,  false],
      ['valor',               corDe($('#f-atual'), 'color'),                 fundo,    TXT,  false],
      ['valor em erro',       corDe($('#f-curta'), 'color'),                 fundo,    TXT,  false],
      ['olho',                corDe(olho('f-atual'), 'color'),               fundo,    GRAF, false],
      ['anel do olho',        anelDoOlho(),                                  fundo,    GRAF, false],
      ['borda em repouso',    corDe(caixa('f-atual'), 'borderTopColor'),     form,     GRAF, true],
      ['borda em erro',       corDe(caixa('f-curta'), 'borderTopColor'),     form,     GRAF, false],
      ['texto desabilitado',  corDe($('#f-bloq'), 'color'),                  fundoOff, TXT,  true],
      ['olho desabilitado',   corDe(olho('f-bloq'), 'color'),                fundoOff, GRAF, true],
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
    print(f'site/password-qa.html escrito ({len(html)} bytes)')
    print(f'  embutido: {", ".join(n for n, _ in CSS_FILES)}, password.js')
    corpo = re.sub(r'<(style|script)\b[^>]*>.*?</\1>', '', html, flags=re.S)
    n = len(re.findall(r'<input\b[^>]*al-password__field', corpo))
    print(f'  campos de verdade no documento: {n}  '
          f'({len(ESTADOS)} cartoes de estado + 5 dos formularios)')
