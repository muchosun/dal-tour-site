/* Лендинг «Туры в Хуньчунь». Форм на сайте нет — только меню и год в подвале. */
(function () {
  'use strict';

  function initDrawer() {
    var drawer = document.querySelector('[data-drawer]');
    var openBtn = document.querySelector('[data-drawer-open]');
    if (!drawer || !openBtn) return;

    var lastFocused = null;

    function open() {
      lastFocused = document.activeElement;
      drawer.setAttribute('data-open', 'true');
      document.body.classList.add('is-locked');
      openBtn.setAttribute('aria-expanded', 'true');
      var first = drawer.querySelector('a, button');
      if (first) first.focus();
    }

    function close() {
      drawer.setAttribute('data-open', 'false');
      document.body.classList.remove('is-locked');
      openBtn.setAttribute('aria-expanded', 'false');
      if (lastFocused instanceof HTMLElement) lastFocused.focus();
    }

    openBtn.addEventListener('click', open);
    Array.prototype.forEach.call(drawer.querySelectorAll('[data-drawer-close]'), function (el) {
      el.addEventListener('click', close);
    });
    Array.prototype.forEach.call(drawer.querySelectorAll('a'), function (a) {
      a.addEventListener('click', close);
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && drawer.getAttribute('data-open') === 'true') close();
    });
  }

  function initYear() {
    Array.prototype.forEach.call(document.querySelectorAll('[data-year]'), function (el) {
      el.textContent = String(new Date().getFullYear());
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    initDrawer();
    initYear();
  });
})();
