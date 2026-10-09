/* AL Design System - Toast (regras 15 a 24)
 *
 * A marcacao do toast mora na pagina, num <template>; este arquivo so cuida
 * de MOSTRAR, CRONOMETRAR e TIRAR. Ver o contrato no cabecalho do toast.css.
 *
 *   - um por vez: quem chega com outro na tela espera na fila (regra 15);
 *   - Success e Info saem depois de `toast-timeout` (6000ms); o relogio pausa
 *     com o ponteiro em cima ou o foco dentro, e retoma de onde parou
 *     (regra 17);
 *   - Warning e Error so saem pelo X ou pelo Esc - e seguram a fila (regra 18);
 *   - o X fecha sempre; Esc fecha com o foco dentro do toast, e o Esc para ai:
 *     sobre um Modal, o primeiro Esc fecha so o toast (regra 19);
 *   - nunca move o foco para o toast (regra 21). Se a pessoa tabulou ate o X
 *     e o toast saiu, o foco volta para onde ela estava antes de entrar;
 *   - Error entra na regiao role="alert", os outros na role="status"
 *     (regra 22). As duas regioes ja existem na pagina (regra 23).
 * O tempo na tela e a duracao da saida sao lidos dos tokens no CSS, nunca
 * escritos aqui.
 *
 * Uso:
 *   <script src="toast.js"></script>
 *   alToast.show('toast-salvo')                        -> clona o <template id>
 *   alToast.show(tpl, { title: '…', description: '…' }) -> troca os textos
 *   alToast.dismiss()                                  -> tira o da tela
 *   alToast.clear()                                    -> esvazia a fila e tira o da tela
 * Navegador sem popover: a regiao fica no fluxo, no fim da pagina, e o anuncio
 * continua chegando ao leitor de tela.
 */
(function () {
  'use strict';

  var queue = [];
  var current = null;   // { el, timer, remaining, started, hover, focus, returnTo }

  function token(el, name) {
    return parseFloat(getComputedStyle(el).getPropertyValue('--al-toast-' + name)) || 0;
  }

  function region() {
    return document.querySelector('.al-toast-region');
  }

  // A regiao fica aberta para sempre. Um Modal ou Drawer aberto (dialog:modal)
  // torna INERTE tudo que esta fora dele - inclusive a regiao, mesmo desenhada
  // por cima: o X nao recebe clique nem foco e o leitor de tela deixa de ver o
  // toast. Entao, enquanto houver um aberto, a regiao mora DENTRO dele, e volta
  // para o <body> quando ele fecha. Mover tira o popover da top layer; abrir de
  // novo a poe no topo, acima do proprio dialog.
  function host() {
    var open = document.querySelectorAll('dialog:modal');
    return open.length ? open[open.length - 1] : document.body;
  }

  function home(r) {
    document.body.appendChild(r);
    if (!r.matches(':popover-open')) r.showPopover();
  }

  function raise(r) {
    if (typeof r.showPopover !== 'function') return;
    var h = host();
    if (r.parentNode !== h) {
      h.appendChild(r);
      // Observa o atributo `open` em vez do evento `close`: o observer roda
      // logo depois do close(), o evento espera uma tarefa da fila.
      if (h !== document.body) {
        var watch = new MutationObserver(function () {
          if (h.open) return;
          watch.disconnect();
          home(r);
        });
        watch.observe(h, { attributes: true, attributeFilter: ['open'] });
      }
    }
    if (!r.matches(':popover-open')) r.showPopover();
  }

  function persistent(el) {
    return el.classList.contains('al-toast--warning') || el.classList.contains('al-toast--error');
  }

  // ---------------------------------------------------------------- relogio
  function stopClock() {
    if (!current || !current.timer) return;
    clearTimeout(current.timer);
    current.timer = 0;
    current.remaining -= Date.now() - current.started;
  }

  function startClock() {
    if (!current || current.timer || persistent(current.el)) return;
    if (current.hover || current.focus) return;
    var el = current.el;
    current.started = Date.now();
    current.timer = setTimeout(function () { dismiss(el); }, Math.max(current.remaining, 0));
  }

  // --------------------------------------------------------------- entra/sai
  function build(source, text) {
    var tpl = typeof source === 'string' ? document.getElementById(source) : source;
    if (!tpl) return null;
    var root = tpl.content ? tpl.content.firstElementChild : tpl;
    if (!root || !root.classList.contains('al-toast')) return null;
    var el = root.cloneNode(true);
    if (text && text.title != null) el.querySelector('.al-toast__title').textContent = text.title;
    if (text && text.description != null) {
      var d = el.querySelector('.al-toast__description');
      if (text.description === '') { if (d) d.remove(); }
      else if (d) d.textContent = text.description;
    }
    return el;
  }

  function bind(el) {
    el.addEventListener('pointerenter', function () {
      if (!current || current.el !== el) return;
      current.hover = true; stopClock();
    });
    el.addEventListener('pointerleave', function () {
      if (!current || current.el !== el) return;
      current.hover = false; startClock();
    });
    el.addEventListener('focusin', function (e) {
      if (!current || current.el !== el) return;
      if (e.relatedTarget && !el.contains(e.relatedTarget)) current.returnTo = e.relatedTarget;
      current.focus = true; stopClock();
    });
    el.addEventListener('focusout', function (e) {
      if (!current || current.el !== el || el.contains(e.relatedTarget)) return;
      current.focus = false; startClock();
    });
    el.addEventListener('click', function (e) {
      if (e.target.closest('.al-toast__close')) dismiss(el);
    });
    el.addEventListener('keydown', function (e) {
      if (e.key !== 'Escape') return;
      e.preventDefault();
      e.stopPropagation();
      dismiss(el);
    });
  }

  function next() {
    if (current || !queue.length) return;
    var r = region();
    if (!r) return;
    var el = queue.shift();
    raise(r);
    var live = r.querySelector(el.classList.contains('al-toast--error') ? '[role="alert"]' : '[role="status"]');
    if (!live) return;
    bind(el);
    live.appendChild(el);
    current = { el: el, timer: 0, remaining: token(el, 'timeout'), started: 0,
                hover: false, focus: false, returnTo: null };
    startClock();
  }

  function show(source, text) {
    var el = build(source, text);
    if (!el) return null;
    queue.push(el);
    next();
    return el;
  }

  function dismiss(el) {
    if (!current || (el && current.el !== el) || current.el.hasAttribute('data-leaving')) return;
    var gone = current;
    clearTimeout(gone.timer);
    if (gone.el.contains(document.activeElement)) {
      if (gone.returnTo && gone.returnTo.isConnected) gone.returnTo.focus();
      else document.activeElement.blur();
    }
    var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var wait = reduce ? 0 : token(gone.el, 'duration');
    gone.el.setAttribute('data-leaving', '');
    setTimeout(function () {
      gone.el.remove();
      if (current === gone) current = null;
      next();
    }, wait);
  }

  function clear() {
    queue.length = 0;
    dismiss();
  }

  function init() {
    var r = region();
    if (r && typeof r.showPopover === 'function' && !r.matches(':popover-open')) r.showPopover();
  }

  window.alToast = { show: show, dismiss: dismiss, clear: clear };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
