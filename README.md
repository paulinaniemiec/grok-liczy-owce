# Grok liczy owce · strona

Strona główna serialu „Grok liczy owce”, czyli animowanej matematyki dla klas 4–5.

Cała strona leży w `strona/` (czysty HTML i CSS, bez budowania). Po każdym pushu na `main` GitHub Actions
(`.github/workflows/pages.yml`) wrzuca ją na GitHub Pages.

Podgląd lokalny: otwórz `strona/index.html` w przeglądarce.

Odcinki #1–#17 linkują do filmów na kanale `@grokliczyowce`, a klasy na kartach są wzięte z tytułów na YouTube.
Po wrzuceniu kolejnego odcinka w `index.html` zamień jego `<div class="ep soon" …>` na `<a class="ep" … href="https://www.youtube.com/watch?v=…">`, a plakietkę „Wkrótce” na czas trwania.

## Mini-gra „Policz stado!”

`strona/gra.html` to samodzielna gra (jeden plik, bez budowania). Pastwiska: „Ile owiec?” (odc. 7), „Owca na osi” (odc. 5),
„Zagrody” (odc. 2), „Stado w prostokąt” (odc. 3), „Okrągłe pary” (odc. 8), „Która większa?” (odc. 1), „Snopki dla zagród” (odc. 4),
„Ile zostało?” (odc. 6), „Ile lat ma pasterz?” (odc. 10), „Trójkątna zagroda” (odc. 11), „Sprytne odejmowanie” (odc. 12), „Trójkąty z kosmosu” (odc. 13), „Owce w rzędach” (odc. 14), „Dzielna owca” (odc. 15), „Pion Groka” (odc. 16), „Zera na końcu” (odc. 17) i finał „Wielka powtórka” (odc. 9, 10 rund na czas).
Linki do odcinków są w obiekcie `ODCINKI` w `gra.html` (po dodaniu pastwiska do nowego odcinka wpisz tam jego adres).
Do pastwiska można wejść bezpośrednio: `gra.html#szacowanie`, `#os`, `#zagrody`, `#prostokat`, `#pary`, `#porownaj`, `#snopki`, `#zostalo`, `#zadania`, `#trojkaty`, `#odejmowanie`, `#rownoramienne`, `#mnozenie`, `#dzielenie`, `#wysokosc`, `#sprytne`, `#final`.

## SEO i wyszukiwarki AI

Strona działa pod adresem https://grokliczyowce.pl (DNS w OVH, domena ustawiona w Settings → Pages).
`<title>`, opisy i znaczniki Open Graph są wpisane ręcznie w `<head>` obu stron. Dane strukturalne (JSON-LD
z listą odcinków), `strona/sitemap.xml` i `strona/llms.txt` (opis serialu dla ChatGPT, Perplexity i innych wyszukiwarek AI)
generuje skrypt. **Po dodaniu albo zmianie odcinka w `index.html` uruchom:**

    python3 scripts/seo.py

Daty publikacji filmów skrypt pobiera z YouTube i zapisuje w `scripts/seo-daty.json`.

### Podstrony tematyczne

Każdy odcinek ma własną podstronę pod adresem `grokliczyowce.pl/<temat>/` (np. `/liczby-pierwsze-i-zlozone/`): film,
rozdziały z linkami do minut na YouTube, „Do zapamiętania”, przykład krok po kroku, link do pastwiska w grze i pytania.
Treść jest w `scripts/tematy.json` (klucz = numer odcinka), szablon w `scripts/podstrony.py`, wygląd w `strona/temat.css`.
Strony `strona/<temat>/index.html` generuje `scripts/seo.py`, więc ich nie edytuj ręcznie. Nowy odcinek: dopisz kartę
w `index.html`, wpis w `tematy.json` (slug, h1, title do ~60 znaków, description do ~155 znaków, lead, pamietaj,
przyklad, faq oraz `rozdzialy` z opisu na YouTube albo `w_odcinku`) i uruchom `python3 scripts/seo.py`.
