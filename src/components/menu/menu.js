/* AL Design System - Menu
 *
 * W3C "menu button" pattern with an actions menu (role="menu"), unlike the
 * Breadcrumb `…`, which is a disclosure of links:
 *   - Enter, Space or Down on the trigger open on the first item; Up opens
 *     on the last (rule 22);
 *   - inside, Up/Down move with wrap, Home/End go to the ends; disabled
 *     items (aria-disabled) are stops too (rule A=a);
 *   - Esc closes and focus goes back to the trigger; Tab closes (rule 23);
 *   - choosing an enabled item closes and returns focus to the trigger,
 *     unless the action opened a dialog that took focus (rule 24);
 *   - closes on a click outside.
 * Choosing an item fires the button's normal click; the product listens to it.
 *
 * Usage:
 *   <script src="menu.js"></script>   -> binds by itself when the page loads
 *   alMenu.init(container)             -> binds content inserted later
 * Binding the same trigger twice duplicates nothing.
 */
(function () {
  'use strict';

  function bind(button) {
    if (button.hasAttribute('data-al-menu')) return;
    var list = document.getElementById(button.getAttribute('aria-controls'));
    if (!list) return;
    button.setAttribute('data-al-menu', '');
    var wrap = button.parentNode;

    function items() {
      return [].slice.call(list.querySelectorAll('[role="menuitem"]'));
    }

    function isOpen() { return button.getAttribute('aria-expanded') === 'true'; }

    function set(open) {
      button.setAttribute('aria-expanded', open ? 'true' : 'false');
      list.hidden = !open;
    }

    function open(at) {
      set(true);
      var all = items();
      if (all.length) all[at === 'last' ? all.length - 1 : 0].focus();
    }

    function close(refocus) {
      set(false);
      if (refocus) button.focus();
    }

    set(isOpen());   // markup and state always agree

    button.addEventListener('click', function () {
      if (isOpen()) close(false); else open('first');
    });

    button.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowDown') { e.preventDefault(); open('first'); }
      else if (e.key === 'ArrowUp') { e.preventDefault(); open('last'); }
    });

    list.addEventListener('keydown', function (e) {
      var all = items();
      var i = all.indexOf(document.activeElement);
      var next = null;
      if (e.key === 'ArrowDown') next = all[(i + 1) % all.length];
      else if (e.key === 'ArrowUp') next = all[(i - 1 + all.length) % all.length];
      else if (e.key === 'Home') next = all[0];
      else if (e.key === 'End') next = all[all.length - 1];
      else if (e.key === 'Escape') { e.preventDefault(); close(true); return; }
      else if (e.key === 'Tab') { close(false); return; }
      if (next) { e.preventDefault(); next.focus(); }
    });

    list.addEventListener('click', function (e) {
      var item = e.target.closest('[role="menuitem"]');
      if (!item) return;
      if (item.getAttribute('aria-disabled') === 'true') {
        e.preventDefault();
        e.stopImmediatePropagation();
        return;
      }
      // after the product's handlers: if one opened a dialog, focus stays there
      setTimeout(function () {
        var stay = document.activeElement && document.activeElement.closest('dialog[open]');
        close(!stay);
      }, 0);
    });

    document.addEventListener('pointerdown', function (e) {
      if (isOpen() && !wrap.contains(e.target)) close(false);
    });
  }

  function init(root) {
    [].forEach.call((root || document).querySelectorAll('[aria-haspopup="menu"][aria-controls]'), bind);
  }

  window.alMenu = { init: init };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () { init(); });
  } else {
    init();
  }
})();
