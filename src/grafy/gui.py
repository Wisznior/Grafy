import re

import matplotlib.pyplot as plt
import streamlit as st

from grafy.common.graph import edges_to_adj
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
from grafy.zestaw3.weighted_graph import random_connected_weighted_graph


# -------------------------------
# Helpers shared across all sets
# -------------------------------
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

    return {v: sorted(graph.get(v, set())) for v in range(1, n + 1)}


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


# -------------------------------
# Zestaw 1 — 3 zadania
# -------------------------------
def task1_section() -> None:
    st.markdown("### Zestaw 1 · Zadanie 1")
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
    st.subheader("Wizualizacja")
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
    else:
        converted = data

    if target == "lista":
        st.code(adj_to_text(converted))
    elif target == "matrix":
        st.code(matrix_to_text(converted))
    else:
        st.code(matrix_to_text(converted))


def task2_visualization_section() -> None:
    st.markdown("### Zestaw 1 · Zadanie 2")
    st.write("Program do wizualizacji grafów prostych z wierzchołkami równomiernie rozmieszczonymi na okręgu.")

    preset_name = st.selectbox("Wybierz preset", list(PRESETS.keys()), key="circle_preset")
    if st.button("Załaduj preset do wizualizacji"):
        st.session_state["circle_graph"] = PRESETS[preset_name]
    if "circle_graph" not in st.session_state:
        st.session_state["circle_graph"] = DEFAULT_GRAPH

    st.pyplot(render_graph(st.session_state["circle_graph"], title="Wizualizacja na okręgu"))


def task3_random_graph_section() -> None:
    st.markdown("### Zestaw 1 · Zadanie 3")
    st.write("Tutaj można wygenerować losowe grafy z parametrami n, l lub n, p i zobaczyć ich reprezentacje.")

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
                g = gnl(n, l, seed=seed)
            else:
                g = gnp(n, float(p), seed=seed)
            st.session_state["random_graph"] = normalize_graph(g)
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


def render_set1() -> None:
    st.markdown("## Zestaw 1")
    st.caption("Grafy i ich zastosowania")

    task_map = {
        1: task1_section,
        2: task2_visualization_section,
        3: task3_random_graph_section,
    }
    task_no = st.radio("Wybierz zadanie", list(task_map.keys()), horizontal=True)
    task_map[task_no]()


# -------------------------------
# Zestaw 2 — 6 zadań
# -------------------------------
def z2_task1() -> None:
    st.markdown("### Zestaw 2 · Zadanie 1")
    st.write(
        "Dla danej sekwencji liczb naturalnych sprawdź, czy jest ciągiem graficznym, a następnie zbuduj prosty graf o takich stopniach wierzchołków."
    )
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


def z2_task2() -> None:
    st.markdown("### Zestaw 2 · Zadanie 2")
    st.write(
        "Powtarzaj operację zamiany par krawędzi ab i cd na ad i bc, zachowując stopnie wierzchołków."
    )
    if "z2_rand_graph" not in st.session_state:
        st.session_state["z2_rand_graph"] = build_graph([4, 2, 2, 3, 2, 1, 4, 2, 2, 2, 2])

    graph = st.session_state["z2_rand_graph"]
    swaps = st.number_input("Liczba swapów", min_value=1, max_value=500, value=50)
    seed = st.number_input("Seed", min_value=0, max_value=10000, value=0)

    if st.button("Wykonaj randomizację"):
        st.session_state["z2_rand_graph"] = randomize(graph, swaps, seed=seed)

    st.code(adj_to_text(st.session_state["z2_rand_graph"]))
    st.pyplot(render_graph(st.session_state["z2_rand_graph"], title="Graf po randomizacji"))


def z2_task3() -> None:
    st.markdown("### Zestaw 2 · Zadanie 3")
    st.write("Znajdź największą spójną składową grafu prostego.")
    base = {
        1: [2],
        2: [1],
        3: [4, 5],
        4: [3],
        5: [3],
        6: [],
    }
    comp = components(base)
    st.code("Składowe:\n" + str(comp))
    st.info(f"Największa składowa: {largest_component(base)}")
    st.pyplot(render_graph(base, title="Graf do sprawdzania komponentów"))


def z2_task4() -> None:
    st.markdown("### Zestaw 2 · Zadanie 4")
    st.write("Wygeneruj losowy graf eulerowski i znajdź cykl Eulera.")
    n = st.number_input("n", min_value=3, max_value=12, value=8)
    seed = st.number_input("seed", min_value=0, max_value=10000, value=0)

    if st.button("Wygeneruj graf Eulera"):
        st.session_state["z2_euler_graph"] = random_eulerian_graph(n, seed)

    if "z2_euler_graph" not in st.session_state:
        st.session_state["z2_euler_graph"] = random_eulerian_graph(8, 0)

    graph = st.session_state["z2_euler_graph"]
    st.code(adj_to_text(graph))
    try:
        cyc = euler_cycle(graph)
        st.success(f"Cykl Eulera: {cyc}")
    except Exception as exc:
        st.error(f"Błąd: {exc}")
    st.pyplot(render_graph(graph, title="Graf Eulera"))


def z2_task5() -> None:
    st.markdown("### Zestaw 2 · Zadanie 5")
    st.write("Wygeneruj graf, w którym każdy wierzchołek ma dokładnie k sąsiadów.")
    n = st.number_input("Liczba wierzchołków n", min_value=2, max_value=20, value=8)
    k = st.number_input("Stopień k", min_value=0, max_value=10, value=2)
    seed = st.number_input("seed", min_value=0, max_value=10000, value=0)

    if st.button("Wygeneruj graf k-regularny"):
        try:
            st.session_state["z2_k_graph"] = random_k_regular(n, k, seed=seed)
        except Exception as exc:
            st.error(f"Błąd: {exc}")

    if "z2_k_graph" not in st.session_state:
        st.session_state["z2_k_graph"] = random_k_regular(8, 2, seed=0)

    graph = st.session_state["z2_k_graph"]
    st.code(adj_to_text(graph))
    st.info(f"Stopnie: {[len(v) for v in graph.values()]}")
    st.pyplot(render_graph(graph, title="Graf k-regularny"))


def z2_task6() -> None:
    st.markdown("### Zestaw 2 · Zadanie 6")
    st.write("Sprawdź, czy mały graf jest hamiltonowski — znajdź cykl Hamiltona lub uzyskaj odpowiedź NIE.")

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


def render_set2() -> None:
    st.markdown("## Zestaw 2")
    st.caption("Grafy i ich zastosowania")
    task_map = {
        1: z2_task1,
        2: z2_task2,
        3: z2_task3,
        4: z2_task4,
        5: z2_task5,
        6: z2_task6,
    }
    task_no = st.radio("Wybierz zadanie", list(task_map.keys()), horizontal=True)
    task_map[task_no]()


# -------------------------------
# Zestaw 3 — 5 zadań
# -------------------------------
def z3_task1() -> None:
    st.markdown("### Zestaw 3 · Zadanie 1")
    st.write("Wygeneruj spójny graf losowy i przypisz każdej krawędzi losową wagę z przedziału 1..10.")
    n = st.number_input("n", min_value=2, max_value=30, value=12)
    p = st.slider("p", min_value=0.0, max_value=1.0, value=0.2, step=0.01)
    seed = st.number_input("seed", min_value=0, max_value=10000, value=0)

    if st.button("Generuj graf ważony"):
        edges, matrix = random_connected_weighted_graph(n, p=p, seed=seed)
        st.session_state["z3_edges"] = edges
        st.session_state["z3_matrix"] = matrix
        st.session_state["z3_adj"] = edges_to_adj(n, [(u, v) for u, v, _ in edges])

    if "z3_edges" not in st.session_state:
        edges, matrix = random_connected_weighted_graph(12, p=0.2, seed=0)
        st.session_state["z3_edges"] = edges
        st.session_state["z3_matrix"] = matrix
        st.session_state["z3_adj"] = edges_to_adj(12, [(u, v) for u, v, _ in edges])

    edges = st.session_state["z3_edges"]
    matrix = st.session_state["z3_matrix"]
    st.code("\n".join(f"{u} {v} {w}" for u, v, w in edges))
    st.code(matrix_to_text(matrix))
    st.pyplot(render_graph(st.session_state["z3_adj"], title="Graf ważony"))


def z3_task2() -> None:
    st.markdown("### Zestaw 3 · Zadanie 2")
    st.write("Znajdź najkrótsze ścieżki od zadanego wierzchołka do wszystkich pozostałych.")
    if "z3_matrix" not in st.session_state:
        st.session_state["z3_matrix"] = random_connected_weighted_graph(12, p=0.2, seed=0)[1]
    w = st.session_state["z3_matrix"]
    start = st.number_input("Wierzchołek startowy (1..n)", min_value=1, max_value=len(w), value=1)
    ds, ps = dijkstra(w, start - 1)
    st.code("Dystansy: " + str(ds))
    for v in range(len(w)):
        path = shortest_path(ps, start - 1, v)
        st.code(f"d({start} -> {v + 1}) = {ds[v]}, ścieżka: {[x + 1 for x in path]}")


def z3_task3() -> None:
    st.markdown("### Zestaw 3 · Zadanie 3")
    st.write("Wyznacz macierz odległości między wszystkimi parami wierzchołków.")
    if "z3_matrix" not in st.session_state:
        st.session_state["z3_matrix"] = random_connected_weighted_graph(12, p=0.2, seed=0)[1]
    w = st.session_state["z3_matrix"]
    d = distance_matrix(w)
    st.code(matrix_to_text(d))


def z3_task4() -> None:
    st.markdown("### Zestaw 3 · Zadanie 4")
    st.write("Znajdź centrum grafu i centrum minimax.")
    if "z3_matrix" not in st.session_state:
        st.session_state["z3_matrix"] = random_connected_weighted_graph(12, p=0.2, seed=0)[1]
    w = st.session_state["z3_matrix"]
    d = distance_matrix(w)
    c, cs = center(d)
    m, mf = minimax_center(d)
    st.info(f"Centrum: {c} (suma odległości: {cs})")
    st.info(f"Centrum minimax: {m} (odległość do najdalszego: {mf})")
    st.code(matrix_to_text(d))


def z3_task5() -> None:
    st.markdown("### Zestaw 3 · Zadanie 5")
    st.write("Zastosuj algorytm Kruskala i wyznacz minimalne drzewo rozpinające.")
    if "z3_edges" not in st.session_state:
        edges, _ = random_connected_weighted_graph(12, p=0.2, seed=0)
        st.session_state["z3_edges"] = edges
    edges = st.session_state["z3_edges"]
    n = max(max(u, v) for u, v, _ in edges)
    tree = minimum_spanning_tree(n, edges)
    st.code("\n".join(f"{u} {v} {w}" for u, v, w in tree))
    st.success(f"Suma wag MST: {sum(x for *_, x in tree)}")


def render_set3() -> None:
    st.markdown("## Zestaw 3")
    st.caption("Grafy i ich zastosowania")
    task_map = {
        1: z3_task1,
        2: z3_task2,
        3: z3_task3,
        4: z3_task4,
        5: z3_task5,
    }
    task_no = st.radio("Wybierz zadanie", list(task_map.keys()), horizontal=True)
    task_map[task_no]()


# -------------------------------
# Landing page with all sets and tasks
# -------------------------------
def landing_page() -> None:
    st.markdown("# Grafy lab — wybór zestawu i zadania")
    st.write("Kliknij konkretne zadanie, aby przejść do jego treści i kalkulatora.")

    set_tasks = {
        "Zestaw 1": [
            (1, "Kodowanie grafów i konwersja"),
            (2, "Wizualizacja grafów prostych na okręgu"),
            (3, "Generowanie grafów losowych G(n, l) i G(n, p)"),
        ],
        "Zestaw 2": [
            (1, "Ciąg graficzny i budowa grafu"),
            (2, "Randomizacja grafu prostego"),
            (3, "Największa spójna składowa"),
            (4, "Graf eulerowski i cykl Eulera"),
            (5, "Graf k-regularny"),
            (6, "Hamiltonowość grafu"),
        ],
        "Zestaw 3": [
            (1, "Losowy spójny graf z wagami"),
            (2, "Algorytm Dijkstry"),
            (3, "Macierz odległości"),
            (4, "Centrum i centrum minimax"),
            (5, "Minimalne drzewo rozpinające"),
        ],
    }

    for title, tasks in set_tasks.items():
        st.markdown(f"### {title}")
        cols = st.columns(3)
        for idx, (task_no, desc) in enumerate(tasks):
            with cols[idx % 3]:
                if st.button(f"Zadanie {task_no}\n{desc}", key=f"main_{title}_{task_no}"):
                    st.session_state["selected_set"] = title
                    st.session_state["selected_task"] = task_no

    if "selected_set" in st.session_state and "selected_task" in st.session_state:
        st.markdown("---")
        st.markdown(f"## Wybrane: {st.session_state['selected_set']} · Zadanie {st.session_state['selected_task']}")

        if st.session_state["selected_set"] == "Zestaw 1":
            render_set1()
        elif st.session_state["selected_set"] == "Zestaw 2":
            render_set2()
        else:
            render_set3()


# -------------------------------
# Main app
# -------------------------------
def main() -> None:
    st.set_page_config(page_title="Grafy Lab", page_icon="📈", layout="wide")

    if "selected_set" not in st.session_state:
        st.session_state["selected_set"] = "Zestaw 1"
    if "selected_task" not in st.session_state:
        st.session_state["selected_task"] = 1

    landing_page()


if __name__ == "__main__":
    main()
