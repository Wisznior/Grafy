"""Symulowane wyzarzanie TSP z symetrycznymi ruchami 2-opt."""
from __future__ import annotations

from collections.abc import Sequence
import math
from pathlib import Path
import random

Point = tuple[float, float]


def read_points(path) -> list[Point]:
    points = []
    for line_number, raw_line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue
        values = line.split()
        if len(values) != 2:
            raise ValueError(f"Linia {line_number}: oczekiwano dwoch wspolrzednych.")
        points.append((float(values[0]), float(values[1])))
    if len(points) < 3:
        raise ValueError("TSP wymaga co najmniej 3 punktow.")
    return points


def tour_length(points: Sequence[Point], tour: Sequence[int]) -> float:
    if len(points) != len(tour) or set(tour) != set(range(len(points))):
        raise ValueError("Trasa musi byc permutacja wszystkich punktow.")
    return sum(math.hypot(points[tour[i]][0] - points[tour[(i + 1) % len(tour)]][0],
                          points[tour[i]][1] - points[tour[(i + 1) % len(tour)]][1])
               for i in range(len(tour)))


def two_opt_swap(tour: Sequence[int], first_edge: int, second_edge: int) -> list[int]:
    """Zamienia dwie nieprzylegle krawedzie i odwraca odcinek miedzy nimi."""
    n = len(tour)
    if not (0 <= first_edge < second_edge < n):
        raise ValueError("Indeksy krawedzi musza spelniac 0 <= i < j < n.")
    if second_edge - first_edge < 2 or (first_edge == 0 and second_edge == n - 1):
        raise ValueError("Ruch 2-opt nie moze wybierac krawedzi sasiednich.")
    result = list(tour)
    result[first_edge + 1:second_edge + 1] = reversed(result[first_edge + 1:second_edge + 1])
    return result


def simulated_annealing(points: Sequence[Point], iterations: int = 200_000,
                        seed: int | None = None, initial_tour: Sequence[int] | None = None,
                        initial_temperature: float | None = None,
                        final_temperature: float | None = None
                        ) -> tuple[list[int], float]:
    """Zwraca najlepsza znaleziona trase i jej dlugosc.

    Kandydat powstaje ruchem 2-opt. Gorszy ruch jest akceptowany z
    prawdopodobienstwem exp(-delta/T), a temperatura maleje wykładniczo.
    """
    n = len(points)
    if n < 3 or iterations < 1:
        raise ValueError("Potrzeba co najmniej 3 punktow i jednej iteracji.")
    rng = random.Random(seed)
    current = list(range(n)) if initial_tour is None else list(initial_tour)
    current_length = tour_length(points, current)
    best, best_length = current.copy(), current_length
    start_temp = initial_temperature or max(current_length / n, 1.0)
    end_temp = final_temperature or start_temp * 1e-4
    if start_temp <= 0 or end_temp <= 0 or end_temp > start_temp:
        raise ValueError("Temperatury musza byc dodatnie, a koncowa nie moze przewyzszac poczatkowej.")
    if n < 4:
        return best, best_length

    for step in range(iterations):
        first = rng.randrange(n)
        choices = [edge for edge in range(n) if edge > first + 1
                   and not (first == 0 and edge == n - 1)]
        if not choices:
            first = rng.randrange(1, n - 2)
            choices = list(range(first + 2, n))
        second = rng.choice(choices)
        a, b = current[first], current[(first + 1) % n]
        c, d = current[second], current[(second + 1) % n]
        delta = (math.dist(points[a], points[c]) + math.dist(points[b], points[d])
                 - math.dist(points[a], points[b]) - math.dist(points[c], points[d]))
        fraction = step / max(iterations - 1, 1)
        temperature = start_temp * (end_temp / start_temp) ** fraction
        if delta < 0 or rng.random() < math.exp(-delta / temperature):
            current[first + 1:second + 1] = reversed(current[first + 1:second + 1])
            current_length += delta
            if current_length < best_length:
                best, best_length = current.copy(), current_length
    return best, tour_length(points, best)


def draw_tour(points: Sequence[Point], tour: Sequence[int], out_path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    ordered = [points[i] for i in tour] + [points[tour[0]]]
    fig, ax = plt.subplots(figsize=(9, 7))
    ax.plot([point[0] for point in ordered], [point[1] for point in ordered],
            color="#2364aa", linewidth=0.9, marker="o", markersize=2.5)
    ax.set_aspect("equal", adjustable="datalim")
    ax.set_title(f"Trasa TSP, dlugosc: {tour_length(points, tour):.3f}")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.grid(alpha=0.18)
    fig.savefig(out_path, dpi=160, bbox_inches="tight")
    plt.close(fig)
