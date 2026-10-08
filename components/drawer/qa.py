"""
Gera a visualizacao de QA do Drawer (etapa 6) em site/drawer-qa.html.

Mesmo arranjo dos outros componentes: a pagina INLINA os arquivos reais do
repositorio - foundation, Icon, Button, Icon Button, Input, Modal (so para o
cenario "Excluir abre um Modal", regra 22), tokens do Drawer, drawer.css e
drawer.js. Ela nao pode divergir do codigo porque ela E o codigo. O unico
script a mais e o cromo (tema, registro de abertura/fechamento, medicao).

O QUE A PAGINA MOSTRA

  - tres tamanhos CONGELADOS lado a lado (sm, md, lg). Um <dialog> de verdade
    so existe aberto no topo da pagina; aqui eles ficam inline, com `open`,
    sob `inert` + `aria-hidden`, a posicao do UA zerada e uma altura de
    exemplo. Sao "simulado" e o a11y.py isenta o `open` deles;
  - quatro cenarios AO VIVO, abertos por showModal() pelo proprio drawer.js:
    detalhe (so leitura, sem rodape, com botao que abre um Modal), formulario
    (com campos), termos (lg, conteudo longo, so o miolo rola) e notificacoes
    (sem X: a saida visivel e o rodape);
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
OUT = os.path.join(ROOT, 'site', 'drawer-qa.html')

FOUND = json.load(open(os.path.join(ROOT, 'tokens.json')))
DRW = json.load(open(os.path.join(HERE, 'tokens.json')))
COMP = os.path.join(ROOT, 'components')

CSS_FILES = [
    ('foundation', os.path.join(ROOT, 'foundation', 'al-foundation.css')),
    ('icon - tokens', os.path.join(COMP, 'icon', 'al-icon-tokens.css')),
    ('icon', os.path.join(COMP, 'icon', 'icon.css')),
    ('button - tokens', os.path.join(COMP, 'button', 'al-button-tokens.css')),
    ('button', os.path.join(COMP, 'button', 'button.css')),
    ('icon-button - tokens', os.path.join(COMP, 'icon-button', 'al-icon-button-tokens.css')),
    ('icon-button', os.path.join(COMP, 'icon-button', 'icon-button.css')),
    ('input - tokens', os.path.join(COMP, 'input', 'al-input-tokens.css')),
    ('input', os.path.join(COMP, 'input', 'input.css')),
    ('modal - tokens', os.path.join(COMP, 'modal', 'al-modal-tokens.css')),
    ('modal', os.path.join(COMP, 'modal', 'modal.css')),
    ('drawer - tokens', os.path.join(HERE, 'al-drawer-tokens.css')),
    ('drawer', os.path.join(HERE, 'drawer.css')),
]
JS_FILES = [
    os.path.join(COMP, 'modal', 'modal.js'),
    os.path.join(HERE, 'drawer.js'),
]


def x_icon():
    svg = open(os.path.join(COMP, 'icon', 'icons', 'x.svg'), encoding='utf-8').read()
    path = re.search(r'<svg[^>]*>(.*?)</svg>', svg, flags=re.S).group(1).strip()
    return ('<svg class="al-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
            f'aria-hidden="true" focusable="false">{path}</svg>')


def btn(rotulo, variante, extra=''):
    return (f'<button type="button" class="al-btn al-btn--{variante} al-btn--md"{extra}>'
            f'<span class="al-btn__label">{rotulo}</span></button>')


def fechar():
    return ('<button type="button" class="al-icon-btn al-icon-btn--ghost al-icon-btn--sm" '
            f'aria-label="Fechar" data-al-drawer-close>{x_icon()}</button>')


def drawer(did, titulo, corpo, acoes='', tamanho='md', extra='', com_x=True):
    rodape = f'<div class="al-drawer__actions">{acoes}</div>' if acoes else ''
    return (f'<dialog class="al-drawer al-drawer--{tamanho}" id="{did}" aria-labelledby="{did}-t"{extra}>'
            f'<header class="al-drawer__header"><h2 class="al-drawer__title" id="{did}-t">{titulo}</h2>'
            f'{fechar() if com_x else ""}</header>'
            f'<div class="al-drawer__content">{corpo}</div>{rodape}</dialog>')


def modal(mid, titulo, corpo, acoes, tamanho='sm'):
    return (f'<dialog class="al-modal al-modal--{tamanho}" id="{mid}" aria-labelledby="{mid}-t">'
            f'<h2 class="al-modal__title" id="{mid}-t">{titulo}</h2>'
            f'<div class="al-modal__content">{corpo}</div>'
            f'<div class="al-modal__actions">{acoes}</div></dialog>')


def campo(cid, rotulo, tipo='text', valor=''):
    return (f'<div class="al-input"><div class="al-input__labelrow">'
            f'<label class="al-input__label" for="{cid}">{rotulo}</label></div>'
            f'<div class="al-input__control"><input class="al-input__field" id="{cid}" name="{cid}" '
            f'type="{tipo}" value="{valor}" autocomplete="off"></div></div>')


def p(txt):
    return f'<p class="qa-copy">{txt}</p>'


DETALHE = (
    '<dl class="qa-dl">'
    '<div><dt>Nome</dt><dd>Ana Souza</dd></div>'
    '<div><dt>E-mail</dt><dd>ana@empresa.com</dd></div>'
    '<div><dt>Cliente desde</dt><dd>12 de março de 2024</dd></div>'
    '<div><dt>Pedidos</dt><dd>38, o último em 02/10</dd></div>'
    '</dl>'
    + btn('Excluir cliente', 'danger', ' data-al-modal-open="m-excluir"')
)
EXCLUIR = p('Isso não pode ser desfeito. Os pedidos dela continuam no histórico.')
FORM = '<div class="qa-fields">' + campo('qa-nome', 'Nome', 'text', 'Ana Souza') \
    + campo('qa-email', 'E-mail', 'email', 'ana@empresa.com') \
    + campo('qa-tel', 'Telefone', 'tel', '(11) 98888-7777') + '</div>'
_TERMOS = [
    'Ao usar o serviço você concorda com estas condições. Elas descrevem o que oferecemos, o que '
    'esperamos de você e como resolvemos um problema quando ele acontece.',
    'Você é responsável por manter a sua senha em segredo e por tudo o que acontece na sua conta. '
    'Se perceber um acesso que não foi seu, avise o atendimento na hora.',
    'Podemos mudar o serviço ou estas condições. Quando a mudança for relevante, avisamos com '
    '30 dias de antecedência por e-mail e dentro do aplicativo.',
    'Os dados que você cadastra são usados para entregar o pedido, emitir a nota e prevenir '
    'fraude. Não vendemos os seus dados e você pode pedir a exclusão a qualquer momento.',
    'Reembolsos seguem o prazo da forma de pagamento: até 7 dias úteis no cartão e no Pix, e '
    'até 10 dias úteis no boleto, depois que o pedido é cancelado.',
    'Se uma parte destas condições não puder ser aplicada, o restante continua valendo. '
    'A lei aplicável é a brasileira e o foro é o da cidade do consumidor.',
    'Dúvidas? Fale com o atendimento pelo aplicativo, em Conta › Ajuda. Respondemos em até '
    'dois dias úteis, de segunda a sexta.',
]
LONGO = ''.join(p(f'<strong>{i}.</strong> {t}') for i, t in enumerate(_TERMOS + _TERMOS, 1))
NOTIFICA = p('Você tem 3 avisos novos: duas respostas ao seu pedido e uma promoção que termina hoje.')


def congelados():
    out = []
    for tam, rot in (('sm', 'sm · 320'), ('md', 'md · 480'), ('lg', 'lg · 640')):
        d = drawer(f'frz-{tam}', 'Editar cliente', p('Conteúdo do painel. O miolo ocupa o que sobra '
                                                    'e é o único que rola.'),
                   btn('Cancelar', 'ghost', ' data-al-drawer-close') + btn('Salvar', 'primary'),
                   tam, ' open')
        out.append(f'<div class="qa-cell" inert aria-hidden="true" data-size="{tam}">'
                   f'<p class="qa-matrix__label">{rot}</p>{d}</div>')
    return ''.join(out)


def vivos():
    gatilhos = [
        ('d-detalhe', 'Detalhes do cliente',
         'Sem campos e sem rodapé: o foco entra no X; o clique no fundo fecha. “Excluir” abre um Modal por cima.'),
        ('d-editar', 'Editar cliente',
         'Com campos: o foco entra no primeiro campo; o clique no fundo NÃO fecha.'),
        ('d-termos', 'Termos de uso',
         'lg, conteúdo longo: só o miolo rola; cabeçalho e botões ficam. O foco entra em “Aceitar”.'),
        ('d-notifica', 'Notificações',
         'Sem X: a saída visível é o rodapé (regra 14).'),
    ]
    cards = ''.join(
        f'<div class="qa-trigger">{btn(rot, "secondary", f" data-al-drawer-open={chr(34)}{did}{chr(34)}")}'
        f'<p class="qa-pagenote">{nota}</p></div>' for did, rot, nota in gatilhos)
    dialogs = '\n'.join([
        drawer('d-detalhe', 'Detalhes do cliente', DETALHE, '', 'md'),
        drawer('d-editar', 'Editar cliente', FORM,
               btn('Cancelar', 'ghost', ' data-al-drawer-close') + btn('Salvar cliente', 'primary', ' data-al-drawer-close'), 'md'),
        drawer('d-termos', 'Termos de uso', LONGO,
               btn('Voltar', 'ghost', ' data-al-drawer-close') + btn('Aceitar', 'primary', ' data-al-drawer-close'), 'lg'),
        drawer('d-notifica', 'Notificações', NOTIFICA,
               btn('Dispensar', 'ghost', ' data-al-drawer-close') + btn('Ver todas', 'primary', ' data-al-drawer-close'),
               'sm', com_x=False),
        modal('m-excluir', 'Excluir cliente?', EXCLUIR,
              btn('Cancelar', 'ghost', ' data-al-modal-close') + btn('Excluir cliente', 'danger', ' data-al-modal-close')),
    ])
    return cards, dialogs


def build():
    css = []
    for nome, path in CSS_FILES:
        css.append(f'/* ================= {nome} ================= */')
        css.append(open(path, encoding='utf-8').read())
    css_inline = '\n'.join(css)
    js_inline = '\n'.join(open(f, encoding='utf-8').read() for f in JS_FILES)
    gatilhos, dialogs = vivos()

    meta = DRW['meta']
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
<title>AL Drawer QA</title>
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
  max-width: 1120px; margin: 0 auto;
  padding-inline: var(--al-space-16);
  padding-block: var(--al-space-32) var(--al-space-64);
  display: flex; flex-direction: column; gap: var(--al-space-48);
}}
.qa-head {{
  display: flex; flex-wrap: wrap; align-items: flex-end;
  justify-content: space-between; gap: var(--al-space-16);
  border-bottom: 1px solid var(--al-border-subtle); padding-bottom: var(--al-space-16);
}}
.qa-head h1 {{ margin: 0; font-size: var(--al-font-size-3xl); line-height: var(--al-line-height-3xl); font-weight: 600; letter-spacing: -0.02em; text-wrap: balance; }}
.qa-sub {{ margin: var(--al-space-4) 0 0; color: var(--al-text-secondary); font-size: var(--al-font-size-sm); }}
.qa-btn {{
  display: inline-flex; align-items: center; gap: var(--al-space-8);
  padding: var(--al-space-8) var(--al-space-16);
  border: 1px solid var(--al-border-strong); border-radius: var(--al-radius-full);
  background: var(--al-bg-surface-raised); color: var(--al-text-primary);
  font: inherit; font-size: var(--al-font-size-sm); cursor: pointer;
}}
.qa-btn:focus-visible {{ outline: none; box-shadow: var(--al-focus-ring-default); }}
section > h2 {{ margin: 0 0 var(--al-space-4); font-size: var(--al-font-size-xl); line-height: var(--al-line-height-xl); font-weight: 600; letter-spacing: -0.01em; }}
section > p.qa-lede {{ margin: 0 0 var(--al-space-20); color: var(--al-text-secondary); max-width: 66ch; }}
.qa-tag {{
  font-size: var(--al-font-size-xs); line-height: var(--al-line-height-xs);
  padding: 2px var(--al-space-8); border-radius: var(--al-radius-full);
  border: 1px solid var(--al-border-default); color: var(--al-text-secondary);
  white-space: nowrap; vertical-align: middle; margin-left: var(--al-space-8); font-weight: 400; letter-spacing: 0;
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

/* ---- especificos do Drawer ---- */
.qa-panel {{ padding: var(--al-space-24); border-radius: var(--al-radius-xl); background: var(--al-bg-surface); }}
.qa-matrix {{ display: flex; flex-wrap: wrap; gap: var(--al-space-24); align-items: flex-start; }}
.qa-matrix__label {{ margin: 0 0 var(--al-space-8); font-size: var(--al-font-size-xs); font-weight: 600; letter-spacing: 0.04em; text-transform: uppercase; color: var(--al-text-secondary); }}
/* o <dialog open> do UA e fixo e colado na direita; aqui ele e so uma caixa,
   com uma altura de exemplo no lugar da altura da tela */
.qa-cell {{ min-width: 0; max-width: 100%; }}
.qa-cell .al-drawer {{ position: static; inset: auto; max-inline-size: 100%; block-size: 360px; opacity: 1; translate: none; transition: none; }}
.qa-copy {{ margin: 0; color: var(--al-text-secondary); }}
.qa-fields {{ display: flex; flex-direction: column; gap: var(--al-space-16); }}
.al-drawer__content > .qa-copy + .qa-copy {{ margin-block-start: var(--al-space-12); }}
.qa-dl {{ margin: 0 0 var(--al-space-24); display: grid; gap: var(--al-space-12); }}
.qa-dl div {{ display: grid; gap: var(--al-space-4); }}
.qa-dl dt {{ font-size: var(--al-font-size-xs); line-height: var(--al-line-height-xs); color: var(--al-text-secondary); }}
.qa-dl dd {{ margin: 0; }}
.qa-triggers {{ display: grid; gap: var(--al-space-20); grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); }}
.qa-trigger {{ display: flex; flex-direction: column; gap: var(--al-space-8); align-items: flex-start; }}
.qa-pagenote {{ margin: 0; color: var(--al-text-secondary); font-size: var(--al-font-size-xs); line-height: var(--al-line-height-xs); }}
.qa-log {{ margin: var(--al-space-16) 0 0; font-size: var(--al-font-size-sm); color: var(--al-text-secondary); min-height: var(--al-line-height-sm); }}
</style>

<div class="qa-wrap">
  <header class="qa-head">
    <div>
      <h1>Drawer — QA da etapa 6</h1>
      <p class="qa-sub">AL Design System {FOUND['meta']['version']} · componente {meta['version']} ·
      3 tamanhos × 4 cenários × 2 temas{resumo}</p>
    </div>
    <button type="button" class="qa-btn" id="theme-toggle" aria-pressed="false">
      <span id="theme-label">Tema claro</span>
    </button>
  </header>

  <section>
    <h2>O que testar</h2>
    <ol class="qa-checks">
      <li><strong>Abra cada cenário</strong> e veja onde o foco cai: sem campos e sem rodapé, no X; com campos, no primeiro campo; com rodapé e sem campos, no botão principal (regra 27).</li>
      <li><strong>Tab e Shift+Tab</strong> rodam só dentro do Drawer e dão a volta; a página atrás não recebe foco (regra 24).</li>
      <li><strong>Esc fecha em todos</strong>, inclusive no formulário. O foco volta para o botão que abriu (regras 15 e 17) — a linha de registro abaixo diz onde ele caiu.</li>
      <li><strong>Clique no fundo escurecido</strong>: fecha em “Detalhes”, “Termos” e “Notificações”; NÃO fecha em “Editar cliente” (regra 16). Aperte dentro do campo, arraste e solte fora: não fecha.</li>
      <li><strong>Entrada e saída</strong>: o painel entra pela direita (da direita para a esquerda) e sai pela direita (da esquerda para a direita), com o fundo escurecendo e clareando. Ao fechar, nada dentro dele muda de forma (regra 30).</li>
      <li><strong>Role a roda do mouse</strong> sobre os “Termos de uso”: só o miolo rola, cabeçalho e botões ficam (regra 29). Role fora do Drawer: a página atrás não anda.</li>
      <li><strong>Em “Detalhes do cliente”, clique em “Excluir cliente”</strong>: um Modal abre por cima do Drawer. Esc fecha só o Modal e o foco volta para “Excluir cliente” (regras 22 e 17).</li>
      <li><strong>Troque o tema</strong> com um Drawer aberto, passe o mouse sobre o X e sobre “Cancelar”: no escuro o fundo do hover tem que aparecer (os estados -raised). Feche: o painel clareia sobre o fundo escurecido, sem contorno.</li>
      <li><strong>Tela estreita</strong> (≈375px): o Drawer deixa 16 de respiro à esquerda e nunca passa da tela (regra 12).</li>
      <li><strong>Leitor de tela</strong> (VoiceOver: Ctrl+Opção+→): anuncia “diálogo”, o título como nome, o X como “Fechar”, e o que está atrás fica mudo.</li>
      <li><strong>“Reduzir movimento”</strong> ligado nas preferências do sistema: abre e fecha sem deslizar.</li>
    </ol>
  </section>

  <section>
    <h2>Tamanhos congelados <span class="qa-tag qa-tag--simulado">simulado</span></h2>
    <p class="qa-lede">Um <code>&lt;dialog&gt;</code> real só existe aberto no topo da página, colado na
    direita e com a altura da tela. Aqui os três tamanhos ficam inline, lado a lado, com uma altura de exemplo,
    só para comparar com o Figma. Mesmo CSS; o que não existe é a camada de cima. Não recebem foco.</p>
    <div class="qa-panel"><div class="qa-matrix" id="matrix-frozen">{congelados()}</div></div>
  </section>

  <section>
    <h2>Ao vivo <span class="qa-tag qa-tag--real">real</span></h2>
    <p class="qa-lede">Abertos por <code>data-al-drawer-open</code> → <code>showModal()</code>, do
    <code>drawer.js</code> inlinado.</p>
    <div class="qa-panel">
      <div class="qa-triggers">{gatilhos}</div>
      <p class="qa-log" id="qa-log" role="status" aria-live="polite"></p>
    </div>
  </section>

  <section>
    <h2>Contraste medido no navegador</h2>
    <p class="qa-lede">Não são os números do <code>tokens.json</code>: o script lê a cor que o navegador
    pintou nos Drawers congelados e a do scrim composta sobre a página, com
    <code>getComputedStyle</code>, depois da transição terminar.</p>
    <div class="qa-tablewrap">
      <table class="qa-measure">
        <thead><tr><th>onde</th><th>o quê</th><th>cor</th><th>fundo</th><th>medido</th><th>piso</th><th>veredito</th></tr></thead>
        <tbody id="measure-body"></tbody>
      </table>
    </div>
  </section>

  <p class="qa-foot">Gerado por <code>components/drawer/qa.py</code> a partir do CSS e do JS commitados em
  <code>dev</code>. Foundation, Icon, Button, Icon Button, Input, Modal, <code>al-drawer-tokens.css</code>,
  <code>drawer.css</code> e <code>drawer.js</code> estão embutidos como estão no repositório.</p>
</div>

{dialogs}

<script>
{js_inline}
</script>
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
  function depois() {{
    setTimeout(function () {{
      Promise.all(document.getAnimations().map(function (a) {{ return a.finished; }}))
        .then(medir, medir);
    }}, 50);
  }}
  btn.addEventListener('click', function () {{
    root.dataset.theme = escuro() ? 'light' : 'dark';
    pintarBotao();
    depois();
  }});
  pintarBotao();

  // ------------------------------------------- registro (so cromo de QA)
  var log = r('qa-log');
  function nome(el) {{
    if (!el || el === document.body) return 'o corpo da página (foco perdido)';
    if (el.labels && el.labels.length) return 'o campo “' + el.labels[0].textContent.trim() + '”';
    var t =(el.textContent || '').trim().replace(/\\s+/g, ' ');
    return t ? '“' + t + '”' : (el.getAttribute('aria-label') ? 'o botão “' + el.getAttribute('aria-label') + '”' : '<' + el.tagName.toLowerCase() + '>');
  }}
  document.querySelectorAll('dialog.al-drawer[id^="d-"], dialog.al-modal[id^="m-"]').forEach(function (d) {{
    d.addEventListener('close', function () {{
      var t = d.querySelector('.al-drawer__title, .al-modal__title').textContent.trim();
      setTimeout(function () {{
        log.textContent = 'Fechou “' + t + '” — o foco voltou para ' + nome(document.activeElement);
      }}, 0);
    }});
  }});
  document.addEventListener('click', function (e) {{
    var o = e.target.closest && e.target.closest('[data-al-drawer-open], [data-al-modal-open]');
    if (!o) return;
    var alvo = document.getElementById(o.getAttribute('data-al-drawer-open') || o.getAttribute('data-al-modal-open'));
    setTimeout(function () {{
      if (alvo && alvo.open) log.textContent = 'Abriu — o foco entrou em ' + nome(document.activeElement);
    }}, 50);
  }});

  // ------------------------------------------------------------- contraste
  function rgb(str) {{
    var m = str && str.match(/rgba?\\(([^)]+)\\)/);
    if (!m) return null;
    var p = m[1].split(/[ ,\\/]+/).filter(Boolean).map(function (x) {{ return +x; }});
    return [p[0], p[1], p[2], p[3] === undefined ? 1 : p[3]];
  }}
  function lin(c) {{ c /= 255; return c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4); }}
  function lum(c) {{ return 0.2126 * lin(c[0]) + 0.7152 * lin(c[1]) + 0.0722 * lin(c[2]); }}
  function cr(a, b) {{
    var la = lum(a), lb = lum(b);
    return (Math.max(la, lb) + 0.05) / (Math.min(la, lb) + 0.05);
  }}
  function sobre(fg, base) {{
    var a = fg[3];
    return [0, 1, 2].map(function (i) {{ return Math.round(fg[i] * a + base[i] * (1 - a)); }}).concat([1]);
  }}
  function css(c) {{ return 'rgb(' + c.slice(0, 3).join(', ') + ')'; }}
  function cor(tokenVar, prop) {{
    var t = document.createElement('div');
    t.style.cssText = 'position:absolute;visibility:hidden;' + prop + ':var(' + tokenVar + ')';
    document.body.appendChild(t);
    var v = rgb(getComputedStyle(t)[prop === 'color' ? 'color' : 'backgroundColor']);
    t.remove();
    return v;
  }}
  function linha(where, what, fg, bg, piso, exc, modo) {{
    var v = cr(fg, bg);
    var distinto = css(fg) !== css(bg);
    var ok = modo === 'distinto' ? distinto : v >= piso;
    var classe = ok ? 'ok' : exc ? 'exc' : 'bad';
    var texto = ok ? (modo === 'distinto' ? 'diferente do painel' : 'passa') : exc ? 'exceção declarada' : (modo === 'distinto' ? 'IGUAL AO PAINEL' : 'REPROVA');
    var tr = document.createElement('tr');
    [where, what, css(fg), css(bg), v.toFixed(2) + ':1', modo === 'distinto' ? '≠' : piso.toFixed(1) + ':1'].forEach(function (x) {{
      var td = document.createElement('td'); td.textContent = x; tr.appendChild(td);
    }});
    var td = document.createElement('td');
    td.textContent = texto; td.className = 'qa-verdict qa-verdict--' + classe;
    tr.appendChild(td);
    r('measure-body').appendChild(tr);
  }}

  // le a cor que uma custom property do botao resolve (o hover -raised), pondo
  // uma sonda DENTRO do botao: a propriedade nao herda para fora dele
  function viaBotao(btnEl, prop) {{
    var t = document.createElement('i');
    t.style.cssText = 'position:absolute;visibility:hidden;background-color:var(' + prop + ')';
    btnEl.appendChild(t);
    var v = rgb(getComputedStyle(t).backgroundColor);
    t.remove();
    return v;
  }}

  function medir() {{
    r('measure-body').textContent = '';
    var tema = escuro() ? 'escuro' : 'claro';
    var scrim = cor('--al-drawer-scrim', 'background-color');
    document.querySelectorAll('#matrix-frozen .qa-cell').forEach(function (cell) {{
      var d = cell.querySelector('.al-drawer');
      var cs = getComputedStyle(d);
      var card = rgb(cs.backgroundColor);
      var onde = 'Drawer ' + cell.dataset.size + ' · ' + tema;
      linha(onde, 'título', rgb(getComputedStyle(d.querySelector('.al-drawer__title')).color), card, 4.5);
      linha(onde, 'texto do miolo', rgb(getComputedStyle(d.querySelector('.al-drawer__content p')).color), card, 4.5);
      linha(onde, 'ícone do X', rgb(getComputedStyle(d.querySelector('.al-icon-btn .al-icon')).color), card, 3);
      var ghost = d.querySelector('.al-drawer__actions .al-btn--ghost');
      var x = d.querySelector('.al-icon-btn');
      if (cell.dataset.size === 'md') {{
        linha(onde, 'hover do Ghost', viaBotao(ghost, '--_bg-hover'), card, 1, false, 'distinto');
        linha(onde, 'pressed do Ghost', viaBotao(ghost, '--_bg-active'), card, 1, false, 'distinto');
        linha(onde, 'hover do X', viaBotao(x, '--_bg-hover'), card, 1, false, 'distinto');
      }}
    }});
    ['--al-bg-canvas', '--al-bg-surface'].forEach(function (v) {{
      var pagina = cor(v, 'background-color');
      var card = cor('--al-drawer-bg', 'background-color');
      linha('Painel × página escurecida · ' + tema, v.replace('--al-', '') + ' + scrim',
            card, sobre(scrim, pagina), 3, true);
    }});
  }}

  if (document.fonts && document.fonts.ready) {{
    document.fonts.ready.then(depois);
  }} else {{
    depois();
  }}
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function () {{
    pintarBotao(); depois();
  }});
}})();
</script>
'''


if __name__ == '__main__':
    html = build()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, 'w', encoding='utf-8').write(html)
    print(f'site/drawer-qa.html escrito ({len(html)} bytes)')
    print(f'  CSS embutido: {", ".join(n for n, _ in CSS_FILES)}')
    corpo = re.sub(r'<style\b[^>]*>.*?</style>', '', html, flags=re.S)
    corpo = re.sub(r'<script\b[^>]*>.*?</script>', '', corpo, flags=re.S)
    n = len(re.findall(r'<dialog class="al-drawer', corpo))
    print(f'  dialogs de verdade no documento: {n}')
