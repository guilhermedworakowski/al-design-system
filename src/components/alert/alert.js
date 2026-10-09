/* AL Design System - Alert (rules 11, 20 to 25)
 *
 * The Alert is regular page markup (contract in alert.css's header). This
 * file only takes care of CLOSING and INSERTING AFTER page load:
 *
 *   - the X ([data-al-alert-close]) removes the Alert with an exit fade and
 *     fires the `al-alert-close` event on the slot, so the product stores the
 *     choice and the Alert doesn't come back on the next visit (rule 21);
 *   - if focus was inside, it goes to the next focusable element after the
 *     Alert; with none, to <main> (rule 22). It never gets lost on the body;
 *   - alAlert.show() puts an Alert coming from a <template> into the slot.
 *     One per page: the one that was there leaves (rule 11). It enters a
 *     live region that is born EMPTY and only then receives the Alert - a
 *     region born together with the message isn't announced. Danger goes in
 *     role="alert", the others in role="status" (rule 24). Focus doesn't
 *     move (rule 25).
 *   - an Alert present on page load gets no role at all (rule 23).
 * The exit duration is read from the token in the CSS, never written here.
 *
 * Usage:
 *   <script src="alert.js"></script>
 *   alAlert.show('alert-plan')                        -> clones the <template id> into the .al-alert-slot
 *   alAlert.show(tpl, { slot: el })                   -> into another slot
 *   alAlert.dismiss(el)                               -> removes the Alert (the same as the X)
 *   slot.addEventListener('al-alert-close', e => …)    -> e.detail.alert is the one that left
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

  // Rule 22: the next focusable AFTER the Alert in document order.
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

    // Rule 11: one per page. The previous one leaves at once, no fade - the new
    // one takes the same place.
    var old = slot.querySelectorAll('.al-alert-live, .al-alert');
    for (var i = 0; i < old.length; i++) {
      if (old[i].parentNode === slot) old[i].remove();
    }

    var live = document.createElement('div');
    live.className = 'al-alert-live';
    live.setAttribute('role', alert.classList.contains('al-alert--danger') ? 'alert' : 'status');
    slot.appendChild(live);
    // The region must exist empty before the message for the reader to announce it.
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
