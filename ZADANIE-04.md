# ZADANIE 04 — Rozbicie na joby i `needs`

## Cel

Rozbić jeden długi job na kilka, które mogą biec **równolegle**, i opisać zależności między
nimi przez `needs`.

## Na czym polega problem

Po ZADANIU 03 kolejność kontroli jest już rozsądna, ale wszystkie nadal wykonują się po kolei w jednym jobie. Ma to trzy konsekwencje.

**Rzeczy niezależne czekają na siebie bez potrzeby.** Lint, testy jednostkowe i build nie potrzebują swoich wyników nawzajem, a mimo to w jednym jobie muszą wykonywać się jeden po drugim. Lint czeka nawet na instalację przeglądarek, której w ogóle nie potrzebuje.

**Na pull requeście trudno od razu zobaczyć, co się zepsuło.** Jest tylko jedna kontrola o nazwie `test` — zielona albo czerwona. Żeby sprawdzić, czy problem dotyczy lintu, buildu, testów API czy testów UI, trzeba otworzyć przebieg i zajrzeć do logów.

**Trudniej sterować poszczególnymi kontrolami niezależnie.** Jeśli wszystko znajduje się w jednym jobie, nie możemy łatwo zdecydować, że konkretna grupa testów ma mieć inne warunki uruchamiania albo inną rolę w ochronie pull requesta.

## Zadanie

Wszystkie zmiany robisz w pliku `.github/workflows/ci.yml`, w sekcji `jobs:`. Sekcje `on:`
i `concurrency:` z ZADANIA 02 zostają bez zmian.

**1. Zanim cokolwiek zmienisz, odpowiedz sobie na cztery pytania** i zapisz odpowiedzi
w `docs/baseline.md`:

- czy lint, testy jednostkowe i build zależą od siebie, czy mogą wystartować równolegle?
- czy testy API i UI powinny wystartować, jeśli aplikacja się nie buduje?
- czy warto uruchamiać drogie testy API i UI, jeśli lint albo testy jednostkowe już wykryły problem?
- na co testy API i UI czekają, bo muszą, a na co tylko dlatego, że tak zdecydowaliśmy?

**2. Zastąp całą sekcję `jobs:`** (od linii `jobs:` do końca pliku) pięcioma jobami:

```yaml
jobs:
  quality:
    name: Lint and typecheck
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version-file: .nvmrc
          cache: npm
      - run: npm ci
      - run: npm run lint
      - run: npm run typecheck

  unit:
    name: Unit tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version-file: .nvmrc
          cache: npm
      - run: npm ci
      - run: npm run test:unit

  build:
    name: Build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version-file: .nvmrc
          cache: npm
      - run: npm ci
      - run: npm run build

  test-api:
    name: API tests
    runs-on: ubuntu-latest
    needs: [build, quality, unit]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version-file: .nvmrc
          cache: npm
      - run: npm ci
      - run: npm run test:api

  test-ui:
    name: UI tests
    runs-on: ubuntu-latest
    needs: [build, quality, unit]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version-file: .nvmrc
          cache: npm
      - run: npm ci

      - name: Resolve Playwright version
        id: pw
        run: echo "version=$(node -p "require('@playwright/test/package.json').version")" >> "$GITHUB_OUTPUT"

      - name: Cache Playwright browsers
        id: pw-cache
        uses: actions/cache@v4
        with:
          path: ~/.cache/ms-playwright
          key: playwright-${{ runner.os }}-${{ steps.pw.outputs.version }}

      - name: Install Playwright browsers
        if: steps.pw-cache.outputs.cache-hit != 'true'
        run: npx playwright install chromium

      - run: npm run test:ui

      - uses: actions/upload-artifact@v4
        with:
          name: playwright-report
          path: playwright-report/
```

**3. Porównaj z odpowiedziami z punktu 1.** Każdy job to osobna maszyna, więc:

| Job | `needs` | Dlaczego |
|---|---|---|
| `quality`, `unit`, `build` | brak | są od siebie niezależne i mogą wystartować równolegle |
| `test-api`, `test-ui` | `build`, `quality`, `unit` | uruchamiamy je dopiero wtedy, gdy aplikacja się buduje i tańsze kontrole nie wykryły wcześniej problemu. To nie są zależności techniczne — to świadoma bramka, która ma ograniczyć uruchamianie droższych testów |

Przeglądarki instaluje tylko `test-ui`, bo tylko on ich używa.

Każdy job działa na osobnej maszynie. `needs: build` nie przekazuje więc do testów plików utworzonych przez job `Build` — określa jedynie kolejność uruchamiania. Testy API i UI nadal budują aplikację we własnych jobach przez `webServer` z `playwright.config.ts`. To nie jest pomyłka. W następnym zadaniu wrócimy do kosztu tej duplikacji.

**4. Zatwierdź, wypchnij na `main` i obejrzyj graf.**

```bash
git add .github/workflows/ci.yml
git commit -m "Split the pipeline into jobs"
git push
```

Otwórz przebieg w zakładce **Actions**. Na górze jest graf jobów. Sprawdź, że:

- `Lint and typecheck`, `Unit tests` i `Build` startują jednocześnie,
- `API tests` i `UI tests` czekają, aż wszystkie trzy się skończą.

**5. Zmierz czas i koszt.** Gdy przebieg się skończy, zapisz w `docs/baseline.md`:

- **czas całego przebiegu** — na stronie przebiegu, pole *Total duration*,
- **sumę czasów wszystkich jobów** — po lewej **Usage**, pole z łącznym czasem jobów.

Porównaj z przebiegiem z ZADANIA 03.

**6. Sprawdź, jak wygląda to na pull requeście.** Zmiana w koszyku jeszcze raz, tym razem
na nowym pipelinie:

```bash
git checkout -b check-cart-2
git checkout warsztat/demo/failing-lint -- src/shared/cart.ts
git commit -m "Cart change to verify"
git push -u origin check-cart-2
```

Otwórz pull request z `check-cart-2` do `main` (**Compare & pull request** →
**Create pull request**). Na dole strony pull requesta jest lista kontroli. Sprawdź, że widać pięć osobnych kontroli: na czerwono jest `Lint and typecheck`, a `API tests` i `UI tests` są **pominięte** — nie wystartowały, ponieważ jedna z wymaganych wcześniejszych kontroli zakończyła się błędem. Dzięki temu nie uruchamiamy kosztownych testów, gdy problem został już wykryty wcześniej. To realizuje zasadę fail fast: kończymy pracę możliwie wcześnie, gdy dalsze kontrole nie mają już sensu.

Zapisz, po ilu sekundach od startu lint zgłosił błąd.

Pull requesta nie scalaj. Pull request z ZADANIA 03 (`check-cart`) możesz zamknąć.

**7. Wróć na `main`:**

```bash
git checkout main
```

## Kryteria akceptacji

- [ ] pipeline ma pięć osobnych jobów (krok 2)
- [ ] `Lint and typecheck`, `Unit tests` i `Build` startują jednocześnie (krok 4)
- [ ] `API tests` i `UI tests` uruchamiają się dopiero po pomyślnym zakończeniu `Build`, `Lint and typecheck` oraz `Testów jednostkowych` (krok 4)
- [ ] na pull requeście widać pięć kontroli z nazwami jobów, a nie jedno `test` (krok 6)
- [ ] zmiana w koszyku zatrzymuje się na `Lint and typecheck`, a testy API i UI w ogóle nie startują (krok 6)

## Zmierz

| Co | Po ZADANIU 03 | Po ZADANIU 04 |
|---|---|---|
| Czas całego przebiegu | ? | ? |
| **Suma** czasów wszystkich jobów | ? | ? |
| Czas do informacji o błędzie lintu | ? | ? |
| Liczba kontroli widocznych na pull requeście | 1 | ? |
