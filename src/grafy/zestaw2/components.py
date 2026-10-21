from grafy.common.types import AdjList


def components(adj: AdjList) -> dict[int, int]:
    """comp[v] = numer skladowej (od 1); przeszukiwanie w glab."""
    comp = {v: -1 for v in adj}
    nr = 0
    for s in adj:
        if comp[s] == -1:
            nr += 1
            comp[s] = nr
            stack = [s]
            while stack:
                u = stack.pop()
                for v in adj[u]:
                    if comp[v] == -1:
                        comp[v] = nr
                        stack.append(v)
    return comp


def largest_component(adj: AdjList) -> list[int]:
    comp = components(adj)
    groups: dict[int, list[int]] = {}
    for v in sorted(comp):
        groups.setdefault(comp[v], []).append(v)
    return max(groups.values(), key=len) if groups else []