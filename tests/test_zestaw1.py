import pytest
from conftest import DATA

from grafy.common import io
from grafy.common.validation import is_simple_adjacency_matrix
from grafy.zestaw1 import random_graphs as rg, representations as rep
from grafy.zestaw1.visualization import circle_layout, draw_graph_on_circle

M12 = DATA / "zestaw1" / "adjacency_matrix_12.txt"
L12 = DATA / "zestaw1" / "adjacency_list_12.txt"


def test_matrix_to_list_matches_pdf():
    assert rep.matrix_to_list(io.read_adjacency_matrix(M12)) == io.read_adjacency_list(L12)


def test_roundtrips_all_representations():
    m = io.read_adjacency_matrix(M12)
    inc = rep.matrix_to_incidence(m)
    assert len(inc) == 12 and len(inc[0]) == 18
    assert all(sum(c) == 2 for c in zip(*inc))
    assert rep.incidence_to_matrix(inc) == m
    for src, data in (("matrix", m), ("list", rep.matrix_to_list(m)), ("incidence", inc)):
        for dst in ("matrix", "list", "incidence"):
            back = rep.convert(rep.convert(data, src, dst), dst, src)
            assert rep.convert(back, src, "matrix") == m


def test_reader_rejects_loop(tmp_path):
    f = tmp_path / "bad.txt"
    f.write_text("1 1\n1 0\n")
    with pytest.raises(ValueError):
        io.read_adjacency_matrix(f)
    assert not is_simple_adjacency_matrix([[1]])


def test_gnl():
    adj = rg.gnl(7, 10, seed=1)
    assert sum(map(len, adj.values())) == 20 and all(u not in nb for u, nb in adj.items())
    assert sum(map(len, rg.gnl(5, 10).values())) == 20      # graf pelny
    with pytest.raises(ValueError):
        rg.gnl(5, 11)


def test_gnp_extremes():
    assert sum(map(len, rg.gnp(6, 0.0).values())) == 0
    assert sum(map(len, rg.gnp(6, 1.0).values())) == 30


def test_layout_and_drawing(tmp_path):
    assert circle_layout(4)[0] == (1.0, 0.0)
    out = tmp_path / "g.png"
    draw_graph_on_circle(io.read_adjacency_list(L12), str(out))
    assert out.stat().st_size > 0