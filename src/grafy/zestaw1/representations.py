from grafy.common.graph import adj_to_edges, edges_to_adj
from grafy.common.types import AdjList, Matrix


def matrix_to_list(m: Matrix) -> AdjList:
    n = len(m)
    return {i + 1: [j + 1 for j in range(n) if m[i][j]] for i in range(n)}


def list_to_matrix(adj: AdjList) -> Matrix:
    n = len(adj)
    m = [[0] * n for _ in range(n)]
    for u, nb in adj.items():
        for v in nb:
            m[u - 1][v - 1] = 1
    return m


def list_to_incidence(adj: AdjList) -> Matrix:
    edges = adj_to_edges(adj)
    inc = [[0] * len(edges) for _ in adj]
    for k, (u, v) in enumerate(edges):
        inc[u - 1][k] = inc[v - 1][k] = 1
    return inc


def incidence_to_list(inc: Matrix) -> AdjList:
    edges = []
    for col in zip(*inc):
        u, v = [i + 1 for i, x in enumerate(col) if x]
        edges.append((u, v))
    return edges_to_adj(len(inc), edges)


def matrix_to_incidence(m: Matrix) -> Matrix:
    return list_to_incidence(matrix_to_list(m))


def incidence_to_matrix(inc: Matrix) -> Matrix:
    return list_to_matrix(incidence_to_list(inc))


_TO_LIST = {"matrix": matrix_to_list, "list": lambda x: x, "incidence": incidence_to_list}
_FROM_LIST = {"matrix": list_to_matrix, "list": lambda x: x, "incidence": list_to_incidence}


def convert(data, src: str, dst: str):
    """src, dst in {'matrix', 'list', 'incidence'}."""
    return _FROM_LIST[dst](_TO_LIST[src](data))