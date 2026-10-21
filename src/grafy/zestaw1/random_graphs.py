import random
from itertools import combinations

from grafy.common.graph import edges_to_adj
from grafy.common.types import AdjList


def gnl(n: int, l: int, seed: int | None = None) -> AdjList:
    pairs = list(combinations(range(1, n + 1), 2))
    if not 0 <= l <= len(pairs):
        raise ValueError(f"l musi byc z przedzialu [0, {len(pairs)}]")
    return edges_to_adj(n, random.Random(seed).sample(pairs, l))


def gnp(n: int, p: float, seed: int | None = None) -> AdjList:
    if not 0 <= p <= 1:
        raise ValueError("p musi byc z przedzialu [0, 1]")
    rng = random.Random(seed)
    return edges_to_adj(n, [e for e in combinations(range(1, n + 1), 2) if rng.random() < p])