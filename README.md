# Grafy

Projekt poświęcony grafom i algorytmom grafowym z sześciu zestawów zadań: reprezentacje grafów, analiza właściwości grafów, algorytmy optymalizacyjne i wizualizacja.

## Co jest w projekcie

- interaktywny wizualizator grafów w `src/grafy/gui.py`
- implementacje zadań z zestawów 1–6 w katalogu `src/grafy/`
- podstawowe moduły wspólne: typy grafów, konwersje, generatory i narzędzia pomocnicze

## Zestawy zadań

### Zestaw 1
- program kodujący graf prosty za pomocą macierzy sąsiedztwa, macierzy incydencji i listy sąsiedztwa
- moduł konwersji pomiędzy reprezentacjami
- wizualizacja grafu z wierzchołkami rozmieszczonymi na okręgu
- generowanie grafów losowych `G(n, l)` i `G(n, p)`

### Zestaw 2
- sprawdzanie ciągu graficznego i budowanie grafu o zadanych stopniach
- randomizacja grafów o zadanych stopniach
- znajdowanie największej spójnej składowej
- generowanie grafu eulerowskiego i znajdowanie cyklu Eulera
- generowanie grafów k-regularnych
- sprawdzanie Hamiltonowości grafu

### Zestaw 3
- losowy spójny graf z wagami na krawędziach
- algorytm Dijkstry
- macierz odległości
- centrum i centrum minimax grafu
- minimalne drzewo rozpinające

### Zestaw 4
- reprezentacje i generator losowych digrafów `G(n,p)`
- silnie spójne składowe wyznaczane algorytmem Kosaraju
- losowy silnie spójny digraf ważony i algorytm Bellmana-Forda
- macierz najkrótszych odległości wszystkich par wyznaczana algorytmem Johnsona

### Zestaw 5
- generator warstwowych sieci przepływowych z przepustowościami
- maksymalny przepływ algorytmem Edmondsa-Karpa (Ford-Fulkerson z BFS)

### Zestaw 6
- PageRank przez losowy spacer z teleportacją i iterację wektora
- symulowane wyżarzanie problemu komiwojażera z ruchami 2-opt

## Uruchomienie aplikacji GUI

Wymagane: Python 3.10+

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# lub .venv\Scripts\activate  # Windows
pip install -r requirements.txt
streamlit run src/grafy/gui.py
```

Aplikacja pozwala na:
- generowanie grafów z różnych modeli
- manualną zmianę krawędzi klikając wierzchołki / edytując graf
- wizualizację w okręgu
- prezentację listy sąsiedztwa, macierzy sąsiedztwa i macierzy incydencji
- analizę grafu (składowe, cykl Eulera, cykl Hamiltona)
- eksperymenty z wagami i Dijkstrą

## Zestaw 4 z wiersza poleceń

`python -m grafy digraph 7 0.3 --seed 10` generuje digraf `G(n,p)`, wypisuje trzy reprezentacje oraz znajduje jego silnie spójne składowe.

`python -m grafy set4 --n 12 --p 0.25 --source 1 --seed 10` wykonuje zadania zestawu 4 na jednym losowym silnie spójnym digrafie. Szczegóły opisano w [`docs/zestawy/zestaw4.md`](docs/zestawy/zestaw4.md).

`python -m grafy set5 --layers 3 --seed 10` generuje sieć przepływową, oblicza maksymalny przepływ i zapisuje rysunek `output/zestaw5_flow.png`. Szczegóły: [`docs/zestawy/zestaw5.md`](docs/zestawy/zestaw5.md).

`python -m grafy set6 --seed 10` porównuje dwie metody PageRank i optymalizuje trasę dla dołączonych danych TSP; zapisuje `output/zestaw6_tsp.png`. Szczegóły: [`docs/zestawy/zestaw6.md`](docs/zestawy/zestaw6.md).

## Struktura repozytorium

```text
Grafy/
├── README.md
├── requirements.txt
├── src/
│   └── grafy/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── gui.py
│       ├── common/
│       ├── zestaw1/
│       ├── zestaw2/
│       ├── zestaw3/
│       ├── zestaw4/
│       ├── zestaw5/
│       └── zestaw6/
└── issues/
```

## Dodatkowe informacje

Kod interaktywny z GUI znajduje się w pliku `src/grafy/gui.py`. To tam powinny być umieszczone elementy wizualne, generatory grafów, obsługa danych wejściowych i interakcje użytkownika.
