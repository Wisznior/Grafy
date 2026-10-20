from conftest import DATA, read_int_matrix, todo

from grafy.zestaw1 import random_graphs, representations as rep

EXPECTED_LIST_12 = {
    1: [2, 5, 6], 2: [1, 3, 6], 3: [2, 4, 5, 12], 4: [3, 8, 9, 11], 5: [1, 3, 7, 9],
    6: [1, 2, 7], 7: [5, 6, 8], 8: [4, 7, 9, 12], 9: [4, 5, 8, 10], 10: [9], 11: [4], 12: [3, 8],
}


@todo
def test_matrix_to_list_example():
    m = read_int_matrix(DATA / "zestaw1" / "adjacency_matrix_12.txt")
    assert rep.matrix_to_list(m) == EXPECTED_LIST_12


@todo
def test_roundtrip_matrix_list():
    m = read_int_matrix(DATA / "zestaw1" / "adjacency_matrix_12.txt")
    assert rep.list_to_matrix(rep.matrix_to_list(m)) == m


@todo
def test_incidence_shape_and_roundtrip():
    m = read_int_matrix(DATA / "zestaw1" / "adjacency_matrix_12.txt")
    inc = rep.matrix_to_incidence(m)
    assert len(inc) == 12 and len(inc[0]) == 18          # 18 krawedzi w przykladzie
    assert all(sum(col) == 2 for col in zip(*inc))       # kazda krawedz ma 2 konce
    assert rep.incidence_to_matrix(inc) == m             # kolejnosc kolumn nie ma znaczenia


@todo
def test_gnl_edge_count_and_simple():
    adj = random_graphs.gnl(7, 10, seed=1)
    assert sum(len(v) for v in adj.values()) == 20
    assert all(u not in nb for u, nb in adj.items())     # brak petli


@todo
def test_gnp_extremes():
    assert sum(len(v) for v in random_graphs.gnp(6, 0.0).values()) == 0
    assert sum(len(v) for v in random_graphs.gnp(6, 1.0).values()) == 30
