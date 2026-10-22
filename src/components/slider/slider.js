/* AL Design System - Slider, fill and value
 *
 * What it does on every .al-slider__input inside `root`:
 *   - writes --al-slider-progress on the .al-slider (the WebKit/Blink fill;
 *     Firefox paints it natively);
 *   - writes the value into the <output for="id">, with data-unit appended;
 *   - with data-unit, writes aria-valuetext too ("60%" and not "60",
 *     rule 18).
 * The keyboard, the click on the track and the value itself stay native.
 *
 * Usage:
 *   <script src="slider.js"></script>   -> binds itself when the page loads
 *   alSlider.init(container)             -> binds content inserted later
 * Binding the same input twice duplicates nothing.
 */
(function () {
  'use strict';

  function sync(input) {
    var min = parseFloat(input.min) || 0;
    var max = input.max === '' ? 100 : parseFloat(input.max);
    var pct = max > min ? (parseFloat(input.value) - min) / (max - min) * 100 : 0;
    var box = input.closest('.al-slider');
    if (box) box.style.setProperty('--al-slider-progress', pct + '%');

    var unit = input.getAttribute('data-unit');
    var text = input.value + (unit || '');
    if (unit) input.setAttribute('aria-valuetext', text);
    if (input.id && box) {
      var out = box.querySelector('output[for~="' + input.id + '"]');
      if (out) out.textContent = text;
    }
  }

  function bind(input) {
    if (input.hasAttribute('data-al-slider')) return;
    input.setAttribute('data-al-slider', '');
    input.addEventListener('input', function () { sync(input); });
    sync(input);
  }

  function init(root) {
    [].forEach.call((root || document).querySelectorAll('.al-slider__input'), bind);
  }

  window.alSlider = { init: init };
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () { init(); });
  } else {
    init();
  }
})();
