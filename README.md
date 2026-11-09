# Grok liczy owce · strona

Strona główna serialu „Grok liczy owce”, czyli animowanej matematyki dla klas 4–5.

Cała strona leży w `strona/` (czysty HTML i CSS, bez budowania). Po każdym pushu na `main` GitHub Actions
(`.github/workflows/pages.yml`) wrzuca ją na GitHub Pages.

Podgląd lokalny: otwórz `strona/index.html` w przeglądarce.

Odcinki #1–#14 linkują do filmów na kanale `@grokliczyowce`, a klasy na kartach są wzięte z tytułów na YouTube.
Po wrzuceniu kolejnego odcinka w `index.html` zamień jego `<div class="ep soon" …>` na `<a class="ep" … href="https://www.youtube.com/watch?v=…">`, a plakietkę „Wkrótce” na czas trwania.

## Mini-gra „Policz stado!”

`strona/gra.html` to samodzielna gra (jeden plik, bez budowania). Pastwiska: „Ile owiec?” (odc. 7), „Owca na osi” (odc. 5),
„Zagrody” (odc. 2), „Stado w prostokąt” (odc. 3), „Okrągłe pary” (odc. 8), „Która większa?” (odc. 1), „Snopki dla zagród” (odc. 4),
„Ile zostało?” (odc. 6), „Ile lat ma pasterz?” (odc. 10), „Trójkątna zagroda” (odc. 11), „Owce w rzędach” (odc. 14) i finał „Wielka powtórka” (odc. 9, 10 rund na czas).
Linki do odcinków są w obiekcie `ODCINKI` w `gra.html` (po dodaniu pastwiska do nowego odcinka wpisz tam jego adres).
Do pastwiska można wejść bezpośrednio: `gra.html#szacowanie`, `#os`, `#zagrody`, `#prostokat`, `#pary`, `#porownaj`, `#snopki`, `#zostalo`, `#zadania`, `#trojkaty`, `#mnozenie`, `#final`.

## SEO i wyszukiwarki AI

Strona działa pod adresem https://grokliczyowce.pl (DNS w OVH, domena ustawiona w Settings → Pages).
`<title>`, opisy i znaczniki Open Graph są wpisane ręcznie w `<head>` obu stron. Dane strukturalne (JSON-LD
z listą odcinków), `strona/sitemap.xml` i `strona/llms.txt` (opis serialu dla ChatGPT, Perplexity i innych wyszukiwarek AI)
generuje skrypt. **Po dodaniu albo zmianie odcinka w `index.html` uruchom:**

    python3 scripts/seo.py

Daty publikacji filmów skrypt pobiera z YouTube i zapisuje w `scripts/seo-daty.json`.
