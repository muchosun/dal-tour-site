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
    # 633865: адреса кириллицей в латинице, как Яндекс подсвечивает в выдаче
    "stoma": "stomatologiya.hunchun-hunchun.ru",
    "lech": "lechenie-v-kitae.hunchun-hunchun.ru",
}
# Старые адреса разделов уводят на новые — ссылки на них уже разосланы
OLD_HOSTS = {"stoma": "dental.hunchun-hunchun.ru", "lech": "clinic.hunchun-hunchun.ru"}

# R1 (633847, 633863, 633864): тот же сайт с туров под другой город
# отправления, на поддомене. Программа та же, меняется город старта.
# draft — закрыт от поиска, пока заказчик не пришлёт тексты под город.
DEPARTURES = {
    "main": {"host": "hunchun-hunchun.ru", "from": "Владивостока", "from_gen": "Владивосток",
             "to_acc": "во Владивосток", "route_there": "Владивосток", "route_back": "Владивосток",
             "draft": False},
    "us": {"host": "ussuriysk.hunchun-hunchun.ru", "from": "Уссурийска", "from_gen": "Уссурийск",
           "to_acc": "в Уссурийск", "route_there": "Уссурийск", "route_back": "Уссурийск",
           "draft": True},
    # из Хабаровска — свой автобус до Уссурийска, там пересадка
    "hb": {"host": "habarovsk.hunchun-hunchun.ru", "from": "Хабаровска", "from_gen": "Хабаровск",
           "to_acc": "в Хабаровск", "route_there": "Хабаровск — Уссурийск",
           "route_back": "Уссурийск — Хабаровск", "draft": True},
}
DEP = "main"   # какой город сейчас собираем; переключает build_dist()
MIRROR = "xn----ytbaba5abcbmfug6dded.xn--p1ai"   # хуньчунь-хуньчунь.рф в punycode

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
    "lead": "Автобусные туры в Хуньчунь, Китай. Выезды ежедневно.",   # 633800
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
# Порядок от заказчика (633804, 633805): YouTube, Яндекс (Дзен), Rutube, VK,
# Telegram. YouTube и Дзен — как на dal-tour.ru, Rutube прислал заказчик.
# Третье поле — ключ иконки в ARC.
SOCIALS = [("YouTube", "https://www.youtube.com/@DALTOUR", "youtube"),
           ("Дзен", "https://dzen.ru/daltour", "zen"),
           ("Rutube", "https://rutube.ru/channel/54520250/", "rutube"),
           ("VK", "https://vk.com/daltour", "vk"),
           ("Telegram", TG_LINK, "telegram")]
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


# H1–H4: видео экскурсий на страницах туров, одинаковые для всех
# длительностей. Порядок — как у заказчика (633828): приезд, гостиница,
# экскурсии, еда, чайная церемония. Подписи — «тема — туры в Хуньчунь»,
# так просил заказчик для поиска (633829), в том числе у стеклянного моста. Формат как у PAGES["videos"]:
# (подпись, страница на Дзене, превью в assets/img, секунды, embed-id).
TOUR_VIDEOS = [
    ("Дорога из Владивостока на автобусе — туры в Хуньчунь",
     "https://dzen.ru/video/watch/695a3c5f86ae062350c7f467", "video-tour-1", 743, "oy0b1CCQKAAA"),
    ("Гостиницы — туры в Хуньчунь",
     "https://dzen.ru/video/watch/695b90a7d6e03c1d0079b0ec", "video-tour-2", 3461, "oy0ZqQScKAAA"),
    ("Большой Будда в Дуньхуа — туры в Хуньчунь",
     "https://dzen.ru/video/watch/695b130f2e2b4a128b7c39d7", "video-tour-3", 3247, "oy0YCACYKAAA"),
    ("Стеклянный мост — туры в Хуньчунь",
     "https://dzen.ru/video/watch/68102f027535b749adb6df14", "video-tour-4", 1631, "oy0aA8-0IAAA"),
    ("Рестораны и цены — туры в Хуньчунь",
     "https://dzen.ru/video/watch/695b90d3b2bf8e79dd527604", "video-tour-5", 2081, "oy0YQQicKAAA"),
    ("Чайная церемония — туры в Хуньчунь",
     "https://dzen.ru/video/watch/695b0adbe8b4617811c49770", "video-tour-6", 1267, "oy0bi-SUKAAA"),
]


# G1: дни подписываем словами — «люди не понимают один, два, три»
ORDINALS = ["", "Первый", "Второй", "Третий", "Четвёртый", "Пятый",
            "Шестой", "Седьмой", "Восьмой", "Девятый", "Десятый"]


# ---------------------------------------------------------------- иконки

# Иконки сервисов — один набор Arcticons (github.com/Arcticons-Team/Arcticons,
# CC BY-SA 4.0, автор указан в подвале). Линейные, как остальные иконки сайта.
# Сетка 48×48, толщину линии задаёт brand_icon().
ARC = {
    'youtube': '<path fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" d="M43.112 14.394a5 5 0 0 0-3.533-3.533c-2.314-.894-24.732-1.332-31.236.025A5 5 0 0 0 4.81 14.42c-1.045 4.583-1.124 14.491.026 19.177a5 5 0 0 0 3.533 3.533c4.583 1.055 26.371 1.203 31.236 0a5 5 0 0 0 3.533-3.533c1.114-4.993 1.193-14.287-.026-19.203"/><path fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" d="M30.567 23.995L20.12 18.004v11.982Z"/>',
    'zen': '<path fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" d="M24 3.5C24 18.457 29.653 24 44.5 24C29.568 24 24 29.657 24 44.5C24 29.59 18.457 24 3.5 24C18.457 24 24 18.373 24 3.5"/>',
    'rutube': '<path fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" d="M13.5 14.203h16.86a3.624 3.624 0 0 1 3.622 3.623v4.658c0 2-1.623 3.623-3.623 3.623H13.5zm16.046 11.904l4.954 7.69m-21-7.69v7.69"/><rect width="37" height="37" x="5.5" y="5.5" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" rx="4" ry="4"/>',
    'vk': '<path fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" d="M27.55 35.19v-6.64c4.46.68 5.87 4.19 8.71 6.64h7.24a29.36 29.36 0 0 0-7.9-10.47c2.6-3.58 5.36-6.95 6.71-12.06h-6.58c-2.58 3.91-3.94 8.49-8.18 11.51V12.66H18l2.28 2.82v10.05c-3.7-.43-6.2-7.2-8.91-12.87H4.5c2.5 7.66 7.76 24.47 23.05 22.53"/>',
    'telegram': '<path fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" d="M40.83 8.48c1.14 0 2 1 1.54 2.86l-5.58 26.3c-.39 1.87-1.52 2.32-3.08 1.45L20.4 29.26a.4.4 0 0 1 0-.65l15.37-13.88c.7-.62-.15-.92-1.07-.36L15.41 26.54a.46.46 0 0 1-.4.05L6.82 24C5 23.47 5 22.22 7.23 21.33L40 8.69a2.2 2.2 0 0 1 .83-.21"/>',
    'whatsapp': '<path fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" d="M24 2.5c-11.885.013-21.51 9.658-21.497 21.543A21.5 21.5 0 0 0 5.15 34.36L3.5 44.5l10.14-1.65c10.41 5.71 23.48 1.901 29.19-8.51s1.902-23.479-8.509-29.19a21.5 21.5 0 0 0-10.32-2.65Zm-10.75 9.77h5.86a1 1 0 0 1 1 1a10.4 10.4 0 0 0 .66 3.91a1.93 1.93 0 0 1-.66 2.44l-2.05 2a18.6 18.6 0 0 0 3.52 4.79A18.6 18.6 0 0 0 26.35 30l2-2.05c1-1 1.46-1 2.44-.66a10.4 10.4 0 0 0 3.91.66a1.05 1.05 0 0 1 1 1v5.86a1.05 1.05 0 0 1-1 1a23.68 23.68 0 0 1-15.64-6.84a23.6 23.6 0 0 1-6.84-15.64a1.07 1.07 0 0 1 1.03-1.06"/>',
}


def brand_icon(key: str, size: int = 18, stroke: float = 3.2) -> str:
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 48 48" '
            f'stroke-width="{stroke}" aria-hidden="true">{ARC[key]}</svg>')

IC_WA = brand_icon("whatsapp")
IC_TG = brand_icon("telegram")
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
         canonical: str = "", noindex: bool = False) -> str:
    # Превью (staging на github.io) закрываем от индексации целиком: иначе
    # после запуска это полная копия боевого сайта на чужом адресе.
    # В боевой сборке каждая страница указывает свой канонический адрес —
    # по нему же будет ссылаться зеркало на .рф.
    if SPLIT and DEPARTURES[DEP]["draft"]:
        noindex = True
    if SPLIT and canonical and not noindex:
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
    <span>Выезды ежедневно</span>
    <div class="topbar__right">
      <span class="topbar__hours">{HOURS}</span>
      <span class="topbar__sep" aria-hidden="true">|</span>
      {' '.join(f'<a class="topbar__soc" href="{u}" target="_blank" rel="noopener">{brand_icon(k, 15, 3.4)}{n}</a>' for n, u, k in SOCIALS)}
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
    <div class="drawer__contacts">
      <a class="btn btn--primary" href="{wa_href}" target="_blank" rel="noopener">{IC_WA} Спросить в WhatsApp</a>
      <a class="btn btn--ghost" href="{TG_LINK}" target="_blank" rel="noopener">{IC_TG} Спросить в Telegram</a>
      <a class="btn btn--ghost btn--tel" href="tel:{PHONE_MAIN_TEL}">{IC_PHONE} {PHONE_MAIN_HUMAN}</a>
    </div>
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
        f'          <a href="{u}" target="_blank" rel="noopener" aria-label="{n}" title="{n}">{brand_icon(k, 22, 2.8)}</a>'
        for n, u, k in SOCIALS)
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
{socials}
        </div>
      </div>
    </div>

    <p class="footer__legal">
      Информация на сайте носит информационный характер и не является публичной офертой (ст. 437 ГК РФ).
      Стоимость тура зависит от даты выезда, категории отеля 3*, 4*, 5* и количества дней — уточняйте
      у менеджера по телефону {PHONE_MAIN_HUMAN} или в WhatsApp.
      <br>© <span data-year>2026</span> ДАЛЬТУР. Иконки сервисов —
      <a href="https://github.com/Arcticons-Team/Arcticons" target="_blank" rel="noopener">Arcticons</a>, CC BY-SA 4.0.
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
          <span class="duration__go">Программа тура {IC_ARROW}</span>
        </a>""" for d, n in TOURS)

    first, last = TOURS[0][0], TOURS[-1][0]

    return (head(
        f"Туры в {CITY['name']} из {CITY['from']} — ДАЛЬТУР",
        f"Туры в {CITY['name']} из {CITY['from']} от {first} до {last} дней. "
        f"Программа тура, выезды ежедневно. "
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
          <svg width="22" height="22" viewBox="0 0 20 20" fill="none" aria-hidden="true"><rect x="3" y="3" width="14" height="11" rx="2.5" stroke="#A7211A" stroke-width="1.4"/><path d="M3 9h14M6.5 17v-3M13.5 17v-3" stroke="#A7211A" stroke-width="1.4" stroke-linecap="round"/><circle cx="6.5" cy="11.5" r=".9" fill="#A7211A"/><circle cx="13.5" cy="11.5" r=".9" fill="#A7211A"/></svg>
          Рейсовый автобус 100%!
        </li>
        <li class="mark">
          <svg width="22" height="22" viewBox="0 0 20 20" fill="none" aria-hidden="true"><circle cx="10" cy="10" r="7.5" stroke="#A7211A" stroke-width="1.4"/><path d="M10 6v4.3l2.8 1.7" stroke="#A7211A" stroke-width="1.4" stroke-linecap="round"/></svg>
          Выезды ежедневно!
        </li>
      </ul>
    </div>
  </section>

  <section class="section" id="o-gorode">
    <div class="wrap">
      <div class="section__head"><h2>{render_md("o-gorode.md")[0] or "О городе"}</h2></div>
      <div class="prose" style="margin-top:14px">
        {render_md("o-gorode.md")[1]}
      </div>
    </div>
  </section>
"""
        # D4, D6: «рады проконсультировать», без оговорки про праздники (D5)
        + contacts(
            "Всегда рады вас проконсультировать в WhatsApp",
            # 633807: формулировка заказчика
            "Стоимость тура зависит от даты выезда, категории отеля 3*, 4*, 5* "
            "и количества дней.",
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


def vcard(name: str, url: str, thumb: str, secs: int, embed: str = "") -> str:
    """Карточка видео. Нажатие на превью — плеер Дзена прямо на странице
    (iframe создаётся только по клику, заранее ничего не грузится).
    Ссылка под названием и клик с Ctrl/Cmd — ролик в новой вкладке, чтобы,
    закрыв его, человек не закрыл сайт (633831, 633833)."""
    mins = f"{secs // 60} мин"
    data = f' data-embed="https://dzen.ru/embed/{embed}"' if embed else ""
    img = (f'<img src="assets/img/{thumb}.jpg" alt="" loading="lazy" '
           f'decoding="async" width="516" height="290">'
           if has_img(thumb + ".jpg") else "")
    return f"""        <div class="video{' video--thumb' if img else ''}"{data}>
          <a class="video__frame" href="{url}" target="_blank" rel="noopener" aria-label="Смотреть: {name}">
            {img}
            <span class="video__play">{IC_PLAY}</span>
            <span class="video__len">{mins}</span>
          </a>
          <span class="video__cap">{name}<a class="video__ext" href="{url}" target="_blank" rel="noopener">Открыть в новом окне ↗</a></span>
        </div>"""


def video_cards(d: int) -> str:
    return "\n".join(vcard(*v) for v in TOUR_VIDEOS)


# ---------------------------------------------------------------- контентные страницы

def build_page(pg: dict) -> str:
    """K: статья заказчика, фото, видео и контакты — стоматология, лечение."""
    h1, article = render_md(pg["content"])

    shots = ""
    for i, name in enumerate(pg["imgs"]):
        img = picture(name, f"{h1}, фотография {i + 1}", "", w=1600, h=1067)
        # пустое место под фото показываем только в превью: на боевом домене
        # посетитель не должен видеть «[ФОТОГРАФИЯ — пришлёт заказчик]»
        if img:
            shots += f'        <div class="gallery__item">{img}</div>\n'
        elif not SPLIT:
            shots += (f'        <div class="gallery__item gallery__item--empty">'
                      f'<span>[ФОТОГРАФИЯ {i + 1} — пришлёт заказчик]</span></div>\n')

    # embed-id Дзен отдаёт в <meta name="twitter:player:stream"> страницы ролика
    vids = "\n".join(vcard(*v) for v in pg["videos"])
    video_block = f"""
  <section class="section" id="video">
    <div class="wrap">
      <div class="section__head"><h2>Видео</h2></div>
      <div class="videos">
{vids}
      </div>
    </div>
  </section>
""" if vids else ""
    gallery_block = f"""
  <section class="section">
    <div class="wrap">
      <div class="gallery">
{shots}      </div>
    </div>
  </section>
""" if shots else ""

    key = pg.get("key") or ("stoma" if pg["slug"].startswith("stoma") else "lech")
    return (head(pg["title"], pg["desc"], canonical=canon(key, pg.get("path", "")),
                 noindex=pg.get("draft", False)) + header() + f"""
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

{video_block}{gallery_block}
  <section class="section">
    <div class="wrap">
      <div class="notice">
        <b>Важно!</b>
        <p><strong>Имеются противопоказания. Необходима консультация специалиста.</strong></p>
        <p>ДАЛЬТУР организует поездку: проезд, трансфер, проживание
        и сопровождение. Медицинскую деятельность компания не осуществляет —
        диагностику и лечение проводят медицинские организации Китая.</p>
        <p>Информация на сайте носит ознакомительный характер и не является
        медицинской консультацией, постановкой диагноза или назначением
        лечения. Решение о лечении и процедурах принимает врач после
        консультации и обследования. Стоимость, сроки и программу лечения
        определяет клиника.</p>
        <p>Перед поездкой рекомендуем проконсультироваться с лечащим врачом.</p>
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
        dep = DEPARTURES[DEP]
        if i == 1:
            title = f"{dep['route_there']} — {CITY['name']}"
            body = (f"[ВЫЕЗД из {dep['from']}, пункт пропуска, прибытие в "
                    f"{CITY['name_pre']}, размещение в отеле. Текст пришлёт заказчик.]")
        elif i == d:
            title = f"{CITY['name']} — {dep['route_back']}"
            body = (f"[ОСВОБОЖДЕНИЕ НОМЕРОВ, выезд, прибытие {dep['to_acc']}. "
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
      <div class="section__head"><h2>Программа тура в {CITY['name']}</h2></div>
      <div class="days">
{chr(10).join(days)}
      </div>
    </div>
  </section>
"""
        # C6: после программы — телефон и мессенджеры
        + contacts("Остались вопросы? Рады вас проконсультировать",
                   "Ответим в рабочее время: ПН–ПТ 10:00–18:00.",
                   wa_text)
        + f"""
  <section class="section" id="video">
    <div class="wrap">
      <div class="section__head"><h2>Экскурсии на видео</h2></div>
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
      <div class="section__head"><h2>Туры в {CITY['name']} на</h2></div>
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


def set_departure(key: str) -> None:
    """Переключить город отправления: заголовки, программа, адреса туров."""
    global DEP
    DEP = key
    dep = DEPARTURES[key]
    CITY["from"], CITY["from_gen"] = dep["from"], dep["from_gen"]
    HOSTS["main"] = dep["host"]


def build_dist() -> list:
    """Отдельный корень под каждый домен: у каждого свой CNAME."""
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

    # сайты туров — по городу отправления; разделы — общие для всех
    plan = [(k, None, None) for k in DEPARTURES] + [
        ("stoma", HOSTS["stoma"], PAGES[0]),
        ("lech", HOSTS["lech"], PAGES[1]),
    ]

    for key, host, pg in plan:
        if key in DEPARTURES:
            set_departure(key)
            host = HOSTS["main"]
        else:
            set_departure("main")
        root = os.path.join(DIST, key)
        os.makedirs(root, exist_ok=True)
        clean(root)
        shutil.copytree(os.path.join(HERE, "assets"), os.path.join(root, "assets"))

        with open(os.path.join(root, "CNAME"), "w", encoding="utf-8") as fh:
            fh.write(host + "\n")

        if key in DEPARTURES:
            with open(os.path.join(root, "index.html"), "w", encoding="utf-8") as fh:
                fh.write(build_index())
            for d, n in TOURS:
                with open(os.path.join(root, slug(d)), "w", encoding="utf-8") as fh:
                    fh.write(build_tour(d, n))
            out.append(f"dist/{key}/ — {host}, {len(TOURS) + 1} страниц")
        else:
            with open(os.path.join(root, "index.html"), "w", encoding="utf-8") as fh:
                fh.write(build_page(pg))
            extra = [p for p in PAGES if p.get("key") == key and p.get("path")]
            for p in extra:
                with open(os.path.join(root, p["path"]), "w", encoding="utf-8") as fh:
                    fh.write(build_page(p))
            out.append(f"dist/{key}/ — {host}, {1 + len(extra)} стр.")

        # GitHub Pages иначе прогонит файлы через Jekyll
        open(os.path.join(root, ".nojekyll"), "w").close()

        # sitemap и robots — чтобы поисковики сразу нашли все страницы.
        # Host: не пишем: Яндекс отказался от директивы в 2018, главное зеркало
        # теперь определяется по canonical и редиректам.
        urls = ([] if DEPARTURES[DEP]["draft"] and key in DEPARTURES else
                [canon("main")] + [canon("main", slug(d)) for d, _ in TOURS]
                if key in DEPARTURES else
                [canon(key)] + [canon(key, p["path"]) for p in PAGES
                                if p.get("key") == key and p.get("path") and not p.get("draft")])
        today = __import__("datetime").date.today().isoformat()
        sm = "".join(f"  <url><loc>{u}</loc><lastmod>{today}</lastmod></url>\n" for u in urls)
        with open(os.path.join(root, "sitemap.xml"), "w", encoding="utf-8") as fh:
            fh.write('<?xml version="1.0" encoding="UTF-8"?>\n'
                     '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                     f"{sm}</urlset>\n")
        with open(os.path.join(root, "robots.txt"), "w", encoding="utf-8") as fh:
            fh.write(f"User-agent: *\nAllow: /\n\nSitemap: https://{host}/sitemap.xml\n")

    set_departure("main")
    out.append(build_mirror())
    for key in OLD_HOSTS:
        out.append(build_old_redirect(key))
    return out


def redirect_page(target: str) -> str:
    """Страница зеркала: сразу уводит на тот же адрес основного домена.
    301 GitHub Pages не умеет; мгновенный meta refresh Яндекс и Google
    считают перенаправлением, canonical подтверждает главное зеркало."""
    return f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<title>ДАЛЬТУР — туры в Хуньчунь</title>
<link rel="canonical" href="{target}">
<meta http-equiv="refresh" content="0; url={target}">
<script>location.replace("{target}" + location.search + location.hash)</script>
</head>
<body><p><a href="{target}">{target}</a></p></body>
</html>
"""


def build_mirror() -> str:
    """хуньчунь-хуньчунь.рф → hunchun-hunchun.ru, каждая страница на свою."""
    root = os.path.join(DIST, "rf")
    os.makedirs(root, exist_ok=True)
    for name in os.listdir(root):
        if name != ".git":
            path = os.path.join(root, name)
            shutil.rmtree(path) if os.path.isdir(path) else os.remove(path)
    pages = [("index.html", canon("main"))] + [(slug(d), canon("main", slug(d))) for d, _ in TOURS]
    for name, target in pages:
        with open(os.path.join(root, name), "w", encoding="utf-8") as fh:
            fh.write(redirect_page(target))
    # Любой другой адрес — на тот же путь основного домена
    main_root = f"https://{HOSTS['main']}"
    with open(os.path.join(root, "404.html"), "w", encoding="utf-8") as fh:
        fh.write(redirect_page(main_root + "/").replace(
            f'location.replace("{main_root}/" + location.search + location.hash)',
            f'location.replace("{main_root}" + location.pathname + location.search + location.hash)'))
    with open(os.path.join(root, "CNAME"), "w", encoding="utf-8") as fh:
        fh.write(MIRROR + "\n")
    open(os.path.join(root, ".nojekyll"), "w").close()
    # Без Sitemap: в карте зеркала не может быть адресов чужого домена
    with open(os.path.join(root, "robots.txt"), "w", encoding="utf-8") as fh:
        fh.write("User-agent: *\nAllow: /\n")
    return f"dist/rf/ — {MIRROR} → {HOSTS['main']}, {len(pages)} страниц-редиректов"


def build_old_redirect(key: str) -> str:
    """dental. → stomatologiya., clinic. → lechenie-v-kitae.: старые адреса
    разделов уводят на новые, тем же способом, что и зеркало .рф."""
    root = os.path.join(DIST, f"old-{key}")
    os.makedirs(root, exist_ok=True)
    for name in os.listdir(root):
        if name != ".git":
            path = os.path.join(root, name)
            shutil.rmtree(path) if os.path.isdir(path) else os.remove(path)
    target = canon(key)
    with open(os.path.join(root, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(redirect_page(target))
    # была страница-заготовка clinic./lechenie-v-kitae.html — туда же
    with open(os.path.join(root, "404.html"), "w", encoding="utf-8") as fh:
        fh.write(redirect_page(target))
    with open(os.path.join(root, "CNAME"), "w", encoding="utf-8") as fh:
        fh.write(OLD_HOSTS[key] + "\n")
    open(os.path.join(root, ".nojekyll"), "w").close()
    with open(os.path.join(root, "robots.txt"), "w", encoding="utf-8") as fh:
        fh.write("User-agent: *\nAllow: /\n")
    return f"dist/old-{key}/ — {OLD_HOSTS[key]} → {HOSTS[key]}"


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
