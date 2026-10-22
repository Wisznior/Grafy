# Grafy i ich zastosowania

To repozytorium ma już implementację algorytmów z zestawów 1–3, ale żeby było wygodnie do prezentacji i testowania, dodałem także prosty interaktywny GUI w Pythonie z wykorzystaniem Streamlit.

## Uruchomienie GUI

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
streamlit run src/grafy/gui.py
```

Po uruchomieniu otworzy się aplikacja w przeglądarce, w której możesz:

- generować grafy losowe G(n, p) i G(n, l)
- budować graf z ciągu graficznego
- tworzyć grafy k-regularne
- zmieniać graf ręcznie przez dodawanie/usuwanie krawędzi
- oglądać graf na okręgu
- sprawdzać spójność, cykl Eulera, cykl Hamiltona
- uruchamiać algorytm Dijkstry na grafie ważonym

## Funkcje aplikacji

- sidebar do zmiany parametrów grafu
- przyciski akcji typu „Generate”, „Randomize”, „Check”
- podgląd macierzy sąsiedztwa, listy sąsiedztwa i macierzy incydencji
- wizualizacja grafu z numeracją wierzchołków
- szybkie analizy: największa składowa, Euler, Hamilton, Dijkstra

To jest najprostsza i najszybsza opcja GUI w Pythonie, która jest bardzo dobra do laboratorium i prezentacji. Jeśli w przyszłości chcesz, można łatwo rozbudować to o:

- drag & drop wierzchołków,
- edycję krawędzi na canvasie,
- bardziej zaawansowaną warstwę frontendową w JavaScript (React / Cytoscape / D3.js).
