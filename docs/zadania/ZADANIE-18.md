# ZADANIE 18 — Bramka, uprawnienia i domknięcie

## Cel

Domknąć dzień: jedna bramka chroniąca `main`, najmniejsze potrzebne uprawnienia,
limity czasu — i porównanie z tym, od czego zaczynaliśmy.

## Dlaczego to boli

Pipeline jest szybki i czytelny, ale **niczego nie pilnuje**. Da się scalić PR-a
z czerwonymi testami — wystarczy kliknąć merge.

Naturalny odruch to oznaczyć wszystkie joby jako wymagane. Wpadniesz wtedy prosto
w pułapkę z ZADANIA 09:

> **`skipped` to nie `success`.**

Job `test-ui` pominięty przez filtr po ścieżkach **nigdy nie zaraportuje sukcesu**.
Ustawiony jako wymagany, zablokuje każdy PR, który nie dotyka `src/web/` — **na zawsze**.
Nie ma sposobu, żeby go odblokować poza usunięciem wymagania.

Do tego każdy job dostaje domyślnie szerszy zestaw uprawnień, niż potrzebuje,
i żaden nie ma limitu czasu — więc zawieszony job potrafi mielić sześć godzin.

## Zadanie

**1. Dodaj job `pipeline-status`**, który zależy od wszystkich pozostałych i agreguje
ich wyniki przez `needs.*.result`. **To on jest jedyną wymaganą kontrolą.**

**2. Obsłuż `skipped` poprawnie.** Pominięty job to nie porażka — ale `failure`
i `cancelled` już tak.

**3. Ustaw `permissions`** na poziomie workflow na `contents: read` i podnoś je
tylko tam, gdzie faktycznie trzeba.

**4. Dodaj `timeout-minutes`** do każdego joba. Domyślne sześć godzin to nie limit,
tylko brak limitu.

**5. Włącz ochronę `main`** w ustawieniach repozytorium: wymagany PR, wymagana kontrola
`pipeline-status`.

**6. Zrób porównanie.** Wypełnij tabelę baseline vs finał **własnymi** liczbami.

## Kryteria akceptacji

- [ ] `pipeline-status` agreguje wyniki i jest jedyną wymaganą kontrolą
- [ ] PR z pominiętym `test-ui` **da się** scalić
- [ ] PR z padającym testem **nie da się** scalić
- [ ] `permissions` zawężone na poziomie workflow
- [ ] każdy job ma `timeout-minutes`
- [ ] tabela porównawcza wypełniona własnymi pomiarami

## Zmierz — porównanie dnia

| | Baseline | Finał |
|---|---|---|
| Całkowity czas (`main`) | 3:58 | ? |
| Czas na PR-ze | 3:58 | ? |
| Czas do informacji o błędzie lintu | **nigdy** | ? |
| Czas do informacji o błędzie unit | 3:44 | ? |
| Czy wykrywa sekret w kodzie | **nie** | ? |
| Czy raport jest przy padających testach | **nie** | ? |
| Liczba kontroli na PR-ze | 1 | ? |

<details>
<summary><b>Rozwiązanie</b></summary>

```yaml
# Least privilege as the default. Individual jobs raise it where they must - the report
# job needs `checks: write`, and nothing else does.
permissions:
  contents: read

jobs:
  # ... pozostałe joby, każdy z timeout-minutes

  pipeline-status:
    name: Pipeline status
    runs-on: ubuntu-latest
    timeout-minutes: 5
    if: always()
    needs: [quality, unit, build, security, test-api, ui-report]
    steps:
      - name: Check results
        run: |
          # A skipped job is not a failure: path filters legitimately skip UI tests when
          # nothing they cover has changed. Requiring the skipped job itself would block
          # every such pull request permanently, because a skipped check never reports
          # success. This aggregate job is the required check instead.
          results='${{ join(needs.*.result, ' ') }}'
          echo "Wyniki jobów: $results"
          for result in $results; do
            case "$result" in
              success|skipped) ;;
              *) echo "::error::Job zakończył się wynikiem: $result"; exit 1 ;;
            esac
          done
          echo "Wszystkie kontrole przeszły."
```

### Ustawienia repozytorium

*Settings → Rules → New ruleset* (albo *Branches → Add rule* dla starszego interfejsu):

- **Target**: `main`
- **Require a pull request before merging**
- **Require status checks to pass** → dodaj **wyłącznie** `Pipeline status`
- opcjonalnie: **Require branches to be up to date before merging**

> Reguły ochrony gałęzi są dostępne w repozytoriach **publicznych** na koncie Free.
> Na prywatnym repozytorium darmowego konta ta część zadania jest niewykonalna —
> to jeden z powodów, dla których repozytorium warsztatowe jest publiczne.

### Wyniki referencyjne

Liczby zmierzone na `ubuntu-latest`, repozytorium publiczne (runy `33920530578`
i `33998317276`). U Ciebie mogą się różnić o kilkanaście procent — istotne są proporcje.

| | Baseline | Finał |
|---|---|---|
| Całkowity czas (`main`) | 3:58 | **1:50** |
| Czas na PR-ze | 3:58 | **~1:10** |
| Czas do informacji o błędzie lintu | nigdy | **~35 s** |
| Czas do informacji o błędzie unit | 3:44 | **~40 s** |
| Wykrywa sekret w kodzie | nie | **tak** |
| Raport przy padających testach | nie | **tak** |
| Liczba kontroli na PR-ze | 1 | 7 |

Warto zauważyć, że finałowy pipeline jest ponad dwa razy szybszy, **robiąc znacznie
więcej**: doszedł lint, typecheck, skan bezpieczeństwa, kontrola kontraktu API,
scalanie raportów i publikacja. Skrócenie czasu nie wzięło się z usunięcia pracy,
tylko z ułożenia jej równolegle i we właściwej kolejności.

</details>

## Pułapki

**Wymaganie pojedynczych jobów zamiast agregatu.** Najdroższy błąd w tym zadaniu.
Wymagana kontrola, która bywa pomijana, blokuje PR-y bez możliwości odblokowania.

**Zapomniane `if: always()` w agregacie.** Bez tego job nie uruchomi się po awarii
zależności — i wymagana kontrola nigdy nie zaraportuje wyniku. Ten sam efekt, inna przyczyna.

**Zbyt szerokie `permissions`.** `write-all` działa zawsze i jest zawsze złym pomysłem.
Zaczynaj od `contents: read` i podnoś punktowo.

**Nazwa kontroli w ustawieniach musi zgadzać się z `name:` joba**, a nie z jego kluczem
w YAML-u. Rozjazd oznacza wymaganą kontrolę, która nie istnieje — i PR-y zablokowane na zawsze.

## Do dyskusji

- Siedem kontroli na PR-ze to więcej informacji i więcej hałasu naraz. Gdzie jest granica
  czytelności?
- Wymagana bramka zakłada, że pipeline mówi prawdę. Co się dzieje, gdy zaczyna być flaky?
- **Trzy rzeczy, które zmienię w swoim pipelinie w poniedziałek** — wypisz je teraz,
  póki masz świeże liczby przed oczami.
