# ZADANIE 04 — Rozbicie na joby i `needs`

## Cel

Rozbić jeden liniowy job na kilka, które mogą biec **równolegle**, i opisać zależności
między nimi przez `needs`.

## Dlaczego to boli

Po ZADANIU 03 kolejność jest już rozsądna, ale wszystko nadal wykonuje się **sekwencyjnie
w jednym jobie**. To ma trzy konsekwencje.

**Rzeczy niezależne czekają na siebie bez powodu.** Lint nie potrzebuje wyniku typechecku,
a typecheck nie potrzebuje lintu. Mimo to jedno czeka na drugie.

**Nie widać, co właściwie padło.** Job nazywa się `test` i albo jest zielony, albo czerwony.
Żeby dowiedzieć się, czy problem jest w lincie, czy w testach API, trzeba wejść w logi.

**Nie da się nic uruchomić selektywnie.** Skoro wszystko jest jednym krokiem, nie można
powiedzieć „testy UI tylko na `main`" — bo nie ma czego wskazać.

## Zadanie

**1. Wydziel joby:** `quality` (lint + typecheck), `unit`, `build`, `test-api`, `test-ui`.

**2. Opisz zależności przez `needs`.** Zastanów się, co naprawdę od czego zależy:

- czy `unit` potrzebuje wyniku `quality`?
- czy testy API i UI potrzebują zbudowanej aplikacji?
- co może ruszyć od razu, bez czekania na cokolwiek?

**3. Obejrzyj graf.** W zakładce Actions run pokazuje joby jako graf zależności.
Sprawdź, czy wygląda tak, jak zamierzyłeś.

**4. Zmierz, co się zmieniło** — i zwróć uwagę, że **suma czasów jobów wzrośnie**,
a czas całego przebiegu spadnie. Zrozum, dlaczego.

## Kryteria akceptacji

- [ ] pipeline ma co najmniej pięć osobnych jobów
- [ ] `quality` i `unit` startują równolegle, bez czekania na siebie
- [ ] testy API i UI nie startują, dopóki build się nie powiedzie
- [ ] na liście kontroli PR-a widać nazwy poszczególnych jobów, nie jedno `test`
- [ ] graf zależności w UI odpowiada zamierzeniu

## Zmierz

| Co | Przed | Po |
|---|---|---|
| Czas całego przebiegu | ? | ? |
| **Suma** czasów wszystkich jobów | ? | ? |
| Czas do informacji o błędzie lintu | ~35 s | ? |
| Liczba kontroli widocznych na PR-ze | 1 | ? |

<details>
<summary><b>Rozwiązanie</b></summary>

```yaml
jobs:
  quality:
    name: Lint i typecheck
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version-file: .nvmrc
          cache: npm
      - run: npm ci
      - run: npm run lint
      - run: npm run typecheck

  unit:
    name: Testy jednostkowe
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version-file: .nvmrc
          cache: npm
      - run: npm ci
      - run: npm run test:unit

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

  test-api:
    name: Testy API
    runs-on: ubuntu-latest
    needs: build
    steps:
      # ... setup jak wyżej, plus przeglądarki z cache
      - run: npm run test:api

  test-ui:
    name: Testy UI
    runs-on: ubuntu-latest
    needs: build
    steps:
      # ... setup jak wyżej, plus przeglądarki z cache
      - run: npm run test:ui
```

### Dlaczego akurat takie zależności

`quality`, `unit` i `build` **nie mają `needs`** — startują jednocześnie, w chwili
uruchomienia przebiegu. Żaden z nich nie potrzebuje wyniku pozostałych.

`test-api` i `test-ui` mają `needs: build`, bo testują działającą aplikację.
Nie ma sensu uruchamiać ich, jeśli kod się nie kompiluje.

Kusi, żeby dodać `needs: quality` do testów — „po co testować kod, który nie przechodzi
lintu?". To jednak **wydłuża** ścieżkę do wyniku testów o czas lintu, nie dając nic w zamian:
lint i tak zablokuje merge przez bramkę, którą postawimy w ZADANIU 18.

### Dlaczego suma czasów rośnie

Każdy job to **osobna maszyna**. Każda robi własny checkout, własne `npm ci`, własne
przygotowanie środowiska. Pięć jobów to pięć razy ten narzut.

Czas *całego przebiegu* spada, bo joby biegną równolegle. Ale *zużycie minut* rośnie.
To jest realny koszt rozbijania i trzeba go znać — wrócimy do niego w ZADANIACH 05 i 17.

</details>

## Pułapki

**Nadmiarowe `needs`.** Każda zależność, która nie jest konieczna, zamienia równoległość
w kolejkę. Zanim dopiszesz `needs`, zadaj pytanie: *czy ten job naprawdę potrzebuje wyniku
tamtego, czy tylko wydaje mi się, że tak porządniej?*

**Powtórzony setup w każdym jobie.** Po tym zadaniu ten sam czterokrokowy wstęp jest
w pięciu miejscach. To realny problem, nie estetyczny — ale rozwiązujemy go dopiero
w ZADANIU 17, żeby najpierw zobaczyć, jak bardzo przeszkadza.

**`needs` nie przekazuje plików.** Job zależny dostaje informację, że poprzedni się powiódł —
ale **nie dostaje jego wyników**. Zbudowana aplikacja z joba `build` nie jest widoczna
w `test-ui`, więc na razie każdy job buduje ją od nowa. To jest ZADANIE 05.

## Do dyskusji

- Czy testy powinny zależeć od lintu? Argumenty są po obu stronach.
- Rozbicie na joby kosztuje minuty, a oszczędza czas oczekiwania. Kiedy ten kompromis
  przestaje się opłacać?
- Pięć osobnych kontroli na PR-ze to więcej informacji, ale też więcej hałasu.
  Gdzie jest granica?
