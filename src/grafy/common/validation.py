from grafy.common.types import AdjList, Matrix

def is_simple_adjacency_matrix(m: Matrix) -> bool:
    n = len(m)
    return all(len(r) == n for r in m) and all(
        m[i][i] == 0 and m[i][j] == m[j][i] and m[i][j] in (0, 1)
        for i in range(n) for j in range(n)
    )

def is_simple_adjacency_list(adj: AdjList) -> bool:
    return all(
        u not in nb and len(set(nb)) == len(nb) and all(v in adj and u in adj[v] for v in nb)
        for u, nb in adj.items()
    )