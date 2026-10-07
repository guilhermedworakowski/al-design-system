/* AL Design System - Tab, comportamento de teclado (decisao de Gui na etapa 5)
 *
 * So o uso de PAINEL precisa deste arquivo. Navegacao por links (regra 22) e
 * <a> comum: o Tab do teclado passa por todos e nada aqui se aplica.
 *
 * O que ele faz em todo grupo [role="tablist"] dentro de `root`
 * (padrao de abas da APG, regra 21):
 *   - so a aba selecionada fica em tabindex 0 (roving tabindex);
 *   - seta direita/esquerda vai para a proxima/anterior, dando a volta;
 *     Home e End vao para a primeira e a ultima;
 *   - ativacao AUTOMATICA: a aba que recebe o foco abre o painel. Grupo com
 *     data-activation="manual" so move o foco - Enter/Espaco (o clique nativo
 *     do <button>) abre. Use manual quando o painel carrega da rede;
 *   - painel e escondido com `hidden`, nunca removido: o que foi digitado
 *     nele continua la (regra 20);
 *   - clicar na aba ja aberta nao faz nada (regra 19).
 *
 * Uso:
 *   <script src="tab.js"></script>   -> liga sozinho quando a pagina carrega
 *   alTabs.init(container)            -> liga em conteudo inserido depois
 * Ligar duas vezes o mesmo grupo nao duplica nada.
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
      if (tab.getAttribute('aria-selected') === 'true') return;  // regra 19
      tabs.forEach(function (t) {
        var on = t === tab;
        t.setAttribute('aria-selected', on ? 'true' : 'false');
        t.tabIndex = on ? 0 : -1;
        var p = panel(t);
        if (p) p.hidden = !on;
      });
    }

    // estado inicial coerente: exatamente uma selecionada (regra 7)
    var start = tabs.filter(function (t) {
      return t.getAttribute('aria-selected') === 'true';
    })[0] || tabs[0];
    tabs.forEach(function (t) { t.setAttribute('aria-selected', 'false'); });
    select(start);

    tabs.forEach(function (tab, i) {
      tab.addEventListener('click', function () { select(tab); });
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

    // no manual o foco pode sair de uma aba nao aberta; ao sair do grupo, a
    // entrada pelo Tab volta a ser a aba selecionada
    list.addEventListener('focusout', function (e) {
      if (list.contains(e.relatedTarget)) return;
      tabs.forEach(function (t) {
        t.tabIndex = t.getAttribute('aria-selected') === 'true' ? 0 : -1;
      });
    });
  }

  function init(root) {
    [].slice.call((root || document).querySelectorAll('[role="tablist"]')).forEach(bind);
  }

  window.alTabs = { init: init };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () { init(); });
  } else {
    init();
  }
})();
