"""Z1.3 - grafy losowe Erdosa-Renyi: G(n,l) i G(n,p) (2 x 1 pkt). Bez petli i krawedzi wielokrotnych."""
from __future__ import annotations

from grafy.common.types import AdjList


def gnl(n: int, l: int, seed: int | None = None) -> AdjList:
    """l w [0, n(n-1)/2] krawedzi wybranych losowo."""
    raise NotImplementedError


def gnp(n: int, p: float, seed: int | None = None) -> AdjList:
    """Kazda z n(n-1)/2 mozliwych krawedzi z prawdopodobienstwem p."""
    raise NotImplementedError
