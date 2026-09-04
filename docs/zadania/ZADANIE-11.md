# ZADANIE 11 — Matrix jako mechanizm ogólny

## Cel

Zobaczyć, że `matrix` to nie jest „mechanizm do shardowania". W ZADANIU 10 użyliśmy go
do podziału jednego zestawu na maszyny — teraz użyjemy tego samego narzędzia do czegoś
zupełnie innego, i w dodatku **z drugim wymiarem**.

## Dlaczego to boli

Testy UI uruchamiamy wyłącznie w Chromium. Aplikacja działa w trzech silnikach i nikt
nie sprawdza dwóch pozostałych.

Naturalny odruch to uruchomić wszystko wszędzie. To jednak **potroiłoby** liczbę jobów
i zużycie minut, dając informację, która na pull requeście prawie nigdy nie jest potrzebna:
różnice między silnikami to rzadka klasa błędów, a nie codzienność.

Do tego, gdyby zostawić w warsztacie samo ZADANIE 10, wyszedłbyś z przekonaniem,
że `matrix` **służy do** shardowania. Nie służy — shardowanie to jedno z jego zastosowań.

## Zadanie

**1. Dodaj drugi wymiar `browser`** do istniejącego matrixa z shardami.

**2. Niech wymiar będzie zależny od zdarzenia:** na pull requeście tylko `chromium`,
na `main` wszystkie trzy silniki. Użyj `fromJSON`.

**3. Instaluj tylko potrzebną przeglądarkę** — `--with-deps ${{ matrix.browser }}`,
nie wszystkie trzy.

**4. Policz joby.** Ile ich jest na PR-ze, a ile na `main`? Porównaj z limitem
**20 równoległych jobów** na koncie Free.

**5. Wypróbuj `exclude`.** Wyłącz jedną kombinację — na przykład WebKit dla sharda 4 —
i zobacz, jak zmienia się liczba jobów.

## Kryteria akceptacji

- [ ] matrix ma dwa wymiary: `browser` i `shard`
- [ ] PR uruchamia 4 joby UI, `main` — 12
- [ ] instalowana jest wyłącznie przeglądarka z bieżącej kombinacji
- [ ] nazwa joba mówi, który silnik i który shard
- [ ] potrafisz policzyć, ile jobów zmieści się w limicie konta

## Zmierz

| Zdarzenie | Liczba jobów UI | Wszystkie joby w przebiegu | Limit |
|---|---|---|---|
| `pull_request` | ? | ? | 20 |
| `push` do `main` | ? | ? | 20 |

<details>
<summary><b>Rozwiązanie</b></summary>

```yaml
  test-ui:
    name: UI ${{ matrix.browser }} (shard ${{ matrix.shard }}/4)
    runs-on: ubuntu-latest
    needs: build
    strategy:
      fail-fast: false
      matrix:
        # A full cross-browser sweep on every pull request is waste, not diligence:
        # engine differences are a rare class of defect, and the review loop pays for
        # the check every single time. Main carries the cost once per merge instead.
        browser: >-
          ${{ fromJSON(github.event_name == 'pull_request'
              && '["chromium"]'
              || '["chromium","firefox","webkit"]') }}
        shard: [1, 2, 3, 4]

    steps:
      # ...
      - name: Install browser
        run: npx playwright install --with-deps ${{ matrix.browser }}

      - name: UI tests
        run: npx playwright test --project=ui-${{ matrix.browser }} --shard=${{ matrix.shard }}/4

      - uses: actions/upload-artifact@v4
        if: always()
        with:
          # Two dimensions now, so both belong in the name.
          name: blob-report-${{ matrix.browser }}-${{ matrix.shard }}
          path: blob-report/
```

### Rachunek jobów

| Zdarzenie | UI | Pozostałe | Razem | Limit |
|---|---|---|---|---|
| `pull_request` | 1 × 4 = **4** | ~5 | **9** | 20 |
| `push` do `main` | 3 × 4 = **12** | ~5 | **17** | 20 |

Siedemnaście z dwudziestu. **Mieści się, ale ciasno.** Wystarczy, że w tym samym momencie
biegnie drugi przebieg — na innym repozytorium tego samego konta — i zaczyna się kolejkowanie.

To jest sedno tego zadania: **matrix skaluje się multiplikatywnie**. Dodanie trzeciego wymiaru
o trzech wartościach dałoby 36 jobów UI i przekroczyło limit dwukrotnie.

### `include` i `exclude`

```yaml
    strategy:
      matrix:
        browser: [chromium, firefox, webkit]
        shard: [1, 2, 3, 4]
        exclude:
          # WebKit is the slowest engine here; trimming one combination is a cheap
          # way to stay under the concurrency ceiling.
          - browser: webkit
            shard: 4
        include:
          # `include` can also add a combination that the product would not generate.
          - browser: chromium
            shard: 1
            record-trace: true
```

</details>

## Pułapki

**`fromJSON` wymaga poprawnego JSON-a w stringu.** Pojedyncze cudzysłowy w środku wyrażenia,
podwójne w JSON-ie. Literówka daje komunikat, który nie wskazuje `fromJSON` jako źródła.

**Matrix mnoży, nie dodaje.** Trzy przeglądarki × cztery shardy to dwanaście jobów, nie siedem.
Przy trzech wymiarach rośnie to szybciej, niż podpowiada intuicja.

**Nazwa joba musi rozróżniać kombinacje.** Bez `${{ matrix.browser }}` w nazwie dwanaście
identycznie nazwanych jobów jest nie do odczytania w UI.

**Projekt Playwrighta musi istnieć.** `--project=ui-firefox` zadziała tylko, jeśli taki projekt
jest w `playwright.config.ts`. W tym repozytorium są wszystkie trzy.

## Do dyskusji

- Ile realnych błędów w Twoim projekcie wynikało z różnic między silnikami? Czy uzasadniają
  cross-browser na każdym PR-ze?
- Matrix po wersjach Node (18/20/22) to inny klasyczny przypadek. Kiedy biblioteka go
  potrzebuje, a kiedy aplikacja?
- Limit 20 jobów jest na konto, nie na repozytorium. Jak to zmienia projektowanie matrixa
  w zespole, gdzie wszyscy pracują na jednej organizacji?
