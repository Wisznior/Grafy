"""Algorytm Johnsona dla macierzy najkrotszych odleglosci."""
from heapq import heappop, heappush
from math import inf
from collections.abc import Iterable

from grafy.zestaw4.bellman_ford import NegativeCycleError
from grafy.zestaw4.directed_graph import WeightedArc


def johnson(n: int, arcs: Iterable[WeightedArc]) -> list[list[int | float]]:
    """Zwraca macierz n x n odleglosci; inf oznacza brak drogi.

    Potencjaly liczone sa relaksacja jak w Bellmanie-Fordzie ze sztucznym
    zrodlem polaczonym lukami zerowymi do kazdego wierzcholka.
    """
    if n < 1:
        raise ValueError("n musi byc dodatnie.")
    edges = list(arcs)
    adjacency = {u: [] for u in range(1, n + 1)}
    for u, v, weight in edges:
        if not (1 <= u <= n and 1 <= v <= n):
            raise ValueError("Luk wskazuje wierzcholek poza zakresem 1..n.")
        adjacency[u].append((v, weight))

    potential = [0] * (n + 1)
    for _ in range(n - 1):
        changed = False
        for u, v, weight in edges:
            if potential[v] > potential[u] + weight:
                potential[v] = potential[u] + weight
                changed = True
        if not changed:
            break
    if any(potential[v] > potential[u] + weight for u, v, weight in edges):
        raise NegativeCycleError("Graf zawiera ujemny cykl.")

    result = []
    for source in range(1, n + 1):
        distances = {v: inf for v in range(1, n + 1)}
        distances[source] = 0
        queue = [(0, source)]
        while queue:
            distance, u = heappop(queue)
            if distance != distances[u]:
                continue
            for v, weight in adjacency[u]:
                reduced = weight + potential[u] - potential[v]
                candidate = distance + reduced
                if candidate < distances[v]:
                    distances[v] = candidate
                    heappush(queue, (candidate, v))
        result.append([inf if value == inf else value - potential[source] + potential[v]
                       for v, value in distances.items()])
    return result
