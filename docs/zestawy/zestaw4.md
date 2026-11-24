# Zestaw 4

1. Kodowanie prostych digrafow jako listy sasiedztwa, macierzy sasiedztwa i macierzy incydencji. Generator G(n,p) losuje niezaleznie kazdy z n(n-1) mozliwych lukow; petle nie wystepuja.
2. Algorytm Kosaraju zwraca silnie spojne skladowe digrafu w czasie O(n + m).
3. Losowy silnie spojny digraf otrzymuje calkowite wagi z zakresu [-5, 10]. Konstrukcja wag przez potencjaly zachowuje brak ujemnych cykli, aby Bellman-Ford i Johnson zawsze mialy rozwiazanie.
4. Bellman-Ford wyznacza najkrotsze odleglosci od zadanego zrodla i zglasza ujemny cykl osiagalny ze zrodla. Johnson wyznacza macierz odleglosci dla wszystkich par; dla nieosiagalnych par zwraca `inf`.

## Uruchomienie

```console
python -m grafy digraph 7 0.3 --seed 10
python -m grafy set4 --n 12 --p 0.25 --source 1 --seed 10
```

Pierwsze polecenie pokazuje trzy reprezentacje losowego digrafu G(n,p) i jego silnie spojne skladowe. Drugie wykonuje caly zestaw na jednym losowym silnie spojnym digrafie: wypisuje wazone luki, skladowe Kosaraju, odleglosci Bellmana-Forda od wskazanego wierzcholka oraz macierz Johnsona.
