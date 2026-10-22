# Grafy

Projekt poświęcony grafom i algorytmom grafowym z trzech zestawów zadań: reprezentacje grafów, analiza właściwości grafów, algorytmy optymalizacyjne i wizualizacja.

## Co jest w projekcie

- interaktywny wizualizator grafów w `src/grafy/gui.py`
- implementacje zadań z zestawów 1–3 w katalogu `src/grafy/`
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
│       └── zestaw3/
└── issues/
```

## Dodatkowe informacje

Kod interaktywny z GUI znajduje się w pliku `src/grafy/gui.py`. To tam powinny być umieszczone elementy wizualne, generatory grafów, obsługa danych wejściowych i interakcje użytkownika.
