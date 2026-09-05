# -*- coding: utf-8 -*-
"""Łańcuch teoria → zadanie, część 1 (ZADANIA 01–09)."""

CHAIN1 = [
 ("theory", "Jak czytać przebieg w GitHub Actions", [
    ("Suma czasu nic nie mówi — liczy się rozkład na kroki", True),
    ("Actions → run → job → rozwiń krok, przy każdym jest czas", True),
    ("Szukamy dwóch rzeczy: co trwa najdłużej i co jest za późno", True),
    ("Dobra metryka jest jedna, mierzalna i niewygodna", True),
 ],
  "Zanim cokolwiek zoptymalizujecie, musicie wiedzieć, ile to teraz trwa — i gdzie dokładnie ucieka czas. "
  "Zwróćcie uwagę, że sama suma nic nie mówi. „Cztery minuty” nie podpowiada, co poprawić. "
  "Dopiero rozkład na kroki pokazuje, że jeden krok to sześćdziesiąt procent czasu, a inny trwa sekundę "
  "i jest na samym końcu. Szukamy więc dwóch rzeczy naraz: co trwa najdłużej i co jest uruchamiane za późno. "
  "I jeszcze jedno o metryce: dobra metryka jest niewygodna. Jeśli wybierzecie taką, która zawsze wygląda "
  "dobrze, to nie jest metryka, tylko dekoracja."),

 ("task", "ZADANIE 01 — Baseline i pomiar", [
    ("Cel: zmierzyć stan wyjściowy. Nie zmieniamy ani linijki ci.yml", True),
    ("Uruchom pipeline, przepisz czasy kroków do docs/baseline.md", True),
    ("Zmierz czas do pierwszego czerwonego sygnału na demo/failing-unit", True),
    ("Sprawdź demo/failing-lint i demo/failing-security — wynik Cię zaskoczy", True),
    ("Wypisz pięć problemów, które widzisz", True),
 ],
  "To jest zadanie na jakieś dwadzieścia pięć minut, z czego większość to czekanie na przebiegi — "
  "wykorzystajcie ten czas na przeczytanie ci.yml linijka po linijce. "
  "Najważniejszy jest punkt czwarty: dwa branche, które mają nie przejść. Nie zdradzam, co się stanie — "
  "chcę, żebyście to zobaczyli sami i sami się zdziwili. "
  "Najczęstszy błąd: ludzie mierzą tylko całkowity czas i idą dalej. Bez rozbicia na kroki "
  "reszta dnia nie będzie miała punktu odniesienia. "
  "Jeśli ktoś utknie — git checkout solution/zadanie-01, tam jest wypełniony baseline."),

 ("theory", "Eventy i concurrency", [
    ("push, pull_request, schedule, workflow_dispatch — różne pytania", True),
    ("pull_request testuje commit scalenia, nie szczyt gałęzi", True),
    ("Trzy pushe pod rząd to trzy pełne przebiegi", True),
    ("Dwa pierwsze są nieaktualne, zanim ruszy trzeci", True),
 ],
  "Zmierzyliście, ile trwa jeden przebieg. Teraz pytanie: ile przebiegów w ogóle potrzebujecie? "
  "Domyślnie każdy push na każdą gałąź uruchamia wszystko. "
  "Wyobraźcie sobie, że poprawiacie literówkę i pushujecie trzy razy w ciągu minuty. "
  "Startują trzy pełne pipeline'y, z których dwa pierwsze opisują kod, którego już nie ma. "
  "A pamiętacie limit dwudziestu jobów na konto? Właśnie zaczęliście kolejkować sami sobie."),

 ("task", "ZADANIE 02 — Triggery i concurrency", [
    ("push tylko na main, dodaj pull_request i workflow_dispatch", True),
    ("Dodaj concurrency z cancel-in-progress", True),
    ("Udowodnij: trzy szybkie pushe = jeden działający run, dwa anulowane", True),
    ("Do przemyślenia: kiedy anulowanie jest złym pomysłem?", True),
 ],
  "Krótkie zadanie, jakieś piętnaście minut. Kluczowy jest punkt trzeci — nie wierzcie, że działa, "
  "tylko to zobaczcie w zakładce Actions. "
  "Najczęstszy błąd: ludzie zostawiają push bez ograniczenia do main i dodają pull_request. "
  "Efekt jest taki, że push na gałąź z otwartym PR-em uruchamia pipeline dwa razy — "
  "płacicie podwójnie za tę samą informację. "
  "Pytanie na koniec zostawcie sobie na dyskusję: gdzie anulowanie przebiegu byłoby groźne?"),

 ("theory", "Kolejność kontroli i shift left", [
    ("Wasz pomiar: testy jednostkowe trwają sekundę i są ostatnie", True),
    ("Czekacie 3:44 na informację dostępną po sekundzie", True),
    ("Shift left: najtańsza kontrola, która potrafi ubić przebieg, idzie pierwsza", True),
    ("Cache: co jest naprawdę drogie? Zmierzcie, nie zgadujcie", True),
    ("Lintu i typechecku w tym pipelinie nie ma wcale", True),
 ],
  "I teraz wracamy do tego, co zmierzyliście. Testy jednostkowe trwają sekundę i są uruchamiane ostatnie. "
  "To znaczy, że czekacie prawie cztery minuty na informację, którą można było mieć po sekundzie. "
  "Zasada jest prosta: najtańsza kontrola, która potrafi ubić przebieg, powinna iść pierwsza. "
  "Druga rzecz to cache — i tu uwaga, bo intuicja myli. Zanim coś zacache'ujecie, sprawdźcie, "
  "co naprawdę kosztuje. Nie mówię, co wyjdzie; zmierzycie to sami za chwilę. "
  "I trzecia rzecz, najpoważniejsza: w tym pipelinie w ogóle nie ma lintu ani typechecku. "
  "To już nie jest kwestia szybkości — pipeline po prostu nie sprawdza tych rzeczy."),

 ("task", "ZADANIE 03 — Szybkie kontrole i cache", [
    ("Dodaj lint, typecheck i jawny build — przed testami", True),
    ("Przestaw testy: jednostkowe → API → UI", True),
    ("Zacache'uj zależności npm ORAZ przeglądarki (dwa różne cache)", True),
    ("Klucz cache przeglądarek musi zawierać wersję Playwrighta", True),
    ("Zmierz na demo/failing-lint: z „nigdy” na ile sekund?", True),
 ],
  "Najważniejsze zadanie w całym dniu i najdłuższe — liczcie trzydzieści minut. "
  "Zwróćcie uwagę, że cache przeglądarek to osobny cache, w innej lokalizacji i z własnym kluczem. "
  "Najczęstszy błąd, i naprawdę kosztowny: klucz bez wersji Playwrighta. Działa idealnie, "
  "aż do pierwszego podbicia zależności — wtedy dostajecie z cache stare przeglądarki i testy padają "
  "w sposób, którego nie da się powiązać ze zmianą. "
  "Drugi częsty błąd: zapomniane zależności systemowe przy trafieniu w cache. "
  "Branch ratunkowy: solution/zadanie-03."),

 ("theory", "Joby, zależności i rozdzielanie sygnałów", [
    ("Każdy job to osobna maszyna — może biec równolegle", True),
    ("needs opisuje zależność, ale NIE przekazuje plików", True),
    ("Jeden job „test” daje jeden sygnał: zielony albo czerwony", True),
    ("Pięć jobów mówi, co dokładnie padło — bez wchodzenia w logi", True),
    ("Koszt: suma minut rośnie, czas oczekiwania spada", True),
 ],
  "Macie już rozsądną kolejność, ale wszystko nadal wykonuje się po kolei w jednym jobie. "
  "Lint nie potrzebuje wyniku typechecku, a jednak na niego czeka. "
  "Jest jeszcze drugi powód rozbicia, mniej oczywisty niż szybkość: rozdzielenie sygnałów. "
  "Jeden job o nazwie „test” mówi Wam tylko tyle, że coś padło. Pięć osobnych jobów mówi, co dokładnie — "
  "widzicie to na liście kontroli przy pull requeście, bez wchodzenia w logi. "
  "I od razu uprzedzam o koszcie: suma zużytych minut wzrośnie, bo każdy job to osobna maszyna "
  "z własnym narzutem. Czas oczekiwania spadnie. To jest ten kompromis."),

 ("task", "ZADANIE 04 — Rozbicie na joby i needs", [
    ("Wydziel: quality, unit, build, test-api, test-ui", True),
    ("Zastanów się, co NAPRAWDĘ od czego zależy", True),
    ("Obejrzyj graf zależności w zakładce Actions", True),
    ("Zmierz: czas przebiegu spada, suma minut rośnie — zrozum dlaczego", True),
 ],
  "Około dwudziestu pięciu minut. Przy needs zadajcie sobie za każdym razem pytanie: "
  "czy ten job naprawdę potrzebuje wyniku tamtego, czy tylko wydaje mi się, że tak jest porządniej? "
  "Najczęstszy błąd to nadmiarowe needs — na przykład uzależnianie testów od lintu. "
  "Brzmi rozsądnie, „po co testować kod, który nie przechodzi lintu”, ale w praktyce "
  "wydłuża drogę do wyniku testów, nie zapobiegając niczemu, bo i tak zablokuje to bramka scalania. "
  "Po tym zadaniu zauważycie, że ten sam setup powtarza się w pięciu miejscach. Tak, to problem. "
  "Wrócimy do niego, ale dopiero w ZADANIU 17 — chcę, żebyście najpierw poczuli, jak bardzo przeszkadza."),

 ("theory", "Artefakty — zbuduj raz, testuj wszędzie", [
    ("needs przekazuje sygnał, nie pliki — job nie widzi dist/", True),
    ("Skutek: aplikacja budowana trzy razy w trzech jobach", True),
    ("Artefakt to ten sam bajt w każdym jobie — determinizm", True),
    ("Build ukryty w webServer: błąd kompilacji udaje błąd testu", True),
 ],
  "Tu jest pułapka, na którą wpada prawie każdy przy pierwszym rozbiciu na joby. "
  "needs mówi „poprzedni job się udał”, ale nie przekazuje ani jednego pliku. "
  "Job test-ui nie widzi katalogu dist zbudowanego w jobie build. "
  "W efekcie aplikacja jest budowana trzy razy, a job build nie robi nic użytecznego — "
  "sprawdza tylko, czy kod się kompiluje, i wyrzuca wynik do kosza. "
  "Jest jeszcze druga, poważniejsza rzecz: build w naszym repo jest ukryty wewnątrz konfiguracji "
  "Playwrighta. Błąd kompilacji objawia się więc jako błąd testu i szukacie go w złym miejscu."),

 ("task", "ZADANIE 05 — Artefakt builda", [
    ("build publikuje dist/ jako artefakt", True),
    ("test-api i test-ui pobierają artefakt zamiast budować od nowa", True),
    ("Wyjmij npm run build z webServer w playwright.config.ts", True),
    ("Zepsuj kompilację i sprawdź, GDZIE teraz pada pipeline", True),
 ],
  "Dwadzieścia pięć minut. Punkt czwarty jest najciekawszy — zepsujcie kompilację celowo, "
  "wystarczy jedna linijka z błędnym typem, i zobaczcie, że pipeline pada teraz w jobie build, "
  "a joby testowe w ogóle nie startują. To jest prawdziwy fail-fast. "
  "Uwaga praktyczna: po wyjęciu builda z webServer lokalne uruchomienie testów przestanie działać "
  "na czystym repo, bo nie ma czego uruchomić. Trzeba to opisać w README albo dodać skrypt. "
  "I zapamiętajcie ten wzorzec: job buduje artefakt, job testowy go pobiera i uruchamia. "
  "To jest dokładnie to samo, co „wdróż na środowisko i przetestuj” — różni się tylko adresem."),

 ("theory", "Bezpieczeństwo jako część jakości", [
    ("Branch z tokenem API w kodzie przeszedł na zielono", True),
    ("Dwie różne rzeczy: podatności w zależnościach i sekrety w kodzie", True),
    ("gitleaks skanuje historię, nie tylko bieżące pliki", True),
    ("Decyzja: blokować czy ostrzegać? To zależy od kosztu pomyłki", True),
 ],
  "Wracamy do tego, co zobaczyliście w pierwszym zadaniu. Branch z zahardkodowanym tokenem płatniczym "
  "przeszedł bez słowa. Nie dlatego, że coś zawiodło — po prostu nikt nie dodał takiej kontroli. "
  "Rozdzielmy dwie rzeczy, bo bywają mylone. npm audit sprawdza znane podatności w zależnościach. "
  "gitleaks szuka sekretów w Waszym własnym kodzie — i co ważne, przeszukuje historię, "
  "bo sekret usunięty w ostatnim commicie nadal jest sekretem ujawnionym. "
  "I pytanie, na które nie ma jednej odpowiedzi: blokować merge czy tylko ostrzegać? "
  "Zależy od tego, ile kosztuje pomyłka w każdą stronę."),

 ("task", "ZADANIE 06 — Skan bezpieczeństwa", [
    ("Równoległy job: npm audit --audit-level=high", True),
    ("gitleaks z regułą z .gitleaks.toml", True),
    ("Sprawdź na demo/failing-security — teraz musi paść", True),
    ("Do dyskusji: continue-on-error czy blokowanie merge'a", True),
 ],
  "Dwadzieścia minut. Zwróćcie uwagę na dwie flagi w rozwiązaniu. "
  "Pierwsza to --redact: bez niej narzędzie, które wykrywa wycieki sekretów, "
  "wypisałoby ten sekret do logów, które w repozytorium publicznym może przeczytać każdy. "
  "Druga to ograniczenie skanu do bieżącej gałęzi — i to jest błąd, na który sam wpadłem, "
  "przygotowując ten warsztat. Domyślnie gitleaks skanuje wszystkie gałęzie, więc sekret z brancha demo "
  "wywalał skan na każdym innym branchu. Zobaczycie to w treści zadania jako pułapkę."),

 ("theory", "Kontrakt API i zmiany łamiące", [
    ("Aplikacja wystawia swój kontrakt: /api/openapi.json i /api/docs", True),
    ("Usunięte pole wychodzi dziś z padających testów UI konsumenta", True),
    ("Kilkanaście minut później i w zupełnie innym miejscu niż przyczyna", True),
    ("Porównanie specyfikacji: kilkanaście sekund, równolegle z lintem", True),
 ],
  "Ten blok jest krótki, ale wprowadza sposób myślenia, który przydaje się daleko poza CI. "
  "Nasza aplikacja wystawia swój kontrakt jako OpenAPI — możecie go zobaczyć pod /api/docs. "
  "Wyobraźcie sobie, że ktoś zmienia nazwę pola w odpowiedzi. Dziś dowiecie się o tym dopiero wtedy, "
  "gdy padną testy UI konsumenta tego API — kilkanaście minut później i w zupełnie innym miejscu "
  "niż przyczyna. Porównanie dwóch wersji specyfikacji kosztuje kilkanaście sekund "
  "i wskazuje przyczynę wprost."),

 ("task", "ZADANIE 07 — Kontrakt API", [
    ("npm run openapi:dump zapisuje spec BEZ podnoszenia serwera", True),
    ("Porównaj spec z main i z PR-a narzędziem oasdiff", True),
    ("Wymaga fetch-depth: 0 — porównujemy dwie wersje", True),
    ("Do dyskusji: jak przepuścić świadomą zmianę łamiącą?", True),
 ],
  "Dwadzieścia minut. Zwróćcie uwagę, dlaczego spec da się zapisać bez uruchamiania aplikacji — "
  "gdyby trzeba było ją podnieść, ten check przestałby być tani, a cała jego wartość polega na tym, "
  "że kosztuje kilkanaście sekund i biegnie równolegle z lintem. "
  "Pytanie na dyskusję jest realne: czasem zmiana łamiąca jest świadoma i konieczna. "
  "Jak ją przepuścić, nie wyłączając całej kontroli? To ten sam problem, co przy bezpieczeństwie."),

 ("theory", "Smoke kontra regresja — jak wybrać pięć testów", [
    ("Pull request pyta o jedno: czy coś oczywistego się zepsuło?", True),
    ("Smoke to nie „szybkie testy”, tylko ścieżka krytyczna", True),
    ("Nasze pięć: katalog, wyszukiwanie, koszyk, suma, zamówienie", True),
    ("Pełna regresja na main — jej wynik bramkuje wydanie, nie review", True),
    ("Trzeci tryb: nocny cron dla tego, co nie musi być natychmiast", True),
 ],
  "Teraz decyzja, która wymaga wiedzy testerskiej, a nie znajomości GitHub Actions. "
  "Które testy uruchamiać na pull requeście? Pull request zadaje jedno pytanie: "
  "czy coś oczywistego się zepsuło. Smoke to nie jest po prostu „szybkie testy” — "
  "to jest ścieżka, bez której produkt nie ma sensu. "
  "U nas jest ich pięć i przechodzą całą drogę klienta: od katalogu do złożonego zamówienia. "
  "Pełna regresja idzie na main, bo tam jej wynik bramkuje wydanie, a nie czyjeś review. "
  "I trzeci tryb, o którym często się zapomina: nocny przebieg dla rzeczy, "
  "które nie muszą być znane natychmiast."),

 ("task", "ZADANIE 08 — Trzy tryby uruchomienia", [
    ("Tagi @smoke i --grep na pull requestach", True),
    ("Pełna regresja na main", True),
    ("on: schedule — nocny przebieg (cron działa, bo to nie jest fork)", True),
    ("workflow_dispatch z wyborem zakresu: smoke, regression, all", True),
 ],
  "Dwadzieścia pięć minut. Ciekawostka, o której warto wiedzieć: cron u nas zadziała, "
  "bo Wasze repozytorium powstało z szablonu, czyli jest zwykłym repozytorium. "
  "W forkach scheduled workflows są wyłączone — gdybyśmy poszli drogą forka, to zadanie by nie zadziałało. "
  "Efekt nocnego przebiegu zobaczycie dopiero jutro, więc dziś sprawdzamy tylko konfigurację. "
  "Mówię o tym uczciwie, bo nie chcę, żeby ktoś czekał na coś, co się dziś nie wydarzy."),

 ("theory", "Selektywność — co ta zmiana mogła zepsuć", [
    ("Zmiana w README nie może zepsuć testów UI", True),
    ("Dwa piętra decyzji: czy odpalać job i które testy w nim", True),
    ("paths-filter decyduje o jobie, --only-changed o testach", True),
    ("Filtr, który przepuszcza zmianę łamiącą, jest gorszy niż brak filtru", True),
 ],
  "Selektywność to najbardziej ryzykowna optymalizacja w całym dniu i chcę to powiedzieć wprost. "
  "Pomysł jest oczywisty: zmiana w README nie może zepsuć testów UI, więc po co je uruchamiać. "
  "Decyzja ma dwa piętra: czy w ogóle odpalać job, i które testy w nim uruchomić. "
  "Ale uwaga na ryzyko: filtr, który przepuści zmianę zdolną coś zepsuć, jest gorszy niż brak filtru, "
  "bo daje fałszywe poczucie bezpieczeństwa. U nas katalog src/shared jest używany i przez serwer, "
  "i przez frontend — dlatego pojawia się w obu filtrach."),

 ("task", "ZADANIE 09 — Selektywność na dwóch poziomach", [
    ("dorny/paths-filter: czy w ogóle uruchamiać testy UI", True),
    ("playwright --only-changed: które testy uruchomić", True),
    ("Pułapka: wymaga fetch-depth: 0, bez historii nie znajdzie nic", True),
    ("Pułapka: skipped ≠ success przy required checks", True),
 ],
  "Dwadzieścia minut. Dwie pułapki, obie bolesne. "
  "Pierwsza: --only-changed porównuje z historią gita, a domyślny płytki klon jej nie ma. "
  "Bez fetch-depth zero polecenie cicho nie znajduje nic i wszystko wygląda na zielone. "
  "Druga jest jeszcze gorsza i wrócimy do niej w ostatnim zadaniu: job pominięty to nie jest job udany. "
  "Jeśli ustawicie pominięty job jako wymaganą kontrolę, zablokujecie sobie wszystkie pull requesty, "
  "które go nie dotyczą."),
]
