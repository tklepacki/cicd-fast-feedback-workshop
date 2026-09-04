# ZADANIE 10 — Równoległość: najpierw workers, potem shardowanie

## Cel

Skrócić testy UI przez zrównoleglenie. Zadanie ma **trzy pomiary w określonej kolejności** —
i chodzi o to, żebyś sam odkrył, który z nich dał najwięcej.

Nie czytaj rozwiązania przed wykonaniem pomiarów. Zepsujesz sobie najlepszą część tego zadania.

## Dlaczego to boli

Testy UI to nadal 2:27 na `main`. Zestaw jest podzielny — 123 niezależne testy, każdy
z własnym koszykiem, żaden nie zależy od pozostałych. Nic nie stoi na przeszkodzie,
żeby biegły równocześnie.

Równoległość ma jednak **dwie niezależne osie** i mylenie ich to najczęstsze nieporozumienie
w tym temacie:

| | **workers** (pionowo) | **shardowanie** (poziomo) |
|---|---|---|
| Co skaluje | procesy na jednej maszynie | liczbę maszyn |
| Mechanizm | `workers` w konfiguracji | `strategy.matrix` + `--shard` |
| Twardy limit | rdzenie runnera | 20 równoległych jobów (konto Free) |
| Koszt w minutach | **zero** | rośnie liniowo |

## Zadanie

**Pomiar A — stan wyjściowy.** Zapisz obecny czas testów UI na `main`.

**Pomiar B — oś pionowa.** W `playwright.config.ts` znajdź linijkę:

```ts
workers: process.env.CI ? 1 : undefined,
```

Zastanów się, skąd się tam wzięła i ile rdzeni ma runner. Zmień wartość. Zmierz.

**Pomiar C — oś pozioma.** Dodaj `strategy.matrix` z czterema shardami i `--shard=i/4`.
Ustaw `fail-fast: false`. Zmierz.

**Porównaj A, B i C.** Który zysk był większy? Który coś kosztował?

**Zadanie dodatkowe:** podbij do ośmiu shardów i wyjaśnij, dlaczego czas prawie nie spadł,
a zużycie minut wzrosło dwukrotnie.

## Kryteria akceptacji

- [ ] zapisane trzy pomiary: A, B, C
- [ ] cztery shardy widoczne jako osobne joby w UI
- [ ] `fail-fast: false` — awaria jednego sharda nie anuluje pozostałych
- [ ] każdy shard wgrywa artefakt pod **unikalną** nazwą
- [ ] potrafisz powiedzieć, która oś dała więcej i dlaczego

## Zmierz

| Konfiguracja | Czas testów UI | Zużyte minuty |
|---|---|---|
| A: `workers: 1`, bez shardów | ? | ? |
| B: `workers: 4`, bez shardów | ? | ? |
| C: 4 shardy × `workers: 4` | ? | ? |
| dodatkowo: 8 shardów × `workers: 4` | ? | ? |

<details>
<summary><b>Rozwiązanie — najpierw wykonaj pomiary</b></summary>

### Skąd wzięła się jedynka

`workers: process.env.CI ? 1 : undefined` pochodzi z konfiguracji generowanej przez
`npm init playwright`. Trafia do tysięcy projektów i prawie nikt jej nie rewiduje —
mimo że **runner w repozytorium publicznym ma cztery rdzenie** (w prywatnym dwa).

Domyślna wartość `workers` w Playwrightcie to **połowa logicznych rdzeni**. Ta linijka
świadomie ją obniża do jednego, a potem zostaje na zawsze.

```ts
workers: process.env.CI ? 4 : undefined,
```

### Shardowanie

```yaml
  test-ui:
    name: Testy UI (shard ${{ matrix.shard }}/4)
    runs-on: ubuntu-latest
    needs: build
    strategy:
      # Without this, one failing shard cancels the other three and you lose their results -
      # exactly the information needed to tell a real failure from a flaky one.
      fail-fast: false
      matrix:
        shard: [1, 2, 3, 4]
    steps:
      # ...
      - run: npx playwright test --project=ui-chromium --shard=${{ matrix.shard }}/4

      - uses: actions/upload-artifact@v4
        if: always()
        with:
          # upload-artifact@v4 requires unique names within a run. A shared name makes
          # all four shards collide and the job fails on the upload, not on the tests.
          name: playwright-report-${{ matrix.shard }}
          path: playwright-report/
```

### Pomiary referencyjne

| Konfiguracja | Czas testów UI | Zysk |
|---|---|---|
| A: `workers: 1` | **2:18** | — |
| B: `workers: 4` | **0:37** | **3,7×** |
| C: 1 shard z 4, `workers: 4` | **0:14** | 9,9× wobec A |

### Wniosek

**Oś pionowa dała większy zysk i nie kosztowała nic.** Zmiana jednej liczby skróciła zestaw
prawie czterokrotnie. Shardowanie dołożyło kolejne skrócenie, ale **zużywa czterokrotnie
więcej minut** — cztery maszyny zamiast jednej.

Kolejność ma znaczenie: gdybyś zaczął od shardowania, zapłaciłbyś czterema maszynami
za coś, co jedna linijka konfiguracji dawała za darmo.

### Dlaczego osiem shardów nie pomaga

Przy czterech shardach każdy wykonuje ~31 testów w ~14 sekundach. Przy ośmiu — ~15 testów
w ~7 sekundach. Ale **narzut startu joba** (checkout, `npm ci`, pobranie artefaktu,
przygotowanie przeglądarki) to kilkadziesiąt sekund **na każdy shard** i się nie zmienia.

Osiem shardów to osiem razy ten narzut. Czas ścienny prawie nie spada, zużycie minut się
podwaja. **Shardowanie ma punkt malejących zysków** i leży on niżej, niż większość ludzi zakłada.

</details>

## Pułapki

**Kolizja nazw artefaktów.** `upload-artifact@v4` wymaga unikalnych nazw w obrębie przebiegu.
Cztery shardy z tą samą nazwą wywalą się na uploadzie — a komunikat nie wskaże shardowania
jako przyczyny.

**`fail-fast: true` (domyślne dla matrix).** Pierwszy padający shard anuluje pozostałe.
Tracisz wtedy informację, czy problem jest w jednym teście, czy w całym zestawie —
czyli dokładnie to, czego potrzebujesz do diagnozy.

**Więcej workerów niż rdzeni.** Procesy zaczynają rywalizować o CPU, testy zwalniają
i **rośnie liczba flaków** — bo asercje czasowe zaczynają się nie wyrabiać.

**Shardowanie psuje raportowanie.** Po tym zadaniu masz cztery osobne raporty zamiast jednego.
To jest ZADANIE 13.

## Do dyskusji

- Skoro `workers` daje więcej i za darmo, dlaczego tak wiele projektów zaczyna od shardowania?
- Runner w repozytorium publicznym ma 4 rdzenie, w prywatnym 2. Jak to zmienia rachunek?
- Limit 20 równoległych jobów jest **na całe konto**. Ile shardów jest bezpieczne, gdy
  w repozytorium biegnie jednocześnie kilka pipeline'ów?
