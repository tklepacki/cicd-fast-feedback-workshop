# ZADANIE 16 — Publikacja raportu na zewnętrzny storage i sekrety

## Cel

Raport, do którego prowadzi **link**, a nie instrukcja „pobierz artefakt i rozpakuj".
Przy okazji jedyne w całym warsztacie zetknięcie z `secrets` — a bez nich obraz
GitHub Actions jest niepełny.

## Dlaczego to boli

Artefakty mają dwie wady, które ujawniają się dopiero w praktyce.

**Wygasają.** Domyślnie po 90 dniach, a po ZADANIU 14 — po siedmiu. Zgłoszenie błędu
sprzed miesiąca ma w treści martwy odnośnik.

**Wymagają pobrania i rozpakowania.** Nie da się ich wkleić do zgłoszenia ani wysłać
osobie spoza zespołu. Programista, który ma naprawić błąd, musi najpierw wykonać
trzy czynności, zanim cokolwiek zobaczy.

Raport pod adresem HTTP nie ma żadnej z tych wad.

## Zadanie

**1. Odbierz poświadczenia** — prowadzący rozda cztery wartości. Wpisz je jako sekrety
repozytorium: *Settings → Secrets and variables → Actions → New repository secret*.

| Sekret | Co to |
|---|---|
| `R2_ACCOUNT_ID` | identyfikator konta Cloudflare |
| `R2_ACCESS_KEY_ID` | klucz dostępu |
| `R2_SECRET_ACCESS_KEY` | klucz tajny |
| `R2_BUCKET` | nazwa bucketu |

**2. Dodaj krok publikujący** scalony raport z ZADANIA 13 na storage.
Użyj zwykłego `aws s3 sync` — Cloudflare R2 wystawia **API zgodne z S3**.

**3. Zadbaj o przestrzeń nazw.** Bez tego piętnaście osób nadpisze sobie raporty nawzajem.
Użyj `${{ github.repository_owner }}/run-${{ github.run_number }}/`.

**4. Wypisz adres do Job Summary**, żeby raport był o jedno kliknięcie.

**5. Sprawdź, czy sekret nie wyciekł do logów.** Dodaj tymczasowo `echo` z wartością sekretu
i zobacz, co pojawi się w logu.

## Kryteria akceptacji

- [ ] cztery sekrety wpisane w ustawieniach repozytorium
- [ ] raport publikowany po każdym przebiegu na `main`
- [ ] adres widoczny w Job Summary
- [ ] raporty różnych osób nie nadpisują się
- [ ] wartość sekretu jest **maskowana** w logach
- [ ] w pliku workflow nie ma żadnej wartości poświadczeń

## Zmierz

| Co | Artefakt | Storage |
|---|---|---|
| Kroki do zobaczenia raportu | pobierz, rozpakuj, otwórz | ? |
| Czas życia | 7 dni | ? |
| Da się wysłać linkiem | nie | ? |

<details>
<summary><b>Rozwiązanie</b></summary>

```yaml
  publish-report:
    name: Publikacja raportu
    runs-on: ubuntu-latest
    needs: ui-report
    if: always() && github.event_name == 'push'
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: playwright-report
          path: playwright-report

      - name: Publish to object storage
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.R2_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.R2_SECRET_ACCESS_KEY }}
          AWS_DEFAULT_REGION: auto
          PREFIX: ${{ github.repository_owner }}/run-${{ github.run_number }}
        run: |
          aws s3 sync playwright-report "s3://${{ secrets.R2_BUCKET }}/$PREFIX" \
            --endpoint-url "https://${{ secrets.R2_ACCOUNT_ID }}.r2.cloudflarestorage.com"

      - name: Link in the summary
        run: |
          echo "## Raport z testów" >> "$GITHUB_STEP_SUMMARY"
          echo "" >> "$GITHUB_STEP_SUMMARY"
          echo "[Otwórz raport](https://pub-XXXX.r2.dev/${{ github.repository_owner }}/run-${{ github.run_number }}/index.html)" >> "$GITHUB_STEP_SUMMARY"
```

### Dlaczego `aws s3`, a nie narzędzie Cloudflare

To jest **sedno tego zadania**. R2 wystawia API zgodne z S3, więc działa zwykłe `aws s3 sync`
z podmienionym `--endpoint-url`.

Konsekwencja: przesiadka na **Azure Blob**, AWS S3 czy Google Cloud Storage w firmowym
projekcie to zmiana endpointu i poświadczeń — **nie przepisywanie pipeline'u**.
Wychodzisz ze wzorcem, nie z przywiązaniem do dostawcy.

Równoważny krok dla Azure:

```yaml
      - run: |
          az storage blob upload-batch \
            --destination "$CONTAINER" --source playwright-report \
            --destination-path "$PREFIX" --sas-token "${{ secrets.AZURE_SAS_TOKEN }}"
```

### Maskowanie

GitHub zastępuje wartość każdego sekretu ciągiem `***` w logach. Ochrona jest jednak
**tekstowa i płytka**: sekret zakodowany w base64 albo rozbity na części nie zostanie
rozpoznany. To zabezpieczenie przed przypadkowym wypisaniem, nie przed złą wolą.

</details>

## Pułapki

**Sekrety nie są kopiowane.** Ani przez *Use this template*, ani przez forka.
Każdy wpisuje je u siebie — i to jest właściwe zachowanie, choć bywa zaskoczeniem.

**Brak przestrzeni nazw.** Bez prefiksu wszyscy piszą pod ten sam klucz i widzą cudzy raport.

**Sekret w pliku workflow.** Plik workflow jest w repozytorium, a repozytorium jest publiczne.
Poświadczenia **wyłącznie** przez `secrets:`.

**Sekrety niedostępne dla PR-ów z forków.** Świadome ograniczenie GitHuba: inaczej każdy
mógłby przysłać PR wypisujący Wasze klucze.

**Publikacja przy każdym przebiegu** zapełni bucket. Warto ograniczyć do `main`
i ustawić regułę wygasania po stronie storage'u.

## Do dyskusji

- Wszyscy dostają **ten sam** token do jednego bucketu. Jakie to niesie ryzyko i jak byś
  je ograniczył w prawdziwym zespole? (podpowiedź: uprawnienia tylko do zapisu, osobne
  prefiksy, rotacja po warsztacie)
- Raport publiczny pod adresem HTTP to wygoda i wyciek informacji naraz. Co jest w raporcie
  Playwrighta, czego nie chciałbyś pokazać światu?
- Kiedy warto płacić za usługę typu Currents czy ReportPortal zamiast wrzucać HTML
  na storage?
