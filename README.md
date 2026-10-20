# Grafy i ich zastosowania – laboratorium (AGH)

Repozytorium zespołu: projekty z zestawów 1–6.
Prowadząca: dr Elżbieta Strzałka (p. 232/D-10) · kurs na UPeL: *Grafy i ich zastosowania – laboratorium*.

## Zespół
| Osoba | GitHub | Obszar |
|-------|--------|--------|
| ...   | @...   | ...    |

## Zasady zaliczenia (z prezentacji prowadzącej)
- 6 zestawów = 6 projektów w zespołach (4 zespoły po 3–4 osoby), max **10 pkt** za projekt.
- Ocena z laboratorium = suma punktów przeliczona na % → skala z Regulaminu Studiów AGH.
- Ocena końcowa = (O_L + O_S) / 2.
- Prezentacja: **max 15 min na projekt (wliczając pytania)**, każdy z zespołu wie, co jest w projekcie.
- **Wymagany link do źródła** implementowanej wersji algorytmu (albo tytuł + autor książki) → `docs/ZRODLA.md`.
- Biblioteki (NetworkX, igraph…) dozwolone, **o ile algorytmy wymagane w treści zestawu są napisane samodzielnie**.
- Język dowolny (tu: Python), forma dowolna (CLI/GUI), wizualizacja np. Graphviz/matplotlib.

Szczegóły i harmonogram: `docs/ZASADY.md`.

## Struktura
```
src/grafy/
  common/        # wspólne: IO, typy, walidacja grafu prostego
  zestaw1/       # reprezentacje, wizualizacja na okręgu, G(n,l), G(n,p)
  zestaw2/       # ciąg graficzny, randomizacja, składowe, Euler, k-regularne, Hamilton
  zestaw3/       # graf ważony, Dijkstra, macierz odległości, centra, MST
  cli.py         # punkt wejścia: python -m grafy <komenda>
tests/           # pytest; przykłady z PDF-ów prowadzącej w data/examples/
data/examples/   # przykładowe wejścia/wyjścia z materiałów
docs/            # zasady, formaty danych, źródła algorytmów, treści zestawów
issues/          # tasks.json = definicja tasków (źródło prawdy dla Issues)
scripts/         # create_issues.py – zakłada Issues + zależności przez `gh`
output/          # wygenerowane obrazki/wyniki (ignorowane przez git)
```

## Start
```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest            # na starcie testy są xfail (NotImplementedError) – zielone
python -m grafy --help
```

## Workflow
1. Założ Issues: `python scripts/create_issues.py --repo ORG/REPO` (najpierw `--dry-run`). Wymaga `gh auth login`.
2. Weź task, który **nie ma label `blocked`** (zależności zamknięte). Przypisz się.
3. Branch `zN-M-krotki-opis` (np. `z2-4-euler`), PR z szablonu, review od jednej osoby z zespołu.
4. Po zamknięciu taska zdejmij label `blocked` z tasków, które na nim czekały.
5. Przed prezentacją: uzupełnij `docs/ZRODLA.md` i zamknij issue „Prezentacja zestawu N”.
