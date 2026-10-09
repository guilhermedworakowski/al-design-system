/* AL Design System - Tab, keyboard behavior
 *
 * Only the PANEL use needs this file. Navigation with links (rule 22) is a
 * plain <a>: the keyboard Tab goes through all of them and nothing here
 * applies.
 *
 * What it does on every .al-tabs[role="tablist"] group inside `root`
 * (APG tabs pattern, rule 21):
 *   - only the selected tab sits at tabindex 0 (roving tabindex);
 *   - right/left arrow goes to the next/previous one, wrapping around;
 *     Home and End go to the first and the last;
 *   - AUTOMATIC activation: the tab that receives focus opens its panel. A
 *     group with data-activation="manual" only moves focus - Enter/Space (the
 *     native <button> click) opens it. Use manual when the panel loads from
 *     the network;
 *   - a panel is hidden with `hidden`, never removed: whatever was typed in
 *     it stays there (rule 20);
 *   - clicking the tab that is already open does nothing (rule 19);
 *   - the tab opened by a click gets `data-al-just-selected` until the next
 *     press, so it doesn't paint the selected pressed state (see the click
 *     below).
 *
 * Usage:
 *   <script src="tab.js"></script>   -> binds itself when the page loads
 *   alTabs.init(container)            -> binds content inserted later
 * Binding the same group twice duplicates nothing.
 */
(function () {
  'use strict';

  var KEYS = { ArrowRight: 1, ArrowLeft: -1, Home: 'first', End: 'last' };

  function bind(list) {
    if (list.hasAttribute('data-al-tabs')) return;
    list.setAttribute('data-al-tabs', '');

    var tabs = [].slice.call(list.querySelectorAll('[role="tab"]'));
    if (!tabs.length) return;
    var manual = list.getAttribute('data-activation') === 'manual';

    function panel(tab) {
      var id = tab.getAttribute('aria-controls');
      return id ? document.getElementById(id) : null;
    }

    function select(tab) {
      if (tab.getAttribute('aria-selected') === 'true') return;  // rule 19
      tabs.forEach(function (t) {
        var on = t === tab;
        t.setAttribute('aria-selected', on ? 'true' : 'false');
        t.tabIndex = on ? 0 : -1;
        var p = panel(t);
        if (p) p.hidden = !on;
      });
    }

    // consistent initial state: exactly one selected (rule 7)
    var start = tabs.filter(function (t) {
      return t.getAttribute('aria-selected') === 'true';
    })[0] || tabs[0];
    tabs.forEach(function (t) { t.setAttribute('aria-selected', 'false'); });
    select(start);

    tabs.forEach(function (tab, i) {
      // A tab selected BY ITS OWN click doesn't paint the selected pressed
      // state: some browsers (Safari) still consider it :active when the
      // click fires, and it would go from bg-active to brand-active in the
      // middle of the press. The mark goes away on the next press - then it
      // really is the pressed state of a tab that was already open.
      tab.addEventListener('pointerdown', function () {
        tab.removeAttribute('data-al-just-selected');
      });
      tab.addEventListener('click', function () {
        if (tab.getAttribute('aria-selected') === 'true') return;  // rule 19
        select(tab);
        tab.setAttribute('data-al-just-selected', '');
      });
      tab.addEventListener('keydown', function (e) {
        var k = KEYS[e.key];
        if (!k) return;
        var next = k === 'first' ? tabs[0]
          : k === 'last' ? tabs[tabs.length - 1]
          : tabs[(i + k + tabs.length) % tabs.length];
        e.preventDefault();
        if (manual) {
          tabs.forEach(function (t) { t.tabIndex = t === next ? 0 : -1; });
        } else {
          select(next);
        }
        next.focus();
      });
    });

    // in manual mode focus can leave from a tab that isn't open; when it
    // leaves the group, the Tab key entry point goes back to the selected tab
    list.addEventListener('focusout', function (e) {
      if (list.contains(e.relatedTarget)) return;
      tabs.forEach(function (t) {
        t.tabIndex = t.getAttribute('aria-selected') === 'true' ? 0 : -1;
      });
    });
  }

  function init(root) {
    [].slice.call((root || document).querySelectorAll('.al-tabs[role="tablist"]')).forEach(bind);
  }

  window.alTabs = { init: init };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () { init(); });
  } else {
    init();
  }
})();
