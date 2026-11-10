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


def parse_matrix_text(raw: str) -> Matrix:
    rows = [[int(x) for x in re.split(r"[\s,]+", line.strip()) if x]
            for line in raw.splitlines() if line.strip()]
    if not rows or any(len(row) != len(rows) for row in rows):
        raise ValueError("Macierz musi być niepusta i kwadratowa.")
    return rows


def graph_from_representation(kind: str, raw: str) -> AdjList:
    if kind == "lista sąsiedztwa":
        return parse_adj_list_text(raw)
    matrix = parse_matrix_text(raw)
    if kind == "macierz sąsiedztwa":
        if any(x not in (0, 1) for row in matrix for x in row) or any(matrix[i][i] for i in range(len(matrix))):
            raise ValueError("Macierz grafu prostego zawiera tylko 0/1 i ma zera na przekątnej.")
        if any(matrix[i][j] != matrix[j][i] for i in range(len(matrix)) for j in range(len(matrix))):
            raise ValueError("Macierz sąsiedztwa musi być symetryczna.")
        return matrix_to_list(matrix)
    if kind == "macierz incydencji":
        if any(x not in (0, 1) for row in matrix for x in row) or any(sum(col) != 2 for col in zip(*matrix)):
            raise ValueError("Każda kolumna macierzy incydencji musi zawierać dokładnie dwie jedynki.")
        return incidence_to_list(matrix)
    raise ValueError("Nieznana reprezentacja.")


def graph_to_matrix_text(graph: AdjList) -> str:
    return matrix_to_text(list_to_matrix(normalize_graph(graph))) if graph else ""


def graph_to_incidence_text(graph: AdjList) -> str:
    return matrix_to_text(list_to_incidence(normalize_graph(graph))) if graph else ""


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


DEFAULT_GRAPH: AdjList = {1: [2, 3], 2: [1, 3, 4], 3: [1, 2, 4, 5], 4: [2, 3, 5], 5: [3, 4]}
PRESETS = {
    "Trójkąt i gałąź": DEFAULT_GRAPH,
    "Cykl z przekątnymi": {1: [2, 4, 5], 2: [1, 3, 5], 3: [2, 4, 6], 4: [1, 3, 5, 6], 5: [1, 2, 4, 6], 6: [3, 4, 5]},
    "Drzewo": {1: [2, 3], 2: [1, 4, 5], 3: [1, 6], 4: [2], 5: [2], 6: [3]},
    "Pełny graf K5": {1: [2, 3, 4, 5], 2: [1, 3, 4, 5], 3: [1, 2, 4, 5], 4: [1, 2, 3, 5], 5: [1, 2, 3, 4]},
}

# Zestaw 1

def z1_task1():
    st.markdown("### 1. Kodowanie grafów i konwersja")
    st.write("Koduj graf prosty listą sąsiedztwa, macierzą sąsiedztwa i macierzą incydencji; edytuj reprezentację i konwertuj ją na pozostałe.")
    preset = st.selectbox("Preset grafu", list(PRESETS), key="z1_preset")
    if "z1_graph" not in st.session_state:
        st.session_state["z1_graph"] = DEFAULT_GRAPH
    if st.button("Załaduj preset", key="z1_load"):
        st.session_state["z1_graph"] = PRESETS[preset]
        st.session_state.pop("z1_input", None)
    kind = st.selectbox("Reprezentacja wejściowa", ["lista sąsiedztwa", "macierz sąsiedztwa", "macierz incydencji"], key="z1_kind")
    if "z1_input" not in st.session_state:
        g = st.session_state["z1_graph"]
        st.session_state["z1_input"] = adj_to_text(g) if kind == "lista sąsiedztwa" else graph_to_matrix_text(g) if kind == "macierz sąsiedztwa" else graph_to_incidence_text(g)
    st.text_area("Edytuj dane", key="z1_input", height=150)
    if st.button("Zaktualizuj graf", key="z1_apply"):
        try:
            st.session_state["z1_graph"] = graph_from_representation(kind, st.session_state["z1_input"])
            st.success("Graf zaktualizowany.")
        except ValueError as exc:
            st.error(str(exc))
    g = st.session_state["z1_graph"]
    st.pyplot(render_graph(g, "Graf prosty"), use_container_width=False)
    tabs = st.tabs(["Lista", "Macierz sąsiedztwa", "Macierz incydencji"])
    with tabs[0]: st.code(adj_to_text(g))
    with tabs[1]: st.code(graph_to_matrix_text(g))
    with tabs[2]: st.code(graph_to_incidence_text(g))


def z1_task2():
    st.markdown("### 2. Wizualizacja grafu na okręgu")
    st.write("Wybierz graf i zobacz wierzchołki równomiernie rozmieszczone na okręgu.")
    preset = st.selectbox("Wybierz preset", list(PRESETS), key="z1_visual_preset")
    if st.button("Pokaż graf", key="z1_visual_show"):
        st.session_state["z1_visual_graph"] = PRESETS[preset]
    g = st.session_state.get("z1_visual_graph", DEFAULT_GRAPH)
    st.code(adj_to_text(g))
    st.pyplot(render_graph(g, "Wizualizacja na okręgu"), use_container_width=False)


def z1_task3():
    st.markdown("### 3. Generowanie grafów losowych G(n, l) i G(n, p)")
    st.write("Generuj graf o n wierzchołkach z dokładnie l krawędziami albo z prawdopodobieństwem p dla każdej krawędzi.")
    model = st.radio("Model", ["G(n, l)", "G(n, p)"], horizontal=True, key="z1_model")
    n = st.number_input("Liczba wierzchołków n", 1, 30, 8, key="z1_n")
    if model == "G(n, l)":
        max_l = n * (n - 1) // 2
        l = st.number_input("Liczba krawędzi l", 0, max_l, min(10, max_l), key="z1_l")
    else:
        p = st.slider("Prawdopodobieństwo p", 0.0, 1.0, .4, .01, key="z1_p")
    seed = st.number_input("Seed", 0, 100000, 0, key="z1_seed")
    if st.button("Generuj", key="z1_generate"):
        st.session_state["z1_random_graph"] = gnl(n, l, seed) if model == "G(n, l)" else gnp(n, p, seed)
    g = st.session_state.get("z1_random_graph", gnl(8, 10, seed=0))
    st.code(adj_to_text(g))
    st.pyplot(render_graph(g, "Graf losowy"), use_container_width=False)
    with st.expander("Reprezentacje"):
        st.code("Macierz sąsiedztwa:\n" + graph_to_matrix_text(g) + "\n\nMacierz incydencji:\n" + graph_to_incidence_text(g))


def render_set1(task):
    [z1_task1, z1_task2, z1_task3][task - 1]()

# Zestaw 2

def z2_task1():
    st.markdown("### 1. Sprawdzanie ciągu graficznego i budowa grafu")
    st.write("Podaj stopnie wierzchołków. Program sprawdzi graficzność i skonstruuje graf metodą Havla–Hakimiego.")
    raw = st.text_input("Ciąg stopni", "4 2 2 3 2 1 4 2 2 2 2", key="z2_seq")
    try:
        seq = [int(x) for x in raw.split()]
        ok = is_graphic(seq)
        st.info("Ciąg jest graficzny." if ok else "Ciąg nie jest graficzny.")
        if ok:
            g = build_graph(seq)
            st.write("Stopnie zbudowanego grafu:", [len(g[v]) for v in sorted(g)])
            st.code(adj_to_text(g))
            st.pyplot(render_graph(g, "Graf z zadanego ciągu"), use_container_width=False)
    except ValueError as exc:
        st.error(f"Podaj nieujemne liczby całkowite: {exc}")


def z2_task2():
    st.markdown("### 2. Randomizacja grafu o zadanych stopniach")
    st.write("Podaj ciąg stopni wierzchołków. Program zbuduje graf prosty o tych stopniach, a następnie wykona losowe zamiany krawędzi ab, cd → ad, bc. Stopnie pozostaną niezmienione.")
    sequence_text = st.text_input(
        "Ciąg stopni wierzchołków (liczby oddziel spacjami)",
        value="3 3 2 2 2 2",
        key="z2_random_degree_sequence",
        help="Przykład: 3 3 2 2 2 2. Podany ciąg musi być graficzny.",
    )
    swaps = st.number_input("Liczba prób zamiany krawędzi", min_value=1, max_value=5000, value=50, key="z2_swaps")
    seed = st.number_input("Seed (to samo ziarno daje ten sam wynik)", min_value=0, max_value=100000, value=0, key="z2_random_seed")

    try:
        degrees = [int(value) for value in sequence_text.split()]
        if not degrees:
            raise ValueError("Wpisz co najmniej jeden stopień.")
        if any(degree < 0 for degree in degrees):
            raise ValueError("Stopnie nie mogą być ujemne.")
        if not is_graphic(degrees):
            st.error("Podany ciąg nie jest graficzny. Zmień stopnie tak, aby można było zbudować graf prosty.")
            return

        original = build_graph(degrees)
        degree_key = tuple(degrees)
        state_key = "z2_random_result"
        if st.session_state.get("z2_random_result_degrees") != degree_key:
            st.session_state[state_key] = original
            st.session_state["z2_random_result_degrees"] = degree_key

        if st.button("Zbuduj i randomizuj graf", key="z2_randomize"):
            st.session_state[state_key] = randomize(original, int(swaps), seed=int(seed))
            st.session_state["z2_random_result_degrees"] = degree_key

        result = st.session_state[state_key]
        original_degrees = [len(original[v]) for v in sorted(original)]
        result_degrees = [len(result[v]) for v in sorted(result)]

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Graf skonstruowany z ciągu")
            st.caption(f"Stopnie: {original_degrees} · Krawędzie: {len(__import__('grafy.common.graph', fromlist=['adj_to_edges']).adj_to_edges(original))}")
            st.code(adj_to_text(original))
            st.pyplot(render_graph(original, "Graf przed randomizacją"), use_container_width=False)
        with col2:
            st.subheader("Graf po randomizacji")
            st.caption(f"Stopnie: {result_degrees} · Zamiany: maks. {int(swaps)} prób")
            st.code(adj_to_text(result))
            st.pyplot(render_graph(result, "Graf po randomizacji"), use_container_width=False)
        if original_degrees != result_degrees:
            st.error("Błąd: randomizacja zmieniła stopnie wierzchołków.")
        else:
            st.success("Stopnie wierzchołków są zachowane.")
    except ValueError as exc:
        st.error(f"Niepoprawny ciąg stopni: {exc}")


def z2_task3():
    st.markdown("### 3. Największa spójna składowa")
    st.write("Edytuj listę sąsiedztwa. Program wypisze wszystkie składowe i wyświetli największą.")
    default = {1: [2], 2: [1], 3: [4, 5], 4: [3], 5: [3], 6: []}
    g = graph_editor("Graf wejściowy", "z2_components_input", default)
    comp = components(g)
    groups: dict[int, list[int]] = {}
    for vertex, label in comp.items():
        groups.setdefault(label, []).append(vertex)
    st.subheader("Składowe spójności")
    for number, vertices in groups.items():
        st.write(f"Składowa {number}: {vertices} (rozmiar {len(vertices)})")
    biggest = largest_component(g)
    st.success(f"Największa składowa: {biggest} — {len(biggest)} wierzchołków")
    st.pyplot(render_graph(g, "Graf wejściowy"), use_container_width=False)
    sub = {u: [v for v in g[u] if v in biggest] for u in biggest}
    st.subheader("Podgraf największej składowej")
    st.code(adj_to_text(sub))
    st.pyplot(render_graph(sub, "Największa składowa"), use_container_width=False)


def z2_task4():
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
    st.pyplot(render_graph(g, "Graf eulerowski", highlight_edges=list(zip(cycle, cycle[1:]))), use_container_width=False)


def z2_task5():
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
    g = st.session_state["z2_regular_graph"]
    st.write("Stopnie:", [len(g[v]) for v in sorted(g)])
    st.code(adj_to_text(g))
    st.pyplot(render_graph(g, "Graf k-regularny"), use_container_width=False)


def z2_task6():
    st.markdown("### 6. Sprawdzanie Hamiltonowości")
    st.write("Edytuj graf prosty. Program sprawdzi, czy istnieje cykl Hamiltona przechodzący przez każdy wierzchołek dokładnie raz.")
    default = {1: [2, 3], 2: [1, 3, 4], 3: [1, 2, 4], 4: [2, 3]}
    g = graph_editor("Graf wejściowy", "z2_hamilton_input", default)
    cycle = hamilton_cycle(g)
    if cycle:
        st.success("Graf jest hamiltonowski. Cykl: " + " → ".join(map(str, cycle)))
        st.pyplot(render_graph(g, "Znaleziony cykl Hamiltona", highlight_edges=list(zip(cycle, cycle[1:]))), use_container_width=False)
    else:
        st.warning("Graf nie jest hamiltonowski — cyklu Hamiltona nie znaleziono.")
        st.pyplot(render_graph(g, "Graf wejściowy"), use_container_width=False)
    st.subheader("Lista sąsiedztwa grafu")
    st.code(adj_to_text(g))


def render_set2(task):
    {1: z2_task1, 2: z2_task2, 3: z2_task3, 4: z2_task4, 5: z2_task5, 6: z2_task6}[task]()

# Zestaw 3

def ensure_weighted_graph():
    if "z3_edges" not in st.session_state:
        edges, matrix = random_connected_weighted_graph(12, p=.2, seed=0)
        st.session_state["z3_edges"] = edges
        st.session_state["z3_matrix"] = matrix
        st.session_state["z3_adj"] = edges_to_adj(12, [(u, v) for u, v, _ in edges])
    return st.session_state["z3_edges"], st.session_state["z3_matrix"], st.session_state["z3_adj"]


def z3_task1():
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


def z3_task2():
    st.markdown("### 2. Najkrótsze ścieżki — algorytm Dijkstry")
    st.write("Dla wybranego wierzchołka pokaż długości i przebiegi najkrótszych ścieżek do pozostałych.")
    _, w, graph = ensure_weighted_graph()
    start = st.number_input("Wierzchołek startowy", 1, len(w), 1, key="z3_dijkstra_start")
    ds, parents = dijkstra(w, start - 1)
    rows = [{"Cel": v + 1, "Odległość": d, "Ścieżka": " → ".join(str(x + 1) for x in shortest_path(parents, start - 1, v))}
            for v, d in enumerate(ds)]
    st.dataframe(rows, use_container_width=True, hide_index=True)
    st.pyplot(render_graph(graph, f"Najkrótsze ścieżki od {start}"), use_container_width=False)


def z3_task3():
    st.markdown("### 3. Macierz odległości")
    st.write("Wyznacz najkrótsze odległości między wszystkimi parami wierzchołków.")
    _, w, _ = ensure_weighted_graph()
    st.dataframe(distance_matrix(w), use_container_width=True, hide_index=True)


def z3_task4():
    st.markdown("### 4. Centrum i centrum minimax")
    st.write("Centrum minimalizuje sumę odległości; centrum minimax minimalizuje maksymalną odległość.")
    _, w, _ = ensure_weighted_graph()
    d = distance_matrix(w)
    c, total = center(d)
    m, radius = minimax_center(d)
    col1, col2 = st.columns(2)
    col1.metric("Centrum", c, f"Suma odległości: {total}")
    col2.metric("Centrum minimax", m, f"Maksymalna odległość: {radius}")
    st.dataframe(d, use_container_width=True, hide_index=True)


def z3_task5():
    st.markdown("### 5. Minimalne drzewo rozpinające")
    st.write("Zastosuj algorytm Kruskala. Krawędzie MST są zaznaczone na czerwono.")
    edges, _, graph = ensure_weighted_graph()
    tree = minimum_spanning_tree(len(graph), edges)
    highlight = {(min(u, v), max(u, v)) for u, v, _ in tree}
    st.code("u  v  waga\n" + "\n".join(f"{u}  {v}  {w}" for u, v, w in tree))
    st.success(f"Krawędzie: {len(tree)} · Suma wag: {sum(w for _, _, w in tree)}")
    labels = {(u, v): w for u, v, w in edges}
    st.pyplot(render_graph(graph, "Minimalne drzewo rozpinające", labels, highlight), use_container_width=False)


def render_set3(task):
    {1: z3_task1, 2: z3_task2, 3: z3_task3, 4: z3_task4, 5: z3_task5}[task]()


SETS = {
    "Zestaw 1": ["1. Kodowanie grafów i konwersja", "2. Wizualizacja na okręgu", "3. Generowanie grafów losowych G(n, l), G(n, p)"],
    "Zestaw 2": ["1. Ciąg graficzny", "2. Randomizacja", "3. Największa spójna składowa", "4. Graf eulerowski i cykl Eulera", "5. Graf k-regularny", "6. Hamiltonowość"],
    "Zestaw 3": ["1. Graf ważony", "2. Algorytm Dijkstry", "3. Macierz odległości", "4. Centrum i centrum minimax", "5. Minimalne drzewo rozpinające"],
}


def main():
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
    else:
        render_set3(task)


if __name__ == "__main__":
    main()
