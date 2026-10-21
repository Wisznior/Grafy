import random

from grafy.common.types import AdjList
from grafy.zestaw2.components import largest_component
from grafy.zestaw2.degree_sequence import build_graph, is_graphic
from grafy.zestaw2.randomization import randomize


def random_eulerian_graph(n: int | None = None, seed: int | None = None) -> AdjList:
    """Parzyste stopnie -> graf -> randomizacja -> najwieksza spojna skladowa (przenumerowana od 1)."""
    rng = random.Random(seed)
    n = n or rng.randint(5, 12)
    if n < 3:
        raise ValueError("n >= 3")
    while True:
        seq = [rng.choice(range(2, n, 2)) for _ in range(n)]
        if is_graphic(seq):
            break
    adj = randomize(build_graph(seq), 100, rng.randrange(2**32))
    keep = largest_component(adj)
    new = {v: i + 1 for i, v in enumerate(keep)}
    return {new[v]: sorted(new[u] for u in adj[v]) for v in keep}


def _reachable(g, u, target) -> bool:
    seen, stack = {u}, [u]
    while stack:
        x = stack.pop()
        if x == target:
            return True
        for y in g[x]:
            if y not in seen:
                seen.add(y)
                stack.append(y)
    return False


def euler_cycle(adj: AdjList, start: int | None = None) -> list[int]:
    """Algorytm Fleury'ego: most przechodzimy tylko, gdy nie ma innej mozliwosci."""
    g = {v: set(nb) for v, nb in adj.items()}
    if any(len(nb) % 2 for nb in g.values()):
        raise ValueError("graf nie jest eulerowski (nieparzysty stopien)")
    m = sum(len(nb) for nb in g.values()) // 2
    u = start or next((v for v in sorted(g) if g[v]), None)
    if u is None:
        return []
    path = [u]
    for _ in range(m):
        nbs = sorted(g[u])
        if not nbs:
            raise ValueError("graf nie jest spojny")
        v = nbs[0]
        for cand in nbs:
            g[u].remove(cand)
            g[cand].remove(u)
            is_bridge = not _reachable(g, u, cand)
            g[u].add(cand)
            g[cand].add(u)
            if len(nbs) == 1 or not is_bridge:
                v = cand
                break
        g[u].remove(v)
        g[v].remove(u)
        path.append(v)
        u = v
    return path