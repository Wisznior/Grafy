from grafy.common.types import AdjList


def hamilton_cycle(adj: AdjList) -> list[int] | None:
    """Brute force (DFS z nawrotami). Zwraca [1, ..., 1] albo None."""
    n = len(adj)
    if n < 3:
        return None
    path, seen = [1], {1}

    def dfs() -> bool:
        if len(path) == n:
            return 1 in adj[path[-1]]
        for v in adj[path[-1]]:
            if v not in seen:
                path.append(v)
                seen.add(v)
                if dfs():
                    return True
                path.pop()
                seen.remove(v)
        return False

    return path + [1] if dfs() else None