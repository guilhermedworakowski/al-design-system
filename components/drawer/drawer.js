/* AL Design System - Drawer, comportamento
 *
 * O <dialog> nativo ja faz o grosso (regra 24): prende o foco, deixa a pagina
 * inerte, fecha com Esc (regra 15) e devolve o foco a quem abriu (regra 17).
 * Este arquivo cobre so o que o nativo nao faz:
 *   - abrir e fechar por atributo, sem JS na pagina:
 *       data-al-drawer-open="<id>"   no botao que abre
 *       data-al-drawer-close         no botao que fecha (dentro do dialog)
 *   - clique no scrim fecha SO quando nao ha campos (regra 16). Com campo, o
 *     clique acidental perderia o que foi digitado;
 *   - foco inicial (regra 27), quando a marcacao nao pede um com `autofocus`.
 *     O nativo foca o primeiro focavel na ordem do documento, e no Drawer esse
 *     e o X do cabecalho; por isso a ordem aqui e explicita:
 *       com campo        -> o primeiro campo do miolo
 *       sem campo        -> a acao principal (a ultima do rodape)
 *       sem rodape       -> o X (o nativo ja faz, nao mexe)
 *
 * Fechar com mudanca nao salva e do formulario, nao deste arquivo (regra 19):
 * ele escuta o evento `cancel` do <dialog> e decide.
 *
 * Uso:
 *   carregar este arquivo com um script src  -> liga sozinho quando a pagina carrega
 *   alDrawers.init(container)                -> liga em conteudo inserido depois
 * Ligar duas vezes o mesmo dialog nao duplica nada.
 */
(function () {
  'use strict';

  var FIELDS = 'input:not([type="hidden"]), select, textarea, [contenteditable=""], [contenteditable="true"]';
  var FOCUSABLE_FIELD = 'input:not([type="hidden"]):not([disabled]), select:not([disabled]), textarea:not([disabled]), [contenteditable=""], [contenteditable="true"]';

  function hasFields(dialog) {
    return !!dialog.querySelector(FIELDS);
  }

  function inside(dialog, x, y) {
    var r = dialog.getBoundingClientRect();
    return x >= r.left && x <= r.right && y >= r.top && y <= r.bottom;
  }

  function initialFocus(dialog) {
    if (dialog.querySelector('[autofocus]')) return;   // a marcacao decidiu
    var content = dialog.querySelector('.al-drawer__content');
    var field = content && content.querySelector(FOCUSABLE_FIELD);
    if (field) { field.focus(); return; }               // regra 27: o primeiro campo
    var actions = dialog.querySelectorAll('.al-drawer__actions button, .al-drawer__actions a[href]');
    if (actions.length) actions[actions.length - 1].focus();   // regra 27: a principal
  }

  function bind(dialog) {
    if (dialog.hasAttribute('data-al-drawer')) return;
    dialog.setAttribute('data-al-drawer', '');

    // O clique so conta se o aperto E a soltura foram no scrim: arrastar para
    // selecionar texto dentro do Drawer e soltar fora nao fecha nada.
    var pressedOnScrim = false;
    dialog.addEventListener('pointerdown', function (e) {
      pressedOnScrim = e.target === dialog && !inside(dialog, e.clientX, e.clientY);
    });
    dialog.addEventListener('click', function (e) {
      var onScrim = e.target === dialog && !inside(dialog, e.clientX, e.clientY);
      if (onScrim && pressedOnScrim && !hasFields(dialog)) dialog.close();   // regra 16
      pressedOnScrim = false;
    });

    // foco inicial: observa o `open`, porque quem abre pode ser o atributo de
    // dados ou um showModal() de fora
    new MutationObserver(function () {
      if (dialog.open) initialFocus(dialog);
    }).observe(dialog, { attributes: true, attributeFilter: ['open'] });
  }

  function init(root) {
    [].slice.call((root || document).querySelectorAll('dialog.al-drawer')).forEach(bind);
  }

  // Abrir e fechar por atributo: delegado no documento, uma vez so, entao
  // vale tambem para botao inserido depois.
  document.addEventListener('click', function (e) {
    var opener = e.target.closest && e.target.closest('[data-al-drawer-open]');
    if (opener) {
      var dialog = document.getElementById(opener.getAttribute('data-al-drawer-open'));
      if (dialog && typeof dialog.showModal === 'function' && !dialog.open) {
        bind(dialog);
        dialog.showModal();
      }
      return;
    }
    var closer = e.target.closest && e.target.closest('[data-al-drawer-close]');
    if (closer) {
      var host = closer.closest('dialog');
      if (host) host.close();
    }
  });

  window.alDrawers = { init: init };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () { init(); });
  } else {
    init();
  }
})();
