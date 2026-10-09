/* AL Design System - Drawer, behavior
 *
 * The native <dialog> already does the bulk (rule 24): it traps focus, makes
 * the page inert, closes with Esc (rule 15) and returns focus to the opener
 * (rule 17). This file only covers what the native one doesn't:
 *   - opening and closing by attribute, with no JS on the page:
 *       data-al-drawer-open="<id>"   on the button that opens
 *       data-al-drawer-close         on the button that closes (inside the dialog)
 *   - a click on the scrim closes ONLY when there are no fields (rule 16).
 *     With a field, an accidental click would lose what was typed;
 *   - initial focus (rule 27), when the markup doesn't ask for one with
 *     `autofocus`. The native one focuses the first focusable in document
 *     order, and in the Drawer that is the header's X; that is why the order
 *     here is explicit:
 *       with a field     -> the first field in the body
 *       no field         -> the main action (the last one in the footer)
 *       no footer        -> the X (the native one already does it)
 *
 * Closing with unsaved changes belongs to the form, not to this file
 * (rule 19): it listens to the <dialog>'s `cancel` event and decides.
 *
 * Usage:
 *   load this file with a script src  -> binds by itself when the page loads
 *   alDrawers.init(container)         -> binds content inserted later
 * Binding the same dialog twice duplicates nothing.
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
    if (dialog.querySelector('[autofocus]')) return;   // the markup decided
    var content = dialog.querySelector('.al-drawer__content');
    var field = content && content.querySelector(FOCUSABLE_FIELD);
    if (field) { field.focus(); return; }               // rule 27: the first field
    var actions = dialog.querySelectorAll('.al-drawer__actions button, .al-drawer__actions a[href]');
    if (actions.length) actions[actions.length - 1].focus();   // rule 27: the main one
  }

  function bind(dialog) {
    if (dialog.hasAttribute('data-al-drawer')) return;
    dialog.setAttribute('data-al-drawer', '');

    // The click only counts if the press AND the release were on the scrim:
    // dragging to select text inside the Drawer and releasing outside closes nothing.
    var pressedOnScrim = false;
    dialog.addEventListener('pointerdown', function (e) {
      pressedOnScrim = e.target === dialog && !inside(dialog, e.clientX, e.clientY);
    });
    dialog.addEventListener('click', function (e) {
      var onScrim = e.target === dialog && !inside(dialog, e.clientX, e.clientY);
      if (onScrim && pressedOnScrim && !hasFields(dialog)) dialog.close();   // rule 16
      pressedOnScrim = false;
    });

    // initial focus: watches `open`, because the opener may be the data
    // attribute or a showModal() from outside
    new MutationObserver(function () {
      if (dialog.open) initialFocus(dialog);
    }).observe(dialog, { attributes: true, attributeFilter: ['open'] });
  }

  function init(root) {
    [].slice.call((root || document).querySelectorAll('dialog.al-drawer')).forEach(bind);
  }

  // Opening and closing by attribute: delegated on the document, only once, so
  // it also works for a button inserted later.
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
