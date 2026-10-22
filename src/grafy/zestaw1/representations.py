from __future__ import annotations

from typing import Any

Matrix = list[list[int]]
AdjList = dict[int, list[int]]


def matrix_to_list(m: Matrix) -> AdjList:
    if not m:
        return {}
    n = len(m)
    return {i + 1: [j + 1 for j in range(n) if m[i][j]] for i in range(n)}


def list_to_matrix(adj: AdjList) -> Matrix:
    vertices = sorted(adj)
    n = max(vertices, default=0)
    m = [[0] * n for _ in range(n)]
    for u in vertices:
        for v in adj.get(u, []):
            if u == v:
                raise ValueError("Graf prosty nie może mieć pętli.")
            if not 1 <= v <= n:
                raise ValueError(f"Błędny numer wierzchołka {v} dla grafu z {n} wierzchołkami.")
            m[u - 1][v - 1] = 1
    return m


def adj_to_edges(adj: AdjList) -> list[tuple[int, int]]:
    return sorted((u, v) for u, nb in adj.items() for v in nb if u < v)


def edges_to_adj(n: int, edges) -> AdjList:
    adj = {v: [] for v in range(1, n + 1)}
    for u, v in edges:
        if u == v:
            raise ValueError("Graf prosty nie może mieć pętli.")
        adj[u].append(v)
        adj[v].append(u)
    return {v: sorted(nb) for v, nb in adj.items()}


def list_to_incidence(adj: AdjList) -> Matrix:
    edges = adj_to_edges(adj)
    if not edges:
        return [[0] * 0 for _ in range(max(adj, default=0))]
    inc = [[0] * len(edges) for _ in range(max(adj, default=0))]
    for k, (u, v) in enumerate(edges):
        inc[u - 1][k] = 1
        inc[v - 1][k] = 1
    return inc


def incidence_to_list(inc: Matrix) -> AdjList:
    if not inc:
        return {}
    if not inc[0]:
        return {v: [] for v in range(1, len(inc) + 1)}
    edges = []
    for col in zip(*inc):
        vertices = [i + 1 for i, x in enumerate(col) if x]
        if len(vertices) != 2:
            raise ValueError("Każda kolumna macierzy incydencji musi mieć dokładnie dwie jedynki.")
        edges.append((vertices[0], vertices[1]))
    return edges_to_adj(len(inc), edges)


def matrix_to_incidence(m: Matrix) -> Matrix:
    return list_to_incidence(matrix_to_list(m))


def incidence_to_matrix(inc: Matrix) -> Matrix:
    return list_to_matrix(incidence_to_list(inc))


_TO_LIST = {"matrix": matrix_to_list, "list": lambda x: x, "incidence": incidence_to_list}
_FROM_LIST = {"matrix": list_to_matrix, "list": lambda x: x, "incidence": list_to_incidence}


class Graph:
    """Prosta warstwa pomocnicza do edycji grafu w trzech reprezentacjach."""

    def __init__(self, n: int = 0, edges: list[tuple[int, int]] | None = None, adj: AdjList | None = None):
        self.n = n
        self.adj: AdjList = {v: [] for v in range(1, n + 1)}
        if adj is not None:
            self.set_adjacency_list(adj)
        elif edges is not None:
            self.set_adjacency_list(edges_to_adj(n, edges))

    def _validate_vertex(self, v: int):
        if not 1 <= v <= self.n:
            raise ValueError(f"Wierzchołek {v} nie należy do zbioru 1..{self.n}.")

    def add_edge(self, u: int, v: int):
        self._validate_vertex(u)
        self._validate_vertex(v)
        if u == v:
            raise ValueError("Graf prosty nie może mieć pętli.")
        if v not in self.adj[u]:
            self.adj[u].append(v)
            self.adj[v].append(u)
        self.adj[u].sort()
        self.adj[v].sort()

    def remove_edge(self, u: int, v: int):
        self._validate_vertex(u)
        self._validate_vertex(v)
        if v in self.adj[u]:
            self.adj[u].remove(v)
            self.adj[v].remove(u)

    def set_adjacency_list(self, adj: AdjList):
        vertices = sorted(adj)
        self.n = max(vertices, default=0)
        self.adj = {v: sorted(set(nb)) for v, nb in adj.items()}
        for v in range(1, self.n + 1):
            self.adj.setdefault(v, [])

    def set_adjacency_matrix(self, m: Matrix):
        self.n = len(m)
        self.adj = matrix_to_list(m)
        for v in range(1, self.n + 1):
            self.adj.setdefault(v, [])

    def set_incidence_matrix(self, inc: Matrix):
        self.n = len(inc)
        self.adj = incidence_to_list(inc)

    def to_adjacency_list(self) -> AdjList:
        return {k: sorted(v) for k, v in self.adj.items()}

    def to_adjacency_matrix(self) -> Matrix:
        return list_to_matrix(self.adj)

    def to_incidence_matrix(self) -> Matrix:
        return list_to_incidence(self.adj)


def convert(data, src: str, dst: str):
    """src, dst in {'matrix', 'list', 'incidence'}."""
    if src == dst:
        return data
    if src not in _TO_LIST or dst not in _FROM_LIST:
        raise ValueError(f"Nieobsługiwane konwersje: {src} -> {dst}")
    return _FROM_LIST[dst](_TO_LIST[src](data))
