#!/usr/bin/env python3
"""Генератор лендинга «Туры в Хуньчунь».

Собирает index.html и по странице на каждую длительность тура.
Запуск:  python3 build.py
Тот же скрипт переиспользуется под Яньцзи — менять блок CITY и TRANSPORT.

Требования — в PRD.md. В комментариях ниже проставлены id требований,
чтобы было видно, что чем закрыто.
"""
import hashlib
import os
import pathlib
import re
import shutil
import sys
from urllib.parse import quote

HERE = os.path.dirname(os.path.abspath(__file__))

# J1: боевые адреса. GitHub Pages разрешает один домен на репозиторий,
# поэтому апекс и каждый сабдомен — свой репозиторий и своя папка в dist/.
HOSTS = {
    "main": "hunchun-hunchun.ru",
    "stoma": "dental.hunchun-hunchun.ru",
    "lech": "clinic.hunchun-hunchun.ru",
}
MIRROR = "xn--h1adcgsc.xn--h1adcgsc.xn--p1ai"   # хуньчунь-хуньчунь.рф в punycode

# python3 build.py          — превью, всё в одной папке, ссылки относительные
# python3 build.py --split  — боевая сборка в dist/, ссылки между сайтами абсолютные
SPLIT = "--split" in sys.argv
DIST = os.path.join(HERE, "dist")


def asset_v(rel: str) -> str:
    """Версия файла по хэшу содержимого. Поменялся файл — поменялась ссылка,
    и браузер не отдаст из кэша старый CSS или JS."""
    data = pathlib.Path(os.path.join(HERE, rel)).read_bytes()
    return f"{rel}?v={hashlib.sha1(data).hexdigest()[:8]}"


def site_url(key: str, path: str = "") -> str:
    """Ссылка на страницу. В боевой сборке — абсолютная, иначе относительная."""
    if not SPLIT:
        return {"main": f"index.html{path}",
                "stoma": "stomatologiya.html",
                "lech": "lechenie.html"}[key]
    if key == "main":
        return f"https://{HOSTS['main']}/{path}"
    return f"https://{HOSTS[key]}/"



# ---------------------------------------------------------------- город

CITY = {
    "name": "Хуньчунь",
    "name_pre": "Хуньчуне",       # предложный падеж
    "hiero": "珲春",
    "from": "Владивостока",
    "from_gen": "Владивосток",    # именительный, для строк «Владивосток — Хуньчунь»
    "lead": "Ближайший к Владивостоку город Китая. Выезды ежедневно, "
            "туры от 3 до 10 дней.",
}

# J2, J3: домены от заказчика. Канонический выбираем позже (см. PRD).
DOMAINS = ["hunchun-hunchun.ru", "хуньчунь-хуньчунь.рф"]

# K: отдельные разделы «просто текст и пара картинок».
# Если заказчик захочет их на своих доменах — каждая страница уже
# самодостаточна, выносится копированием вместе с assets.
PAGES = [
    {
        "slug": "stomatologiya.html",
        "nav": "Стоматология",
        "content": "stomatologiya.md",
        "title": "Стоматология в Хуньчуне — лечение и протезирование зубов, "
                 "цены и отзывы",
        "desc": "Стоматология в Хуньчуне, Китай: лечение зубов, протезирование "
                "и имплантация. Цены, отзывы и поездки в Хуньчунь из "
                "Владивостока с компанией «Дальтур».",
        "imgs": ["stoma-1", "stoma-2"],
        "videos": [("Стоматология в Хуньчуне",
                    "https://dzen.ru/video/watch/667cb4c8c5d3b34f342f0946",
                    "video-stoma-1", 1259, "vkGZpvH8-TWU")],
        "wa": "Здравствуйте! Интересует стоматология в Хуньчуне.",
    },
    {
        "slug": "lechenie.html",
        "nav": "Лечение",
        "content": "lechenie.md",
        "title": "Лечение в Хуньчуне, Китай — цены, клиники, отзывы | ДАЛЬТУР",
        "desc": "Лечение в Хуньчуне из Владивостока: стоматология, лечение "
                "зубов, позвоночника и суставов. Цены, клиники, процедуры и "
                "организация поездки в Китай с ДАЛЬТУР.",
        "imgs": ["lech-1", "lech-2"],
        # второй ролик заказчик прислал ссылкой yandex.ru/video/preview/… —
        # это обёртка, которая крутит две сторонние рекламы перед роликом.
        # Источник — Дзен, канал ДАЛЬТУР, ссылаемся напрямую.
        "videos": [("Лечение и стоматология в Хуньчуне",
                    "https://dzen.ru/video/watch/656c36c30befad215ce48720",
                    "video-lech-1", 1402, "veb3SLmoQ5Hk"),
                   ("Лечение в Хуньчуне: клиники и цены",
                    "https://dzen.ru/video/watch/695b5698a45e4e67c3bbee6a",
                    "video-lech-2", 1108, "oy0Z1aSYKAAA")],
        "wa": "Здравствуйте! Интересует лечение в Хуньчуне.",
    },
]


# Тег транспорта. Для Яньцзи будет «АВТОБУС + ПОЕЗД» — F7.
TRANSPORT = "АВТОБУС"

# B1, B2: тура на 2 дня не существует, минимум — 3 дня / 2 ночи.
TOURS = [(n, n - 1) for n in range(3, 11)]

# ---------------------------------------------------------------- контакты

PHONE_MAIN_HUMAN = "+7 (964) 44-44-144"
PHONE_MAIN_TEL = "+79644444144"
PHONES_EXTRA = [("+7 (423) 248-48-92", "+74232484892"),
                ("+7 (423) 248-48-91", "+74232484891")]
WA_NUMBER = "79644444144"
TG_LINK = "https://t.me/daltourChina"     # C4: закрыто, ссылка от заказчика
SOCIALS = [("VK", "https://vk.com/daltour"),
           ("YouTube", "https://youtube.com/daltour"),
           ("Дзен", "https://dzen.ru/daltour")]
ADDRESS = "690091, Россия, г. Владивосток,<br>ул. Мордовцева 3, офис 705"
HOURS = "ПН–ПТ 10:00–18:00, СБ–ВС выходной"

FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'"
           "%3E%3Crect width='32' height='32' rx='7' fill='%23CE2B22'/%3E%3Ctext x='16' y='22'"
           " font-family='sans-serif' font-size='17' font-weight='700' fill='white'"
           " text-anchor='middle'%3E%D0%94%3C/text%3E%3C/svg%3E")

# A5, I3: фотографий на сайте сейчас нет — на первом экране их убрали,
# в карточках туров их место занимают видео. Хелперы picture() и CREDITS
# оставлены: вернуть снимок = снова вызвать picture() в нужном месте.
CREDITS = {
    "hero": {
        "alt": "Торговая улица в Хуньчуне с вывеской «Торговый центр»",
        "author": "Baycrest",
        "lic": "CC BY-SA 2.5",
        "lic_url": "https://creativecommons.org/licenses/by-sa/2.5/deed.ru",
        "src": "https://commons.wikimedia.org/wiki/File:Hunchun_Yanhe_Xijie.jpg",
    },
}

IMG_DIR = os.path.join(HERE, "assets", "img")


def credit_line(name: str) -> str:
    c = CREDITS.get(name)
    if not c:
        return ""
    return (f'<figcaption class="credit">Фото: '
            f'<a href="{c["src"]}" target="_blank" rel="noopener nofollow">{c["author"]}</a>, '
            f'<a href="{c["lic_url"]}" target="_blank" rel="noopener nofollow">{c["lic"]}</a>, '
            f'кадрировано</figcaption>')


def has_img(name: str) -> bool:
    return os.path.exists(os.path.join(IMG_DIR, name))


def picture(name: str, alt: str, cls: str, eager: bool = False,
            w: int = 1600, h: int = 480) -> str:
    """<img> с webp-версией, если она есть. Пустая строка, если файла нет."""
    if not has_img(name + ".jpg"):
        return ""
    loading = 'loading="eager" fetchpriority="high"' if eager else 'loading="lazy"'
    webp = (f'<source srcset="assets/img/{name}.webp" type="image/webp">'
            if has_img(name + ".webp") else "")
    return (f'<figure class="shot {cls}"><picture>{webp}'
            f'<img src="assets/img/{name}.jpg" alt="{alt}" {loading} decoding="async"'
            f' width="{w}" height="{h}"></picture>{credit_line(name)}</figure>')


def wa(text: str) -> str:
    return f"https://wa.me/{WA_NUMBER}?text={quote(text)}"


def plural(n: int, forms: tuple) -> str:
    n10, n100 = n % 10, n % 100
    if n10 == 1 and n100 != 11:
        return forms[0]
    if 2 <= n10 <= 4 and not (10 <= n100 < 20):
        return forms[1]
    return forms[2]


def days_word(n: int) -> str:
    return plural(n, ("день", "дня", "дней"))


def nights_word(n: int) -> str:
    return plural(n, ("ночь", "ночи", "ночей"))


def label(d: int, n: int) -> str:
    return f"{d} {days_word(d)} / {n} {nights_word(n)}"


def slug(d: int) -> str:
    return f"tur-{d}-{'dnya' if d < 5 else 'dney'}.html"


def canon(key: str, path: str = "") -> str:
    """Канонический адрес страницы. Всегда боевой хост, даже на зеркале."""
    return f"https://{HOSTS[key]}/{path}"


def tour_url(d: int, base: str = "") -> str:
    """Страницы туров живут на основном сайте."""
    return site_url("main", slug(d)) if SPLIT else f"{base}{slug(d)}"


# H1, H2: видео НЕ встраиваем плеером — по клику открывается новая вкладка
# с Яндексом, сайт остаётся в своей. Так страница не тянет чужой скрипт.
# Обычно 3–4 ролика на тур, максимум 5.
VIDEO_SLOTS = 4

# Заполняется, когда заказчик пришлёт ссылки:
#   VIDEOS = {3: [("Аквапарк", "https://..."), ("Зоопарк", "https://...")]}
# ключ — количество дней в туре.
VIDEOS: dict[int, list[tuple[str, str]]] = {}


# G1: дни подписываем словами — «люди не понимают один, два, три»
ORDINALS = ["", "Первый", "Второй", "Третий", "Четвёртый", "Пятый",
            "Шестой", "Седьмой", "Восьмой", "Девятый", "Десятый"]


# ---------------------------------------------------------------- иконки

IC_WA = ('<svg width="18" height="18" viewBox="0 0 18 18" fill="none" aria-hidden="true">'
         '<path d="M2.5 15.5l1-3.3A6.3 6.3 0 1 1 6 15l-3.5.5z" stroke="currentColor"'
         ' stroke-width="1.5" stroke-linejoin="round"/></svg>')
IC_TG = ('<svg width="18" height="18" viewBox="0 0 18 18" fill="none" aria-hidden="true">'
         '<path d="M1.8 8.4l13.4-5.2-2.3 12-4-3-2 2-.5-3.6 6.2-5.6-7.5 4.4-3.3-1z"'
         ' stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/></svg>')
IC_PHONE = ('<svg width="18" height="18" viewBox="0 0 18 18" fill="none" aria-hidden="true">'
            '<path d="M3 3.5h3l1.2 3-1.6 1.2a9 9 0 0 0 4.7 4.7L11.5 11l3 1.2v3a13 13 0'
            ' 0 1-11.5-11.7z" stroke="currentColor" stroke-width="1.4"'
            ' stroke-linejoin="round"/></svg>')
IC_ARROW = ('<svg width="14" height="12" viewBox="0 0 14 12" fill="none" aria-hidden="true">'
            '<path d="M1 6h11M8 2l4 4-4 4" stroke="currentColor" stroke-width="1.6"'
            ' stroke-linecap="round" stroke-linejoin="round"/></svg>')
IC_PLAY = ('<svg width="34" height="34" viewBox="0 0 34 34" fill="none" aria-hidden="true">'
           '<circle cx="17" cy="17" r="16" stroke="currentColor" stroke-width="1.6"/>'
           '<path d="M14 11.5l9 5.5-9 5.5z" fill="currentColor"/></svg>')


# ---------------------------------------------------------------- общие блоки

def contacts(title: str, note: str, wa_text: str, anchor: str = "") -> str:
    """C1–C3, D4: WhatsApp → Telegram → трубка. Одинаково на всех страницах."""
    ident = f' id="{anchor}"' if anchor else ""
    return f"""
  <section class="section"{ident}>
    <div class="wrap">
      <div class="contacts">
        <div class="contacts__text">
          <b>{title}</b>
          <span>{note}</span>
        </div>
        <div class="contacts__actions">
          <a class="btn btn--primary" href="{wa(wa_text)}" target="_blank" rel="noopener">{IC_WA} Спросить в WhatsApp</a>
          <a class="btn btn--ghost" href="{TG_LINK}" target="_blank" rel="noopener">{IC_TG} Спросить в Telegram</a>
          <a class="btn btn--ghost btn--tel" href="tel:{PHONE_MAIN_TEL}">{IC_PHONE} {PHONE_MAIN_HUMAN}</a>
        </div>
      </div>
    </div>
  </section>
"""


# ---------------------------------------------------------------- каркас

# Шрифты лежат на своём домене: запрос к Google Fonts блокировал отрисовку
# (~750 мс по PageSpeed), а из России fonts.googleapis.com бывает медленным.
# Оба шрифта вариативные — один файл на набор символов покрывает все толщины.
FONT_RANGES = {
    "cyrillic": "U+0301, U+0400-045F, U+0490-0491, U+04B0-04B1, U+2116",
    "latin": ("U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, "
              "U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, "
              "U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD"),
}
FONTS = (("Golos Text", "golos", "400 700"), ("Unbounded", "unbounded", "600 700"))


def font_faces(base: str = "") -> str:
    return "".join(
        f"@font-face{{font-family:'{family}';font-style:normal;font-weight:{weights};"
        f"font-display:swap;src:url({base}{asset_v(f'assets/fonts/{stem}-{sub}.woff2')}) "
        f"format('woff2');unicode-range:{rng}}}"
        for family, stem, weights in FONTS for sub, rng in FONT_RANGES.items())


def inline_css() -> str:
    """main.css прямо в <head>: минус один блокирующий запрос. Кэш на GitHub
    Pages всё равно 10 минут, отдельный файл почти ничего не экономит."""
    css = pathlib.Path(os.path.join(HERE, "assets/css/main.css")).read_text(encoding="utf-8")
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"\s+", " ", css)
    return re.sub(r"\s*([{};,>])\s*", r"\1", css).strip()


def head(title: str, desc: str, base: str = "", sticky: bool = False,
         canonical: str = "") -> str:
    # Превью (staging на github.io) закрываем от индексации целиком: иначе
    # после запуска это полная копия боевого сайта на чужом адресе.
    # В боевой сборке каждая страница указывает свой канонический адрес —
    # по нему же будет ссылаться зеркало на .рф.
    if SPLIT and canonical:
        seo = (f'<link rel="canonical" href="{canonical}">\n'
               f'<meta property="og:url" content="{canonical}">')
    else:
        seo = '<meta name="robots" content="noindex, nofollow">'
    return f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
{seo}
<meta name="theme-color" content="#FBF9F5">
<meta property="og:type" content="website">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:locale" content="ru_RU">
<link rel="icon" href="{FAVICON}">
<link rel="preload" href="{base}{asset_v('assets/fonts/unbounded-cyrillic.woff2')}" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{base}{asset_v('assets/fonts/golos-cyrillic.woff2')}" as="font" type="font/woff2" crossorigin>
<style>{font_faces(base)}{inline_css()}</style>
</head>
<body{' class="has-stickybar"' if sticky else ''}>

<a class="skip-link" href="#main">Перейти к содержимому</a>
"""


def header(base: str = "") -> str:
    wa_href = wa(f"Здравствуйте! Интересуют туры в {CITY['name']} из {CITY['from']}.")
    return f"""
<div class="topbar">
  <div class="wrap">
    <span>Выезды из {CITY['from']} ежедневно</span>
    <div class="topbar__right">
      <span class="topbar__hours">{HOURS}</span>
      <span class="topbar__sep" aria-hidden="true">|</span>
      <a href="{TG_LINK}">Telegram</a>
      {' '.join(f'<a href="{u}">{n}</a>' for n, u in SOCIALS)}
    </div>
  </div>
</div>

<header class="header">
  <div class="wrap">
    <button type="button" class="icon-btn icon-btn--plain header__burger" data-drawer-open aria-expanded="false" aria-controls="drawer" aria-label="Открыть меню">
      <svg width="22" height="16" viewBox="0 0 22 16" fill="none" aria-hidden="true"><path d="M0 1h22M0 8h22M0 15h16" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>
    </button>

    <div class="header__center"><a class="logo" href="{site_url("main")}">ДАЛЬТУР</a></div>

    <nav class="header__nav" aria-label="Основная навигация">
      <a href="{site_url("main", "#tury")}">Все туры</a>
      <a href="{site_url("stoma")}">Стоматология</a>
      <a href="{site_url("lech")}">Лечение</a>
      <a href="{site_url("main", "#kontakty")}">Контакты</a>
    </nav>

    <div class="header__contacts">
      <span class="header__phone">
        <a href="tel:{PHONE_MAIN_TEL}">{PHONE_MAIN_HUMAN}</a>
        <span>Единая справочная и WhatsApp</span>
      </span>
      <span class="msgr">
        <a class="btn btn--primary" href="{wa_href}" target="_blank" rel="noopener">{IC_WA} WhatsApp</a>
        <a class="icon-btn icon-btn--tg" href="{TG_LINK}" target="_blank" rel="noopener" aria-label="Написать в Telegram">{IC_TG}</a>
      </span>
    </div>

    <a class="icon-btn icon-btn--accent header__wa-mobile" href="{wa_href}" target="_blank" rel="noopener" aria-label="Написать в WhatsApp">{IC_WA}</a>
  </div>
</header>

<div class="drawer" id="drawer" data-drawer data-open="false">
  <button type="button" class="drawer__backdrop" data-drawer-close aria-label="Закрыть меню"></button>
  <nav class="drawer__panel" aria-label="Мобильное меню">
    <div class="drawer__top">
      <span class="logo">ДАЛЬТУР</span>
      <button type="button" class="icon-btn" data-drawer-close aria-label="Закрыть меню">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M1 1l14 14M15 1L1 15" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>
      </button>
    </div>
    <a href="{site_url("main")}">Главная</a>
    <a href="{site_url("main", "#tury")}">Все туры</a>
    <a href="{site_url("main", "#o-gorode")}">О городе</a>
    <a href="{site_url("stoma")}">Стоматология</a>
    <a href="{site_url("lech")}">Лечение</a>
    <a href="{site_url("main", "#kontakty")}">Контакты</a>
    <a class="drawer__phone" href="tel:{PHONE_MAIN_TEL}">{PHONE_MAIN_HUMAN}</a>
    <a href="{TG_LINK}">Telegram</a>
  </nav>
</div>
"""


def footer(base: str = "", tail: str = "") -> str:
    tours_links = "\n".join(
        f'          <li><a href="{tour_url(d, base)}">{label(d, n)}</a></li>'
        for d, n in TOURS)
    # C5: городские номера внизу
    phones = "\n".join(f'          <a href="tel:{t}">{h}</a>' for h, t in PHONES_EXTRA)
    socials = "\n".join(
        f'          <a href="{u}" aria-label="{n}">{n[:2].upper() if n != "Дзен" else "Дзен"}</a>'
        for n, u in SOCIALS)
    return f"""
<footer class="footer" id="kontakty">
  <div class="wrap">
    <div class="footer__grid">
      <div class="footer__col footer__col--brand">
        <span class="logo">ДАЛЬТУР</span>
        <p class="footer__addr">{ADDRESS}<br>{HOURS}</p>
      </div>
      <div class="footer__col">
        <h3>ТУРЫ В {CITY['name'].upper()}</h3>
        <ul>
{tours_links}
        </ul>
      </div>
      <div class="footer__col">
        <h3>КОНТАКТЫ</h3>
        <div class="footer__phones">
          <a href="tel:{PHONE_MAIN_TEL}">{PHONE_MAIN_HUMAN}</a>
{phones}
        </div>
        <div class="footer__social">
          <a href="{TG_LINK}" aria-label="Telegram">TG</a>
{socials}
        </div>
      </div>
    </div>

    <p class="footer__legal">
      Информация на сайте носит информационный характер и не является публичной офертой (ст. 437 ГК РФ).
      Стоимость тура зависит от дат выезда, категории отеля и количества дней — уточняйте у менеджера
      по телефону {PHONE_MAIN_HUMAN} или в WhatsApp.
      <br>© <span data-year>2026</span> ДАЛЬТУР.
    </p>
  </div>
</footer>
{tail}
<script src="{base}{asset_v('assets/js/main.js')}" defer></script>
</body>
</html>
"""


# ---------------------------------------------------------------- главная

def build_index() -> str:
    cards = "\n".join(f"""        <a class="duration" href="{slug(d)}">
          <span class="duration__n">
            <span class="duration__days">{d} {days_word(d)}</span>
            <span class="duration__nights">{n} {nights_word(n)}</span>
          </span>
          <span class="duration__go">Программа {IC_ARROW}</span>
        </a>""" for d, n in TOURS)

    first, last = TOURS[0][0], TOURS[-1][0]

    return (head(
        f"Туры в {CITY['name']} из {CITY['from']} — ДАЛЬТУР",
        f"Туры в {CITY['name']} из {CITY['from']} от {first} до {last} дней. "
        f"Программа по дням, выезды ежедневно. "
        f"Звоните {PHONE_MAIN_HUMAN} или пишите в WhatsApp.",
        canonical=canon("main"))
        + header() + f"""
<main id="main">

  <!-- A1: без слова «туроператор». A3–A5: ни кнопок, ни фактов, ни фото. -->
  <section class="hero hero--lean">
    <div class="wrap">
      <h1>Туры в {CITY['name']} <br class="br-desktop">из {CITY['from']}</h1>
      <p class="hero__lead">{CITY['lead']}</p>
    </div>
  </section>

  <!-- A6, B3: каталог сразу под заголовком -->
  <section class="section section--tight" id="tury">
    <div class="wrap">
      <div class="durations">
{cards}
      </div>
    </div>
  </section>

  <!-- D1, D2: без заголовка «Почему ДАЛЬТУР», только два факта -->
  <section class="section">
    <div class="wrap">
      <ul class="marks">
        <li class="mark">
          <svg width="22" height="22" viewBox="0 0 20 20" fill="none" aria-hidden="true"><circle cx="10" cy="7" r="3" stroke="#A7211A" stroke-width="1.4"/><path d="M4 17c0-3.3 2.7-5 6-5s6 1.7 6 5" stroke="#A7211A" stroke-width="1.4" stroke-linecap="round"/></svg>
          Гиды-переводчики
        </li>
        <li class="mark">
          <svg width="22" height="22" viewBox="0 0 20 20" fill="none" aria-hidden="true"><circle cx="10" cy="10" r="7.5" stroke="#A7211A" stroke-width="1.4"/><path d="M10 6v4.3l2.8 1.7" stroke="#A7211A" stroke-width="1.4" stroke-linecap="round"/></svg>
          Выезды ежедневно
        </li>
      </ul>
    </div>
  </section>

  <section class="section" id="o-gorode">
    <div class="wrap">
      <div class="section__head"><h2>О городе</h2></div>
      <p style="margin-top:14px;max-width:780px;font-size:15px;line-height:1.65;color:var(--muted)">
        [ТЕКСТ О ГОРОДЕ {CITY['name'].upper()} — 2–3 абзаца, пришлёт заказчик или копируем с dal-tour.ru.
        Что за город, чем интересен, сколько ехать из {CITY['from']}, что обычно смотрят.]
      </p>
    </div>
  </section>
"""
        # D4, D6: «рады проконсультировать», без оговорки про праздники (D5)
        + contacts(
            "Всегда рады вас проконсультировать в WhatsApp",
            "Стоимость зависит от дат выезда, категории отеля и количества дней. "
            "Позвоните или напишите — посчитаем на ваши даты.",
            f"Здравствуйте! Подскажите по турам в {CITY['name']}.")
        + """
</main>
""" + footer())


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render_md(name: str) -> tuple:
    """Очень простой markdown: # заголовок, ## подзаголовок, - список, абзацы.
    Возвращает (h1, html остального текста)."""
    raw = pathlib.Path(os.path.join(HERE, "content", name)).read_text(encoding="utf-8")
    h1, parts = "", []
    for block in raw.split("\n\n"):
        b = block.strip()
        if not b:
            continue
        if b.startswith("# "):
            h1 = esc(b[2:].strip())
        elif b.startswith("## "):
            parts.append(f"<h2>{esc(b[3:].strip())}</h2>")
        elif b.startswith("- "):
            items = "".join(f"<li>{esc(l[2:].strip())}</li>"
                            for l in b.split("\n") if l.strip().startswith("- "))
            parts.append(f"<ul class=\"prose__list\">{items}</ul>")
        else:
            parts.append(f"<p>{esc(' '.join(b.split()))}</p>")
    return h1, "\n        ".join(parts)


def video_cards(d: int) -> str:
    """H1–H3: карточка-ссылка на Яндекс, открывается в новой вкладке."""
    items = VIDEOS.get(d)
    if items:
        return "\n".join(f"""        <a class="video" href="{url}" target="_blank" rel="noopener">
          <span class="video__frame">
            <span class="video__play">{IC_PLAY}</span>
            <span class="video__hint">Смотреть на Яндексе</span>
          </span>
          <span class="video__cap">{name}</span>
        </a>""" for name, url in items)

    return "\n".join(f"""        <div class="video video--empty">
          <span class="video__frame">
            <span class="video__play">{IC_PLAY}</span>
            <span class="video__hint">Откроется на Яндексе в новой вкладке</span>
          </span>
          <span class="video__cap">[ЭКСКУРСИЯ {v} — название и ссылку пришлёт заказчик]</span>
        </div>""" for v in range(1, VIDEO_SLOTS + 1))


# ---------------------------------------------------------------- контентные страницы

def build_page(pg: dict) -> str:
    """K: статья заказчика, фото, видео и контакты — стоматология, лечение."""
    h1, article = render_md(pg["content"])

    shots = ""
    for i, name in enumerate(pg["imgs"]):
        img = picture(name, f"{h1}, фотография {i + 1}", "", w=1600, h=1067)
        shots += (f'        <div class="gallery__item">{img}</div>\n' if img else
                  f'        <div class="gallery__item gallery__item--empty">'
                  f'<span>[ФОТОГРАФИЯ {i + 1} — пришлёт заказчик]</span></div>\n')

    # видео открывается на Яндексе в новой вкладке, как на страницах туров
    # Плеер «по клику»: сначала только превью, iframe Дзена создаётся при
    # нажатии и сразу стартует. Страница не грузит плеер заранее, а href на
    # страницу ролика остаётся запасным путём, если скрипты отключены.
    # embed-id Дзен отдаёт в <meta name="twitter:player:stream"> страницы ролика.
    def vcard(name: str, url: str, thumb: str, secs: int, embed: str = "") -> str:
        mins = f"{secs // 60} мин"
        data = f' data-embed="https://dzen.ru/embed/{embed}"' if embed else ""
        hint = "Смотреть здесь же" if embed else "Откроется на Дзене в новой вкладке"
        img = (f'<img src="assets/img/{thumb}.jpg" alt="" loading="lazy" '
               f'decoding="async" width="516" height="290">'
               if has_img(thumb + ".jpg") else "")
        return f"""        <a class="video{' video--thumb' if img else ''}" href="{url}" target="_blank" rel="noopener"{data}>
          <span class="video__frame">
            {img}
            <span class="video__play">{IC_PLAY}</span>
            <span class="video__len">{mins}</span>
          </span>
          <span class="video__cap">{name}<small>{hint}</small></span>
        </a>"""

    vids = "\n".join(vcard(*v) for v in pg["videos"])

    key = "stoma" if pg["slug"].startswith("stoma") else "lech"
    return (head(pg["title"], pg["desc"], canonical=canon(key)) + header() + f"""
<main id="main">

  <section class="hero hero--lean">
    <div class="wrap">
      <nav class="crumbs" aria-label="Хлебные крошки">
        <a href="{site_url("main")}">Туры в {CITY['name']}</a><span aria-hidden="true">/</span>
        <span aria-current="page">{pg["nav"]}</span>
      </nav>
      <h1>{h1}</h1>
    </div>
  </section>

  <section class="section section--tight">
    <div class="wrap">
      <article class="prose">
        {article}
      </article>
    </div>
  </section>

  <section class="section" id="video">
    <div class="wrap">
      <div class="section__head"><h2>Видео</h2></div>
      <div class="videos">
{vids}
      </div>
    </div>
  </section>

  <section class="section">
    <div class="wrap">
      <div class="gallery">
{shots}      </div>
    </div>
  </section>

  <section class="section">
    <div class="wrap">
      <div class="notice">
        <b>Важно</b>
        <p>[ДИСКЛЕЙМЕР — проверить с юристом. Реклама медицинских услуг в РФ,
        как правило, требует предупреждения о противопоказаниях и
        необходимости консультации специалиста. Точную формулировку
        согласовать до публикации на боевом домене.]</p>
      </div>
    </div>
  </section>
"""
        + contacts("Всегда рады вас проконсультировать",
                   "Расскажем, как проходит поездка, и ответим на вопросы.",
                   pg["wa"])
        + """
</main>
""" + footer())


# ---------------------------------------------------------------- страница тура

def build_tour(d: int, n: int) -> str:
    lbl = label(d, n)
    wa_text = (f"Здравствуйте! Интересует тур в {CITY['name']} на {lbl}. "
               f"Подскажите ближайшие даты и стоимость.")

    # G1, G2: «Первый день» вместо цифры
    days = []
    for i in range(1, d + 1):
        if i == 1:
            title = f"{CITY['from_gen']} — {CITY['name']}"
            body = ("[ВЫЕЗД из Владивостока, пункт пропуска, прибытие в "
                    f"{CITY['name_pre']}, размещение в отеле. Текст пришлёт заказчик.]")
        elif i == d:
            title = f"{CITY['name']} — {CITY['from_gen']}"
            body = ("[ОСВОБОЖДЕНИЕ НОМЕРОВ, выезд, прибытие во Владивосток. "
                    "Текст пришлёт заказчик.]")
        else:
            title = CITY["name"]
            body = "[ПРОГРАММА ДНЯ и экскурсии. Текст пришлёт заказчик.]"
        days.append(f"""        <article class="day">
          <div class="day__head">
            <span class="day__ord">{ORDINALS[i]} день</span>
            <h3 class="day__title">{title}</h3>
          </div>
          <p>{body}</p>
        </article>""")

    videos = video_cards(d)

    others = "\n".join(
        f'        <a class="pill" href="{tour_url(od)}">{label(od, on)}</a>'
        for od, on in TOURS if od != d)

    return (head(
        f"Тур в {CITY['name']} {lbl} из {CITY['from']} — ДАЛЬТУР",
        f"Тур в {CITY['name']} на {lbl} из {CITY['from']}: программа по дням, "
        f"выезды ежедневно. Стоимость уточняйте по телефону {PHONE_MAIN_HUMAN}.",
        sticky=True, canonical=canon("main", slug(d)))
        + header() + f"""
<main id="main">

  <section class="tour-head">
    <div class="wrap">
      <nav class="crumbs" aria-label="Хлебные крошки">
        <a href="{site_url("main")}">Туры в {CITY['name']}</a><span aria-hidden="true">/</span>
        <span aria-current="page">{lbl}</span>
      </nav>

      <div class="tour-head__row">
        <h1>Тур в {CITY['name']}<br>{lbl}</h1>
        <span class="tour-head__hiero" lang="zh" aria-hidden="true">{CITY['hiero']}</span>
      </div>

      <!-- F6: тег транспорта оставляем, заказчику понравился -->
      <div class="tour-head__tags">
        <span class="tag tag--jade">{TRANSPORT}</span>
        <span class="tag tag--sand">ВЫЕЗДЫ ЕЖЕДНЕВНО</span>
      </div>

      <!-- F1, F2: без «Дороги» и «Времени выезда». F3: только длительность и питание. -->
      <dl class="facts facts--pair">
        <div class="fact"><dt>Длительность</dt><dd>{lbl}</dd></div>
        <div class="fact"><dt>Питание</dt><dd>Завтраки</dd></div>
      </dl>
    </div>
  </section>

  <section class="section" id="programma">
    <div class="wrap">
      <div class="section__head"><h2>Программа по дням</h2></div>
      <div class="days">
{chr(10).join(days)}
      </div>
    </div>
  </section>
"""
        # C6: после программы — телефон и мессенджеры
        + contacts("Звоните и пишите — подскажем по этому туру",
                   "Ответим в рабочее время: ПН–ПТ 10:00–18:00.",
                   wa_text)
        + f"""
  <section class="section" id="video">
    <div class="wrap">
      <div class="section__head">
        <h2>Экскурсии на видео</h2>
        <span class="section__note">Яндекс.Видео</span>
      </div>
      <div class="videos">
{videos}
      </div>
    </div>
  </section>
"""
        # C6: и ещё раз после видео
        + contacts("Всегда рады вас проконсультировать",
                   "Подберём даты и посчитаем стоимость.",
                   wa_text)
        + f"""
  <section class="section" id="drugie">
    <div class="wrap">
      <div class="section__head">
        <h2>Другая длительность</h2>
        <span class="section__note">та же программа, больше дней в городе</span>
      </div>
      <div class="pill-row">
{others}
      </div>
    </div>
  </section>

</main>
""" + footer(tail=f"""
<div class="stickybar">
  <a class="icon-btn" href="tel:{PHONE_MAIN_TEL}" aria-label="Позвонить">{IC_PHONE}</a>
  <a class="btn btn--primary" href="{wa(wa_text)}" target="_blank" rel="noopener">Спросить в WhatsApp</a>
</div>
"""))


def build_dist() -> list:
    """Три отдельных корня под три домена: у каждого свой CNAME."""
    out = []

    def clean(root: str) -> None:
        """Чистим только сгенерированное. .git внутри трогать нельзя —
        каждая папка dist/* это рабочая копия своего репозитория."""
        if not os.path.isdir(root):
            return
        for name in os.listdir(root):
            if name == ".git":
                continue
            path = os.path.join(root, name)
            shutil.rmtree(path) if os.path.isdir(path) else os.remove(path)

    plan = [
        ("main", HOSTS["main"], None),
        ("stoma", HOSTS["stoma"], PAGES[0]),
        ("lech", HOSTS["lech"], PAGES[1]),
    ]

    for key, host, pg in plan:
        root = os.path.join(DIST, key)
        os.makedirs(root, exist_ok=True)
        clean(root)
        shutil.copytree(os.path.join(HERE, "assets"), os.path.join(root, "assets"))

        with open(os.path.join(root, "CNAME"), "w", encoding="utf-8") as fh:
            fh.write(host + "\n")

        if key == "main":
            with open(os.path.join(root, "index.html"), "w", encoding="utf-8") as fh:
                fh.write(build_index())
            for d, n in TOURS:
                with open(os.path.join(root, slug(d)), "w", encoding="utf-8") as fh:
                    fh.write(build_tour(d, n))
            out.append(f"dist/{key}/ — {host}, {len(TOURS) + 1} страниц")
        else:
            with open(os.path.join(root, "index.html"), "w", encoding="utf-8") as fh:
                fh.write(build_page(pg))
            out.append(f"dist/{key}/ — {host}, 1 страница")

        # GitHub Pages иначе прогонит файлы через Jekyll
        open(os.path.join(root, ".nojekyll"), "w").close()

        # sitemap и robots — чтобы поисковики сразу нашли все страницы.
        # Host: не пишем: Яндекс отказался от директивы в 2018, главное зеркало
        # теперь определяется по canonical и редиректам.
        urls = ([canon("main")] + [canon("main", slug(d)) for d, _ in TOURS]
                if key == "main" else [canon(key)])
        today = __import__("datetime").date.today().isoformat()
        sm = "".join(f"  <url><loc>{u}</loc><lastmod>{today}</lastmod></url>\n" for u in urls)
        with open(os.path.join(root, "sitemap.xml"), "w", encoding="utf-8") as fh:
            fh.write('<?xml version="1.0" encoding="UTF-8"?>\n'
                     '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                     f"{sm}</urlset>\n")
        with open(os.path.join(root, "robots.txt"), "w", encoding="utf-8") as fh:
            fh.write(f"User-agent: *\nAllow: /\n\nSitemap: https://{host}/sitemap.xml\n")

    return out


def main() -> None:
    # В боевом режиме пишем только dist/, чтобы в папку превью не попали
    # абсолютные ссылки на ещё не поднятые домены.
    if SPLIT:
        for w in build_dist():
            print("  ", w)
        print("\nдальше: каждая папка dist/* — корень отдельного репозитория,")
        print("CNAME внутри уже проставлен. DNS-записи — в DEPLOY.md")
        return

    written = []

    with open(os.path.join(HERE, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(build_index())
    written.append("index.html")

    # подчистить страницы туров, которых больше нет в каталоге
    keep = {slug(d) for d, _ in TOURS}
    for f in os.listdir(HERE):
        if f.startswith("tur-") and f.endswith(".html") and f not in keep:
            os.remove(os.path.join(HERE, f))
            written.append(f"{f} — удалена")

    for d, n in TOURS:
        with open(os.path.join(HERE, slug(d)), "w", encoding="utf-8") as fh:
            fh.write(build_tour(d, n))
        written.append(slug(d))

    for pg in PAGES:
        with open(os.path.join(HERE, pg["slug"]), "w", encoding="utf-8") as fh:
            fh.write(build_page(pg))
        written.append(pg["slug"])

    print("собрано (превью):")
    for w in written:
        print("  ", w)


if __name__ == "__main__":
    main()
