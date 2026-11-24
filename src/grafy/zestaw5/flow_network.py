"""Generator warstwowych sieci przeplywowych i wizualizacja."""
from __future__ import annotations

from dataclasses import dataclass
import random
from pathlib import Path

Arc = tuple[int, int]


@dataclass(frozen=True)
class FlowNetwork:
    layers: list[list[int]]
    capacities: dict[Arc, int]

    @property
    def source(self) -> int:
        return self.layers[0][0]

    @property
    def sink(self) -> int:
        return self.layers[-1][0]

    @property
    def vertices(self) -> list[int]:
        return [v for layer in self.layers for v in layer]


def random_flow_network(intermediate_layers: int = 3, seed: int | None = None) -> FlowNetwork:
    """Losuje siec z N warstwami posrednimi wedlug tresci zestawu."""
    if intermediate_layers < 2:
        raise ValueError("Liczba warstw posrednich N musi byc co najmniej 2.")
    rng = random.Random(seed)
    layers = [[0]]
    next_vertex = 1
    for _ in range(intermediate_layers):
        width = rng.randint(2, intermediate_layers)
        layers.append(list(range(next_vertex, next_vertex + width)))
        next_vertex += width
    sink = next_vertex
    layers.append([sink])

    arcs: set[Arc] = set()
    for current, following in zip(layers, layers[1:]):
        # Kazdy wierzcholek ma luk wychodzacy, a kazdy nastepnej warstwy
        # co najmniej jeden wchodzacy.
        arcs.update((u, rng.choice(following)) for u in current)
        arcs.update((rng.choice(current), v) for v in following)

    vertices = [v for layer in layers for v in layer]
    candidates = [(u, v) for u in vertices for v in vertices
                  if u != v and v != layers[0][0] and u != sink and (u, v) not in arcs]
    extra_count = 2 * intermediate_layers
    if len(candidates) < extra_count:
        raise ValueError("Za malo mozliwych lukow do spelnienia wymagan generatora.")
    arcs.update(rng.sample(candidates, extra_count))
    capacities = {arc: rng.randint(1, 10) for arc in sorted(arcs)}
    return FlowNetwork(layers=layers, capacities=capacities)


def draw_flow_network(network: FlowNetwork, out_path, flows: dict[Arc, int] | None = None) -> None:
    """Rysuje warstwy, kierunki lukow oraz przepustowosci albo przeplywy/przepustowosci."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyArrowPatch

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    positions = {}
    for x, layer in enumerate(network.layers):
        for i, vertex in enumerate(layer):
            positions[vertex] = (x, ((len(layer) - 1) / 2 - i) * 2.1)
    tallest_layer = max(len(layer) for layer in network.layers)
    fig, ax = plt.subplots(figsize=(max(9, len(network.layers) * 2.2),
                                    max(7, tallest_layer * 1.8)))
    pairs = set(network.capacities)
    for u, v in sorted(pairs):
        x1, y1 = positions[u]
        x2, y2 = positions[v]
        reverse = (v, u) in pairs
        rad = (0.18 if u < v else -0.18) if reverse else (
            (((u * 17 + v * 13) % 5) - 2) * 0.075)
        arrow = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                mutation_scale=13, linewidth=1.25, color="#526579",
                                connectionstyle=f"arc3,rad={rad}", shrinkA=17, shrinkB=17,
                                zorder=1)
        ax.add_patch(arrow)
        label = (f"{flows.get((u, v), 0)}/{network.capacities[(u, v)]}"
                 if flows is not None else str(network.capacities[(u, v)]))
        dx, dy = x2 - x1, y2 - y1
        length = (dx * dx + dy * dy) ** 0.5 or 1
        fraction = 0.28 + ((u * 19 + v * 7) % 5) * 0.11
        offset = 0.22 if (u * 17 + v * 13) % 2 else -0.22
        mx = x1 + dx * fraction - dy / length * offset
        my = y1 + dy * fraction + dx / length * offset
        ax.text(mx, my, label, ha="center", va="center", fontsize=8,
                bbox={"fc": "white", "ec": "none", "pad": 1.0}, zorder=2)

    for vertex, (x, y) in positions.items():
        label = "s" if vertex == network.source else ("t" if vertex == network.sink else str(vertex))
        ax.scatter([x], [y], s=650, color="#dce9fa", edgecolors="#1769aa", zorder=3)
        ax.text(x, y, label, ha="center", va="center", fontsize=10, zorder=4)
    for x in range(len(network.layers)):
        ax.text(x, max((y for _, y in positions.values()), default=0) + 0.65,
                "Źródło" if x == 0 else ("Ujście" if x == len(network.layers) - 1
                                         else f"Warstwa {x}"),
                ha="center", color="#40566b", fontsize=9)
    ax.set_xlim(-0.55, len(network.layers) - 0.45)
    ax.set_ylim(min(y for _, y in positions.values()) - 0.75,
                max(y for _, y in positions.values()) + 1.0)
    ax.set_title("Siec przeplywowa: przeplyw / przepustowosc" if flows is not None
                 else "Losowa siec przeplywowa")
    ax.axis("off")
    fig.savefig(out_path, dpi=160, bbox_inches="tight")
    plt.close(fig)
