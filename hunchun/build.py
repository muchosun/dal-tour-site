#!/usr/bin/env python3
"""Генератор лендинга «Туры в Хуньчунь».

Собирает index.html и по странице на каждую длительность тура.
Запуск:  python3 build.py
Тот же скрипт переиспользуется под Яньцзи — менять только блок CITY.
"""
import os
from urllib.parse import quote

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- город

CITY = {
    "name": "Хуньчунь",
    "name_pre": "Хуньчуне",       # предложный падеж
    "hiero": "珲春",
    "from": "Владивостока",
    "lead": "Ближайший к Владивостоку город Китая. Выезд автобусом, "
            "выезды ежедневно. Туры от 2 до 10 дней.",
}

# длительности: (дней, ночей)
TOURS = [(n, n - 1) for n in range(2, 11)]

# ---------------------------------------------------------------- контакты

PHONE_MAIN_HUMAN = "+7 (964) 44-44-144"
PHONE_MAIN_TEL = "+79644444144"
PHONES_EXTRA = [("+7 (423) 248-48-92", "+74232484892"),
                ("+7 (423) 248-48-91", "+74232484891")]
WA_NUMBER = "79644444144"
TG_LINK = "https://t.me/daltour"          # [УТОЧНИТЬ] реальная ссылка
SOCIALS = [("VK", "https://vk.com/daltour"),
           ("YouTube", "https://youtube.com/daltour"),
           ("Дзен", "https://dzen.ru/daltour")]
ADDRESS = "690091, Россия, г. Владивосток,<br>ул. Мордовцева 3, офис 705"
HOURS = "ПН–ПТ 10:00–18:00, СБ–ВС выходной"

FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'"
           "%3E%3Crect width='32' height='32' rx='7' fill='%23CE2B22'/%3E%3Ctext x='16' y='22'"
           " font-family='sans-serif' font-size='17' font-weight='700' fill='white'"
           " text-anchor='middle'%3E%D0%94%3C/text%3E%3C/svg%3E")


IMG_DIR = os.path.join(HERE, "assets", "img")


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
    return (f'<picture class="{cls}">{webp}'
            f'<img src="assets/img/{name}.jpg" alt="{alt}" {loading} decoding="async"'
            f' width="{w}" height="{h}"></picture>')


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


# ---------------------------------------------------------------- куски страниц

def head(title: str, desc: str, base: str = "", sticky: bool = False) -> str:
    return f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#FBF9F5">
<meta property="og:type" content="website">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:locale" content="ru_RU">
<link rel="icon" href="{FAVICON}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Golos+Text:wght@400;500;600;700&family=Unbounded:wght@600;700&display=swap">
<link rel="stylesheet" href="{base}assets/css/main.css">
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

    <div class="header__center"><a class="logo" href="{base}index.html">ДАЛЬТУР</a></div>

    <nav class="header__nav" aria-label="Основная навигация">
      <a href="{base}index.html#tury">Все туры</a>
      <a href="{base}index.html#o-gorode">О городе</a>
      <a href="{base}index.html#kontakty">Контакты</a>
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
    <a href="{base}index.html">Главная</a>
    <a href="{base}index.html#tury">Все туры</a>
    <a href="{base}index.html#o-gorode">О городе</a>
    <a href="{base}index.html#kontakty">Контакты</a>
    <a class="drawer__phone" href="tel:{PHONE_MAIN_TEL}">{PHONE_MAIN_HUMAN}</a>
    <a href="{TG_LINK}">Telegram</a>
  </nav>
</div>
"""


def footer(base: str = "", tail: str = "") -> str:
    tours_links = "\n".join(
        f'          <li><a href="{base}{slug(d)}">{label(d, n)}</a></li>'
        for d, n in TOURS)
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
      Стоимость тура зависит от дат выезда и категории отеля — уточняйте у менеджера по телефону
      {PHONE_MAIN_HUMAN} или в WhatsApp.
      <br>© <span data-year>2026</span> ДАЛЬТУР.
    </p>
  </div>
</footer>
{tail}
<script src="{base}assets/js/main.js"></script>
</body>
</html>
"""


# ---------------------------------------------------------------- главная

def build_index() -> str:
    cards = []
    for d, n in TOURS:
        cards.append(f"""        <a class="duration" href="{slug(d)}">
          <span class="duration__n">
            <span class="duration__days">{d} {days_word(d)}</span>
            <span class="duration__nights">{n} {nights_word(n)}</span>
          </span>
          <span class="duration__go">Программа {IC_ARROW}</span>
        </a>""")

    wa_href = wa(f"Здравствуйте! Подскажите по турам в {CITY['name']}.")

    shot = picture("hero", f"Автобус на отправлении в {CITY['name']} из {CITY['from'][:-1]}а",
                   "hero__shot", eager=True)
    hero_art = ("" if shot else
                f'<div class="hero__art">'
                f'<b lang="zh" style="font-family:var(--display);font-size:44px;'
                f'color:#CDBFAC;line-height:1">{CITY["hiero"]}</b>'
                f'<span>Здесь будет фотография города</span></div>')
    hero_band = f'<div class="wrap"><div class="hero__band">{shot}</div></div>' if shot else ""

    return (head(
        f"Туры в {CITY['name']} из {CITY['from']} — ДАЛЬТУР",
        f"Туры в {CITY['name']} из {CITY['from']} от 2 до 10 дней. Программа по дням, "
        f"выезды ежедневно. Звоните {PHONE_MAIN_HUMAN} или пишите в WhatsApp.")
        + header() + f"""
<main id="main">

  <section class="hero">
    <div class="wrap hero__grid{' hero__grid--solo' if not hero_art else ''}">
      <div class="hero__col">
        <span class="hero__eyebrow">ТУРОПЕРАТОР ДАЛЬТУР · {CITY['from'].upper()}</span>
        <h1>Туры в {CITY['name']} <br class="br-desktop">из {CITY['from']}</h1>
        <p class="hero__lead">{CITY['lead']}</p>

        <div class="hero__actions">
          <a class="btn btn--primary" href="tel:{PHONE_MAIN_TEL}">{IC_PHONE} {PHONE_MAIN_HUMAN}</a>
          <a class="btn btn--ghost" href="{wa_href}" target="_blank" rel="noopener">{IC_WA} Написать в WhatsApp</a>
        </div>

        <div class="hero__facts">
          <span class="hero__fact">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none" aria-hidden="true"><circle cx="10" cy="10" r="7.5" stroke="#A7211A" stroke-width="1.4"/><path d="M10 6v4.3l2.8 1.7" stroke="#A7211A" stroke-width="1.4" stroke-linecap="round"/></svg>
            <span>Выезды ежедневно</span>
          </span>
          <span class="hero__fact">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none" aria-hidden="true"><circle cx="10" cy="7" r="3" stroke="#A7211A" stroke-width="1.4"/><path d="M4 17c0-3.3 2.7-5 6-5s6 1.7 6 5" stroke="#A7211A" stroke-width="1.4" stroke-linecap="round"/></svg>
            <span>Гиды-переводчики в Китае</span>
          </span>
          <span class="hero__fact">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none" aria-hidden="true"><path d="M10 18s6-5.4 6-9.4a6 6 0 1 0-12 0c0 4 6 9.4 6 9.4z" stroke="#A7211A" stroke-width="1.4" stroke-linejoin="round"/><circle cx="10" cy="8.4" r="2.1" stroke="#A7211A" stroke-width="1.4"/></svg>
            <span>Офис во {CITY['from'][:-1]}е</span>
          </span>
        </div>
      </div>

      {hero_art}
    </div>
    {hero_band}
  </section>

  <section class="section" id="tury">
    <div class="wrap">
      <div class="section__head">
        <h2>Выберите длительность</h2>
        <span class="section__note">от 2 до 10 дней · программа по дням внутри</span>
      </div>

      <div class="durations">
{chr(10).join(cards)}
      </div>
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

  <section class="section">
    <div class="wrap">
      <div class="cta">
        <div>
          <b>Цену уточняйте у менеджера</b>
          <span>Стоимость зависит от дат выезда и категории отеля — в праздники дороже. Позвоните или напишите, посчитаем на ваши даты.</span>
        </div>
        <div class="cta__actions">
          <a class="btn btn--ghost" href="tel:{PHONE_MAIN_TEL}">{PHONE_MAIN_HUMAN}</a>
          <a class="btn btn--primary" href="{wa_href}" target="_blank" rel="noopener">Написать в WhatsApp</a>
        </div>
      </div>
    </div>
  </section>

</main>
""" + footer())


# ---------------------------------------------------------------- страница тура

def build_tour(d: int, n: int) -> str:
    lbl = label(d, n)
    wa_href = wa(f"Здравствуйте! Интересует тур в {CITY['name']} на {lbl}. "
                 f"Подскажите ближайшие даты и стоимость.")

    shot = picture("tour", f"{CITY['name']}, фотография из тура", "", w=1600, h=900)
    tour_band = f'<div class="wrap"><div class="tour__band">{shot}</div></div>' if shot else ""

    # программа по дням: каркас, тексты заказчик присылает отдельно
    days = []
    for i in range(1, d + 1):
        if i == 1:
            title = f"{CITY['from'][:-1]} — {CITY['name']}"
            body = ("[ДЕНЬ 1 — выезд из Владивостока, пункт пропуска, прибытие в "
                    f"{CITY['name_pre']}, размещение в отеле. Текст пришлёт заказчик.]")
        elif i == d:
            title = f"{CITY['name']} — {CITY['from'][:-1]}"
            body = ("[ПОСЛЕДНИЙ ДЕНЬ — освобождение номеров, выезд, прибытие во "
                    "Владивосток. Текст пришлёт заказчик.]")
        else:
            title = CITY["name"]
            body = f"[ДЕНЬ {i} — программа и экскурсии. Текст пришлёт заказчик.]"
        days.append(f"""        <article class="day">
          <div class="day__head">
            <span class="day__num" aria-hidden="true">{i}</span>
            <h3 class="day__title">{title}</h3>
          </div>
          <p>{body}</p>
        </article>""")

    # перелинковка на остальные длительности
    others = "\n".join(
        f'        <a class="pill" href="{slug(od)}">{label(od, on)}</a>'
        for od, on in TOURS if od != d)

    # блоки под видео
    videos = "\n".join(f"""        <div class="video">
          <div class="video__frame">
            <b>[ВИДЕО ЭКСКУРСИИ {v}]</b>
            <span>Плеер Яндекс.Видео — вставить iframe, когда заказчик пришлёт ссылку</span>
          </div>
          <div class="video__cap">[НАЗВАНИЕ ЭКСКУРСИИ {v}]</div>
        </div>""" for v in (1, 2))

    return (head(
        f"Тур в {CITY['name']} {lbl} из {CITY['from']} — ДАЛЬТУР",
        f"Тур в {CITY['name']} на {lbl} из {CITY['from']}: программа по дням, "
        f"выезды ежедневно. Стоимость уточняйте по телефону {PHONE_MAIN_HUMAN}.",
        sticky=True)
        + header() + f"""
<main id="main">

  <section class="tour-head">
    <div class="wrap">
      <nav class="crumbs" aria-label="Хлебные крошки">
        <a href="index.html">Туры в {CITY['name']}</a><span aria-hidden="true">/</span>
        <span aria-current="page">{lbl}</span>
      </nav>

      <div class="tour-head__row">
        <h1>Тур в {CITY['name']}<br>{lbl}</h1>
        <span class="tour-head__hiero" lang="zh" aria-hidden="true">{CITY['hiero']}</span>
      </div>

      <div class="tour-head__tags">
        <span class="tag tag--jade">АВТОБУС</span>
        <span class="tag tag--sand">ВЫЕЗДЫ ЕЖЕДНЕВНО</span>
      </div>

      <dl class="facts">
        <div class="fact"><dt>Длительность</dt><dd>{lbl}</dd></div>
        <div class="fact"><dt>Отправление</dt><dd>[ВРЕМЯ ВЫЕЗДА]</dd></div>
        <div class="fact"><dt>Дорога</dt><dd>[АВТОБУС, ~N ЧАСОВ]</dd></div>
        <div class="fact"><dt>Питание</dt><dd>[ЗАВТРАКИ?]</dd></div>
      </dl>

      <div class="askprice">
        <span>
          <b>Цена зависит от дат выезда</b>
          <p>В праздники и высокий сезон стоимость выше. Напишите или позвоните — посчитаем на ваши даты и категорию отеля.</p>
        </span>
        <span class="askprice__actions">
          <a class="btn btn--ghost btn--sm" href="tel:{PHONE_MAIN_TEL}">{IC_PHONE} Позвонить</a>
          <a class="btn btn--primary btn--sm" href="{wa_href}" target="_blank" rel="noopener">{IC_WA} WhatsApp</a>
        </span>
      </div>
    </div>
  </section>

  {tour_band}
  <section class="section" id="programma">
    <div class="wrap">
      <div class="section__head"><h2>Программа по дням</h2></div>
      <div class="days">
{chr(10).join(days)}
      </div>
    </div>
  </section>

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
  <a class="btn btn--primary" href="{wa_href}" target="_blank" rel="noopener">Написать в WhatsApp</a>
</div>
"""))


def main() -> None:
    written = []

    with open(os.path.join(HERE, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(build_index())
    written.append("index.html")

    for d, n in TOURS:
        page = build_tour(d, n)
        with open(os.path.join(HERE, slug(d)), "w", encoding="utf-8") as fh:
            fh.write(page)
        written.append(slug(d))

    print("собрано:")
    for w in written:
        print("  ", w)


if __name__ == "__main__":
    main()
