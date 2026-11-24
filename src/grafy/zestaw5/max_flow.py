"""Algorytm Edmondsa-Karpa (Ford-Fulkerson z BFS)."""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass

from grafy.zestaw5.flow_network import Arc, FlowNetwork


@dataclass
class MaxFlowResult:
    value: int
    flows: dict[Arc, int]
    augmentations: list[tuple[list[int], int]]


def ford_fulkerson(network: FlowNetwork, source: int | None = None,
                   sink: int | None = None) -> MaxFlowResult:
    """Znajduje maksymalny przeplyw, wybierajac najkrotsze sciezki przez BFS."""
    source = network.source if source is None else source
    sink = network.sink if sink is None else sink
    vertices = set(network.vertices)
    if source not in vertices or sink not in vertices or source == sink:
        raise ValueError("Zrodlo i ujscie musza byc roznymi wierzcholkami sieci.")
    if any(u not in vertices or v not in vertices or u == v or capacity <= 0
           for (u, v), capacity in network.capacities.items()):
        raise ValueError("Luki musza laczyc rozne wierzcholki sieci i miec dodatnie przepustowosci.")

    flows = {arc: 0 for arc in network.capacities}
    augmentations: list[tuple[list[int], int]] = []
    while True:
        residual: dict[int, list[tuple[int, Arc, int, int]]] = {v: [] for v in vertices}
        for (u, v), capacity in network.capacities.items():
            forward = capacity - flows[(u, v)]
            if forward > 0:
                residual[u].append((v, (u, v), 1, forward))
            reverse = flows[(u, v)]
            if reverse > 0:
                residual[v].append((u, (u, v), -1, reverse))
        for neighbors in residual.values():
            neighbors.sort(key=lambda item: (item[0], item[1], item[2]))

        parent: dict[int, tuple[int, Arc, int, int] | None] = {source: None}
        queue = deque([source])
        while queue and sink not in parent:
            u = queue.popleft()
            for v, arc, direction, residual_capacity in residual[u]:
                if v not in parent:
                    parent[v] = (u, arc, direction, residual_capacity)
                    queue.append(v)
                    if v == sink:
                        break
        if sink not in parent:
            break

        path_steps = []
        path_vertices = [sink]
        vertex = sink
        while vertex != source:
            previous, arc, direction, residual_capacity = parent[vertex]
            path_steps.append((arc, direction, residual_capacity))
            path_vertices.append(previous)
            vertex = previous
        amount = min(step[2] for step in path_steps)
        for arc, direction, _ in path_steps:
            flows[arc] += direction * amount
        augmentations.append((list(reversed(path_vertices)), amount))

    value = sum(flow for (u, _), flow in flows.items() if u == source) - sum(
        flow for (_, v), flow in flows.items() if v == source
    )
    return MaxFlowResult(value=value, flows=flows, augmentations=augmentations)
