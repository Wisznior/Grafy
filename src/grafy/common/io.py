from pathlib import Path

from grafy.common.types import AdjList, Matrix
from grafy.common.validation import is_simple_adjacency_list, is_simple_adjacency_matrix


def _rows(path):
    return [l.split() for l in Path(path).read_text().splitlines()
            if l.strip() and not l.lstrip().startswith("#")]


def _int_matrix(path) -> Matrix:
    rows = [[int(x) for x in r] for r in _rows(path)]
    if len(rows) > 1 and all(r[0] == i + 1 for i, r in enumerate(rows)):
        rows = [r[1:] for r in rows]  # opcjonalny numer wiersza
    return rows


def read_adjacency_matrix(path) -> Matrix:
    m = _int_matrix(path)
    if not is_simple_adjacency_matrix(m):
        raise ValueError("to nie jest macierz sasiedztwa grafu prostego")
    return m


def read_incidence_matrix(path) -> Matrix:
    m = _int_matrix(path)
    if any(sum(col) != 2 for col in zip(*m)):
        raise ValueError("kazda kolumna macierzy incydencji musi miec dokladnie dwie jedynki")
    return m


def read_adjacency_list(path) -> AdjList:
    adj = {int(r[0].rstrip(".:")): sorted(int(x.strip(",")) for x in r[1:]) for r in _rows(path)}
    if sorted(adj) != list(range(1, len(adj) + 1)) or not is_simple_adjacency_list(adj):
        raise ValueError("niepoprawna lista sasiedztwa grafu prostego")
    return adj


def format_matrix(m: Matrix) -> str:
    return "\n".join(" ".join(map(str, r)) for r in m)


def format_adjacency_list(adj: AdjList) -> str:
    return "\n".join(f"{v}. " + " ".join(map(str, adj[v])) for v in sorted(adj))