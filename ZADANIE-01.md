# ZADANIE 01 — Baseline i pomiar

## Cel

Zmierzyć stan wyjściowy pipeline’u i ustalić metrykę, którą będziemy poprawiać przez cały dzień.

W tym zadaniu nie zmieniasz **ani jednej linijki** w `ci.yml`.

Najpierw mierzymy, dopiero potem optymalizujemy. Bez punktu odniesienia nie da się pod koniec dnia powiedzieć, które zmiany naprawdę skróciły czas oczekiwania na feedback.

## Na czym polega problem

Pipeline z pliku `.github/workflows/ci.yml` działa. Pobiera kod, instaluje zależności, uruchamia wszystkie testy i zapisuje raport. Na pierwszy rzut oka wszystko jest w porządku.

Na wynik trzeba jednak czekać kilka minut. Nawet test jednostkowy, który trwa około sekundy, rusza dopiero po instalacji przeglądarek, choć w ogóle ich nie potrzebuje.

Do tego niektóre błędy przechodzą niezauważone, a o błędzie wykrywanym przez testy UI dowiadujemy się dopiero pod koniec przebiegu.

## Zadanie

**1. Znajdź bazowy przebieg pipeline’u na `main`.**

Pipeline uruchomił się sam na branchu `main` zaraz po utworzeniu repozytorium z szablonu. Otwórz ten przebieg w zakładce **Actions**.

Jeśli go nie ma, wypchnij dowolną drobną zmianę, na przykład dopisz jedną linijkę do `README.md`.

**2. Odczytaj czasy poszczególnych kroków.**

W przebiegu wejdź w job `test` i rozwiń kolejne kroki. Czas wykonania widać przy każdym z nich.

Wpisz czasy do tabeli *Czasy kroków* w pliku `docs/baseline.md`. Plik jest już w repozytorium — uzupełniasz tylko puste pola. W ostatnim wierszu wpisz czas całego przebiegu.

**3. Pobierz pięć branchy z błędami.**

Pięć osób z zespołu przygotowało niezależne zmiany w sklepie. Każda zmiana jest na osobnym branchu i każda zawiera błąd, który nie powinien trafić do `main`:

| Branch | Co zmienia | Plik |
|---|---|---|
| `demo/failing-unit` | inne zaokrąglanie kwoty rabatu procentowego w funkcji `discountAmount` | `src/shared/discounts.ts` |
| `demo/failing-ui` | nowy próg stanu magazynowego, od którego w katalogu pojawia się etykieta „Ostatnie sztuki” | `src/web/views/Catalog.tsx` |
| `demo/failing-search` | krótsza nazwa parametru, którym wyszukiwarka w katalogu wysyła zapytanie do API | `src/web/api.ts` |
| `demo/failing-lint` | przeróbka funkcji `subtotal`, która liczy sumę koszyka: wynik trafia do zmiennej, a pusty koszyk jest obsłużony osobno | `src/shared/cart.ts` |
| `demo/failing-security` | nowy moduł `payments.ts` z funkcją `chargeOrder`, która wysyła zamówienie do zewnętrznej bramki płatności | `src/server/payments.ts` |

Pipeline ma zatrzymać takie zmiany, zanim ktoś je scali. Sprawdzisz, które z nich zatrzymuje i jak szybko.

Pobierz branche i wypchnij je do swojego repozytorium:

```bash
git remote add warsztat https://github.com/tklepacki/cicd-fast-feedback-workshop.git
git fetch warsztat
git push origin 'refs/remotes/warsztat/demo/*:refs/heads/demo/*'
```

Ten push uruchomi pipeline na wszystkich pięciu branchach. Branche przydadzą się też w kolejnych zadaniach.

**4. Zmierz czas do pierwszego czerwonego sygnału.**

To **główna metryka dnia**: czas od startu przebiegu do chwili, w której wiadomo już, że zmiana zawiera błąd.

Liczysz go od startu przebiegu, a nie od startu kroku z błędem: zsumuj czasy wszystkich wcześniejszych kroków i dodaj czas kroku z błędem. Informacja o błędzie pojawia się dopiero wtedy, gdy ten krok zakończy się na czerwono.

Zmierz ten czas na dwóch branchach i wpisz wyniki do tabeli *Czas do pierwszego czerwonego sygnału* w `docs/baseline.md`:

- `demo/failing-unit` — błąd w naliczaniu rabatu wykrywa test jednostkowy. Zapisz:
  - ile trwa sam test jednostkowy,
  - po ilu sekundach od startu przebiegu widać błąd,
  - co stało się z krokami z testami API i UI.

- `demo/failing-search` — błąd w wyszukiwarce wykrywają testy UI. Zapisz, po ilu minutach od startu przebiegu widać błąd.

Branch `demo/failing-ui` w tym zadaniu tylko pobierasz. Przyda się w ZADANIACH 09, 11 i 13.

**5. Sprawdź `demo/failing-lint` i `demo/failing-security`.**

Zmiana w koszyku łamie regułę lintu, a integracja płatności ma token API wpisany wprost w kod. Sprawdź, jak pipeline reaguje na oba przypadki.

Wpisz wynik do tabeli w sekcji o tych dwóch branchach w `docs/baseline.md` i zastanów się, dlaczego pipeline zachował się właśnie tak.

**6. Wypisz pięć problemów obecnego pipeline’u.**

Zapisz je w sekcji *Pięć problemów* w `docs/baseline.md`.

Nie ma jednej poprawnej listy. Szukaj problemów w konfiguracji pipeline’u i w wynikach wszystkich przebiegów: na `main` i na pięciu branchach.

**7. Zatwierdź pomiary (zalecane).** Wyniki z `docs/baseline.md` będą Ci potrzebne przez cały dzień,
a na koniec porównasz je z finałem. Najbezpieczniej trzymać je w repozytorium:

```bash
git add docs/baseline.md
git commit -m "Record the baseline"
git push
```

Ten push uruchomi pipeline na `main` — to nic złego. Kolejne pomiary dopisuj w tym samym pliku
i zatwierdzaj tak samo, osobnym commitem. To nie jest wymagane: jeśli wolisz, trzymaj plik tylko
lokalnie.

## Kryteria akceptacji

- [ ] w `docs/baseline.md` jest czas **każdego kroku**, a nie tylko całego przebiegu (krok 2)
- [ ] jest czas całego przebiegu (krok 2)
- [ ] jest czas do pierwszego czerwonego sygnału na `demo/failing-unit` (krok 4)
- [ ] jest zapisane, co na `demo/failing-unit` stało się z testami API i UI (krok 4)
- [ ] jest czas do pierwszego czerwonego sygnału na `demo/failing-search` (krok 4)
- [ ] jest wynik `demo/failing-lint` i `demo/failing-security` z wyjaśnieniem (krok 5)
- [ ] jest co najmniej pięć problemów obecnego pipeline’u (krok 6)

## Zmierz

| Co | Gdzie odczytać |
|---|---|
| Czas całego przebiegu | nagłówek przebiegu w zakładce Actions |
| Czas każdego kroku | job `test` → rozwinięty krok |
| Najdłuższy krok | porównanie czasów kroków |
| Czas do błędu wykrywanego przez test jednostkowy | przebieg na `demo/failing-unit` |
| Czas do błędu wykrywanego przez testy UI | przebieg na `demo/failing-search` |
