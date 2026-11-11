"""Podstrony tematyczne: strona/<slug>/index.html dla każdego odcinka z scripts/tematy.json.

Wywoływane z scripts/seo.py (nie uruchamiaj osobno). Każda podstrona: film (lekki embed, iframe dopiero po kliknięciu),
„Do zapamiętania”, przykład krok po kroku, link do pastwiska w grze, pytania i odpowiedzi,
inne tematy z tej samej klasy. JSON-LD: WebPage + VideoObject (z rozdziałami jako Clip) + BreadcrumbList + FAQPage.
"""
import html, json, os

E = lambda s: html.escape(str(s), quote=True)


def secs(t):
    m, s = t.split(":")
    return int(m) * 60 + int(s)


def ld_for(e, site, channel, klasa, total):
    t, url = e["t"], e["page"]
    watch = f"https://www.youtube.com/watch?v={e['id']}"
    video = {
        "@type": ["VideoObject", "LearningResource"], "@id": f"{url}#film",
        "name": f"{e['title']} | Matematyka {klasa[e['klasa']]} | Grok liczy owce #{e['n']}",
        "description": t["lead"], "thumbnailUrl": f"{site}/{e['thumb']}", "uploadDate": e["date"],
        "duration": e["iso"], "embedUrl": f"https://www.youtube.com/embed/{e['id']}", "url": watch,
        "inLanguage": "pl", "isFamilyFriendly": True, "isAccessibleForFree": True,
        "educationalLevel": klasa[e["klasa"]], "learningResourceType": "film edukacyjny", "teaches": t["h1"],
        "audience": {"@type": "EducationalAudience", "educationalRole": "student"},
        "partOfSeries": {"@id": f"{site}/#seria"}, "publisher": {"@id": f"{site}/#serial"},
    }
    ch = t.get("rozdzialy") or []
    if ch:
        starts = [secs(a) for a, _ in ch] + [total]
        video["hasPart"] = [{"@type": "Clip", "name": name, "startOffset": starts[i], "endOffset": starts[i + 1],
                             "url": f"{watch}&t={starts[i]}s"} for i, (_, name) in enumerate(ch)]
    page = {"@type": "WebPage", "@id": url, "url": url, "name": t["title"], "description": t["description"],
            "inLanguage": "pl", "isPartOf": {"@id": f"{site}/#strona"}, "primaryImageOfPage": f"{site}/{e['thumb']}",
            "mainEntity": {"@id": f"{url}#film"}, "breadcrumb": {"@id": f"{url}#okruszki"}}
    crumbs = {"@type": "BreadcrumbList", "@id": f"{url}#okruszki", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Grok liczy owce", "item": f"{site}/"},
        {"@type": "ListItem", "position": 2, "name": f"Matematyka {klasa[e['klasa']]}", "item": f"{site}/#odcinki"},
        {"@type": "ListItem", "position": 3, "name": t["h1"], "item": url}]}
    graph = [page, video, crumbs]
    if t.get("faq"):
        graph.append({"@type": "FAQPage", "@id": f"{url}#pytania", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in t["faq"]]})
    return {"@context": "https://schema.org", "@graph": graph}


def render(e, eps, site, channel, klasa, ld):
    t = e["t"]
    url, watch, k = e["page"], f"https://www.youtube.com/watch?v={e['id']}", klasa[e["klasa"]]
    same = [x for x in eps if x["t"] and x["klasa"] == e["klasa"] and x is not e]
    other = [x for x in eps if x["t"] and x["klasa"] != e["klasa"]][:4]
    i = [x["n"] for x in eps].index(e["n"])
    prev = eps[i - 1] if i > 0 and eps[i - 1]["t"] else None
    nxt = eps[i + 1] if i + 1 < len(eps) and eps[i + 1]["t"] else None

    pamietaj = "\n".join(f"        <li>{E(p)}</li>" for p in t["pamietaj"])
    kroki = "\n".join(f"        <li>{E(p)}</li>" for p in t["przyklad"]["kroki"])
    faq = "\n".join(f"    <details><summary>{E(q)}</summary><p>{E(a)}</p></details>" for q, a in t.get("faq", []))
    tile = lambda x: (f'      <a class="tile" href="../{x["t"]["slug"]}/"><img src="../{x["thumb"]}" alt="" loading="lazy" width="800" height="450">'
                      f'<span>{E(x["t"]["h1"])}</span></a>')
    tiles = "\n".join(tile(x) for x in same)
    tiles_other = "\n".join(tile(x) for x in other)
    other_k = "klasa 5" if e["klasa"] == "4" else "klasa 4"
    game = ""
    if e["game"]:
        game = f'''
<section class="t-game">
  <div class="wrap game">
    <img src="../img/owca.png" alt="" width="240" height="240" loading="lazy">
    <div>
      <h2>Poćwicz w grze: {E(e["game"][1])}</h2>
      <p>Pastwisko do tego odcinka w darmowej grze „Policz stado!”. Bez logowania, działa na telefonie i na tablicy interaktywnej.</p>
      <a class="btn" href="../gra.html#{E(e["game"][0])}">Zagraj: {E(e["game"][1])}</a>
    </div>
  </div>
</section>'''
    pager = '<div class="pager">' + (f'<a href="../{prev["t"]["slug"]}/">← #{prev["n"]} {E(prev["title"])}</a>' if prev else "<span></span>") + \
            (f'<a href="../{nxt["t"]["slug"]}/">#{nxt["n"]} {E(nxt["title"])} →</a>' if nxt else "<span></span>") + "</div>"
    return f'''<!doctype html>
<html lang="pl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(t["title"])}</title>
<meta name="description" content="{E(t["description"])}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Grok liczy owce">
<meta property="og:locale" content="pl_PL">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{E(t["h1"])} – matematyka {k} | Grok liczy owce">
<meta property="og:description" content="{E(t["description"])}">
<meta property="og:image" content="{site}/{e["thumb"]}">
<meta property="og:image:width" content="800">
<meta property="og:image:height" content="450">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#7cc8f2">
<link rel="icon" href="../favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@600;800&family=Nunito:wght@600;700;800;900&display=swap&subset=latin-ext" rel="stylesheet">
<link rel="stylesheet" href="../temat.css">
<!-- Plik generowany przez scripts/seo.py z scripts/tematy.json. Nie edytuj ręcznie. -->
<script type="application/ld+json">
{json.dumps(ld, ensure_ascii=False, indent=1)}
</script>
</head>
<body>
<header class="nav">
  <div class="wrap">
    <a class="brand" href="../"><img src="../img/awatar.jpg" alt="" width="44" height="44"><span>Grok liczy owce</span></a>
    <a class="link" href="../#odcinki">Wszystkie odcinki</a>
    <a class="link" href="../gra.html">Gra „Policz stado!”</a>
    <a class="btn btn-yt" href="{channel}" target="_blank" rel="noopener"><span class="play"></span>YouTube</a>
  </div>
</header>

<main>
<section class="t-hero">
  <div class="wrap">
    <nav class="crumbs" aria-label="Okruszki"><ol>
      <li><a href="../">Grok liczy owce</a></li>
      <li><a href="../#odcinki">Matematyka {k}</a></li>
      <li aria-current="page">{E(t["h1"])}</li>
    </ol></nav>
    <span class="eyebrow">Matematyka · {k} · odcinek #{e["n"]}</span>
    <h1>{E(t["h1"])}</h1>
    <p class="lead">{E(t["lead"])}</p>
    <div class="player">
      <a class="yt" href="{E(watch)}" data-id="{E(e["id"])}" aria-label="Odtwórz film: {E(e["title"])}">
        <img src="../{e["thumb"]}" alt="Odcinek {e["n"]}: {E(e["title"])} – Grok, owca Beata i Kosmita" width="800" height="450" fetchpriority="high">
        <span class="yt-play"></span>
      </a>
    </div>
  </div>
</section>

<section>
  <div class="wrap cols">
    <div>
      <h2>Przykład krok po kroku</h2>
      <div class="example">
        <p class="q">{E(t["przyklad"]["pytanie"])}</p>
        <ol>
{kroki}
        </ol>
      </div>
    </div>
    <aside class="note">
      <h2>Do zapamiętania</h2>
      <ul>
{pamietaj}
      </ul>
      <p class="hint">Przepisz do zeszytu!</p>
    </aside>
  </div>
</section>
{game}
<section class="faq">
  <div class="wrap">
    <h2>Pytania i odpowiedzi</h2>
{faq}
  </div>
</section>

<section class="more">
  <div class="wrap">
    <h2>Inne tematy: matematyka {k}</h2>
    <div class="tiles">
{tiles}
    </div>
    <h2 style="margin-top:44px">Tematy: matematyka {other_k}</h2>
    <div class="tiles">
{tiles_other}
    </div>
    {pager}
  </div>
</section>
</main>

<footer>
  <div class="wrap">
    <p><a href="../">Grok liczy owce</a> · animowana matematyka dla klas 4–5 · <a href="{channel}" target="_blank" rel="noopener">kanał na YouTube</a></p>
    <p>© 2026</p>
  </div>
</footer>

<script>
// Film ładuje się dopiero po kliknięciu (szybsza strona, bez ciasteczek YouTube przed odtworzeniem).
document.querySelector(".yt").addEventListener("click", (ev) => {{
  ev.preventDefault();
  const a = ev.currentTarget, f = document.createElement("iframe");
  f.src = "https://www.youtube-nocookie.com/embed/" + a.dataset.id + "?autoplay=1&rel=0";
  f.title = a.getAttribute("aria-label");
  f.allow = "accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture; fullscreen";
  a.replaceWith(f);
}});
</script>
</body>
</html>
'''


def render_404(eps, channel):
    """Strona 404 (GitHub Pages podaje ją pod każdym złym adresem, więc ścieżki muszą być bezwzględne)."""
    tiles = "\n".join(f'      <a class="tile" href="/{x["t"]["slug"]}/"><img src="/{x["thumb"]}" alt="" loading="lazy" width="800" height="450">'
                      f'<span>{E(x["t"]["h1"])}</span></a>' for x in eps if x["t"])
    return f'''<!doctype html>
<html lang="pl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Nie ma takiej strony · Grok liczy owce</title>
<meta name="robots" content="noindex">
<link rel="icon" href="/favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@600;800&family=Nunito:wght@600;700;800;900&display=swap&subset=latin-ext" rel="stylesheet">
<link rel="stylesheet" href="/temat.css">
<!-- Plik generowany przez scripts/seo.py. Nie edytuj ręcznie. -->
</head>
<body>
<header class="nav">
  <div class="wrap">
    <a class="brand" href="/"><img src="/img/awatar.jpg" alt="" width="44" height="44"><span>Grok liczy owce</span></a>
    <a class="link" href="/#odcinki">Wszystkie odcinki</a>
    <a class="link" href="/gra.html">Gra „Policz stado!”</a>
    <a class="btn btn-yt" href="{channel}" target="_blank" rel="noopener"><span class="play"></span>YouTube</a>
  </div>
</header>
<main>
<section class="t-hero">
  <div class="wrap game">
    <img src="/img/owca-spi.png" alt="" width="240" height="240">
    <div>
      <span class="eyebrow">Błąd 404</span>
      <h1>Ta owca uciekła z zagrody</h1>
      <p class="lead">Nie ma takiej strony. Grok liczył, liczył i się zgubił. Wybierz temat poniżej albo wróć na stronę główną.</p>
      <a class="btn" href="/">Strona główna</a>
    </div>
  </div>
</section>
<section class="more">
  <div class="wrap">
    <h2>Tematy z matematyki</h2>
    <div class="tiles">
{tiles}
    </div>
  </div>
</section>
</main>
<footer>
  <div class="wrap"><p><a href="/">Grok liczy owce</a> · animowana matematyka dla klas 4–5</p></div>
</footer>
</body>
</html>
'''


def generate(eps, root, site, channel, klasa, dates):
    open(os.path.join(root, "strona", "404.html"), "w", encoding="utf-8").write(render_404(eps, channel))
    for e in eps:
        if not e["t"]:
            continue
        total = secs(e["dur"])
        ld = ld_for(e, site, channel, klasa, total)
        d = os.path.join(root, "strona", e["t"]["slug"])
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(render(e, eps, site, channel, klasa, ld))
