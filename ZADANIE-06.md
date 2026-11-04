# ZADANIE 06 — Skan bezpieczeństwa

## Cel

Dodać do pipeline’u kontrolę, której do tej pory brakowało i która pozwoli wykryć zmianę z tokenem płatniczym wpisanym bezpośrednio do kodu.

## Na czym polega problem

Pamiętasz integrację z bramką płatności z ZADANIA 01, czyli `demo/failing-security`? Ktoś w pośpiechu wkleił klucz API bezpośrednio do pliku `src/server/payments.ts`:

```ts
const PAYMENT_API_TOKEN = 'wshop_sk_live_8Kx2mQ7pLvN4rT9wZ3aB6cDe';
```

Pipeline przepuścił tę zmianę na zielono, ponieważ nie sprawdza dwóch rzeczy: **sekretów zapisanych w kodzie** oraz **znanych podatności w zależnościach**.

To inna klasa problemu niż wolny pipeline. Klucz, który trafił do repozytorium, trzeba traktować jako ujawniony. Każdy, kto ma dostęp do kodu albo jego kopii, może go odczytać i wykorzystać.

Samo usunięcie linijki z kodu nie wystarczy, ponieważ klucz nadal pozostaje w historii Git. Trzeba go unieważnić u dostawcy płatności i wygenerować nowy.

## Zadanie

Zmieniasz plik `.github/workflows/ci.yml`. Sekcje `on:` i `concurrency:` z ZADANIA 02 oraz joby z ZADAŃ 04–05 pozostają bez zmian.

**1. Dodaj job `Security`.** W sekcji `jobs:`, pod jobem `unit`, dodaj:

```yaml
  security:
    name: Security
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: actions/setup-node@v4
        with:
          node-version-file: .nvmrc
          cache: npm

      - run: npm ci

      - name: Known vulnerabilities in dependencies
        run: npm audit --audit-level=high

      - name: Install gitleaks
        run: |
          curl -sSL https://github.com/gitleaks/gitleaks/releases/download/v8.24.0/gitleaks_8.24.0_linux_x64.tar.gz \
            | tar -xz -C /usr/local/bin gitleaks

      - name: Secrets in the repository
        run: gitleaks detect --source . --config .gitleaks.toml --redact --verbose --log-opts="--first-parent HEAD"
```

Co jest tutaj ważne:

| Element | Po co |
|---|---|
| brak `needs` | skan bezpieczeństwa nie potrzebuje buildu ani testów, dlatego może wystartować od razu, równolegle z pozostałymi jobami |
| `npm audit --audit-level=high` | sprawdza znane podatności w zależnościach; job kończy się błędem dopiero wtedy, gdy znajdzie podatność na poziomie *high* lub wyższym |
| `fetch-depth: 0` | pobiera pełną historię repozytorium, dzięki czemu gitleaks może sprawdzić również wcześniejsze commity, a nie tylko aktualny stan plików |
| `.gitleaks.toml` | konfiguracja, która jest już w repozytorium; zawiera między innymi regułę wykrywającą warsztatowy format tokenu |
| `--redact` | ukrywa znaleziony sekret w logach; bez tej opcji narzędzie wykrywające wyciek mogłoby samo wypisać wartość tokenu do logu publicznego repozytorium |
| `--log-opts="--first-parent HEAD"` | ogranicza skanowanie historii do gałęzi, której dotyczy przebieg |

**2. Zatwierdź zmiany, wypchnij je na `main` i sprawdź przebieg.**

```bash
git add .github/workflows/ci.yml
git commit -m "Scan dependencies and secrets"
git push
```

W zakładce **Actions** otwórz nowy przebieg i sprawdź, że:

- `Security` startuje razem z `Lint and typecheck`, `Unit tests` i `Build`,
- `Security` jest zielony — na `main` nie ma żadnego sekretu,
- `Security` kończy się wcześniej niż `UI tests`.

Jeśli `Security` jest na `main` czerwony, sprawdź, który krok zakończył się błędem. Jeśli `Known vulnerabilities in dependencies`, to `npm audit` znalazł nową podatność w którejś z zależności — daj znać prowadzącemu.

Zapisz w `docs/baseline.md` czas joba `Security` oraz całkowity czas przebiegu.

**3. Sprawdź zmianę w płatnościach.** Przenieś zmianę na nową gałąź utworzoną z `main` i otwórz pull request, tak samo jak w poprzednich zadaniach:

```bash
git checkout -b check-payments
git checkout warsztat/demo/failing-security -- src/server/payments.ts
git commit -m "Payment integration to verify"
git push -u origin check-payments
```

Otwórz pull request z `check-payments` do `main`. Na liście kontroli czerwony powinien być tylko `Security`. Otwórz ten job i rozwiń krok `Secrets in the repository`. W logu sprawdź, że:

- widoczna jest nazwa pliku: `src/server/payments.ts`,
- widoczna jest nazwa reguły: `workshop-api-token`,
- zamiast wartości tokenu pojawia się `REDACTED`.

Zapisz, po ilu sekundach od startu przebiegu job `Security` kończy się błędem. Pull requesta nie scalaj.

**4. Zdecyduj: blokować czy ostrzegać?** Zapisz w `docs/baseline.md` jedno zdanie: czy według Ciebie job `Security` powinien blokować scalenie pull requesta, czy tylko ostrzegać, oraz dlaczego. Wrócimy do tego podczas omówienia.

**5. Wróć na `main`:**

```bash
git checkout main
```

## Kryteria akceptacji

- [ ] job `Security` nie ma `needs` i startuje razem z pozostałymi jobami (krok 2)
- [ ] na `main` `Security` jest zielony (krok 2)
- [ ] `Security` kończy się wcześniej niż `UI tests` (krok 2)
- [ ] zmiana w płatnościach kończy się błędem na kontroli `Security` (krok 3)
- [ ] log pokazuje nazwę pliku i regułę, ale nie ujawnia wartości tokenu (krok 3)

## Zmierz

| Co | Po ZADANIU 05 | Po ZADANIU 06 |
|---|---|---|
| Czas do informacji o tokenie w kodzie | **nigdy** | ? |
| Czas joba `Security` | — | ? |
| Czas całego przebiegu | ? | ? |
