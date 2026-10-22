import streamlit as st
import matplotlib.pyplot as plt

from grafy.common.graph import adj_to_edges, edges_to_adj
from grafy.zestaw1.random_graphs import gnl, gnp
from grafy.zestaw1.representations import (
    convert,
    incidence_to_matrix,
    list_to_incidence,
    list_to_matrix,
    matrix_to_incidence,
)
from grafy.zestaw1.visualization import circle_layout
from grafy.zestaw2.components import components, largest_component
from grafy.zestaw2.degree_sequence import build_graph, is_graphic
from grafy.zestaw2.euler import euler_cycle
from grafy.zestaw2.hamilton import hamilton_cycle
from grafy.zestaw2.randomization import randomize
from grafy.zestaw2.regular import random_k_regular
from grafy.zestaw3.dijkstra import dijkstra, shortest_path
from grafy.zestaw3.weighted_graph import random_connected_weighted_graph


def simple_adj(adj):
    return {v: sorted({u for u in nb if u != v}) for v, nb in adj.items()}


def adj_to_text(adj):
    return "\n".join(
        f"{v}: {', '.join(map(str, adj[v])) if adj[v] else '-'}"
        for v in sorted(adj)
    )


def matrix_to_text(m):
    return "\n".join(" ".join(map(str, row)) for row in m)


def render_graph(adj, weights=None, title="Graf"):
    fig, ax = plt.subplots(figsize=(7, 7))
    pos = circle_layout(len(adj))
    for u in sorted(adj):
        for v in sorted(adj[u]):
            if u < v:
                (x1, y1), (x2, y2) = pos[u - 1], pos[v - 1]
                ax.plot([x1, x2], [y1, y2], color="#2c7be5", lw=2)
                if weights and (u, v) in weights:
                    ax.text((x1 + x2) / 2, (y1 + y2) / 2, str(weights[(u, v)]),
                            ha="center", va="center", fontsize=9, color="black",
                            bbox={"boxstyle": "round,pad=0.25", "fc": "white", "ec": "none"}, zorder=3)
    for i, (x, y) in enumerate(pos, start=1):
        ax.text(x, y, str(i), ha="center", va="center", fontsize=11,
                bbox={"boxstyle": "circle,pad=0.4", "fc": "#dfe8ff", "ec": "#2c7be5"})
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, pad=18)
    return fig


def ensure_graph_state():
    if "graph" not in st.session_state:
        st.session_state.graph = gnp(7, 0.45, seed=4)
    return st.session_state.graph


def regenerate_graph(kind, n, p, l, k, seq_text, seed):
    if kind == "G(n, p)":
        adj = gnp(n, p, seed)
    elif kind == "G(n, l)":
        adj = gnl(n, l, seed)
    elif kind == "ciąg graficzny":
        seq = [int(x) for x in seq_text.split() if x]
        if not seq or not is_graphic(seq):
            st.warning("Podany ciąg nie jest graficzny.")
            return None
        adj = build_graph(seq)
    elif kind == "k-regular":
        adj = random_k_regular(n, k, seed)
    else:
        adj = ensure_graph_state()
    return simple_adj(adj)


def main():
    st.set_page_config(page_title="Grafy Lab", page_icon="📈", layout="wide")
    st.title("Grafy i ich zastosowania")
    st.caption("Interaktywny wizualizator i narzędzie do testów algorytmów grafowych")

    graph = ensure_graph_state()
    with st.sidebar:
        st.header("Ustawienia grafu")
        graph_kind = st.radio("Typ grafu", ["G(n, p)", "G(n, l)", "ciąg graficzny", "k-regular"])
        n = st.number_input("Liczba wierzchołków", min_value=2, max_value=20, value=7)
        p = st.slider("p", 0.0, 1.0, 0.45, 0.01)
        l = st.number_input("l", min_value=0, max_value=30, value=10)
        k = st.number_input("k", min_value=0, max_value=10, value=2)
        seq_text = st.text_input("Ciąg graficzny", value="4 2 2 3 2 1 4 2 2 2 2")
        seed = st.number_input("Seed", min_value=0, max_value=10_000, value=4)
        if st.button("Generuj graf"):
            new_graph = regenerate_graph(graph_kind, n, p, l, k, seq_text, seed)
            if new_graph is not None:
                st.session_state.graph = new_graph
                graph = new_graph

        st.markdown("---")
        st.subheader("Edycja ręczna")
        vertices = sorted(graph)
        a = st.selectbox("Wierzchołek A", vertices)
        b = st.selectbox("Wierzchołek B", vertices)
        if a == b:
            st.info("Wybierz dwa różne wierzchołki.")
        else:
            edge_exists = b in graph.get(a, [])
            if st.button("Dodaj / usuń krawędź"):
                graph = simple_adj(graph)
                if edge_exists:
                    graph.setdefault(a, []).remove(b)
                    graph.setdefault(b, []).remove(a)
                else:
                    graph.setdefault(a, []).append(b)
                    graph.setdefault(b, []).append(a)
                graph = {v: sorted(set(nb)) for v, nb in graph.items()}
                st.session_state.graph = graph
                graph = st.session_state.graph

    st.subheader("Wizualizacja")
    fig = render_graph(graph, title="Graf prosty")
    st.pyplot(fig)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Lista sąsiedztwa")
        st.code(adj_to_text(graph))
    with col2:
        st.subheader("Macierz sąsiedztwa")
        mat = list_to_matrix({v: graph.get(v, []) for v in sorted(graph)})
        st.code(matrix_to_text(mat))

    st.subheader("Macierz incydencji")
    inc = list_to_incidence({v: graph.get(v, []) for v in sorted(graph)})
    st.code(matrix_to_text(inc))

    st.markdown("---")
    st.subheader("Analiza grafu")
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        comp = components(graph)
        groups = {}
        for v in sorted(comp):
            groups.setdefault(comp[v], []).append(v)
        st.write("Składowe:")
        st.code("\n".join(f"{k}: {v}" for k, v in groups.items()))
        st.write(f"Największa składowa: {largest_component(graph)}")

    with col_b:
        try:
            cyc = euler_cycle(graph)
            st.write("Cykl Eulera:")
            st.code(" -> ".join(map(str, cyc)))
        except ValueError:
            st.warning("Graf nie jest eulerowski.")

    with col_c:
        cyc = hamilton_cycle(graph)
        if cyc:
            st.write("Cykl Hamiltona:")
            st.code(" -> ".join(map(str, cyc)))
        else:
            st.warning("Graf nie jest hamiltonowski.")

    st.markdown("---")
    st.subheader("Graf ważony (Dijkstra)")
    n_weighted = max(graph) if graph else 1
    edges, _ = random_connected_weighted_graph(n_weighted, 0.4, seed=seed)
    weighted_map = {(u, v): w for u, v, w in edges}
    st.write("Losowe wagi krawędzi:")
    st.code("\n".join(f"{u}-{v}: {w}" for u, v, w in edges))

    start = st.selectbox("Wierzchołek startowy", options=sorted(graph), key="dijkstra_start")
    if st.button("Uruchom Dijkstra"):
        wmat = [[0] * n_weighted for _ in range(n_weighted)]
        for u, v, x in edges:
            wmat[u - 1][v - 1] = wmat[v - 1][u - 1] = x
        ds, ps = dijkstra(wmat, start - 1)
        st.code("\n".join(
            f"d({v}) = {ds[v-1]}  ścieżka: {' -> '.join(map(str, shortest_path(ps, start - 1, v - 1)))}"
            for v in range(1, n_weighted + 1)
        ))

    st.markdown("---")
    st.subheader("Konwersje reprezentacji")
    src = st.selectbox("Źródłowa reprezentacja", ["matrix", "list", "incidence"])
    if src == "matrix":
        data = mat
        out = convert(data, "matrix", "list")
        st.code(adj_to_text(out))
    elif src == "list":
        data = {v: graph.get(v, []) for v in sorted(graph)}
        out = convert(data, "list", "matrix")
        st.code(matrix_to_text(out))
    else:
        data = inc
        out = convert(data, "incidence", "list")
        st.code(adj_to_text(out))


if __name__ == "__main__":
    main()
