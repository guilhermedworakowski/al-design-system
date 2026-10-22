/* AL Design System - Carousel, arrows, dots and announcement
 *
 * What it does on every .al-carousel inside `root` (usage rules 13-22):
 *   - previous / next scroll by one page (rule 14, A=a): next starts at the
 *     first slide not fully in view, so the one cut at the edge is never
 *     skipped; previous goes back as far as one viewport allows;
 *   - the arrows get `disabled` at the ends - no loop (rule 13). When the
 *     arrow that has focus turns disabled, focus moves to the other one, so
 *     it never falls back to <body>;
 *   - the dot of the first visible slide gets data-current (rule 22);
 *   - only after an ARROW, the live region says which slides are in view
 *     (rule 21, B=a). Swipe and trackpad announce nothing. The sentence is
 *     data-al-live on the .al-carousel, with {first}, {last} and {total}
 *     (default "Slides {first} to {last} of {total}"; one slide in view
 *     uses data-al-live-one, default "Slide {first} of {total}").
 *
 * Usage:
 *   <script src="carousel.js"></script>   -> binds itself when the page loads
 *   alCarousel.init(container)            -> binds content inserted later
 * Binding the same carousel twice duplicates nothing.
 */
(function () {
  'use strict';

  function bind(root) {
    if (root.hasAttribute('data-al-carousel-bound')) return;
    var viewport = root.querySelector('.al-carousel__viewport');
    if (!viewport) return;
    root.setAttribute('data-al-carousel-bound', '');

    var slides = [].slice.call(viewport.querySelectorAll('.al-carousel__slide'));
    var dots = [].slice.call(root.querySelectorAll('.al-carousel__dot'));
    var prev = root.querySelector('[data-al-carousel="prev"]');
    var next = root.querySelector('[data-al-carousel="next"]');
    var live = root.querySelector('.al-carousel__live');
    var announce = false;

    // slides fully (or almost fully) inside the viewport, 1-based
    function inView() {
      var v = viewport.getBoundingClientRect();
      var first = 0, last = 0;
      slides.forEach(function (s, i) {
        var r = s.getBoundingClientRect();
        if (r.left >= v.left - 1 && r.right <= v.right + 1) {
          if (!first) first = i + 1;
          last = i + 1;
        }
      });
      return { first: first || 1, last: last || first || 1 };
    }

    function update() {
      var max = viewport.scrollWidth - viewport.clientWidth;
      var atStart = viewport.scrollLeft <= 1;
      var atEnd = viewport.scrollLeft >= max - 1;
      var lost = document.activeElement;

      if (prev) prev.disabled = atStart;
      if (next) next.disabled = atEnd;
      if (lost === prev && atStart && next && !atEnd) next.focus();
      if (lost === next && atEnd && prev && !atStart) prev.focus();

      var pos = inView();
      dots.forEach(function (d, i) {
        if (i === pos.first - 1) d.setAttribute('data-current', '');
        else d.removeAttribute('data-current');
      });

      if (announce && live) {
        var one = pos.first === pos.last;
        var text = one
          ? root.getAttribute('data-al-live-one') || 'Slide {first} of {total}'
          : root.getAttribute('data-al-live') || 'Slides {first} to {last} of {total}';
        live.textContent = text
          .replace('{first}', pos.first)
          .replace('{last}', pos.last)
          .replace('{total}', slides.length);
      }
      announce = false;
    }

    // a slide's start, in the viewport's scroll coordinates
    function start(s) { return s.offsetLeft - slides[0].offsetLeft; }

    // Next: the first slide not fully in view becomes the first one - a slide
    // cut at the edge is never skipped. Previous: the mirror, the earliest
    // slide that still fits one viewport back.
    function page(dir) {
      announce = true;
      var pos = inView();
      var left;
      if (dir > 0) {
        left = start(slides[Math.min(pos.last, slides.length - 1)]);
      } else {
        var floor = viewport.scrollLeft - viewport.clientWidth;
        var target = slides.filter(function (s) { return start(s) >= floor - 1; })[0];
        left = Math.min(start(target), start(slides[Math.max(pos.first - 2, 0)]));
      }
      viewport.scrollTo({ left: left });
    }

    if (prev) prev.addEventListener('click', function () { page(-1); });
    if (next) next.addEventListener('click', function () { page(1); });

    // scrollend where it exists; a short quiet period elsewhere (Safari)
    if ('onscrollend' in window) {
      viewport.addEventListener('scrollend', update);
    } else {
      var timer;
      viewport.addEventListener('scroll', function () {
        clearTimeout(timer);
        timer = setTimeout(update, 100);
      });
    }
    window.addEventListener('resize', update);
    update();
  }

  function init(root) {
    [].slice.call((root || document).querySelectorAll('.al-carousel')).forEach(bind);
  }

  window.alCarousel = { init: init };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () { init(); });
  } else {
    init();
  }
})();
