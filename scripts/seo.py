#!/usr/bin/env python3
"""SEO/GEO strony: dane strukturalne (JSON-LD), sitemap.xml i llms.txt z kart odcinków w index.html.

Uruchom w katalogu głównym repo po każdej zmianie odcinków:  python3 scripts/seo.py
- czyta karty odcinków z strona/index.html (numer, tytuł, opis, klasa, czas, link do YouTube),
- daty publikacji pobiera z YouTube i zapamiętuje w scripts/seo-daty.json,
- wpisuje JSON-LD między <!-- SEO:START --> i <!-- SEO:END --> w index.html,
- uzupełnia alt miniaturek, zapisuje strona/sitemap.xml i strona/llms.txt,
- z scripts/tematy.json generuje podstrony tematyczne strona/<slug>/index.html (scripts/podstrony.py).
"""
import datetime, html, json, os, re, sys, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://grokliczyowce.pl"
CHANNEL = "https://www.youtube.com/@grokliczyowce"
INDEX = os.path.join(ROOT, "strona", "index.html")
DATES = os.path.join(ROOT, "scripts", "seo-daty.json")

src = open(INDEX, encoding="utf-8").read()


def text(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s)).strip()


# ---- karty odcinków ----
grid = src[src.index('<div class="grid">'):src.index('<div class="ep trailer">')]
cards = re.split(r'\n\s*(?=<(?:a|div) class="ep[ "])', grid)[1:]
eps = []
for c in cards:
    num = re.search(r"<b>#(\d+)</b>", c)
    vid = re.search(r"watch\?v=([\w-]+)", c)
    if not num or not vid:
        continue  # odcinek jeszcze bez linku
    m, s = re.search(r'class="dur">(\d+):(\d+)<', c).groups()
    game = re.search(r'href="gra\.html#(\w+)"[^>]*>.*?Zagraj: ([^<]+)</a>', c)
    eps.append(dict(
        n=int(num.group(1)), id=vid.group(1),
        title=text(re.search(r"<h3>(.*?)</h3>", c).group(1)),
        desc=text(re.search(r"<p>(.*?)</p>", c).group(1)),
        klasa=re.search(r'data-klasa="(\d)"', c).group(1),
        thumb=re.search(r'src="(img/odc-\d+\.jpg)"', c).group(1),
        dur=f"{m}:{s}", iso=f"PT{int(m)}M{int(s)}S",
        game=(game.group(1), text(game.group(2))) if game else None,
    ))
eps.sort(key=lambda e: e["n"])

# ---- daty publikacji z YouTube ----
dates = json.load(open(DATES)) if os.path.exists(DATES) else {}
for e in eps:
    if e["id"] not in dates:
        req = urllib.request.Request(f"https://www.youtube.com/watch?v={e['id']}",
                                     headers={"User-Agent": "Mozilla/5.0", "Accept-Language": "pl"})
        page = urllib.request.urlopen(req, timeout=20).read().decode("utf-8", "ignore")
        d = re.search(r'itemprop="uploadDate" content="([^"]+)"', page) or re.search(r'"uploadDate":"([^"]+)"', page)
        if not d:
            raise SystemExit(f"Nie znalazłem daty publikacji odcinka #{e['n']} ({e['id']})")
        dates[e["id"]] = d.group(1)
json.dump(dates, open(DATES, "w"), indent=2, ensure_ascii=False)
for e in eps:
    e["date"] = dates[e["id"]]

# ---- treść podstron tematycznych (scripts/tematy.json) ----
TEMATY = json.load(open(os.path.join(ROOT, "scripts", "tematy.json"), encoding="utf-8"))
for e in eps:
    e["t"] = TEMATY.get(str(e["n"]))
    e["page"] = f"{SITE}/{e['t']['slug']}/" if e["t"] else None

# ---- JSON-LD ----
KLASA = {"4": "klasa 4", "5": "klasa 5"}
org = {"@type": "Organization", "@id": f"{SITE}/#serial", "name": "Grok liczy owce", "url": f"{SITE}/",
       "logo": f"{SITE}/img/awatar.jpg", "sameAs": [CHANNEL]}
site = {"@type": "WebSite", "@id": f"{SITE}/#strona", "name": "Grok liczy owce", "url": f"{SITE}/",
        "inLanguage": "pl", "publisher": {"@id": f"{SITE}/#serial"}}
series = {
    "@type": "CreativeWorkSeries", "@id": f"{SITE}/#seria", "name": "Grok liczy owce",
    "description": "Animowany serial matematyczny dla uczniów klas 4–5 szkoły podstawowej.",
    "inLanguage": "pl", "genre": ["animacja edukacyjna", "matematyka"], "isFamilyFriendly": True,
    "audience": {"@type": "EducationalAudience", "educationalRole": "student", "audienceType": "uczniowie klas 4–5 szkoły podstawowej"},
    "educationalLevel": ["klasa 4", "klasa 5"], "about": {"@type": "Thing", "name": "matematyka"},
    "publisher": {"@id": f"{SITE}/#serial"}, "url": f"{SITE}/", "sameAs": [CHANNEL],
}
videos = {
    "@type": "ItemList", "@id": f"{SITE}/#odcinki", "name": "Odcinki serialu Grok liczy owce",
    "itemListOrder": "https://schema.org/ItemListOrderAscending", "numberOfItems": len(eps),
    # Pełny VideoObject każdego filmu jest na jego podstronie (tam film jest osadzony). Tu tylko lista odcinków.
    "itemListElement": [{
        "@type": "ListItem", "position": e["n"], "name": f"{e['title']} – matematyka {KLASA[e['klasa']]}",
        "url": e["page"] or f"https://www.youtube.com/watch?v={e['id']}",
    } for e in eps],
}

# ---- pastwiska gry (z obiektu PASTWISKA w gra.html) ----
GRA = os.path.join(ROOT, "strona", "gra.html")
gra = open(GRA, encoding="utf-8").read()
pastwiska = [dict(key=k, klasa=kl, title=html.unescape(t), ep=int(ep), desc=html.unescape(d)) for k, kl, t, ep, d in re.findall(
    r'\{ key: "(\w+)", klasa: "(\d+)",.*?title: "([^"]+)", ep: (\d+), desc: "([^"]+)"', gra)]
by_n = {e["n"]: e for e in eps}
game = {
    "@type": ["VideoGame", "LearningResource"], "name": "Policz stado!", "url": f"{SITE}/gra.html",
    "description": "Darmowa gra matematyczna w przeglądarce dla klas 4–5. Pastwiska: "
                   + ", ".join(by_n[p["ep"]]["title"].lower() if p["ep"] in by_n else p["title"] for p in pastwiska) + ".",
    "inLanguage": "pl", "isAccessibleForFree": True, "gamePlatform": "przeglądarka internetowa",
    "applicationCategory": "Game", "educationalLevel": ["klasa 4", "klasa 5"], "isFamilyFriendly": True,
    "publisher": {"@id": f"{SITE}/#serial"},
}
ld = {"@context": "https://schema.org", "@graph": [org, site, series, videos, game]}
block = ('<!-- SEO:START (generowane przez scripts/seo.py, nie edytuj ręcznie) -->\n'
         '<script type="application/ld+json">\n' + json.dumps(ld, ensure_ascii=False, indent=1) +
         '\n</script>\n<!-- SEO:END -->')
if "<!-- SEO:START" in src:
    src = re.sub(r"<!-- SEO:START.*?<!-- SEO:END -->", lambda _: block, src, flags=re.S)
else:
    src = src.replace("</head>", block + "\n</head>", 1)

# ---- gra.html: JSON-LD i lista tematów ----
gra_ld = {"@context": "https://schema.org", "@graph": [dict(game, **{"@id": f"{SITE}/gra.html#gra"}), {
    "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Grok liczy owce", "item": f"{SITE}/"},
        {"@type": "ListItem", "position": 2, "name": "Gra „Policz stado!”", "item": f"{SITE}/gra.html"}]}]}
gra_block = ('<!-- SEO:START (generowane przez scripts/seo.py, nie edytuj ręcznie) -->\n<script type="application/ld+json">\n'
             + json.dumps(gra_ld, ensure_ascii=False, indent=1) + '\n</script>\n<!-- SEO:END -->')
gra = re.sub(r"<!-- SEO:START.*?<!-- SEO:END -->", lambda _: gra_block, gra, flags=re.S) if "<!-- SEO:START" in gra \
    else gra.replace("</head>", gra_block + "\n</head>", 1)
rows = []
for p in pastwiska:
    e = by_n.get(p["ep"])
    kl = "klasy 4–5" if p["klasa"] == "45" else f"klasa {p['klasa']}"
    temat = (f'<a href="{e["t"]["slug"]}/">{html.escape(e["t"]["h1"])}</a>' if e and e["t"] else html.escape(e["title"] if e else ""))
    rows.append(f'      <li><a class="tp-game" href="#{p["key"]}">{html.escape(p["title"])}</a> <span>({kl})</span> – {html.escape(p["desc"])} '
                f'Temat: {temat}, odcinek #{p["ep"]}.</li>')
tematy_block = ('<!-- TEMATY:START (generowane przez scripts/seo.py z PASTWISKA i scripts/tematy.json) -->\n'
                '    <section class="topics" aria-labelledby="tematy-h">\n'
                '      <h2 id="tematy-h">Pastwiska i tematy z matematyki</h2>\n'
                '      <p>Każde pastwisko ćwiczy temat z jednego odcinka serialu. Przy każdym temacie jest film, ściąga i przykłady.</p>\n'
                '      <ul>\n' + "\n".join(rows) + '\n      </ul>\n    </section>\n    <!-- TEMATY:END -->')
gra = re.sub(r"<!-- TEMATY:START.*?<!-- TEMATY:END -->", lambda _: tematy_block, gra, flags=re.S) if "<!-- TEMATY:START" in gra \
    else gra.replace('    <p class="back-home">', "    " + tematy_block + '\n    <p class="back-home">', 1)
open(GRA, "w", encoding="utf-8").write(gra)

# alt miniaturek
for e in eps:
    src = src.replace(f'<img src="{e["thumb"]}" alt=""',
                      f'<img src="{e["thumb"]}" alt="Odcinek {e["n"]}: {html.escape(e["title"])} – miniaturka filmu"')
for e in eps:
    if e["t"]:
        src = src.replace(f'<h3>{html.escape(e["title"], quote=False)}</h3>',
                          f'<h3><a href="{e["t"]["slug"]}/">{html.escape(e["title"], quote=False)}</a></h3>', 1)
open(INDEX, "w", encoding="utf-8").write(src)

# ---- podstrony tematyczne ----
import podstrony
podstrony.generate(eps, ROOT, SITE, CHANNEL, KLASA, dates)

# ---- sitemap.xml ----
today = datetime.date.today().isoformat()
urls = [("", "1.0"), ("gra.html", "0.8")] + [(e["t"]["slug"] + "/", "0.9") for e in eps if e["t"]]
sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
sm += [f"  <url><loc>{SITE}/{u}</loc><lastmod>{today}</lastmod><priority>{p}</priority></url>" for u, p in urls]
sm.append("</urlset>")
open(os.path.join(ROOT, "strona", "sitemap.xml"), "w").write("\n".join(sm) + "\n")

# ---- llms.txt (dla wyszukiwarek AI) ----
L = [
    "# Grok liczy owce",
    "",
    "> Darmowy animowany serial matematyczny po polsku dla uczniów klas 4–5 szkoły podstawowej. "
    "Każdy odcinek (ok. 5 minut, na YouTube, z polskimi napisami i rozdziałami) wyjaśnia jeden temat z programu matematyki. "
    "Bohaterowie: pasterz Grok, uparta owca Beata i Kosmita, który liczy po osiem.",
    "",
    "Dla kogo: uczniowie klas 4 i 5 (powtórka przed klasówką, nadrobienie lekcji), rodzice i nauczyciele matematyki (krótki film na początek lekcji).",
    "W odcinkach są zagadki „Zatrzymaj film!” i quizy. Na stronie jest też darmowa gra „Policz stado!”.",
    "",
    "## Odcinki",
    "",
]
for e in eps:
    g = f" Gra do odcinka: {SITE}/gra.html#{e['game'][0]} („{e['game'][1]}”)." if e["game"] else ""
    strona = f" Opis, ściąga i przykłady: {e['page']}" if e["page"] else ""
    L.append(f"- [#{e['n']} {e['title']} (matematyka {KLASA[e['klasa']]}, {e['dur']})](https://www.youtube.com/watch?v={e['id']}): {e['desc']}{g}{strona}")
L += [
    "",
    "## Materiały",
    "",
    f"- [Strona serialu]({SITE}/): wszystkie odcinki z podziałem na klasy",
    f"- [Gra „Policz stado!”]({SITE}/gra.html): mini-gra w przeglądarce, bez logowania, działa na telefonie i tablicy interaktywnej",
    f"- [Kanał YouTube]({CHANNEL})",
    "- [Playlista klasa 4](https://www.youtube.com/playlist?list=PLWAZGF4-ivZc)",
    "- [Playlista klasa 5](https://www.youtube.com/playlist?list=PLOltZXzmRTJY)",
    "",
]
open(os.path.join(ROOT, "strona", "llms.txt"), "w").write("\n".join(L))
print(f"{len(eps)} odcinków → JSON-LD w index.html, {sum(1 for e in eps if e['t'])} podstron tematycznych, sitemap.xml, llms.txt")
