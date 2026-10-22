# Grafy i ich zastosowania

To repozytorium ma już implementację algorytmów z zestawów 1–3, a dodatkowo przygotowałem interaktywną aplikację w Pythonie z użyciem Streamlit. Aplikacja ma podział na zestawy zadań i pozwala prezentować konkretne ćwiczenia z grafów w przejrzystej formie.

## Uruchomienie GUI

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
streamlit run src/grafy/gui.py
```

## Struktura aplikacji

Po wejściu do programu widzisz:

- stronę główną z zestawami 1, 2 i 3,
- rozdział na konkretne zadania w ramach każdego zestawu,
- opis zadania, co można zmieniać i co uruchamiać,
- wizualizację grafów na okręgu,
- analizę algorytmiczną dla zadań z danego zestawu.

## Zestaw 1

- kodowanie grafów w reprezentacjach: macierz sąsiedztwa, lista sąsiedztwa, macierz incydencji,
- konwersja między reprezentacjami,
- wizualizacja grafu na okręgu,
- generowanie grafów G(n, l) i G(n, p).

## Zestaw 2

- sprawdzanie ciągu graficznego,
- randomizacja grafu zachowująca stopnie wierzchołków,
- największa spójna składowa,
- generacja i analiza grafu eulerowskiego,
- grafy k-regularne,
- sprawdzanie hamiltonowości.

## Zestaw 3

- graf ważony z losowymi wagami,
- algorytm Dijkstry,
- macierz odległości,
- centrum i centrum minimax,
- minimalne drzewo rozpinające.

To daje wygodną prezentację ćwiczeń podczas laboratorium i pozwala szybko zmieniać dane wejściowe, wizualizować graf i uruchamiać algorytmy.
