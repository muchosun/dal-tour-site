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
           "draft": False},   # 30.09: все 10 туров и SEO-статья от заказчика
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
# Третье поле — ключ иконки в BRAND.
SOCIALS = [("YouTube", "https://www.youtube.com/@DALTOUR", "youtube"),
           ("Дзен", "https://dzen.ru/daltour", "zen"),
           ("Rutube", "https://rutube.ru/channel/54520250/", "rutube"),
           ("VK", "https://vk.ru/daltourvk", "vk"),   # ссылку дал Александр 30.09
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

# Иконки сервисов — сплошные, одним цветом (выбор 30.09). YouTube, VK,
# Telegram, WhatsApp — Simple Icons (simpleicons.org, CC0). Rutube и Дзен
# в открытых наборах залитыми нет: Rutube — официальный знак с rutube.ru
# в один цвет, Дзен — его звезда. Цвет — currentColor.
BRAND = {
    'youtube': ('0 0 24 24',
              'M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z'),
    'zen': ('2 2 44 44',   # звезда тоньше соседей — чуть крупнее
              'M24 3.5C24 18.457 29.653 24 44.5 24C29.568 24 24 29.657 24 44.5C24 29.59 18.457 24 3.5 24C18.457 24 24 18.373 24 3.5Z'),
    'rutube': ('0 0 132 132',
              'M32 0h68a32 32 0 0 1 32 32v68a32 32 0 0 1-32 32H32A32 32 0 0 1 0 100V32A32 32 0 0 1 32 0z M81.536 62.987H42.54V47.555h38.997c2.278 0 3.862.397 4.657 1.09s1.287 1.98 1.287 3.858v5.541c0 1.98-.492 3.265-1.287 3.959-.795.693-2.379.99-4.657.99zm2.675-29.981H26V99h16.539V77.53h30.479L87.48 99H106L90.055 77.429c5.878-.871 8.518-2.673 10.695-5.642s3.269-7.716 3.269-14.051v-4.948c0-3.758-.398-6.727-1.092-9.002s-1.88-4.255-3.565-6.033c-1.78-1.683-3.76-2.868-6.14-3.663-2.378-.693-5.35-1.09-9.01-1.09z'),
    'vk': ('0 0 24 24',
              'm9.489.004.729-.003h3.564l.73.003.914.01.433.007.418.011.403.014.388.016.374.021.36.025.345.03.333.033c1.74.196 2.933.616 3.833 1.516.9.9 1.32 2.092 1.516 3.833l.034.333.029.346.025.36.02.373.025.588.012.41.013.644.009.915.004.98-.001 3.313-.003.73-.01.914-.007.433-.011.418-.014.403-.016.388-.021.374-.025.36-.03.345-.033.333c-.196 1.74-.616 2.933-1.516 3.833-.9.9-2.092 1.32-3.833 1.516l-.333.034-.346.029-.36.025-.373.02-.588.025-.41.012-.644.013-.915.009-.98.004-3.313-.001-.73-.003-.914-.01-.433-.007-.418-.011-.403-.014-.388-.016-.374-.021-.36-.025-.345-.03-.333-.033c-1.74-.196-2.933-.616-3.833-1.516-.9-.9-1.32-2.092-1.516-3.833l-.034-.333-.029-.346-.025-.36-.02-.373-.025-.588-.012-.41-.013-.644-.009-.915-.004-.98.001-3.313.003-.73.01-.914.007-.433.011-.418.014-.403.016-.388.021-.374.025-.36.03-.345.033-.333c.196-1.74.616-2.933 1.516-3.833.9-.9 2.092-1.32 3.833-1.516l.333-.034.346-.029.36-.025.373-.02.588-.025.41-.012.644-.013.915-.009ZM6.79 7.3H4.05c.13 6.24 3.25 9.99 8.72 9.99h.31v-3.57c2.01.2 3.53 1.67 4.14 3.57h2.84c-.78-2.84-2.83-4.41-4.11-5.01 1.28-.74 3.08-2.54 3.51-4.98h-2.58c-.56 1.98-2.22 3.78-3.8 3.95V7.3H10.5v6.92c-1.6-.4-3.62-2.34-3.71-6.92Z'),
    'telegram': ('0 0 24 24',
              'M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z'),
    'whatsapp': ('0 0 24 24',
              'M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z'),
}


def brand_icon(key: str, size: int = 18, stroke: float = 0) -> str:
    vb, d = BRAND[key]
    return (f'<svg width="{size}" height="{size}" viewBox="{vb}" aria-hidden="true">'
            f'<path fill="currentColor" fill-rule="evenodd" d="{d}"/></svg>')

IC_WA = brand_icon("whatsapp")
IC_TG = brand_icon("telegram")
# трубка — залитая, в пару к логотипам WhatsApp и Telegram (Material Design Icons, Apache 2.0)
IC_PHONE = ('<svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true">'
            '<path fill="currentColor" d="M6.62 10.79c1.44 2.83 3.76 5.15 6.59 6.59l2.2-2.2c.28-.28.67-.36 '
            '1.02-.25c1.12.37 2.32.57 3.57.57a1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 '
            '1 0 0 1 1 1c0 1.25.2 2.45.57 3.57c.11.35.03.74-.25 1.02z"/></svg>')
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
          <span class="duration__go">Программа тура {IC_ARROW}</span>
        </a>""" for d, n in TOURS)

    first, last = TOURS[0][0], TOURS[-1][0]

    # SEO-статья под город отправления (633955): content/city/<город>.md,
    # Title и Description — content/city/<город>.meta.json. Нет статьи —
    # общий блок «О городе».
    city_md = os.path.join(HERE, "content", "city", f"{DEP}.md")
    city_meta = os.path.join(HERE, "content", "city", f"{DEP}.meta.json")
    meta = __import__("json").load(open(city_meta, encoding="utf-8")) if os.path.exists(city_meta) else {}
    if os.path.exists(city_md):
        _, art = render_md(os.path.join("city", f"{DEP}.md"))
        city_block = f"""
  <section class="section" id="o-gorode">
    <div class="wrap">
      <div class="prose prose--city">
        {art}
      </div>
    </div>
  </section>
"""
    else:
        city_block = f"""
  <section class="section" id="o-gorode">
    <div class="wrap">
      <div class="section__head"><h2>{render_md("o-gorode.md")[0] or "О городе"}</h2></div>
      <div class="prose" style="margin-top:14px">
        {render_md("o-gorode.md")[1]}
      </div>
    </div>
  </section>
"""

    return (head(
        meta.get("title") or f"Туры в {CITY['name']} из {CITY['from']} — ДАЛЬТУР",
        meta.get("desc") or
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

{city_block}"""
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
        elif b.startswith("### "):
            parts.append(f"<h3>{esc(b[4:].strip())}</h3>")
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
        и сопровождение. Лечение в стоимость тура не входит. Медицинскую
        деятельность компания не осуществляет — диагностику и лечение
        проводят медицинские организации Китая.</p>
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


# ---------------------------------------------------------------- тексты туров

# Тексты туров от заказчика лежат как есть: content/tours/<город>/<дней>.txt
# (город — ключ DEPARTURES). Формат — как он присылает в Telegram:
# вступление, «Программа тура…», «N день — …», экскурсии «… — примерно N
# юаней», заключение. Контактные строки (☎️, «Звонки + WhatsApp») пропускаем —
# на странице свои блоки контактов.
DAY_RE = re.compile(r"^(\d+) день — (.+)$")
PRICE_RE = re.compile(r"^(.+?) — (примерно .+)$")
SKIP = ("ДАЛЬТУР", "☎️", "Звонки + WhatsApp")
# 633938: «дополнительные экскурсии — во множественном числе»
PLURAL = [("другую дополнительную экскурсионную программу", "другие дополнительные экскурсионные программы"),
          ("дополнительную экскурсионную программу", "дополнительные экскурсионные программы"),
          ("дополнительную экскурсию", "дополнительные экскурсии")]


def tour_text(d: int) -> dict | None:
    path = os.path.join(HERE, "content", "tours", DEP, f"{d}.txt")
    if not os.path.exists(path):
        return None
    raw = pathlib.Path(path).read_text(encoding="utf-8")
    for one, many in PLURAL:
        raw = raw.replace(one, many)
    lines = [l.strip() for l in raw.splitlines() if l.strip()]
    t = {"intro_h": "", "intro": [], "days": [], "exc_h": "", "exc_intro": [],
         "exc": [], "exc_note": "", "outro_h": "", "outro": []}
    part = "title"
    for l in lines:
        if l.startswith(SKIP) and not l.startswith("ДАЛЬТУР —") and part != "days":
            continue
        if l.startswith("ДАЛЬТУР —"):          # подпись в конце
            continue
        if part == "title":
            part = "intro_h0"; continue
        if part == "intro_h0":
            t["intro_h"] = l; part = "intro"; continue
        if l.startswith("Программа тура"):
            part = "days"; continue
        m = DAY_RE.match(l)
        if m and part in ("days",):
            t["days"].append([m.group(2), []]); continue
        if l.startswith("Экскурсии за дополнительную плату"):
            t["exc_h"] = l; part = "exc"; continue
        if part == "exc" and l.startswith("Важно:"):
            t["exc_note"] = l; part = "outro_h0"; continue
        if part == "outro_h0":
            t["outro_h"] = l; part = "outro"; continue
        if part == "intro":
            t["intro"].append(l)
        elif part == "days" and t["days"]:
            t["days"][-1][1].append(l)
        elif part == "exc":
            pm = PRICE_RE.match(l)
            (t["exc"].append((pm.group(1), pm.group(2))) if pm else t["exc_intro"].append(l))
        elif part == "outro":
            t["outro"].append(l)
    if len(t["days"]) != d:
        raise SystemExit(f"{path}: дней в тексте {len(t['days'])}, а в туре {d}")
    return t


def build_tour(d: int, n: int) -> str:
    lbl = label(d, n)
    wa_text = (f"Здравствуйте! Интересует тур в {CITY['name']} на {lbl}. "
               f"Подскажите ближайшие даты и стоимость.")

    text = tour_text(d)

    # G1, G2: «Первый день» вместо цифры
    days = []
    for i in range(1, d + 1):
        dep = DEPARTURES[DEP]
        if text:
            title, rows = text["days"][i - 1]
            title = title[:1].upper() + title[1:]
            body = "\n          ".join(
                f'<p class="day__note">{esc(r)}</p>' if r.startswith("Экскурсии и шопинг")
                else f"<p>{esc(r)}</p>" for r in rows)
            days.append(f"""        <article class="day">
          <div class="day__head">
            <span class="day__ord">{ORDINALS[i]} день</span>
            <h3 class="day__title">{esc(title)}</h3>
          </div>
          {body}
        </article>""")
            continue
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

    intro_block = exc_block = outro_block = ""
    if text:
        intro_block = f"""
  <section class="section section--tight">
    <div class="wrap">
      <div class="prose">
        <h2>{esc(text["intro_h"])}</h2>
        {"".join(f"<p>{esc(p)}</p>" for p in text["intro"])}
      </div>
    </div>
  </section>
"""
        items = "\n".join(
            f'          <li><span>{esc(name)}</span><b>{esc(price)}</b></li>'
            for name, price in text["exc"])
        exc_block = f"""
  <section class="section" id="ekskursii">
    <div class="wrap">
      <div class="section__head"><h2>{esc(text["exc_h"])}</h2></div>
      {"".join(f'<p class="section__lead">{esc(p)}</p>' for p in text["exc_intro"])}
      <ul class="excursions">
{items}
      </ul>
      <p class="excursions__note">{esc(text["exc_note"])}</p>
    </div>
  </section>
"""
        outro_block = f"""
  <section class="section">
    <div class="wrap">
      <div class="prose">
        <h2>{esc(text["outro_h"])}</h2>
        {"".join(f"<p>{esc(p)}</p>" for p in text["outro"])}
      </div>
    </div>
  </section>
"""

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
        <h1>Тур в {CITY['name']} из {CITY['from']}<br>{lbl}</h1>
        <span class="tour-head__hiero" lang="zh" aria-hidden="true">{CITY['hiero']}</span>
      </div>

      <!-- F6: тег транспорта оставляем, заказчику понравился -->
      <div class="tour-head__tags">
        <span class="tag tag--jade">{TRANSPORT}</span>
        <span class="tag tag--sand">ВЫЕЗДЫ ЕЖЕДНЕВНО</span>
      </div>

      <!-- F1, F2: без «Дороги» и «Времени выезда». F3: только длительность и питание. -->
      <dl class="facts facts--three">
        <div class="fact"><dt>Длительность</dt><dd>{lbl}</dd></div>
        <div class="fact"><dt>Питание</dt><dd>Завтраки</dd></div>
        <div class="fact fact--gift"><dt>Экскурсии в подарок</dt><dd>Чайная церемония и<br>кулинарное шоу</dd></div>
      </dl>
    </div>
  </section>
{intro_block}
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
                   # 633931: «мы всегда отвечаем, если не спим» — без режима работы
                   "Звоните или пишите в WhatsApp и Telegram.",
                   wa_text)
        + exc_block + f"""
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
        + outro_block + f"""
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
    out.append(build_www())
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


def build_www() -> str:
    """www.hunchun-hunchun.ru — отдельный репозиторий с перенаправлением на
    корень. GitHub завис на выпуске общего сертификата «корень + www»
    (статус dns_changed с 28.09); у отдельного адреса сертификат свой."""
    root = os.path.join(DIST, "www")
    os.makedirs(root, exist_ok=True)
    for name in os.listdir(root):
        if name != ".git":
            path = os.path.join(root, name)
            shutil.rmtree(path) if os.path.isdir(path) else os.remove(path)
    main_root = f"https://{HOSTS['main']}"
    pages = [("index.html", canon("main"))] + [(slug(d), canon("main", slug(d))) for d, _ in TOURS]
    for name, target in pages:
        with open(os.path.join(root, name), "w", encoding="utf-8") as fh:
            fh.write(redirect_page(target))
    with open(os.path.join(root, "404.html"), "w", encoding="utf-8") as fh:
        fh.write(redirect_page(main_root + "/").replace(
            f'location.replace("{main_root}/" + location.search + location.hash)',
            f'location.replace("{main_root}" + location.pathname + location.search + location.hash)'))
    with open(os.path.join(root, "CNAME"), "w", encoding="utf-8") as fh:
        fh.write(f"www.{HOSTS['main']}\n")
    open(os.path.join(root, ".nojekyll"), "w").close()
    with open(os.path.join(root, "robots.txt"), "w", encoding="utf-8") as fh:
        fh.write("User-agent: *\nAllow: /\n")
    return f"dist/www/ — www.{HOSTS['main']} → {HOSTS['main']}"


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
