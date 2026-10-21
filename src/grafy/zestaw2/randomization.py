import random

from grafy.common.graph import adj_to_edges, edges_to_adj
from grafy.common.types import AdjList


def randomize(adj: AdjList, swaps: int, seed: int | None = None) -> AdjList:
    """swaps razy: losowe krawedzie ab, cd -> ad, cb (stopnie bez zmian, bez petli i multikrawedzi)."""
    rng = random.Random(seed)
    edges = adj_to_edges(adj)
    present = set(edges)
    done = attempts = 0
    while len(edges) >= 2 and done < swaps and attempts < swaps * 100 + 1000:
        attempts += 1
        i, j = rng.sample(range(len(edges)), 2)
        (a, b), (c, d) = edges[i], edges[j]
        if rng.random() < 0.5:
            c, d = d, c
        if len({a, b, c, d}) < 4:
            continue
        e1, e2 = (min(a, d), max(a, d)), (min(c, b), max(c, b))
        if e1 in present or e2 in present:
            continue
        present -= {edges[i], edges[j]}
        present |= {e1, e2}
        edges[i], edges[j] = e1, e2
        done += 1
    return edges_to_adj(len(adj), edges)