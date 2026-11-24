"""Reprezentacje digrafow prostych i ich losowanie."""
from __future__ import annotations

import random
from collections.abc import Iterable

Digraph = dict[int, list[int]]
Arc = tuple[int, int]
WeightedArc = tuple[int, int, int]


def edges_to_digraph(n: int, arcs: Iterable[Arc]) -> Digraph:
    if n < 1:
        raise ValueError("Digraf musi miec co najmniej jeden wierzcholek.")
    graph = {v: [] for v in range(1, n + 1)}
    seen = set()
    for u, v in arcs:
        if u not in graph or v not in graph:
            raise ValueError("Numer wierzcholka poza zakresem 1..n.")
        if u == v:
            raise ValueError("Digraf prosty nie moze zawierac petli.")
        if (u, v) in seen:
            raise ValueError("Digraf prosty nie moze zawierac powtorzonych lukow.")
        seen.add((u, v))
        graph[u].append(v)
    return {u: sorted(vs) for u, vs in graph.items()}


def validate_digraph(graph: Digraph) -> int:
    if not graph:
        raise ValueError("Digraf musi zawierac co najmniej jeden wierzcholek.")
    n = len(graph)
    if set(graph) != set(range(1, n + 1)):
        raise ValueError("Wierzcholki musza byc numerowane kolejno od 1 do n.")
    for u, neighbors in graph.items():
        if len(neighbors) != len(set(neighbors)):
            raise ValueError(f"Powtorzony luk wychodzacy z wierzcholka {u}.")
        if any(v not in graph for v in neighbors):
            raise ValueError(f"Luk z wierzcholka {u} wskazuje nieistniejacy wierzcholek.")
        if u in neighbors:
            raise ValueError("Digraf prosty nie moze zawierac petli.")
    return n


def digraph_to_edges(graph: Digraph) -> list[Arc]:
    validate_digraph(graph)
    return [(u, v) for u in graph for v in sorted(graph[u])]


def adjacency_matrix(graph: Digraph) -> list[list[int]]:
    n = validate_digraph(graph)
    return [[int(v in graph[u]) for v in range(1, n + 1)] for u in range(1, n + 1)]


def incidence_matrix(graph: Digraph) -> list[list[int]]:
    """Macierz n x m: -1 przy zrodle luku, +1 przy jego celu."""
    n = validate_digraph(graph)
    arcs = digraph_to_edges(graph)
    matrix = [[0] * len(arcs) for _ in range(n)]
    for column, (u, v) in enumerate(arcs):
        matrix[u - 1][column] = -1
        matrix[v - 1][column] = 1
    return matrix


def incidence_to_digraph(matrix: list[list[int]]) -> Digraph:
    if not matrix or not matrix[0]:
        if matrix and all(not row for row in matrix):
            return {v: [] for v in range(1, len(matrix) + 1)}
        raise ValueError("Macierz incydencji musi miec co najmniej jeden wiersz.")
    n, m = len(matrix), len(matrix[0])
    if any(len(row) != m for row in matrix):
        raise ValueError("Macierz incydencji musi byc prostokatna.")
    arcs = []
    for col in range(m):
        values = [matrix[row][col] for row in range(n)]
        if any(value not in (-1, 0, 1) for value in values):
            raise ValueError("Macierz incydencji moze zawierac tylko -1, 0 i 1.")
        sources = [i + 1 for i, value in enumerate(values) if value == -1]
        targets = [i + 1 for i, value in enumerate(values) if value == 1]
        if len(sources) != 1 or len(targets) != 1:
            raise ValueError("Kazda kolumna musi miec jedno zrodlo (-1) i jeden cel (+1).")
        arcs.append((sources[0], targets[0]))
    return edges_to_digraph(n, arcs)


def transpose(graph: Digraph) -> Digraph:
    n = validate_digraph(graph)
    return edges_to_digraph(n, ((v, u) for u, v in digraph_to_edges(graph)))


def gnp_digraph(n: int, p: float, seed: int | None = None) -> Digraph:
    """Losuje kazdy z n(n-1) mozliwych lukow niezaleznie z prawdopodobienstwem p."""
    if n < 1:
        raise ValueError("n musi byc dodatnie.")
    if not 0 <= p <= 1:
        raise ValueError("p musi nalezec do przedzialu [0, 1].")
    rng = random.Random(seed)
    return edges_to_digraph(n, ((u, v) for u in range(1, n + 1)
                                for v in range(1, n + 1) if u != v and rng.random() < p))


def random_strongly_connected_weighted_digraph(
    n: int, p: float = 0.25, seed: int | None = None,
) -> tuple[Digraph, list[WeightedArc]]:
    """Buduje silnie spojny digraf z losowymi lukami i bez ujemnych cykli.

    Cykl skierowany zapewnia silna spojność. Dodatkowe luki losuje sie niezaleznie
    z parametrem p. Wagi powstaja jako dodatnia waga zredukowana plus roznica
    potencjalow, co zachowuje brak ujemnych cykli.
    """
    if n < 1:
        raise ValueError("n musi byc dodatnie.")
    if not 0 <= p <= 1:
        raise ValueError("p musi nalezec do przedzialu [0, 1].")
    rng = random.Random(seed)
    arcs = {(u, u % n + 1) for u in range(1, n + 1)} if n > 1 else set()
    for u in range(1, n + 1):
        for v in range(1, n + 1):
            if u != v and rng.random() < p:
                arcs.add((u, v))
    graph = edges_to_digraph(n, arcs)
    potentials = [0] + [rng.randint(0, 5) for _ in range(n)]
    weighted = [(u, v, rng.randint(1, 4) + potentials[v] - potentials[u])
                for u, v in digraph_to_edges(graph)]
    return graph, weighted
