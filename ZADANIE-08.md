# ZADANIE 08 — Selektywność na dwóch poziomach

## Cel

Uruchamiać tylko te testy, na które zmiana mogła mieć wpływ. Ta sama decyzja zapada na dwóch poziomach:

| Poziom | Pytanie | Narzędzie |
|---|---|---|
| **joba** | *czy w ogóle uruchamiać testy UI i API?* | `dorny/paths-filter` |
| **testu** | *które pliki testów uruchomić?* | `playwright test --only-changed` |

## Na czym polega problem

Po ZADANIU 07 pull request uruchamia pięć testów smoke zamiast stu dwudziestu trzech. To duży
postęp, ale testy UI i API ruszają **zawsze** — także wtedy, gdy ktoś poprawił literówkę
w `README.md`. Autor takiej zmiany czeka na testy, które nie sprawdzają żadnego obszaru dotkniętego zmianą,
a runnery są zajęte zamiast obsługiwać pull requesty, w których zmienił się kod.

Selektywność jest jednak najbardziej ryzykowną optymalizacją dnia. Filtr, który pominie
testy przy zmianie zdolnej coś zepsuć, jest gorszy niż brak filtra, bo daje fałszywe poczucie
bezpieczeństwa.

## Zadanie

Zmieniasz plik `.github/workflows/ci.yml`. Sekcje `on:` i `concurrency:` oraz joby z ZADAŃ
04–07 zostają bez zmian, poza `test-api` i `test-ui`.

**1. Dodaj job, który sprawdza, co się zmieniło.** Na samym początku sekcji `jobs:`, przed
jobem `quality`, dopisz:

```yaml
  changes:
    name: Changed files
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
              - 'package.json'
              - 'package-lock.json'
              - '.github/workflows/**'
            api:
              - 'src/server/**'
              - 'src/shared/**'
              - 'tests/api/**'
              - 'playwright.config.ts'
              - 'package.json'
              - 'package-lock.json'
              - '.github/workflows/**'
```

Job zwraca dwa wyniki: `ui` i `api`. `true` oznacza, że zmiana dotknęła co najmniej jednej
ścieżki z danego filtra. Zwróć uwagę na trzy rzeczy:

- `src/shared/**` jest w **obu** filtrach, bo z kodu współdzielonego korzystają i serwer, i frontend.
  Zmiana na przykład w `cart.ts` może wpłynąć i na UI, i na API.
- `package.json` i `package-lock.json` są w obu: nowa wersja zależności potrafi zmienić zachowanie
  aplikacji, choć w naszym kodzie nie zmienia się ani jedna linijka.
- `.github/workflows/**` też jest w obu: zmiana w samym pipelinie ma uruchomić wszystkie testy.

**2. Uruchamiaj testy API tylko wtedy, gdy trzeba.** W jobie `test-api` zamień linię
`needs: [build, quality, unit]` na:

```yaml
    needs: [build, quality, unit, changes]
    if: needs.changes.outputs.api == 'true' || github.event_name == 'schedule' || github.event_name == 'workflow_dispatch'
```

**3. To samo dla testów UI.** W jobie `test-ui` zamień linię `needs: [build, quality, unit]` na:

```yaml
    needs: [build, quality, unit, changes]
    if: needs.changes.outputs.ui == 'true' || github.event_name == 'schedule' || github.event_name == 'workflow_dispatch'
```

Druga część warunku jest ważna: nocny przebieg i ręczne uruchomienie z ZADANIA 07 nie mają
z czym porównać zmian. Bez niej filtr mógłby pominąć testy dokładnie wtedy, gdy chcesz pełnej
regresji.

**4. Zatwierdź i wypchnij na `main`.**

```bash
git add .github/workflows/ci.yml
git commit -m "Run UI and API tests only when the change could break them"
git push
```

Zmieniasz plik workflow, więc oba filtry zwrócą `true` i ruszą testy API i UI. Na grafie pojawi
się nowy job `Changed files`, a `API tests` i `UI tests` czekają na niego oraz na `Build`, lint i testy jednostkowe.

**5. Sprawdź zmianę w dokumentacji.**

```bash
git checkout main
git checkout -b check-readme
```

Dopisz linię do pliku — polecenie zależy od systemu.

macOS, Linux albo Git Bash na Windowsie:

```bash
echo "Drobna poprawka dokumentacji." >> README.md
```

Windows, PowerShell:

```powershell
Add-Content README.md "Drobna poprawka dokumentacji."
```

```bash
git commit -am "Update README"
git push -u origin check-readme
```

Otwórz pull request. Na liście kontroli `API tests` i `UI tests` powinny być **pominięte**
(szara ikona, *Skipped*), a lint, testy jednostkowe, build i skan bezpieczeństwa — zielone.
Zapisz czas całego przebiegu. Zwróć uwagę, jak GitHub oznacza pominięty job — wrócimy do tego
w ZADANIU 14, gdzie okaże się, jak GitHub traktuje pominięte joby przy wymaganych kontrolach.

**6. Sprawdź zmianę w widoku.** Utwórz gałąź:

```bash
git checkout main
git checkout -b check-view
```

Otwórz w edytorze `src/web/views/Catalog.tsx` i dopisz na końcu pliku komentarz
`// filter check`. Potem zatwierdź i wypchnij:

```bash
git commit -am "Change the catalog view"
git push -u origin check-view
```

Otwórz pull request. Tym razem `UI tests` powinny ruszyć, a `API tests` — zostać pominięte.

**7. Na koniec sprawdź drugi poziom selektywności — wybór konkretnych testów.** `--only-changed`
wybiera tylko te pliki testów, które się zmieniły, oraz te, które importują zmienione pliki.
To heurystyka: może pominąć testy, na które zmiana wpływa, więc nie zastępuje pełnej regresji.
Sprawdź, co to znaczy w praktyce.
Wróć na `main` (`git checkout main`), dopisz w edytorze komentarz na końcu `tests/ui/regression/cart.spec.ts`
i uruchom:

```bash
npx playwright test --project=ui-chromium --only-changed --list
```

Na końcu listy powinno być `Total: 11 tests in 1 file` — tylko zmieniony plik. Cofnij zmianę
(`git checkout -- tests/ui/regression/cart.spec.ts`), dopisz komentarz w
`src/web/views/Catalog.tsx` i uruchom to samo polecenie. Wynik: `Total: 0 tests`. Testy UI nie
importują kodu aplikacji, tylko otwierają ją w przeglądarce, więc `--only-changed` zmiany w kodzie
nie widzi. Cofnij zmianę (`git checkout -- src/web/views/Catalog.tsx`).

Zapisz w `docs/baseline.md` jedno zdanie: dlaczego `--only-changed` nie nadaje się jako jedyny
filtr testów UI w CI.

## Kryteria akceptacji

- [ ] zmiana w `ci.yml` uruchamia wszystkie testy (krok 4)
- [ ] zmiana tylko w `README.md` pomija `API tests` i `UI tests` (krok 5)
- [ ] pominięty job jest widoczny jako *Skipped*, a nie jako udany (krok 5)
- [ ] zmiana w `src/web/` uruchamia `UI tests`, a pomija `API tests` (krok 6)
- [ ] lokalnie `--only-changed` wybiera 11 testów po zmianie w pliku testu i 0 po zmianie w kodzie (krok 7)

## Zmierz

| Scenariusz | Czas przebiegu |
|---|---|
| Zmiana tylko w `README.md` | ? |
| Zmiana w `src/web/` | ? |
| Pull request bez selektywności (wynik z ZADANIA 07) | ? |
