import random
import re
import tempfile
from pathlib import Path

import matplotlib.pyplot as plt
import streamlit as st

from grafy.common.graph import edges_to_adj
from grafy.common.types import AdjList, Matrix
from grafy.zestaw1.random_graphs import gnl, gnp
from grafy.zestaw1.representations import incidence_to_list, list_to_incidence, list_to_matrix, matrix_to_list
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
from grafy.zestaw5.flow_network import (FlowNetwork, example_network, flow_network_figure, format_arc_list,
                                       parse_arc_list, random_flow_network, vertex_label)
from grafy.zestaw5.max_flow import ford_fulkerson
from grafy.zestaw6.pagerank import (pagerank_power_iteration, pagerank_random_walk, random_digraph,
                                    ranking, read_digraph)
from grafy.zestaw6.tsp import read_points, simulated_annealing, tour_length

ZESTAW6_DATA = Path(__file__).resolve().parents[2] / "data" / "examples" / "zestaw6"


def normalize_graph(adj: AdjList | None) -> AdjList:
    if not adj:
        return {}
    vertices = {int(v) for v in adj}
    for neighbors in adj.values():
        vertices.update(int(u) for u in neighbors)
    n = max(vertices, default=0)
    graph = {v: set() for v in range(1, n + 1)}
    for v, neighbors in adj.items():
        v = int(v)
        graph[v].update(int(u) for u in neighbors if int(u) != v)
    for v in range(1, n + 1):
        for u in list(graph[v]):
            graph[u].add(v)
    return {v: sorted(graph[v]) for v in range(1, n + 1)}


def adj_to_text(adj: AdjList) -> str:
    graph = normalize_graph(adj)
    return "\n".join(f"{v}: {', '.join(map(str, graph[v])) if graph[v] else '-'}" for v in graph)


def matrix_to_text(matrix: Matrix) -> str:
    return "\n".join(" ".join(map(str, row)) for row in matrix)


def parse_adj_list_text(raw: str) -> AdjList:
    graph: dict[int, list[int]] = {}
    for line_no, line in enumerate(raw.splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        if ":" not in line:
            raise ValueError(f"Wiersz {line_no}: użyj formatu 'wierzchołek: sąsiedzi'.")
        left, right = line.split(":", 1)
        try:
            vertex = int(left.strip())
            neighbors = [int(x) for x in re.split(r"[\s,]+", right.strip()) if x and x != "-"]
        except ValueError as exc:
            raise ValueError(f"Wiersz {line_no}: numery wierzchołków muszą być liczbami całkowitymi.") from exc
        if vertex < 1 or vertex in graph:
            raise ValueError("Numery wierzchołków muszą być dodatnie i unikalne.")
        if vertex in neighbors or len(neighbors) != len(set(neighbors)):
            raise ValueError(f"Wierzchołek {vertex}: pętle i powtórzeni sąsiedzi są niedozwoleni.")
        graph[vertex] = neighbors
    if not graph:
        raise ValueError("Lista sąsiedztwa jest pusta.")
    n = max(graph)
    if set(graph) != set(range(1, n + 1)):
        raise ValueError("Wierzchołki muszą być ponumerowane kolejno od 1.")
    for u, neighbors in graph.items():
        for v in neighbors:
            if v not in graph or u not in graph[v]:
                raise ValueError(f"Lista musi być symetryczna: sprawdź krawędź {u}–{v}.")
    return {v: sorted(graph[v]) for v in graph}


def parse_matrix_text(raw: str, *, square: bool = True) -> Matrix:
    try:
        rows = [
            [int(x) for x in re.split(r"[\s,]+", line.strip()) if x]
            for line in raw.splitlines()
            if line.strip()
        ]
    except ValueError as exc:
        raise ValueError("Macierz może zawierać tylko liczby całkowite.") from exc
    if not rows:
        raise ValueError("Macierz jest pusta.")
    width = len(rows[0])
    if width == 0 or any(len(row) != width for row in rows):
        raise ValueError("Wszystkie wiersze macierzy muszą mieć tę samą liczbę kolumn.")
    if square and len(rows) != width:
        raise ValueError("Macierz sąsiedztwa musi być kwadratowa.")
    return rows


def graph_from_representation(kind: str, raw: str) -> AdjList:
    if kind == "lista sąsiedztwa":
        return parse_adj_list_text(raw)
    if kind == "macierz sąsiedztwa":
        matrix = parse_matrix_text(raw, square=True)
        n = len(matrix)
        if any(x not in (0, 1) for row in matrix for x in row) or any(matrix[i][i] for i in range(n)):
            raise ValueError("Macierz grafu prostego zawiera tylko 0/1 i ma zera na przekątnej.")
        if any(matrix[i][j] != matrix[j][i] for i in range(n) for j in range(n)):
            raise ValueError("Macierz sąsiedztwa musi być symetryczna.")
        return matrix_to_list(matrix)
    if kind == "macierz incydencji":
        matrix = parse_matrix_text(raw, square=False)
        if any(x not in (0, 1) for row in matrix for x in row):
            raise ValueError("Macierz incydencji grafu prostego może zawierać tylko 0 i 1.")
        if any(sum(column) != 2 for column in zip(*matrix)):
            raise ValueError("Każda kolumna macierzy incydencji musi zawierać dokładnie dwie jedynki.")
        edges = [tuple(i + 1 for i, value in enumerate(column) if value) for column in zip(*matrix)]
        if len(edges) != len(set(tuple(sorted(edge)) for edge in edges)):
            raise ValueError("Macierz incydencji zawiera powtórzoną krawędź; graf musi być prosty.")
        return incidence_to_list(matrix)
    raise ValueError("Nieznana reprezentacja.")


def graph_to_matrix_text(graph: AdjList) -> str:
    graph = normalize_graph(graph)
    return matrix_to_text(list_to_matrix(graph)) if graph else ""


def graph_to_incidence_text(graph: AdjList) -> str:
    graph = normalize_graph(graph)
    return matrix_to_text(list_to_incidence(graph)) if graph else ""


def render_graph(adj: AdjList, title: str = "Graf", edge_labels: dict | None = None, highlight_edges=None):
    graph = normalize_graph(adj)
    fig, ax = plt.subplots(figsize=(4.2, 3.8), dpi=100)
    if not graph:
        ax.text(.5, .5, "Brak grafu", ha="center", va="center", fontsize=9)
        ax.axis("off")
        return fig
    pos_list = circle_layout(len(graph), r=.82)
    pos = {i + 1: pos_list[i] for i in range(len(graph))}
    highlighted = {tuple(sorted(e)) for e in (highlight_edges or [])}
    for u, neighbors in graph.items():
        for v in neighbors:
            if u < v:
                key = (u, v)
                color = "#e63946" if key in highlighted else "#2c7be5"
                ax.plot([pos[u][0], pos[v][0]], [pos[u][1], pos[v][1]], color=color,
                        linewidth=2.3 if key in highlighted else 1.3, zorder=1)
                if edge_labels is not None:
                    ax.text((pos[u][0] + pos[v][0]) / 2, (pos[u][1] + pos[v][1]) / 2,
                            str(edge_labels.get(key, "")), fontsize=7, ha="center", va="center",
                            bbox={"fc": "white", "ec": "none", "alpha": .85, "pad": 1})
    for v, (x, y) in pos.items():
        ax.text(x, y, str(v), fontsize=8, ha="center", va="center", zorder=2,
                bbox={"boxstyle": "circle,pad=.3", "fc": "#dfe8ff", "ec": "#2c7be5", "lw": .8})
    ax.set_aspect("equal")
    ax.set_xlim(-1.08, 1.08)
    ax.set_ylim(-1.08, 1.08)
    ax.axis("off")
    ax.set_title(title, fontsize=10, pad=5)
    fig.tight_layout(pad=.25)
    return fig


def graph_editor(title: str, key: str, default_graph: AdjList) -> AdjList:
    st.subheader(title)
    graph_key, text_key = f"{key}_graph", f"{key}_text"
    if graph_key not in st.session_state:
        st.session_state[graph_key] = {v: list(nb) for v, nb in default_graph.items()}
    if text_key not in st.session_state:
        st.session_state[text_key] = adj_to_text(st.session_state[graph_key])
    st.caption("Każdy wiersz: `wierzchołek: sąsiedzi`; izolowany wierzchołek zapisz jako `v: -`.")
    st.text_area("Lista sąsiedztwa", key=text_key, height=150)
    if st.button("Zastosuj graf", key=f"{key}_apply"):
        try:
            st.session_state[graph_key] = parse_adj_list_text(st.session_state[text_key])
            st.success("Graf wejściowy zaktualizowany.")
        except ValueError as exc:
            st.error(f"Niepoprawny graf: {exc}")
    return st.session_state[graph_key]


# W Zestawie 1 dostępne są wyłącznie dwa presety kompletne i poprawne.
def complete_graph(n: int) -> AdjList:
    return {v: [u for u in range(1, n + 1) if u != v] for v in range(1, n + 1)}


PRESETS: dict[str, AdjList] = {
    "Pełny graf K5": complete_graph(5),
    "Pełny graf K6": complete_graph(6),
}


def preset_text(graph: AdjList, kind: str) -> str:
    if kind == "lista sąsiedztwa":
        return adj_to_text(graph)
    if kind == "macierz sąsiedztwa":
        return graph_to_matrix_text(graph)
    return graph_to_incidence_text(graph)


# ---------------- Zestaw 1 ----------------
def z1_task1() -> None:
    st.markdown("### 1. Kodowanie grafów i konwersja")
    st.write("Koduj graf prosty listą sąsiedztwa, macierzą sąsiedztwa i macierzą incydencji; edytuj reprezentację i konwertuj ją na pozostałe.")
    preset = st.selectbox("Preset grafu", list(PRESETS), key="z1_preset_k5_k6")
    kind = st.selectbox("Reprezentacja wejściowa", ["lista sąsiedztwa", "macierz sąsiedztwa", "macierz incydencji"], key="z1_kind")
    graph_key = "z1_graph"
    if graph_key not in st.session_state:
        st.session_state[graph_key] = PRESETS[preset]
    text_key = f"z1_input_{kind}"
    if st.button("Załaduj preset", key="z1_load_k5_k6"):
        st.session_state[graph_key] = PRESETS[preset]
        for rep in ("lista sąsiedztwa", "macierz sąsiedztwa", "macierz incydencji"):
            st.session_state[f"z1_input_{rep}"] = preset_text(PRESETS[preset], rep)
    if text_key not in st.session_state:
        st.session_state[text_key] = preset_text(st.session_state[graph_key], kind)
    st.text_area("Edytuj dane", key=text_key, height=150)
    if st.button("Zaktualizuj graf", key="z1_apply"):
        try:
            st.session_state[graph_key] = graph_from_representation(kind, st.session_state[text_key])
            for rep in ("lista sąsiedztwa", "macierz sąsiedztwa", "macierz incydencji"):
                if rep != kind:
                    st.session_state.pop(f"z1_input_{rep}", None)
            st.success("Graf zaktualizowany.")
        except ValueError as exc:
            st.error(f"Nie można wczytać reprezentacji: {exc}")
    graph = st.session_state[graph_key]
    st.pyplot(render_graph(graph, "Graf prosty"), use_container_width=False)
    tabs = st.tabs(["Lista sąsiedztwa", "Macierz sąsiedztwa", "Macierz incydencji"])
    with tabs[0]: st.code(adj_to_text(graph))
    with tabs[1]: st.code(graph_to_matrix_text(graph))
    with tabs[2]: st.code(graph_to_incidence_text(graph))


def z1_task2() -> None:
    st.markdown("### 2. Wizualizacja grafu prostego na okręgu")
    st.write("Wybierz pełny graf K5 albo K6. Wierzchołki zostaną rozmieszczone równomiernie na okręgu.")
    preset = st.selectbox("Preset grafu", list(PRESETS), key="z1_visual_preset_k5_k6")
    graph = PRESETS[preset]
    st.code(adj_to_text(graph))
    st.pyplot(render_graph(graph, f"Wizualizacja: {preset}"), use_container_width=False)


def z1_task3() -> None:
    st.markdown("### 3. Generowanie grafów losowych G(n, l) i G(n, p)")
    st.write("G(n, l) wybiera dokładnie l krawędzi. G(n, p) wybiera każdą możliwą krawędź niezależnie z prawdopodobieństwem p.")
    model = st.radio("Model", ["G(n, l)", "G(n, p)"], horizontal=True, key="z1_model")
    n = st.number_input("Liczba wierzchołków n", min_value=1, max_value=30, value=8, key="z1_n")
    if model == "G(n, l)":
        max_edges = n * (n - 1) // 2
        l = st.number_input("Liczba krawędzi l", min_value=0, max_value=max_edges, value=min(10, max_edges), key="z1_l")
    else:
        p = st.slider("Prawdopodobieństwo p", 0.0, 1.0, .4, .01, key="z1_p")
    seed = st.number_input("Seed", min_value=0, max_value=100000, value=0, key="z1_seed")
    if st.button("Generuj graf", key="z1_generate"):
        st.session_state["z1_random_graph"] = gnl(n, l, seed) if model == "G(n, l)" else gnp(n, p, seed)
    graph = st.session_state.get("z1_random_graph", gnl(8, 10, seed=0))
    st.write(f"Wierzchołki: {len(graph)} · Krawędzie: {sum(map(len, graph.values())) // 2}")
    st.code(adj_to_text(graph))
    st.pyplot(render_graph(graph, "Graf losowy"), use_container_width=False)
    with st.expander("Pozostałe reprezentacje"):
        st.subheader("Macierz sąsiedztwa")
        st.code(graph_to_matrix_text(graph))
        st.subheader("Macierz incydencji")
        st.code(graph_to_incidence_text(graph))


def render_set1(task: int) -> None:
    {1: z1_task1, 2: z1_task2, 3: z1_task3}[task]()


# ---------------- Zestaw 2 ----------------
def z2_task1() -> None:
    st.markdown("### 1. Sprawdzanie ciągu graficznego i budowa grafu")
    st.write("Podaj stopnie wierzchołków. Program sprawdzi graficzność i skonstruuje graf metodą Havla–Hakimiego.")
    raw = st.text_input("Ciąg stopni", "4 2 2 3 2 1 4 2 2 2 2", key="z2_seq")
    try:
        seq = [int(x) for x in raw.split()]
        ok = is_graphic(seq)
        st.info("Ciąg jest graficzny." if ok else "Ciąg nie jest graficzny.")
        if ok:
            graph = build_graph(seq)
            st.write("Stopnie zbudowanego grafu:", [len(graph[v]) for v in sorted(graph)])
            st.code(adj_to_text(graph))
            st.pyplot(render_graph(graph, "Graf z zadanego ciągu"), use_container_width=False)
    except ValueError as exc:
        st.error(f"Podaj nieujemne liczby całkowite: {exc}")


def z2_task2() -> None:
    st.markdown("### 2. Randomizacja grafu o zadanych stopniach")
    st.write("Podaj ciąg stopni; program zbuduje graf o tych stopniach i wykona losowe zamiany krawędzi.")
    text = st.text_input("Ciąg stopni (oddziel spacjami)", "3 3 2 2 2 2", key="z2_random_degree_sequence")
    swaps = st.number_input("Liczba prób zamiany krawędzi", 1, 5000, 50, key="z2_swaps")
    seed = st.number_input("Seed", 0, 100000, 0, key="z2_random_seed")
    try:
        degrees = [int(x) for x in text.split()]
        if not degrees or any(d < 0 for d in degrees):
            raise ValueError("Wpisz niepusty ciąg nieujemnych stopni.")
        if not is_graphic(degrees):
            st.error("Podany ciąg nie jest graficzny.")
            return
        original = build_graph(degrees)
        degree_key = tuple(degrees)
        if st.session_state.get("z2_random_result_degrees") != degree_key:
            st.session_state["z2_random_result"] = original
            st.session_state["z2_random_result_degrees"] = degree_key
        if st.button("Zbuduj i randomizuj graf", key="z2_randomize"):
            st.session_state["z2_random_result"] = randomize(original, int(swaps), seed=int(seed))
        result = st.session_state["z2_random_result"]
        left, right = st.columns(2)
        with left:
            st.subheader("Przed randomizacją")
            st.write("Stopnie:", [len(original[v]) for v in sorted(original)])
            st.code(adj_to_text(original))
            st.pyplot(render_graph(original, "Graf wyjściowy"), use_container_width=False)
        with right:
            st.subheader("Po randomizacji")
            st.write("Stopnie:", [len(result[v]) for v in sorted(result)])
            st.code(adj_to_text(result))
            st.pyplot(render_graph(result, "Graf zrandomizowany"), use_container_width=False)
        st.success("Stopnie wierzchołków zostały zachowane.")
    except ValueError as exc:
        st.error(f"Niepoprawny ciąg stopni: {exc}")


def z2_task3() -> None:
    st.markdown("### 3. Największa spójna składowa")
    st.write("Edytuj listę sąsiedztwa. Program wypisze wszystkie składowe i wyświetli największą.")
    graph = graph_editor("Edytuj graf wejściowy", "z2_components_input", {1: [2], 2: [1], 3: [4, 5], 4: [3], 5: [3], 6: []})
    labels = components(graph)
    groups: dict[int, list[int]] = {}
    for vertex, label in labels.items():
        groups.setdefault(label, []).append(vertex)
    st.subheader("Składowe spójności")
    for number, vertices in groups.items():
        st.write(f"Składowa {number}: {vertices} (rozmiar {len(vertices)})")
    biggest = largest_component(graph)
    st.success(f"Największa składowa: {biggest} — {len(biggest)} wierzchołków")
    st.pyplot(render_graph(graph, "Cały graf wejściowy"), use_container_width=False)
    subgraph = {u: [v for v in graph[u] if v in biggest] for u in biggest}
    component_edges = [(u, v) for u in biggest for v in subgraph[u] if u < v]
    st.subheader("Podgraf największej składowej")
    st.code("\n".join(f"{u}: {', '.join(map(str, subgraph[u])) or '-'}" for u in biggest))
    st.pyplot(render_graph(graph, "Największa spójna składowa (na czerwono)", highlight_edges=component_edges), use_container_width=False)


def z2_task4() -> None:
    st.markdown("### 4. Losowy graf eulerowski i cykl Eulera")
    st.write("Wygeneruj spójny graf o parzystych stopniach i znajdź cykl przechodzący przez każdą krawędź dokładnie raz.")
    n = st.number_input("Liczba wierzchołków", 3, 12, 8, key="z2_euler_n")
    seed = st.number_input("Seed", 0, 100000, 0, key="z2_euler_seed")
    if st.button("Generuj graf i cykl", key="z2_euler_generate"):
        st.session_state["z2_euler_graph"] = random_eulerian_graph(n, seed)
    graph = st.session_state.get("z2_euler_graph", random_eulerian_graph(8, 0))
    cycle = euler_cycle(graph)
    st.write("Stopnie:", [len(graph[v]) for v in sorted(graph)])
    st.success("Cykl Eulera: " + " → ".join(map(str, cycle)))
    st.code(adj_to_text(graph))
    st.pyplot(render_graph(graph, "Graf eulerowski", highlight_edges=list(zip(cycle, cycle[1:]))), use_container_width=False)


def z2_task5() -> None:
    st.markdown("### 5. Generowanie grafu k-regularnego")
    st.write("Każdy wierzchołek ma stopień k; wymagane k < n i n·k parzyste.")
    n = st.number_input("Liczba wierzchołków n", 2, 20, 8, key="z2_regular_n")
    k = st.number_input("Stopień k", 0, 19, 2, key="z2_regular_k")
    seed = st.number_input("Seed", 0, 100000, 0, key="z2_regular_seed")
    if st.button("Generuj graf k-regularny", key="z2_regular_generate"):
        try:
            st.session_state["z2_regular_graph"] = random_k_regular(n, k, seed)
        except ValueError as exc:
            st.error(str(exc))
    if "z2_regular_graph" not in st.session_state:
        st.session_state["z2_regular_graph"] = random_k_regular(8, 2, 0)
    graph = st.session_state["z2_regular_graph"]
    st.write("Stopnie:", [len(graph[v]) for v in sorted(graph)])
    st.code(adj_to_text(graph))
    st.pyplot(render_graph(graph, "Graf k-regularny"), use_container_width=False)


def z2_task6() -> None:
    st.markdown("### 6. Sprawdzanie Hamiltonowości")
    st.write("Edytuj graf prosty i sprawdź, czy istnieje cykl Hamiltona przechodzący przez każdy wierzchołek dokładnie raz.")
    graph = graph_editor("Edytuj graf wejściowy", "z2_hamilton_input", {1: [2, 3], 2: [1, 3, 4], 3: [1, 2, 4], 4: [2, 3]})
    cycle = hamilton_cycle(graph)
    if cycle:
        st.success("Graf jest hamiltonowski. Cykl: " + " → ".join(map(str, cycle)))
        st.pyplot(render_graph(graph, "Cykl Hamiltona", highlight_edges=list(zip(cycle, cycle[1:]))), use_container_width=False)
    else:
        st.warning("Graf nie jest hamiltonowski — cyklu Hamiltona nie znaleziono.")
        st.pyplot(render_graph(graph, "Graf wejściowy"), use_container_width=False)
    st.code(adj_to_text(graph))


def render_set2(task: int) -> None:
    {1: z2_task1, 2: z2_task2, 3: z2_task3, 4: z2_task4, 5: z2_task5, 6: z2_task6}[task]()


# ---------------- Zestaw 3 ----------------
def ensure_weighted_graph():
    if "z3_edges" not in st.session_state:
        edges, matrix = random_connected_weighted_graph(12, p=.2, seed=0)
        st.session_state["z3_edges"] = edges
        st.session_state["z3_matrix"] = matrix
        st.session_state["z3_adj"] = edges_to_adj(12, [(u, v) for u, v, _ in edges])
    return st.session_state["z3_edges"], st.session_state["z3_matrix"], st.session_state["z3_adj"]


def z3_task1() -> None:
    st.markdown("### 1. Spójny graf losowy z wagami")
    st.write("Generuj spójny graf losowy i przypisz każdej krawędzi wagę naturalną z zakresu 1–10.")
    n = st.number_input("Liczba wierzchołków", 2, 30, 12, key="z3_n")
    p = st.slider("Prawdopodobieństwo krawędzi p", 0.0, 1.0, .2, .01, key="z3_p")
    seed = st.number_input("Seed", 0, 100000, 0, key="z3_seed")
    if st.button("Wygeneruj", key="z3_generate"):
        edges, matrix = random_connected_weighted_graph(n, p, seed=seed)
        st.session_state["z3_edges"] = edges
        st.session_state["z3_matrix"] = matrix
        st.session_state["z3_adj"] = edges_to_adj(n, [(u, v) for u, v, _ in edges])
    edges, matrix, graph = ensure_weighted_graph()
    st.write(f"Wierzchołki: {len(matrix)} · Krawędzie: {len(edges)}")
    st.code("u  v  waga\n" + "\n".join(f"{u}  {v}  {w}" for u, v, w in edges))
    st.subheader("Macierz wag (0 oznacza brak krawędzi)")
    st.code(matrix_to_text(matrix))
    st.pyplot(render_graph(graph, "Graf ważony", {(u, v): w for u, v, w in edges}), use_container_width=False)


def z3_task2() -> None:
    st.markdown("### 2. Najkrótsze ścieżki — algorytm Dijkstry")
    st.write("Dla wybranego wierzchołka pokaż długości i przebiegi najkrótszych ścieżek do pozostałych.")
    _, weights, graph = ensure_weighted_graph()
    start = st.number_input("Wierzchołek startowy", 1, len(weights), 1, key="z3_dijkstra_start")
    distances, parents = dijkstra(weights, start - 1)
    rows = [{"Cel": v + 1, "Odległość": d, "Ścieżka": " → ".join(str(x + 1) for x in shortest_path(parents, start - 1, v))} for v, d in enumerate(distances)]
    st.dataframe(rows, use_container_width=True, hide_index=True)
    st.pyplot(render_graph(graph, f"Najkrótsze ścieżki od {start}"), use_container_width=False)


def z3_task3() -> None:
    st.markdown("### 3. Macierz odległości")
    st.write("Wyznacz najkrótsze odległości między wszystkimi parami wierzchołków.")
    _, weights, _ = ensure_weighted_graph()
    st.dataframe(distance_matrix(weights), use_container_width=True, hide_index=True)


def z3_task4() -> None:
    st.markdown("### 4. Centrum i centrum minimax")
    st.write("Centrum minimalizuje sumę odległości; centrum minimax minimalizuje maksymalną odległość.")
    _, weights, _ = ensure_weighted_graph()
    distances = distance_matrix(weights)
    c, total = center(distances)
    m, radius = minimax_center(distances)
    left, right = st.columns(2)
    left.metric("Centrum", c, f"Suma odległości: {total}")
    right.metric("Centrum minimax", m, f"Maksymalna odległość: {radius}")
    st.dataframe(distances, use_container_width=True, hide_index=True)


def z3_task5() -> None:
    st.markdown("### 5. Minimalne drzewo rozpinające")
    st.write("Zastosuj algorytm Kruskala. Krawędzie MST są zaznaczone na czerwono.")
    edges, _, graph = ensure_weighted_graph()
    tree = minimum_spanning_tree(len(graph), edges)
    highlighted = {(min(u, v), max(u, v)) for u, v, _ in tree}
    st.code("u  v  waga\n" + "\n".join(f"{u}  {v}  {w}" for u, v, w in tree))
    st.success(f"Krawędzie: {len(tree)} · Suma wag: {sum(w for _, _, w in tree)}")
    labels = {(u, v): w for u, v, w in edges}
    st.pyplot(render_graph(graph, "Minimalne drzewo rozpinające", labels, highlighted), use_container_width=False)


def render_set3(task: int) -> None:
    {1: z3_task1, 2: z3_task2, 3: z3_task3, 4: z3_task4, 5: z3_task5}[task]()


# ---------------- Zestaw 5 ----------------
Z5_SOURCES = ["Losowa sieć (N, seed)", "Przykład z treści (rys. 1)"]


def z5_persistent(key: str, default):
    """Wartości widżetów zestawu 5 przetrwają przełączanie między zadaniami 1 i 2."""
    if key not in st.session_state:
        st.session_state[key] = st.session_state.get(f"_{key}", default)


def z5_remember(*keys: str) -> None:
    for key in keys:
        st.session_state[f"_{key}"] = st.session_state[key]


def z5_network() -> tuple[FlowNetwork, bool]:
    """Wspólna sieć obu zadań: losowa albo z rys. 1, z ewentualnie zmienionymi przepustowościami."""
    z5_persistent("z5_source", Z5_SOURCES[0])
    z5_persistent("z5_layers", 3)
    z5_persistent("z5_seed", 10)
    source = st.radio("Sieć", Z5_SOURCES, horizontal=True, key="z5_source")
    if source == Z5_SOURCES[0]:
        c1, c2 = st.columns(2)
        layers = c1.number_input("Liczba warstw pośrednich N", 2, 6, key="z5_layers")
        seed = c2.number_input("Seed", 0, 100000, key="z5_seed")
        base_key = ("random", int(layers), int(seed))
        base = random_flow_network(int(layers), int(seed))
    else:
        base_key = ("example",)
        base = example_network()
    z5_remember("z5_source", "z5_layers", "z5_seed")
    if st.session_state.get("z5_base_key") != base_key:
        st.session_state["z5_base_key"] = base_key
        st.session_state["z5_caps"] = dict(base.capacities)
        st.session_state["z5_editor_version"] = st.session_state.get("z5_editor_version", 0) + 1
    network = FlowNetwork(base.layers, dict(st.session_state["z5_caps"]))
    return network, network.capacities != base.capacities


def z5_show(fig) -> None:
    st.pyplot(fig, width="stretch")
    plt.close(fig)


def z5_task1() -> None:
    st.markdown("### 1. Losowa sieć przepływowa")
    st.write("Sieć ma N warstw pośrednich (N ≥ 2), w każdej od 2 do N wierzchołków. Każdy wierzchołek ma łuk do "
             "następnej warstwy i z poprzedniej; dodatkowo 2N losowych łuków (bez łuków do źródła i z ujścia). "
             "Przepustowości losowane z [1, 10] — możesz edytować listę łuków (zmieniać przepustowości, "
             "dodawać i usuwać łuki), zadanie 2 policzy przepływ dla zmienionej sieci.")
    network, edited = z5_network()
    m1, m2, m3 = st.columns(3)
    m1.metric("Wierzchołki", len(network.vertices))
    m2.metric("Łuki", len(network.capacities))
    m3.metric("Szerokości warstw", " · ".join(str(len(layer)) for layer in network.layers))

    left, right = st.columns([1, 3])
    with left:
        st.subheader("Łuki")
        st.caption("Jeden łuk na wiersz: `z do przepustowość`, np. `s a 10`. Usuń wiersz, aby usunąć łuk; "
                   "dopisz nowy, aby go dodać.")
        text_key = f"z5_arcs_text_{st.session_state['z5_editor_version']}"
        if text_key not in st.session_state:
            st.session_state[text_key] = format_arc_list(network)
        st.text_area("Lista łuków", key=text_key, height=380, label_visibility="collapsed")
        apply, reset = st.columns(2)
        if apply.button("Zastosuj", type="primary", width="stretch"):
            try:
                st.session_state["z5_caps"] = parse_arc_list(st.session_state[text_key], network)
                st.session_state.pop(text_key)
                st.session_state["z5_message"] = "Sieć zaktualizowana."
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))
        if reset.button("Przywróć wylosowaną", disabled=not edited, width="stretch"):
            st.session_state.pop("z5_base_key", None)
            st.rerun()
        if message := st.session_state.pop("z5_message", None):
            st.success(message)
        elif edited:
            st.caption("Sieć zmieniona ręcznie.")
    with right:
        z5_show(flow_network_figure(network))


def z5_task2() -> None:
    st.markdown("### 2. Maksymalny przepływ — Ford-Fulkerson (Edmonds-Karp)")
    st.write("Ścieżki powiększające są wybierane jako najkrótsze (BFS) w sieci rezydualnej. Suwakiem przejdź "
             "przez kolejne iteracje: bieżąca ścieżka jest zielona, a łuk, po którym idziemy pod prąd "
             "(cofnięcie przepływu), pomarańczowy i przerywany.")
    network, edited = z5_network()
    if edited:
        st.info("Sieć została zmieniona ręcznie w zadaniu 1.")
    result = ford_fulkerson(network)
    label = lambda v: vertex_label(network, v)
    saturated = sum(result.flows[arc] == cap for arc, cap in network.capacities.items())
    m1, m2, m3 = st.columns(3)
    m1.metric("Maksymalny przepływ |f_max|", result.value)
    m2.metric("Ścieżki powiększające", len(result.steps))
    m3.metric("Łuki nasycone", f"{saturated} / {len(network.capacities)}")

    total = len(result.steps)
    slider_key = f"z5_step_{hash((st.session_state['z5_base_key'], tuple(sorted(network.capacities.items()))))}"
    k = st.slider("Iteracja k (0 = przepływ zerowy)", 0, total, total, key=slider_key) if total else 0
    if k == 0:
        flows, arcs, amount = {arc: 0 for arc in network.capacities}, None, None
        title = "Iteracja 0: przepływ zerowy"
    else:
        step = result.steps[k - 1]
        flows, arcs, amount = step.flows, step.arcs, step.amount
        title = f"Iteracja {k} z {total}: ścieżka {' → '.join(map(label, step.path))}, przyrost +{amount}"
        cancelled = [arc for arc, direction in step.arcs if direction < 0]
        if cancelled:
            st.warning("Cofnięcie przepływu: ścieżka przechodzi pod prąd po łuku "
                       + ", ".join(f"{label(u)}→{label(v)}" for u, v in cancelled)
                       + f", więc jego przepływ maleje o {amount}.")
    value = sum(f for (u, _), f in flows.items() if u == network.source)
    st.write(f"Wartość przepływu po iteracji {k}: **{value}**"
             + (" — to przepływ maksymalny." if k == total else ""))
    left, right = st.columns([3, 1.3])
    with left:
        z5_show(flow_network_figure(network, flows, arcs, amount, title))
    with right:
        st.subheader("Ścieżki powiększające")
        st.dataframe([{"#": i, "Ścieżka": " → ".join(map(label, s.path)), "Przyrost": f"+{s.amount}",
                       "Cofnięcie": ", ".join(f"{label(u)}→{label(v)}" for (u, v), d in s.arcs if d < 0) or "—",
                       "": "◀" if i == k else ""}
                      for i, s in enumerate(result.steps, 1)], width="stretch", hide_index=True)
        st.subheader(f"Przepływ po iteracji {k}")
        st.dataframe([{"Z": label(u), "Do": label(v), "Przepływ": flows[(u, v)], "Przepustowość": c}
                      for (u, v), c in sorted(network.capacities.items())],
                     width="stretch", hide_index=True, height=300)


def render_set5(task: int) -> None:
    {1: z5_task1, 2: z5_task2}[task]()


# ---------------- Zestaw 6 ----------------
def parse_digraph_text(raw: str):
    """Parsuje digraf `wierzcholek: sasiedzi` tym samym parserem co CLI (read_digraph)."""
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as tmp:
        tmp.write(raw)
    try:
        return read_digraph(tmp.name)
    finally:
        Path(tmp.name).unlink(missing_ok=True)


def digraph_to_text(graph) -> str:
    return "\n".join(f"{v}: {' '.join(map(str, graph[v]))}" for v in graph)


def render_digraph(graph, scores=None, title: str = "Digraf"):
    nodes = list(graph)
    fig, ax = plt.subplots(figsize=(5.2, 4.8), dpi=100)
    pos_list = circle_layout(len(nodes), r=.82)
    pos = {node: pos_list[i] for i, node in enumerate(nodes)}
    top = max(scores.values()) if scores else 1
    for u in nodes:
        for v in graph[u]:
            ax.annotate("", xy=pos[v], xytext=pos[u], zorder=1,
                        arrowprops={"arrowstyle": "-|>", "color": "#2c7be5", "lw": .9, "alpha": .7,
                                    "shrinkA": 11, "shrinkB": 11, "connectionstyle": "arc3,rad=.08"})
    for node, (x, y) in pos.items():
        share = scores[node] / top if scores else .3
        ax.text(x, y, str(node), fontsize=8, ha="center", va="center", zorder=2,
                bbox={"boxstyle": "circle,pad=.35", "fc": plt.cm.Blues(.15 + .75 * share),
                      "ec": "#1d4e89", "lw": .8},
                color="white" if share > .6 else "black")
    ax.set_aspect("equal")
    ax.set_xlim(-1.1, 1.1)
    ax.set_ylim(-1.1, 1.1)
    ax.axis("off")
    ax.set_title(title, fontsize=10, pad=5)
    fig.tight_layout(pad=.25)
    return fig


def z6_task1() -> None:
    st.markdown("### 1. PageRank — dwie metody")
    st.write("Losowy spacer z teleportacją (częstość odwiedzin) oraz iteracja rozkładu prawdopodobieństwa do zbieżności. "
             "Z prawdopodobieństwem d spacer teleportuje się do losowego wierzchołka.")
    source = st.radio("Graf", ["Przykład z zestawu 6", "Losowy digraf"], horizontal=True, key="z6_pr_source")
    if source == "Przykład z zestawu 6":
        if "z6_pr_text" not in st.session_state:
            st.session_state["z6_pr_text"] = digraph_to_text(read_digraph(ZESTAW6_DATA / "pagerank_graph.txt"))
        st.caption("Każdy wiersz: `wierzchołek: sąsiedzi` (łuki wychodzące).")
        st.text_area("Lista sąsiedztwa digrafu", key="z6_pr_text", height=200)
        try:
            graph = parse_digraph_text(st.session_state["z6_pr_text"])
        except ValueError as exc:
            st.error(f"Niepoprawny digraf: {exc}")
            return
    else:
        c1, c2, c3 = st.columns(3)
        n = c1.number_input("Liczba wierzchołków n", 2, 40, 12, key="z6_pr_n")
        p = c2.slider("Prawdopodobieństwo łuku p", 0.0, 1.0, .2, .01, key="z6_pr_p")
        gseed = c3.number_input("Seed grafu", 0, 100000, 0, key="z6_pr_gseed")
        graph = random_digraph(int(n), p, int(gseed))
        with st.expander("Lista sąsiedztwa wylosowanego digrafu"):
            st.code(digraph_to_text(graph))
    c1, c2, c3 = st.columns(3)
    damping = c1.slider("Teleportacja d", 0.0, 1.0, .15, .01, key="z6_pr_d")
    steps = c2.number_input("Kroki spaceru", 1000, 2_000_000, 200_000, 50_000, key="z6_pr_steps")
    seed = c3.number_input("Seed spaceru", 0, 100000, 10, key="z6_pr_seed")

    walk = pagerank_random_walk(graph, damping, int(steps), int(seed))
    power, iterations = pagerank_power_iteration(graph, damping)
    rows = [{"#": i, "Wierzchołek": str(node), "Losowy spacer": round(walk[node], 6),
             "Iteracja": round(score, 6), "Różnica": round(abs(walk[node] - score), 6)}
            for i, (node, score) in enumerate(ranking(power), 1)]
    m1, m2, m3 = st.columns(3)
    m1.metric("Wierzchołki", len(graph))
    m2.metric("Iteracje do zbieżności", iterations)
    m3.metric("Maks. różnica metod", f"{max(r['Różnica'] for r in rows):.6f}")
    left, right = st.columns([3, 2])
    with left:
        st.dataframe(rows, use_container_width=True, hide_index=True)
    with right:
        st.pyplot(render_digraph(graph, power, "Kolor = PageRank (iteracja)"), use_container_width=False)


def random_points(n: int, seed: int) -> list[tuple[float, float]]:
    rng = random.Random(seed)
    return [(round(rng.uniform(0, 100), 2), round(rng.uniform(0, 100), 2)) for _ in range(n)]


def render_tour(points, tour, title: str):
    ordered = [points[i] for i in tour] + [points[tour[0]]]
    fig, ax = plt.subplots(figsize=(6.4, 5), dpi=100)
    ax.plot([p[0] for p in ordered], [p[1] for p in ordered], color="#2364aa", linewidth=.9,
            marker="o", markersize=2.5)
    ax.plot(*points[tour[0]], marker="o", color="#e63946", markersize=6)
    ax.set_aspect("equal", adjustable="datalim")
    ax.set_title(title, fontsize=10)
    ax.grid(alpha=.18)
    fig.tight_layout(pad=.25)
    return fig


def z6_task2() -> None:
    st.markdown("### 2. TSP — symulowane wyżarzanie")
    st.write("Kandydat powstaje ruchem 2-opt (odwrócenie fragmentu trasy). Gorszy ruch jest akceptowany z "
             "prawdopodobieństwem exp(−Δ/T), a temperatura maleje wykładniczo. Wynik jest heurystyczny.")
    source = st.radio("Punkty", ["Przykład z zestawu 6", "Losowe punkty"], horizontal=True, key="z6_tsp_source")
    if source == "Przykład z zestawu 6":
        points = read_points(ZESTAW6_DATA / "tsp_points.txt")
    else:
        c1, c2 = st.columns(2)
        n = c1.number_input("Liczba punktów", 4, 500, 50, key="z6_tsp_n")
        pseed = c2.number_input("Seed punktów", 0, 100000, 0, key="z6_tsp_pseed")
        points = random_points(int(n), int(pseed))
    c1, c2 = st.columns(2)
    iterations = c1.number_input("Liczba prób 2-opt", 1000, 2_000_000, 200_000, 50_000, key="z6_tsp_iter")
    seed = c2.number_input("Seed wyżarzania", 0, 100000, 10, key="z6_tsp_seed")
    config = (source, tuple(points), int(iterations), int(seed))
    if st.button("Uruchom wyżarzanie", key="z6_tsp_run", type="primary"):
        with st.spinner("Wyżarzanie…"):
            # seed + 1 jak w CLI (`python -m grafy set6 --seed S`), żeby wyniki były zgodne.
            tour, length = simulated_annealing(points, int(iterations), int(seed) + 1)
        st.session_state["z6_tsp_result"] = (config, tour, length)
    start = list(range(len(points)))
    start_length = tour_length(points, start)
    result = st.session_state.get("z6_tsp_result")
    if not result or result[0] != config:
        st.info(f"{len(points)} punktów · długość trasy w kolejności z pliku: {start_length:.3f}. "
                "Kliknij „Uruchom wyżarzanie”.")
        st.pyplot(render_tour(points, start, f"Trasa początkowa, długość: {start_length:.3f}"),
                  use_container_width=False)
        return
    _, tour, length = result
    m1, m2, m3 = st.columns(3)
    m1.metric("Punkty", len(points))
    m2.metric("Długość początkowa", f"{start_length:.3f}")
    m3.metric("Znaleziona trasa", f"{length:.3f}", f"{(length - start_length) / start_length:+.1%}",
              delta_color="inverse")
    st.pyplot(render_tour(points, tour, f"Trasa TSP, długość: {length:.3f}"), use_container_width=False)
    with st.expander("Kolejność wierzchołków (indeksy od 1)"):
        st.code(" ".join(str(i + 1) for i in tour + [tour[0]]))


def render_set6(task: int) -> None:
    {1: z6_task1, 2: z6_task2}[task]()


SETS = {
    "Zestaw 1": ["1. Kodowanie grafów i konwersja", "2. Wizualizacja na okręgu", "3. Generowanie grafów losowych G(n, l), G(n, p)"],
    "Zestaw 2": ["1. Ciąg graficzny", "2. Randomizacja", "3. Największa spójna składowa", "4. Graf eulerowski i cykl Eulera", "5. Graf k-regularny", "6. Hamiltonowość"],
    "Zestaw 3": ["1. Graf ważony", "2. Algorytm Dijkstry", "3. Macierz odległości", "4. Centrum i centrum minimax", "5. Minimalne drzewo rozpinające"],
    "Zestaw 5": ["1. Losowa sieć przepływowa", "2. Maksymalny przepływ (Ford-Fulkerson)"],
    "Zestaw 6": ["1. PageRank", "2. TSP — symulowane wyżarzanie"],
}


def main() -> None:
    st.set_page_config(page_title="Grafy Lab", page_icon="📈", layout="wide")
    st.title("Grafy — zestawy i zadania")
    st.write("Wybierz zestaw, a następnie zadanie. Wyniki i wizualizacja pojawią się w widoku zadania.")
    selected_set = st.radio("Wybierz zestaw", list(SETS), horizontal=True, key="selected_set")
    tasks = SETS[selected_set]
    label = st.radio("Wybierz zadanie", tasks, key=f"task_{selected_set}")
    task = tasks.index(label) + 1
    st.markdown(f"## {selected_set} · Zadanie {task}")
    if selected_set == "Zestaw 1":
        render_set1(task)
    elif selected_set == "Zestaw 2":
        render_set2(task)
    elif selected_set == "Zestaw 3":
        render_set3(task)
    elif selected_set == "Zestaw 5":
        render_set5(task)
    else:
        render_set6(task)


if __name__ == "__main__":
    main()
