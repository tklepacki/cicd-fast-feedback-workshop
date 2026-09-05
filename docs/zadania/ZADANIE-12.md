# ZADANIE 12 — Flaki: retry, kwarantanna i dryf środowiska

## Cel

Zająć się drugą połową tytułu warsztatu — **bez utraty jakości**. Szybki pipeline, któremu
nikt nie wierzy, jest gorszy od wolnego, któremu można ufać.

## Dlaczego to boli

Miejsce tego zadania nie jest przypadkowe. Właśnie zwiększyłeś równoległość — cztery workery,
cztery shardy, trzy przeglądarki. **Równoległość ujawnia flaki**, bo zmienia czasy: testy
rywalizują o CPU, odpowiedzi przychodzą w innej kolejności, a asercje, które dotąd zdążały,
przestają zdążać.

W konfiguracji stoi `retries: 0`, więc **każdy flak to czerwony build**. Zespół uczy się
klikać „re-run" bez patrzenia — i od tego momentu czerwony pipeline nie znaczy już nic.

### Trzy różne rzeczy nazywane tym samym słowem

| Rodzaj | Przyczyna | Czy retry pomoże |
|---|---|---|
| **Wyścig w teście** | asercja czyta stan, zanim dane dotrą | tak, i **maskuje błąd** |
| **Kolizja danych** | testy dzielą stan | tak, i **maskuje błąd** |
| **Dryf środowiska** | zmienił się runner, czcionki, przeglądarka | **nie, nigdy** |

Ostatni jest najpodlejszy: pipeline czerwieni się **bez żadnego commita do obwinienia**.

## Zadanie

**1. Włącz retry w CI** — dwie próby — i zrozum, co dokładnie kupujesz.

**2. Zobacz, że Playwright raportuje „flaky" osobno od „passed".** Test, który przeszedł
dopiero za drugim razem, **nie jest sukcesem** — jest sygnałem.

**3. Włącz `--fail-on-flaky-tests` na `main`**, żeby flaki nie przechodziły po cichu.

**4. Zbuduj kwarantannę.** Otaguj test `@flaky` i:
- wyłącz go z joba blokującego (`--grep-invert @flaky`),
- uruchamiaj w osobnym jobie z `continue-on-error: true`.

**5. Poluj na flaki.** Do nocnego przebiegu z ZADANIA 08 dodaj `--repeat-each=5`.

**6. Zajmij się dryfem środowiska.** Przypnij przeglądarkę do konkretnego obrazu:

```yaml
    container:
      image: mcr.microsoft.com/playwright:v1.62.1-noble
```

Zmierz. Porównaj z cache'em przeglądarek z ZADANIA 03. **Wynik Cię zaskoczy** —
i o to chodzi.

## Kryteria akceptacji

- [ ] `retries` w CI ustawione, lokalnie zero
- [ ] w raporcie widać kategorię „flaky" osobno
- [ ] job blokujący pomija testy `@flaky`
- [ ] osobny job uruchamia `@flaky` bez blokowania merge'a
- [ ] nocny przebieg używa `--repeat-each`
- [ ] job UI działa w przypiętym kontenerze
- [ ] potrafisz wyjaśnić, dlaczego kontener jest **wolniejszy niż cache** i mimo to lepszy

## Zmierz

| Co | Wartość |
|---|---|
| Instalacja przeglądarek z cache (ZADANIE 03) | ~8 s |
| Pobranie obrazu kontenera | ? |
| Czy kontener jest szybszy? | ? |
| Czy to rozstrzyga o wyborze? | ? |

<details>
<summary><b>Rozwiązanie</b></summary>

### Retry i kwarantanna

```ts
// playwright.config.ts
retries: process.env.CI ? 2 : 0,
```

```yaml
  test-ui:
    # ...
    run: npx playwright test --project=ui-chromium --grep-invert @flaky

  test-ui-quarantine:
    name: Testy w kwarantannie
    runs-on: ubuntu-latest
    needs: build
    # Quarantined tests report their result without blocking a merge. The alternative is
    # a permanently red pipeline that everyone learns to ignore, or a deleted test - and
    # a deleted test is a silent loss of coverage.
    continue-on-error: true
    steps:
      - run: npx playwright test --project=ui-chromium --grep @flaky
```

### Przypięty kontener

```yaml
  test-ui:
    runs-on: ubuntu-latest
    container:
      # Pinned deliberately. `npx playwright install` fetches a browser matching the
      # installed @playwright/test, but the fonts, codecs and system libraries around it
      # come from `ubuntu-latest` - a label GitHub moves underneath you. When the runner
      # image rolls forward and font rendering shifts, the pipeline turns red with no
      # commit to blame, and no retry helps: the cause is environment drift, not test code.
      image: mcr.microsoft.com/playwright:v1.62.1-noble
```

### Pomiary referencyjne

| Wariant | Przygotowanie przeglądarki | Cały przebieg |
|---|---|---|
| `npx playwright install` (baseline) | 52 s | 3:58 |
| Cache przeglądarek (ZADANIE 03) | **~8 s** | ~3:15 |
| Przypięty kontener | 27 s | 3:33 |

**Kontener jest wolniejszy od cache'u.** I mimo to jest właściwym wyborem.

Cache przyspiesza, ale **nie zamraża środowiska**: jego klucz obejmuje wersję Playwrighta,
nie system operacyjny. `ubuntu-latest` nadal przesuwa się pod spodem i pewnego dnia zmieni
renderowanie czcionek albo wersję biblioteki graficznej.

Przypięty tag zamraża komplet — przeglądarkę, system, czcionki, biblioteki. Te same bajty
dziś i za pół roku.

**Oddajesz kilkanaście sekund za determinizm.** To jest właściwy kompromis i najlepsza
ilustracja tezy tego warsztatu: *najszybsza opcja nie zawsze jest właściwa.*

</details>

## Pułapki

**Retry jako rozwiązanie.** `retries: 2` nie naprawia testu — wydłuża najgorszy przypadek
trzykrotnie i **ukrywa problem**. To środek przeciwbólowy, nie leczenie. Jedyne, co naprawdę
kupuje, to czas na diagnozę bez blokowania zespołu.

**Kwarantanna, która staje się śmietnikiem.** Test wrzucony do kwarantanny i zapomniany
to usunięte pokrycie w przebraniu. Potrzebny jest limit czasu — na przykład dwa tygodnie,
po których test wraca albo zostaje skasowany świadomie.

**`--fail-on-flaky-tests` na PR-ze bywa za ostre.** Na `main` ma sens: nie wypuszczamy
niepewnego stanu. Na PR-ze potrafi blokować z powodów niezwiązanych ze zmianą.

**Kontener nie usuwa flaków z kodu testów.** Zamraża środowisko, więc eliminuje **jedną**
z trzech przyczyn z tabeli na górze. Wyścigi i kolizje danych zostają Twoje.

## Do dyskusji

- **Pomiar z referencyjnego przebiegu:** job kwarantanny okazał się **najdłuższym jobem
  w całym pipelinie (0:58)** — mimo że nie uruchomił ani jednego testu. Pusty zestaw,
  a pełny start kontenera i instalacja zależności. Czy pusta kwarantanna powinna w ogóle
  startować? Jak byś to wykrył, nie wiedząc z góry, że jest pusta?

- Ten warsztat znalazł cztery prawdziwe flaki w testach, które wyglądały na stabilne —
  wyszły dopiero po zmianie liczby workerów i po dodaniu opóźnienia w API. **Co to mówi
  o teście, który „przechodzi"?**
- Gdzie jest granica między „naprawimy" a „usuwamy test"?
- Wzorzec „przeglądarka mieszka gdzie indziej" — osobny serwer przeglądarki w kontenerze,
  do którego testy łączą się przez `connectOptions` — rozwiązuje ten sam problem dryfu.
  Kiedy jest wart dodatkowej złożoności? (podpowiedź: gdy testy i aplikacja są na różnych
  maszynach, a przeglądarkę współdzieli wiele przebiegów)
