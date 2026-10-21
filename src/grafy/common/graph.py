from grafy.common.types import AdjList, Edge


def edges_to_adj(n: int, edges) -> AdjList:
    adj = {v: [] for v in range(1, n + 1)}
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    return {v: sorted(nb) for v, nb in adj.items()}


def adj_to_edges(adj: AdjList) -> list[Edge]:
    return sorted((u, v) for u, nb in adj.items() for v in nb if u < v)