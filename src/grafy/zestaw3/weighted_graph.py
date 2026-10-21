import random
from pathlib import Path

from grafy.common.graph import adj_to_edges
from grafy.common.types import Matrix, WeightedEdge
from grafy.zestaw1.random_graphs import gnp
from grafy.zestaw2.components import components


def edges_to_matrix(n: int, edges: list[WeightedEdge]) -> Matrix:
    w = [[0] * n for _ in range(n)]
    for u, v, x in edges:
        w[u - 1][v - 1] = w[v - 1][u - 1] = x
    return w


def read_weighted_edges(path) -> tuple[int, list[WeightedEdge]]:
    """Plik: linie 'u v waga' (# = komentarz)."""
    edges = [tuple(map(int, l.split())) for l in Path(path).read_text().splitlines()
             if l.strip() and not l.startswith("#")]
    return max(max(u, v) for u, v, _ in edges), edges


def random_connected_weighted_graph(n: int, p: float = 0.3, w_min: int = 1, w_max: int = 10,
                                    seed: int | None = None):
    """G(n,p) + doklejenie krawedzi miedzy skladowymi + losowe wagi. Zwraca (krawedzie, macierz wag)."""
    rng = random.Random(seed)
    adj = gnp(n, p, rng.randrange(2**32))
    groups: dict[int, list[int]] = {}
    for v, c in components(adj).items():
        groups.setdefault(c, []).append(v)
    edges = set(adj_to_edges(adj))
    parts = list(groups.values())
    for a, b in zip(parts, parts[1:]):
        u, v = rng.choice(a), rng.choice(b)
        edges.add((min(u, v), max(u, v)))
    wedges = [(u, v, rng.randint(w_min, w_max)) for u, v in sorted(edges)]
    return wedges, edges_to_matrix(n, wedges)