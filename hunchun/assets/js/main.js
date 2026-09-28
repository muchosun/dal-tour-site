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

  /* Видео: плеер Дзена по клику. До нажатия — только превью. */
  function initVideos() {
    Array.prototype.forEach.call(document.querySelectorAll('a.video[data-embed]'), function (card) {
      card.addEventListener('click', function (e) {
        var frame = card.querySelector('.video__frame');
        if (!frame || card.classList.contains('is-playing')) return;
        e.preventDefault();

        var iframe = document.createElement('iframe');
        var src = card.getAttribute('data-embed');
        iframe.src = src + (src.indexOf('?') === -1 ? '?' : '&') + 'autoplay=1';
        iframe.title = (card.querySelector('.video__cap') || {}).firstChild
          ? card.querySelector('.video__cap').firstChild.textContent.trim()
          : 'Видео';
        iframe.allow = 'autoplay; fullscreen; picture-in-picture; encrypted-media';
        iframe.setAttribute('allowfullscreen', '');
        iframe.setAttribute('frameborder', '0');

        frame.innerHTML = '';
        frame.appendChild(iframe);
        card.classList.add('is-playing');
        // после запуска карточка больше не ссылка — иначе клики по плееру уводили бы на Дзен
        card.removeAttribute('href');
        card.setAttribute('role', 'group');
      });
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    initDrawer();
    initYear();
    initVideos();
  });
})();
