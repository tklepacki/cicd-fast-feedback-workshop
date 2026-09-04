# ZADANIE 09 — Selektywność na dwóch poziomach

## Cel

Nie uruchamiać testów, których zmiana nie mogła zepsuć. Dwa różne piętra tej samej decyzji
i o to w tym zadaniu chodzi:

| Poziom | Pytanie | Narzędzie |
|---|---|---|
| **joba** | *czy w ogóle uruchamiać testy UI?* | `dorny/paths-filter` |
| **testu** | *które testy uruchomić?* | `playwright test --only-changed` |

## Dlaczego to boli

Po ZADANIU 08 pull request uruchamia pięć testów smoke zamiast stu dwudziestu trzech.
To duży postęp, ale nadal uruchamia je **zawsze** — także wtedy, gdy zmieniłeś wyłącznie
plik `README.md` albo komentarz w teście jednostkowym.

Odwrotnie też: gdy zmieniasz jeden plik w `src/web/`, pełna regresja na `main` uruchamia
komplet testów UI, choć zmiana dotyczy jednego widoku.

## Zadanie

**1. Poziom joba.** Dodaj `dorny/paths-filter` i uruchamiaj `test-ui` tylko wtedy, gdy
zmiana dotknęła `src/web/**`, `src/shared/**` lub `tests/ui/**`.

**2. Poziom testu.** Na `main` uruchamiaj `playwright test --only-changed=origin/main~1`,
żeby wykonać wyłącznie pliki testowe zmienione w tym commicie.

**3. Pamiętaj o `fetch-depth: 0`.** `--only-changed` porównuje z historią gita.
Domyślny płytki checkout jej nie ma i polecenie **cicho nie znajdzie niczego**.

**4. Sprawdź trzy przypadki:**

| Zmiana | Oczekiwanie |
|---|---|
| tylko `README.md` | testy UI pominięte |
| plik w `src/web/` | testy UI uruchomione |
| plik w `tests/ui/regression/cart.spec.ts` | uruchomione, a przy `--only-changed` tylko ten plik |

**5. Zobacz, jak pominięty job wygląda na liście kontroli PR-a.** Zapamiętaj to —
w ZADANIU 18 okaże się istotne.

## Kryteria akceptacji

- [ ] zmiana wyłącznie w dokumentacji nie uruchamia testów UI
- [ ] zmiana w `src/web/` uruchamia je
- [ ] `--only-changed` działa (widać mniejszą liczbę uruchomionych testów)
- [ ] checkout ma `fetch-depth: 0` tam, gdzie jest potrzebny
- [ ] pominięty job jest widoczny jako `skipped`, nie jako `success`

## Zmierz

| Scenariusz | Czas przebiegu |
|---|---|
| Zmiana tylko w `README.md` | ? |
| Zmiana w `src/web/` | ? |
| Zmiana w jednym pliku testów UI (`--only-changed`) | ? |

<details>
<summary><b>Rozwiązanie</b></summary>

```yaml
jobs:
  changes:
    name: Co się zmieniło
    runs-on: ubuntu-latest
    outputs:
      ui: ${{ steps.filter.outputs.ui }}
      api: ${{ steps.filter.outputs.api }}
    steps:
      - uses: actions/checkout@v4
      - uses: dorny/paths-filter@v3
        id: filter
        with:
          filters: |
            ui:
              - 'src/web/**'
              - 'src/shared/**'
              - 'tests/ui/**'
              - 'playwright.config.ts'
            api:
              - 'src/server/**'
              - 'src/shared/**'
              - 'tests/api/**'

  test-ui:
    name: Testy UI
    runs-on: ubuntu-latest
    needs: [build, changes]
    if: needs.changes.outputs.ui == 'true'
    steps:
      - uses: actions/checkout@v4
        with:
          # `--only-changed` compares against git history. A shallow clone has none,
          # and the flag then quietly matches nothing at all.
          fetch-depth: 0
      # ... reszta setupu
      - run: npx playwright test --project=ui-chromium --only-changed=origin/main~1
```

### Dlaczego `src/shared/**` jest w obu filtrach

Katalog `src/shared/` zawiera logikę używaną i przez serwer, i przez frontend — koszyk,
rabaty, walidacja. Zmiana w `cart.ts` może zepsuć jedno i drugie, więc musi uruchamiać
oba zestawy.

To jest najczęstszy błąd przy filtrach po ścieżkach: **pominięcie wspólnej zależności**.
Filtr, który przepuszcza zmianę mogącą coś zepsuć, jest gorszy niż brak filtra, bo daje
fałszywą pewność.

</details>

## Pułapki

**`skipped` to nie `success`.** To jest **najważniejsza pułapka w całym warsztacie**.
Jeśli w ZADANIU 18 ustawisz `test-ui` jako wymaganą kontrolę, a filtr ją pominie, PR
zostanie zablokowany **na zawsze** — bo wymagana kontrola nigdy nie zaraportuje sukcesu.
Rozwiązaniem jest job agregujący, który buduje ZADANIE 18. Zapamiętaj to teraz.

**Filtr, który pomija zbyt wiele.** Każda ścieżka nieujęta w filtrze to potencjalna zmiana,
która przejdzie bez testów. Przy wątpliwości **lepiej uruchomić za dużo niż za mało**.

**`--only-changed` porównuje pliki testowe, nie kod produkcyjny.** Zmiana w `src/web/`
nie zmienia żadnego pliku `.spec.ts`, więc `--only-changed` nie uruchomi **niczego**.
Dlatego łączymy oba poziomy: filtr decyduje *czy*, `--only-changed` zawęża *co* — ale tylko
tam, gdzie zmieniły się same testy.

**`origin/main~1` na PR-ze wskazuje co innego niż na `main`.** Warto użyć
`${{ github.event.pull_request.base.sha }}` dla PR-ów.

## Do dyskusji

- Filtr po ścieżkach oszczędza minuty, ale wprowadza ryzyko przeoczenia. Jak wycenić
  ten kompromis — ile minut jest warte jedno przeoczone zepsucie?
- Czy `--only-changed` ma sens na `main`, gdzie i tak chcesz pełnej pewności przed wydaniem?
- Gdyby filtr pomijał testy przy zmianie w `package-lock.json` — co mogłoby przejść niezauważone?
