/* AL Design System - Toast (rules 15 to 24)
 *
 * The toast markup lives on the page, in a <template>; this file only takes
 * care of SHOWING, TIMING and REMOVING. See the contract in toast.css's header.
 *
 *   - one at a time: whoever arrives with another on screen waits in the
 *     queue (rule 15);
 *   - Success and Info leave after `toast-timeout` (6000ms); the clock pauses
 *     with the pointer over it or focus inside, and resumes where it stopped
 *     (rule 17);
 *   - Warning and Error only leave through the X or Esc - and they hold the
 *     queue (rule 18);
 *   - the X always closes; Esc closes with focus inside the toast, and Esc
 *     stops there: over a Modal, the first Esc closes only the toast (rule 19);
 *   - never moves focus to the toast (rule 21). If the person tabbed to the X
 *     and the toast left, focus goes back to where they were before entering;
 *   - Error goes into the role="alert" region, the others into role="status"
 *     (rule 22). Both regions already exist on the page (rule 23).
 * The time on screen and the exit duration are read from the tokens in the
 * CSS, never written here.
 *
 * Usage:
 *   <script src="toast.js"></script>
 *   alToast.show('toast-saved')                        -> clones the <template id>
 *   alToast.show(tpl, { title: '…', description: '…' }) -> swaps the texts
 *   alToast.dismiss()                                  -> removes the one on screen
 *   alToast.clear()                                    -> empties the queue and removes the one on screen
 * A browser without popover: the region stays in the flow, at the end of the
 * page, and the announcement still reaches the screen reader.
 */
(function () {
  'use strict';

  var queue = [];
  var current = null;   // { el, timer, remaining, started, hover, focus, returnTo }

  function token(el, name) {
    return parseFloat(getComputedStyle(el).getPropertyValue('--al-toast-' + name)) || 0;
  }

  function region() {
    return document.querySelector('.al-toast-region');
  }

  // The region stays open forever. An open Modal or Drawer (dialog:modal) makes
  // everything outside it INERT - including the region, even drawn on top: the
  // X gets no click or focus and the screen reader stops seeing the toast. So,
  // while one is open, the region lives INSIDE it, and goes back to <body>
  // when it closes. Moving takes the popover out of the top layer; opening it
  // again puts it on top, above the dialog itself.
  function host() {
    var open = document.querySelectorAll('dialog:modal');
    return open.length ? open[open.length - 1] : document.body;
  }

  function home(r) {
    document.body.appendChild(r);
    if (!r.matches(':popover-open')) r.showPopover();
  }

  function raise(r) {
    if (typeof r.showPopover !== 'function') return;
    var h = host();
    if (r.parentNode !== h) {
      h.appendChild(r);
      // Watches the `open` attribute instead of the `close` event: the observer
      // runs right after close(), the event waits for a queued task.
      if (h !== document.body) {
        var watch = new MutationObserver(function () {
          if (h.open) return;
          watch.disconnect();
          home(r);
        });
        watch.observe(h, { attributes: true, attributeFilter: ['open'] });
      }
    }
    if (!r.matches(':popover-open')) r.showPopover();
  }

  function persistent(el) {
    return el.classList.contains('al-toast--warning') || el.classList.contains('al-toast--error');
  }

  // ------------------------------------------------------------------ clock
  function stopClock() {
    if (!current || !current.timer) return;
    clearTimeout(current.timer);
    current.timer = 0;
    current.remaining -= Date.now() - current.started;
  }

  function startClock() {
    if (!current || current.timer || persistent(current.el)) return;
    if (current.hover || current.focus) return;
    var el = current.el;
    current.started = Date.now();
    current.timer = setTimeout(function () { dismiss(el); }, Math.max(current.remaining, 0));
  }

  // ------------------------------------------------------------ enter/exit
  function build(source, text) {
    var tpl = typeof source === 'string' ? document.getElementById(source) : source;
    if (!tpl) return null;
    var root = tpl.content ? tpl.content.firstElementChild : tpl;
    if (!root || !root.classList.contains('al-toast')) return null;
    var el = root.cloneNode(true);
    if (text && text.title != null) el.querySelector('.al-toast__title').textContent = text.title;
    if (text && text.description != null) {
      var d = el.querySelector('.al-toast__description');
      if (text.description === '') { if (d) d.remove(); }
      else if (d) d.textContent = text.description;
    }
    return el;
  }

  function bind(el) {
    el.addEventListener('pointerenter', function () {
      if (!current || current.el !== el) return;
      current.hover = true; stopClock();
    });
    el.addEventListener('pointerleave', function () {
      if (!current || current.el !== el) return;
      current.hover = false; startClock();
    });
    el.addEventListener('focusin', function (e) {
      if (!current || current.el !== el) return;
      if (e.relatedTarget && !el.contains(e.relatedTarget)) current.returnTo = e.relatedTarget;
      current.focus = true; stopClock();
    });
    el.addEventListener('focusout', function (e) {
      if (!current || current.el !== el || el.contains(e.relatedTarget)) return;
      current.focus = false; startClock();
    });
    el.addEventListener('click', function (e) {
      if (e.target.closest('.al-toast__close')) dismiss(el);
    });
    el.addEventListener('keydown', function (e) {
      if (e.key !== 'Escape') return;
      e.preventDefault();
      e.stopPropagation();
      dismiss(el);
    });
  }

  function next() {
    if (current || !queue.length) return;
    var r = region();
    if (!r) return;
    var el = queue.shift();
    raise(r);
    var live = r.querySelector(el.classList.contains('al-toast--error') ? '[role="alert"]' : '[role="status"]');
    if (!live) return;
    bind(el);
    live.appendChild(el);
    current = { el: el, timer: 0, remaining: token(el, 'timeout'), started: 0,
                hover: false, focus: false, returnTo: null };
    startClock();
  }

  function show(source, text) {
    var el = build(source, text);
    if (!el) return null;
    queue.push(el);
    next();
    return el;
  }

  function dismiss(el) {
    if (!current || (el && current.el !== el) || current.el.hasAttribute('data-leaving')) return;
    var gone = current;
    clearTimeout(gone.timer);
    if (gone.el.contains(document.activeElement)) {
      if (gone.returnTo && gone.returnTo.isConnected) gone.returnTo.focus();
      else document.activeElement.blur();
    }
    var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var wait = reduce ? 0 : token(gone.el, 'duration');
    gone.el.setAttribute('data-leaving', '');
    setTimeout(function () {
      gone.el.remove();
      if (current === gone) current = null;
      next();
    }, wait);
  }

  function clear() {
    queue.length = 0;
    dismiss();
  }

  function init() {
    var r = region();
    if (r && typeof r.showPopover === 'function' && !r.matches(':popover-open')) r.showPopover();
  }

  window.alToast = { show: show, dismiss: dismiss, clear: clear };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
