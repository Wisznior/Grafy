import math
from pathlib import Path

from grafy.cli import main
from grafy.zestaw6.pagerank import (
    pagerank_power_iteration,
    pagerank_random_walk,
    random_digraph,
    read_digraph,
    ranking,
)
from grafy.zestaw6.tsp import (
    draw_tour,
    read_points,
    simulated_annealing,
    tour_length,
    two_opt_swap,
)

ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "data" / "examples" / "zestaw6" / "pagerank_graph.txt"
POINTS = ROOT / "data" / "examples" / "zestaw6" / "tsp_points.txt"


def test_pagerank_power_iteration_matches_course_example():
    scores, iterations = pagerank_power_iteration(read_digraph(GRAPH))
    assert 1 <= iterations < 100
    assert math.isclose(sum(scores.values()), 1.0, abs_tol=1e-12)
    assert ranking(scores)[0][0] == "I"
    assert abs(scores["I"] - 0.150941) < 0.001
    assert abs(scores["H"] - 0.139879) < 0.001


def test_random_walk_pagerank_converges_to_power_result():
    graph = read_digraph(GRAPH)
    walk = pagerank_random_walk(graph, steps=250_000, seed=27)
    power, _ = pagerank_power_iteration(graph)
    assert math.isclose(sum(walk.values()), 1.0, abs_tol=1e-12)
    assert sum(abs(walk[node] - power[node]) for node in graph) < 0.035


def test_random_pagerank_graph_has_no_dangling_vertices():
    graph = random_digraph(12, p=0.0, seed=2)
    assert all(graph.values())
    scores, _ = pagerank_power_iteration(graph)
    assert math.isclose(sum(scores.values()), 1.0, abs_tol=1e-12)


def test_two_opt_is_valid_and_changes_only_route_order():
    tour = [0, 1, 2, 3, 4, 5]
    updated = two_opt_swap(tour, 1, 4)
    assert updated == [0, 1, 4, 3, 2, 5]
    assert sorted(updated) == tour


def test_simulated_annealing_improves_course_tsp_data_and_is_reproducible():
    points = read_points(POINTS)
    initial_length = tour_length(points, list(range(len(points))))
    tour, length = simulated_annealing(points, iterations=20_000, seed=21)
    second_tour, second_length = simulated_annealing(points, iterations=20_000, seed=21)
    assert len(tour) == len(points) and sorted(tour) == list(range(len(points)))
    assert length < initial_length
    assert (tour, length) == (second_tour, second_length)


def test_two_opt_delta_agrees_with_full_cycle_length():
    points = [(0, 0), (4, 0), (5, 3), (2, 5), (-1, 2)]
    tour = [0, 2, 1, 3, 4]
    updated = two_opt_swap(tour, 0, 2)
    assert tour_length(points, updated) < tour_length(points, tour)


def test_set6_cli_reports_both_page_ranks_and_tsp(tmp_path, capsys):
    image = tmp_path / "tour.png"
    main(["set6", "--walk-steps", "30000", "--iterations", "5000",
          "--seed", "8", "--draw", str(image)])
    output = capsys.readouterr().out
    assert "bledzenie losowe" in output
    assert "iteracja potegowa" in output
    assert "Dlugosc znalezionej trasy" in output
    assert image.stat().st_size > 0


def test_set5_cli_reports_max_flow_and_draws(tmp_path, capsys):
    image = tmp_path / "network.png"
    main(["set5", "--layers", "3", "--seed", "5", "--draw", str(image)])
    output = capsys.readouterr().out
    assert "Maksymalny przeplyw:" in output
    assert image.stat().st_size > 0
