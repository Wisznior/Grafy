import re

import matplotlib.pyplot as plt
import streamlit as st

from grafy.common.graph import adj_to_edges, edges_to_adj
from grafy.common.types import AdjList, Matrix
from grafy.zestaw1.random_graphs import gnl, gnp
from grafy.zestaw1.representations import (
    incidence_to_list,
    list_to_incidence,
    list_to_matrix,
    matrix_to_list,
)
from grafy.zestaw1.visualization import circle_layout
from grafy.zestaw2.components import components, largest_component
from grafy.zestaw2.degree_sequence import build_graph, is_graphic
from grafy.zestaw2.euler import euler_cycle, random_eulerian_graph
from grafy.zestaw2.hamilton import hamilton_cycle
from grafy.zestaw2.randomization import randomize
from grafy.zestaw2.regular import random_k_regular
from grafy.zestaw3.centers import center, minimax_center
from grafy.zestaw3.dijkstra import dijkstra, shortest_path
from grafy.zestaw3.distances import distance_matrix
from grafy.zestaw3.mst import minimum_spanning_tree
from grafy.zestaw3.weighted_graph import edges_to_matrix, random_connected_weighted_graph


def normalize_graph(adj: AdjList | None) -> AdjList:
    if not adj:
        return {}

    vertices = set(int(v) for v in adj)
    for neighbors in adj.values():
        vertices |= {int(u) for u in neighbors}

    if not vertices:
        return {}

    n = max(vertices)
    graph = {v: set() for v in range(1, n + 1)}

    for v, neighbors in adj.items():
        v_int = int(v)
        if v_int not in graph:
            graph[v_int] = set()
        graph[v_int].update(int(u) for u in neighbors if int(u) != v_int)

    for v in range(1, n + 1):
        for u in list(graph[v]):
            graph.setdefault(int(u), set())
            graph[int(u)].add(v)

    normalized: AdjList = {}
    for v in range(1, n + 1):
        normalized[v] = sorted(graph.get(v, set()))
    return normalized


def adj_to_text(adj: AdjList) -> str:
    adj = normalize_graph(adj)
    if not adj:
        return ""
    return "\n".join(
        f"{v}: {', '.join(map(str, adj.get(v, []))) if adj.get(v) else '-'}"
        for v in sorted(adj)
    )


def matrix_to_text(m: Matrix) -> str:
    return "\n".join(" ".join(str(x) for x in row) for row in m)


def parse_adj_list_text(raw: str) -> AdjList:
    graph: dict[int, list[int]] = {}
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        if ":" not in line:
            raise ValueError(f"Niewłaściwy format listy sąsiedztwa: '{line}'")
        left, right = [part.strip() for part in line.split(":", 1)]
        v = int(left)
        neighbors = [int(x) for x in re.split(r"[\s,]+", right) if x]
        graph[v] = neighbors

    if not graph:
        raise ValueError("Lista sąsiedztwa jest pusta.")

    vertices = set(graph)
    for neighbors in graph.values():
        vertices |= {int(u) for u in neighbors}

    normalized = {v: [] for v in sorted(vertices)}
    for v, neighbors in graph.items():
        normalized[v] = sorted(set(neighbors))
    return normalize_graph(normalized)


def parse_matrix_text(raw: str) -> Matrix:
    rows = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        row = [int(x) for x in re.split(r"[\s,]+", line) if x]
        rows.append(row)
    if not rows:
        raise ValueError("Macierz jest pusta.")
    n = len(rows)
    if any(len(row) != n for row in rows):
        raise ValueError("Macierz musi być kwadratowa.")
    return rows


def parse_incidence_text(raw: str) -> Matrix:
    return parse_matrix_text(raw)


def graph_from_representation(kind: str, raw: str) -> AdjList:
    if kind == "lista sąsiedztwa":
        return parse_adj_list_text(raw)
    if kind == "macierz sąsiedztwa":
        matrix = parse_matrix_text(raw)
        return normalize_graph(matrix_to_list(matrix))
    if kind == "macierz incydencji":
        matrix = parse_incidence_text(raw)
        return normalize_graph(incidence_to_list(matrix))
    raise ValueError("Nieznana reprezentacja")


def graph_to_list_text(graph: AdjList) -> str:
    return adj_to_text(normalize_graph(graph))


def graph_to_matrix_text(graph: AdjList) -> str:
    graph = normalize_graph(graph)
    if not graph:
        return ""
    max_vertex = max(graph)
    matrix = list_to_matrix({v: graph.get(v, []) for v in range(1, max_vertex + 1)})
    return matrix_to_text(matrix)


def graph_to_incidence_text(graph: AdjList) -> str:
    graph = normalize_graph(graph)
    if not graph:
        return ""
    max_vertex = max(graph)
    matrix = list_to_incidence({v: graph.get(v, []) for v in range(1, max_vertex + 1)})
    return matrix_to_text(matrix)


def render_graph(graph: AdjList, title: str = "Graf"):
    fig, ax = plt.subplots(figsize=(7, 7))
    graph = normalize_graph(graph)

    if not graph:
        ax.text(0.5, 0.5, "Brak grafu", ha="center", va="center", fontsize=14)
        ax.set_axis_off()
        return fig

    n = max(graph)
    layout = circle_layout(n)
    pos = {i + 1: layout[i] for i in range(n)}

    seen: set[tuple[int, int]] = set()
    for u in sorted(graph):
        for v in graph.get(u, []):
            a, b = sorted((u, v))
            if a == b:
                continue
            if (a, b) in seen or (b, a) in seen:
                continue
            seen.add((a, b))
            x1, y1 = pos[a]
            x2, y2 = pos[b]
            ax.plot([x1, x2], [y1, y2], color="#2c7be5", linewidth=2)

    for vertex, (x, y) in pos.items():
        ax.text(
            x,
            y,
            str(vertex),
            ha="center",
            va="center",
            fontsize=11,
            bbox={"boxstyle": "circle,pad=0.45", "fc": "#dfe8ff", "ec": "#2c7be5"},
        )

    ax.set_aspect("equal")
    ax.set_axis_off()
    ax.set_title(title, pad=18)
    return fig


DEFAULT_GRAPH: AdjList = {
    1: [2, 3],
    2: [1, 3, 4],
    3: [1, 2, 4, 5],
    4: [2, 3, 5],
    5: [3, 4],
}

PRESETS = {
    "Preset 1: trójkąt i gałąź": DEFAULT_GRAPH,
    "Preset 2: cykl z przekątnymi": {
        1: [2, 5, 4],
        2: [1, 3, 5],
        3: [2, 4, 6],
        4: [1, 3, 5, 6],
        5: [1, 2, 4, 6],
        6: [3, 4, 5],
    },
    "Preset 3: drzewo": {
        1: [2, 3],
        2: [1, 4, 5],
        3: [1, 6],
        4: [2],
        5: [2],
        6: [3],
    },
    "Preset 4: pełny graf K5": {
        1: [2, 3, 4, 5],
        2: [1, 3, 4, 5],
        3: [1, 2, 4, 5],
        4: [1, 2, 3, 5],
        5: [1, 2, 3, 4],
    },
}


def get_active_text(graph: AdjList, kind: str) -> str:
    graph = normalize_graph(graph)
    if kind == "lista sąsiedztwa":
        return graph_to_list_text(graph)
    if kind == "macierz sąsiedztwa":
        return graph_to_matrix_text(graph)
    if kind == "macierz incydencji":
        return graph_to_incidence_text(graph)
    return ""


def task1_section() -> None:
    st.markdown("### 1. Kodowanie grafów i konwersja")
    st.write(
        "Napisz program kodujący graf prosty za pomocą macierzy sąsiedztwa, macierzy incydencji i listy sąsiedztwa. "
        "Stwórz moduł do zmiany danego kodowania na pozostałe."
    )

    if "graph" not in st.session_state:
        st.session_state.graph = PRESETS["Preset 1: trójkąt i gałąź"]

    preset_name = st.selectbox("Preset grafu", list(PRESETS.keys()))
    if st.button("Załaduj preset"):
        st.session_state.graph = PRESETS[preset_name]

    st.subheader("Edytuj reprezentację grafu")
    source_kind = st.selectbox(
        "Reprezentacja źródłowa",
        ["lista sąsiedztwa", "macierz sąsiedztwa", "macierz incydencji"],
        key="rep_source",
    )

    st.text_area(
        "Wpisz dane grafu",
        value=get_active_text(st.session_state.graph, source_kind),
        key="rep_input",
        height=220,
    )

    if st.button("Zaktualizuj graf z tej reprezentacji"):
        try:
            graph = graph_from_representation(source_kind, st.session_state.rep_input)
            st.session_state.graph = normalize_graph(graph)
            st.success("Graf został zaktualizowany.")
        except Exception as exc:
            st.error(f"Błąd parsowania: {exc}")

    st.markdown("---")
    st.subheader("Wizualizacja grafu")
    st.pyplot(render_graph(st.session_state.graph, title="Graf prosty"))

    st.markdown("---")
    tabs = st.tabs(["Lista sąsiedztwa", "Macierz sąsiedztwa", "Macierz incydencji"])
    with tabs[0]:
        st.code(graph_to_list_text(st.session_state.graph))
    with tabs[1]:
        st.code(graph_to_matrix_text(st.session_state.graph))
    with tabs[2]:
        st.code(graph_to_incidence_text(st.session_state.graph))

    st.markdown("---")
    st.subheader("Konwersja")
    source = st.selectbox("Źródło", ["lista", "matrix", "incidence"], key="convert_source")
    target = st.selectbox("Cel", ["lista", "matrix", "incidence"], key="convert_target")

    graph = normalize_graph(st.session_state.graph)
    if source == "lista":
        data = graph
    elif source == "matrix":
        data = list_to_matrix({v: graph.get(v, []) for v in sorted(graph)})
    else:
        data = list_to_incidence({v: graph.get(v, []) for v in sorted(graph)})

    if source == "lista" and target == "matrix":
        converted = list_to_matrix(graph)
    elif source == "lista" and target == "incidence":
        converted = list_to_incidence(graph)
    elif source == "matrix" and target == "lista":
        converted = matrix_to_list(data)
    elif source == "matrix" and target == "incidence":
        converted = list_to_incidence(matrix_to_list(data))
    elif source == "incidence" and target == "lista":
        converted = incidence_to_list(data)
    elif source == "incidence" and target == "matrix":
        converted = list_to_matrix(incidence_to_list(data))
    elif source == target:
        converted = data
    else:
        converted = data

    if target == "lista":
        st.code(adj_to_text(converted))
    elif target == "matrix":
        st.code(matrix_to_text(converted))
    else:
        st.code(matrix_to_text(converted))


def task2_section() -> None:
    st.markdown("### 2. Wizualizacja grafów prostych na okręgu")
    st.write("Program do wizualizacji grafów prostych z wierzchołkami równomiernie rozmieszczonymi na okręgu.")

    preset_name = st.selectbox("Wybierz preset", list(PRESETS.keys()), key="circle_preset")
    if st.button("Załaduj preset do wizualizacji"):
        st.session_state["circle_graph"] = PRESETS[preset_name]
    if "circle_graph" not in st.session_state:
        st.session_state["circle_graph"] = DEFAULT_GRAPH

    st.pyplot(render_graph(st.session_state["circle_graph"], title="Wizualizacja na okręgu"))


def task3_section() -> None:
    st.markdown("### 3. Generowanie grafów losowych G(n, l) oraz G(n, p)")
    st.write("Tutaj można wygenerować grafy losowe z parametrami n, l lub n, p i zobaczyć ich reprezentacje.")

    model = st.radio("Model grafu", ["G(n, l)", "G(n, p)"], horizontal=True)
    n = st.number_input("n", min_value=1, max_value=30, value=8, step=1)

    if model == "G(n, l)":
        max_edges = n * (n - 1) // 2
        l = st.number_input("l", min_value=0, max_value=max_edges, value=min(10, max_edges), step=1)
        p = None
    else:
        l = None
        p = st.slider("p", min_value=0.0, max_value=1.0, value=0.4, step=0.01)

    seed = st.number_input("seed", min_value=0, max_value=100000, value=0, step=1)

    if st.button("Wygeneruj graf"):
        try:
            if model == "G(n, l)":
                graph = gnl(n, l, seed=seed)
            else:
                graph = gnp(n, float(p), seed=seed)
            st.session_state["random_graph"] = normalize_graph(graph)
            st.success("Graf został wygenerowany.")
        except Exception as exc:
            st.error(f"Błąd generowania: {exc}")

    if "random_graph" not in st.session_state:
        st.session_state["random_graph"] = normalize_graph(gnl(8, 10, seed=0))

    graph = st.session_state["random_graph"]
    st.subheader("Lista sąsiedztwa")
    st.code(adj_to_text(graph))

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Macierz sąsiedztwa")
        st.code(graph_to_matrix_text(graph))
    with col2:
        st.subheader("Macierz incydencji")
        st.code(graph_to_incidence_text(graph))

    st.subheader("Wizualizacja")
    st.pyplot(render_graph(graph, title="Graf losowy"))


def task2_set_section() -> None:
    st.markdown("### Zestaw 2 — ciągi graficzne, randomizacja, spójność, Euler, Hamilton, k-regular")

    tabs = st.tabs([
        "1. Ciąg graficzny",
        "2. Randomizacja",
        "3. Składowe",
        "4. Euler",
        "5. k-regular",
        "6. Hamilton",
    ])

    with tabs[0]:
        seq = st.text_input("Ciąg liczb (oddzielone spacjami)", value="4 2 2 3 2 1 4 2 2 2 2")
        try:
            values = [int(x) for x in seq.split() if x]
            ok = is_graphic(values)
            st.info(f"Czy ciąg jest graficzny? {'TAK' if ok else 'NIE'}")
            if ok:
                graph = build_graph(values)
                st.code(adj_to_text(graph))
                st.pyplot(render_graph(graph, title="Graf z ciągu graficznego"))
        except Exception as exc:
            st.error(f"Błąd: {exc}")

    with tabs[1]:
        if "randomize_graph" not in st.session_state:
            st.session_state["randomize_graph"] = build_graph([4, 2, 2, 3, 2, 1, 4, 2, 2, 2, 2])
        graph = st.session_state["randomize_graph"]
        swaps = st.number_input("Liczba swapów", min_value=1, max_value=500, value=50)
        seed = st.number_input("Seed", min_value=0, max_value=10_000, value=0)
        if st.button("Zrandomizuj graf"):
            st.session_state["randomize_graph"] = randomize(graph, swaps, seed=seed)
        st.code(adj_to_text(st.session_state["randomize_graph"]))
        st.pyplot(render_graph(st.session_state["randomize_graph"], title="Graf po randomizacji"))

    with tabs[2]:
        base = {
            1: [2],
            2: [1],
            3: [4, 5],
            4: [3],
            5: [3],
            6: [],
        }
        st.code(adj_to_text(base))
        comp = components(base)
        st.code(str(comp))
        st.info(f"Największa składowa: {largest_component(base)}")

    with tabs[3]:
        n = st.number_input("n", min_value=3, max_value=12, value=8)
        seed = st.number_input("seed", min_value=0, max_value=10000, value=0)
        if st.button("Wygeneruj graf Eulera"):
            graph = random_eulerian_graph(n, seed)
            st.session_state["euler_graph"] = graph
        if "euler_graph" not in st.session_state:
            st.session_state["euler_graph"] = random_eulerian_graph(8, 0)
        graph = st.session_state["euler_graph"]
        st.code(adj_to_text(graph))
        try:
            cyc = euler_cycle(graph)
            st.success(f"Cykl Eulera: {cyc}")
        except Exception as exc:
            st.error(f"Błąd: {exc}")
        st.pyplot(render_graph(graph, title="Graf Eulera"))

    with tabs[4]:
        n = st.number_input("Liczba wierzchołków n", min_value=2, max_value=20, value=8)
        k = st.number_input("Stopień k", min_value=0, max_value=10, value=2)
        seed = st.number_input("seed", min_value=0, max_value=10_000, value=0)
        if st.button("Wygeneruj graf k-regularny"):
            try:
                g = random_k_regular(n, k, seed=seed)
                st.session_state["k_regular_graph"] = g
            except Exception as exc:
                st.error(f"Błąd: {exc}")
        if "k_regular_graph" not in st.session_state:
            st.session_state["k_regular_graph"] = random_k_regular(8, 2, seed=0)
        g = st.session_state["k_regular_graph"]
        st.code(adj_to_text(g))
        st.info(f"Stopnie: {[len(v) for v in g.values()]}")
        st.pyplot(render_graph(g, title="Graf k-regularny"))

    with tabs[5]:
        graph = {
            1: [2, 3],
            2: [1, 3],
            3: [1, 2],
        }
        cyc = hamilton_cycle(graph)
        st.code(adj_to_text(graph))
        st.info(f"Czy graf jest hamiltonowski? {'TAK' if cyc else 'NIE'}")
        if cyc:
            st.success(f"Cykl Hamiltona: {cyc}")


def task3_set_section() -> None:
    st.markdown("### Zestaw 3 — graf ważony, Dijkstra, odległości, centrum, MST")

    tabs = st.tabs([
        "1. Graf ważony",
        "2. Dijkstra",
        "3. Odległości",
        "4. Centrum",
        "5. MST",
    ])

    with tabs[0]:
        n = st.number_input("n", min_value=2, max_value=30, value=12)
        p = st.slider("p", min_value=0.0, max_value=1.0, value=0.2, step=0.01)
        seed = st.number_input("seed", min_value=0, max_value=10_000, value=0)
        if st.button("Generuj graf ważony"):
            edges, matrix = random_connected_weighted_graph(n, p=p, seed=seed)
            st.session_state["weighted_edges"] = edges
            st.session_state["weighted_matrix"] = matrix
            st.session_state["weighted_adj"] = edges_to_adj(n, [(u, v) for u, v, _ in edges])
        if "weighted_edges" not in st.session_state:
            edges, matrix = random_connected_weighted_graph(12, p=0.2, seed=0)
            st.session_state["weighted_edges"] = edges
            st.session_state["weighted_matrix"] = matrix
            st.session_state["weighted_adj"] = edges_to_adj(12, [(u, v) for u, v, _ in edges])

        edges = st.session_state["weighted_edges"]
        st.code("\n".join(f"{u} {v} {w}" for u, v, w in edges))
        st.code(matrix_to_text(st.session_state["weighted_matrix"]))
        st.pyplot(render_graph(st.session_state["weighted_adj"], title="Graf ważony"))

    with tabs[1]:
        if "weighted_matrix" not in st.session_state:
            st.session_state["weighted_matrix"] = random_connected_weighted_graph(12, p=0.2, seed=0)[1]
        w = st.session_state["weighted_matrix"]
        start = st.number_input("Wierzchołek startowy (1..n)", min_value=1, max_value=len(w), value=1)
        ds, ps = dijkstra(w, start - 1)
        st.code("Dystansy: " + str(ds))
        for v in range(len(w)):
            path = shortest_path(ps, start - 1, v)
            st.code(f"d({start} -> {v + 1}) = {ds[v]}, ścieżka: {[x + 1 for x in path]}")

    with tabs[2]:
        if "weighted_matrix" not in st.session_state:
            st.session_state["weighted_matrix"] = random_connected_weighted_graph(12, p=0.2, seed=0)[1]
        w = st.session_state["weighted_matrix"]
        st.code(matrix_to_text(distance_matrix(w)))

    with tabs[3]:
        if "weighted_matrix" not in st.session_state:
            st.session_state["weighted_matrix"] = random_connected_weighted_graph(12, p=0.2, seed=0)[1]
        w = st.session_state["weighted_matrix"]
        d = distance_matrix(w)
        c, cs = center(d)
        m, mf = minimax_center(d)
        st.info(f"Centrum: {c} (suma odległości: {cs})")
        st.info(f"Centrum minimax: {m} (odległość do najdalszego: {mf})")
        st.code(matrix_to_text(d))

    with tabs[4]:
        if "weighted_edges" not in st.session_state:
            edges, _ = random_connected_weighted_graph(12, p=0.2, seed=0)
            st.session_state["weighted_edges"] = edges
        edges = st.session_state["weighted_edges"]
        n = max(max(u, v) for u, v, _ in edges)
        tree = minimum_spanning_tree(n, edges)
        st.code("\n".join(f"{u} {v} {w}" for u, v, w in tree))
        st.success(f"Suma wag MST: {sum(x for *_, x in tree)}")


def main() -> None:
    st.set_page_config(page_title="Grafy Lab", page_icon="📈", layout="wide")

    with st.sidebar:
        st.title("Nawigacja")
        st.caption("Zestaw 1 – Grafy i ich zastosowania")
        choice = st.radio(
            "Wybierz sekcję",
            [
                "Zestaw 1 • 1. Kodowanie",
                "Zestaw 1 • 2. Wizualizacja",
                "Zestaw 1 • 3. Generatory",
                "Zestaw 2 • 1-6",
                "Zestaw 3 • 1-5",
            ],
        )

    if choice == "Zestaw 1 • 1. Kodowanie":
        task1_section()
    elif choice == "Zestaw 1 • 2. Wizualizacja":
        task2_section()
    elif choice == "Zestaw 1 • 3. Generatory":
        task3_section()
    elif choice == "Zestaw 2 • 1-6":
        task2_set_section()
    else:
        task3_set_section()


if __name__ == "__main__":
    main()
