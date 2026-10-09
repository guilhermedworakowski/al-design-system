/* AL Design System - Breadcrumb, the `…` menu
 *
 * Only the Large needs this file. Short and Medium are links and text:
 * nothing to bind.
 *
 * W3C "disclosure navigation" pattern (rule 17), not an actions menu:
 *   - the `…` opens and closes the list (hidden) and keeps aria-expanded up
 *     to date;
 *   - on opening, focus STAYS on the `…`; the keyboard Tab enters the links,
 *     in order. No arrows, no role="menu";
 *   - closes with Esc - and focus goes back to the `…` (rule 16);
 *   - closes on a click outside, and when focus leaves the `…` and the menu;
 *   - closes on choosing a link (navigation proceeds normally).
 *
 * Usage:
 *   <script src="breadcrumb.js"></script>   -> binds by itself when the page loads
 *   alBreadcrumb.init(container)             -> binds content inserted later
 * Binding the same `…` twice duplicates nothing.
 */
(function () {
  'use strict';

  function bind(button) {
    if (button.hasAttribute('data-al-breadcrumb')) return;
    var menu = document.getElementById(button.getAttribute('aria-controls'));
    if (!menu) return;
    button.setAttribute('data-al-breadcrumb', '');
    var wrap = button.parentNode;

    function isOpen() { return button.getAttribute('aria-expanded') === 'true'; }

    function set(open) {
      button.setAttribute('aria-expanded', open ? 'true' : 'false');
      menu.hidden = !open;
    }

    set(isOpen());   // markup and state always agree

    button.addEventListener('click', function () { set(!isOpen()); });

    wrap.addEventListener('keydown', function (e) {
      if (e.key !== 'Escape' || !isOpen()) return;
      e.preventDefault();
      set(false);
      button.focus();
    });

    // focus left the `…` and the menu (Tab after the last link, Shift+Tab before the `…`)
    wrap.addEventListener('focusout', function (e) {
      if (isOpen() && e.relatedTarget && !wrap.contains(e.relatedTarget)) set(false);
    });

    menu.addEventListener('click', function (e) {
      if (e.target.closest('a[href]')) set(false);
    });

    document.addEventListener('pointerdown', function (e) {
      if (isOpen() && !wrap.contains(e.target)) set(false);
    });
  }

  function init(root) {
    [].forEach.call((root || document).querySelectorAll('.al-breadcrumb__more-button[aria-controls]'), bind);
  }

  window.alBreadcrumb = { init: init };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () { init(); });
  } else {
    init();
  }
})();
