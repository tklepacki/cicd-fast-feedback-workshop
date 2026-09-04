# Baseline — pomiar stanu wyjściowego

Pomiary z `ubuntu-latest`, repozytorium publiczne (4 vCPU / 16 GB).
Run referencyjny: `33920530578`.

## Czasy kroków

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

## Czas do pierwszego czerwonego sygnału

| Branch | Wynik | Czas |
|---|---|---|
| `demo/failing-unit` | pada | **3:44** |
| `demo/failing-ui` | pada | 3:22 |
| `demo/failing-lint` | **przechodzi** | — |
| `demo/failing-security` | **przechodzi** | — |

## Problemy

1. **Testy jednostkowe trwają sekundę i biegną jako ostatnie.** Czekamy 3:44 na informację,
   którą można było mieć po sekundzie. Kolejność kroków jest odwrotna do kosztu.
2. **Nie ma lintu ani typechecku.** Branch z błędem lintu świeci na zielono — pipeline nie
   tyle jest wolny, co **mówi nieprawdę**.
3. **Nie ma skanu bezpieczeństwa.** Commit z tokenem płatniczym przechodzi bez słowa.
4. **52 sekundy na instalację przeglądarek przy każdym przebiegu**, nic nie jest cache'owane.
   Do tego instalowane są trzy przeglądarki, a używana jedna.
5. **Wszystko w jednym jobie** — nic nie biegnie równolegle, a jeden krok blokuje resztę.
6. `on: push` bez ograniczenia — każdy push na każdą gałąź uruchamia pełny pipeline.
7. `upload-artifact` bez `if: always()` — **przy padających testach raportu nie ma**
   dokładnie wtedy, gdy jest najbardziej potrzebny.
8. **Build ukryty** w `webServer` Playwrighta — błąd kompilacji wygląda jak błąd testu.
