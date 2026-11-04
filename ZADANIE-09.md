# ZADANIE 09 — Równoległość: najpierw workers, potem shardowanie

## Cel

Skrócić czas testów UI przez równoległe wykonanie.

W tym zadaniu wykonasz **trzy pomiary w określonej kolejności**. Chodzi o to, żeby osobno zobaczyć
efekt zwiększenia liczby workerów i osobno efekt shardowania, a potem porównać zarówno czas,
jak i koszt obu rozwiązań.

## Na czym polega problem

Pełna regresja UI na `main` nadal trwa ponad dwie minuty, a jej wynik wpływa na decyzję o wydaniu.
Zestaw dobrze nadaje się do równoległego wykonania: mamy 123 niezależne testy, każdy korzysta
z własnego koszyka i żaden nie wymaga wyniku innego testu.

Równoległość ma jednak **dwa niezależne rodzaje** i mylenie ich to najczęstsze nieporozumienie
w tym temacie:

| | **workers** | **shardowanie** |
|---|---|---|
| Co skaluje | procesy na jednej maszynie | liczbę maszyn |
| Mechanizm | `workers` w `playwright.config.ts` | `strategy.matrix` + `--shard` |
| Twardy limit | rdzenie runnera | 20 jobów naraz (konto Free) |
| Koszt w minutach | ? | ? |

Ostatni wiersz uzupełnisz po pomiarach.

## Zadanie

Zmieniasz `playwright.config.ts` i job `test-ui` w `.github/workflows/ci.yml`. Pozostałe joby
i sekcje zostają bez zmian.

**1. Pomiar A — stan wyjściowy.** W zakładce **Actions** otwórz ostatni przebieg na `main`
z pełną regresją. Zapisz w `docs/baseline.md` dwie wartości:

- czas joba `UI tests`,
- łączny czas wszystkich jobów ze strony **Usage**.

To jest punkt odniesienia dla kolejnych pomiarów.

**2. Pomiar B — zwiększ liczbę workerów.** W `playwright.config.ts` znajdź linię:

```ts
  workers: process.env.CI ? 1 : undefined,
```

Zanim ją zmienisz, odpowiedz sobie: skąd się tam wzięła jedynka i ile rdzeni ma runner
w repozytorium publicznym (podpowiedź: warunki brzegowe z początku dnia). Zamień na:

```ts
  workers: process.env.CI ? 4 : undefined,
```

Zatwierdź i wypchnij:

```bash
git add playwright.config.ts
git commit -m "Use four workers on CI"
git push
```

Po zakończeniu przebiegu zapisz te same dwie wartości: czas joba `UI tests` i łączny czas jobów
(**Usage**).

Na tym etapie zmieniasz tylko liczbę workerów. Shardowania jeszcze nie dodawaj.

**3. Pomiar C — podziel testy na cztery shardy.** W jobie `test-ui` zrób cztery zmiany.

Zamień linię `name:` na:

```yaml
    name: UI tests ${{ matrix.shard }}/4 (${{ github.event_name == 'pull_request' && 'smoke' || github.event_name == 'workflow_dispatch' && inputs.suite || 'full regression' }})
```

Pod linią `if:` dopisz:

```yaml
    strategy:
      fail-fast: false
      matrix:
        shard: [1, 2, 3, 4]
```

W kroku `UI tests` zamień linię `run:` na:

```yaml
        run: npx playwright test --project=ui-chromium --shard=${{ matrix.shard }}/4 ${{ env.GREP }}
```

Ostatni krok joba, który wgrywa raport, zamień na:

```yaml
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: playwright-report-${{ matrix.shard }}
          path: playwright-report/
          retention-days: 7
```

| Element | Po co |
|---|---|
| `matrix.shard: [1, 2, 3, 4]` | GitHub uruchamia cztery warianty tego samego joba, każdy na osobnym runnerze |
| `--shard=${{ matrix.shard }}/4` | każdy runner dostaje inną część zestawu testów |
| `fail-fast: false` | jeśli jeden shard zakończy się błędem, pozostałe wykonują się do końca — dostajesz wynik wszystkich części regresji |
| `if: always()` | raport wgrywa się także wtedy, gdy testy nie przejdą — czyli wtedy, gdy jest najbardziej potrzebny |
| `name: playwright-report-${{ matrix.shard }}` | każdy shard wgrywa raport pod inną nazwą; bez tego cztery joby próbowałyby utworzyć artefakt o tej samej nazwie |

Zatwierdź i wypchnij:

```bash
git add .github/workflows/ci.yml
git commit -m "Split UI tests into four shards"
git push
```

Na grafie powinny pojawić się cztery joby: `UI tests 1/4` … `4/4`. Zapisz czas najdłuższego
sharda i łączny czas jobów (**Usage**).

**4. Porównaj A, B i C.** Uzupełnij w `docs/baseline.md` tabelę z sekcji *Zmierz* i ostatni
wiersz tabeli z *Na czym polega problem*. Odpowiedz na dwa pytania:

- co bardziej skróciło czas oczekiwania na wynik — workers czy shardowanie?
- jak zmienił się łączny czas jobów?

Chodzi o rozdzielenie dwóch rzeczy: czasu, który widzi autor zmiany, i kosztu równoległego
wykonania.

**5. Zadanie dodatkowe — osiem shardów.** Zamień `[1, 2, 3, 4]` na `[1, 2, 3, 4, 5, 6, 7, 8]`,
a `/4` na `/8` w linii `name:` i w `--shard`. Wypchnij i zmierz, a potem wróć do czterech shardów:

```bash
git revert --no-edit HEAD
git push
```

Wyjaśnij w `docs/baseline.md`, dlaczego więcej shardów nie musi oznaczać proporcjonalnie
krótszego przebiegu, a może zwiększyć łączny czas jobów.

**6. Sprawdź, co się dzieje, gdy jeden shard zakończy się błędem.** Przenieś na nową gałąź zmianę w katalogu
z ZADANIA 01 (ten sam sposób co w ZADANIU 03):

```bash
git checkout -b check-catalog
git checkout warsztat/demo/failing-ui -- src/web/views/Catalog.tsx
git commit -m "Catalog change to verify"
git push -u origin check-catalog
```

Nie otwieraj pull requesta. Na pull requeście biegnie tylko smoke, a ten błąd wykrywa pełna
regresja. Zamiast tego w zakładce **Actions** wybierz **CI** i kliknij **Run workflow**:

- w **Use workflow from** wybierz gałąź `check-catalog`,
- w **UI test scope** wybierz `all`,
- uruchom workflow.

Sprawdź, że:

- jeden shard kończy się na czerwono,
- pozostałe trzy wykonują się do końca i nie są anulowane,
- na stronie przebiegu, w sekcji **Artifacts**, są cztery raporty: `playwright-report-1` … `-4`.

**7. Wróć na `main`:**

```bash
git checkout main
```

## Kryteria akceptacji

- [ ] zapisane są trzy pomiary: A, B i C (kroki 1–3)
- [ ] cztery shardy są widoczne jako osobne joby (krok 3)
- [ ] potrafisz porównać wpływ workerów i shardowania na czas przebiegu oraz łączny czas jobów (krok 4)
- [ ] błąd jednego sharda nie anuluje pozostałych (krok 6)
- [ ] każdy shard wgrywa własny raport, także wtedy, gdy testy nie przejdą (krok 6)

## Zmierz

| Konfiguracja | Czas `UI tests` | Łączny czas jobów (Usage) |
|---|---|---|
| A: `workers: 1`, bez shardowania | ? | ? |
| B: `workers: 4`, bez shardowania | ? | ? |
| C: 4 shardy × `workers: 4` | ? | ? |
| dodatkowo: 8 shardów × `workers: 4` | ? | ? |
