"""Walidacja grafu prostego: nieskierowany, bez petli, bez krawedzi wielokrotnych."""
from grafy.common.types import AdjList, Matrix


def is_simple_adjacency_matrix(m: Matrix) -> bool:
    raise NotImplementedError


def is_simple_adjacency_list(adj: AdjList) -> bool:
    raise NotImplementedError
