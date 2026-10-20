"""Z2.1 - ciag graficzny + konstrukcja grafu (algorytm 'degree_seq' z materialow prowadzacej)."""
from __future__ import annotations

from grafy.common.types import AdjList


def is_graphic(seq: list[int]) -> bool:
    """Skrot: nieparzysta liczba nieparzystych elementow => na pewno NIE graficzny."""
    raise NotImplementedError


def build_graph(seq: list[int]) -> AdjList:
    """Zbuduj graf prosty o stopniach z seq (ValueError, gdy ciag nie jest graficzny)."""
    raise NotImplementedError
