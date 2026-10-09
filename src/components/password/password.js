/* AL Design System - Password: the eye's behavior
 *
 * The CSS already knows everything visual - which icon to show reads the
 * field's `type`. This file only does what CSS can't reach:
 *
 *   1. removes the button's `hidden` (without JS the eye doesn't exist - GOV.UK);
 *   2. toggles `type` password <-> text and the button's `aria-label`
 *      ("Show password" / "Hide password", rule 28). Focus stays on the button
 *      and the value is not touched (rule 15);
 *   3. hides it again when the form is submitted (rule 16).
 *
 * Several fields on the same screen: the names come from `data-label-show`
 * and `data-label-hide` on the button ("Show new password"), rule 17. They are
 * also how a page in another language sets its own names.
 *
 * A disabled field never toggles - and the button gets `disabled` in the markup.
 *
 * It starts by itself on load. Content inserted later:
 *   window.alPassword.init(elementContainingTheFields)
 */
(function () {
  'use strict';

  function setup(root) {
    var field = root.querySelector('.al-password__field');
    var toggle = root.querySelector('.al-password__toggle');
    if (!field || !toggle || toggle.hasAttribute('data-al-ready')) return;
    toggle.setAttribute('data-al-ready', '');

    var labelShow = toggle.getAttribute('data-label-show') || 'Show password';
    var labelHide = toggle.getAttribute('data-label-hide') || 'Hide password';

    function setVisible(visible) {
      field.type = visible ? 'text' : 'password';
      toggle.setAttribute('aria-label', visible ? labelHide : labelShow);
    }

    toggle.addEventListener('click', function () {
      if (field.disabled) return;
      setVisible(field.type === 'password');
    });

    if (field.form) {
      field.form.addEventListener('submit', function () {
        setVisible(false);
      });
    }

    setVisible(false);          // rule 13: it always starts hidden
    toggle.hidden = false;
  }

  function init(scope) {
    var roots = (scope || document).querySelectorAll('.al-password');
    for (var i = 0; i < roots.length; i++) setup(roots[i]);
  }

  window.alPassword = { init: init };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () { init(); });
  } else {
    init();
  }
})();
