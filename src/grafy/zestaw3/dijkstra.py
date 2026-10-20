"""Z3.2 - Dijkstra (init / relax / dijkstra wg materialow). Zalezy od: Z3.1."""
from __future__ import annotations

from grafy.common.types import Matrix


def dijkstra(w: Matrix, s: int) -> tuple[list[float], list[int | None]]:
    """Zwraca (ds, ps): dlugosci najkrotszych sciezek i poprzedniki."""
    raise NotImplementedError


def shortest_path(ps: list[int | None], s: int, v: int) -> list[int]:
    raise NotImplementedError
