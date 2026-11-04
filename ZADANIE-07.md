# ZADANIE 07 — Trzy tryby uruchomienia: PR, main, noc

## Cel

Przestać uruchamiać pełną regresję UI przy każdej zmianie. Na pull requeście ma działać krótki **smoke**, a pełny zestaw testów na `main` oraz w nocnym przebiegu.

To właśnie tutaj realizujemy główny cel warsztatu: skracamy czas oczekiwania na feedback bez rezygnowania z pełnego pokrycia.

## Na czym polega problem

Testy UI to **123 testy i około 2 minut 27 sekund** — najdłuższa część całego przebiegu. Obecnie uruchamiają się w całości przy każdym pull requeście.

Tymczasem autor pull requesta potrzebuje przede wszystkim szybkiej odpowiedzi na pytanie: *czy ta zmiana nie psuje najważniejszej ścieżki?*

Na to pytanie odpowiada **pięć testów** oznaczonych jako `@smoke`, które przechodzą podstawową ścieżkę klienta w sklepie:

- katalog się ładuje,
- wyszukiwarka znajduje produkt,
- produkt trafia do koszyka,
- koszyk pokazuje pozycję i sumę,
- zamówienie da się złożyć.

Jeśli któryś z tych testów nie przechodzi, pull request i tak wymaga poprawy. Jeśli wszystkie są zielone, zmiana jest gotowa do dalszego sprawdzenia, a pełna regresja może poczekać do scalenia.

W zespole, który otwiera kilkanaście pull requestów dziennie, oznacza to realnie mniej czasu spędzonego na czekaniu.

## Zadanie

Zmieniasz plik `.github/workflows/ci.yml`. Sekcja `concurrency:` z ZADANIA 02 oraz joby z ZADAŃ 04–06 pozostają bez zmian, poza jobem `test-ui`.

**1. Dodaj nocny przebieg i możliwość wyboru trybu.** Sekcja `on:` ma wyglądać tak:

```yaml
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 2 * * *'
  workflow_dispatch:
    inputs:
      suite:
        description: 'UI test scope'
        type: choice
        default: smoke
        options: [smoke, regression, all]
```

Co jest tutaj ważne:

| Element | Po co |
|---|---|
| `schedule` z `cron: '0 2 * * *'` | uruchamia pełną regresję codziennie o 2:00 **czasu UTC**, czyli latem o 4:00 w Polsce |
| `inputs.suite` | przy ręcznym uruchomieniu pozwala wybrać zakres testów: `smoke` (5 testów), `regression` (wszystkie testy poza smoke), `all` (cały zestaw) |

**2. Pokaż wybrany tryb w nazwie joba.** W jobie `test-ui` zamień linię `name: UI tests`, która stoi bezpośrednio pod `test-ui:`. To nazwa całego joba, a nie kroku z testami — krok zmienisz w punkcie 3. Po zmianie początek joba wygląda tak:

```yaml
  test-ui:
    name: UI tests (${{ github.event_name == 'pull_request' && 'smoke' || github.event_name == 'workflow_dispatch' && inputs.suite || 'full regression' }})
    runs-on: ubuntu-latest
    needs: [build, quality, unit]
```

Na pull requeście job będzie nazywał się `UI tests (smoke)`. Przy ręcznym uruchomieniu w nazwie pojawi się wybrany tryb. Na `main` i w przebiegu nocnym job będzie nazywał się `UI tests (full regression)`.

**3. Wybieraj testy w zależności od trybu.** W jobie `test-ui` zamień krok `- run: npm run test:ui` na:

```yaml
      - name: UI tests
        run: npx playwright test --project=ui-chromium ${{ env.GREP }}
        env:
          GREP: >-
            ${{ (github.event_name == 'pull_request'
                 || (github.event_name == 'workflow_dispatch' && inputs.suite == 'smoke'))
                && '--grep @smoke'
             || (github.event_name == 'workflow_dispatch' && inputs.suite == 'regression')
                && '--grep-invert @smoke'
             || '' }}
```

- `--grep @smoke` uruchamia tylko testy oznaczone tagiem `@smoke`.
- `--grep-invert @smoke` uruchamia wszystkie testy poza smoke.
- Pusta wartość oznacza uruchomienie całego zestawu.

W naszym przypadku tag `@smoke` znajduje się w nazwie bloku `describe`, więc obejmuje wszystkie pięć testów znajdujących się w środku.

**4. Zatwierdź zmiany, wypchnij je na `main` i sprawdź pełną regresję.**

```bash
git add .github/workflows/ci.yml
git commit -m "Smoke on pull requests, full regression on main and nightly"
git push
```

W zakładce **Actions** otwórz nowy przebieg. Job powinien nazywać się `UI tests (full regression)`, a na końcu logu kroku `UI tests` powinno być `123 passed`. Zapisz czas joba.

**5. Sprawdź smoke na pull requeście.**

```bash
git checkout -b check-smoke
git commit --allow-empty -m "Check smoke tests"
git push -u origin check-smoke
```

Otwórz pull request z `check-smoke` do `main`. Job powinien nazywać się `UI tests (smoke)`, a w logu powinno być `5 passed`. Zapisz czas joba oraz całkowity czas przebiegu pull requesta i porównaj go z przebiegiem pełnej regresji na `main`. Pull requesta nie scalaj.

**6. Sprawdź ręczne uruchomienie.** W zakładce **Actions** wybierz po lewej **CI** i kliknij **Run workflow**. Zostaw gałąź `main`, w polu **UI test scope** wybierz `regression` i uruchom workflow. Job powinien nazywać się `UI tests (regression)`, a w logu powinno być `118 passed` — wszystkie testy poza pięcioma oznaczonymi jako smoke.

**7. Sprawdź nocny przebieg — jutro.** Nocny przebieg jest zaplanowany na 2:00 czasu UTC, więc dzisiaj nie zobaczysz jego wyniku. Na razie wystarczy upewnić się, że workflow jest poprawny i że przebiegi z poprzednich kroków uruchamiają się zgodnie z oczekiwaniami.

Jutro rano zajrzyj do zakładki **Actions**. Powinien pojawić się przebieg uruchomiony z harmonogramu (*scheduled*). GitHub nie gwarantuje godziny: taki przebieg potrafi przyjść z opóźnieniem nawet kilku godzin (w próbnym przebiegu warsztatu — o 8:16 zamiast o 2:00 UTC), a przy dużym obciążeniu czasem w ogóle się nie pojawia. Brak przebiegu dokładnie o 2:00 nie oznacza błędu w konfiguracji.

Nocne przebiegi zadziałają, ponieważ repozytorium zostało utworzone z szablonu. W forkach harmonogramy GitHub Actions są domyślnie wyłączone.

**8. Wróć na `main`:**

```bash
git checkout main
```

## Kryteria akceptacji

- [ ] push na `main` uruchamia pełny zestaw testów: `UI tests (full regression)`, 123 testy (krok 4)
- [ ] pull request uruchamia tylko smoke: `UI tests (smoke)`, 5 testów (krok 5)
- [ ] przebieg pull requesta jest zauważalnie krótszy niż przebieg pełnej regresji na `main` (krok 5)
- [ ] przy ręcznym uruchomieniu można wybrać tryb, a jego nazwa pojawia się w nazwie joba (krok 6)
- [ ] nocny przebieg jest skonfigurowany w sekcji `schedule` (krok 1, efekt jutro — krok 7)

## Zmierz

| Co | Przed | Po |
|---|---|---|
| Czas `UI tests` na pull requeście | 2:27 | ? |
| Czas `UI tests` na `main` | 2:27 | ? |
| Całkowity czas przebiegu pull requesta | ? | ? |
| Liczba testów UI na pull requeście | 123 | ? |
