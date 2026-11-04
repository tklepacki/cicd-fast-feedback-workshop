# ZADANIE 05 — Artefakt builda zamiast trzech buildów

## Cel

Zbudować aplikację **raz** i przekazać wynik do jobów, które go potrzebują.

## Na czym polega problem

`needs` przekazuje informację o tym, czy poprzedni job zakończył się powodzeniem, ale **nie przekazuje między jobami plików**. Job `test-ui` dostaje więc informację „build się udał”, ale nie widzi katalogu `dist/`.

W efekcie po ZADANIU 04 wygląda to tak:

| Job | Co buduje |
|---|---|
| `build` | aplikację |
| `test-api` | aplikację **jeszcze raz**, przez `webServer` Playwrighta |
| `test-ui` | aplikację **jeszcze raz**, przez `webServer` Playwrighta |

Czyli tę samą aplikację budujemy trzy razy. Job `build` sprawdza tylko, czy kod się kompiluje, a wynik tego buildu nie jest później wykorzystywany.

Jest też drugi problem. Każdy job testowy buduje aplikację osobno, na innej maszynie. Zwykle wynik będzie taki sam, ale nie ma gwarancji, że zawsze tak będzie. Testy API i UI sprawdzają więc dwie osobno zbudowane kopie aplikacji, a żadna z nich nie jest tą, którą wcześniej zbudował job `build`.

## Zadanie

Zmieniasz trzy pliki: `.github/workflows/ci.yml`, `playwright.config.ts` i `package.json`. Sekcje `on:` i `concurrency:` z ZADANIA 02 oraz pozostałe joby z ZADANIA 04 zostają bez zmian.

**1. Niech `build` publikuje wynik jako artefakt.** W jobie `build`, pod krokiem `- run: npm run build`, dopisz:

```yaml
      - name: Upload build
        uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/
          retention-days: 1
```

`retention-days: 1` skraca czas przechowywania artefaktu do jednego dnia. Potrzebujemy go tylko przez kilka minut, a domyślnie byłby przechowywany przez 90 dni.

**2. Niech `test-api` pobiera artefakt.** W jobie `test-api`, pod krokiem `- run: npm ci`, dopisz:

```yaml
      - name: Download build
        uses: actions/download-artifact@v4
        with:
          name: dist
          path: dist/
```

**3. Niech `test-ui` również pobiera artefakt.** W jobie `test-ui` dodaj ten sam krok `Download build` bezpośrednio nad krokiem `- run: npm run test:ui`.

**4. Usuń build z `webServer`.** W pliku `playwright.config.ts` znajdź:

```ts
        command: 'npm run build && npm start',
```

i zamień na:

```ts
        command: 'npm start',
```

Od tego momentu testy uruchamiają aplikację pobraną jako artefakt, zamiast budować ją ponownie we własnym jobie.

**5. Zadbaj o uruchamianie testów lokalnie.** Po zmianie z punktu 4 polecenie `npm run test:ui` uruchomione na czystym repozytorium przestanie działać, ponieważ nie będzie wcześniej zbudowanej aplikacji.

W `package.json`, w sekcji `scripts`, pod linią `"verify": ...` dodaj dwa skróty. Pamiętaj o przecinku na końcu poprzedniej linii.

```json
    "test:ui:local": "npm run build && playwright test --project=ui-chromium",
    "test:api:local": "npm run build && playwright test --project=api"
```

Sprawdź lokalnie, czy wszystko działa:

```bash
npm run test:api:local
```

**6. Zatwierdź zmiany, wypchnij je na `main` i sprawdź przebieg.**

```bash
git add .github/workflows/ci.yml playwright.config.ts package.json
git commit -m "Build once, share the artifact with test jobs"
git push
```

W zakładce **Actions** otwórz nowy przebieg i sprawdź dwie rzeczy:

- na stronie przebiegu, w sekcji **Artifacts**, znajduje się artefakt `dist`,
- w jobach `API tests` i `UI tests` pojawił się krok `Download build`, a w logach testów aplikacja nie jest już ponownie budowana.

Zapisz w `docs/baseline.md` czas joba `UI tests` oraz sumę czasów wszystkich jobów z sekcji **Usage**. Porównaj wyniki z ZADANIEM 04.

**7. Sprawdź, czy błąd builda nadal zatrzymuje testy.** Utwórz gałąź ze zmianą, która przechodzi lint i sprawdzanie typów, ale powoduje błąd podczas budowania frontendu. Dodamy import pliku ze stylami, którego nie ma w repozytorium:

```bash
git checkout -b check-build
```

Dopisz linię do pliku — polecenie zależy od systemu.

macOS, Linux albo Git Bash na Windowsie:

```bash
echo "import './missing-styles.css';" >> src/web/main.tsx
```

Windows, PowerShell:

```powershell
Add-Content src/web/main.tsx "import './missing-styles.css';"
```

```bash
git commit -am "Import a stylesheet that is not in the repository"
git push -u origin check-build
```

Otwórz pull request z `check-build` do `main`. Na liście kontroli sprawdź, że:

- `Lint and typecheck` oraz `Unit tests` są zielone — te kontrole nie wykrywają tego błędu,
- `Build` jest czerwony, a w jego logu widać, którego pliku brakuje,
- `API tests` i `UI tests` są pominięte — mają szarą ikonę i w ogóle nie wystartowały.

Pull requesta nie scalaj.

**8. Wróć na `main`:**

```bash
git checkout main
```

## Kryteria akceptacji

- [ ] `build` publikuje `dist/` jako artefakt (kroki 1 i 6)
- [ ] `test-api` i `test-ui` pobierają artefakt i nie budują aplikacji ponownie (kroki 2, 3 i 6)
- [ ] `webServer` uruchamia wyłącznie `npm start` (krok 4)
- [ ] `npm run test:api:local` działa lokalnie (krok 5)
- [ ] błąd builda zatrzymuje przebieg na jobie `Build`, a joby testowe nie startują (krok 7)

## Zmierz

| Co | Po ZADANIU 04 | Po ZADANIU 05 |
|---|---|---|
| Ile razy budowana jest aplikacja | 3 | ? |
| Czas joba `UI tests` | ? | ? |
| Suma czasów wszystkich jobów | ? | ? |
