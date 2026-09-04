# ZADANIE 06 — Skan bezpieczeństwa

## Cel

Dodać do pipeline'u kontrolę, której w nim nie ma, a której brak przepuszcza commit
z zahardkodowanym tokenem płatniczym.

## Dlaczego to boli

W ZADANIU 01 branch `demo/failing-security` **przeszedł na zielono**. Zawiera on plik
`src/server/payments.ts` z takim fragmentem:

```ts
const PAYMENT_API_TOKEN = 'wshop_sk_live_8Kx2mQ7pLvN4rT9wZ3aB6cDe';
```

Pipeline nie miał nic do powiedzenia, bo nie sprawdza dwóch rzeczy: **poświadczeń w kodzie**
oraz **znanych podatności w zależnościach**.

To jest inna klasa problemu niż wolny pipeline. Wyciek tokenu do publicznego repozytorium
jest nieodwracalny w tym sensie, że token trzeba unieważnić — usunięcie commita nie wystarcza,
bo historia bywa już sklonowana i zaindeksowana.

## Zadanie

**1. Dodaj job `security`**, który biegnie **równolegle** z pozostałymi — nie ma powodu,
żeby czekał na build czy testy.

**2. Sprawdź zależności:** `npm audit --audit-level=high`.

**3. Sprawdź sekrety w kodzie:** [gitleaks](https://github.com/gitleaks/gitleaks).
W repozytorium jest już `.gitleaks.toml` z regułą wykrywającą nasz warsztatowy format tokenu.

**4. Zweryfikuj na obu branchach:**

```bash
git checkout demo/failing-security   # ma paść
git checkout main                    # ma przejść
```

**5. Zastanów się, czy ten job ma blokować merge.** Odpowiedź nie jest oczywista —
patrz *Do dyskusji*.

## Kryteria akceptacji

- [ ] job `security` istnieje i nie ma `needs`
- [ ] `demo/failing-security` **pada** (przed tym zadaniem przechodził)
- [ ] `main` przechodzi
- [ ] w logach widać, **który plik i która reguła** wykryły problem
- [ ] job kończy się szybciej niż testy UI

## Zmierz

| Co | Wartość |
|---|---|
| Czas joba `security` | ? |
| Czy wydłużył cały przebieg | ? |
| Czas do informacji o wycieku sekretu | przed: nigdy, po: ? |

<details>
<summary><b>Rozwiązanie</b></summary>

```yaml
  security:
    name: Bezpieczeństwo
    runs-on: ubuntu-latest
    # No `needs`: nothing here depends on a build, and a leaked credential is worth
    # knowing about within seconds rather than after the UI suite finishes.
    steps:
      - uses: actions/checkout@v4
        with:
          # gitleaks scans history, not just the working tree, so it needs all of it.
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
        run: gitleaks detect --source . --config .gitleaks.toml --redact --verbose
```

### Dlaczego binarka, a nie `gitleaks-action`

Oficjalna akcja wymaga **klucza licencyjnego dla organizacji** (dla kont osobistych jest
darmowa). Ponieważ uczestnicy pracują na kontach prywatnych, a w firmie repozytoria bywają
w organizacji, binarka jest jedynym wariantem, który zadziała u wszystkich bez wyjątku.

### Dlaczego `--redact`

Bez tego gitleaks wypisze znaleziony sekret **w logach przebiegu**, które w publicznym
repozytorium widzi każdy. Narzędzie do wykrywania wycieków samo by go wtedy opublikowało.

### Dlaczego `fetch-depth: 0`

Domyślny checkout pobiera jeden commit. Sekret usunięty w ostatnim commicie, ale obecny
w historii, byłby wtedy niewidoczny — a to najczęstszy realny przypadek.

</details>

## Pułapki

**`npm audit` potrafi być hałaśliwy.** Podatności w zależnościach deweloperskich nie zawsze
mają znaczenie dla produkcji, a `--audit-level=high` to kompromis, nie prawda objawiona.
Job, który świeci na czerwono co drugi dzień z powodów, na które nikt nie ma wpływu,
przestaje być czytany — i to jest gorsze niż brak joba.

**Skanowanie samego drzewa roboczego.** Bez `fetch-depth: 0` sprawdzasz tylko to, co widać
teraz. Sekret sprzed dziesięciu commitów nadal jest w historii i nadal jest ważny.

**Wykrycie to nie naprawa.** Gdy gitleaks znajdzie token, usunięcie go z kodu **nie wystarcza**.
Token trzeba unieważnić u dostawcy — historia mogła już zostać sklonowana.

## Do dyskusji

- **Blokować merge czy tylko ostrzegać?** Argument za blokowaniem: sekret w kodzie to defekt
  jak każdy inny. Argument przeciw: `npm audit` bywa czerwony z powodu podatności bez łatki,
  a zablokowany zespół zacznie obchodzić bramkę. Gdzie jest granica?
- Jeśli część kontroli ma tylko ostrzegać, jak sprawić, żeby ostrzeżenia nie stały się tłem,
  którego nikt nie czyta?
- Ten job biegnie równolegle i kończy się w kilkanaście sekund. Czy jest sens uruchamiać
  go przy **każdym** pushu, czy wystarczy na PR-ach i na `main`?
