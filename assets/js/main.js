/* ДАЛЬТУР — прототип. Бэкенда нет: формы уводят в WhatsApp. */
(function () {
  'use strict';

  var WHATSAPP = '79644444144';

  function waLink(text) {
    return 'https://wa.me/' + WHATSAPP + '?text=' + encodeURIComponent(text);
  }

  /* ---------- мобильное меню ---------- */

  function initDrawer() {
    var drawer = document.querySelector('[data-drawer]');
    var openBtn = document.querySelector('[data-drawer-open]');
    if (!drawer || !openBtn) return;

    var closers = drawer.querySelectorAll('[data-drawer-close]');
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
    Array.prototype.forEach.call(closers, function (el) {
      el.addEventListener('click', close);
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && drawer.getAttribute('data-open') === 'true') close();
    });
    Array.prototype.forEach.call(drawer.querySelectorAll('a[href^="#"]'), function (a) {
      a.addEventListener('click', close);
    });
  }

  /* ---------- подбор тура ---------- */

  function initPicker() {
    var form = document.querySelector('[data-picker]');
    if (!form) return;

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var data = new FormData(form);
      var parts = [];
      data.forEach(function (value, key) {
        if (typeof value === 'string' && value) parts.push(key + ': ' + value);
      });
      var text = 'Здравствуйте! Подберите, пожалуйста, тур.\n' + parts.join('\n');
      window.open(waLink(text), '_blank', 'noopener');
    });
  }

  /* ---------- заявка ---------- */

  function initLeadForm() {
    var form = document.querySelector('[data-lead-form]');
    if (!form) return;

    var status = form.querySelector('[data-lead-status]');

    form.addEventListener('submit', function (e) {
      e.preventDefault();

      var nameInput = form.querySelector('input[name="name"]');
      var telInput = form.querySelector('input[name="tel"]');
      var tel = telInput ? telInput.value.trim() : '';
      var digits = tel.replace(/\D/g, '');

      if (digits.length < 10) {
        if (telInput) {
          telInput.setAttribute('aria-invalid', 'true');
          telInput.focus();
        }
        if (status) status.textContent = 'Проверьте номер телефона — нужно не меньше 10 цифр.';
        return;
      }

      if (telInput) telInput.removeAttribute('aria-invalid');
      var name = nameInput ? nameInput.value.trim() : '';
      var text = 'Здравствуйте! Заявка с сайта.\n' +
        (name ? 'Имя: ' + name + '\n' : '') +
        'Телефон: ' + tel;

      if (status) status.textContent = 'Открываем WhatsApp — отправьте сообщение, менеджер ответит в рабочее время.';
      window.open(waLink(text), '_blank', 'noopener');
    });
  }

  /* ---------- фильтры списка туров ---------- */

  function initFilters() {
    var root = document.querySelector('[data-tour-filters]');
    var list = document.querySelector('[data-tour-list]');
    if (!root || !list) return;

    var chips = root.querySelectorAll('.chip');
    var sort = document.querySelector('[data-tour-sort]');
    var counter = document.querySelector('[data-tour-count]');
    var items = Array.prototype.slice.call(list.querySelectorAll('[data-tour]'));

    var state = { transport: 'all', length: 'all' };

    function matches(el) {
      if (state.transport !== 'all' && el.getAttribute('data-transport') !== state.transport) return false;
      if (state.length !== 'all') {
        var days = parseInt(el.getAttribute('data-days'), 10) || 0;
        if (state.length === 'short' && days > 6) return false;
        if (state.length === 'long' && days < 7) return false;
      }
      return true;
    }

    function apply() {
      var shown = 0;
      items.forEach(function (el) {
        var ok = matches(el);
        el.hidden = !ok;
        if (ok) shown++;
      });
      if (counter) {
        counter.textContent = shown + ' ' + plural(shown, ['тур', 'тура', 'туров']);
      }
    }

    function plural(n, forms) {
      var n10 = n % 10, n100 = n % 100;
      if (n10 === 1 && n100 !== 11) return forms[0];
      if (n10 >= 2 && n10 <= 4 && (n100 < 10 || n100 >= 20)) return forms[1];
      return forms[2];
    }

    Array.prototype.forEach.call(chips, function (chip) {
      chip.addEventListener('click', function () {
        var group = chip.getAttribute('data-group');
        var value = chip.getAttribute('data-value');
        if (!group || !value) return;

        state[group] = value;
        Array.prototype.forEach.call(chips, function (other) {
          if (other.getAttribute('data-group') === group) {
            other.setAttribute('aria-pressed', String(other === chip));
          }
        });
        apply();
      });
    });

    if (sort) {
      sort.addEventListener('change', function () {
        var dir = sort.value === 'desc' ? -1 : 1;
        items.slice()
          .sort(function (a, b) {
            var da = parseInt(a.getAttribute('data-days'), 10) || 0;
            var db = parseInt(b.getAttribute('data-days'), 10) || 0;
            return (da - db) * dir;
          })
          .forEach(function (el) { list.appendChild(el); });
      });
    }

    apply();
  }

  /* ---------- ссылки в WhatsApp ---------- */

  function initWaLinks() {
    Array.prototype.forEach.call(document.querySelectorAll('[data-wa]'), function (el) {
      var text = el.getAttribute('data-wa') || 'Здравствуйте! Пишу с сайта dal-tour.ru';
      el.setAttribute('href', waLink(text));
      el.setAttribute('target', '_blank');
      el.setAttribute('rel', 'noopener');
    });
  }

  /* ---------- год в подвале ---------- */

  function initYear() {
    Array.prototype.forEach.call(document.querySelectorAll('[data-year]'), function (el) {
      el.textContent = String(new Date().getFullYear());
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    initDrawer();
    initPicker();
    initLeadForm();
    initFilters();
    initWaLinks();
    initYear();
  });
})();
