# ZADANIE 05 — Artefakt builda zamiast czterech buildów

## Cel

Zbudować aplikację **raz** i przekazać wynik do jobów, które go potrzebują.

## Dlaczego to boli

`needs` przekazuje informację o powodzeniu, ale **nie przekazuje plików**. Job `test-ui`
dostaje tylko sygnał „build się udał" — katalogu `dist/` nie widzi.

W efekcie, po ZADANIU 04:

| Job | Co buduje |
|---|---|
| `build` | aplikację |
| `test-api` | aplikację **jeszcze raz** (przez `webServer`) |
| `test-ui` | aplikację **jeszcze raz** (przez `webServer`) |

Trzy razy to samo. Job `build` w obecnej postaci nie robi więc **nic użytecznego** —
sprawdza tylko, czy kod się kompiluje, a jego wynik ląduje w koszu.

Gorzej: build nadal jest **ukryty** w `webServer` Playwrighta, więc błąd kompilacji
w testach API wygląda jak awaria testu API.

## Zadanie

**1. Niech `build` publikuje wynik** jako artefakt (`actions/upload-artifact@v4`).
Katalogi do zabrania: `dist/`.

**2. Niech `test-api` i `test-ui` pobierają artefakt** (`actions/download-artifact@v4`)
zamiast budować od nowa.

**3. Wyjmij build z `webServer`.** W `playwright.config.ts` polecenie ma być samym
`npm start`, bez `npm run build`.

**4. Zadbaj o lokalne uruchamianie.** Po zmianie z punktu 3 `npx playwright test`
na czystym repo nie zadziała, bo nie ma czego uruchomić. Opisz to w `README.md`
albo dodaj skrypt, który buduje przed testami.

**5. Sprawdź, że fail-fast działa.** Zepsuj kompilację (np. dopisz `const x: number = 'tekst';`
gdziekolwiek w `src/`) i zobacz, gdzie teraz pada pipeline.

## Kryteria akceptacji

- [ ] `build` wgrywa `dist/` jako artefakt
- [ ] `test-api` i `test-ui` pobierają artefakt i **nie budują** aplikacji
- [ ] `webServer` w konfiguracji Playwrighta uruchamia samo `npm start`
- [ ] błąd kompilacji pada w jobie `build`, a joby testowe w ogóle nie startują
- [ ] lokalne uruchomienie testów jest opisane w `README.md`

## Zmierz

| Co | Przed | Po |
|---|---|---|
| Ile razy budowana jest aplikacja | 3 | ? |
| Czas joba `test-ui` | ? | ? |
| Gdzie pada błąd kompilacji | w testach | ? |
| Suma minut całego przebiegu | ? | ? |

<details>
<summary><b>Rozwiązanie</b></summary>

```yaml
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

      - name: Upload build
        uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/
          retention-days: 1

  test-ui:
    name: Testy UI
    runs-on: ubuntu-latest
    needs: build
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version-file: .nvmrc
          cache: npm
      - run: npm ci

      - name: Download build
        uses: actions/download-artifact@v4
        with:
          name: dist
          path: dist/

      # ... cache przeglądarek jak w ZADANIU 03
      - run: npm run test:ui
```

W `playwright.config.ts`:

```ts
  webServer: process.env.BASE_URL
    ? undefined
    : {
        // No build here any more. The application is built once, in its own job, and
        // arrives as an artifact. A compilation error now fails the build job, where it
        // belongs, instead of masquerading as a broken test.
        command: 'npm start',
        url: 'http://localhost:3000/api/health',
        reuseExistingServer: !process.env.CI,
        timeout: 120_000,
      },
```

W `package.json` warto dodać skrót dla pracy lokalnej:

```json
"test:ui:local": "npm run build && playwright test --project=ui-chromium"
```

### `retention-days: 1`

Artefakt builda jest potrzebny przez kilka minut, a domyślnie leżałby **90 dni**.
Przy kilkunastu przebiegach dziennie to zauważalne zużycie miejsca za nic.

</details>

## Pułapki

**Artefakt nie zachowuje uprawnień plików.** `upload-artifact` gubi bit wykonywalności.
Dla `dist/` nie ma to znaczenia, ale gdybyś przekazywał skrypty — miałoby.

**Domyślna retencja to 90 dni.** Warto ją skrócić dla artefaktów roboczych.

**Nazwy artefaktów muszą być unikalne w obrębie przebiegu.** W `upload-artifact@v4` dwa joby
nie mogą wgrać artefaktu o tej samej nazwie. Teraz to nie przeszkadza, ale uderzy w ZADANIU 10,
gdy shardy zaczną wgrywać raporty.

**To jest ten sam wzorzec, co „wdróż i przetestuj".** Job `build` produkuje artefakt,
job testowy go pobiera i uruchamia. Różnica między tym a testowaniem wdrożonego środowiska
sprowadza się do jednej zmiennej — `BASE_URL`. Warto to zobaczyć teraz, bo wracamy do tego
przy okazji rozmowy o CD.

## Do dyskusji

- Job `build` przed tym zadaniem sprawdzał tylko kompilację, a jego wynik szedł do kosza.
  Ile takich jobów widziałeś w prawdziwych projektach?
- Przekazywanie artefaktów kosztuje czas na upload i download. Kiedy taniej jest zbudować
  ponownie, niż przenosić wynik?
- Gdyby `test-api` nie potrzebował aplikacji w ogóle — czy powinien czekać na `build`?
