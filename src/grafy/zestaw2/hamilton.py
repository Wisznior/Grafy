"""Z2.6 - cykl Hamiltona (brute force DFS ze stosem; tylko male grafy)."""
from __future__ import annotations

from grafy.common.types import AdjList


def hamilton_cycle(adj: AdjList) -> list[int] | None:
    """Cykl [v1, ..., vn, v1] albo None, gdy graf nie jest hamiltonowski."""
    raise NotImplementedError
