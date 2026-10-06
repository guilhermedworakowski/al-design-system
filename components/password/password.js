/* AL Design System - Password: o comportamento do olho
 *
 * O CSS ja sabe tudo o que e visual - qual icone mostrar le o `type` do
 * campo. Este arquivo so faz o que CSS nao alcanca:
 *
 *   1. tira o `hidden` do botao (sem JS o olho nao existe - GOV.UK);
 *   2. alterna `type` password <-> text e o `aria-label` do botao
 *      ("Mostrar senha" / "Ocultar senha", regra 28). O foco fica no botao
 *      e o valor nao e tocado (regra 15);
 *   3. esconde de novo quando o formulario e enviado (regra 16).
 *
 * Varios campos na mesma tela: os nomes vem de `data-label-show` e
 * `data-label-hide` no botao ("Mostrar nova senha"), regra 17.
 *
 * Campo desabilitado nunca alterna - e o botao leva `disabled` na marcacao.
 *
 * Inicia sozinho no carregamento. Conteudo inserido depois:
 *   window.alPassword.init(elementoQueContemOsCampos)
 */
(function () {
  'use strict';

  function setup(root) {
    var field = root.querySelector('.al-password__field');
    var toggle = root.querySelector('.al-password__toggle');
    if (!field || !toggle || toggle.hasAttribute('data-al-ready')) return;
    toggle.setAttribute('data-al-ready', '');

    var labelShow = toggle.getAttribute('data-label-show') || 'Mostrar senha';
    var labelHide = toggle.getAttribute('data-label-hide') || 'Ocultar senha';

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

    setVisible(false);          // regra 13: nasce sempre escondida
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
