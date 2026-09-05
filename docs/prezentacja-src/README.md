# Źródło prezentacji

Prezentacja `docs/Szybki feedback w CICD - Warsztaty.pptx` jest **generowana**, a nie
edytowana ręcznie. Treść slajdów i notatek mówionych żyje w plikach `content_*.py`,
dzięki czemu zmiana w jednym miejscu nie rozjeżdża się z resztą materiałów.

## Jak przebudować

```bash
python3 -m venv /tmp/pptxenv
/tmp/pptxenv/bin/pip install python-pptx --index-url https://pypi.org/simple
cp "<talia bazowa>.pptx" /tmp/deck/base.pptx
/tmp/pptxenv/bin/python build.py
```

Talia bazowa dostarcza oprawę graficzną: wzorce slajdów, logotypy i slajd „o mnie".
Generator klonuje z niej trzy slajdy jako szablony — agendy, teorii i zadania —
i podmienia w nich tekst.

## Pliki

| Plik | Zawartość |
|---|---|
| `builder.py` | mechanika: klonowanie slajdów, podmiana tekstu, notatki |
| `build.py` | złożenie talii i usunięcie oryginalnych slajdów |
| `content_intro.py` | slajd tytułowy, agenda, blok wstępny |
| `content_chain1.py` | teoria i zadania 01–09 |
| `content_chain2.py` | teoria i zadania 10–18, domknięcie |

Notatki mówione są napisane jako **gotowa wypowiedź do uczestników**, nie jako hasła
dla prelegenta. Przy slajdach zadań zawierają dodatkowo przewidywany czas ćwiczenia,
najczęstszy błąd i zdanie ratunkowe (`git checkout solution/zadanie-XX`).
