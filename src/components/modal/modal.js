/* AL Design System - Modal, behavior
 *
 * The native <dialog> already does the bulk (rule 24): it traps focus, makes
 * the page inert, closes with Esc (rule 15) and returns focus to the opener
 * (rule 17). This file only covers what the native one doesn't:
 *   - opening and closing by attribute, with no JS on the page:
 *       data-al-modal-open="<id>"   on the button that opens
 *       data-al-modal-close         on the button that closes (inside the dialog)
 *   - a click on the scrim closes ONLY when there are no fields (rule 14).
 *     With a field, an accidental click would lose what was typed;
 *   - initial focus (rules 26 and 29), when the markup doesn't ask for one
 *     with `autofocus`:
 *       with a field     -> the first field (the native one already does it)
 *       no field         -> the main action (the last one in the footer)
 *       Danger main      -> the SECONDARY action: Enter can't be one press
 *                           away from deleting (rules 23 and 29)
 *
 * Usage:
 *   load this file with a script src    -> binds by itself when the page loads
 *   alModals.init(container)            -> binds content inserted later
 * Binding the same dialog twice duplicates nothing.
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
    if (dialog.querySelector('[autofocus]')) return;   // the markup decided
    if (hasFields(dialog)) return;                      // rule 26: the native one focuses the field
    var actions = dialog.querySelectorAll('.al-modal__actions button, .al-modal__actions a[href]');
    if (!actions.length) return;
    var primary = actions[actions.length - 1];
    var target = primary.matches(DANGER) ? actions[0] : primary;   // rule 29
    target.focus();
  }

  function bind(dialog) {
    if (dialog.hasAttribute('data-al-modal')) return;
    dialog.setAttribute('data-al-modal', '');

    // The click only counts if the press AND the release were on the scrim:
    // dragging to select text inside the Modal and releasing outside closes nothing.
    var pressedOnScrim = false;
    dialog.addEventListener('pointerdown', function (e) {
      pressedOnScrim = e.target === dialog && !inside(dialog, e.clientX, e.clientY);
    });
    dialog.addEventListener('click', function (e) {
      var onScrim = e.target === dialog && !inside(dialog, e.clientX, e.clientY);
      if (onScrim && pressedOnScrim && !hasFields(dialog)) dialog.close();   // rule 14
      pressedOnScrim = false;
    });

    // initial focus: watches `open`, because the opener may be the data
    // attribute or a showModal() from outside
    new MutationObserver(function () {
      if (dialog.open) initialFocus(dialog);
    }).observe(dialog, { attributes: true, attributeFilter: ['open'] });
  }

  function init(root) {
    [].slice.call((root || document).querySelectorAll('dialog.al-modal')).forEach(bind);
  }

  // Opening and closing by attribute: delegated on the document, only once, so
  // it also works for a button inserted later.
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
