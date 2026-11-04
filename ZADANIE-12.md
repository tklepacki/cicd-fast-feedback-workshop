# ZADANIE 12 — Raportowanie w GitHubie: jeden format dla wszystkich testów

## Cel

Doprowadzić do sytuacji, w której wynik wszystkich testów widać bezpośrednio w GitHubie —
**bez pobierania raportów i przeglądania logów**.

## Na czym polega problem

Masz trzy rodzaje testów i każdy raportuje wynik w inny sposób:

| Rodzaj | Jak dziś poznajesz wynik |
|---|---|
| jednostkowe | tekst w logu |
| API | tekst w logu |
| UI | scalony raport do pobrania i rozpakowania (ZADANIE 11) |

Żeby sprawdzić, co nie przeszło, trzeba wejść w przebieg, znaleźć właściwy job, rozwinąć krok
i przejrzeć log — a przy testach UI dodatkowo pobrać raport. To niepotrzebne tarcie: im więcej
kroków dzieli kogoś od wyniku, tym mniejsza szansa, że rzeczywiście z niego skorzysta.

Do tego różni odbiorcy potrzebują różnej szczegółowości:

| Odbiorca | Czego szuka | Gdzie to dostanie |
|---|---|---|
| autor pull requesta | co się zepsuło i w której linii | adnotacje reportera `github` (już działają od ZADANIA 11) |
| recenzent, tester | które testy nie przeszły, z podziałem | check run z listą testów |
| lider zespołu, ktoś z produktu | czy przeszło i ile | tabela w Job Summary |
| ktoś, kto debuguje | dowody | artefakty: raport, trace (ZADANIE 13) |

Żeby wszystkie trzy rodzaje testów dało się pokazać w jednym miejscu, muszą raportować
w **jednym formacie**. Tym formatem będzie JUnit XML.

## Zadanie

Zmieniasz trzy pliki: `vitest.config.ts`, `playwright.config.ts` i `.github/workflows/ci.yml`.
W repozytorium jest już gotowy skrypt `scripts/ci-summary.mjs`, który zamienia pliki JUnit
na tabelę — nie musisz go pisać.

**1. Dodaj JUnit do testów jednostkowych.** W `vitest.config.ts` znajdź:

```ts
    reporters: ['default'],
```

i zamień na:

```ts
    reporters: process.env.CI ? ['default', 'junit'] : ['default'],
    outputFile: { junit: 'reports/unit.xml' },
```

Na CI Vitest nadal wypisuje standardowy wynik, a dodatkowo zapisuje go w formacie JUnit XML.
Lokalnie nic się nie zmienia.

**2. Dodaj JUnit do testów API i UI.** W `playwright.config.ts` zamień reporter z ZADANIA 11 na:

```ts
  reporter: process.env.CI
    ? [
        ['blob'],
        ['github'],
        ['junit', { outputFile: `reports/${process.env.REPORT_NAME ?? 'playwright'}.xml` }],
      ]
    : [['list'], ['html', { open: 'never' }]],
```

`REPORT_NAME` pozwala każdemu jobowi zapisać wynik pod własną nazwą — `api`, `ui-1`, `ui-2`…
Dzięki temu wyniki z kilku jobów nie nadpisują się nawzajem.

**3. Niech każdy job z testami publikuje swój JUnit.**

W jobie `unit`, pod krokiem `- run: npm run test:unit`, dopisz:

```yaml
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: junit-unit
          path: reports/unit.xml
          retention-days: 1
```

W jobie `test-api` zamień krok `- run: npm run test:api` na:

```yaml
      - run: npm run test:api
        env:
          REPORT_NAME: api

      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: junit-api
          path: reports/api.xml
          retention-days: 1
```

W jobie `test-ui`, w kroku `UI tests`, w sekcji `env:` nad linią `GREP:` dopisz:

```yaml
          REPORT_NAME: ui-${{ matrix.shard }}
```

a na końcu joba `test-ui` dopisz:

```yaml
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: junit-ui-${{ matrix.shard }}
          path: reports/ui-*.xml
          retention-days: 1
```

`if: always()` jest wszędzie z tego samego powodu co w ZADANIU 11: plik z wynikami ma zostać
opublikowany **zwłaszcza** wtedy, gdy testy nie przejdą — właśnie wtedy jest najbardziej potrzebny.

**4. Dodaj wspólny job Test report.** Na końcu sekcji `jobs:` dopisz:

```yaml
  test-report:
    name: Test report
    runs-on: ubuntu-latest
    needs: [unit, test-api, test-ui]
    if: always()
    permissions:
      contents: read
      actions: read
      checks: write
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version-file: .nvmrc

      - name: Collect JUnit reports
        uses: actions/download-artifact@v4
        with:
          pattern: junit-*
          path: reports
          merge-multiple: true

      - name: Publish check run
        uses: dorny/test-reporter@v3
        if: always()
        with:
          name: Test results
          path: reports/*.xml
          reporter: java-junit
          fail-on-error: true
          use-actions-summary: false

      - name: Job summary
        if: always()
        run: node scripts/ci-summary.mjs reports/*.xml
```

| Element | Po co |
|---|---|
| `permissions: checks: write` | `dorny/test-reporter` tworzy check run i bez tego uprawnienia nie może go opublikować. To pierwszy moment w warsztacie, w którym uprawnienia mają bezpośredni wpływ na wynik |
| `pattern: junit-*` | pobiera wyniki ze wszystkich jobów z testami, niezależnie od liczby shardów |
| `merge-multiple: true` | wszystkie pliki JUnit trafiają do jednego katalogu |
| `reporter: java-junit` | parser formatu JUnit XML — nazwa sugeruje Javę, ale działa z każdym poprawnym plikiem JUnit |
| `use-actions-summary: false` | od wersji 3 akcja domyślnie zapisuje wyniki tylko w podsumowaniu joba; to ustawienie każe jej utworzyć osobny check run *Test results* |
| `fail-on-error: true` | gdy jakikolwiek test nie przeszedł, check run *Test results* jest czerwony. Zielony check run z napisem „1 failed” byłby sygnałem, któremu nikt nie powinien ufać. Krok `Job summary` ma `if: always()`, więc tabela powstaje i tak |
| brak `npm ci` | skrypt `ci-summary.mjs` nie ma zależności, więc instalowanie całego projektu byłoby niepotrzebnym kosztem |

**5. Zatwierdź, wypchnij na `main` i sprawdź wyniki bez pobierania.**

```bash
git add vitest.config.ts playwright.config.ts .github/workflows/ci.yml
git commit -m "Publish JUnit results as a check run and job summary"
git push
```

Gdy przebieg się skończy, sprawdź dwa miejsca. Nie pobieraj żadnych artefaktów.

- **Job Summary:** na stronie przebiegu, pod grafem jobów, powinna być tabela *Test results*
  z wierszami `unit`, `api`, `ui-1`, `ui-2` i kolejnych shardów oraz sumą testów,
- **check run:** w zakładce **Actions** po lewej stronie przebiegu (albo na liście kontroli
  commita) powinna być pozycja *Test results* z listą wszystkich testów i ich wynikami.

**6. Sprawdź, jak wygląda wynik przy błędzie.** Przenieś na nową gałąź zmianę w naliczaniu rabatu z ZADANIA 01:

```bash
git checkout -b check-discount
git checkout warsztat/demo/failing-unit -- src/shared/discounts.ts
git commit -m "Discount change to verify"
git push -u origin check-discount
```

Otwórz pull request z `check-discount` do `main`. Sprawdź, bez pobierania czegokolwiek:

- w tabeli Job Summary przy `unit` jest ❌ i liczba błędów,
- w check runie *Test results* widać nazwę testu, który nie przeszedł, i komunikat błędu,
- w zakładce **Files changed** pull requesta adnotacji **nie ma** — test leży w innym pliku niż
  zmiana w `discounts.ts`, więc reporter nie ma czego przypiąć do diffu. Właśnie dlatego
  potrzebny jest check run: pokazuje wynik niezależnie od tego, w którym pliku jest test.

Zapisz w `docs/baseline.md`, ile kliknięć dzieli Cię teraz od nazwy testu z błędem, i porównaj
z ZADANIEM 01. Pull requesta nie scalaj.

**7. Wróć na `main`:**

```bash
git checkout main
```

## Kryteria akceptacji

- [ ] testy jednostkowe, API i UI zapisują wynik w formacie JUnit XML (kroki 1–3)
- [ ] Job Summary pokazuje tabelę z wynikami wszystkich zestawów testów (krok 5)
- [ ] check run *Test results* pokazuje listę testów (krok 5)
- [ ] wyniki są publikowane również wtedy, gdy test kończy się błędem (krok 6)
- [ ] nazwę testu, który nie przeszedł, można znaleźć bez pobierania artefaktów (krok 6)

## Zmierz

| Co | ZADANIE 01 | Po ZADANIU 12 |
|---|---|---|
| Kliknięć do nazwy testu z błędem | ? | ? |
| Czy trzeba coś pobierać | tak | ? |
| Czas joba `Test report` | — | ? |
