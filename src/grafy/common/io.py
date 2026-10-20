"""Wczytywanie / zapisywanie reprezentacji grafow (zadanie 1.1 korzysta z tego modulu)."""
from __future__ import annotations

from pathlib import Path

from grafy.common.types import AdjList, Matrix


def read_adjacency_matrix(path: str | Path) -> Matrix:
    raise NotImplementedError


def read_adjacency_list(path: str | Path) -> AdjList:
    raise NotImplementedError


def read_incidence_matrix(path: str | Path) -> Matrix:
    raise NotImplementedError


def write_matrix(m: Matrix, path: str | Path | None = None) -> str:
    raise NotImplementedError


def write_adjacency_list(adj: AdjList, path: str | Path | None = None) -> str:
    raise NotImplementedError
