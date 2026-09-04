# ZADANIE 15 — Trace: „padło w CI, co teraz?"

## Cel

Domknąć pętlę. Cały dzień uczy, jak **szybko dostać czerwony sygnał** — i ani razu nie mówi,
co z nim zrobić. Bez tego zadania wracasz do pracy z szybszym pipelinem i tą samą bezradnością
wobec padającego testu.

## Dlaczego to boli

Test UI pada w CI. Lokalnie przechodzi. Masz do dyspozycji log, w którym widnieje:

```
Error: expect(locator).toHaveText(expected) failed
Expected: "Ostatnie sztuki: 2"
Received: ""
```

Z tego nie wynika **nic** o przyczynie. Czy element się nie pojawił? Pojawił się pusty?
Zapytanie zwróciło błąd? Aplikacja w ogóle wstała?

Klasyczna reakcja to dopisanie `console.log`, push, czekanie cztery minuty, powtórka.
Trzy takie iteracje to kwadrans na zdobycie informacji, którą trace ma od początku.

## Zadanie

**1. Wywołaj prawdziwy błąd.** Repozytorium ma branch z jednym padającym testem UI:

```bash
git checkout demo/failing-ui
git push origin demo/failing-ui
```

**2. Pobierz artefakt z trace'em** z zakładki Actions.

**3. Otwórz trace:**

```bash
npx playwright show-trace ścieżka/do/trace.zip
```

Można też przeciągnąć plik na [trace.playwright.dev](https://trace.playwright.dev) —
działa w przeglądarce, nic nie wysyła na serwer.

**4. Znajdź przyczynę, korzystając z tego, co trace daje:**

| Panel | Co pokazuje |
|---|---|
| oś czasu | każda akcja i jej czas trwania |
| snapshot DOM | stan strony **przed** i **po** akcji |
| Network | wszystkie zapytania z kodami odpowiedzi |
| Console | logi przeglądarki |
| Source | linijka testu, która padła |

**5. Odpowiedz na trzy pytania:** Czy zapytanie do API się powiodło? Co zwróciło?
Czy element istniał, ale był pusty, czy nie istniał wcale?

**6. Sprawdź ustawienia trace'a.** W `playwright.config.ts` porównaj `on`,
`retain-on-failure` i `on-first-retry`. Który wybrać i dlaczego?

## Kryteria akceptacji

- [ ] trace otwarty lokalnie
- [ ] przyczyna błędu z `demo/failing-ui` ustalona **bez** dopisywania `console.log`
- [ ] potrafisz wskazać zapytanie sieciowe, które za to odpowiada
- [ ] rozumiesz różnicę między trybami zapisu trace'a
- [ ] trace jest zapisywany tylko dla padających testów

## Zmierz

| Co | Wartość |
|---|---|
| Czas od pobrania artefaktu do znalezienia przyczyny | ? |
| Ile iteracji „dopisz log i wypchnij" zaoszczędzone | ? |
| Rozmiar trace'a przy `trace: 'on'` | ? |
| Rozmiar przy `retain-on-failure` | ? |

<details>
<summary><b>Rozwiązanie</b></summary>

### Przyczyna błędu na `demo/failing-ui`

Test *„marks a product with only a few left"* oczekuje etykiety `Ostatnie sztuki: 2`
przy produkcie `p-012`.

Trace pokazuje:
- **Network**: zapytanie `GET /api/products?search=Hotfix` zwróciło **200** z produktem
  `p-012` i polem `stock: 2` — dane są poprawne;
- **snapshot DOM**: karta produktu istnieje, ale **nie ma w niej elementu**
  `[data-testid="low-stock"]`;
- **Source**: asercja czekała pięć sekund i element się nie pojawił.

Skoro dane są dobre, a element nie powstaje, przyczyna jest w warunku renderowania.
W `src/web/views/Catalog.tsx`:

```tsx
{product.stock > 0 && product.stock <= 1 && (   // było: <= 3
```

Próg został zmieniony, więc produkt ze stanem `2` przestał spełniać warunek.
**Ustalone bez uruchamiania czegokolwiek lokalnie.**

### Tryby zapisu trace'a

| Ustawienie | Kiedy zapisuje | Koszt | Kiedy używać |
|---|---|---|---|
| `on` | zawsze | **wysoki** — trace dla każdego testu | debugowanie lokalnie |
| `retain-on-failure` | tylko dla padających | niski | **domyślny wybór dla CI** |
| `on-first-retry` | dopiero przy ponowieniu | najniższy | gdy retry są włączone |

Przy `retries: 2` z ZADANIA 12 `on-first-retry` jest kuszący, bo zapisuje najmniej.
Ma jednak wadę: **test, który padł raz i przeszedł za drugim razem, nie zostawi trace'a
z pierwszego przebiegu** — czyli tego, który był interesujący.

</details>

## Pułapki

**`trace: 'on'` w CI.** Trace dla 123 testów to setki megabajtów artefaktów za informację
przydatną w jednym przypadku.

**Trace bez map źródeł** pokazuje zbudowany kod zamiast źródeł. W tym projekcie Vite generuje
mapy w trybie deweloperskim; w produkcyjnym buildzie ich nie ma.

**Otwieranie trace'a przez rozpakowanie ZIP-a.** To nie jest zwykłe archiwum do przeglądania —
używaj `show-trace` albo przeglądarki traców.

**Trace to nie nagranie wideo.** To zapis akcji ze snapshotami DOM. Widać stan przed i po
każdej akcji, ale nie płynny przebieg — i to zwykle wystarcza.

## Do dyskusji

- Ile razy w ostatnim miesiącu debugowałeś błąd z CI przez dopisywanie logów i push?
  Ile czasu zajęła jedna taka iteracja?
- Trace pokazuje stan przeglądarki. Czego **nie** pokaże? (podpowiedź: stanu serwera,
  zawartości bazy, logów aplikacji)
- Gdyby trace był dostępny dla **wszystkich** przebiegów przez 30 dni — co dałoby się
  wtedy analizować, czego dziś nie da się wcale?
