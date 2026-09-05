# -*- coding: utf-8 -*-
"""Łańcuch teoria → zadanie, część 2 (ZADANIA 10–18) i domknięcie."""

CHAIN2 = [
 ("theory", "Dwie osie równoległości", [
    ("Oś pionowa — workers: więcej procesów na jednej maszynie", True),
    ("Oś pozioma — shardowanie: więcej maszyn", True),
    ("Limit pionowej: 4 rdzenie runnera. Poziomej: 20 jobów na konto", True),
    ("Pionowa nie kosztuje nic. Pozioma mnoży zużycie minut", True),
    ("Domyślny workers: 1 na CI jest kopiowany do tysięcy projektów", True),
 ],
  "To jest blok, w którym najczęściej dochodzi do nieporozumienia, bo dwie różne rzeczy nazywa się "
  "tak samo — równoległością. Oś pionowa to więcej procesów na jednej maszynie; ogranicza ją liczba "
  "rdzeni, a repozytorium publiczne daje cztery. Oś pozioma to więcej maszyn; ogranicza ją limit "
  "dwudziestu jobów na konto. "
  "Kluczowa różnica jest kosztowa: oś pionowa jest za darmo, bo płacicie za maszynę tak czy inaczej. "
  "Oś pozioma mnoży zużycie minut. "
  "I teraz rzecz, którą chcę, żebyście sprawdzili sami: w konfiguracji generowanej przez Playwrighta "
  "jest linijka ustawiająca jednego workera na CI. Jest kopiowana do tysięcy projektów i prawie nigdy "
  "nierewidowana. Nie mówię, co z tego wyjdzie — zmierzcie."),

 ("task", "ZADANIE 10 — Workers, potem shardowanie", [
    ("Zmierz trzy razy: workers 1, workers 4, potem 4 shardy", True),
    ("Rób to w tej kolejności — chodzi o porównanie", True),
    ("fail-fast: false, inaczej jeden shard ubija resztę", True),
    ("Pułapka: upload-artifact wymaga unikalnych nazw w przebiegu", True),
    ("Zapisz, która oś dała więcej i ile kosztowała", True),
 ],
  "Trzydzieści minut i to jest zadanie, w którym najwięcej czasu zajmuje czekanie na pomiary. "
  "Kolejność jest istotna: najpierw sama zmiana liczby workerów, dopiero potem shardy. "
  "Chcę, żebyście zobaczyli te dwie liczby osobno. "
  "Nie zdradzam wyniku — powiem tylko, że jedna z tych zmian jest darmowa, a druga nie, "
  "i że to nie jest ta, której się spodziewacie. "
  "Pułapka techniczna: przy czterech shardach nazwy artefaktów muszą być unikalne, "
  "inaczej job padnie na uploadzie, a nie na teście, i przez chwilę nie będziecie wiedzieć dlaczego."),

 ("theory", "Matrix jako mechanizm ogólny", [
    ("Matrix to nie synonim shardowania — to generator jobów", True),
    ("fromJSON pozwala policzyć matrixa wyrażeniem", True),
    ("Matrix mnoży: dwa wymiary po cztery wartości to szesnaście maszyn", True),
    ("Pięć testów na czterech maszynach: więcej startu niż testowania", True),
 ],
  "Shardowanie jest najczęstszym zastosowaniem matrixa, ale matrix to po prostu generator jobów. "
  "Może rozpinać się po wersjach środowiska, po konfiguracjach, po czymkolwiek. "
  "Rzecz, o której warto pamiętać: matrix mnoży, a nie dodaje. Dwa wymiary po cztery wartości "
  "to szesnaście maszyn, nie osiem. Przy limicie dwudziestu jobów na konto łatwo o tę granicę zawadzić. "
  "I konkretny problem, który zaraz rozwiążecie: na pull requeście uruchamiacie pięć testów smoke "
  "rozdzielonych na cztery maszyny. Każda z nich spędza więcej czasu na starcie niż na testowaniu."),

 ("task", "ZADANIE 11 — Matrix, który liczy sam siebie", [
    ("Dwa shardy dla pull_request, osiem dla main", True),
    ("fromJSON — matrixa nie da się policzyć, ale można mu podać tablicę", True),
    ("Mianownik w --shard musi zmieniać się razem z matrixem", True),
    ("Policz, ile jobów zostaje do limitu 20", True),
 ],
  "Dwadzieścia minut. Najważniejsza pułapka i chcę ją podkreślić, bo jest podstępna: "
  "jeśli zmienicie listę shardów, a zapomnicie zmienić mianownik w --shard, "
  "dostaniecie najgorszy możliwy wynik — pipeline świeci na zielono, "
  "a część testów w ogóle się nie uruchomiła. Nic nie pada, więc nikt tego nie zauważa. "
  "To jest ten rodzaj błędu, który potrafi żyć w projekcie miesiącami."),

 ("theory", "Flaki — czego nie naprawi żaden retry", [
    ("Flak to test, który przy tym samym kodzie raz przechodzi, raz nie", True),
    ("Przyczyny: czas, wyścig, współdzielony stan, kolejność, ŚRODOWISKO", True),
    ("Retry nie naprawia — wydłuża najgorszy przypadek i ukrywa problem", True),
    ("Playwright raportuje „flaky” osobno od „passed” — to sygnał, nie sukces", True),
    ("ubuntu-latest to etykieta, którą GitHub przesuwa pod spodem", True),
 ],
  "To jest blok, który realizuje drugą połowę tytułu warsztatu — „bez utraty jakości”. "
  "Flak to test, który przy niezmienionym kodzie raz przechodzi, a raz nie. "
  "Przyczyn jest kilka i większość znacie: czas, wyścig, współdzielony stan, zależność od kolejności. "
  "Ale jest jeszcze jedna, o której mówi się najrzadziej, a która jest najbardziej frustrująca: "
  "dryf środowiska. ubuntu-latest to etykieta, którą GitHub przesuwa. "
  "Gdy runner przechodzi na nowszy system i zmienia się renderowanie czcionek, pipeline czerwieni się "
  "bez żadnego commita do obwinienia. I żaden retry tego nie naprawi, bo problem nie jest w teście. "
  "Powiem też jasno o retry: on niczego nie naprawia. Kupuje czas na diagnozę, "
  "ale wydłuża najgorszy przypadek i ukrywa problem."),

 ("task", "ZADANIE 12 — Retry, kwarantanna i zamrożone środowisko", [
    ("retries na CI — i uczciwa rozmowa o koszcie", True),
    ("Kwarantanna: tag @flaky w osobnym, nieblokującym jobie", True),
    ("Przypięty obraz Playwrighta zamraża przeglądarkę, system i czcionki", True),
    ("Pusta kwarantanna to stan zdrowy — job nie może przez to padać", True),
    ("Do dyskusji: kiedy kwarantanna staje się śmietnikiem?", True),
 ],
  "Trzydzieści minut. Kwarantanna to wzorzec, nie obejście — alternatywą jest albo trwale czerwony "
  "pipeline, którego wszyscy uczą się ignorować, albo skasowany test, czyli cicha utrata pokrycia. "
  "Ale ma jeden warunek: limit czasu przebywania w kwarantannie, inaczej robi się śmietnik. "
  "Przy kontenerze zwróćcie uwagę na uzasadnienie. Nie chodzi o szybkość — chodzi o to, "
  "że przypięty tag zamraża komplet: przeglądarkę, system, czcionki i biblioteki. "
  "Te same bajty dziś i za pół roku. To jest wolniejsze od rozgrzanego cache i o to właśnie chodzi: "
  "oddajecie kilkanaście sekund za determinizm."),

 ("theory", "Dlaczego shardowanie psuje raportowanie", [
    ("Cztery shardy to cztery osobne raporty HTML", True),
    ("Nie da się ich sensownie połączyć — to gotowe strony", True),
    ("blob to format pośredni, zaprojektowany do scalania", True),
    ("Zmiana, o której się zapomina razem z shardowaniem", True),
 ],
  "Krótki blok, ale dotyczy błędu, który widuję najczęściej w prawdziwych projektach. "
  "Rozbiliście testy na cztery maszyny — i macie cztery osobne raporty HTML. "
  "Nie da się ich sensownie połączyć, bo to są gotowe strony, a nie dane. "
  "Playwright ma na to format pośredni o nazwie blob, zaprojektowany właśnie do scalania. "
  "Zapamiętajcie: shardowanie i raportowanie zmienia się razem. Jedno bez drugiego zostawia Was "
  "z czterema raportami, z których nikt nie korzysta."),

 ("task", "ZADANIE 13 — Scalanie raportów", [
    ("Reporter blob zamiast html na CI", True),
    ("Osobny job ui-report z needs i if: always()", True),
    ("merge-multiple: true przy pobieraniu artefaktów", True),
    ("Raport z zielonego przebiegu to ten, którego nikt nie czyta", True),
 ],
  "Piętnaście minut. Zwróćcie uwagę na if: always() — bez tego job scalający nie uruchomi się "
  "po awarii shardów, czyli raport zniknie dokładnie wtedy, gdy jest potrzebny. "
  "To zdanie warto sobie powtórzyć: raport z zielonego przebiegu to ten, którego nikt nie czyta. "
  "Druga rzecz to merge-multiple. Bez tego każdy artefakt wyląduje w osobnym podkatalogu "
  "i narzędzie zobaczy cztery odrębne raporty zamiast czterech części jednego."),

 ("theory", "Komu służy raport", [
    ("Programista w review chce annotacji przy linii kodu", True),
    ("Tester chce listy testów z podziałem na przyczyny", True),
    ("Manager chce jednej liczby: przeszło czy nie", True),
    ("JUnit jako wspólny format dla unit, API i UI", True),
    ("Każdy typ testów raportujący inaczej = nikt nie patrzy na wyniki", True),
 ],
  "Zanim dodamy raportowanie, jedno pytanie: komu ten raport ma służyć? "
  "Bo to nie jest jeden odbiorca. Programista w trakcie review chce zobaczyć annotację przy linii kodu. "
  "Tester chce listy testów z podziałem na przyczyny. Ktoś zaglądający z boku chce jednej liczby. "
  "To są trzy różne poziomy widoczności i dlatego za chwilę dodamy trzy mechanizmy naraz. "
  "Jest jeszcze rzecz techniczna, ale ważniejsza, niż się wydaje: wspólny format. "
  "Jeśli testy jednostkowe raportują inaczej niż API, a API inaczej niż UI, to nikt nie patrzy na wyniki, "
  "bo nie ma jednego miejsca, w którym można je zobaczyć razem."),

 ("task", "ZADANIE 14 — Jeden format dla wszystkich testów", [
    ("JUnit z Vitest, z testów API i z testów UI", True),
    ("dorny/test-reporter tworzy check run z listą testów", True),
    ("Wymaga checks: write — pierwszy raz permissions ma konsekwencję", True),
    ("Job Summary: tabela wyników bez wchodzenia w logi", True),
    ("if: always() na każdym uploadzie artefaktu", True),
 ],
  "Dwadzieścia pięć minut. To jest moment, w którym permissions przestaje być higieną, "
  "a zaczyna mieć konsekwencję — bez checks: write akcja nie utworzy check runu. "
  "Warto też wiedzieć o ograniczeniu: to nie zadziała dla pull requestów z forków, "
  "bo ich token jest tylko do odczytu. U nas działa, bo pracujecie we własnych repozytoriach. "
  "I proszę, zwróćcie uwagę na if: always() przy uploadach. Bez tego artefakt z wynikami "
  "nie powstaje wtedy, gdy testy padły. Czyli zawsze wtedy, kiedy go potrzebujecie."),

 ("theory", "Diagnozowalność — padło w CI, co teraz", [
    ("Cały dzień uczymy się szybko dostawać czerwony sygnał", True),
    ("Ale co z nim zrobić? Log mówi „expected 6, received 12”", True),
    ("Trace to nagranie: DOM przed i po akcji, sieć, konsola", True),
    ("Trace ze wszystkiego to setki megabajtów, których nikt nie otworzy", True),
 ],
  "I teraz rzecz, o której bardzo łatwo zapomnieć przy budowaniu pipeline'u. "
  "Cały dzień uczymy się, jak szybko dostać czerwony sygnał. Ale co z nim zrobić? "
  "Log mówi „oczekiwano sześć, otrzymano dwanaście” i tyle. Nie widzicie, co było na ekranie, "
  "jakie żądania poleciały ani co powiedziała konsola. "
  "Trace to pełne nagranie przebiegu testu. Ma jednak koszt: nagrywanie wszystkiego "
  "produkuje setki megabajtów, których nikt nigdy nie otworzy. Dlatego nagrywamy selektywnie."),

 ("task", "ZADANIE 15 — Trace jako narzędzie diagnozy", [
    ("Pobierz artefakt z traceʼem z padającego przebiegu", True),
    ("npx playwright show-trace — przejdź po osi czasu", True),
    ("Ustaw trace na on-first-retry zamiast on", True),
    ("Trace wgrywany tylko przy porażce, z dłuższą retencją", True),
 ],
  "Piętnaście minut i to jest zadanie, które warto zrobić razem na ekranie, "
  "bo trace ogląda się lepiej, niż o nim opowiada. "
  "Użyjcie brancha demo/failing-ui, żebyśmy wszyscy patrzyli na ten sam błąd. "
  "Przejdźcie po osi czasu i zobaczcie snapshot DOM przed i po akcji — to jest ta rzecz, "
  "która zamienia „test padł” w „wiem dlaczego”."),

 ("theory", "Sekrety w GitHub Actions", [
    ("Sekrety NIE są kopiowane przez fork ani przez szablon", True),
    ("Maskowane w logach, ale to nie jest zabezpieczenie", True),
    ("Token o najwęższym możliwym zakresie i z datą ważności", True),
    ("Artefakty wygasają — raport na storage'u ma URL do wklejenia", True),
 ],
  "Ostatni blok techniczny i jedyny moment, w którym dotykamy sekretów. "
  "Trzy rzeczy warte zapamiętania. Po pierwsze: sekrety nie są kopiowane ani przez forka, "
  "ani przez szablon — dlatego za chwilę każdy będzie musiał wkleić je sobie sam. "
  "Po drugie: maskowanie w logach to wygoda, nie zabezpieczenie. "
  "Po trzecie i najważniejsze: token ma mieć najwęższy możliwy zakres i datę ważności. "
  "A sam storage? Artefakty GitHuba wygasają, a raport na storage'u ma adres, "
  "który można wkleić do zgłoszenia błędu."),

 ("task", "ZADANIE 16 — Publikacja raportu i sekrety", [
    ("Wklej cztery sekrety R2 do ustawień swojego repozytorium", True),
    ("aws s3 sync z endpointem R2 — API zgodne z S3", True),
    ("Prefiks per uczestnik i numer przebiegu, żeby się nie nadpisywać", True),
    ("Publiczny URL raportu w Job Summary", True),
    ("Ten sam krok dla Azure Blob czy S3 to zmiana endpointu", True),
 ],
  "Dwadzieścia pięć minut, z czego pięć na wklejenie sekretów — rozdałem je w przerwie. "
  "Najważniejsza rzecz do wyniesienia z tego zadania nie dotyczy Cloudflare. "
  "Używamy zwykłego aws s3 sync, bo R2 ma API zgodne z S3. "
  "To znaczy, że przeniesienie tego do Waszego projektu na Azure Blob, S3 czy GCS "
  "to zmiana adresu i poświadczeń, a nie przepisywanie pipeline'u. "
  "Wychodzicie ze wzorcem, nie z przywiązaniem do dostawcy."),

 ("theory", "Dług w pipelinie", [
    ("Po szesnastu zadaniach ten sam setup jest w siedmiu jobach", True),
    ("Composite action dzieli kroki wewnątrz joba", True),
    ("Reusable workflow dzieli całe joby między workflow'ami", True),
    ("Optymalizacja zostawia po sobie śmieci — i nikt ich nie sprząta", True),
 ],
  "Przedostatni blok i temat, o którym rzadko się mówi: pipeline też ma dług techniczny. "
  "Po szesnastu zadaniach ten sam czterokrokowy wstęp powtarza się w siedmiu jobach. "
  "Ale jest jeszcze ciekawsza rzecz, którą zaraz znajdziecie. "
  "Kiedy w ZADANIU 12 dodaliśmy kontener z przeglądarkami, trzy kroki instalujące te przeglądarki "
  "stały się martwe. I przez kilka kolejnych zadań nikt ich nie usunął, łącznie ze mną. "
  "Optymalizacja zostawia po sobie śmieci — to jest normalne, pod warunkiem że ktoś je w końcu sprząta."),

 ("task", "ZADANIE 17 — Composite action", [
    ("Zwiń powtórzony setup do .github/actions/setup", True),
    ("Uwaga: akcja lokalna wymaga wcześniejszego checkout", True),
    ("Znajdź i usuń kroki, które kontener uczynił zbędnymi", True),
    ("Do dyskusji: kiedy composite, a kiedy reusable workflow?", True),
 ],
  "Dwadzieścia minut. Jedna rzecz, która potrafi zaskoczyć: akcja lokalna mieszka w repozytorium, "
  "więc repozytorium musi być już sklonowane, zanim da się ją znaleźć. "
  "Nie zwiniecie więc pierwszego kroku, tylko trzy kolejne. "
  "Jeśli komuś zabraknie czasu, to jest zadanie, które najbezpieczniej pominąć — "
  "nic od niego nie zależy, a pipeline działa bez niego tak samo."),

 ("theory", "Pipeline, któremu zespół ufa", [
    ("Wymagane kontrole: nazwy z matrixa zmieniają się razem z nim", True),
    ("Jeden agregujący job o stałej nazwie zamiast dwunastu", True),
    ("Pominięty job musi liczyć się jako sukces — inaczej blokada", True),
    ("Least privilege: read-only domyślnie, wyjątek widoczny w review", True),
    ("Czerwony pipeline, który wszyscy ignorują, jest gorszy niż jego brak", True),
 ],
  "Ostatni blok teorii. Chcę zamknąć dzień czymś, co nie jest techniczne. "
  "Pipeline ma wartość dokładnie wtedy, gdy zespół mu ufa. Czerwony pipeline, "
  "który wszyscy nauczyli się ignorować, jest gorszy niż jego brak — bo daje złudzenie kontroli. "
  "Technicznie: ochrona gałęzi wymaga nazw kontroli, a matrix generuje nazwy, które zmieniają się "
  "razem z nim. Dlatego robimy jeden agregujący job o stałej nazwie. "
  "I rzecz, o której mówiłem przy selektywności: pominięty job musi liczyć się jako sukces, "
  "inaczej zablokujecie każdy pull request, który nie dotyka interfejsu."),

 ("task", "ZADANIE 18 — Bramka i domknięcie", [
    ("Job pipeline-status agregujący needs.*.result", True),
    ("timeout-minutes w każdym jobie, permissions least privilege", True),
    ("Ruleset na main z jedną wymaganą kontrolą", True),
    ("Wypełnij tabelę baseline kontra finał WŁASNYMI liczbami", True),
 ],
  "Ostatnie zadanie, dwadzieścia minut. Najdroższy błąd, jaki można tu popełnić, "
  "to ustawienie pojedynczych jobów jako wymaganych kontroli zamiast agregatu — "
  "wtedy job, który bywa pomijany, blokuje pull requesty bez możliwości odblokowania. "
  "Punkt czwarty jest najważniejszy z całego dnia: wypełnijcie tabelę własnymi liczbami. "
  "Nie moimi. Za chwilę je porównamy."),

 ("theory", "Baseline kontra finał", [
    ("Czas na main: 3:58 → 1:50", True),
    ("Czas do błędu lintu: nigdy → około 35 sekund", True),
    ("Czas do błędu testu jednostkowego: 3:44 → około 40 sekund", True),
    ("Kontroli na pull requeście: 1 → 7", True),
    ("Szybciej, robiąc znacznie więcej — to nie jest usunięta praca", True),
 ],
  "I teraz najważniejszy slajd całego dnia. Popatrzcie na te liczby. "
  "Pipeline jest ponad dwa razy szybszy — ale to nie jest w nim najciekawsze. "
  "Najciekawsze jest to, że robi znacznie więcej niż na starcie: doszedł lint, typecheck, "
  "skan bezpieczeństwa, kontrola kontraktu API, scalanie raportów i publikacja. "
  "Czas nie spadł dlatego, że usunęliśmy pracę. Spadł dlatego, że ułożyliśmy ją równolegle "
  "i we właściwej kolejności. To jest cała teza dzisiejszego dnia i macie ją udowodnioną "
  "na własnych pomiarach."),

 ("theory", "Co zabrać do swojego projektu", [
    ("Zmierz swój baseline — czas do pierwszego czerwonego sygnału", True),
    ("Sprawdź, czego Twój pipeline NIE sprawdza", True),
    ("Najtańsza kontrola, która potrafi ubić przebieg, idzie pierwsza", True),
    ("Zajrzyj do konfiguracji: ile masz workerów na CI?", True),
    ("Trzy rzeczy, które zmienię w poniedziałek — wypiszcie je teraz", True),
 ],
  "Na koniec chcę, żebyście zrobili jedną rzecz, zanim zamkniecie laptopy. "
  "Wypiszcie sobie trzy konkretne rzeczy, które zmienicie w swoim pipelinie w poniedziałek. "
  "Nie ogólniki — konkrety ze swojego projektu. "
  "Podpowiem, od czego zacząć: zmierzcie swój baseline i sprawdźcie, czego Wasz pipeline nie sprawdza. "
  "A jeśli macie testy Playwrighta, zajrzyjcie do konfiguracji i sprawdźcie liczbę workerów na CI. "
  "Podejrzewam, że u części z Was to będzie jedynka. "
  "Repozytorium zostaje Wasze — wszystkie rozwiązania są na branchach solution. "
  "Dziękuję za dziś i zapraszam do pytań."),
]
