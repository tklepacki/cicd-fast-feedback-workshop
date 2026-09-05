# Źródło instrukcji przygotowania

Instrukcja istnieje w trzech postaciach o jednej treści:

| Postać | Plik | Do czego |
|---|---|---|
| Markdown | `docs/README.md` | wersja w repozytorium, czytana na GitHubie |
| HTML | `instrukcja.html` | opublikowana jako Artifact — link do rozesłania |
| `.docx` | `docs/Instrukcja przygotowania…docx` | dla organizatora, do druku i załączników |

`.docx` jest **generowany** przez `make_docx.py`, więc zmiana treści nie wymaga
formatowania dokumentu ręcznie:

```bash
/tmp/pptxenv/bin/pip install python-docx --index-url https://pypi.org/simple
/tmp/pptxenv/bin/python make_docx.py
```

Wersja HTML zapamiętuje zaznaczenia listy kontrolnej w `localStorage` przeglądarki
uczestnika — nic nie jest nigdzie wysyłane.
