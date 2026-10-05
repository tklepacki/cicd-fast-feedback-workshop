# ZADANIE 11 — Scalanie raportów z shardów

## Cel

Naprawić problem, który pojawił się po wprowadzeniu shardowania. Testy wykonują się szybciej,
ale raport rozpadł się na kilka osobnych części.

## Na czym polega problem

Po ZADANIACH 09 i 10 każdy przebieg na `main` tworzy kilka osobnych artefaktów z raportami
Playwrighta — `playwright-report-1`, `-2` … po jednym na shard. Przy czterech shardach są
cztery raporty, przy ośmiu — osiem. Każdy zna wyłącznie swoją część zestawu.

Osoba, która rano sprawdza wynik nocnej regresji, musiałaby pobrać kilka archiwów, rozpakować
każde i przejrzeć kilka raportów, żeby odpowiedzieć na dwa podstawowe pytania: *ile testów nie przeszło
i które*. W praktyce szybko robi się to zbyt niewygodne i ludzie wracają do czytania surowych
logów zamiast korzystać z raportów.

Potrzebujemy jednego raportu z wynikami ze wszystkich shardów.

## Zadanie

Zmieniasz dwa pliki: `playwright.config.ts` i `.github/workflows/ci.yml`. Pozostałe joby zostają
bez zmian.

**1. Zmień reporter używany na CI.** W `playwright.config.ts` znajdź:

```ts
  reporter: [['list'], ['html', { open: 'never' }]],
```

i zamień na:

```ts
  reporter: process.env.CI
    ? [['blob'], ['github']]
    : [['list'], ['html', { open: 'never' }]],
```

| Reporter | Po co |
|---|---|
| `blob` | format pośredni, przygotowany do scalania wyników z kilku shardów. Nie łączymy gotowych raportów HTML — każdy shard zapisuje dane, z których później powstanie jeden wspólny raport |
| `github` | błędy jako adnotacje przy odpowiednich liniach kodu i podsumowanie `N passed / N failed` w logu GitHub Actions |

Lokalnie nic się nie zmienia — nadal korzystasz z reporterów `list` i `html`.

**2. Niech każdy shard publikuje raport `blob`.** W jobie `test-ui`, w ostatnim kroku
(`actions/upload-artifact`), zamień trzy linie `name`, `path` i `retention-days` na:

```yaml
          name: blob-report-${{ matrix.shard }}
          path: blob-report/
          retention-days: 1
```

Każdy shard publikuje teraz własny raport `blob`. Te raporty są potrzebne tylko do chwili scalenia,
więc wystarczy przechowywać je przez jeden dzień.

**3. Dodaj job, który scala raporty.** Na końcu sekcji `jobs:` dopisz:

```yaml
  ui-report:
    name: UI report
    runs-on: ubuntu-latest
    needs: test-ui
    if: always() && needs.test-ui.result != 'skipped'
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
        with:
          name: playwright-report
          path: playwright-report/
          retention-days: 7
```

| Element | Po co |
|---|---|
| `needs: test-ui` | czeka na **wszystkie** shardy — raport może powstać dopiero wtedy, gdy skończy najwolniejszy |
| `if: always()` | job uruchamia się także wtedy, gdy jeden lub kilka shardów zakończyło się błędem; bez tego raport nie powstałby właśnie wtedy, gdy jest najbardziej potrzebny |
| `needs.test-ui.result != 'skipped'` | gdy filtr z ZADANIA 08 całkowicie pominął testy UI, nie ma czego scalać, więc `UI report` też zostaje pominięty |
| `pattern: blob-report-*` | pobiera raporty ze wszystkich shardów, niezależnie od tego, czy było ich dwa, cztery czy osiem |
| `merge-multiple: true` | wszystkie części trafiają do jednego katalogu; bez tego każdy shard ląduje w osobnym podkatalogu, a `merge-reports` szuka plików w jednym |

**4. Zatwierdź zmiany, wypchnij je na `main` i sprawdź raport.**

```bash
git add playwright.config.ts .github/workflows/ci.yml
git commit -m "Merge shard reports into one"
git push
```

Po zakończeniu przebiegu otwórz go w zakładce **Actions**. W sekcji **Artifacts** powinny być
raporty `blob-report-*` ze shardów i jeden końcowy artefakt `playwright-report`. Pobierz
`playwright-report`, rozpakuj i otwórz `index.html`. Raport powinien zawierać wyniki wszystkich
**123** testów, wszystkie zielone.

**5. Sprawdź raport przy błędzie.** Użyj gałęzi `check-catalog` z ZADANIA 09 — ze zmianą
w katalogu, którą wykrywa pełna regresja. Gałąź powstała przed tym zadaniem, więc nadal ma
starszą wersję pipeline'u. Najpierw przenieś na nią aktualne zmiany z `main`:

```bash
git checkout check-catalog
git merge --no-edit main
git push
git checkout main
```

Następnie w zakładce **Actions** wybierz **CI** i kliknij **Run workflow**:

- w **Use workflow from** wybierz `check-catalog`,
- w **UI test scope** wybierz `all`,
- uruchom workflow.

Jeden shard powinien zakończyć się błędem, a job `UI report` — **mimo to** się uruchomić
i utworzyć scalony raport. Pobierz go i sprawdź, że w jednym miejscu pokazuje komplet wyników:
**122 zielone i 1 czerwony**. Otwórz czerwony test i sprawdź, co raport mówi o przyczynie błędu.

**6. Sprawdź pull request bez zmian w UI.**

```bash
git checkout -b check-report-readme
```

Dopisz linię do pliku — polecenie zależy od systemu.

macOS, Linux albo Git Bash na Windowsie:

```bash
echo "Kolejna drobna poprawka." >> README.md
```

Windows, PowerShell:

```powershell
Add-Content README.md "Kolejna drobna poprawka."
```

```bash
git commit -am "Update README"
git push -u origin check-report-readme
git checkout main
```

Otwórz pull request z `check-report-readme` do `main`. Zmiana dotyczy tylko README, więc
`UI tests` są pominięte. `UI report` też powinien mieć status *Skipped* (szara ikona), a nie być
czerwony — w tym przebiegu po prostu nie ma raportów do scalenia. Pull requesta nie scalaj.

## Kryteria akceptacji

- [ ] shardy publikują raporty `blob` zamiast osobnych raportów HTML (krok 2)
- [ ] na `main` powstaje **jeden** wspólny raport ze wszystkimi 123 testami (krok 4)
- [ ] gdy jeden test nie przechodzi, wspólny raport nadal powstaje i pokazuje 122 zielone i 1 czerwony (krok 5)
- [ ] gdy testy UI są pominięte, `UI report` też jest pominięty (krok 6)

## Zmierz

| Co | Przed | Po |
|---|---|---|
| Liczba raportów, które trzeba otworzyć, żeby zobaczyć pełny wynik | 8 (albo 4) | ? |
| Czy raport powstaje przy błędzie | ? | ? |
| Czas joba `UI report` | — | ? |
