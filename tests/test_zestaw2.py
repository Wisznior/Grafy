from conftest import todo

from grafy.zestaw2 import components, degree_sequence as ds, hamilton, randomization, regular


@todo
def test_graphic_sequences_from_pdf():
    assert ds.is_graphic([4, 2, 2, 3, 2, 1, 4, 2, 2, 2, 2]) is True
    assert ds.is_graphic([4, 4, 3, 1, 2]) is False


@todo
def test_build_graph_preserves_degrees():
    seq = [4, 2, 2, 3, 2, 1, 4, 2, 2, 2, 2]
    adj = ds.build_graph(seq)
    assert sorted(len(v) for v in adj.values()) == sorted(seq)


@todo
def test_randomization_preserves_degrees():
    adj = ds.build_graph([4, 2, 2, 3, 2, 1, 4, 2, 2, 2, 2])
    new = randomization.randomize(adj, swaps=10, seed=0)
    assert {v: len(n) for v, n in adj.items()} == {v: len(n) for v, n in new.items()}


@todo
def test_largest_component():
    adj = ds.build_graph([4, 2, 2, 3, 2, 1, 4, 2, 2, 2, 2])
    assert len(components.largest_component(adj)) >= 1


@todo
def test_k_regular():
    adj = regular.random_k_regular(7, 2, seed=0)
    assert all(len(v) == 2 for v in adj.values())


@todo
def test_hamilton_triangle_and_path():
    assert hamilton.hamilton_cycle({1: [2, 3], 2: [1, 3], 3: [1, 2]}) is not None
    assert hamilton.hamilton_cycle({1: [2], 2: [1, 3], 3: [2]}) is None
