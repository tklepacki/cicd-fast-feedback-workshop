# ZADANIE 07 — Kontrakt API i zmiany łamiące

## Cel

Dodać najtańszą kontrolę w całym pipelinie: porównanie specyfikacji API z gałęzią bazową
i zablokowanie zmian, które łamią kontrakt.

## Dlaczego to boli

Aplikacja wystawia swój kontrakt pod `/api/openapi.json`, a klikalną dokumentację
pod `/api/docs`. Ktoś zmienia nazwę pola w odpowiedzi, usuwa parametr albo zawęża typ.

Testy API mogą tego **nie zauważyć** — sprawdzają zachowanie, które same opisują.
Testy UI zauważą, ale dopiero po dwóch minutach i w postaci „nie znaleziono elementu",
czyli komunikatu wskazującego **skutek zamiast przyczyny**.

A konsument tego API — inny zespół, aplikacja mobilna, integracja partnera — dowie się
najpóźniej i najboleśniej.

Zmiana łamiąca kontrakt to defekt, który da się wykryć w kilkanaście sekund, porównując
dwa pliki JSON.

## Zadanie

**1. Zrozum, dlaczego `npm run openapi:dump` nie podnosi serwera.**

Zajrzyj do `scripts/dump-openapi.mjs`. Gdyby spec dało się pobrać tylko z działającej
aplikacji, ten check przestałby być tani — a cała jego wartość polega na tym, że kosztuje
kilkanaście sekund i biegnie równolegle z lintem.

**2. Dodaj job `api-contract`**, który:
- generuje spec dla gałęzi bazowej,
- generuje spec dla wersji z PR-a,
- porównuje oba narzędziem [`oasdiff`](https://github.com/oasdiff/oasdiff),
- pada, gdy wykryto zmianę łamiącą.

**3. Sprawdź, że działa.** Zepsuj kontrakt celowo — na przykład w `src/server/openapi.ts`
zmień nazwę pola `total` na `totalCount` w schemacie `ProductSlice`, albo usuń parametr
`search`. Otwórz PR i zobacz wynik.

**4. Sprawdź też przypadek odwrotny:** dodanie **nowego, opcjonalnego** parametru
nie powinno niczego blokować.

## Kryteria akceptacji

- [ ] job `api-contract` istnieje i uruchamia się dla `pull_request`
- [ ] usunięcie pola z odpowiedzi **blokuje** PR
- [ ] dodanie opcjonalnego parametru **nie blokuje** PR-a
- [ ] w logach widać, **co konkretnie** się zmieniło, nie samo „breaking change detected"
- [ ] job kończy się szybciej niż testy API

## Zmierz

| Co | Wartość |
|---|---|
| Czas joba `api-contract` | ? |
| Czas do informacji o zmianie łamiącej | ? |
| Ile trwałoby dowiedzenie się z testów UI | ~2:30 |

<details>
<summary><b>Rozwiązanie</b></summary>

```yaml
  api-contract:
    name: Kontrakt API
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'
    steps:
      - uses: actions/checkout@v4
        with:
          # Both revisions are needed: the base branch and the pull request head.
          fetch-depth: 0

      - uses: actions/setup-node@v4
        with:
          node-version-file: .nvmrc
          cache: npm

      - run: npm ci

      - name: Contract from the base branch
        run: |
          git checkout "origin/${{ github.base_ref }}" -- src/server/openapi.ts
          npm run build:server
          node scripts/dump-openapi.mjs /tmp/openapi-base.json
          git checkout HEAD -- src/server/openapi.ts

      - name: Contract from the pull request
        run: |
          npm run build:server
          node scripts/dump-openapi.mjs /tmp/openapi-head.json

      - name: Detect breaking changes
        uses: oasdiff/oasdiff-action/breaking@main
        with:
          base: /tmp/openapi-base.json
          revision: /tmp/openapi-head.json
          fail-on: ERR
```

### Co `oasdiff` uznaje za zmianę łamiącą

| Zmiana | Łamiąca? |
|---|---|
| usunięcie pola z odpowiedzi | **tak** — konsument może na nim polegać |
| usunięcie parametru zapytania | **tak** |
| dodanie **wymaganego** pola do żądania | **tak** — stare żądania przestaną działać |
| dodanie **opcjonalnego** parametru | nie |
| dodanie pola do odpowiedzi | nie |
| poszerzenie zakresu enum w odpowiedzi | **tak** — konsument może nie znać nowej wartości |
| zawężenie zakresu enum w żądaniu | **tak** |

Ostatnie dwa bywają zaskoczeniem i są dobrym materiałem na dyskusję.

</details>

## Pułapki

**Brak `fetch-depth: 0`.** Bez pełnej historii nie ma dostępu do gałęzi bazowej,
a `git checkout origin/main` po prostu się nie powiedzie.

**Kontrakt generowany z działającej aplikacji.** Gdyby spec trzeba było pobrać z `/api/openapi.json`
uruchomionego serwera, job musiałby zbudować aplikację, uruchomić ją i odczekać na gotowość —
i z kilkunastu sekund zrobiłaby się minuta. Dlatego `dump-openapi.mjs` importuje dokument
bezpośrednio.

**Traktowanie każdej zmiany łamiącej jako błędu.** Czasem łamiesz kontrakt **świadomie**,
bo wersja API idzie do przodu. Potrzebna jest wtedy droga ucieczki — patrz dyskusja.

## Do dyskusji

- **Jak przepuścić świadomą zmianę łamiącą?** Etykieta na PR-ze (`breaking-change`) sprawdzana
  w `if:`, osobny plik z uzasadnieniem, czy `continue-on-error` z ostrzeżeniem? Każde ma wadę.
- Ten check porównuje z gałęzią bazową. A co z kontraktem, który konsument **realnie ma
  wdrożony** — bywa nim wersja sprzed miesiąca, nie dzisiejszy `main`.
- Kontrakt trzymamy jako obiekt TypeScript, więc `npm run typecheck` pilnuje spójności nazw
  ze zmianami w kodzie. Co byłoby tańsze, a co droższe, gdyby był osobnym plikiem YAML?
