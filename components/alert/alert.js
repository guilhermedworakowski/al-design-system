/* AL Design System - Alert (regras 11, 20 a 25)
 *
 * O Alert e marcacao comum da pagina (contrato no cabecalho do alert.css).
 * Este arquivo so cuida de FECHAR e de INSERIR DEPOIS do carregamento:
 *
 *   - o X ([data-al-alert-close]) tira o Alert com fade de saida e dispara o
 *     evento `al-alert-close` no slot, para o produto guardar a escolha e o
 *     Alert nao voltar na proxima visita (regra 21);
 *   - se o foco estava dentro, ele vai para o proximo elemento focavel depois
 *     do Alert; sem nenhum, para o <main> (regra 22). Nunca se perde no body;
 *   - alAlert.show() poe um Alert vindo de um <template> no slot. Um por
 *     pagina: o que estava la sai (regra 11). Ele entra numa regiao viva que
 *     nasce VAZIA e so depois recebe o Alert - regiao que nasce junto com a
 *     mensagem nao e anunciada. Danger vai em role="alert", os outros em
 *     role="status" (regra 24). O foco nao se move (regra 25).
 *   - Alert presente no carregamento nao ganha role nenhum (regra 23).
 * A duracao da saida e lida do token no CSS, nunca escrita aqui.
 *
 * Uso:
 *   <script src="alert.js"></script>
 *   alAlert.show('alert-plano')                       -> clona o <template id> no .al-alert-slot
 *   alAlert.show(tpl, { slot: el })                   -> noutro slot
 *   alAlert.dismiss(el)                               -> tira o Alert (o mesmo que o X)
 *   slot.addEventListener('al-alert-close', e => …)    -> e.detail.alert e o que saiu
 */
(function () {
  'use strict';

  var FOCUSABLE = 'a[href], button:not([disabled]), input:not([disabled]):not([type="hidden"]), ' +
    'select:not([disabled]), textarea:not([disabled]), summary, [tabindex]:not([tabindex="-1"])';

  function token(el, name) {
    return parseFloat(getComputedStyle(el).getPropertyValue('--al-alert-' + name)) || 0;
  }

  function reduced() {
    return window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  }

  function visible(el) {
    return !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length);
  }

  // Regra 22: o proximo focavel DEPOIS do Alert na ordem do documento.
  function nextFocus(alert) {
    var all = document.querySelectorAll(FOCUSABLE);
    for (var i = 0; i < all.length; i++) {
      var el = all[i];
      if (alert.contains(el) || !visible(el)) continue;
      if (alert.compareDocumentPosition(el) & Node.DOCUMENT_POSITION_FOLLOWING) return el;
    }
    var main = document.querySelector('main');
    if (main && !main.hasAttribute('tabindex')) main.setAttribute('tabindex', '-1');
    return main;
  }

  function dismiss(alert) {
    if (!alert || alert.hasAttribute('data-leaving')) return;
    var slot = alert.closest('.al-alert-slot') || alert.parentNode;
    var live = alert.parentNode && alert.parentNode.classList.contains('al-alert-live')
      ? alert.parentNode : null;

    if (alert.contains(document.activeElement)) {
      var to = nextFocus(alert);
      if (to) to.focus();
    }

    alert.setAttribute('data-leaving', '');
    var ms = reduced() ? 0 : token(alert, 'duration');
    setTimeout(function () {
      (live || alert).remove();
      if (slot) slot.dispatchEvent(new CustomEvent('al-alert-close', { detail: { alert: alert } }));
    }, ms);
  }

  function show(tpl, opts) {
    opts = opts || {};
    if (typeof tpl === 'string') tpl = document.getElementById(tpl);
    if (!tpl) return null;
    var slot = opts.slot || document.querySelector('.al-alert-slot');
    if (!slot) return null;

    var alert = tpl.content.querySelector('.al-alert').cloneNode(true);

    // Regra 11: um por pagina. O anterior sai na hora, sem fade - o novo
    // ocupa o mesmo lugar.
    var old = slot.querySelectorAll('.al-alert-live, .al-alert');
    for (var i = 0; i < old.length; i++) {
      if (old[i].parentNode === slot) old[i].remove();
    }

    var live = document.createElement('div');
    live.className = 'al-alert-live';
    live.setAttribute('role', alert.classList.contains('al-alert--danger') ? 'alert' : 'status');
    slot.appendChild(live);
    // A regiao precisa existir vazia antes da mensagem para o leitor anunciar.
    setTimeout(function () { live.appendChild(alert); }, 50);
    return alert;
  }

  document.addEventListener('click', function (e) {
    var btn = e.target.closest && e.target.closest('[data-al-alert-close]');
    if (!btn) return;
    dismiss(btn.closest('.al-alert'));
  });

  window.alAlert = { show: show, dismiss: dismiss };
})();
