"""Z2.3 - spojne skladowe (DFS: components / components_R) + najwieksza skladowa."""
from __future__ import annotations

from grafy.common.types import AdjList


def components(adj: AdjList) -> dict[int, int]:
    """comp[v] = numer skladowej."""
    raise NotImplementedError


def largest_component(adj: AdjList) -> list[int]:
    raise NotImplementedError
