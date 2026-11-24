"""Algorytm Bellmana-Forda dla digrafow wazonych."""
from math import inf
from collections.abc import Iterable

from grafy.zestaw4.directed_graph import WeightedArc

Distance = int | float


class NegativeCycleError(ValueError):
    """W grafie osiagalnym ze zrodla wystepuje ujemny cykl."""


def bellman_ford(n: int, arcs: Iterable[WeightedArc], source: int):
    """Zwraca (odleglosci, poprzednicy), kluczami sa wierzcholki 1..n."""
    if n < 1 or not 1 <= source <= n:
        raise ValueError("n i zrodlo musza wskazywac wierzcholki numerowane od 1.")
    edges = list(arcs)
    for u, v, _ in edges:
        if not (1 <= u <= n and 1 <= v <= n):
            raise ValueError("Luk wskazuje wierzcholek poza zakresem 1..n.")
    distance = {v: inf for v in range(1, n + 1)}
    predecessor = {v: None for v in range(1, n + 1)}
    distance[source] = 0
    for _ in range(n - 1):
        changed = False
        for u, v, weight in edges:
            if distance[u] != inf and distance[v] > distance[u] + weight:
                distance[v] = distance[u] + weight
                predecessor[v] = u
                changed = True
        if not changed:
            break
    if any(distance[u] != inf and distance[v] > distance[u] + weight
           for u, v, weight in edges):
        raise NegativeCycleError("Ujemny cykl jest osiagalny ze wskazanego zrodla.")
    return distance, predecessor
