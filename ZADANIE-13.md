# ZADANIE 13 — Trace: „błąd w CI, co teraz?"

## Cel

Domknąć całą pętlę. Przez cały dzień skupiamy się na tym, jak **szybko dostać czerwony sygnał**.
Teraz zajmiemy się tym, co zrobić dalej. Szybki pipeline niewiele daje, jeśli po błędzie nadal
nie wiadomo, gdzie szukać przyczyny.

## Na czym polega problem

Zmiana w etykiecie „Ostatnie sztuki” z ZADANIA 01 psuje jeden test UI. W logu widać tylko:

```
Error: expect(locator).toHaveText(expected) failed
Expected: "Ostatnie sztuki: 2"
Timeout: 5000ms
Error: element(s) not found
```

Wiemy więc, że elementu nie ma na stronie, ale nie wiemy dlaczego. Czy API nie zwróciło
produktu? Czy aplikacja go dostała, ale nie wyświetliła etykiety? Czy aplikacja w ogóle
poprawnie wstała?

Typowa reakcja to dopisanie `console.log`, wypchnięcie zmiany, czekanie na kolejny przebieg
i ponowne sprawdzenie wyniku. Kilka takich iteracji potrafi kosztować kilkanaście minut.
**Trace** pozwala zebrać te informacje od razu. To zapis przebiegu testu: kolejne akcje, stan
strony przed nimi i po nich, zapytania sieciowe, logi konsoli i miejsce w kodzie testu,
w którym wystąpił błąd.

## Zadanie

Zmieniasz `playwright.config.ts` i job `test-ui` w `.github/workflows/ci.yml`.

**1. Wywołaj błąd.** Użyj gałęzi `check-catalog` z ZADAŃ 09 i 11. Najpierw przenieś na nią
aktualną wersję pipeline'u:

```bash
git checkout check-catalog
git merge --no-edit main
git push
git checkout main
```

Następnie w zakładce **Actions** wybierz **CI** i kliknij **Run workflow**:

- w **Use workflow from** wybierz `check-catalog`,
- w **UI test scope** wybierz `all`,
- uruchom workflow.

Po zakończeniu przebiegu zapisz w `docs/baseline.md` rozmiary artefaktów z sekcji **Artifacts**:
`playwright-report` i `blob-report-*`. Na tym etapie jest ustawione `trace: 'on'`, więc
Playwright zapisuje trace dla **każdego** testu.

**2. Znajdź trace testu z błędem.** Pobierz `playwright-report`, rozpakuj i otwórz
`index.html`. Znajdź czerwony test *marks a product with only a few left*, otwórz jego
szczegóły, przewiń do sekcji **Traces** i kliknij trace. Otworzy się przeglądarka trace'ów.

Możesz też otworzyć plik `trace.zip` lokalnie poleceniem:

```bash
npx playwright show-trace path/to/trace.zip
```

albo przeciągnąć go na [trace.playwright.dev](https://trace.playwright.dev) — narzędzie działa
w przeglądarce, a dane trace'a nie są wysyłane na serwer.

**3. Znajdź przyczynę bez zmieniania kodu.** Przeglądarka trace'ów pokazuje kilka źródeł informacji:

| Panel | Co pokazuje |
|---|---|
| oś czasu (u góry) i lista akcji (po lewej) | kolejne kroki wykonane przez test i czas ich trwania |
| snapshot (środek) | stan strony **przed** wybraną akcją i **po** niej |
| Network | żądania sieciowe, kody odpowiedzi i ich zawartość |
| Console | komunikaty z konsoli przeglądarki |
| Source | kod testu i linię, na której wystąpił błąd |

Na podstawie trace'a odpowiedz w `docs/baseline.md` na trzy pytania:

- czy zapytanie do API o produkty się powiodło i co zwróciło dla produktu `p-012`?
- czy na stronie jest element z etykietą „Ostatnie sztuki”, czy go nie ma wcale?
- skoro dane są takie, jakie są, a strona wygląda tak, jak wygląda — w którym miejscu kodu
  szukać przyczyny?

Na koniec otwórz wskazany plik i sprawdź, czy rzeczywiście tam jest problem.

**4. Zachowuj trace tylko wtedy, gdy jest potrzebny.** W `playwright.config.ts` znajdź:

```ts
    trace: 'on',
```

i zamień na:

```ts
    trace: 'retain-on-failure',
```

| Ustawienie | Kiedy zapisuje | Koszt |
|---|---|---|
| `on` | zawsze, dla każdego testu | najwyższy — pełna regresja daje trace dla wszystkich 123 testów, choć zwykle interesuje nas kilka z błędem |
| `retain-on-failure` | nagrywa każdy test, a po przebiegu zostawia tylko trace'y testów, które nie przeszły | średni — nadal płacimy za nagrywanie, ale nie przechowujemy danych z zielonych testów |
| `on-first-retry` | dopiero przy pierwszej powtórce testu | najniższy — ale wymaga włączonego `retries`; u nas `retries: 0`, więc nie zapisałby żadnego trace'a |

W tym zadaniu wybieramy `retain-on-failure`.

**5. Publikuj trace tylko przy błędzie.** Na samym końcu joba `test-ui` dopisz:

```yaml
      - name: Upload traces
        uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: traces-${{ matrix.shard }}
          path: test-results/
          retention-days: 14
```

`if: failure()` sprawia, że artefakt powstaje tylko dla sharda, który zakończył się błędem —
zielone shardy nie tworzą dodatkowych artefaktów. Trace przechowujemy przez 14 dni, bo do
materiałów diagnostycznych często wraca się kilka dni po przebiegu.

**6. Zatwierdź zmiany i porównaj wynik.**

```bash
git add playwright.config.ts .github/workflows/ci.yml
git commit -m "Keep traces only for failing tests and upload them on failure"
git push
git checkout check-catalog
git merge --no-edit main
git push
git checkout main
```

Ponownie uruchom **Run workflow** na gałęzi `check-catalog` z zakresem `all`. Sprawdź, że:

- w **Artifacts** jest artefakt `traces-N` tylko dla sharda, który zakończył się błędem,
- w środku jest trace testu z błędem,
- artefakty `playwright-report` i `blob-report-*` są wyraźnie mniejsze niż przy `trace: 'on'` w kroku 1.

Na `main`, gdzie wszystkie testy są zielone, nie powinien powstać żaden artefakt `traces-*`.

## Kryteria akceptacji

- [ ] trace testu z błędem jest otwarty lokalnie albo w trace.playwright.dev (krok 2)
- [ ] przyczyna błędu jest ustalona bez dopisywania logów i bez uruchamiania testu tylko po to, żeby zebrać więcej informacji (krok 3)
- [ ] na podstawie trace'a wskazane jest zapytanie sieciowe i dane zwrócone przez API (krok 3)
- [ ] trace zostaje tylko dla testów z błędem (kroki 4 i 6)
- [ ] artefakt z trace'em powstaje tylko dla sharda, który zakończył się błędem (kroki 5–6)
- [ ] rozmiary artefaktów przed zmianą i po niej są zapisane (kroki 1 i 6)

## Zmierz

| Co | `trace: 'on'` | `retain-on-failure` |
|---|---|---|
| Rozmiar `playwright-report` | ? | ? |
| Suma rozmiarów `blob-report-*` | ? | ? |
| Artefakt z trace'ami na zielonym `main` | — | ? |
| Czas od otwarcia trace'a do znalezienia przyczyny | ? | — |
