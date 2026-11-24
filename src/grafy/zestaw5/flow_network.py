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


def example_network() -> FlowNetwork:
    """Siec z rys. 1 w tresci zestawu (N = 3), maksymalny przeplyw = 19."""
    s, a, b, c, d, e, f, g, h, i, t = range(11)
    capacities = {
        (s, a): 10, (s, b): 3, (s, c): 6,
        (a, b): 8, (a, d): 8, (a, e): 6, (b, e): 2, (b, f): 10, (c, d): 9, (c, f): 1,
        (e, d): 1, (d, h): 6, (e, i): 9, (f, g): 7, (h, f): 8, (h, g): 1,
        (g, t): 7, (h, t): 5, (i, t): 7,
    }
    return FlowNetwork(layers=[[s], [a, b, c], [d, e, f], [g, h, i], [t]], capacities=capacities)


def vertex_label(network: FlowNetwork, vertex: int) -> str:
    """s i t dla zrodla i ujscia, pozostale litery a, b, c, ... (jak w tresci zadania)."""
    if vertex == network.source:
        return "s"
    if vertex == network.sink:
        return "t"
    inner = [v for v in network.vertices if v not in (network.source, network.sink)]
    if all(1 <= v <= 18 for v in inner):
        return chr(ord("a") + vertex - 1)
    return str(vertex)


_X_STEP, _Y_STEP = 3.0, 2.2
_COLORS = {"capacity": "#4a5d70", "empty": "#c3ccd5", "flow": "#1f77b4", "saturated": "#d62728",
           "path": "#2ca02c", "cancel": "#ff7f0e"}


def _positions(network: FlowNetwork) -> dict[int, tuple[float, float]]:
    return {vertex: (x * _X_STEP, ((len(layer) - 1) / 2 - i) * _Y_STEP)
            for x, layer in enumerate(network.layers) for i, vertex in enumerate(layer)}


def _arc_bend(network: FlowNetwork, u: int, v: int, layer_of: dict[int, int]) -> float:
    if (v, u) in network.capacities:
        return 0.2
    if layer_of[u] == layer_of[v]:
        return 0.45
    if abs(layer_of[u] - layer_of[v]) > 1:
        return 0.22 if (u + v) % 2 else -0.22
    return (((u * 17 + v * 13) % 5) - 2) * 0.06


def flow_network_figure(network: FlowNetwork, flows: dict[Arc, int] | None = None,
                        path_arcs: list[tuple[Arc, int]] | None = None, amount: int | None = None,
                        title: str | None = None):
    """Zwraca figure matplotlib z siecia.

    flows: etykiety `przeplyw/przepustowosc` i kolory wg przeplywu,
    path_arcs: luki biezacej sciezki powiekszajacej z kierunkiem (+1 / -1 = cofniecie przeplywu).
    """
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.patches import FancyArrowPatch

    positions = _positions(network)
    layer_of = {v: x for x, layer in enumerate(network.layers) for v in layer}
    on_path = dict(path_arcs or [])
    placed: list[tuple[float, float]] = []
    xs = [x for x, _ in positions.values()]
    ys = [y for _, y in positions.values()]
    x_min, x_max = min(xs) - 0.8, max(xs) + 0.8
    y_min, y_max = min(ys) - 1.2, max(ys) + 1.3
    fig, ax = plt.subplots(figsize=((x_max - x_min) * 0.85, (y_max - y_min) * 0.85), dpi=110)

    for (u, v), capacity in sorted(network.capacities.items()):
        (x1, y1), (x2, y2) = positions[u], positions[v]
        rad = _arc_bend(network, u, v, layer_of)
        flow = flows.get((u, v), 0) if flows is not None else None
        style, width, text_color = "-", 1.3, "#22313f"
        if flows is None:
            color = _COLORS["capacity"]
        elif flow == 0:
            color, text_color = _COLORS["empty"], "#7b8794"
        elif flow == capacity:
            color, width = _COLORS["saturated"], 1.6 + 2.4 * flow / capacity
        else:
            color, width = _COLORS["flow"], 1.6 + 2.4 * flow / capacity
        if (u, v) in on_path:
            cancel = on_path[(u, v)] < 0
            color = _COLORS["cancel"] if cancel else _COLORS["path"]
            width, style = 4.2, "--" if cancel else "-"
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=14,
                                     linewidth=width, linestyle=style, color=color,
                                     connectionstyle=f"arc3,rad={rad}", shrinkA=16, shrinkB=16,
                                     zorder=3 if (u, v) in on_path else 1))

        # Etykieta lezy na samym luku (krzywa Beziera z arc3); wybieramy punkt
        # najdalej od wierzcholkow i juz postawionych etykiet.
        cx = (x1 + x2) / 2 + rad * (y2 - y1)
        cy = (y1 + y2) / 2 - rad * (x2 - x1)

        def clearance(t: float) -> float:
            px = (1 - t) ** 2 * x1 + 2 * (1 - t) * t * cx + t ** 2 * x2
            py = (1 - t) ** 2 * y1 + 2 * (1 - t) * t * cy + t ** 2 * y2
            near = [((px - qx) ** 2 + (py - qy) ** 2) ** 0.5 / 1.6 for qx, qy in positions.values()]
            near += [((px - qx) ** 2 + ((py - qy) * 2.5) ** 2) ** 0.5 for qx, qy in placed]
            return min(min(near, default=9), 1.0) - abs(t - 0.5) * 0.3

        tt = max((0.5, 0.42, 0.58, 0.34, 0.66, 0.28, 0.72), key=clearance)
        lx = (1 - tt) ** 2 * x1 + 2 * (1 - tt) * tt * cx + tt ** 2 * x2
        ly = (1 - tt) ** 2 * y1 + 2 * (1 - tt) * tt * cy + tt ** 2 * y2
        placed.append((lx, ly))
        label = str(capacity) if flows is None else f"{flow}/{capacity}"
        if (u, v) in on_path and amount is not None:
            label += f"  ({'−' if on_path[(u, v)] < 0 else '+'}{amount})"
        ax.text(lx, ly, label, ha="center", va="center", fontsize=9, color=text_color,
                fontweight="bold" if (u, v) in on_path else "normal",
                bbox={"boxstyle": "round,pad=0.18", "fc": "white", "ec": color, "lw": 0.8},
                zorder=4)

    for vertex, (x, y) in positions.items():
        terminal = vertex in (network.source, network.sink)
        ax.scatter([x], [y], s=900, color="#c9def5" if terminal else "#e6effa",
                   edgecolors="#1769aa", linewidths=2.2 if terminal else 1.3, zorder=5)
        ax.text(x, y, vertex_label(network, vertex), ha="center", va="center", fontsize=12,
                fontweight="bold" if terminal else "normal", zorder=6)
    for x in range(len(network.layers)):
        name = "Źródło" if x == 0 else ("Ujście" if x == len(network.layers) - 1 else f"Warstwa {x}")
        ax.text(x * _X_STEP, max(ys) + 0.95, name, ha="center", color="#40566b", fontsize=10)

    if flows is not None:
        handles = [Line2D([], [], color=_COLORS["empty"], lw=1.3, label="brak przepływu"),
                   Line2D([], [], color=_COLORS["flow"], lw=3, label="przepływ"),
                   Line2D([], [], color=_COLORS["saturated"], lw=3, label="łuk nasycony (f = c)")]
        if path_arcs:
            handles += [Line2D([], [], color=_COLORS["path"], lw=4, label="bieżąca ścieżka"),
                        Line2D([], [], color=_COLORS["cancel"], lw=4, ls="--", label="cofnięcie przepływu")]
        ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, 0.0),
                  ncol=len(handles), frameon=False, fontsize=9)
    ax.set_title(title or ("Sieć przepływowa: przepływ / przepustowość" if flows is not None
                           else "Losowa sieć przepływowa: przepustowości"), fontsize=13)
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.tight_layout()
    return fig


def draw_flow_network(network: FlowNetwork, out_path, flows: dict[Arc, int] | None = None) -> None:
    """Zapisuje rysunek sieci (przepustowosci albo przeplyw/przepustowosc) do pliku."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    fig = flow_network_figure(network, flows)
    fig.savefig(out_path, dpi=160, bbox_inches="tight")
    plt.close(fig)


def format_arc_list(network: FlowNetwork) -> str:
    """Luki jako tekst: jeden na wiersz `z do przepustowosc`, np. `s a 10`."""
    return "\n".join(f"{vertex_label(network, u)} {vertex_label(network, v)} {c}"
                     for (u, v), c in sorted(network.capacities.items()))


def parse_arc_list(text: str, network: FlowNetwork, max_capacity: int = 100) -> dict[Arc, int]:
    """Odczytuje luki w formacie `z do przepustowosc` (dopuszczalne tez `s -> a : 10`, `s→a 10`).

    Wierzcholki podaje sie etykietami z rysunku; zwraca nowe przepustowosci albo ValueError
    z numerem blednego wiersza.
    """
    by_label = {vertex_label(network, v): v for v in network.vertices}
    capacities: dict[Arc, int] = {}
    for line_no, line in enumerate(text.splitlines(), start=1):
        line = line.split("#", 1)[0]
        for separator in ("->", "→", ":", ",", ";"):
            line = line.replace(separator, " ")
        parts = line.split()
        if not parts:
            continue
        if len(parts) != 3:
            raise ValueError(f"Wiersz {line_no}: oczekiwano `z do przepustowość`, np. `s a 10`.")
        tail, head, raw = parts
        for name in (tail, head):
            if name not in by_label:
                raise ValueError(f"Wiersz {line_no}: nieznany wierzchołek `{name}` "
                                 f"(dostępne: {', '.join(by_label)}).")
        u, v = by_label[tail], by_label[head]
        if u == v:
            raise ValueError(f"Wiersz {line_no}: pętla {tail}→{head} jest niedozwolona.")
        if v == network.source:
            raise ValueError(f"Wiersz {line_no}: łuk nie może wchodzić do źródła s.")
        if u == network.sink:
            raise ValueError(f"Wiersz {line_no}: łuk nie może wychodzić z ujścia t.")
        if (u, v) in capacities:
            raise ValueError(f"Wiersz {line_no}: łuk {tail}→{head} występuje więcej niż raz.")
        try:
            capacity = int(raw)
        except ValueError:
            raise ValueError(f"Wiersz {line_no}: przepustowość `{raw}` musi być liczbą całkowitą.") from None
        if not 1 <= capacity <= max_capacity:
            raise ValueError(f"Wiersz {line_no}: przepustowość musi być z zakresu [1, {max_capacity}].")
        capacities[(u, v)] = capacity
    if not capacities:
        raise ValueError("Lista łuków jest pusta.")
    return capacities
