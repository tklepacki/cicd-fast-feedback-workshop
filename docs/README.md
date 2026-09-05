# Przygotowanie do warsztatu

**Szybki feedback w CI/CD: pipeline, który testuje i raportuje bez utraty jakości**

Warsztat jest praktyczny — przez większość dnia będziesz pracować przy klawiaturze na
własnym repozytorium. Żeby nie stracić pierwszej godziny na instalacje, **wykonaj poniższe
kroki przed warsztatem** i sprawdź, że wszystko działa.

Całość zajmuje około 30 minut.

> **Przyjdź z laptopem**, na którym masz uprawnienia do instalowania oprogramowania
> i dostęp do sieci bez blokad (firmowy VPN albo polityki bezpieczeństwa potrafią
> zablokować `npm` lub GitHuba).

---

## 1. Narzędzia do zainstalowania

| Narzędzie | Wersja | Skąd |
|---|---|---|
| Visual Studio Code | dowolna aktualna | https://code.visualstudio.com/download |
| Node.js | **22 LTS lub nowszy** | https://nodejs.org/ |
| Git | dowolna aktualna | https://git-scm.com/downloads |

Sprawdź w terminalu, czy wszystko odpowiada:

```bash
node --version     # v22.x lub nowsza
npm --version
git --version
```

> **Nie potrzebujesz Javy ani Dockera.** Jeśli brałeś udział w poprzedniej edycji tego
> warsztatu — tym razem pracujemy wyłącznie na GitHub Actions.

---

## 2. Konto GitHub

Potrzebujesz **prywatnego konta GitHub**. Darmowe w zupełności wystarczy.

Jeśli masz konto firmowe objęte logowaniem SSO, **użyj konta prywatnego** — firmowe
polityki potrafią blokować tworzenie repozytoriów publicznych i uruchamianie workflow.

---

## 3. Utwórz własną kopię repozytorium

Otwórz repozytorium warsztatowe:

**https://github.com/tklepacki/cicd-fast-feedback-workshop**

Kliknij zielony przycisk **Use this template** → **Create a new repository**.

W formularzu:

| Pole | Ustawienie |
|---|---|
| Repository name | dowolna, np. `warsztat-cicd` |
| Widoczność | **Public** |
| **Include all branches** | **zaznacz** |

### Dwie rzeczy, które łatwo przeoczyć

**Zaznacz „Include all branches".** Bez tego nie dostaniesz branchy `solution/*`
z rozwiązaniami ani branchy `demo/*` z celowo zepsutym kodem — a używamy ich już
w pierwszym zadaniu. To najczęściej pomijany krok w całej instrukcji.

**Repozytorium musi być publiczne.** Nie chodzi o dzielenie się kodem, tylko o to,
że na darmowym koncie repozytorium publiczne dostaje nielimitowane minuty GitHub Actions
i mocniejszy runner (4 rdzenie zamiast 2). Na repozytorium prywatnym część zadań
jest technicznie niewykonalna.

---

## 4. Sklonuj repozytorium i zainstaluj zależności

```bash
git clone <adres-Twojego-nowego-repozytorium>
cd <nazwa-katalogu>
npm ci
npx playwright install --with-deps chromium
```

> Instalacja przeglądarki jest tym razem **potrzebna** — w warsztacie są testy UI,
> nie tylko API. Pobranie Chromium zajmuje chwilę, więc zrób to przed warsztatem.

---

## 5. Sprawdź, że wszystko działa

```bash
npm run verify
```

To polecenie uruchamia lint, typecheck, build i testy jednostkowe. Powinno zakończyć się
bez błędów i wypisać `78 passed`.

Sprawdź też testy przeglądarkowe i samą aplikację:

```bash
npm run test:smoke     # 5 testów, powinny przejść
npm run dev            # aplikacja na http://localhost:5173
```

Aplikacja to prosty sklep: katalog, koszyk, zamówienie. Dokumentacja API jest pod
adresem http://localhost:3000/api/docs po uruchomieniu `npm start`.

---

## 6. Włącz GitHub Actions w swoim repozytorium

Wejdź w swoje repozytorium na GitHubie → zakładka **Actions**.

Jeśli zobaczysz komunikat o wyłączonych workflow, kliknij przycisk włączający je.
Bez tego pierwsze zadanie nie ruszy.

Następnie sprawdź, że pipeline działa:

1. wejdź w **Actions** → wybierz workflow **CI**,
2. jeśli nie ma żadnego przebiegu, zrób dowolny commit i wypchnij go na `main`,
3. poczekaj, aż przebieg się zakończy — powinien być zielony i trwać około czterech minut.

**Te cztery minuty to nie błąd.** To jest punkt wyjścia, który będziemy skracać przez cały dzień.

---

## Lista kontrolna

Przed warsztatem odhacz wszystkie punkty:

- [ ] `node --version` pokazuje 22 lub nowszą
- [ ] `git --version` działa
- [ ] Visual Studio Code zainstalowany
- [ ] mam prywatne konto GitHub
- [ ] utworzyłem repozytorium z szablonu, **publiczne**, z **Include all branches**
- [ ] widzę u siebie branche `solution/zadanie-01` i `demo/failing-lint`
- [ ] `npm ci` przeszło bez błędów
- [ ] `npx playwright install --with-deps chromium` przeszło bez błędów
- [ ] `npm run verify` kończy się sukcesem (78 testów)
- [ ] `npm run test:smoke` kończy się sukcesem (5 testów)
- [ ] Actions są włączone i pierwszy przebieg zakończył się na zielono

---

## Gdyby coś nie zadziałało

**`npm ci` zgłasza błąd wersji Node** — sprawdź `node --version`. Projekt wymaga 22 lub nowszej.

**`npx playwright install` przerywa się na pobieraniu** — najczęściej blokada sieci firmowej.
Spróbuj z innej sieci albo z wyłączonym VPN-em.

**Nie widzę branchy `solution/*` ani `demo/*`** — kopia powstała bez zaznaczonego
„Include all branches". Najprościej usunąć repozytorium i utworzyć je jeszcze raz.

**Zakładka Actions jest pusta albo workflow się nie uruchamia** — sprawdź, czy Actions
są włączone (punkt 6) i czy repozytorium jest publiczne.

Jeśli utkniesz — napisz do mnie przed warsztatem, żebyśmy nie tracili na to czasu na sali.
