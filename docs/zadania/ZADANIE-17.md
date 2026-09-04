# ZADANIE 17 — Composite action: DRY w workflow

## Cel

Zwinąć powtórzony setup do jednej lokalnej akcji. Po szesnastu zadaniach `ci.yml` powtarza
ten sam wstęp w siedmiu jobach.

## Dlaczego to boli

Każdy job zaczyna się identycznie:

```yaml
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version-file: .nvmrc
          cache: npm
      - run: npm ci
```

Siedem jobów, siedem kopii. To nie jest problem estetyczny.

**Zmiana wymaga siedmiu edycji.** Podbicie `setup-node` do v5 albo dodanie kroku
z cache'em przeglądarek to siedem miejsc — i wystarczy jedno przeoczone, żeby jeden job
zachowywał się inaczej niż reszta.

**Rozjazd jest niewidoczny.** Job, w którym ktoś zapomniał `cache: npm`, działa poprawnie,
tylko wolniej. Nikt tego nie zauważy przez miesiące.

## Zadanie

**1. Utwórz lokalną akcję** `.github/actions/setup/action.yml` typu `composite`.

**2. Przenieś do niej** setup Node, instalację zależności i cache przeglądarek.

**3. Dodaj parametry** — na przykład `install-browsers` (domyślnie `false`), żeby joby
niepotrzebujące przeglądarki nie płaciły za ich przygotowanie.

**4. Podmień siedem powtórzeń** na `- uses: ./.github/actions/setup`.

**5. Zauważ, czego nie da się zwinąć** — i zrozum dlaczego.

## Kryteria akceptacji

- [ ] `.github/actions/setup/action.yml` istnieje i ma `using: composite`
- [ ] joby używają akcji zamiast powtarzać kroki
- [ ] akcja przyjmuje parametr sterujący instalacją przeglądarek
- [ ] `ci.yml` jest zauważalnie krótszy
- [ ] wszystko nadal działa
- [ ] potrafisz wyjaśnić, dlaczego `checkout` został poza akcją

## Zmierz

| Co | Przed | Po |
|---|---|---|
| Linii w `ci.yml` | ? | ? |
| Miejsc do zmiany przy podbiciu `setup-node` | 7 | ? |
| Czas przebiegu | ? | ? |

<details>
<summary><b>Rozwiązanie</b></summary>

`.github/actions/setup/action.yml`:

```yaml
name: Setup
description: Node, dependencies and optionally Playwright browsers

inputs:
  install-browsers:
    description: Install Playwright browsers
    required: false
    default: 'false'

runs:
  using: composite
  steps:
    - uses: actions/setup-node@v4
      with:
        node-version-file: .nvmrc
        cache: npm

    - run: npm ci
      shell: bash

    - name: Resolve Playwright version
      if: inputs.install-browsers == 'true'
      id: pw
      run: echo "version=$(node -p "require('@playwright/test/package.json').version")" >> "$GITHUB_OUTPUT"
      shell: bash

    - name: Cache browsers
      if: inputs.install-browsers == 'true'
      id: pw-cache
      uses: actions/cache@v4
      with:
        path: ~/.cache/ms-playwright
        key: playwright-${{ runner.os }}-${{ steps.pw.outputs.version }}

    - name: Install browsers
      if: inputs.install-browsers == 'true' && steps.pw-cache.outputs.cache-hit != 'true'
      run: npx playwright install --with-deps chromium
      shell: bash
```

Użycie:

```yaml
  quality:
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/actions/setup
      - run: npm run lint
      - run: npm run typecheck

  test-ui:
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/actions/setup
        with:
          install-browsers: 'true'
      - run: npm run test:ui
```

### Dlaczego `checkout` zostaje poza akcją

**Lokalna akcja jest plikiem w repozytorium.** Żeby GitHub mógł ją wczytać, repozytorium
musi być już pobrane. `checkout` musi więc poprzedzać `uses: ./.github/actions/setup` —
akcja nie może zwinąć kroku, który jest warunkiem jej własnego istnienia.

### `shell: bash` jest obowiązkowy

W akcji `composite` każdy krok `run` musi jawnie podać `shell`. Pominięcie kończy się
błędem walidacji, którego komunikat nie wskazuje przyczyny wprost.

### Composite action a reusable workflow

| | Composite action | Reusable workflow |
|---|---|---|
| Co dzieli | **kroki** wewnątrz joba | **całe joby** |
| Gdzie leży | `.github/actions/*/action.yml` | `.github/workflows/*.yml` |
| Wywołanie | `uses:` w kroku | `uses:` na poziomie joba |
| Widzi sekrety | dziedziczy z joba | wymaga jawnego przekazania |
| Kiedy | powtórzony setup | powtórzony **pipeline** w wielu repozytoriach |

Tu potrzebny jest composite: powtarza się setup, nie cały pipeline.

</details>

## Pułapki

**Brak `shell:`** — najczęstszy błąd przy pierwszej akcji composite.

**Próba zwinięcia `checkout`.** Nie zadziała, bo akcji jeszcze nie ma na dysku.

**Nadmierna parametryzacja.** Akcja z ośmioma wejściami jest trudniejsza do zrozumienia
niż powtórzone cztery linijki. DRY ma granicę.

**Wersjonowanie.** Lokalna akcja jest zawsze w wersji z bieżącego commita. To zaleta
(spójność) i wada (brak możliwości przypięcia starszej wersji).

## Do dyskusji

- Trzy powtórzenia zwykle jeszcze nie bolą, siedem już tak. Gdzie jest Twoja granica?
- Gdyby ten sam pipeline miał działać w pięciu repozytoriach — composite action
  wystarczy, czy potrzebny jest reusable workflow?
- Lokalna akcja zmienia się razem z repozytorium. Kiedy to jest zaleta, a kiedy problem?
