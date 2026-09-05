# -*- coding: utf-8 -*-
"""Slajdy tytułowe, agenda i blok wstępny."""

TITLE = "Szybki feedback w CI/CD: pipeline, który testuje i raportuje bez utraty jakości"
SUBTITLE = "Tomasz Klepacki"

NOTES_TITLE = (
    "Cześć, witam Was serdecznie na warsztatach „Szybki feedback w CI/CD”. "
    "Dzisiaj nie będziemy uczyć się pisać testów — one już są napisane i czekają na Was w repozytorium. "
    "Będziemy budować pipeline, który te testy uruchamia tak, żeby dawał Wam odpowiedź szybko, "
    "a nie po kwadransie. To jest cały dzień przy klawiaturze: osiemnaście zadań, "
    "między nimi krótka teoria, i za każdym razem mierzymy, czy to, co zrobiliśmy, faktycznie pomogło."
)

NOTES_ABOUT = (
    "Nim zaczniemy, dosłownie kilka słów o mnie. Testowaniem oprogramowania zajmuję się od kilkunastu lat, "
    "obecnie jako Test Lead i Test Automation Engineer. Prowadzę szkolenia, piszę na blogu automatyzacja.it "
    "i współtworzę podcast Testers Unplugged. Na co dzień mierzę się dokładnie z tym, o czym dziś mówimy — "
    "z pipeline'ami, które rosną, zwalniają i przestają dawać zespołowi użyteczną informację."
)

AGENDA = [
    ("Agenda", [
        ("Czym jest CI/CD i gdzie w tym wszystkim jest tester", True),
        ("Feedback loop jako metryka — dlaczego czekanie kosztuje", True),
        ("GitHub Actions: event, workflow, job, step, runner", True),
        ("ZADANIE 01 — mierzymy stan wyjściowy", True),
        ("Triggery, concurrency i kolejność kontroli (ZADANIA 02–03)", True),
        ("Rozbicie na joby, artefakt builda (ZADANIA 04–05)", True),
        ("Bezpieczeństwo i kontrakt API (ZADANIA 06–07)", True),
    ],
     "Spójrzmy pokrótce na agendę. Zaczniemy od podstaw — czym jest ciągła integracja i dostarczanie, "
     "i co z tego wynika dla nas jako testerów. Potem od razu siadamy do kodu: pierwsze zadanie to pomiar, "
     "bo bez liczby wyjściowej nie da się później powiedzieć, czy cokolwiek pomogło. "
     "Dalej idziemy krok po kroku: najpierw porządkujemy to, co mamy, potem dokładamy rzeczy, których brakuje."),

    ("Agenda", [
        ("Smoke na PR, pełna regresja na main (ZADANIE 08)", True),
        ("Selektywność — co ta zmiana mogła zepsuć (ZADANIE 09)", True),
        ("Równoległość i shardowanie (ZADANIA 10–11)", True),
        ("Flaki: retry, kwarantanna, dryf środowiska (ZADANIE 12)", True),
        ("Raportowanie: scalanie, JUnit, trace (ZADANIA 13–15)", True),
        ("Publikacja raportów i sekrety (ZADANIE 16)", True),
        ("Porządek i bramka scalania (ZADANIA 17–18)", True),
        ("Podsumowanie: baseline kontra finał na Waszych liczbach", True),
    ],
     "Druga połowa dnia to skala i raportowanie. Nauczymy się uruchamiać drogie testy selektywnie, "
     "rozkładać je na wiele maszyn i — co równie ważne — czytelnie raportować wynik. "
     "Osobny blok poświęcimy flakom, bo to najczęstszy powód, dla którego zespoły przestają ufać własnym testom. "
     "Na koniec porównamy stan wyjściowy z tym, co zbudujecie, na Waszych własnych pomiarach."),
]

INTRO = [
    ("Continuous Integration, Delivery, Deployment", [
        ("Continuous Integration — częsta integracja kodu, automatyczna weryfikacja", True),
        ("Continuous Delivery — gotowość do wdrożenia w każdej chwili, decyzja ręczna", True),
        ("Continuous Deployment — każda poprawna zmiana trafia na produkcję sama", True),
        ("Różnica między Delivery a Deployment to jedna decyzja: kto naciska guzik", True),
    ],
     "Zacznijmy od uporządkowania trzech pojęć, które bardzo często są mylone. "
     "Continuous Integration to praktyka częstego łączenia kodu i automatycznego sprawdzania, "
     "czy nadal wszystko działa. Continuous Delivery idzie dalej: oprogramowanie jest w każdej chwili "
     "gotowe do wdrożenia, ale ktoś musi podjąć decyzję. Continuous Deployment usuwa tę decyzję — "
     "każda zmiana, która przeszła pipeline, trafia na produkcję automatycznie. "
     "Zwróćcie uwagę, że różnica między Delivery a Deployment to nie technologia, tylko to, "
     "czy ufacie swoim testom na tyle, żeby oddać im ostatnią decyzję."),

    ("Gdzie w tym wszystkim jest tester", [
        ("To my decydujemy, czego pipeline dowodzi — i czego nie", True),
        ("Zielony pipeline znaczy dokładnie tyle, ile sprawdza", True),
        ("Kolejność i dobór kontroli to decyzja testerska, nie devopsowa", True),
        ("Dziś zobaczycie pipeline, który przepuszcza zepsuty lint i wyciek sekretu", True),
    ],
     "I teraz najważniejsze pytanie tego wstępu: gdzie w tym wszystkim jesteśmy my? "
     "Bardzo często CI/CD traktuje się jako temat devopsowy — ktoś ustawił, działa, nie dotykamy. "
     "Tymczasem to, czego pipeline dowodzi, jest decyzją testerską. "
     "Zielony pipeline nie znaczy „kod jest dobry”. Znaczy dokładnie tyle, ile ten pipeline sprawdza. "
     "Za chwilę zobaczycie repozytorium, w którym branch z zepsutym lintem i branch z zahardkodowanym "
     "tokenem płatniczym świecą na zielono. Nie dlatego, że coś jest zepsute — tylko dlatego, "
     "że nikt tych kontroli nie dodał."),

    ("Feedback loop — dlaczego czekanie kosztuje", [
        ("Cztery minuty to nie cztery minuty — to utrata kontekstu", True),
        ("Im później sygnał, tym drożej kosztuje poprawka", True),
        ("Metryka dnia: czas do pierwszego czerwonego sygnału", True),
        ("Nie: „ile trwa pipeline”, tylko: „jak szybko wiem, że coś jest nie tak”", True),
    ],
     "Kiedy mówimy, że pipeline trwa cztery minuty, to brzmi niegroźnie. Ale te cztery minuty "
     "nie są czterema minutami czekania — są momentem, w którym wychodzicie z zadania. "
     "Powrót do kontekstu, z którego się wyszło, kosztuje znacznie więcej niż sam czas przebiegu. "
     "Dlatego naszą metryką przez cały dzień nie będzie „ile trwa pipeline”, "
     "tylko „jak szybko dowiaduję się, że coś jest nie tak”. To są dwie różne liczby "
     "i zaraz zobaczycie, jak bardzo potrafią się rozjechać."),

    ("Piramida testów w kontekście CI", [
        ("Testy jednostkowe: tanie, szybkie, dużo — sekundy", True),
        ("Testy API: średni koszt, średnia pewność", True),
        ("Testy UI: najdroższe, najwolniejsze, najmniej przewidywalne", True),
        ("Wniosek dla pipeline'u: kolejność ma odpowiadać kosztowi", True),
        ("W naszym baseline jest dokładnie odwrotnie", True),
    ],
     "Piramidę testów znacie. Chcę ją jednak pokazać w innym świetle niż zwykle — nie jako proporcje "
     "liczby testów, tylko jako koszt uzyskania informacji. Test jednostkowy odpowiada w milisekundach. "
     "Test UI potrzebuje przeglądarki, zbudowanej aplikacji i działającego serwera. "
     "Skoro tak, to kolejność w pipelinie powinna odpowiadać kosztowi: najpierw to, co tanie. "
     "W repozytorium, które zaraz otworzycie, jest dokładnie odwrotnie — i to nie jest przypadek, "
     "tylko celowo przygotowany punkt wyjścia."),

    ("GitHub Actions — pojęcia", [
        ("Event — co uruchamia pipeline (push, pull_request, schedule)", True),
        ("Workflow — plik YAML w .github/workflows/", True),
        ("Job — zestaw kroków; każdy job to osobna maszyna", True),
        ("Step — pojedyncze polecenie albo gotowa akcja", True),
        ("Runner — maszyna, na której to wszystko się wykonuje", True),
    ],
     "Zanim dotkniemy YAML-a, pięć pojęć, które będą wracać przez cały dzień. "
     "Event to zdarzenie uruchamiające — push, pull request, harmonogram. "
     "Workflow to plik, który opisuje, co ma się stać. Job to zestaw kroków — "
     "i to jest najważniejsze do zapamiętania: każdy job dostaje własną, czystą maszynę. "
     "Step to pojedyncze polecenie. Runner to maszyna. "
     "Fakt, że joby są osobnymi maszynami, będzie miał dziś konsekwencje, których na początku nie widać — "
     "między innymi taką, że joby nie widzą nawzajem swoich plików."),

    ("Nasze warunki brzegowe", [
        ("Darmowe konto GitHub — 20 równoległych jobów na całe konto", True),
        ("Repozytorium publiczne: nielimitowane minuty i 4 vCPU zamiast 2", True),
        ("Tylko ubuntu-latest — bez większych runnerów", True),
        ("Aplikacja startuje na runnerze; BASE_URL przełącza na inne środowisko", True),
    ],
     "Ostatnia rzecz przed pierwszym zadaniem: warunki, w jakich dziś pracujemy. "
     "Wszyscy jesteśmy na darmowych kontach, więc mamy dwadzieścia równoległych jobów — "
     "i uwaga, ten limit liczy się dla całego konta, nie dla repozytorium. "
     "Repozytorium musi być publiczne, bo wtedy minuty są darmowe, a runner dostaje cztery rdzenie "
     "zamiast dwóch. To drugie okaże się dziś istotne. "
     "Aplikacja testowa startuje na tym samym runnerze co testy — ale jest tak napisana, "
     "że jedna zmienna środowiskowa przełącza cały zestaw na dowolne inne środowisko."),
]
