# ZADANIE 14 — Bramka, uprawnienia i domknięcie

## Cel

Domknąć cały dzień: dodać jedną bramkę chroniącą `main`, ograniczyć uprawnienia workflow,
ustawić limity czasu i porównać końcowy pipeline ze stanem wyjściowym.

## Na czym polega problem

Pipeline jest już szybki, selektywny i czytelny, ale **nadal nie chroni `main`**. Dopóki
repozytorium nie wymaga żadnej kontroli przed scaleniem, pull request z czerwonymi testami da się
scalić jednym kliknięciem. Zmiana w rabacie z ZADANIA 01 mogłaby trafić na `main` mimo błędu
wykrytego przez test jednostkowy.

Naturalny pomysł to oznaczyć wszystkie joby jako wymagane kontrole. Przy naszym pipelinie szybko
robi się to problematyczne, z trzech powodów.

**Pominięty shard pojawia się pod inną nazwą.** Gdy filtr z ZADANIA 08 pominie testy UI, pominięty
job pojawia się na liście kontroli pod surową nazwą z `${{ … }}`, a nie jako `UI tests 1/2 (smoke)`.
Wymagana kontrola o tej nazwie się nie pojawi, a GitHub będzie na nią czekać **w nieskończoność**
— każdy pull request, który nie dotyka interfejsu, utknie. Do tego nazwy shardów zmieniają się
razem z liczbą shardów (`1/2` na PR, `1/8` na `main`), więc lista wymaganych kontroli przestaje
pasować przy każdej zmianie matrixa.

**Pominięty job liczy się jako zaliczony.** Przy wymaganych kontrolach GitHub traktuje status
*Skipped* tak samo jak *Success*. Jeśli wymagasz tylko części jobów, a wcześniej zawiedzie lint,
pominięte testy UI „przejdą” — i czerwona zmiana trafi na `main`.

**Job zbiorczy bez `always()` też zostałby pominięty.** Gdyby końcowy job zależał od pozostałych
i nie miał `if: always()`, po błędzie którejś zależności zostałby pominięty — a więc uznany
za zaliczony. Dokładnie odwrotnie, niż potrzebujemy.

Dlatego zamiast wymagać wszystkich jobów osobno, dodamy jedną końcową bramkę o stałej nazwie:
`Pipeline status`. Do tego uporządkujemy jeszcze dwie rzeczy: każdy job dostaje dziś szersze
uprawnienia, niż potrzebuje, i żaden nie ma limitu czasu — zawieszony job potrafi zajmować
runner przez sześć godzin.

## Zadanie

Zmieniasz plik `.github/workflows/ci.yml` oraz ustawienia repozytorium na GitHubie.

> Kroki 1 i 2 pokaże prowadzący na swoim ekranie. Na warsztacie zacznij od kroku 3,
> a do kroków 1 i 2 wróć po warsztacie — nie wpływają na pomiary.

**1. Zawęź uprawnienia (pokaz prowadzącego).** Nad linią `jobs:`, na najwyższym poziomie pliku, dopisz:

```yaml
permissions:
  contents: read
```

Od teraz joby domyślnie mają tylko prawo do odczytu repozytorium. Job `test-report` z ZADANIA 12
ma własną sekcję `permissions` z `checks: write`, bo jako jedyny potrzebuje dodatkowego uprawnienia
do utworzenia check runa. Wyjątek jest widoczny w pliku, dokładnie przy jobie, który go potrzebuje.

**2. Dodaj limity czasu (pokaz prowadzącego).** W **każdym** jobie, pod linią `runs-on: ubuntu-latest`, dopisz:

```yaml
    timeout-minutes: 15
```

Domyślne sześć godzin to nie limit, tylko jego brak. Piętnaście minut daje duży zapas względem
najdłuższego joba, a zawieszony proces nie zajmie runnera na pół dnia.

**3. Dodaj końcową bramkę.** Na końcu sekcji `jobs:` dopisz:

```yaml
  pipeline-status:
    name: Pipeline status
    runs-on: ubuntu-latest
    timeout-minutes: 5
    needs: [changes, quality, unit, security, build, test-api, test-ui, ui-report, test-report]
    if: always()
    steps:
      - name: Check results
        run: |
          results='${{ join(needs.*.result, ' ') }}'
          echo "Job results: $results"
          for result in $results; do
            case "$result" in
              success|skipped) ;;
              *) echo "::error::A job finished with result: $result"; exit 1 ;;
            esac
          done
          echo "All checks passed."
```

| Element | Po co |
|---|---|
| `needs:` ze wszystkimi jobami | bramka czeka na wszystkie części pipeline'u, które mają wpływ na scalenie. Jeśli później dodasz nowy job, który powinien blokować scalenie, dopisz go też tutaj |
| `if: always()` | bramka uruchamia się niezależnie od wyniku wcześniejszych jobów. Bez tego po błędzie którejś zależności zostałaby pominięta, a pominiętą wymaganą kontrolę GitHub liczy jako zaliczoną — czerwona zmiana dałaby się scalić |
| `success\|skipped` | pominięty job jest u nas poprawnym wynikiem, bo pomija go świadomie selektywność; `failure` i `cancelled` kończą bramkę błędem |
| stała nazwa `Pipeline status` | ochrona gałęzi wymaga jednej kontroli, której nazwa nie zależy od liczby shardów ani budowy pipeline'u |

**4. Zatwierdź, wypchnij na `main` i zmierz finał.**

```bash
git add .github/workflows/ci.yml
git commit -m "Add a status gate"
git push
```

Na grafie powinien pojawić się job `Pipeline status`, zielony. Zapisz czas całego przebiegu —
to jest **czas finałowy na `main`**. To również ostatni push bezpośrednio na `main` podczas
warsztatu: po kroku 5 ochrona gałęzi będzie takie próby odrzucać.

Jeśli czas wyraźnie odbiega od poprzednich przebiegów, sprawdź na grafie, czy joby raportujące
(`UI report`, `Test report`) nie czekały na start po zakończeniu shardów. To kolejka GitHuba,
nie Twój pipeline — w takim przypadku porównuj raczej czas do zakończenia ostatniego sharda.

**5. Włącz ochronę `main`.** Na stronie repozytorium wejdź w **Settings → Rules → Rulesets →
New ruleset → New branch ruleset** i ustaw:

- **Ruleset name:** `main`
- **Enforcement status:** `Active`
- **Target branches:** **Add target → Include default branch**
- zaznacz **Require a pull request before merging**
- zaznacz **Require status checks to pass**, kliknij **Add checks** i dodaj **tylko jedną**
  kontrolę: `Pipeline status`

Kliknij **Create**. GitHub nazywa kontrolę tak jak `name:` joba, a nie jak jego klucz w YAML-u,
więc wpisz dokładnie `Pipeline status`. Inaczej wymagana kontrola nigdy się nie pojawi i każdy
pull request zostanie zablokowany.

**6. Sprawdź, że bramka przepuszcza bezpieczną zmianę.**

```bash
git checkout -b gate-readme
```

Dopisz linię do pliku — polecenie zależy od systemu.

macOS, Linux albo Git Bash na Windowsie:

```bash
echo "Ostatnia poprawka dnia." >> README.md
```

Windows, PowerShell:

```powershell
Add-Content README.md "Ostatnia poprawka dnia."
```

```bash
git commit -am "Update README"
git push -u origin gate-readme
git checkout main
```

Otwórz pull request i sprawdź, że:

- `UI tests` i `API tests` są pominięte,
- `Pipeline status` jest **zielony**,
- przycisk *Merge pull request* jest aktywny.

Scal ten pull request.

**7. Sprawdź, że bramka zatrzymuje błąd.**

```bash
git pull
git checkout -b gate-discount
git checkout warsztat/demo/failing-unit -- src/shared/discounts.ts
git commit -m "Discount change"
git push -u origin gate-discount
git checkout main
```

Otwórz pull request i sprawdź, że:

- `Unit tests` kończą się błędem,
- `Pipeline status` też jest czerwony,
- scalenie jest zablokowane, bo wymagana kontrola `Pipeline status` nie przeszła.

Zapisz, po ilu sekundach od startu przebiegu test jednostkowy wykrył błąd. **Pull requesta nie scalaj.**

**8. Sprawdź, że `main` jest chroniony.**

```bash
git commit --allow-empty -m "Try a direct push"
git push
```

Push powinien zostać odrzucony z informacją o regule ochrony gałęzi. Cofnij lokalny commit:

```bash
git reset --hard origin/main
```

**9. Porównaj cały dzień.** Uzupełnij tabelę w sekcji *Zmierz* **własnymi** wynikami —
z `docs/baseline.md` i z przebiegów z tego zadania. Nie chodzi już o pojedynczą optymalizację:
porównujesz pipeline z początku dnia z tym, który masz teraz.

Jeśli zatwierdzasz `docs/baseline.md`, pamiętaj, że po kroku 5 `main` jest chroniony — zmianę
wyślij przez pull request, tak jak w krokach 6 i 7.

## Kryteria akceptacji

- [ ] po warsztacie: workflow ma domyślnie `contents: read`, a `checks: write` jest tylko tam, gdzie jest potrzebne (krok 1)
- [ ] po warsztacie: każdy job ma ustawiony `timeout-minutes` (krok 2)
- [ ] `Pipeline status` jest jedyną wymaganą kontrolą przed scaleniem (krok 5)
- [ ] pull request z pominiętymi testami UI i API **da się** scalić (krok 6)
- [ ] pull request z testem, który nie przechodzi, **nie da się** scalić (krok 7)
- [ ] bezpośredni push na `main` jest odrzucany (krok 8)
- [ ] tabela porównawcza zawiera własne wyniki z początku i końca dnia (krok 9)

## Zmierz — porównanie dnia

| | Na początku dnia | Na koniec dnia |
|---|---|---|
| Cały przebieg na `main` | ? | ? |
| Cały przebieg na pull requeście | ? | ? |
| Czas do informacji o zmianie w koszyku (lint) | **nigdy** | ? |
| Czas do informacji o zmianie w rabacie (unit) | ? | ? |
| Czy wykrywa token w kodzie | **nie** | ? |
| Czy jest raport, gdy testy nie przejdą | **nie** | ? |
| Liczba kontroli na pull requeście | 1 | ? |
| Czy da się scalić zmianę z czerwonym testem | **tak** | ? |
