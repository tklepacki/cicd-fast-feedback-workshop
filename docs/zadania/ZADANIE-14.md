# ZADANIE 14 — Raportowanie w GitHubie: jeden format dla wszystkich testów

## Cel

Doprowadzić do stanu, w którym wynik testów widać **bez pobierania czegokolwiek**.

## Dlaczego to boli

Masz trzy rodzaje testów i każdy raportuje inaczej:

| Rodzaj | Jak dziś poznajesz wynik |
|---|---|
| jednostkowe | tekst w logu |
| API | tekst w logu |
| UI | artefakt do pobrania i rozpakowania |

Żeby dowiedzieć się, co padło, trzeba wejść w run, znaleźć właściwy job, rozwinąć krok
i przeczytać log — albo pobrać archiwum. **To jest tarcie**, przez które ludzie przestają
patrzeć na wyniki i wracają do pytania „u mnie działa".

## Zadanie

Cztery poziomy widoczności tego samego wyniku, każdy dla innego odbiorcy.

**1. Wspólny format.** Niech wszystkie trzy rodzaje testów emitują **JUnit XML** do `reports/`.
Vitest przez `--reporter=junit`, Playwright przez reporter `junit`.

**2. Check run.** Dodaj `dorny/test-reporter@v3` z `path: 'reports/*.xml'`.
Wymaga uprawnień `checks: write` i `actions: read` — to pierwszy raz, gdy `permissions:`
ma konsekwencję, a nie jest dobrą praktyką na zapas.

**3. Job Summary.** Napisz `scripts/ci-summary.mjs`, który czyta JUnit i wypisuje tabelę
do `$GITHUB_STEP_SUMMARY`.

**4. Artefakty jak należy.** Napraw defekt z baseline: `if: always()` na uploadach,
sensowne `retention-days`, trace **tylko dla padających testów**.

## Kryteria akceptacji

- [ ] wszystkie trzy rodzaje testów produkują JUnit XML
- [ ] check run pokazuje listę testów z podziałem na przechodzące i padające
- [ ] Job Summary zawiera tabelę z liczbami
- [ ] przy padających testach artefakty **istnieją**
- [ ] trace jest wgrywany tylko dla padających testów
- [ ] wynik da się odczytać **bez pobierania czegokolwiek**

## Zmierz

| Co | Przed | Po |
|---|---|---|
| Kliknięć do odczytania, co padło | ? | ? |
| Czy trzeba coś pobierać | tak | ? |
| Rozmiar artefaktów | ? | ? |

<details>
<summary><b>Rozwiązanie</b></summary>

```ts
// playwright.config.ts
reporter: process.env.CI
  ? [
      ['blob'],
      ['github'],                                          // annotations in the PR diff
      ['junit', { outputFile: 'reports/playwright.xml' }],  // machine-readable, shared format
    ]
  : [['list'], ['html', { open: 'never' }]],

use: {
  baseURL,
  // 'on' in the baseline meant a trace for every test, including the 122 that passed.
  // Traces are heavy; keeping them only where they help costs nothing and saves a lot.
  trace: 'retain-on-failure',
  screenshot: 'only-on-failure',
},
```

```json
"test:unit": "vitest run --reporter=default --reporter=junit --outputFile=reports/unit.xml"
```

```yaml
  test-report:
    name: Raport z testów
    runs-on: ubuntu-latest
    needs: [unit, test-api, ui-report]
    if: always()
    permissions:
      contents: read
      actions: read
      checks: write        # required by dorny/test-reporter to create a check run
    steps:
      - uses: actions/download-artifact@v4
        with:
          pattern: junit-*
          path: reports
          merge-multiple: true

      - name: Publish check run
        uses: dorny/test-reporter@v3
        if: always()
        with:
          name: Wyniki testów
          path: 'reports/*.xml'
          reporter: java-junit

      - name: Job summary
        if: always()
        run: node scripts/ci-summary.mjs reports/*.xml >> "$GITHUB_STEP_SUMMARY"
```

### Cztery poziomy i po co każdy

| Poziom | Odbiorca | Co daje |
|---|---|---|
| reporter `github` | autor PR-a | adnotacja **przy linijce** w diffie |
| check run (`dorny`) | recenzent | lista testów z podziałem, bez wchodzenia w logi |
| Job Summary | każdy patrzący na run | tabela z liczbami na wierzchu |
| artefakty | ktoś, kto debuguje | trace, zrzuty, pełny raport HTML |

Reporter `github` i check run **nie są tym samym**. Pierwszy daje adnotacje w diffie,
drugi ustrukturyzowaną listę. Warto mieć oba.

</details>

## Pułapki

**`dorny/test-reporter` nie działa dla PR-ów z forków.** Token jest wtedy tylko do odczytu
i nie może utworzyć check runu. U nas działa, bo pracujemy we własnym repozytorium —
ale w projekcie przyjmującym PR-y z zewnątrz trzeba wzorca `workflow_run`.

**Brakujące `permissions`.** Bez `checks: write` akcja kończy się błędem uprawnień,
a komunikat nie mówi wprost, czego brakuje.

**`trace: 'on'` w baseline** oznaczał trace dla 123 testów, w tym 122 przechodzących.
Trace'y są ciężkie i to one zjadają storage.

**JUnit z Playwrighta a `reporter: java-junit`.** Nazwa myli — to po prostu parser JUnit XML,
nie coś specyficznego dla Javy.

## Do dyskusji

- Cztery poziomy widoczności to cztery miejsca do utrzymania. Który wyciąłbyś pierwszy?
- Adnotacja przy linijce w diffie jest najbliżej autora. Dlaczego więc nie wystarcza?
- Retencja artefaktów to koszt kontra możliwość diagnozy po fakcie. Ile dni ma sens
  dla trace'ów, a ile dla raportu?
