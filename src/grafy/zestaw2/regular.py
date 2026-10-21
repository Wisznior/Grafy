from grafy.common.types import AdjList
from grafy.zestaw2.degree_sequence import build_graph
from grafy.zestaw2.randomization import randomize


def random_k_regular(n: int, k: int, seed: int | None = None) -> AdjList:
    if not 0 <= k < n or n * k % 2:
        raise ValueError("wymagane: 0 <= k < n oraz n*k parzyste")
    return randomize(build_graph([k] * n), 100 + 10 * n * k, seed)