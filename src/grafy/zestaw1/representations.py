"""Z1.1 - reprezentacje grafow prostych i konwersje miedzy nimi (3 reprezentacje x 2 pkt)."""
from __future__ import annotations

from grafy.common.types import AdjList, Matrix


def matrix_to_list(m: Matrix) -> AdjList:
    raise NotImplementedError


def matrix_to_incidence(m: Matrix) -> Matrix:
    raise NotImplementedError


def list_to_matrix(adj: AdjList) -> Matrix:
    raise NotImplementedError


def list_to_incidence(adj: AdjList) -> Matrix:
    raise NotImplementedError


def incidence_to_matrix(inc: Matrix) -> Matrix:
    raise NotImplementedError


def incidence_to_list(inc: Matrix) -> AdjList:
    raise NotImplementedError


def convert(data, src: str, dst: str):
    """src/dst in {'matrix', 'list', 'incidence'}."""
    raise NotImplementedError
