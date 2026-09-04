# ZADANIE 08 — Trzy tryby uruchomienia: PR, main, noc

## Cel

Przestać uruchamiać pełną regresję UI przy każdej zmianie. Na pull requeście ma biec
**smoke**, pełny zestaw — na `main` i w nocy.

To jest zadanie, w którym warsztat robi to, co obiecuje w tytule: skraca feedback loop
bez utraty pokrycia.

## Dlaczego to boli

Testy UI to **123 testy i 2:27** — dwie trzecie całego przebiegu. Uruchamiane są przy
każdym pushu, na każdą gałąź.

Tymczasem pytanie, które zadaje autor pull requesta, brzmi: *„czy nie zepsułem czegoś
oczywistego?"*. Odpowiada na nie **pięć testów** oznaczonych `@smoke`, trwających 1,7 sekundy:

- katalog się ładuje,
- wyszukiwarka znajduje produkt,
- produkt trafia do koszyka,
- koszyk pokazuje pozycję i sumę,
- zamówienie da się złożyć.

Jeśli którykolwiek z nich pada, dalsza regresja nie ma sensu — sklepu nie da się używać.
A jeśli wszystkie przechodzą, PR jest wart obejrzenia przez człowieka i pełna regresja
może poczekać do merge'a.

## Zadanie

**1. Na `pull_request` uruchamiaj tylko `@smoke`.**

**2. Na `push` do `main` uruchamiaj pełną regresję.**

**3. Dodaj nocny przebieg** przez `on: schedule` — pełny zestaw, raz na dobę.

**4. Dodaj wybór trybu do `workflow_dispatch`**, żeby dało się ręcznie uruchomić
`smoke`, `regression` albo `all`.

**5. Zmierz czas PR-a** i porównaj z ZADANIEM 04.

## Kryteria akceptacji

- [ ] PR uruchamia wyłącznie testy `@smoke`
- [ ] push do `main` uruchamia pełny zestaw
- [ ] `on: schedule` jest skonfigurowany
- [ ] `workflow_dispatch` przyjmuje parametr z trybem
- [ ] czas przebiegu na PR-ze spadł zauważalnie
- [ ] w nazwie joba albo w logu widać, **który tryb** się wykonał

## Zmierz

| Co | Przed | Po |
|---|---|---|
| Czas testów UI na PR-ze | 2:27 | ? |
| Czas testów UI na `main` | 2:27 | ? |
| Całkowity czas przebiegu na PR-ze | ? | ? |
| Liczba uruchomionych testów UI na PR-ze | 123 | ? |

<details>
<summary><b>Rozwiązanie</b></summary>

```yaml
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    # Nightly full regression. Cron runs in UTC.
    - cron: '0 2 * * *'
  workflow_dispatch:
    inputs:
      suite:
        description: 'Zakres testów UI'
        type: choice
        default: smoke
        options: [smoke, regression, all]
```

```yaml
  test-ui:
    name: Testy UI (${{ github.event_name == 'pull_request' && 'smoke' || 'pełna regresja' }})
    runs-on: ubuntu-latest
    needs: build
    steps:
      # ... setup, artefakt, przeglądarki

      - name: UI tests
        run: npx playwright test --project=ui-chromium ${{ env.GREP }}
        env:
          # A pull request asks one question: did anything obvious break? Five tagged tests
          # answer it. The full regression belongs on main, where the answer gates a release
          # rather than a review.
          GREP: >-
            ${{ github.event_name == 'pull_request' && '--grep @smoke'
             || (github.event_name == 'workflow_dispatch' && inputs.suite == 'smoke') && '--grep @smoke'
             || (github.event_name == 'workflow_dispatch' && inputs.suite == 'regression') && '--grep-invert @smoke'
             || '' }}
```

### Wyniki referencyjne

| Co | Przed | Po |
|---|---|---|
| Testy UI na PR-ze | 2:27 (123 testy) | **~15 s** (5 testów) |
| Testy UI na `main` | 2:27 | 2:27 |
| Całkowity czas PR-a | ~3:30 | **~1:10** |

### Dlaczego cron w ogóle działa

W **forkach** scheduled workflows są wyłączone. Repozytorium warsztatowe kopiujesz przez
*Use this template*, co tworzy **zwykłe repozytorium, nie fork** — dlatego `on: schedule`
zadziała. Gdybyśmy zostali przy forku, ten fragment zadania byłby martwy.

Nocny przebieg zobaczysz dopiero następnego dnia. To uczciwe ograniczenie tego ćwiczenia —
konfigurujesz teraz, efekt sprawdzasz jutro.

</details>

## Pułapki

**`--grep @smoke` a `--grep-invert @smoke`.** Pierwszy uruchamia oznaczone, drugi wszystkie
pozostałe. Tryb `all` to brak obu.

**Tag w nazwie `describe`, nie tylko w nazwie testu.** Playwright dopasowuje `--grep`
do pełnej nazwy testu razem z nazwami bloków `describe`. U nas `@smoke` jest w nazwie
bloku, więc obejmuje wszystkie testy w środku.

**Cron liczy czas w UTC** i nie gwarantuje punktualności — przy dużym obciążeniu GitHuba
przebieg potrafi ruszyć kilkanaście minut później.

**Nocne przebiegi na nieaktywnym repozytorium są wyłączane** po 60 dniach bez aktywności.
GitHub przysyła wtedy powiadomienie, które łatwo przeoczyć.

**Smoke daje fałszywe poczucie bezpieczeństwa**, jeśli zestaw jest źle dobrany. Pięć testów
ma pokrywać **ścieżkę krytyczną**, a nie pięć losowych przypadków.

## Do dyskusji

- Co powinno decydować o tym, że test jest `@smoke`? Krytyczność ścieżki, czas wykonania,
  historia wykrywania błędów?
- Regresja na `main` znaczy, że błąd wykryty jest **po** scaleniu. Czy to akceptowalne?
  Co daje merge queue i czego wymaga?
- Nocny przebieg wykrywa problem rano. Kto na niego patrzy, jeśli nikt nie jest przypisany?
