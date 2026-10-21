from grafy.common.types import WeightedEdge


def minimum_spanning_tree(n: int, edges: list[WeightedEdge]) -> list[WeightedEdge]:
    """Kruskal + zbiory rozlaczne (wierzcholki od 1)."""
    parent = list(range(n + 1))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    tree = []
    for u, v, w in sorted(edges, key=lambda e: e[2]):
        ru, rv = find(u), find(v)
        if ru != rv:
            parent[ru] = rv
            tree.append((u, v, w))
            if len(tree) == n - 1:
                break
    return tree