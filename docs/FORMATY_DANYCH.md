# Konwencje i formaty danych

Decyzje zespołu – zmieniamy tylko przez PR do tego pliku.

## Wierzchołki
- W plikach i na wyjściu numerujemy **od 1** (jak w materiałach prowadzącej).
- Wewnątrz kodu wolno 0-indeksowo, ale konwersja tylko na granicy IO (`grafy.common.io`).

## Reprezentacje grafu prostego (zestaw 1)
Jedno uruchomienie = jedna reprezentacja na wejściu; program wypisuje pozostałe dwie.
Wiodący numer wiersza w pliku jest opcjonalny (parser go toleruje).

| Reprezentacja | Typ w Pythonie | Plik |
|---|---|---|
| macierz sąsiedztwa n×n | `list[list[int]]` | n wierszy po n liczb 0/1 |
| lista sąsiedztwa | `dict[int, list[int]]` | `v: s1 s2 ...` (kropka po numerze opcjonalna) |
| macierz incydencji n×k | `list[list[int]]` | n wierszy po k liczb 0/1; kolejność kolumn dowolna |

Graf prosty = nieskierowany, bez pętli, bez krawędzi wielokrotnych – walidacja w `common/validation.py`.

## Graf ważony (zestaw 3)
Macierz wag `w[u][v]` (0 = brak krawędzi, wagi to liczby naturalne 1–10) albo lista krawędzi `u v w`.

## Wyniki
- Obrazki → `output/` (PNG/SVG).
- Teksty w formatach z przykładów prowadzącej (patrz `data/examples/`).
