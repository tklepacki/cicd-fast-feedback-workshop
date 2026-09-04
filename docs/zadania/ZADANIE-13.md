# ZADANIE 13 — Scalanie raportów z shardów

## Cel

Naprawić to, co zepsuło ZADANIE 10. Shardowanie skróciło testy, ale rozbiło raport
na cztery kawałki — a to najczęstszy błąd w prawdziwych projektach.

## Dlaczego to boli

Po wprowadzeniu shardów masz cztery artefakty: `playwright-report-1` do `-4`.
Każdy zna wyłącznie swoją część zestawu.

Żeby odpowiedzieć na pytanie *„ile testów padło?"*, trzeba pobrać cztery archiwa,
rozpakować każde i otworzyć cztery zakładki. Nikt tego nie robi. Ludzie wracają
do czytania surowych logów — czyli do stanu sprzed całego warsztatu.

Doszedł drugi problem: przy trzech przeglądarkach z ZADANIA 11 jest tych raportów **dwanaście**.

## Zadanie

**1. Przełącz reporter na `blob`.** To format pośredni, zaprojektowany do scalania —
w przeciwieństwie do HTML, którego scalić się nie da.

**2. Niech każdy shard wgrywa raport `blob`** pod unikalną nazwą.

**3. Dodaj job `ui-report`**, który po zakończeniu wszystkich shardów pobiera wszystkie
raporty i scala je poleceniem `npx playwright merge-reports`.

**4. Ustaw `if: always()`.** Bez tego job scalający **nie uruchomi się, gdy testy padną** —
czyli dokładnie wtedy, gdy raport jest potrzebny.

**5. Sprawdź na zepsutym branchu:**

```bash
git checkout demo/failing-ui
```

Raport ma pokazywać komplet: 122 przechodzące i 1 padający, w jednym miejscu.

## Kryteria akceptacji

- [ ] shardy wgrywają raporty `blob`, nie HTML
- [ ] job `ui-report` ma `needs: test-ui` i `if: always()`
- [ ] scalony raport obejmuje testy ze **wszystkich** shardów
- [ ] przy padających testach raport nadal powstaje
- [ ] jest **jeden** artefakt z raportem, nie cztery

## Zmierz

| Co | Przed | Po |
|---|---|---|
| Liczba artefaktów z raportem | 4 (lub 12) | ? |
| Kroki potrzebne do zobaczenia wyniku | pobierz ×4, rozpakuj ×4 | ? |
| Czy raport powstaje przy błędzie | ? | ? |
| Czas joba scalającego | — | ? |

<details>
<summary><b>Rozwiązanie</b></summary>

```ts
// playwright.config.ts
reporter: process.env.CI
  ? [['blob'], ['github']]
  : [['list'], ['html', { open: 'never' }]],
```

```yaml
  test-ui:
    # ...
    steps:
      - run: npx playwright test --project=ui-chromium --shard=${{ matrix.shard }}/4

      - name: Upload blob report
        uses: actions/upload-artifact@v4
        # Without `always()` the report is missing precisely when tests fail.
        if: always()
        with:
          name: blob-report-${{ matrix.shard }}
          path: blob-report/
          retention-days: 1

  ui-report:
    name: Raport UI
    runs-on: ubuntu-latest
    needs: test-ui
    # The merge job must run even when shards failed. A report describing a green run
    # is the one nobody needs to read.
    if: always()
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version-file: .nvmrc
          cache: npm
      - run: npm ci

      - name: Download all blob reports
        uses: actions/download-artifact@v4
        with:
          pattern: blob-report-*
          path: all-blob-reports
          merge-multiple: true

      - name: Merge into one HTML report
        run: npx playwright merge-reports --reporter=html ./all-blob-reports

      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: playwright-report
          path: playwright-report/
          retention-days: 7
```

### Dlaczego `blob`, a nie HTML

Raport HTML to gotowa strona z zaindeksowanymi wynikami — dwóch takich nie da się połączyć
w sensowny sposób. `blob` jest formatem pośrednim, stworzonym właśnie po to, żeby
`merge-reports` mógł go złożyć w całość.

### `merge-multiple: true`

Bez tego każdy artefakt trafia do własnego podkatalogu i `merge-reports` widzi cztery
osobne raporty zamiast czterech części jednego.

</details>

## Pułapki

**Brak `if: always()` w jobie scalającym.** Domyślnie job z `needs` nie uruchamia się,
gdy zależność padła. Efekt: raport jest tylko dla zielonych przebiegów. To jest ten sam
błąd, co `upload-artifact` bez `if: always()` w baseline — i równie łatwo go przeoczyć.

**Reporter HTML zamiast `blob` w shardach.** Wtedy nie ma czego scalać, a `merge-reports`
kończy się błędem, który nie wskazuje reportera jako przyczyny.

**Retencja.** Raporty `blob` są potrzebne przez minutę — scalony przez tydzień.
Warto ustawić osobne `retention-days`.

**`needs: test-ui` przy matrixie** czeka na **wszystkie** kombinacje. To jest zamierzone,
ale oznacza, że raport pojawia się dopiero po najwolniejszym shardzie.

## Do dyskusji

- Czy raport powinien powstawać także wtedy, gdy shard został **anulowany** (a nie padł)?
- Job scalający to dodatkowa maszyna i dodatkowe `npm ci` dla kilku sekund pracy.
  Kiedy to się nie opłaca?
- Gdyby raportów było dwanaście (trzy przeglądarki × cztery shardy) — scalać wszystko
  w jeden, czy trzy osobne per przeglądarka?
