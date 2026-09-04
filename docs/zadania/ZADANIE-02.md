# ZADANIE 02 — Triggery i `concurrency`

## Cel

Ustalić, **kiedy** pipeline ma się uruchamiać, i przestać płacić za przebiegi, których wynik
już nikogo nie interesuje.

## Dlaczego to boli

Wyjściowy workflow ma jedną linijkę konfiguracji uruchamiania:

```yaml
on:
  push:
```

Z tego wynikają trzy rzeczy, z których żadna nie jest zamierzona.

**Każdy push na każdy branch uruchamia pełny pipeline** — łącznie z branchem, na którym
zapisujesz notatki albo eksperymentujesz.

**Pull requesty nie mają własnego zdarzenia.** Pipeline uruchamia się z `push`, więc dla PR-a
sprawdza stan brancha, a nie stan po scaleniu z `main`. To dwie różne rzeczy i różnica potrafi
zaboleć dokładnie wtedy, gdy najmniej się tego spodziewasz.

**Trzy pushe pod rząd uruchamiają trzy pełne przebiegi.** Pierwsze dwa są nieaktualne w chwili,
gdy startuje trzeci — ale i tak zajmują runnery i minuty. Przy darmowym koncie masz **20
równoległych jobów na całe konto**, więc kolejkujesz sam sobie.

## Zadanie

**1. Ogranicz `push` do gałęzi głównej i dodaj `pull_request`.**

Pipeline ma się uruchamiać, gdy coś trafia do `main` oraz gdy ktoś otwiera lub aktualizuje PR.

**2. Dodaj `workflow_dispatch`**, żeby dało się uruchomić pipeline ręcznie z zakładki Actions.

**3. Dodaj `concurrency`** — nowy przebieg na tej samej gałęzi ma **anulować** poprzedni,
jeszcze niezakończony.

**4. Udowodnij, że działa.** Wypchnij trzy commity szybko jeden po drugim i zobacz
w zakładce Actions, co stało się z dwoma pierwszymi przebiegami.

## Kryteria akceptacji

- [ ] `push` uruchamia pipeline tylko dla `main`
- [ ] `pull_request` uruchamia pipeline dla PR-ów kierowanych do `main`
- [ ] `workflow_dispatch` pozwala uruchomić pipeline ręcznie
- [ ] trzy szybkie pushe zostawiają **jeden** działający przebieg, dwa oznaczone jako anulowane
- [ ] otwarcie PR-a nie uruchamia dwóch przebiegów naraz

## Zmierz

| Co | Jak sprawdzić |
|---|---|
| Liczba przebiegów po trzech pushach | zakładka Actions — ile `cancelled`, ile `in_progress` |
| Czy PR uruchamia jeden run czy dwa | lista przebiegów po otwarciu PR-a |
| Zaoszczędzone minuty | (liczba anulowanych) × czas baseline |

<details>
<summary><b>Rozwiązanie</b></summary>

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:

# One run per branch. A newer push cancels the run that is already in flight, because
# its result describes code nobody is going to merge.
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  test:
    runs-on: ubuntu-latest
    # ... reszta bez zmian
```

### Dlaczego akurat taki `group`

`${{ github.workflow }}-${{ github.ref }}` daje jedną grupę na parę *workflow + gałąź*.
Dzięki temu przebiegi na różnych branchach nie anulują się nawzajem, a kolejne pushe
na ten sam branch — tak.

Gdybyś użył samego `${{ github.ref }}`, dwa **różne** workflow na tej samej gałęzi
anulowałyby się nawzajem, co prawie nigdy nie jest tym, o co chodzi.

</details>

## Pułapki

**`cancel-in-progress` na `main` bywa niepożądane.** Na gałęzi głównej anulowanie przebiegu
oznacza, że dla któregoś commita **nigdy nie poznasz wyniku** — a jeśli pipeline coś wdraża,
możesz przerwać go w połowie. Częsty kompromis: anuluj na PR-ach, nie anuluj na `main`:

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: ${{ github.ref != 'refs/heads/main' }}
```

**Podwójne uruchomienie na PR-ach z tego samego repo.** Jeśli zostawisz `push` bez ograniczenia
do `main`, a jednocześnie dodasz `pull_request`, to push na branch z otwartym PR-em uruchomi
pipeline **dwa razy** — raz z `push`, raz z `pull_request`. Płacisz podwójnie za tę samą informację.

**`pull_request` testuje commit scalenia**, a nie szczyt Twojej gałęzi. To zwykle zaleta —
sprawdzasz to, co faktycznie trafi do `main` — ale bywa mylące, gdy `main` posunął się do przodu.

## Do dyskusji

- Kiedy anulowanie przebiegu jest **złym** pomysłem? (podpowiedź: wdrożenia, publikowanie
  artefaktów, cokolwiek z efektem ubocznym)
- `push` na `main` i `pull_request` do `main` to dwa różne zdarzenia dla tego samego kodu.
  Czy oba powinny uruchamiać **ten sam** zestaw kontroli?
- Limit 20 równoległych jobów liczy się dla **całego konta**, nie repozytorium. Co to znaczy
  dla kogoś, kto pracuje nad kilkoma projektami naraz?
