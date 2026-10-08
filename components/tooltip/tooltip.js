/* AL Design System - Tooltip (regras 13 a 20)
 *
 * Quem liga gatilho e tooltip e o ARIA do gatilho, nao uma classe:
 *   aria-labelledby="<id>"   o tooltip e o nome do gatilho
 *   aria-describedby="<id>"  o tooltip complementa um gatilho que ja tem nome
 * Este arquivo so cuida de MOSTRAR e ESCONDER. O nome e a descricao funcionam
 * sem ele: o leitor de tela le o tooltip escondido pelo atributo.
 *
 *   - hover: abre depois de `tooltip-delay-show` (500ms). Se outro tooltip ja
 *     esta aberto, troca na hora - quem esta lendo uma fileira de botoes nao
 *     espera de novo a cada um (regra 16);
 *   - foco por teclado (:focus-visible): abre na hora. Foco por clique nao
 *     abre (regras 16 e 20);
 *   - toque nao abre, clique fecha (regra 20);
 *   - fica aberto enquanto o ponteiro esta no gatilho OU no tooltip, ou o
 *     foco de teclado esta no gatilho; `tooltip-delay-hide` (100ms) de folga
 *     para o ponteiro atravessar o vao de 4 (regra 17, WCAG 1.4.13);
 *   - Esc fecha sem mover o foco, e o Esc para ai: com um tooltip aberto
 *     dentro de um Modal, o primeiro Esc fecha so o tooltip (regra 18);
 *   - um aberto por vez (regra 19);
 *   - lado: data-placement do .al-tooltip, top por padrao; vira para o
 *     oposto se nao couber, e acompanha rolagem e redimensionamento (regras
 *     13 e 15).
 * Os tempos e a distancia sao lidos dos tokens no CSS, nunca escritos aqui.
 *
 * Uso:
 *   <script src="tooltip.js"></script>   -> liga sozinho quando a pagina carrega
 *   alTooltip.init(container)             -> liga em conteudo inserido depois
 * Ligar duas vezes o mesmo gatilho nao duplica nada. Navegador sem popover:
 * o tooltip nunca aparece, e o nome continua chegando ao leitor de tela.
 */
(function () {
  'use strict';

  var OPPOSITE = { top: 'bottom', bottom: 'top', left: 'right', right: 'left' };
  var current = null;          // { trigger, tip }
  var showTimer = 0;
  var hideTimer = 0;

  function token(tip, name) {
    return parseFloat(getComputedStyle(tip).getPropertyValue('--al-tooltip-' + name)) || 0;
  }

  function clamp(v, lo, hi) { return hi < lo ? lo : Math.max(lo, Math.min(v, hi)); }

  function place(trigger, tip) {
    var r = trigger.getBoundingClientRect();
    var w = tip.offsetWidth;
    var h = tip.offsetHeight;
    var gap = token(tip, 'offset');
    var vw = document.documentElement.clientWidth;
    var vh = document.documentElement.clientHeight;
    var room = { top: r.top - gap, bottom: vh - r.bottom - gap, left: r.left - gap, right: vw - r.right - gap };
    var need = { top: h, bottom: h, left: w, right: w };
    var pref = OPPOSITE[tip.getAttribute('data-placement')] ? tip.getAttribute('data-placement') : 'top';
    var opp = OPPOSITE[pref];
    var side = room[pref] >= need[pref] ? pref
      : room[opp] >= need[opp] ? opp
      : room[pref] >= room[opp] ? pref : opp;
    var x, y;
    if (side === 'top' || side === 'bottom') {
      x = clamp(r.left + r.width / 2 - w / 2, gap, vw - w - gap);
      y = side === 'top' ? r.top - gap - h : r.bottom + gap;
    } else {
      x = side === 'left' ? r.left - gap - w : r.right + gap;
      y = clamp(r.top + r.height / 2 - h / 2, gap, vh - h - gap);
    }
    tip.style.left = Math.round(x) + 'px';
    tip.style.top = Math.round(y) + 'px';
    tip.setAttribute('data-side', side);
  }

  function hide() {
    clearTimeout(showTimer);
    clearTimeout(hideTimer);
    if (!current) return;
    if (current.tip.matches(':popover-open')) current.tip.hidePopover();
    current = null;
  }

  function show(trigger, tip) {
    clearTimeout(showTimer);
    clearTimeout(hideTimer);
    if (current && current.tip === tip) return;
    hide();                                         // um por vez
    if (trigger.disabled || !trigger.isConnected) return;
    tip.showPopover();
    place(trigger, tip);
    current = { trigger: trigger, tip: tip };
  }

  function keyboardFocused(el) {
    return el === document.activeElement && el.matches(':focus-visible');
  }

  function scheduleHide(trigger, tip) {
    clearTimeout(hideTimer);
    hideTimer = setTimeout(function () {
      if (!current || current.tip !== tip) return;
      if (trigger.matches(':hover') || tip.matches(':hover') || keyboardFocused(trigger)) return;
      hide();
    }, token(tip, 'delay-hide'));
  }

  function bind(trigger, tip) {
    if (trigger.hasAttribute('data-al-tooltip')) return;
    trigger.setAttribute('data-al-tooltip', '');

    trigger.addEventListener('pointerenter', function (e) {
      if (e.pointerType === 'touch') return;
      clearTimeout(hideTimer);
      if (current) { show(trigger, tip); return; }   // ja tem um aberto: troca na hora
      clearTimeout(showTimer);
      showTimer = setTimeout(function () { show(trigger, tip); }, token(tip, 'delay-show'));
    });
    trigger.addEventListener('pointerleave', function () {
      clearTimeout(showTimer);
      scheduleHide(trigger, tip);
    });
    trigger.addEventListener('pointerdown', hide);
    trigger.addEventListener('focus', function () {
      if (trigger.matches(':focus-visible')) show(trigger, tip);
    });
    trigger.addEventListener('blur', function () {
      if (current && current.tip === tip) scheduleHide(trigger, tip);
    });

    if (tip.hasAttribute('data-al-tooltip')) return;
    tip.setAttribute('data-al-tooltip', '');
    tip.addEventListener('pointerenter', function () { clearTimeout(hideTimer); });
    tip.addEventListener('pointerleave', function () {
      if (current && current.tip === tip) scheduleHide(current.trigger, tip);
    });
  }

  function init(root) {
    var scope = root || document;
    [].forEach.call(scope.querySelectorAll('.al-tooltip[id][popover]'), function (tip) {
      if (typeof tip.showPopover !== 'function') return;
      var id = CSS.escape(tip.id);
      [].forEach.call(document.querySelectorAll(
        '[aria-labelledby~="' + id + '"], [aria-describedby~="' + id + '"]'), function (trigger) {
        bind(trigger, tip);
      });
    });
  }

  // Esc na captura: fecha o tooltip antes de o Modal ou o Drawer ouvirem.
  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape' || !current) return;
    e.preventDefault();
    e.stopPropagation();
    hide();
  }, true);

  function follow() { if (current) place(current.trigger, current.tip); }
  window.addEventListener('scroll', follow, { capture: true, passive: true });
  window.addEventListener('resize', follow, { passive: true });

  window.alTooltip = { init: init, hide: hide };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () { init(); });
  } else {
    init();
  }
})();
