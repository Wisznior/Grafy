"""Algorytm Kosaraju dla silnie spojnych skladowych."""
from grafy.zestaw4.directed_graph import Digraph, transpose, validate_digraph


def strongly_connected_components(graph: Digraph) -> list[list[int]]:
    """Zwraca skladowe Kosaraju; kazda jest posortowana rosnaco. O(n + m)."""
    n = validate_digraph(graph)
    visited = set()
    finish_order = []
    for start in range(1, n + 1):
        if start in visited:
            continue
        visited.add(start)
        stack = [(start, iter(graph[start]))]
        while stack:
            u, neighbors = stack[-1]
            v = next(neighbors, None)
            if v is None:
                finish_order.append(u)
                stack.pop()
            elif v not in visited:
                visited.add(v)
                stack.append((v, iter(graph[v])))

    reversed_graph = transpose(graph)
    assigned = set()
    result = []
    for start in reversed(finish_order):
        if start in assigned:
            continue
        component = []
        stack = [start]
        assigned.add(start)
        while stack:
            u = stack.pop()
            component.append(u)
            for v in reversed_graph[u]:
                if v not in assigned:
                    assigned.add(v)
                    stack.append(v)
        result.append(sorted(component))
    return result


def is_strongly_connected(graph: Digraph) -> bool:
    return len(strongly_connected_components(graph)) == 1
