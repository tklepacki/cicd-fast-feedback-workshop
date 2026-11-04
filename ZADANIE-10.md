# ZADANIE 10 — Matrix, który liczy sam siebie

## Cel

Potraktować `matrix` jako **ogólny mechanizm generowania jobów**, a nie tylko sposób na
shardowanie, i dopasować liczbę shardów do rodzaju przebiegu.

## Na czym polega problem

Po ZADANIU 09 testy UI dzielą się na cztery shardy — **zawsze cztery**, niezależnie od tego,
czy uruchamiamy pięć testów smoke, czy pełną regresję.

Na pull requeście to nie ma sensu. Pięć testów na czterech maszynach oznacza, że każdy runner
spędza większość czasu na przygotowaniu środowiska — checkout, `npm ci`, pobranie artefaktu —
a nie na testowaniu. Zajmujemy cztery maszyny dla kilku krótkich testów, a te same zasoby
mogłyby w tym czasie obsługiwać inne przebiegi.

Liczba shardów jest wpisana w matrixie na sztywno. Matrix nie musi jednak być stałą listą —
możemy wyliczyć jego zawartość dynamicznie.

## Zadanie

Zmieniasz tylko job `test-ui` w `.github/workflows/ci.yml`. Pozostałe joby i sekcje zostają bez zmian.

**1. Wylicz liczbę shardów z wyrażenia.** W sekcji `strategy:` zamień linię `shard: [1, 2, 3, 4]` na:

```yaml
        shard: >-
          ${{ fromJSON(github.event_name == 'pull_request'
              && '[1,2]'
              || '[1,2,3,4,5,6,7,8]') }}
```

Na pull requeście matrix utworzy dwa shardy, w pozostałych przypadkach osiem. Wyrażenie
`${{ ... }}` zwraca **napis**, a matrix potrzebuje **listy**. `fromJSON` zamienia napis
`'[1,2]'` na prawdziwą listę dwóch wartości. Bez `fromJSON` matrix dostałby napis zamiast
listy i nie powstałyby dwa osobne shardy.

**2. Zmień nazwę joba.** Zamień linię `name:` na:

```yaml
    name: UI tests ${{ matrix.shard }}/${{ github.event_name == 'pull_request' && 2 || 8 }} (${{ github.event_name == 'pull_request' && 'smoke' || github.event_name == 'workflow_dispatch' && inputs.suite || 'full regression' }})
```

Dzięki temu nazwa każdego joba pokaże:

- numer sharda,
- łączną liczbę shardów,
- tryb testów.

**3. Użyj tej samej liczby w `--shard`.** W kroku `UI tests` zamień linię `run:` na:

```yaml
        run: npx playwright test --project=ui-chromium --shard=${{ matrix.shard }}/${{ github.event_name == 'pull_request' && 2 || 8 }} ${{ env.GREP }}
```

To najważniejsza część zadania. Liczba shardów występuje teraz w **trzech miejscach**:

- w matrixie,
- w nazwie joba,
- w mianowniku `--shard`.

Wszystkie trzy muszą się zgadzać. Jeśli matrix utworzy dwa joby, a w `--shard` zostanie `/4`,
ruszą tylko shardy 1/4 i 2/4. Shardy 3/4 i 4/4 nigdy nie wystartują — a pipeline i tak będzie
zielony.

**4. Zatwierdź zmiany, wypchnij je na `main` i sprawdź osiem shardów.**

```bash
git add .github/workflows/ci.yml
git commit -m "Choose the shard count by event"
git push
```

W zakładce **Actions** powinno pojawić się osiem jobów: `UI tests 1/8 (full regression)` …
`UI tests 8/8 (full regression)`. Sprawdź i zapisz w `docs/baseline.md`:

- **sumę testów ze wszystkich shardów** — w logu kroku `UI tests` każdego sharda jest
  `N passed`. Dodaj osiem liczb. Musi wyjść **123**. Jeśli wychodzi mniej, któryś mianownik
  się nie zgadza i część testów się nie uruchomiła.
- **czas najdłuższego sharda**,
- **łączny czas wszystkich jobów** z sekcji **Usage**,
- **ile jobów działało jednocześnie** w najbardziej obciążonym momencie przebiegu — i ile
  zostaje do limitu 20 jobów naraz.

**5. Sprawdź pull request.**

```bash
git checkout -b check-shards
```

Dopisz linię do pliku — polecenie zależy od systemu.

macOS, Linux albo Git Bash na Windowsie:

```bash
echo "// shard check" >> src/web/views/Catalog.tsx
```

Windows, PowerShell:

```powershell
Add-Content src/web/views/Catalog.tsx "// shard check"
```

```bash
git commit -am "Check shards on a pull request"
git push -u origin check-shards
```

Dopisujemy komentarz w widoku, a nie pusty commit, bo pusty commit nie zmienia żadnego pliku —
filtr z ZADANIA 08 pominąłby wtedy testy UI i nie byłoby czego dzielić na shardy.

Otwórz pull request z `check-shards` do `main`. Tym razem powinny ruszyć tylko dwa joby:
`UI tests 1/2 (smoke)` i `UI tests 2/2 (smoke)`. Zsumuj testy z obu shardów — powinno wyjść
**5**. Zapisz też czas najdłuższego sharda i łączny czas jobów (**Usage**). Pull requesta
nie scalaj.

**6. Porównaj z ZADANIEM 09.** Obok pomiaru z kroku 4 (osiem shardów) wpisz w `docs/baseline.md`
pomiar C z ZADANIA 09 (cztery shardy): czas najdłuższego sharda i łączny czas jobów. Zastanów
się, czy zysk z ośmiu shardów zamiast czterech uzasadnia dodatkowy koszt — wrócimy do tego
na omówieniu.

**7. Wróć na `main`:**

```bash
git checkout main
```

## Kryteria akceptacji

- [ ] pull request uruchamia **dwa** shardy, a `main` — **osiem** (kroki 4–5)
- [ ] suma testów ze wszystkich shardów wynosi 123 na `main` i 5 na pull requeście (kroki 4–5)
- [ ] nazwa joba pokazuje numer sharda, łączną liczbę shardów i tryb testów (krok 2)
- [ ] policzona jest maksymalna liczba jobów działających jednocześnie na `main` i to, ile zostaje do limitu (krok 4)
- [ ] pomiar ośmiu shardów jest zapisany i porównany z czterema shardami z ZADANIA 09 (krok 6)

## Zmierz

| Co | PR (2 shardy) | main (8 shardów) | main (4 shardy, z ZADANIA 09) |
|---|---|---|---|
| Czas najdłuższego sharda | ? | ? | ? |
| Łączny czas jobów (Usage) | ? | ? | ? |
| Suma testów ze shardów | ? | ? | — |
| Jobów jednocześnie w szczycie | ? | ? | — |
