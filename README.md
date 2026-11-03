# Grok liczy owce · strona

Strona główna serialu „Grok liczy owce”, czyli animowanej matematyki dla klas 4–5.

Cała strona leży w `strona/` (czysty HTML i CSS, bez budowania). Po każdym pushu na `main` GitHub Actions
(`.github/workflows/pages.yml`) wrzuca ją na GitHub Pages.

Podgląd lokalny: otwórz `strona/index.html` w przeglądarce.

Odcinki #1–#7 linkują do filmów na kanale `@grokliczyowce`, a klasy na kartach są wzięte z tytułów na YouTube. #8–#10 są oznaczone jako „Wkrótce”.
Po wrzuceniu kolejnego odcinka w `index.html` zamień jego `<div class="ep soon" …>` na `<a class="ep" … href="https://www.youtube.com/watch?v=…">`, a plakietkę „Wkrótce” na czas trwania.

## Mini-gra „Policz stado!”

`strona/gra.html` to samodzielna gra (jeden plik, bez budowania). Pastwiska: „Ile owiec?” (odc. 7), „Owca na osi” (odc. 5),
„Zagrody” (odc. 2), „Stado w prostokąt” (odc. 3), „Okrągłe pary” (odc. 8) i finał „Wielka powtórka” (odc. 9, 10 rund na czas).
Linki do odcinków są w obiekcie `ODCINKI` w `gra.html`. Po wrzuceniu odcinka 8 albo 9 wpisz tam jego adres.
Do pastwiska można wejść bezpośrednio: `gra.html#szacowanie`, `#os`, `#zagrody`, `#prostokat`, `#pary`, `#final`.
