# ZADANIE 01 — Baseline i pomiar

## Cel

Zmierzyć stan wyjściowy pipeline'u i ustalić metrykę, którą będziemy poprawiać przez cały dzień.

Nie zmieniasz w tym zadaniu **ani jednej linijki** `ci.yml`. Optymalizowanie czegoś, czego się
nie zmierzyło, to zgadywanie — a pod koniec dnia i tak nie da się powiedzieć, co pomogło.

## Dlaczego to boli

Pipeline w `.github/workflows/ci.yml` działa. Robi checkout, instaluje zależności, uruchamia
wszystkie testy i wrzuca raport. Nikt nie powie, że jest zepsuty.

A jednak: pull request czeka na wynik kilka minut, i przez ten czas **nie wiesz nic** —
ani czy kod się kompiluje, ani czy przechodzi lint, ani czy testy jednostkowe są zielone.
Dowiesz się wszystkiego naraz, na końcu.

## Zadanie

**1. Uruchom pipeline i poczekaj na wynik.**

Wypchnij dowolną drobną zmianę na swój branch (na przykład dopisz linijkę do `README.md`)
albo uruchom workflow ręcznie z zakładki **Actions**.

**2. Odczytaj czasy poszczególnych kroków.**

Wejdź w run → job `test` → rozwiń kolejne kroki. Przy każdym jest czas trwania.
Przepisz je do tabeli w `docs/baseline.md` (plik utwórz).

**3. Zmierz „czas do pierwszego czerwonego sygnału".**

To będzie **główna metryka dnia**. Przełącz się na branch z celowo zepsutym testem
jednostkowym i zobacz, po ilu minutach pipeline o tym powie:

```bash
git checkout demo/failing-unit
git push origin demo/failing-unit
```

Zapisz: ile trwa sam test jednostkowy, a ile trzeba czekać, żeby zobaczyć jego wynik.

**4. Sprawdź dwa branche, które *nie* powinny przejść.**

```bash
git checkout demo/failing-lint       # zepsuty lint
git checkout demo/failing-security   # token API w kodzie
```

Wypchnij oba i zobacz, co zrobi pipeline. **Wynik Cię zaskoczy** — zanotuj go
i zastanów się, dlaczego tak jest.

**5. Wypisz pięć problemów**, które widzisz w tym pipelinie. Do `docs/baseline.md`.

## Kryteria akceptacji

- [ ] `docs/baseline.md` zawiera tabelę z czasem **każdego kroku**, nie tylko sumą
- [ ] zapisany całkowity czas przebiegu
- [ ] zapisany czas do pierwszego czerwonego sygnału (branch `demo/failing-unit`)
- [ ] zapisany wynik branchy `demo/failing-lint` i `demo/failing-security` wraz z wyjaśnieniem
- [ ] wypisane co najmniej pięć problemów

## Zmierz

| Co | Gdzie odczytać |
|---|---|
| Całkowity czas runu | nagłówek runu w zakładce Actions |
| Czas każdego kroku | job `test` → rozwinięty krok |
| Który krok zabiera najwięcej | porównanie czasów kroków |
| Czas do informacji o błędzie unit | run na `demo/failing-unit` |

<details>
<summary><b>Rozwiązanie — pomiary referencyjne</b></summary>

Wartości zmierzone na `ubuntu-latest` (run 33920530578). U Ciebie mogą się różnić
o kilkanaście procent — istotne są **proporcje**, nie liczby bezwzględne.

| Krok | Czas | Udział |
|---|---|---|
| Set up job + checkout + Node | 2 s | ~1% |
| `npm ci` | 6 s | 3% |
| **Instalacja przeglądarek** | **52 s** | **22%** |
| **Testy UI** | **2:27** | **62%** |
| Testy API | 19 s | 8% |
| **Testy jednostkowe** | **1 s** | 0,4% |
| Upload artefaktu | 1 s | |
| **Razem** | **3:58** | |

Czas do pierwszego czerwonego sygnału na `demo/failing-unit`: **3:44**.

Wyniki branchy, które miały nie przejść:

| Branch | Wynik | Dlaczego |
|---|---|---|
| `demo/failing-unit` | pada po 3:44 | testy jednostkowe są, tylko na końcu |
| `demo/failing-ui` | pada po 3:22 | testy UI są pierwsze, więc pada wcześniej |
| `demo/failing-lint` | **przechodzi** | **w pipelinie nie ma lintu** |
| `demo/failing-security` | **przechodzi** | **w pipelinie nie ma skanu bezpieczeństwa** |

### Pięć problemów

1. **Testy jednostkowe trwają sekundę i biegną jako ostatnie.** Czekasz 3:44, żeby dowiedzieć
   się czegoś, co można było wiedzieć po sekundzie. Kolejność kroków jest odwrotna do kosztu.
2. **Nie ma lintu ani typechecku.** Branch z błędem lintu świeci na zielono. Pipeline nie
   tyle jest wolny, co **mówi nieprawdę**.
3. **Nie ma skanu bezpieczeństwa.** Commit z tokenem płatniczym w kodzie przechodzi bez słowa.
4. **Instalacja przeglądarek zabiera 52 sekundy przy każdym przebiegu** i nic nie jest cache'owane.
5. **Wszystko siedzi w jednym jobie**, więc nic nie może biec równolegle, a jeden zepsuty
   krok zatrzymuje resztę.

Dodatkowo, do wychwycenia dla dociekliwych:

6. `on: push` bez ograniczenia — każdy push na każdy branch uruchamia pełny pipeline.
7. `upload-artifact` nie ma `if: always()`, więc **przy niepowodzeniu testów raportu nie ma**
   dokładnie wtedy, kiedy jest najbardziej potrzebny.
8. Build aplikacji nie jest osobnym krokiem — dzieje się w środku `webServer` Playwrighta,
   więc błąd kompilacji wygląda jak błąd testu.

</details>

## Pułapki

**Mierzenie tylko całości.** „Cztery minuty" nie mówi nic o tym, co poprawić. Dopiero rozbicie
na kroki pokazuje, że 62% czasu to jeden krok, a inny trwa sekundę i jest na końcu.

**Uwierzenie zielonemu kolorowi.** Dwa z czterech branchy demo przechodzą mimo realnych błędów.
Zielony pipeline znaczy tylko tyle, ile sprawdza.

**Poprawianie w trakcie mierzenia.** Kuszące jest poprawić `ci.yml` od razu. Nie rób tego —
bez liczby wyjściowej nie udowodnisz na koniec dnia, że cokolwiek pomogło.

## Do dyskusji

- Ile kosztuje zespół czekanie na pipeline? Nie chodzi o minuty CI, tylko o **utratę kontekstu**:
  ile trwa powrót do zadania, od którego się odeszło na cztery minuty?
- Który z pięciu problemów jest najgroźniejszy — najwolniejszy krok czy brakujący lint?
- Gdyby wolno było poprawić **tylko jedną rzecz**, co dałoby największy zysk?
