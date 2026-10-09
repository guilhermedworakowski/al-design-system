/* AL Design System - Breadcrumb, menu do `…` (decisoes 5a e B)
 *
 * So a Large precisa deste arquivo. Short e Medium sao links e texto: nada
 * para ligar.
 *
 * Padrao "disclosure navigation" do W3C (regra 17), nao menu de acoes:
 *   - o `…` abre e fecha a lista (hidden) e mantem aria-expanded em dia;
 *   - ao abrir, o foco FICA no `…` (decisao B = a); o Tab do teclado entra nos
 *     links, na ordem. Sem setas, sem role="menu";
 *   - fecha com Esc - e o foco volta ao `…` (regra 16);
 *   - fecha no clique fora, e quando o foco sai do `…` e do menu;
 *   - fecha ao escolher um link (a navegacao segue normalmente).
 *
 * Uso:
 *   <script src="breadcrumb.js"></script>   -> liga sozinho quando a pagina carrega
 *   alBreadcrumb.init(container)             -> liga em conteudo inserido depois
 * Ligar duas vezes o mesmo `…` nao duplica nada.
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

    set(isOpen());   // marcacao e estado sempre concordam

    button.addEventListener('click', function () { set(!isOpen()); });

    wrap.addEventListener('keydown', function (e) {
      if (e.key !== 'Escape' || !isOpen()) return;
      e.preventDefault();
      set(false);
      button.focus();
    });

    // foco saiu do `…` e do menu (Tab depois do ultimo link, Shift+Tab antes do `…`)
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
