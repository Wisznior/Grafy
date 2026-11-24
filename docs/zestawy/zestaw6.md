# Zestaw 6

1. PageRank jest obliczany dwiema metodami na tym samym digrafie: jako częstość odwiedzin w losowym spacerze z teleportacją o prawdopodobieństwie d = 0,15 oraz przez iterację rozkładu prawdopodobieństwa do zbieżności. Domyślna lista sąsiedztwa z materiałów prowadzącej znajduje się w `data/examples/zestaw6/pagerank_graph.txt`. Generator losowego digrafu zapewnia co najmniej jeden łuk wychodzący z każdego wierzchołka.
2. TSP jest przybliżany symulowanym wyżarzaniem. Kandydat powstaje przez odwrócenie fragmentu trasy w ruchu 2-opt; gorszy ruch jest akceptowany z prawdopodobieństwem exp(-delta/T), a temperatura maleje wykładniczo. Punkty wejściowe są w `data/examples/zestaw6/tsp_points.txt` (dane z folderu zestawu 6).

## Uruchomienie

```console
python -m grafy set6 --seed 10 --draw output/zestaw6_tsp.png
```

Można podać własny graf sąsiedztwa przez `--graph-file`, własne współrzędne przez `--points-file`, liczbę kroków spaceru przez `--walk-steps` oraz liczbę prób 2-opt przez `--iterations`. Trasa TSP jest heurystyczna i nie ma gwarancji optimum globalnego.
