"""Symulowane wyzarzanie TSP (ruchy 2-opt, chlodzenie kwadratowe z alg_6)."""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
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


def _random_edge_pair(rng: random.Random, n: int) -> tuple[int, int]:
    """Losuje dwie rozne, niesasiednie krawedzie cyklu: (tour[i], tour[i+1]) i (tour[j], tour[j+1])."""
    while True:
        i, j = rng.randrange(n), rng.randrange(n)
        if i > j:
            i, j = j, i
        if j - i >= 2 and not (i == 0 and j == n - 1):
            return i, j


def temperature(i: int) -> float:
    """Chlodzenie kwadratowe z alg_6: T = 0.001 * i^2 dla i = 100, 99, ..., 1 (od 10 do 0.001)."""
    return 0.001 * i * i


def simulated_annealing(points: Sequence[Point], max_it: int = 2_000,
                        seed: int | None = None, initial_tour: Sequence[int] | None = None,
                        trace: list[float] | None = None, trace_points: int = 200
                        ) -> tuple[list[int], float]:
    """Algorytm 1 z alg_6; zwraca najlepszy znaleziony cykl i jego dlugosc.

    Petla chlodzenia: i = 100..1, T = 0.001 i^2; dla kazdej temperatury `max_it` prob 2-opt.
    Krotszy cykl jest przyjmowany zawsze, dluzszy z prawdopodobienstwem exp(-delta/T).
    Jesli podano `trace`, dopisywane sa do niej dlugosci biezacego cyklu (ok. `trace_points` probek).
    """
    n = len(points)
    if n < 3 or max_it < 1:
        raise ValueError("Potrzeba co najmniej 3 punktow i MAX_IT >= 1.")
    rng = random.Random(seed)
    current = list(range(n)) if initial_tour is None else list(initial_tour)
    current_length = tour_length(points, current)
    best, best_length = current.copy(), current_length
    if trace is not None:
        trace.append(current_length)
    if n < 4:
        return best, best_length

    every = max(100 * max_it // max(trace_points, 1), 1)
    step = 0
    for i in range(100, 0, -1):
        T = temperature(i)
        for _ in range(max_it):
            first, second = _random_edge_pair(rng, n)
            a, b = current[first], current[first + 1]
            c, d = current[second], current[(second + 1) % n]
            delta = (math.dist(points[a], points[c]) + math.dist(points[b], points[d])
                     - math.dist(points[a], points[b]) - math.dist(points[c], points[d]))
            if delta < 0 or rng.random() < math.exp(-delta / T):
                current[first + 1:second + 1] = reversed(current[first + 1:second + 1])
                current_length += delta
                if current_length < best_length:
                    best, best_length = current.copy(), current_length
            step += 1
            if trace is not None and step % every == 0:
                trace.append(current_length)
    return best, tour_length(points, best)


@dataclass
class AnnealingRuns:
    tour: list[int]
    length: float
    run_lengths: list[float]
    """Dlugosc najlepszej trasy z kazdego przebiegu."""
    trace: list[float]
    """Dlugosc biezacej trasy w kolejnych probkach wszystkich przebiegow."""
    run_starts: list[int]
    """Indeksy w `trace`, od ktorych zaczyna sie kolejny przebieg."""


def simulated_annealing_runs(points: Sequence[Point], runs: int = 5, max_it: int = 2_000,
                             seed: int | None = None, initial_tour: Sequence[int] | None = None,
                             start_from_best: bool = True) -> AnnealingRuns:
    """Powtarza wyzarzanie `runs` razy i zwraca najlepszy cykl.

    Przy `start_from_best` kazdy kolejny przebieg startuje z najlepszego dotychczasowego
    cyklu, inaczej zawsze z cyklu poczatkowego.
    """
    if runs < 1:
        raise ValueError("Liczba przebiegow musi byc dodatnia.")
    rng = random.Random(seed)
    start = list(range(len(points))) if initial_tour is None else list(initial_tour)
    best, best_length = start, tour_length(points, start)
    run_lengths: list[float] = []
    trace: list[float] = []
    run_starts: list[int] = []
    for run in range(runs):
        restart = start_from_best and run > 0
        run_starts.append(len(trace))
        tour, length = simulated_annealing(points, max_it, rng.randrange(2 ** 31),
                                           best if restart else start, trace=trace)
        run_lengths.append(length)
        if length < best_length:
            best, best_length = tour, length
    return AnnealingRuns(best, best_length, run_lengths, trace, run_starts)


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
