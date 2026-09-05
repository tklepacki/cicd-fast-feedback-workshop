# ZADANIE 11 — Matrix, który liczy sam siebie

## Cel

Zobaczyć `matrix` jako **mechanizm ogólny**, a nie synonim shardowania, i uzależnić liczbę
shardów od tego, co pipeline właśnie robi.

## Dlaczego to boli

Po ZADANIU 10 testy UI dzielą się na cztery shardy — **zawsze cztery**, niezależnie od tego,
czy uruchamiamy pięć testów smoke, czy pełną regresję.

Na pull requeście to jest strata. Pięć testów rozdzielonych na cztery maszyny oznacza,
że każda z nich spędza więcej czasu na starcie — checkout, `npm ci`, pobranie artefaktu —
niż na testowaniu. Płacisz za cztery maszyny, żeby uruchomić jeden test na każdej.

Na `main`, gdzie idzie pełna regresja, cztery shardy to z kolei za mało.

Liczba shardów jest wpisana na sztywno, bo `matrix` wygląda na coś, co musi być stałą listą.
Nie musi.

## Zadanie

**1. Uzależnij liczbę shardów od zdarzenia.** Dwa shardy dla `pull_request`, osiem dla reszty.

Kluczem jest `fromJSON`: matrixa nie da się policzyć wyrażeniem, ale **można mu podać
tablicę JSON zbudowaną przez wyrażenie**.

**2. Zadbaj o mianownik.** `--shard=3/4` przestaje mieć sens, gdy shardów jest osiem.
Liczba w mianowniku musi zmieniać się razem z rozmiarem matrixa.

**3. Zadbaj o nazwy artefaktów**, żeby osiem shardów nie zderzyło się nazwami.

**4. Policz joby.** Przy ośmiu shardach sprawdź w zakładce Actions, ile jobów startuje
jednocześnie i ile zostaje do limitu **20 na koncie**.

**5. Zmierz oba tryby.** Odpal raz jako PR, raz na `main`, i porównaj czas oraz zużycie minut.

## Kryteria akceptacji

- [ ] pull request uruchamia **dwa** shardy, push na `main` — **osiem**
- [ ] mianownik w `--shard` odpowiada rzeczywistej liczbie shardów w obu trybach
- [ ] artefakty z ośmiu shardów nie kolidują nazwami
- [ ] w nazwie joba widać, który to shard i z ilu
- [ ] policzone, ile jobów działa równolegle w trybie `main`

## Zmierz

| Co | PR (2 shardy) | main (8 shardów) |
|---|---|---|
| Czas najdłuższego sharda | ? | ? |
| Czas całego etapu UI | ? | ? |
| Suma zużytych minut | ? | ? |
| Jobów równolegle w szczycie | ? | ? |

<details>
<summary><b>Rozwiązanie</b></summary>

```yaml
  test-ui:
    name: UI ${{ github.event_name == 'pull_request' && 2 || 8 }} × ${{ matrix.shard }}
    runs-on: ubuntu-latest
    needs: [build, changes]
    if: needs.changes.outputs.ui == 'true'
    strategy:
      fail-fast: false
      matrix:
        # A matrix cannot be computed with an expression, but it can be handed a JSON
        # array built by one. That is the whole trick.
        shard: >-
          ${{ fromJSON(github.event_name == 'pull_request'
              && '[1,2]'
              || '[1,2,3,4,5,6,7,8]') }}
    steps:
      # ...
      - name: UI tests
        run: >-
          npx playwright test --project=ui-chromium
          --shard=${{ matrix.shard }}/${{ github.event_name == 'pull_request' && 2 || 8 }}
          ${{ env.GREP }}
```

### Dlaczego `fromJSON`

`matrix.shard` musi być listą. Wyrażenie `${{ ... }}` zwraca **napis**, więc bez konwersji
GitHub dostałby jeden element o wartości `"[1,2]"` zamiast dwóch shardów.
`fromJSON` zamienia ten napis z powrotem w tablicę.

### Mianownik w dwóch miejscach

Wyrażenie `github.event_name == 'pull_request' && 2 || 8` powtarza się w nazwie joba
i w poleceniu. To zapach — i słusznie. Można je wynieść do `env` na poziomie workflow:

```yaml
env:
  SHARD_TOTAL: ${{ github.event_name == 'pull_request' && 2 || 8 }}
```

</details>

## Pułapki

**Matrix mnoży.** Każdy dodany wymiar mnoży liczbę jobów przez swoją długość, a nie dodaje.
Dwa wymiary po cztery wartości to szesnaście maszyn, nie osiem. Przy limicie **20 jobów
na koncie** — który liczy się dla wszystkich repozytoriów łącznie — łatwo o tę granicę zawadzić
i zacząć kolejkować samemu sobie.

**Mianownik rozjeżdża się z matrixem.** Zmiana listy shardów bez zmiany `--shard=x/N` daje
najgorszy możliwy wynik: pipeline świeci na zielono, a **część testów nigdy się nie uruchomiła**.
Nic nie pada, więc nikt nie zauważa.

**Więcej shardów nie zawsze znaczy szybciej.** Każdy shard płaci pełny narzut startu.
W pewnym momencie dokładanie maszyn przestaje skracać czas, a zaczyna tylko zwiększać
rachunek za minuty. Punkt, w którym to następuje, wyznacza się pomiarem, nie intuicją.

## Do dyskusji

- Gdzie w Twoim projekcie liczba shardów powinna zależeć od kontekstu, a gdzie stała
  wartość jest w porządku?
- `fromJSON` pozwala zbudować matrixa z czegokolwiek — także z wyniku poprzedniego joba
  przez `outputs`. Jakie zastosowania to otwiera?
- Osiem shardów, z których każdy startuje minutę, to osiem minut narzutu na jeden przebieg.
  Kiedy przestaje się to opłacać?
