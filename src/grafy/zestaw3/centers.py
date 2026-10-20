"""Z3.4 - centrum (min suma odleglosci) i centrum minimax (min odleglosc do najdalszego). Zalezy od: Z3.3."""
from __future__ import annotations

from grafy.common.types import Matrix


def center(d: Matrix) -> tuple[int, int]:
    """(wierzcholek, suma odleglosci)."""
    raise NotImplementedError


def minimax_center(d: Matrix) -> tuple[int, int]:
    """(wierzcholek, odleglosc do najdalszego)."""
    raise NotImplementedError
