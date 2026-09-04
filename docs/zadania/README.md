# Zadania warsztatowe

Osiemnaście zadań, które przebudowują wyjściowy pipeline w coś, co daje szybki i czytelny
feedback. Każde zadanie ma tę samą strukturę:

**Cel** → **Dlaczego to boli** → **Zadanie** → **Kryteria akceptacji** → **Zmierz** →
rozwiązanie (zwinięte) → **Pułapki** → **Do dyskusji**.

## Jak pracować

Rozwiązanie każdego zadania jest dostępne w **dwóch postaciach** — użyj tej, która pasuje
do sytuacji:

| Sytuacja | Co zrobić |
|---|---|
| Utknąłeś na jednym kroku | rozwiń sekcję *Rozwiązanie* w pliku zadania |
| Odpadłeś całkiem albo dołączyłeś później | `git checkout solution/zadanie-05` — pełny, działający stan repo po tym zadaniu |

Branche `solution/*` są **kumulatywne**: `solution/zadanie-05` zawiera wszystko z zadań 01–05.
Dzięki temu można pominąć dowolne zadanie i wrócić do gry przy następnym.

## Kolejność

| Blok | Zadania |
|---|---|
| **Diagnoza** — gdzie ucieka feedback | 01 |
| **Krok po kroku** — budujemy pipeline | 02, 03, 04, 05 |
| **Testuje** — co, kiedy i jak szybko uruchamiać | 06, 07, 08, 09, 10, 11 |
| **Bez utraty jakości** — flaki | 12 |
| **Raportuje** — od loga do publicznego URL-a | 13, 14, 15, 16 |
| **Domknięcie** — porządek i bramka | 17, 18 |

## Lista

| # | Zadanie | Czego dotyczy |
|---|---|---|
| [01](ZADANIE-01.md) | Baseline i pomiar | czytanie czasów w GHA, metryka dnia |
| [02](ZADANIE-02.md) | Triggery i `concurrency` | eventy, anulowanie nieaktualnych runów |
| [03](ZADANIE-03.md) | Szybkie kontrole i cache | lint, typecheck, build, kolejność, cache |
| [04](ZADANIE-04.md) | Rozbicie na joby | `needs`, graf zależności, równoległość |
| [05](ZADANIE-05.md) | Artefakt builda | budujemy raz, nie cztery razy |
| [06](ZADANIE-06.md) | Skan bezpieczeństwa | `npm audit`, gitleaks, blokować czy ostrzegać |
| [07](ZADANIE-07.md) | Kontrakt API | wykrywanie zmian łamiących kontrakt |
| [08](ZADANIE-08.md) | Trzy tryby uruchomienia | smoke na PR, regresja na `main`, cron |
| [09](ZADANIE-09.md) | Selektywność | `paths-filter` i `--only-changed` |
| [10](ZADANIE-10.md) | Równoległość | workers, potem shardowanie |
| [11](ZADANIE-11.md) | Matrix | cross-browser selektywnie, `fromJSON` |
| [12](ZADANIE-12.md) | Flaki | retry, kwarantanna, dryf środowiska |
| [13](ZADANIE-13.md) | Scalanie raportów | `blob` + `merge-reports` |
| [14](ZADANIE-14.md) | Raportowanie w GitHubie | JUnit, check run, Job Summary |
| [15](ZADANIE-15.md) | Trace | „padło w CI, co teraz?" |
| [16](ZADANIE-16.md) | Storage i sekrety | publikacja raportu poza GitHubem |
| [17](ZADANIE-17.md) | Composite action | DRY w workflow |
| [18](ZADANIE-18.md) | Bramka i domknięcie | required checks, `permissions`, porównanie |
