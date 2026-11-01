import math

import pytest

from grafy.cli import main
from grafy.zestaw4.bellman_ford import NegativeCycleError, bellman_ford
from grafy.zestaw4.directed_graph import (
    adjacency_matrix, digraph_to_edges, edges_to_digraph, gnp_digraph,
    incidence_matrix, incidence_to_digraph,
    random_strongly_connected_weighted_digraph, transpose,
)
from grafy.zestaw4.johnson import johnson
from grafy.zestaw4.scc import is_strongly_connected, strongly_connected_components


def test_digraph_representations_round_trip():
    graph = edges_to_digraph(4, [(1, 2), (2, 1), (2, 4), (4, 3)])
    assert adjacency_matrix(graph) == [
        [0, 1, 0, 0], [1, 0, 0, 1], [0, 0, 0, 0], [0, 0, 1, 0]
    ]
    assert incidence_to_digraph(incidence_matrix(graph)) == graph
    assert transpose(transpose(graph)) == graph
    assert digraph_to_edges(graph) == [(1, 2), (2, 1), (2, 4), (4, 3)]


def test_gnp_digraph_probability_extremes_and_seed():
    assert gnp_digraph(5, 0, seed=4) == {v: [] for v in range(1, 6)}
    complete = gnp_digraph(4, 1, seed=4)
    assert sum(map(len, complete.values())) == 12
    assert all(u not in neighbors for u, neighbors in complete.items())
    assert gnp_digraph(8, 0.3, seed=91) == gnp_digraph(8, 0.3, seed=91)


def test_kosaraju_components_and_singleton():
    graph = edges_to_digraph(7, [
        (1, 2), (2, 3), (3, 1), (3, 4), (4, 5), (5, 4), (5, 6), (6, 7), (7, 6)
    ])
    assert strongly_connected_components(graph) == [[1, 2, 3], [4, 5], [6, 7]]
    assert strongly_connected_components({1: []}) == [[1]]
    assert is_strongly_connected(edges_to_digraph(3, [(1, 2), (2, 3), (3, 1)]))


def test_bellman_ford_and_johnson_with_negative_edges():
    arcs = [(1, 2, 2), (1, 3, 5), (2, 3, -4), (3, 4, 3), (2, 4, 8)]
    distances, predecessors = bellman_ford(4, arcs, 1)
    assert distances == {1: 0, 2: 2, 3: -2, 4: 1}
    assert predecessors[4] == 3
    assert johnson(4, arcs) == [
        [0, 2, -2, 1], [math.inf, 0, -4, -1],
        [math.inf, math.inf, 0, 3], [math.inf, math.inf, math.inf, 0],
    ]


def test_negative_cycle_detection():
    arcs = [(1, 2, 1), (2, 3, -3), (3, 1, 1)]
    with pytest.raises(NegativeCycleError):
        bellman_ford(3, arcs, 1)
    with pytest.raises(NegativeCycleError):
        johnson(3, arcs)


def test_random_strongly_connected_weighted_digraph_invariants():
    graph, arcs = random_strongly_connected_weighted_digraph(12, p=0.1, seed=17)
    assert is_strongly_connected(graph)
    assert all(-5 <= weight <= 10 for _, _, weight in arcs)
    assert len(arcs) == sum(map(len, graph.values()))
    johnson(12, arcs)


def test_set4_cli_reports_all_results(capsys):
    main(["set4", "--n", "5", "--p", "0.2", "--source", "2", "--seed", "3"])
    output = capsys.readouterr().out
    assert "silnie spojny digraf" in output
    assert "Silnie spojne skladowe:" in output
    assert "Bellman-Ford od wierzcholka 2:" in output
    assert "Macierz odleglosci Johnsona:" in output


def test_digraph_cli_prints_three_representations(capsys):
    main(["digraph", "4", "0.5", "--seed", "8"])
    output = capsys.readouterr().out
    assert "Lista sasiedztwa:" in output
    assert "Macierz sasiedztwa:" in output
    assert "Macierz incydencji" in output
    assert "Silnie spojne skladowe:" in output
