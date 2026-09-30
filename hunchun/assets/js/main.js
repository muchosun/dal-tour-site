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
  // Превью — ссылка на Дзен. Обычный клик запускает плеер прямо на странице,
  // клик с Ctrl/Cmd/Shift или средней кнопкой — как у ссылки, новая вкладка.
  function initVideos() {
    Array.prototype.forEach.call(document.querySelectorAll('.video[data-embed]'), function (card) {
      var frame = card.querySelector('.video__frame');
      if (!frame) return;
      frame.addEventListener('click', function (e) {
        if (card.classList.contains('is-playing')) return;
        if (e.button !== 0 || e.ctrlKey || e.metaKey || e.shiftKey || e.altKey) return;
        e.preventDefault();

        var iframe = document.createElement('iframe');
        var src = card.getAttribute('data-embed');
        iframe.src = src + (src.indexOf('?') === -1 ? '?' : '&') + 'autoplay=1';
        var cap = card.querySelector('.video__cap');
        iframe.title = cap && cap.firstChild ? cap.firstChild.textContent.trim() : 'Видео';
        iframe.allow = 'autoplay; fullscreen; picture-in-picture; encrypted-media';
        iframe.setAttribute('allowfullscreen', '');
        iframe.setAttribute('frameborder', '0');

        frame.innerHTML = '';
        frame.appendChild(iframe);
        card.classList.add('is-playing');
        // после запуска превью больше не ссылка — клики по плееру не должны уводить на Дзен
        frame.removeAttribute('href');
        frame.removeAttribute('target');
      });
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    initDrawer();
    initYear();
    initVideos();
  });
})();
