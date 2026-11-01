"""Dwie metody wyznaczania PageRank dla skierowanego grafu."""
from __future__ import annotations

from collections.abc import Hashable, Mapping, Sequence
from pathlib import Path
import random

Node = Hashable
Digraph = dict[Node, list[Node]]


def validate_digraph(graph: Mapping[Node, Sequence[Node]]) -> list[Node]:
    if not graph:
        raise ValueError("Graf PageRank musi miec co najmniej jeden wierzcholek.")
    nodes = list(graph)
    node_set = set(nodes)
    for node, neighbors in graph.items():
        if len(neighbors) != len(set(neighbors)):
            raise ValueError(f"Powtorzony luk wychodzacy z wierzcholka {node}.")
        if any(neighbor not in node_set for neighbor in neighbors):
            raise ValueError(f"Luk z wierzcholka {node} wskazuje nieznany wierzcholek.")
    return nodes


def read_digraph(path) -> Digraph:
    """Czyta liste `wierzcholek: sasiad1, sasiad2`; etykiety moga byc tekstowe."""
    graph: Digraph = {}
    for line_number, raw_line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue
        if ":" not in line:
            raise ValueError(f"Linia {line_number}: oczekiwano formatu 'wierzcholek: sasiedzi'.")
        node_text, neighbor_text = line.split(":", 1)
        node = node_text.strip()
        if not node or node in graph:
            raise ValueError(f"Linia {line_number}: brak lub powtorzona etykieta wierzcholka.")
        graph[node] = [name for name in neighbor_text.replace(",", " ").split()]
    for neighbors in list(graph.values()):
        for node in neighbors:
            graph.setdefault(node, [])
    validate_digraph(graph)
    return graph


def random_digraph(n: int, p: float = 0.2, seed: int | None = None) -> dict[int, list[int]]:
    """Losuje digraf i uzupelnia kazdy pusty wiersz co najmniej jednym lukiem."""
    if n < 2:
        raise ValueError("Losowy digraf PageRank musi miec co najmniej 2 wierzcholki.")
    if not 0 <= p <= 1:
        raise ValueError("p musi nalezec do przedzialu [0, 1].")
    rng = random.Random(seed)
    graph = {u: [v for v in range(1, n + 1) if v != u and rng.random() < p]
             for u in range(1, n + 1)}
    for u, neighbors in graph.items():
        if not neighbors:
            neighbors.append(rng.choice([v for v in graph if v != u]))
    return graph


def pagerank_random_walk(graph: Mapping[Node, Sequence[Node]], damping: float = 0.15,
                         steps: int = 1_000_000, seed: int | None = None) -> dict[Node, float]:
    """Szacuje PageRank jako czestosc odwiedzin w losowym spacerze z teleportacja."""
    nodes = validate_digraph(graph)
    if not 0 <= damping <= 1 or steps < 1:
        raise ValueError("damping musi byc w [0, 1], a liczba krokow dodatnia.")
    rng = random.Random(seed)
    current = rng.choice(nodes)
    visits = dict.fromkeys(nodes, 0)
    for _ in range(steps):
        if rng.random() < damping or not graph[current]:
            current = rng.choice(nodes)
        else:
            current = rng.choice(graph[current])
        visits[current] += 1
    return {node: count / steps for node, count in visits.items()}


def pagerank_power_iteration(graph: Mapping[Node, Sequence[Node]], damping: float = 0.15,
                             tolerance: float = 1e-12, max_iterations: int = 10_000
                             ) -> tuple[dict[Node, float], int]:
    """Iteruje rozklad PageRank do zbieznosci; wynik to (ranking, liczba_iteracji)."""
    nodes = validate_digraph(graph)
    n = len(nodes)
    if not 0 <= damping <= 1 or tolerance <= 0 or max_iterations < 1:
        raise ValueError("Niepoprawne parametry iteracji PageRank.")
    rank = dict.fromkeys(nodes, 1 / n)
    for iteration in range(1, max_iterations + 1):
        updated = dict.fromkeys(nodes, damping / n)
        for source in nodes:
            neighbors = graph[source]
            if neighbors:
                share = (1 - damping) * rank[source] / len(neighbors)
                for target in neighbors:
                    updated[target] += share
            else:
                share = (1 - damping) * rank[source] / n
                for target in nodes:
                    updated[target] += share
        difference = sum(abs(updated[node] - rank[node]) for node in nodes)
        rank = updated
        if difference < tolerance:
            return rank, iteration
    return rank, max_iterations


def ranking(scores: Mapping[Node, float]) -> list[tuple[Node, float]]:
    return sorted(scores.items(), key=lambda item: (-item[1], str(item[0])))
