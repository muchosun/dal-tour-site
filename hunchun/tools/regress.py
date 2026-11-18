#!/usr/bin/env python3
"""Регресс боевых сайтов: обход по внутренним ссылкам, ответы, canonical,
noindex у черновиков, заглушки, файлы, внешние ссылки, sitemap и robots.

    python3 tools/regress.py
"""
import html, random, re, urllib.error, urllib.request

SITES = {   # хост → черновик (должен быть noindex)
    "hunchun-hunchun.ru": False,
    "stomatologiya.hunchun-hunchun.ru": False,
    "lechenie-v-kitae.hunchun-hunchun.ru": False,
    "ussuriysk.hunchun-hunchun.ru": False,
    "habarovsk.hunchun-hunchun.ru": False,
    "yanji-yanji.ru": False,
    "ussuriysk.yanji-yanji.ru": False,
    "habarovsk.yanji-yanji.ru": False,
}
# зеркала: каждая страница — мгновенный редирект на ту же страницу основного сайта
MIRRORS = {
    "xn----ytbaba5abcbmfug6dded.xn--p1ai": "hunchun-hunchun.ru",   # хуньчунь-хуньчунь.рф
    "xn----mtbbcczd2ee8cf2ag.xn--p1ai": "yanji-yanji.ru",          # яньцзи-яньцзи.рф
    "xn----mtbbvc5cd1be5af.xn--p1ai": "yanji-yanji.ru",            # янцзы-янцзы.рф
    "dental.hunchun-hunchun.ru": "stomatologiya.hunchun-hunchun.ru",
    "clinic.hunchun-hunchun.ru": "lechenie-v-kitae.hunchun-hunchun.ru",
}
PAGES = ["", "tur-3-dnya.html", "tur-4-dnya.html"] + [f"tur-{d}-dney.html" for d in range(5, 11)]
UA = {"User-Agent": "Mozilla/5.0 (regress)"}
SKIP_EXT = ("dental.",)          # у разработчика провайдер режет «dental» — проверяем снаружи
ASSET = (".css", ".js", ".woff2", ".jpg", ".png", ".svg", ".webp", ".ico")


def fetch(u):
    try:
        req = urllib.request.Request(f"{u}{'&' if '?' in u else '?'}r={random.randint(1, 10**9)}", headers=UA)
        r = urllib.request.urlopen(req, timeout=20)
        return r.status, r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:  # noqa: BLE001
        return 0, str(e)


def text(s):
    s = re.sub(r"<(script|style).*?</\1>", "", s, flags=re.S)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s)))


problems, report, seen, ext, assets = [], [], set(), set(), set()
for host, draft in SITES.items():
    todo, pages = [f"https://{host}/"], 0
    while todo:
        base = todo.pop().split("?")[0].split("#")[0]
        if base in seen:
            continue
        seen.add(base)
        st, body = fetch(base)
        pages += 1
        if st != 200:
            problems.append(f"{base} → {st}")
            continue
        t = text(body)
        if not draft:
            for ph in re.findall(r"\[[^\]]{4,90}\]", t):
                problems.append(f"{base}: заглушка «{ph[:60]}»")
            canon = re.findall(r'rel="canonical" href="([^"]*)"', body)
            if not canon or canon[0].rstrip("/") != base.rstrip("/"):
                problems.append(f"{base}: canonical {canon}")
            if "noindex" in body:
                problems.append(f"{base}: noindex на боевом")
        elif "noindex" not in body:
            problems.append(f"{base}: черновик без noindex")
        for tag in ("<title>", 'name="description"', "<h1"):
            if tag not in body:
                problems.append(f"{base}: нет {tag}")
        if re.search(r"https?://(dental|clinic)\.hunchun", body):
            problems.append(f"{base}: ссылка на старый dental./clinic.")
        for href in set(re.findall(r'(?:href|src)="([^"#]+)', body)):
            if href.startswith(("tel:", "mailto:", "data:")):
                continue
            if href.startswith("http"):
                h = re.match(r"https?://([^/]+)", href).group(1)
                (todo if h == host else [ext.add(href)] and []).append(href) if h == host else ext.add(href)
            else:
                full = f"https://{host}/" + href.lstrip("./")
                (assets.add(full.split("?")[0]) if full.split("?")[0].endswith(ASSET) else todo.append(full))
    report.append(f"{host}: {pages} стр.")

for a in sorted(assets):
    if fetch(a)[0] != 200:
        problems.append(f"файл {a}")
ok = 0
for e in sorted(ext):
    if any(s in e for s in SKIP_EXT):
        continue
    st, _ = fetch(e)
    if st in (200, 301, 302, 303, 307, 308):
        ok += 1
    else:
        problems.append(f"ссылка {e} → {st}")
report.append(f"файлов {len(assets)}, внешних и межсайтовых ссылок ок {ok}")
for host, draft in SITES.items():
    st, sm = fetch(f"https://{host}/sitemap.xml")
    locs = re.findall(r"<loc>([^<]+)</loc>", sm)
    bad = [l for l in locs if fetch(l)[0] != 200]
    report.append(f"{host}/sitemap.xml: {st}, адресов {len(locs)}, битых {len(bad)}")
    if draft and locs:
        problems.append(f"{host}: у черновика непустой sitemap")
for mirror, main in MIRRORS.items():
    if any(x in mirror for x in SKIP_EXT):
        continue
    pages = [""] if main.startswith(("stomatologiya.", "lechenie")) else PAGES
    bad = 0
    for pg in pages:
        st, body = fetch(f"https://{mirror}/{pg}")
        target = (re.findall(r'rel="canonical" href="([^"]*)"', body) or [""])[0]
        if st != 200 or not target.startswith(f"https://{main}/") or fetch(target)[0] != 200:
            bad += 1
            problems.append(f"зеркало {mirror}/{pg}: {st} → {target or 'нет canonical'}")
    report.append(f"зеркало {mirror} → {main}: страниц {len(pages)}, битых {bad}")
# http → https: GitHub отдаёт 301, только если включено «Enforce HTTPS»
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None
opener = urllib.request.build_opener(NoRedirect)
for host in list(SITES) + [m for m in MIRRORS if not any(x in m for x in SKIP_EXT)]:
    try:
        opener.open(urllib.request.Request(f"http://{host}/", headers=UA), timeout=20)
        problems.append(f"http://{host}/ не перенаправляет на https")
    except urllib.error.HTTPError as e:
        loc = e.headers.get("Location", "")
        if e.code != 301 or not loc.startswith(f"https://{host}"):
            problems.append(f"http://{host}/ → {e.code} {loc}")
    except Exception as e:  # noqa: BLE001
        problems.append(f"http://{host}/: {e}")
print("\n".join(report))
print("\nпроблем нет" if not problems else "\nПРОБЛЕМЫ:\n" + "\n".join(problems))
