from conftest import DATA, read_int_matrix, todo

from grafy.zestaw3 import centers, dijkstra, distances, mst


def _w12():
    n, edges = 12, []
    for line in (DATA / "zestaw3" / "weighted_edges_12.txt").read_text().splitlines():
        if line.strip() and not line.startswith("#"):
            u, v, w = map(int, line.split())
            edges.append((u, v, w))
    w = [[0] * n for _ in range(n)]
    for u, v, wt in edges:
        w[u - 1][v - 1] = w[v - 1][u - 1] = wt
    return n, edges, w


@todo
def test_dijkstra_from_1():
    _, _, w = _w12()
    ds, _ = dijkstra.dijkstra(w, 0)
    assert ds == [0, 3, 2, 5, 7, 10, 8, 9, 12, 13, 14, 17]


@todo
def test_distance_matrix_matches_pdf():
    _, _, w = _w12()
    assert distances.distance_matrix(w) == read_int_matrix(DATA / "zestaw3" / "distance_matrix_12.txt")


@todo
def test_centers_match_pdf():
    d = read_int_matrix(DATA / "zestaw3" / "distance_matrix_12.txt")
    assert centers.center(d) == (5, 55)
    assert centers.minimax_center(d) == (8, 9)


@todo
def test_mst_total_weight():
    n, edges, _ = _w12()
    tree = mst.minimum_spanning_tree(n, edges)
    assert len(tree) == n - 1 and sum(w for _, _, w in tree) == 26
