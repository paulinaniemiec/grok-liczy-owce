# Grok liczy owce · strona

Strona główna serialu „Grok liczy owce”, czyli animowanej matematyki dla klas 4–5.

Cała strona leży w `strona/` (czysty HTML i CSS, bez budowania). Po każdym pushu na `main` GitHub Actions
(`.github/workflows/pages.yml`) wrzuca ją na GitHub Pages.

Podgląd lokalny: otwórz `strona/index.html` w przeglądarce.

Odcinki #1–#7 linkują do filmów na kanale `@grokliczyowce`, a klasy na kartach są wzięte z tytułów na YouTube. #8–#10 są oznaczone jako „Wkrótce”.
Po wrzuceniu kolejnego odcinka w `index.html` zamień jego `<div class="ep soon" …>` na `<a class="ep" … href="https://www.youtube.com/watch?v=…">`, a plakietkę „Wkrótce” na czas trwania.
