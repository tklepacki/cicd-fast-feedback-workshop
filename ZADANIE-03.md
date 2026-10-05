# ZADANIE 03 — Szybkie kontrole najpierw i cache

## Cel

Dodać do pipeline’u brakujące kontrole, uruchamiać je przed testami oraz zacache’ować elementy, które najbardziej wpływają na czas przebiegu.

## Na czym polega problem

Pamiętasz zmianę w koszyku z ZADANIA 01, czyli `demo/failing-lint`? Łamie ona reguły lintu ustalone przez zespół, a mimo to pipeline przepuścił ją na zielono.

To nie jest problem z szybkością działania pipeline’u. Ta kontrola po prostu w ogóle się w nim nie znajduje. Tak samo jest ze sprawdzaniem typów.

Build również się wykonuje, ale jest ukryty. Uruchamia go `webServer` z konfiguracji Playwrighta: raz w kroku z testami API i drugi raz w kroku z testami UI. W efekcie błąd kompilacji wygląda jak błąd testów, więc informacji o problemie szukasz w niewłaściwym miejscu.

Jest jeszcze jeden problem. Przy każdym przebiegu pipeline od nowa pobiera zależności npm oraz wszystkie trzy przeglądarki Playwrighta, mimo że nasze testy korzystają wyłącznie z Chromium.

## Zadanie

Wszystkie zmiany wykonujesz w pliku `.github/workflows/ci.yml`, w sekcji `steps:` joba `test`. Sekcje `on:` i `concurrency:`, które zostały zmienione w ZADANIU 02, pozostają bez zmian.

**1. Dodaj cache dla zależności npm.** W kroku `Set up Node` dopisz `cache: npm`:

```yaml
      - name: Set up Node
        uses: actions/setup-node@v4
        with:
          node-version-file: .nvmrc
          cache: npm
```

Dzięki temu npm nie będzie przy każdym przebiegu pobierał wszystkich zależności od zera.

**2. Dodaj cache dla przeglądarek Playwrighta.** Bezpośrednio pod krokiem `Install dependencies` dodaj dwa nowe kroki:

```yaml
      - name: Resolve Playwright version
        id: pw
        run: echo "version=$(node -p "require('@playwright/test/package.json').version")" >> "$GITHUB_OUTPUT"

      - name: Cache Playwright browsers
        id: pw-cache
        uses: actions/cache@v4
        with:
          path: ~/.cache/ms-playwright
          key: playwright-${{ runner.os }}-${{ steps.pw.outputs.version }}
```

Przeglądarki Playwrighta są przechowywane w innym miejscu niż zależności npm, dlatego potrzebują osobnego cache.

Klucz cache zawiera wersję Playwrighta. Jeśli wersja zostanie zmieniona, zmieni się również klucz i pipeline pobierze właściwą wersję przeglądarki zamiast korzystać ze starego cache.

**3. Instaluj przeglądarkę tylko wtedy, gdy nie ma jej w cache.** Zastąp dotychczasowy krok `Install Playwright browsers` następującym:

```yaml
      - name: Install Playwright browsers
        if: steps.pw-cache.outputs.cache-hit != 'true'
        run: npx playwright install chromium
```

Od tego momentu pipeline instaluje tylko Chromium i robi to wyłącznie wtedy, gdy przeglądarka nie została znaleziona w cache. Jeśli cache zostanie trafiony, ten krok zostanie pominięty.

Nie musisz instalować dodatkowych bibliotek systemowych. Te, których potrzebuje Chromium, są już dostępne na runnerze `ubuntu-latest`.

**4. Dodaj lint, sprawdzanie typów i build przed testami.** Pod krokami z punktu 3 dodaj:

```yaml
      - name: Lint
        run: npm run lint

      - name: Typecheck
        run: npm run typecheck

      - name: Build
        run: npm run build
```

Chodzi o to, żeby szybkie kontrole wykonywały się przed testami. Jeśli kod nie przechodzi lintu, nie kompiluje się albo ma błędy typów, nie ma sensu czekać na testy API i UI.

Po wykonaniu punktów 1–4 sekcja `steps:` powinna wyglądać tak:

```yaml
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Node
        uses: actions/setup-node@v4
        with:
          node-version-file: .nvmrc
          cache: npm

      - name: Install dependencies
        run: npm ci

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

      - name: Lint
        run: npm run lint

      - name: Typecheck
        run: npm run typecheck

      - name: Build
        run: npm run build

      - name: Unit tests
        run: npm run test:unit

      - name: API tests
        run: npm run test:api

      - name: UI tests
        run: npm run test:ui

      - name: Upload Playwright report
        uses: actions/upload-artifact@v4
        with:
          name: playwright-report
          path: playwright-report/
```

**5. Zatwierdź zmiany, wypchnij je na `main` i zmierz pierwszy przebieg.**

```bash
git add .github/workflows/ci.yml
git commit -m "Run fast checks first, cache dependencies and browsers"
git push
```

Gdy przebieg się zakończy, zapisz w `docs/baseline.md`:

- czas kroku `Install dependencies`,
- czas kroku `Install Playwright browsers`,
- całkowity czas przebiegu.

To będzie wynik pierwszego uruchomienia po zmianach.

**6. Sprawdź, czy cache działa.** Otwórz zakończony przebieg w zakładce **Actions** i kliknij **Re-run all jobs**. W drugim przebiegu sprawdź trzy rzeczy:

- w logu kroku `Cache Playwright browsers` powinien pojawić się komunikat `Cache restored from key`,
- krok `Install Playwright browsers` powinien zostać pominięty i mieć szarą ikonę,
- cały przebieg powinien być o kilka sekund krótszy. Większej różnicy nie będzie, bo najdłużej trwają testy UI, a nimi zajmiemy się później.

Zapisz nowe czasy obok wyników z pierwszego przebiegu i porównaj je.

**7. Sprawdź zmianę w koszyku.** Utwórz nową gałąź na podstawie `main`, przenieś na nią zmianę z `demo/failing-lint` i otwórz pull request:

```bash
git checkout -b check-cart
git checkout warsztat/demo/failing-lint -- src/shared/cart.ts
git commit -m "Cart change to verify"
git push -u origin check-cart
```

Na stronie repozytorium kliknij **Compare & pull request** przy gałęzi `check-cart`, a następnie **Create pull request**.

W zakładce **Actions** otwórz przebieg uruchomiony dla tego pull requesta. Tym razem pipeline powinien zatrzymać zmianę na kroku `Lint`. Zapisz, po ilu sekundach od startu przebiegu pojawił się czerwony sygnał.

Dlaczego robimy to w ten sposób, zamiast po prostu wypchnąć branch demo?

- Od ZADANIA 02 push na gałąź inną niż `main` nie uruchamia pipeline’u. Potrzebny jest pull request.
- Branch demo zawiera własną, wyjściową wersję `ci.yml`, w której nie ma jeszcze lintu. Zmiana musi więc trafić na gałąź utworzoną z aktualnego `main`, żeby przebieg korzystał z nowej wersji pipeline’u.
- Remote `warsztat` jest już dostępny, ponieważ został dodany w ZADANIU 01.

Pull requesta nie scalaj.

**8. Wróć na `main`:**

```bash
git checkout main
```

## Kryteria akceptacji

- [ ] pipeline ma kroki `Lint`, `Typecheck` i `Build` przed testami (krok 4)
- [ ] w drugim przebiegu przeglądarki pochodzą z cache, a cały przebieg jest krótszy (krok 6)
- [ ] zmiana w koszyku zatrzymuje się na kroku `Lint` (krok 7)
- [ ] informacja o błędzie lintu pojawia się w mniej niż minutę od startu przebiegu (krok 7)

## Zmierz

| Co | Przed | Po |
|---|---|---|
| Czas do informacji o błędzie lintu | **nigdy** | ? |
| `Install dependencies` | 6 s | ? |
| Instalacja przeglądarek, pierwszy przebieg | 18 s | ? |
| Instalacja przeglądarek, drugi przebieg | 18 s | ? |
| Cały przebieg | 3:21 | ? |
