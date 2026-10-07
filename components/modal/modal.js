/* AL Design System - Modal, comportamento
 *
 * O <dialog> nativo ja faz o grosso (regra 24): prende o foco, deixa a pagina
 * inerte, fecha com Esc (regra 15) e devolve o foco a quem abriu (regra 17).
 * Este arquivo cobre so o que o nativo nao faz:
 *   - abrir e fechar por atributo, sem JS na pagina:
 *       data-al-modal-open="<id>"   no botao que abre
 *       data-al-modal-close         no botao que fecha (dentro do dialog)
 *   - clique no scrim fecha SO quando nao ha campos (regra 14). Com campo, o
 *     clique acidental perderia o que foi digitado;
 *   - foco inicial (regras 26 e 29), quando a marcacao nao pede um com
 *     `autofocus`:
 *       com campo        -> o primeiro campo (o nativo ja faz, nao mexe)
 *       sem campo        -> a acao principal (a ultima do rodape)
 *       principal Danger -> a acao SECUNDARIA: o Enter nao pode ficar a um
 *                           toque de apagar (regras 23 e 29)
 *
 * Uso:
 *   <script src="modal.js"></script>   -> liga sozinho quando a pagina carrega
 *   alModals.init(container)            -> liga em conteudo inserido depois
 * Ligar duas vezes o mesmo dialog nao duplica nada.
 */
(function () {
  'use strict';

  var FIELDS = 'input:not([type="hidden"]), select, textarea, [contenteditable=""], [contenteditable="true"]';
  var DANGER = '.al-btn--danger';

  function hasFields(dialog) {
    return !!dialog.querySelector(FIELDS);
  }

  function inside(dialog, x, y) {
    var r = dialog.getBoundingClientRect();
    return x >= r.left && x <= r.right && y >= r.top && y <= r.bottom;
  }

  function initialFocus(dialog) {
    if (dialog.querySelector('[autofocus]')) return;   // a marcacao decidiu
    if (hasFields(dialog)) return;                      // regra 26: o nativo foca o campo
    var actions = dialog.querySelectorAll('.al-modal__actions button, .al-modal__actions a[href]');
    if (!actions.length) return;
    var primary = actions[actions.length - 1];
    var target = primary.matches(DANGER) ? actions[0] : primary;   // regra 29
    target.focus();
  }

  function bind(dialog) {
    if (dialog.hasAttribute('data-al-modal')) return;
    dialog.setAttribute('data-al-modal', '');

    // O clique so conta se o aperto E a soltura foram no scrim: arrastar para
    // selecionar texto dentro do Modal e soltar fora nao fecha nada.
    var pressedOnScrim = false;
    dialog.addEventListener('pointerdown', function (e) {
      pressedOnScrim = e.target === dialog && !inside(dialog, e.clientX, e.clientY);
    });
    dialog.addEventListener('click', function (e) {
      var onScrim = e.target === dialog && !inside(dialog, e.clientX, e.clientY);
      if (onScrim && pressedOnScrim && !hasFields(dialog)) dialog.close();   // regra 14
      pressedOnScrim = false;
    });

    // foco inicial: observa o `open`, porque quem abre pode ser o atributo de
    // dados ou um showModal() de fora
    new MutationObserver(function () {
      if (dialog.open) initialFocus(dialog);
    }).observe(dialog, { attributes: true, attributeFilter: ['open'] });
  }

  function init(root) {
    [].slice.call((root || document).querySelectorAll('dialog.al-modal')).forEach(bind);
  }

  // Abrir e fechar por atributo: delegado no documento, uma vez so, entao
  // vale tambem para botao inserido depois.
  document.addEventListener('click', function (e) {
    var opener = e.target.closest && e.target.closest('[data-al-modal-open]');
    if (opener) {
      var dialog = document.getElementById(opener.getAttribute('data-al-modal-open'));
      if (dialog && typeof dialog.showModal === 'function' && !dialog.open) {
        bind(dialog);
        dialog.showModal();
      }
      return;
    }
    var closer = e.target.closest && e.target.closest('[data-al-modal-close]');
    if (closer) {
      var host = closer.closest('dialog');
      if (host) host.close();
    }
  });

  window.alModals = { init: init };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () { init(); });
  } else {
    init();
  }
})();
