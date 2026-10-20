"""Wspolne aliasy typow. Wierzcholki numerowane od 1 na granicy IO (patrz docs/FORMATY_DANYCH.md)."""
from __future__ import annotations

Matrix = list[list[int]]          # macierz sasiedztwa n x n / incydencji n x k
AdjList = dict[int, list[int]]    # {v: [sasiedzi]}
Edge = tuple[int, int]
WeightedEdge = tuple[int, int, int]
