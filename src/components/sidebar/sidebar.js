/* AL Design System - Sidebar, narrow screen behavior
 *
 * Above 1024px the Sidebar is only markup and CSS: there is nothing to bind.
 * Below that it becomes a modal panel from the left (rules 24 and 25), and
 * this file covers what the CSS doesn't:
 *   - opening from the product's Menu button: data-al-sidebar-open="<aside id>".
 *     The SAME <aside> is moved into a <dialog class="al-sidebar-modal"> and
 *     goes back to its place on closing - there are never two copies of the
 *     navigation;
 *   - the native <dialog> traps focus, makes the page inert, closes with Esc
 *     and returns focus to the Menu button;
 *   - initial focus on the current item (aria-current), otherwise on the
 *     first item;
 *   - closes on choosing a destination (a click on a <nav> link);
 *   - ALWAYS closes on a scrim click: the Sidebar has no fields;
 *   - no X: Menu, Esc and the scrim are enough;
 *   - if the screen widens with the panel open, it closes and the Sidebar
 *     goes back to the page;
 *   - keeps the Menu button's aria-expanded up to date.
 *
 * Usage:
 *   load this file with a script src  -> binds by itself
 * The breakpoint repeats sidebar.css's (exception `breakpoint`).
 */
(function () {
  'use strict';

  var NARROW = window.matchMedia('(width < 1024px)');
  var open = null;   // { aside, dialog, marker, opener }

  function initialFocus(aside) {
    var target = aside.querySelector('.al-sidebar__nav [aria-current]:not([aria-current="false"])') ||
                 aside.querySelector('.al-sidebar__nav a[href]');
    if (target) target.focus();
  }

  function inside(el, x, y) {
    var r = el.getBoundingClientRect();
    return x >= r.left && x <= r.right && y >= r.top && y <= r.bottom;
  }

  function restore() {
    if (!open) return;
    var s = open;
    open = null;
    s.marker.parentNode.insertBefore(s.aside, s.marker);
    s.marker.remove();
    s.dialog.remove();
    if (s.opener) s.opener.setAttribute('aria-expanded', 'false');
  }

  function show(aside, opener) {
    if (open || typeof HTMLDialogElement === 'undefined') return;
    var dialog = document.createElement('dialog');
    dialog.className = 'al-sidebar-modal';
    dialog.setAttribute('aria-label', aside.getAttribute('aria-label') || 'Menu');
    var marker = document.createComment('al-sidebar');
    aside.parentNode.insertBefore(marker, aside);
    document.body.appendChild(dialog);
    dialog.appendChild(aside);
    open = { aside: aside, dialog: dialog, marker: marker, opener: opener };

    // Only gives the <aside> back after the exit animation: the `close` event
    // comes right away, but the panel is still sliding.
    dialog.addEventListener('close', function () {
      if (opener) opener.setAttribute('aria-expanded', 'false');
      var done = false;
      function finish() { if (!done) { done = true; restore(); } }
      dialog.addEventListener('transitionend', function (e) {
        if (e.target === dialog && e.propertyName === 'translate') finish();
      });
      var ms = parseFloat(getComputedStyle(dialog).transitionDuration) * 1000 || 0;
      setTimeout(finish, ms + 50);
    });

    var pressedOnScrim = false;
    dialog.addEventListener('pointerdown', function (e) {
      pressedOnScrim = e.target === dialog && !inside(dialog, e.clientX, e.clientY);
    });
    dialog.addEventListener('click', function (e) {
      var onScrim = e.target === dialog && !inside(dialog, e.clientX, e.clientY);
      if (onScrim && pressedOnScrim) { dialog.close(); return; }
      pressedOnScrim = false;
      var link = e.target.closest && e.target.closest('.al-sidebar__nav a[href], .al-sidebar__profile a[href]');
      if (link) dialog.close();                    // rule 25: chose, closes
    });

    dialog.showModal();
    if (opener) opener.setAttribute('aria-expanded', 'true');
    initialFocus(aside);
  }

  document.addEventListener('click', function (e) {
    var opener = e.target.closest && e.target.closest('[data-al-sidebar-open]');
    if (!opener || !NARROW.matches) return;
    var aside = document.getElementById(opener.getAttribute('data-al-sidebar-open'));
    if (aside) show(aside, opener);
  });

  // The screen widened with the panel open: close and give back at once, no animation.
  NARROW.addEventListener('change', function (e) {
    if (!e.matches && open) {
      var d = open.dialog;
      restore();
      if (d.open) d.close();
    }
  });
})();
