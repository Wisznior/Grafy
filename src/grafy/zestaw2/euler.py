"""Z2.4 - losowy graf eulerowski + cykl Eulera (Fleury).

Zalezy od: Z2.1 (ciag graficzny), Z2.2 (randomizacja), Z2.3 (skladowe/spojnosc).
Stopnie parzyste -> graf z Z2.1 -> randomizacja -> najwieksza spojna skladowa -> Fleury.
"""
from __future__ import annotations

from grafy.common.types import AdjList


def random_eulerian_graph(n: int | None = None, seed: int | None = None) -> AdjList:
    raise NotImplementedError


def euler_cycle(adj: AdjList, start: int | None = None) -> list[int]:
    raise NotImplementedError
