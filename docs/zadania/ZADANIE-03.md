# ZADANIE 03 — Szybkie kontrole najpierw i cache

## Cel

Największy pojedynczy zysk w całym dniu. Dwie zmiany:

1. **Dodać kontrole, których w pipelinie nie ma** — lint, typecheck i jawny build.
2. **Ustawić je przed testami** i zacache'ować to, co da się cache'ować.

Po tym zadaniu błąd lintu wyjdzie po kilkudziesięciu sekundach zamiast **nigdy**.

## Dlaczego to boli

Z ZADANIA 01 wiesz, że branch `demo/failing-lint` **przechodzi**. To nie jest kwestia szybkości —
pipeline po prostu nie sprawdza tej rzeczy. Tak samo nie ma typechecku.

Build też formalnie się dzieje, ale **jest ukryty**: uruchamia go `webServer` w konfiguracji
Playwrighta, w środku kroku z testami UI. Błąd kompilacji objawia się więc jako błąd testu,
i szukasz go w złym miejscu.

Do tego kolejność jest odwrotna do kosztu: **najdroższe testy idą pierwsze, najtańsze ostatnie.**

| Krok | Czas | Pozycja |
|---|---|---|
| Testy UI | 2:27 | pierwszy |
| Testy API | 19 s | drugi |
| Testy jednostkowe | 1 s | ostatni |

## Zadanie

**1. Dodaj trzy kroki przed testami**, w tej kolejności: `npm run lint`, `npm run typecheck`,
`npm run build`.

**2. Przestaw testy** tak, żeby szły od najtańszych: jednostkowe → API → UI.

**3. Zacache'uj zależności npm** przez wbudowany mechanizm `actions/setup-node`.

**4. Zacache'uj przeglądarki Playwrighta.** To **osobny** cache, w innej lokalizacji
(`~/.cache/ms-playwright`) i wymaga własnego klucza. Klucz musi zawierać **wersję Playwrighta** —
inaczej po podbiciu zależności dostaniesz z cache stare przeglądarki.

**5. Instaluj tylko jedną przeglądarkę.** Pipeline uruchamia testy w Chromium,
a `npx playwright install --with-deps` ściąga wszystkie trzy.

**6. Zmierz na `demo/failing-lint`**, po ilu sekundach pipeline teraz mówi o błędzie.

## Kryteria akceptacji

- [ ] pipeline zawiera kroki `lint`, `typecheck` i `build`
- [ ] kolejność: lint → typecheck → build → unit → API → UI
- [ ] `demo/failing-lint` **pada** (przed tym zadaniem przechodził)
- [ ] pada w mniej niż minutę od startu przebiegu
- [ ] drugi przebieg pod rząd jest zauważalnie krótszy od pierwszego (cache działa)
- [ ] w logach kroku instalacji przeglądarek widać trafienie w cache

## Zmierz

| Co | Przed | Po |
|---|---|---|
| Czas do informacji o błędzie lintu | **nigdy** | ? |
| `npm ci` | 6 s | ? |
| Instalacja przeglądarek, pierwszy przebieg | 52 s | ? |
| Instalacja przeglądarek, drugi przebieg | 52 s | ? |
| Całkowity czas | 3:58 | ? |

<details>
<summary><b>Rozwiązanie</b></summary>

```yaml
jobs:
  test:
    runs-on: ubuntu-latest

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

      # Read the Playwright version from the lockfile so the cache key changes the moment
      # the dependency is bumped. Without the version in the key, a bumped Playwright would
      # be served stale browsers from cache and fail in ways that make no sense.
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
        run: npx playwright install --with-deps chromium

      # System dependencies live outside ~/.cache/ms-playwright, so they are not covered by
      # the cache above and have to be installed even on a cache hit.
      - name: Install browser system dependencies
        if: steps.pw-cache.outputs.cache-hit == 'true'
        run: npx playwright install-deps chromium

      # Cheapest checks first. Each one can fail the run before anything expensive starts.
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

### Wyniki referencyjne

| Co | Przed | Po |
|---|---|---|
| Czas do informacji o błędzie lintu | nigdy | **~35 s** |
| Instalacja przeglądarek, pierwszy przebieg | 52 s | 30 s (tylko Chromium) |
| Instalacja przeglądarek, kolejne przebiegi | 52 s | **~8 s** (z cache) |
| `npm ci` z cache | 6 s | 4 s |

**Uwaga o `npm ci`:** cache npm oszczędza tu około dwóch sekund, bo instalacja i tak trwała
sześć. To dobry moment, żeby zauważyć, że **cache'owanie rzeczy taniej niczego nie daje** —
prawdziwy zysk siedział w przeglądarkach.

</details>

## Pułapki

**Klucz cache bez wersji.** `key: playwright-${{ runner.os }}` wygląda niewinnie i działa —
do pierwszego podbicia Playwrighta. Wtedy dostajesz z cache przeglądarki w starej wersji,
a testy zaczynają padać w sposób, którego nie da się powiązać ze zmianą.

**Zapomniane zależności systemowe.** `~/.cache/ms-playwright` zawiera przeglądarki, ale
biblioteki systemowe (czcionki, kodeki, GTK) instaluje `--with-deps` poza tym katalogiem.
Przy trafieniu w cache trzeba je doinstalować osobno przez `playwright install-deps`.

**Cache jako proteza.** Cache przyspiesza, ale **nie zamraża środowiska**. `ubuntu-latest`
nadal przesuwa się pod spodem i pewnego dnia zmieni renderowanie czcionek. Wrócimy do tego.

## Do dyskusji

- Kolejność „od najtańszych" jest oczywista, gdy się ją zobaczy. Dlaczego więc tak wiele
  pipeline'ów jej nie ma?
- Cache dał największy zysk tam, gdzie krok trwał najdłużej. Czy to zawsze prawda?
- Lint i typecheck sprawdzają różne rzeczy, ale oba są tanie. Czy powinny być osobnymi
  krokami, czy jednym? (do tego wrócimy w ZADANIU 04)
