/* AL Design System - Number field: the steppers' behavior
 *
 * The arrow keys and typing are native to <input type="number">. This file
 * only does what the browser doesn't:
 *
 *   1. removes the buttons' `hidden` (without JS they don't exist);
 *   2. - and + call stepDown()/stepUp() and fire `input` and `change`, so the
 *      form hears the change like it was typed. One click is one step:
 *      holding the button does NOT repeat (decision E=a);
 *   3. keeps focus where it was - clicking a stepper doesn't move focus to
 *      the field or to the button (rule 15);
 *   4. disables the stepper at the limit: - at the minimum, + at the maximum
 *      (rule 10). A disabled field disables both.
 *
 * It never clamps what was typed (decision F=a): a value out of range stays
 * as typed, and the form shows the error by reading `field.validity`
 * (rangeUnderflow / rangeOverflow) and setting aria-invalid + the message.
 *
 * It starts by itself on load. Content inserted later:
 *   window.alNumberField.init(elementContainingTheFields)
 */
(function () {
  'use strict';

  function setup(root) {
    var field = root.querySelector('.al-number-field__field');
    var down = root.querySelector('.al-number-field__step[data-step="down"]');
    var up = root.querySelector('.al-number-field__step[data-step="up"]');
    if (!field || !down || !up || root.hasAttribute('data-al-ready')) return;
    root.setAttribute('data-al-ready', '');

    function bound(attr) {
      var v = field.getAttribute(attr);
      return v === null || v === '' ? null : Number(v);
    }

    function sync() {
      var value = field.valueAsNumber;
      var min = bound('min');
      var max = bound('max');
      var off = field.disabled || field.readOnly;
      down.disabled = off || (min !== null && !isNaN(value) && value <= min);
      up.disabled = off || (max !== null && !isNaN(value) && value >= max);
    }

    function step(dir) {
      if (field.disabled || field.readOnly) return;
      try {
        if (dir === 'up') field.stepUp(); else field.stepDown();
      } catch (e) {
        return;   // an empty or invalid value - stepping has nothing to start from
      }
      field.dispatchEvent(new Event('input', { bubbles: true }));
      field.dispatchEvent(new Event('change', { bubbles: true }));
      sync();
    }

    [down, up].forEach(function (button) {
      // rule 15: the click must not take focus from where it was
      button.addEventListener('mousedown', function (e) { e.preventDefault(); });
      button.addEventListener('click', function () {
        step(button.getAttribute('data-step'));
      });
      button.hidden = false;
    });

    field.addEventListener('input', sync);
    sync();
  }

  function init(scope) {
    var roots = (scope || document).querySelectorAll('.al-number-field');
    for (var i = 0; i < roots.length; i++) setup(roots[i]);
  }

  window.alNumberField = { init: init };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () { init(); });
  } else {
    init();
  }
})();
