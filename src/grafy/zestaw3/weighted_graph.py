"""Z3.1 - spojny graf losowy z wagami 1..10.

Zalezy od: Z1.3 (G(n,l)/G(n,p)) i Z2.3 (sprawdzenie spojnosci / dobranie skladowej).
"""
from __future__ import annotations

from grafy.common.types import Matrix, WeightedEdge


def random_connected_weighted_graph(
    n: int, p: float = 0.3, w_min: int = 1, w_max: int = 10, seed: int | None = None
) -> tuple[list[WeightedEdge], Matrix]:
    """Zwraca (lista krawedzi (u,v,w), macierz wag)."""
    raise NotImplementedError
