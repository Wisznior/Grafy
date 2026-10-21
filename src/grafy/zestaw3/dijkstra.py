from grafy.common.types import Matrix

INF = float("inf")


def dijkstra(w: Matrix, s: int):
    """w - macierz wag (0 = brak krawedzi), s - wierzcholek startowy (od 0). Zwraca (ds, ps)."""
    n = len(w)
    ds, ps, done = [INF] * n, [None] * n, [False] * n  # init
    ds[s] = 0
    for _ in range(n):
        u = min((v for v in range(n) if not done[v]), key=lambda v: ds[v])
        if ds[u] == INF:
            break
        done[u] = True
        for v in range(n):
            if w[u][v] and not done[v] and ds[v] > ds[u] + w[u][v]:  # relax
                ds[v] = ds[u] + w[u][v]
                ps[v] = u
    return ds, ps


def shortest_path(ps, s: int, v: int) -> list[int]:
    """Sciezka s -> v (numeracja od 0); [] gdy nieosiagalny."""
    path = [v]
    while path[-1] != s:
        p = ps[path[-1]]
        if p is None:
            return []
        path.append(p)
    return path[::-1]