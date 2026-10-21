import pytest

from grafy.common.graph import adj_to_edges
from grafy.zestaw2.components import components, largest_component
from grafy.zestaw2.degree_sequence import build_graph, is_graphic
from grafy.zestaw2.euler import euler_cycle, random_eulerian_graph
from grafy.zestaw2.hamilton import hamilton_cycle
from grafy.zestaw2.randomization import randomize
from grafy.zestaw2.regular import random_k_regular

SEQ = [4, 2, 2, 3, 2, 1, 4, 2, 2, 2, 2]


def degrees(adj):
    return [len(adj[v]) for v in sorted(adj)]


def test_graphic_sequences_from_pdf():
    assert is_graphic(SEQ)
    assert not is_graphic([4, 4, 3, 1, 2])
    assert not is_graphic([1, 1, 1])        # nieparzysta suma
    assert is_graphic([0, 0, 0])


def test_build_graph_degrees_and_simple():
    adj = build_graph(SEQ)
    assert degrees(adj) == SEQ
    assert all(u not in nb for u, nb in adj.items())


def test_randomize_keeps_degrees_and_changes_graph():
    adj = build_graph(SEQ)
    new = randomize(adj, 50, seed=0)
    assert degrees(new) == degrees(adj) and new != adj
    assert len(adj_to_edges(new)) == len(adj_to_edges(adj))


def test_components():
    adj = {1: [2], 2: [1], 3: [4, 5], 4: [3], 5: [3], 6: []}
    comp = components(adj)
    assert comp[1] == comp[2] != comp[3] == comp[4] == comp[5] != comp[6]
    assert largest_component(adj) == [3, 4, 5]


@pytest.mark.parametrize("seed", range(5))
def test_euler_cycle_uses_every_edge_once(seed):
    adj = random_eulerian_graph(8, seed)
    cyc = euler_cycle(adj)
    used = [tuple(sorted(e)) for e in zip(cyc, cyc[1:])]
    assert cyc[0] == cyc[-1]
    assert sorted(used) == adj_to_edges(adj)


def test_euler_rejects_odd_degree():
    with pytest.raises(ValueError):
        euler_cycle({1: [2], 2: [1]})


def test_k_regular():
    assert all(len(nb) == 2 for nb in random_k_regular(7, 2, seed=0).values())
    assert all(len(nb) == 3 for nb in random_k_regular(8, 3, seed=1).values())
    with pytest.raises(ValueError):
        random_k_regular(7, 3)


def test_hamilton():
    cyc = hamilton_cycle({1: [2, 3], 2: [1, 3], 3: [1, 2]})
    assert cyc[0] == cyc[-1] and sorted(cyc[:-1]) == [1, 2, 3]
    assert hamilton_cycle({1: [2], 2: [1, 3], 3: [2]}) is None
    star = {1: [2, 3, 4], 2: [1], 3: [1], 4: [1]}
    assert hamilton_cycle(star) is None