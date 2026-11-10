import re

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
    """Strictly parse an undirected simple graph adjacency list (one-based vertices)."""
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
        except ValueError as exc:
            raise ValueError(f"Wiersz {line_no}: numer wierzchołka przed ':' musi być liczbą.") from exc
        if vertex < 1:
            raise ValueError("Numery wierzchołków muszą być dodatnie.")
        if vertex in graph:
            raise ValueError(f"Wierzchołek {vertex} występuje w liście więcej niż raz.")
        tokens = [x for x in re.split(r"[\s,]+", right.strip()) if x and x != "-"]
        try:
            neighbors = [int(x) for x in tokens]
        except ValueError as exc:
            raise ValueError(f"Wiersz {line_no}: sąsiedzi muszą być liczbami.") from exc
        if len(neighbors) != len(set(neighbors)):
            raise ValueError(f"Wierzchołek {vertex}: powtórzony sąsiad.")
        if vertex in neighbors:
            raise ValueError(f"Pętla przy wierzchołku {vertex} nie jest dozwolona.")
        graph[vertex] = neighbors

    if not graph:
        raise ValueError("Lista sąsiedztwa jest pusta.")
    n = max(graph)
    if set(graph) != set(range(1, n + 1)):
        raise ValueError("Wierzchołki muszą być ponumerowane kolejno od 1 (bez brakujących numerów).")
    for u, neighbors in graph.items():
        for v in neighbors:
            if v not in graph:
                raise ValueError(f"Sąsiad {v} nie ma własnego wiersza w liście.")
            if u not in graph[v]:
                raise ValueError(f"Lista nie jest symetryczna: {u} ma sąsiada {v}, ale {v} nie ma sąsiada {u}.")
    return {v: sorted(graph[v]) for v in range(1, n + 1)}


def parse_matrix_text(raw: str) -> Matrix:
    rows = [[int(x) for x in re.split(r"[\s,]+", line.strip()) if x]
            for line in raw.splitlines() if line.strip()]
    if not rows or any(len(row) != len(rows) for row in rows):
        raise ValueError("Macierz musi być niepusta i kwadratowa.")
    return rows


def graph_from_representation(kind: str, raw: str) -> AdjList:
    if kind == "lista sąsiedztwa":
        return parse_adj_list_text(raw)
    if kind == "macierz sąsiedztwa":
        matrix = parse_matrix_text(raw)
        if any(x not in (0, 1) for row in matrix for x in row):
            raise ValueError("Macierz sąsiedztwa grafu prostego zawiera tylko 0 i 1.")
        if any(matrix[i][i] for i in range(len(matrix))) or any(matrix[i][j] != matrix[j][i] for i in range(len(matrix)) for j in range(len(matrix))):
            raise ValueError("Macierz musi być symetryczna i mieć zera na przekątnej.")
        return matrix_to_list(matrix)
    if kind == "macierz incydencji":
        matrix = parse_matrix_text(raw)
        if any(sum(col) != 2 for col in zip(*matrix)):
            raise ValueError("Każda kolumna macierzy incydencji musi zawierać dokładnie dwie jedynki.")
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
    fig, ax = plt.subplots(figsize=(7, 6))
    if not graph:
        ax.text(.5, .5, "Brak grafu", ha="center", va="center")
        ax.set_axis_off()
        return fig
    pos_list = circle_layout(len(graph))
    pos = {i + 1: pos_list[i] for i in range(len(graph))}
    highlighted = {tuple(sorted(e)) for e in (highlight_edges or [])}
    for u, neighbors in graph.items():
        for v in neighbors:
            if u < v:
                key = (u, v)
                color = "#e63946" if key in highlighted else "#2c7be5"
                ax.plot([pos[u][0], pos[v][0]], [pos[u][1], pos[v][1]], color=color,
                        linewidth=3 if key in highlighted else 1.8, zorder=1)
                if edge_labels is not None:
                    ax.text((pos[u][0] + pos[v][0]) / 2, (pos[u][1] + pos[v][1]) / 2,
                            str(edge_labels.get(key, "")), ha="center", va="center",
                            bbox={"fc": "white", "ec": "none", "alpha": .8})
    for v, (x, y) in pos.items():
        ax.text(x, y, str(v), ha="center", va="center", zorder=2,
                bbox={"boxstyle": "circle,pad=.4", "fc": "#dfe8ff", "ec": "#2c7be5"})
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title)
    return fig


def graph_editor(title: str, key: str, default_graph: AdjList) -> AdjList | None:
    """Text editor and strict apply action for tasks whose input is an adjacency list."""
    st.subheader(title)
    text_key = f"{key}_text"
    graph_key = f"{key}_graph"
    if graph_key not in st.session_state:
        st.session_state[graph_key] = {v: list(nb) for v, nb in default_graph.items()}
    if text_key not in st.session_state:
        st.session_state[text_key] = adj_to_text(st.session_state[graph_key])
    st.caption("Edytuj listę sąsiedztwa. Każdy wiersz: `wierzchołek: sąsiedzi`; dla izolowanego wierzchołka wpisz `v: -`.")
    st.text_area("Lista sąsiedztwa", key=text_key, height=190)
    if st.button("Zastosuj graf", key=f"{key}_apply"):
        try:
            st.session_state[graph_key] = parse_adj_list_text(st.session_state[text_key])
            st.success("Graf wejściowy zaktualizowany.")
        except ValueError as exc:
            st.error(f"Niepoprawny graf: {exc}")
    return st.session_state[graph_key]


DEFAULT_GRAPH: AdjList = {1: [2, 3], 2: [1, 3, 4], 3: [1, 2, 4, 5], 4: [2, 3, 5], 5: [3, 4]}
PRESETS = {
    "Trójkąt i gałąź": DEFAULT_GRAPH,
    "Cykl z przekątnymi": {1: [2, 4, 5], 2: [1, 3, 5], 3: [2, 4, 6], 4: [1, 3, 5, 6], 5: [1, 2, 4, 6], 6: [3, 4, 5]},
    "Drzewo": {1: [2, 3], 2: [1, 4, 5], 3: [1, 6], 4: [2], 5: [2], 6: [3]},
    "Pełny graf K5": {1: [2, 3, 4, 5], 2: [1, 3, 4, 5], 3: [1, 2, 4, 5], 4: [1, 2, 3, 5], 5: [1, 2, 3, 4]},
}

# ---------------- Zestaw 1 ----------------
def z1_task1() -> None:
    st.markdown("### 1. Kodowanie grafów i konwersja")
    st.write("Koduj graf prosty listą sąsiedztwa, macierzą sąsiedztwa i macierzą incydencji; edytuj reprezentację i konwertuj ją na pozostałe.")
    preset = st.selectbox("Preset grafu", list(PRESETS), key="z1_preset")
    if "z1_graph" not in st.session_state:
        st.session_state["z1_graph"] = DEFAULT_GRAPH
    if st.button("Załaduj preset", key="z1_load"):
        st.session_state["z1_graph"] = PRESETS[preset]
        st.session_state.pop("z1_input", None)
    kind = st.selectbox("Reprezentacja wejściowa", ["lista sąsiedztwa", "macierz sąsiedztwa", "macierz incydencji"], key="z1_kind")
    text_key = "z1_input"
    if text_key not in st.session_state:
        g = st.session_state["z1_graph"]
        st.session_state[text_key] = (adj_to_text(g) if kind == "lista sąsiedztwa" else
                                     graph_to_matrix_text(g) if kind == "macierz sąsiedztwa" else graph_to_incidence_text(g))
    st.text_area("Edytuj dane", key=text_key, height=180)
    if st.button("Zaktualizuj graf", key="z1_apply"):
        try:
            st.session_state["z1_graph"] = graph_from_representation(kind, st.session_state[text_key])
            st.success("Graf zaktualizowany.")
        except ValueError as exc:
            st.error(str(exc))
    g = st.session_state["z1_graph"]
    st.pyplot(render_graph(g, "Graf prosty"))
    tabs = st.tabs(["Lista", "Macierz sąsiedztwa", "Macierz incydencji"])
    with tabs[0]: st.code(adj_to_text(g))
    with tabs[1]: st.code(graph_to_matrix_text(g))
    with tabs[2]: st.code(graph_to_incidence_text(g))


def z1_task2() -> None:
    st.markdown("### 2. Wizualizacja grafu na okręgu")
    st.write("Wybierz graf i zobacz jego wizualizację z wierzchołkami rozmieszczonymi równomiernie na okręgu.")
    preset = st.selectbox("Wybierz preset", list(PRESETS), key="z1_visual_preset")
    if st.button("Pokaż graf", key="z1_visual_show"):
        st.session_state["z1_visual_graph"] = PRESETS[preset]
    graph = st.session_state.get("z1_visual_graph", DEFAULT_GRAPH)
    st.code(adj_to_text(graph))
    st.pyplot(render_graph(graph, "Wizualizacja na okręgu"))


def z1_task3() -> None:
    st.markdown("### 3. Generowanie grafów losowych G(n, l) i G(n, p)")
    st.write("Generuj graf o n wierzchołkach z dokładnie l krawędziami albo z prawdopodobieństwem p dla każdej krawędzi.")
    model = st.radio("Model", ["G(n, l)", "G(n, p)"], horizontal=True, key="z1_model")
    n = st.number_input("Liczba wierzchołków n", min_value=1, max_value=30, value=8, key="z1_n")
    if model == "G(n, l)":
        max_l = n * (n - 1) // 2
        l = st.number_input("Liczba krawędzi l", min_value=0, max_value=max_l, value=min(10, max_l), key="z1_l")
    else:
        p = st.slider("Prawdopodobieństwo p", 0.0, 1.0, 0.4, 0.01, key="z1_p")
    seed = st.number_input("Seed", min_value=0, max_value=100000, value=0, key="z1_seed")
    if st.button("Generuj", key="z1_generate"):
        g = gnl(n, l, seed) if model == "G(n, l)" else gnp(n, p, seed)
        st.session_state["z1_random_graph"] = g
    g = st.session_state.get("z1_random_graph", gnl(8, 10, seed=0))
    st.code(adj_to_text(g))
    st.pyplot(render_graph(g, "Graf losowy"))
    with st.expander("Reprezentacje"):
        st.code("Macierz sąsiedztwa:\n" + graph_to_matrix_text(g) + "\n\nMacierz incydencji:\n" + graph_to_incidence_text(g))


def render_set1(task: int) -> None:
    [z1_task1, z1_task2, z1_task3][task - 1]()

# ---------------- Zestaw 2 ----------------
def z2_task1() -> None:
    st.markdown("### 1. Sprawdzanie ciągu graficznego i budowa grafu")
    st.write("Podaj stopnie wierzchołków. Program sprawdzi warunki graficzności i skonstruuje graf prosty metodą Havla–Hakimiego.")
    raw = st.text_input("Ciąg stopni", "4 2 2 3 2 1 4 2 2 2 2", key="z2_seq")
    try:
        seq = [int(x) for x in raw.split()]
        st.info("Ciąg jest graficzny." if is_graphic(seq) else "Ciąg nie jest graficzny.")
        if is_graphic(seq):
            g = build_graph(seq)
            st.write("Stopnie zbudowanego grafu:", [len(g[v]) for v in sorted(g)])
            st.code(adj_to_text(g))
            st.pyplot(render_graph(g, "Graf z zadanego ciągu"))
    except ValueError as exc:
        st.error(f"Podaj nieujemne liczby całkowite: {exc}")


def z2_task2() -> None:
    st.markdown("### 2. Randomizacja grafu o zadanych stopniach")
    st.write("Wybierz graf, a następnie wykonaj próby zamiany krawędzi ab, cd na ad, bc. Stopnie pozostają zachowane.")
    default = build_graph([4, 2, 2, 3, 2, 1, 4, 2, 2, 2, 2])
    g = graph_editor("Graf wejściowy", "z2_random_input", default)
    swaps = st.number_input("Liczba zaakceptowanych zamian", 1, 500, 50, key="z2_swaps")
    seed = st.number_input("Seed", 0, 100000, 0, key="z2_random_seed")
    if st.button("Randomizuj", key="z2_randomize"):
        st.session_state["z2_random_result"] = randomize(g, swaps, seed)
    result = st.session_state.get("z2_random_result", g)
    st.write("Stopnie przed:", [len(g[v]) for v in sorted(g)])
    st.write("Stopnie po:", [len(result[v]) for v in sorted(result)])
    st.code(adj_to_text(result))
    st.pyplot(render_graph(result, "Graf po randomizacji"))


def z2_task3() -> None:
    st.markdown("### 3. Największa spójna składowa")
    st.write("Wprowadź graf prosty jako listę sąsiedztwa. Program wypisze wszystkie składowe, ich rozmiary i wyświetli największą.")
    default = {1: [2], 2: [1], 3: [4, 5], 4: [3], 5: [3], 6: []}
    graph = graph_editor("Graf wejściowy", "z2_components_input", default)
    comp = components(graph)
    groups: dict[int, list[int]] = {}
    for vertex, component in comp.items():
        groups.setdefault(component, []).append(vertex)
    st.subheader("Składowe spójności")
    for number, vertices in groups.items():
        st.write(f"Składowa {number}: " + ", ".join(map(str, vertices)) + f" (rozmiar {len(vertices)})")
    biggest = largest_component(graph)
    st.success(f"Największa składowa: {{{', '.join(map(str, biggest))}}} — {len(biggest)} wierzchołków")
    st.pyplot(render_graph(graph, "Graf wejściowy — największa składowa na czerwono", highlight_edges=[(u, v) for u in biggest for v in graph[u] if u < v]))
    subgraph = {u: [v for v in graph[u] if v in biggest] for u in biggest}
    st.subheader("Podgraf największej składowej")
    st.code(adj_to_text(subgraph))
    st.pyplot(render_graph(subgraph, "Największa spójna składowa"))


def z2_task4() -> None:
    st.markdown("### 4. Losowy graf eulerowski i cykl Eulera")
    st.write("Wygeneruj spójny graf o parzystych stopniach i znajdź cykl przechodzący przez każdą krawędź dokładnie raz.")
    n = st.number_input("Liczba wierzchołków", 3, 12, 8, key="z2_euler_n")
    seed = st.number_input("Seed", 0, 100000, 0, key="z2_euler_seed")
    if st.button("Generuj graf i cykl", key="z2_euler_generate"):
        st.session_state["z2_euler_graph"] = random_eulerian_graph(n, seed)
    g = st.session_state.get("z2_euler_graph", random_eulerian_graph(8, 0))
    cycle = euler_cycle(g)
    st.write("Stopnie:", [len(g[v]) for v in sorted(g)])
    st.success("Cykl Eulera: " + " → ".join(map(str, cycle)))
    st.code(adj_to_text(g))
    st.pyplot(render_graph(g, "Graf eulerowski", highlight_edges=list(zip(cycle, cycle[1:]))))


def z2_task5() -> None:
    st.markdown("### 5. Generowanie grafu k-regularnego")
    st.write("Wygeneruj prosty graf, w którym każdy wierzchołek ma stopień k. Warunki: k < n oraz n·k jest parzyste.")
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
    g = st.session_state["z2_regular_graph"]
    st.write("Stopnie:", [len(g[v]) for v in sorted(g)])
    st.code(adj_to_text(g))
    st.pyplot(render_graph(g, "Graf k-regularny"))


def z2_task6() -> None:
    st.markdown("### 6. Sprawdzanie Hamiltonowości")
    st.write("Edytuj graf prosty. Program sprawdzi, czy istnieje cykl Hamiltona przechodzący przez każdy wierzchołek dokładnie raz.")
    default = {1: [2, 3], 2: [1, 3, 4], 3: [1, 2, 4], 4: [2, 3]}
    graph = graph_editor("Graf wejściowy", "z2_hamilton_input", default)
    cycle = hamilton_cycle(graph)
    if cycle:
        st.success("Graf jest hamiltonowski. Cykl: " + " → ".join(map(str, cycle)))
        st.pyplot(render_graph(graph, "Znaleziony cykl Hamiltona", highlight_edges=list(zip(cycle, cycle[1:]))))
    else:
        st.warning("Graf nie jest hamiltonowski — cyklu Hamiltona nie znaleziono.")
        st.pyplot(render_graph(graph, "Graf wejściowy"))
    st.subheader("Lista sąsiedztwa grafu")
    st.code(adj_to_text(graph))


def render_set2(task: int) -> None:
    tasks = {1: z2_task1, 2: z2_task2, 3: z2_task3, 4: z2_task4, 5: z2_task5, 6: z2_task6}
    tasks[task]()

# ---------------- Zestaw 3 ----------------
def ensure_weighted_graph() -> tuple[list[tuple[int, int, int]], Matrix, AdjList]:
    if "z3_edges" not in st.session_state:
        edges, matrix = random_connected_weighted_graph(12, p=.2, seed=0)
        st.session_state["z3_edges"] = edges
        st.session_state["z3_matrix"] = matrix
        st.session_state["z3_adj"] = edges_to_adj(12, [(u, v) for u, v, _ in edges])
    return st.session_state["z3_edges"], st.session_state["z3_matrix"], st.session_state["z3_adj"]


def z3_task1() -> None:
    st.markdown("### 1. Spójny graf losowy z wagami")
    st.write("Generuj spójny graf losowy i przypisz każdej krawędzi naturalną wagę z zakresu 1–10.")
    n = st.number_input("Liczba wierzchołków", 2, 30, 12, key="z3_n")
    p = st.slider("Prawdopodobieństwo krawędzi p", 0.0, 1.0, .2, .01, key="z3_p")
    seed = st.number_input("Seed", 0, 100000, 0, key="z3_seed")
    if st.button("Wygeneruj", key="z3_generate"):
        edges, matrix = random_connected_weighted_graph(n, p, seed=seed)
        st.session_state["z3_edges"] = edges
        st.session_state["z3_matrix"] = matrix
        st.session_state["z3_adj"] = edges_to_adj(n, [(u, v) for u, v, _ in edges])
    edges, matrix, graph = ensure_weighted_graph()
    st.write(f"Liczba wierzchołków: {len(matrix)}, liczba krawędzi: {len(edges)}")
    st.code("u  v  waga\n" + "\n".join(f"{u}  {v}  {w}" for u, v, w in edges))
    st.subheader("Macierz wag (0 oznacza brak krawędzi)")
    st.code(matrix_to_text(matrix))
    labels = {(u, v): weight for u, v, weight in edges}
    st.pyplot(render_graph(graph, "Graf ważony", edge_labels=labels))


def z3_task2() -> None:
    st.markdown("### 2. Najkrótsze ścieżki — algorytm Dijkstry")
    st.write("Wybierz wierzchołek początkowy. Dla każdego wierzchołka zobaczysz długość najkrótszej ścieżki i jej przebieg.")
    _, w, graph = ensure_weighted_graph()
    start = st.number_input("Wierzchołek startowy", 1, len(w), 1, key="z3_dijkstra_start")
    ds, parents = dijkstra(w, start - 1)
    rows = []
    for v, distance in enumerate(ds):
        path = shortest_path(parents, start - 1, v)
        rows.append({"Cel": v + 1, "Odległość": distance, "Najkrótsza ścieżka": " → ".join(str(x + 1) for x in path) if path else "brak"})
    st.dataframe(rows, use_container_width=True, hide_index=True)
    st.pyplot(render_graph(graph, f"Najkrótsze ścieżki od {start}"))


def z3_task3() -> None:
    st.markdown("### 3. Macierz odległości")
    st.write("Wyznacz najkrótszą odległość między każdą parą wierzchołków grafu ważonego.")
    _, w, _ = ensure_weighted_graph()
    distances = distance_matrix(w)
    st.dataframe(distances, use_container_width=True, hide_index=True)
    st.caption("Wiersz i kolumna odpowiadają numerom wierzchołków; wartości są sumami wag najkrótszych ścieżek.")


def z3_task4() -> None:
    st.markdown("### 4. Centrum i centrum minimax")
    st.write("Centrum minimalizuje sumę odległości do wszystkich pozostałych wierzchołków. Centrum minimax minimalizuje maksymalną odległość.")
    _, w, _ = ensure_weighted_graph()
    distances = distance_matrix(w)
    c, total = center(distances)
    m, radius = minimax_center(distances)
    col1, col2 = st.columns(2)
    col1.metric("Centrum", c, f"Suma odległości: {total}")
    col2.metric("Centrum minimax", m, f"Maksymalna odległość: {radius}")
    st.dataframe(distances, use_container_width=True, hide_index=True)


def z3_task5() -> None:
    st.markdown("### 5. Minimalne drzewo rozpinające")
    st.write("Zastosuj algorytm Kruskala. Czerwone krawędzie na rysunku należą do minimalnego drzewa rozpinającego.")
    edges, _, graph = ensure_weighted_graph()
    tree = minimum_spanning_tree(len(graph), edges)
    tree_edges = {(min(u, v), max(u, v)) for u, v, _ in tree}
    st.code("u  v  waga\n" + "\n".join(f"{u}  {v}  {weight}" for u, v, weight in tree))
    st.success(f"Liczba krawędzi: {len(tree)} · Suma wag: {sum(weight for _, _, weight in tree)}")
    labels = {(u, v): weight for u, v, weight in edges}
    st.pyplot(render_graph(graph, "Minimalne drzewo rozpinające", edge_labels=labels, highlight_edges=tree_edges))


def render_set3(task: int) -> None:
    tasks = {1: z3_task1, 2: z3_task2, 3: z3_task3, 4: z3_task4, 5: z3_task5}
    tasks[task]()


SETS = {
    "Zestaw 1": ["1. Kodowanie grafów i konwersja", "2. Wizualizacja na okręgu", "3. Generowanie grafów losowych G(n, l), G(n, p)"],
    "Zestaw 2": ["1. Ciąg graficzny", "2. Randomizacja", "3. Największa spójna składowa", "4. Graf eulerowski i cykl Eulera", "5. Graf k-regularny", "6. Hamiltonowość"],
    "Zestaw 3": ["1. Graf ważony", "2. Algorytm Dijkstry", "3. Macierz odległości", "4. Centrum i centrum minimax", "5. Minimalne drzewo rozpinające"],
}


def main() -> None:
    st.set_page_config(page_title="Grafy Lab", page_icon="📈", layout="wide")
    st.title("Grafy — zestawy i zadania")
    st.write("Wybierz zestaw, a następnie zadanie. Wyniki, reprezentacje i wizualizacja pojawią się w widoku zadania.")
    selected_set = st.radio("Wybierz zestaw", list(SETS), horizontal=True, key="selected_set")
    tasks = SETS[selected_set]
    selected_label = st.radio("Wybierz zadanie", tasks, key=f"task_{selected_set}")
    task_no = tasks.index(selected_label) + 1
    st.markdown(f"## {selected_set} · Zadanie {task_no}")
    if selected_set == "Zestaw 1":
        render_set1(task_no)
    elif selected_set == "Zestaw 2":
        render_set2(task_no)
    else:
        render_set3(task_no)


if __name__ == "__main__":
    main()
