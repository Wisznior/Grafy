from conftest import DATA, read_int_matrix

from grafy.cli import main
from grafy.common.graph import edges_to_adj
from grafy.zestaw2.components import components
from grafy.zestaw3.centers import center, minimax_center
from grafy.zestaw3.dijkstra import dijkstra, shortest_path
from grafy.zestaw3.distances import distance_matrix
from grafy.zestaw3.mst import minimum_spanning_tree
from grafy.zestaw3.weighted_graph import (edges_to_matrix, random_connected_weighted_graph,
                                          read_weighted_edges)

EDGES = DATA / "zestaw3" / "weighted_edges_12.txt"
DIST = read_int_matrix(DATA / "zestaw3" / "distance_matrix_12.txt")


def test_random_weighted_graph_connected_and_in_range():
    for seed in range(10):
        edges, w = random_connected_weighted_graph(15, p=0.05, seed=seed)
        adj = edges_to_adj(15, [(u, v) for u, v, _ in edges])
        assert set(components(adj).values()) == {1}
        assert all(1 <= x <= 10 for *_, x in edges)


def test_dijkstra_from_1():
    n, edges = read_weighted_edges(EDGES)
    ds, ps = dijkstra(edges_to_matrix(n, edges), 0)
    assert ds == [0, 3, 2, 5, 7, 10, 8, 9, 12, 13, 14, 17]
    assert shortest_path(ps, 0, 5) == [0, 1, 4, 7, 5]


def test_distance_matrix_and_centers_match_pdf():
    n, edges = read_weighted_edges(EDGES)
    assert distance_matrix(edges_to_matrix(n, edges)) == DIST
    assert center(DIST) == (5, 55)
    assert minimax_center(DIST) == (8, 9)


def test_mst_weight():
    n, edges = read_weighted_edges(EDGES)
    tree = minimum_spanning_tree(n, edges)
    assert len(tree) == 11 and sum(x for *_, x in tree) == 26


def test_cli_set3_matches_expected_output(capsys, tmp_path):
    main(["set3", "--edges", str(EDGES), "--draw", str(tmp_path / "g.png")])
    out = capsys.readouterr().out
    for line in (DATA / "zestaw3" / "expected.txt").read_text().splitlines():
        if not line.startswith("MST"):
            assert line in out.splitlines()
    assert "suma wag = 26" in out and (tmp_path / "g.png").exists()