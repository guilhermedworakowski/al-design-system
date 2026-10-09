/* AL Design System - Tooltip (rules 13 to 20)
 *
 * What links trigger and tooltip is the trigger's ARIA, not a class:
 *   aria-labelledby="<id>"   the tooltip is the trigger's name
 *   aria-describedby="<id>"  the tooltip complements a trigger that already has a name
 * This file only takes care of SHOWING and HIDING. Name and description work
 * without it: the screen reader reads the hidden tooltip through the attribute.
 *
 *   - hover: opens after `tooltip-delay-show` (500ms). If another tooltip is
 *     already open, it switches at once - whoever is reading a row of buttons
 *     doesn't wait again on each one (rule 16);
 *   - keyboard focus (:focus-visible): opens at once. Click focus doesn't
 *     open (rules 16 and 20);
 *   - touch doesn't open, click closes (rule 20);
 *   - stays open while the pointer is on the trigger OR on the tooltip, or
 *     keyboard focus is on the trigger; `tooltip-delay-hide` (100ms) of slack
 *     for the pointer to cross the 4 gap (rule 17, WCAG 1.4.13);
 *   - Esc closes without moving focus, and Esc stops there: with a tooltip
 *     open inside a Modal, the first Esc closes only the tooltip (rule 18);
 *   - one open at a time (rule 19);
 *   - side: the .al-tooltip's data-placement, top by default; flips to the
 *     opposite if it doesn't fit, and follows scrolling and resizing (rules
 *     13 and 15).
 * Times and distance are read from the tokens in the CSS, never written here.
 *
 * Usage:
 *   <script src="tooltip.js"></script>   -> binds by itself when the page loads
 *   alTooltip.init(container)             -> binds content inserted later
 * Binding the same trigger twice duplicates nothing. A browser without
 * popover: the tooltip never appears, and the name still reaches the screen
 * reader.
 */
(function () {
  'use strict';

  var OPPOSITE = { top: 'bottom', bottom: 'top', left: 'right', right: 'left' };
  var current = null;          // { trigger, tip }
  var showTimer = 0;
  var hideTimer = 0;

  function token(tip, name) {
    return parseFloat(getComputedStyle(tip).getPropertyValue('--al-tooltip-' + name)) || 0;
  }

  function clamp(v, lo, hi) { return hi < lo ? lo : Math.max(lo, Math.min(v, hi)); }

  function place(trigger, tip) {
    var r = trigger.getBoundingClientRect();
    var w = tip.offsetWidth;
    var h = tip.offsetHeight;
    var gap = token(tip, 'offset');
    var vw = document.documentElement.clientWidth;
    var vh = document.documentElement.clientHeight;
    var room = { top: r.top - gap, bottom: vh - r.bottom - gap, left: r.left - gap, right: vw - r.right - gap };
    var need = { top: h, bottom: h, left: w, right: w };
    var pref = OPPOSITE[tip.getAttribute('data-placement')] ? tip.getAttribute('data-placement') : 'top';
    var opp = OPPOSITE[pref];
    var side = room[pref] >= need[pref] ? pref
      : room[opp] >= need[opp] ? opp
      : room[pref] >= room[opp] ? pref : opp;
    var x, y;
    if (side === 'top' || side === 'bottom') {
      x = clamp(r.left + r.width / 2 - w / 2, gap, vw - w - gap);
      y = side === 'top' ? r.top - gap - h : r.bottom + gap;
    } else {
      x = side === 'left' ? r.left - gap - w : r.right + gap;
      y = clamp(r.top + r.height / 2 - h / 2, gap, vh - h - gap);
    }
    tip.style.left = Math.round(x) + 'px';
    tip.style.top = Math.round(y) + 'px';
    tip.setAttribute('data-side', side);
  }

  function hide() {
    clearTimeout(showTimer);
    clearTimeout(hideTimer);
    if (!current) return;
    if (current.tip.matches(':popover-open')) current.tip.hidePopover();
    current = null;
  }

  function show(trigger, tip) {
    clearTimeout(showTimer);
    clearTimeout(hideTimer);
    if (current && current.tip === tip) return;
    hide();                                         // one at a time
    if (trigger.disabled || !trigger.isConnected) return;
    tip.showPopover();
    place(trigger, tip);
    current = { trigger: trigger, tip: tip };
  }

  function keyboardFocused(el) {
    return el === document.activeElement && el.matches(':focus-visible');
  }

  function scheduleHide(trigger, tip) {
    clearTimeout(hideTimer);
    hideTimer = setTimeout(function () {
      if (!current || current.tip !== tip) return;
      if (trigger.matches(':hover') || tip.matches(':hover') || keyboardFocused(trigger)) return;
      hide();
    }, token(tip, 'delay-hide'));
  }

  function bind(trigger, tip) {
    if (trigger.hasAttribute('data-al-tooltip')) return;
    trigger.setAttribute('data-al-tooltip', '');

    trigger.addEventListener('pointerenter', function (e) {
      if (e.pointerType === 'touch') return;
      clearTimeout(hideTimer);
      if (current) { show(trigger, tip); return; }   // one is already open: switch at once
      clearTimeout(showTimer);
      showTimer = setTimeout(function () { show(trigger, tip); }, token(tip, 'delay-show'));
    });
    trigger.addEventListener('pointerleave', function () {
      clearTimeout(showTimer);
      scheduleHide(trigger, tip);
    });
    trigger.addEventListener('pointerdown', hide);
    trigger.addEventListener('focus', function () {
      if (trigger.matches(':focus-visible')) show(trigger, tip);
    });
    trigger.addEventListener('blur', function () {
      if (current && current.tip === tip) scheduleHide(trigger, tip);
    });

    if (tip.hasAttribute('data-al-tooltip')) return;
    tip.setAttribute('data-al-tooltip', '');
    tip.addEventListener('pointerenter', function () { clearTimeout(hideTimer); });
    tip.addEventListener('pointerleave', function () {
      if (current && current.tip === tip) scheduleHide(current.trigger, tip);
    });
  }

  function init(root) {
    var scope = root || document;
    [].forEach.call(scope.querySelectorAll('.al-tooltip[id][popover]'), function (tip) {
      if (typeof tip.showPopover !== 'function') return;
      var id = CSS.escape(tip.id);
      [].forEach.call(document.querySelectorAll(
        '[aria-labelledby~="' + id + '"], [aria-describedby~="' + id + '"]'), function (trigger) {
        bind(trigger, tip);
      });
    });
  }

  // Esc in the capture phase: closes the tooltip before the Modal or the Drawer hear it.
  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape' || !current) return;
    e.preventDefault();
    e.stopPropagation();
    hide();
  }, true);

  function follow() { if (current) place(current.trigger, current.tip); }
  window.addEventListener('scroll', follow, { capture: true, passive: true });
  window.addEventListener('resize', follow, { passive: true });

  window.alTooltip = { init: init, hide: hide };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () { init(); });
  } else {
    init();
  }
})();
