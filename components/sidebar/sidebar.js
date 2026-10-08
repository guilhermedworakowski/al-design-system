/* AL Design System - Sidebar, comportamento da tela estreita
 *
 * Acima de 1024px a Sidebar e so marcacao e CSS: nao ha nada para ligar.
 * Abaixo disso ela vira painel modal pela esquerda (regras 24 e 25), e este
 * arquivo cobre o que o CSS nao faz:
 *   - abrir pelo botao Menu do produto: data-al-sidebar-open="<id da aside>".
 *     A MESMA <aside> e movida para dentro de um <dialog class="al-sidebar-modal">
 *     e volta para o lugar dela ao fechar - nunca ha duas copias da navegacao;
 *   - o <dialog> nativo prende o foco, deixa a pagina inerte, fecha com Esc e
 *     devolve o foco ao botao Menu;
 *   - foco inicial no item atual (aria-current), senao no primeiro item;
 *   - fecha ao escolher um destino (clique num link do <nav>);
 *   - fecha SEMPRE no clique no scrim: a Sidebar nao tem campos;
 *   - sem X (decisao 3): Menu, Esc e scrim bastam;
 *   - se a tela alargar com o painel aberto, fecha e a Sidebar volta a pagina;
 *   - mantem aria-expanded do botao Menu em dia.
 *
 * Uso:
 *   carregar este arquivo com um script src  -> liga sozinho
 * O ponto de quebra repete o do sidebar.css (excecao `ponto-de-quebra`).
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

    // So devolve a <aside> depois da animacao de saida: o evento `close` vem
    // na hora, mas o painel ainda esta deslizando.
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
      if (link) dialog.close();                    // regra 25: escolheu, fecha
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

  // Tela alargou com o painel aberto: fecha e devolve na hora, sem animacao.
  NARROW.addEventListener('change', function (e) {
    if (!e.matches && open) {
      var d = open.dialog;
      restore();
      if (d.open) d.close();
    }
  });
})();
