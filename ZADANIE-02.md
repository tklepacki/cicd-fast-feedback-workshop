# ZADANIE 02 — Triggery i `concurrency`

## Cel

Ustalić, **kiedy** pipeline ma się uruchamiać, i przestać płacić za przebiegi, których wynik
już nikogo nie interesuje.

## Na czym polega problem

Zespół pracuje na gałęziach. Każdy pushuje na swoją kilka razy dziennie, a kiedy zmiana jest
gotowa, otwiera pull request do `main`. Wyjściowy workflow nie rozróżnia tych sytuacji, bo ma
jedną linijkę konfiguracji uruchamiania:

```yaml
on:
  push:
```

Z tego wynikają trzy rzeczy, z których żadna nie jest zamierzona.

**Każdy push na każdy branch uruchamia pełny pipeline** — łącznie z branchem, na którym
ktoś zapisuje notatki albo eksperymentuje.

**Pull requesty nie mają własnego zdarzenia.** Pipeline uruchamia się z `push`, więc dla PR-a
sprawdza stan brancha, a nie stan po scaleniu z `main`. To dwie różne rzeczy i różnica potrafi
zaboleć dokładnie wtedy, gdy najmniej się tego spodziewasz.

**Trzy pushe pod rząd uruchamiają trzy pełne przebiegi.** Pierwsze dwa są nieaktualne w chwili,
gdy startuje trzeci — ale i tak zajmują runnery i minuty. Przy darmowym koncie masz **20
równoległych jobów na całe konto**, więc kolejkujesz sam sobie.

## Zadanie

Wszystkie zmiany robisz w pliku `.github/workflows/ci.yml`, w jego górnej części.

**1. Ogranicz `push` do gałęzi `main`.** Znajdź na początku pliku:

```yaml
on:
  push:
```

i zamień na:

```yaml
on:
  push:
    branches: [main]
```

Od teraz push uruchamia pipeline tylko wtedy, gdy trafia na `main`.

**2. Dodaj `pull_request`.** W tej samej sekcji `on:`, pod `push`, dopisz:

```yaml
  pull_request:
    branches: [main]
```

Pipeline uruchomi się dla każdego pull requesta kierowanego do `main` i przy każdym kolejnym
pushu do jego gałęzi.

**3. Dodaj `workflow_dispatch`.** Pod `pull_request` dopisz jedną linię:

```yaml
  workflow_dispatch:
```

W zakładce Actions pojawi się przycisk **Run workflow** do ręcznego uruchomienia.

**4. Dodaj `concurrency`.** Między sekcją `on:` a `jobs:` dopisz nową sekcję, bez wcięcia:

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

`group` łączy przebiegi tego samego workflow na tej samej gałęzi. `cancel-in-progress: true`
sprawia, że nowy przebieg w grupie anuluje poprzedni, jeszcze niezakończony. Przebiegi na
różnych gałęziach nie anulują się nawzajem.

Po krokach 1–4 początek pliku wygląda tak (komentarze pominięte):

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  test:
    # ... bez zmian
```

**5. Zatwierdź i wypchnij zmiany na `main`.**

```bash
git add .github/workflows/ci.yml
git commit -m "Run the pipeline only for main and pull requests, cancel outdated runs"
git push
```

**6. Sprawdź anulowanie.** Od razu, zanim poprzedni przebieg się skończy, wypchnij trzy puste
commity jeden po drugim:

```bash
git commit --allow-empty -m "test 1"; git push
git commit --allow-empty -m "test 2"; git push
git commit --allow-empty -m "test 3"; git push
```

W zakładce **Actions** powinien trwać tylko przebieg „test 3”. Wszystkie wcześniejsze mają
szarą ikonę i status **Cancelled**.

**7. Sprawdź, że push na inną gałąź nic nie uruchamia, a pull request tak.**

```bash
git checkout -b test-pr
git commit --allow-empty -m "test PR"
git push -u origin test-pr
```

W zakładce **Actions** nie powinien pojawić się żaden nowy przebieg.

Teraz otwórz pull request: na stronie repozytorium kliknij **Compare & pull request** przy
gałęzi `test-pr`, sprawdź, że bazą jest `main`, i kliknij **Create pull request**. W zakładce
**Actions** powinien pojawić się **dokładnie jeden** nowy przebieg, opisany jako pull request.

**8. Sprawdź ręczne uruchomienie.** W zakładce **Actions** wybierz po lewej workflow **CI**,
kliknij **Run workflow**, zostaw gałąź `main` i potwierdź. Na liście pojawi się nowy przebieg.

**9. Wróć na `main`**, żeby kolejne zadania robić na właściwej gałęzi:

```bash
git checkout main
```

## Kryteria akceptacji

- [ ] push na `main` uruchamia pipeline (krok 5)
- [ ] z czterech szybkich pushy na `main` trwa tylko ostatni, wcześniejsze są anulowane (krok 6)
- [ ] push na gałąź inną niż `main` nie uruchamia pipeline'u (krok 7)
- [ ] otwarcie pull requesta do `main` uruchamia **jeden** przebieg (krok 7)
- [ ] pipeline da się uruchomić ręcznie przyciskiem **Run workflow** (krok 8)

## Zmierz

| Co | Jak sprawdzić |
|---|---|
| Liczba przebiegów po szybkich pushach | zakładka Actions — ile `Cancelled`, ile w toku |
| Czy PR uruchamia jeden przebieg czy dwa | lista przebiegów po otwarciu PR-a |
| Zaoszczędzone minuty | (liczba anulowanych) × czas baseline |
