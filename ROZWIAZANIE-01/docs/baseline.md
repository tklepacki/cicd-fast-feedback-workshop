# Baseline — pomiar stanu wyjściowego

Rozwiązanie ZADANIA 01. Pomiary z `ubuntu-latest`, repozytorium publiczne (4 vCPU / 16 GB),
przebieg referencyjny `36785901463`. U Ciebie liczby mogą się różnić — liczą się proporcje.

## Czasy kroków — przebieg na `main`

| Krok | Czas |
|---|---|
| Set up job | 1 s |
| Checkout | 1 s |
| Set up Node | 0 s |
| Install dependencies | 6 s |
| Install Playwright browsers | 18 s |
| Unit tests | 0 s |
| API tests | 20 s |
| UI tests | 2:27 |
| Upload Playwright report | 2 s |
| Post Set up Node | 0 s |
| Post Checkout | 0 s |
| Complete job | 0 s |
| **Cały przebieg** | **3:21** |

## Czas do pierwszego czerwonego sygnału

| Branch | Czas samego testu | Od startu przebiegu do informacji o błędzie |
|---|---|---|
| `demo/failing-unit` | 0 s | **0:28** |
| `demo/failing-search` | — | **4:10** |

Co na `demo/failing-unit` stało się z testami API i UI: **pominięte**. Wszystko jest w jednym jobie, więc po
czerwonym kroku kolejne się nie wykonują — nie wiemy, czy ta zmiana psuje coś jeszcze.

## `demo/failing-lint` i `demo/failing-security`

| Branch | Wynik przebiegu | Dlaczego tak |
|---|---|---|
| `demo/failing-lint` | **zielony** | w pipelinie nie ma lintu |
| `demo/failing-security` | **zielony** | w pipelinie nie ma skanu sekretów ani bezpieczeństwa |

## Pięć problemów obecnego pipeline’u

1. **Testy jednostkowe trwają sekundę, a czekają na instalację przeglądarek.** Informację
   o błędzie w rabacie dostajemy po 28 s, choć test, który go wykrywa, trwa sekundę
   i przeglądarki nie potrzebuje.
2. **Nie ma lintu ani typechecku.** Branch z błędem lintu świeci na zielono — pipeline nie
   tyle jest wolny, co **mówi nieprawdę**.
3. **Nie ma skanu bezpieczeństwa.** Commit z tokenem płatniczym przechodzi bez słowa.
4. **Instalacja przeglądarek przy każdym przebiegu**, nic nie jest cache'owane.
   Do tego instalowane są trzy przeglądarki, a używana jedna.
5. **Wszystko w jednym jobie** — nic nie biegnie równolegle, a jeden krok blokuje resztę.
6. `on: push` bez ograniczenia — każdy push na każdą gałąź uruchamia pełny pipeline.
7. `upload-artifact` bez `if: always()` — **przy padających testach raportu nie ma**
   dokładnie wtedy, gdy jest najbardziej potrzebny.
8. **Build ukryty** w `webServer` Playwrighta — błąd kompilacji wygląda jak błąd testu.

## Pomiary z kolejnych zadań

Tu dopisujesz pomiary i odpowiedzi z kolejnych zadań, pod nagłówkiem z numerem zadania.
