from grafy.common.graph import edges_to_adj
from grafy.common.types import AdjList


def build_graph(seq: list[int]) -> AdjList:
    """Algorytm Havela-Hakimiego (degree_seq z materialow). ValueError, gdy ciag nie jest graficzny."""
    if any(d < 0 for d in seq) or sum(seq) % 2:
        raise ValueError("ciag nie jest graficzny")
    rem = [[d, i + 1] for i, d in enumerate(seq)]
    edges = []
    while True:
        rem.sort(key=lambda x: (-x[0], x[1]))
        d, v = rem[0] if rem else (0, 0)
        if d == 0:
            return edges_to_adj(len(seq), edges)
        if d > len(rem) - 1:
            raise ValueError("ciag nie jest graficzny")
        for item in rem[1:d + 1]:
            if item[0] == 0:
                raise ValueError("ciag nie jest graficzny")
            item[0] -= 1
            edges.append((v, item[1]))
        rem[0][0] = 0


def is_graphic(seq: list[int]) -> bool:
    try:
        build_graph(seq)
        return True
    except ValueError:
        return False