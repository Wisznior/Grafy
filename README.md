import streamlit as st
import matplotlib.pyplot as plt

from grafy.zestaw1.random_graphs import gnl, gnp
from grafy.zestaw1.representations import convert, list_to_incidence, list_to_matrix
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


SETS = {
    "z1": {
        "title": "Zestaw 1",
        "tasks": {
            "z1_1": {
                "title": "Zadanie 1: reprezentacje grafów i konwersja",
                "description": "Napisz program kodujący graf prosty za pomocą macierzy sąsiedztwa, macierzy incydencji i listy sąsiedztwa. Stwórz moduł do zamiany pomiędzy reprezentacjami. Wartość: 3 reprezentacje × 2 pkt = 6 pkt.",
            },
            "z1_2": {
                "title": "Zadanie 2: wizualizacja grafu na okręgu",
                "description": "Narysuj graf prosty z wierzchołkami rozłożonymi równomiernie na okręgu. Wartość: 2 pkt.",
            },
            "z1_3": {
                "title": "Zadanie 3: generowanie grafów losowych G(n, l) i G(n, p)",
                "description": "Zaimplementuj generowanie grafu losowego G(n, l) i G(n, p). Wartość: 2 rodzaje losowań × 1 pkt = 2 pkt.",
            },
        },
    },
    "z2": {
        "title": "Zestaw 2",
        "tasks": {
            "z2_1": {"title": "Zadanie 1: ciąg graficzny", "description": "Sprawdź, czy ciąg jest graficzny i zbuduj prosty graf o podanych stopniach wierzchołków."},
            "z2_2": {"title": "Zadanie 2: randomizacja grafu", "description": "Zamieniaj losowe pary krawędzi ab i cd na ad i bc, zachowując stopnie wierzchołków."},
            "z2_3": {"title": "Zadanie 3: największa spójna składowa", "description": "Znajdź największą składową spójną grafu."},
            "z2_4": {"title": "Zadanie 4: cykl Eulera", "description": "Wygeneruj graf eulerowski i znajdź cykl Eulera."},
            "z2_5": {"title": "Zadanie 5: graf k-regularny", "description": "Wygeneruj losowy graf k-regularny."},
            "z2_6": {"title": "Zadanie 6: graf hamiltonowski", "description": "Sprawdź, czy graf jest hamiltonowski."},
        },
    },
    "z3": {
        "title": "Zestaw 3",
        "tasks": {
            "z3_1": {"title": "Zadanie 1: graf ważony", "description": "Wygeneruj spójny graf losowy i przypisz każdej krawędzi losową wagę z zakresu 1..10."},
            "z3_2": {"title": "Zadanie 2: Dijkstra", "description": "Znajdź najkrótsze ścieżki od zadanego wierzchołka."},
            "z3_3": {"title": "Zadanie 3: macierz odległości", "description": "Wyznacz macierz odległości między wszystkimi parami wierzchołków."},
            "z3_4": {"title": "Zadanie 4: centrum grafu", "description": "Wyznacz centrum grafu i centrum minimax."},
            "z3_5": {"title": "Zadanie 5: MST", "description": "Znajdź minimalne drzewo rozpinające."},
        },
    },
}


SAMPLE_MATRIX = """1 0 1 1 0 1 0 0 0 0 0 0
0 1 0 0 1 1 0 0 0 0 0 0
1 0 1 0 1 0 0 0 0 0 0 0
0 1 0 0 0 1 1 0 0 0 0 0
0 0 1 0 0 0 1 0 0 0 0 0
1 1 0 1 0 0 0 1 0 0 0 0
0 0 0 1 1 0 0 1 0 0 0 0
0 0 0 0 0 1 1 0 1 0 0 0
0 0 0 0 0 0 0 1 0 1 0 1
0 0 0 0 0 0 0 0 1 0 1 0
0 0 0 0 0 0 0 0 0 1 0 1
0 0 0 0 0 0 0 0 1 0 1 0"""

SAMPLE_LIST = """1: 2 3 6
2: 1 4 5 6
3: 1 2 5
4: 2 6 7
5: 2 3 7
6: 1 2 4 8
7: 4 5 8
8: 6 7 9 12
9: 8 10 12
10: 9 11
11: 10 12
12: 8 9 11"""

SAMPLE_INCIDENCE = """0 0 0 1 0 0 0 0 0 0 0 0
1 0 0 0 0 0 0 0 0 0 0 0
0 1 0 0 0 0 0 0 0 0 0 0
0 0 1 0 1 0 0 0 0 0 0 0
0 0 0 0 0 1 0 0 0 0 0 0
1 0 0 0 0 0 1 0 0 0 0 0
0 0 0 0 0 0 0 1 0 0 0 0
0 0 0 0 0 0 0 0 1 0 0 0
0 0 0 0 0 0 0 0 0 1 0 0
0 0 0 0 0 0 0 0 0 0 1 0
0 0 0 0 0 0 0 0 0 0 0 1
0 0 0 0 0 0 0 0 0 0 0 0"""


def clean_adj(adj):
    return {v: sorted(set(nb)) for v, nb in adj.items()}


def adj_to_text(adj):
    return "\n".join(
        f"{v}: {', '.join(map(str, adj.get(v, []))) if adj.get(v) else '-'}"
        for v in sorted(adj)
    )


def matrix_to_text(matrix):
    return "\n".join(" ".join(map(str, row)) for row in matrix)


def parse_matrix(text):
    rows = []
    for line in text.strip().splitlines():
        if not line.strip():
            continue
        rows.append([int(x) for x in line.split()])
    return rows


def parse_list(text):
    adj = {}
    for line in text.strip().splitlines():
        if not line.strip():
            continue
        left, right = line.split(":", 1)
        key = int(left.strip())
        values = [int(x.strip()) for x in right.split() if x.strip()]
        adj[key] = values
    return adj


def parse_incidence(text):
    rows = []
    for line in text.strip().splitlines():
        if not line.strip():
            continue
        rows.append([int(x) for x in line.split()])
    return rows


def render_graph(adj, title="Graf", weights=None, tree_edges=None, colors=None):
    fig, ax = plt.subplots(figsize=(7, 7))
    pos = circle_layout(len(adj))
    for u in sorted(adj):
        for v in sorted(adj[u]):
            if u < v:
                (x1, y1), (x2, y2) = pos[u - 1], pos[v - 1]
                is_tree = bool(tree_edges and (min(u, v), max(u, v)) in tree_edges)
                color = "#2c7be5" if is_tree else "#495057"
                lw = 3.0 if is_tree else 1.8
                ax.plot([x1, x2], [y1, y2], color=color, lw=lw)
                if weights and (min(u, v), max(u, v)) in weights:
                    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
                    ax.text(mx, my, str(weights[(min(u, v), max(u, v))]), fontsize=9, ha="center", va="center",
                            bbox={"boxstyle": "round,pad=0.25", "fc": "white", "ec": "none"})
    for idx, (x, y) in enumerate(pos, start=1):
        fill = plt.cm.tab10(colors[idx] % 10) if colors else "#dfe8ff"
        ax.text(x, y, str(idx), ha="center", va="center", fontsize=11,
                bbox={"boxstyle": "circle,pad=0.35", "fc": fill, "ec": "#2c7be5"})
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, pad=18)
    return fig


def default_graph_for_task(set_key, task_key):
    if set_key == "z1":
        if task_key == "z1_1":
            return clean_adj(parse_list(SAMPLE_LIST))
        return clean_adj(gnp(7, 0.45, seed=4))
    if set_key == "z2":
        return clean_adj(build_graph([4, 2, 2, 3, 2, 1, 4, 2, 2, 2, 2]))
    if set_key == "z3":
        edges, _ = random_connected_weighted_graph(6, 0.45, seed=4)
        adj = {v: [] for v in range(1, 7)}
        for u, v, _ in edges:
            adj[u].append(v)
            adj[v].append(u)
        return {k: sorted(set(v)) for k, v in adj.items()}
    return {}


def ensure_task_state(set_key, task_key):
    graph_key = f"graph_{set_key}_{task_key}"
    if graph_key not in st.session_state:
        st.session_state[graph_key] = default_graph_for_task(set_key, task_key)
    return st.session_state[graph_key]


def show_home():
    st.title("Grafy i ich zastosowania")
    st.caption("Wybierz zestaw. Następnie wybierz zadanie z listy, aby zobaczyć tylko te pola i funkcje, które są potrzebne do danego ćwiczenia.")
    cols = st.columns(3)
    for idx, key in enumerate(["z1", "z2", "z3"]):
        with cols[idx]:
            st.markdown(f"### {SETS[key]['title']}")
            st.write(f"Zadania: {len(SETS[key]['tasks'])}")
            if st.button(f"Otwórz {SETS[key]['title']}", key=f"open_{key}"):
                st.session_state.current_set = key
                st.session_state.current_task = next(iter(SETS[key]["tasks"]))
                st.rerun()


def show_set(set_key):
    st.title(SETS[set_key]["title"])
    st.markdown("---")
    task_keys = list(SETS[set_key]["tasks"].keys())
    for task_key in task_keys:
        task = SETS[set_key]["tasks"][task_key]
        st.subheader(task["title"])
        st.write(task["description"])
        if st.button(f"Wybierz {task['title']}", key=f"select_{set_key}_{task_key}"):
            st.session_state.current_task = task_key
            st.rerun()
        st.markdown("---")


def render_z1_1():
    set_key, task_key = "z1", "z1_1"
    graph = ensure_task_state(set_key, task_key)
    st.subheader("Zadanie 1: reprezentacje grafów i konwersja")
    st.write(SETS[set_key]["tasks"][task_key]["description"])

    example = st.radio("Wybierz przykładowy input", ["Lista sąsiedztwa", "Macierz sąsiedztwa", "Macierz incydencji"], key=f"{task_key}_example")
    if example == "Lista sąsiedztwa":
        default_text = SAMPLE_LIST
    elif example == "Macierz sąsiedztwa":
        default_text = SAMPLE_MATRIX
    else:
        default_text = SAMPLE_INCIDENCE

    source = st.selectbox("Reprezentacja wejściowa", ["list", "matrix", "incidence"], key=f"{task_key}_source")
    raw = st.text_area("Wprowadź dane grafu", value=default_text, height=220, key=f"{task_key}_raw")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Przykład z zadania", key=f"{task_key}_example_button"):
            st.session_state[f"{task_key}_raw"] = default_text
    with col2:
        if st.button("Konwertuj", key=f"{task_key}_convert"):
            try:
                if source == "list":
                    data = parse_list(raw)
                elif source == "matrix":
                    data = parse_matrix(raw)
                else:
                    data = parse_incidence(raw)
                out_list = convert(data, source, "list")
                out_matrix = convert(data, source, "matrix")
                out_inc = convert(data, source, "incidence")
                st.session_state[f"{task_key}_out_list"] = out_list
                st.session_state[f"{task_key}_out_matrix"] = out_matrix
                st.session_state[f"{task_key}_out_inc"] = out_inc
                st.success("Konwersja zakończona pomyślnie.")
            except Exception as exc:
                st.error(f"Błąd parsowania: {exc}")

    if f"{task_key}_out_list" in st.session_state:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.subheader("Lista sąsiedztwa")
            st.code(adj_to_text(st.session_state[f"{task_key}_out_list"]))
        with c2:
            st.subheader("Macierz sąsiedztwa")
            st.code(matrix_to_text(st.session_state[f"{task_key}_out_matrix"]))
        with c3:
            st.subheader("Macierz incydencji")
            st.code(matrix_to_text(st.session_state[f"{task_key}_out_inc"]))

    st.markdown("---")
    st.subheader("Wizualizacja")
    st.pyplot(render_graph(graph, title="Graf prosty"))


def render_z1_2():
    set_key, task_key = "z1", "z1_2"
    graph = ensure_task_state(set_key, task_key)
    st.subheader("Zadanie 2: wizualizacja grafu na okręgu")
    st.write(SETS[set_key]["tasks"][task_key]["description"])

    n = st.slider("Liczba wierzchołków", min_value=3, max_value=12, value=max(graph.keys()) if graph else 7)
    p = st.slider("Prawdopodobieństwo połączenia p", min_value=0.0, max_value=1.0, value=0.45, step=0.01)
    seed = st.number_input("Seed", min_value=0, max_value=1000, value=3)
    if st.button("Generuj graf", key=f"{task_key}_gen"):
        st.session_state[f"graph_{set_key}_{task_key}"] = clean_adj(gnp(n, p, seed=seed))
    graph = st.session_state[f"graph_{set_key}_{task_key}"]
    st.pyplot(render_graph(graph, title="Graf na okręgu"))
    st.code(adj_to_text(graph))


def render_z1_3():
    set_key, task_key = "z1", "z1_3"
    graph = ensure_task_state(set_key, task_key)
    st.subheader("Zadanie 3: generowanie grafów losowych G(n, l) i G(n, p)")
    st.write(SETS[set_key]["tasks"][task_key]["description"])

    model = st.radio("Model losowy", ["G(n, l)", "G(n, p)"], key=f"{task_key}_model")
    n = st.number_input("n", min_value=2, max_value=20, value=7, key=f"{task_key}_n")
    p = st.slider("p", min_value=0.0, max_value=1.0, value=0.35, step=0.01, key=f"{task_key}_p")
    l = st.number_input("l", min_value=0, max_value=60, value=10, key=f"{task_key}_l")
    seed = st.number_input("Seed", min_value=0, max_value=1000, value=2, key=f"{task_key}_seed")
    if st.button("Generuj graf", key=f"{task_key}_gen"):
        if model == "G(n, p)":
            graph = clean_adj(gnp(n, p, seed=seed))
        else:
            graph = clean_adj(gnl(n, l, seed=seed))
        st.session_state[f"graph_{set_key}_{task_key}"] = graph
    graph = st.session_state[f"graph_{set_key}_{task_key}"]
    st.pyplot(render_graph(graph, title=model))
    st.code(f"Liczba krawędzi: {sum(len(v) for v in graph.values()) // 2}")
    st.code(adj_to_text(graph))


def render_z2_1():
    set_key, task_key = "z2", "z2_1"
    graph = ensure_task_state(set_key, task_key)
    st.subheader("Zadanie 1: ciąg graficzny")
    st.write(SETS[set_key]["tasks"][task_key]["description"])
    seq = st.text_input("Ciąg stopni", value="4 2 2 3 2 1 4 2 2 2 2", key=f"{task_key}_seq")
    if st.button("Sprawdź i zbuduj graf", key=f"{task_key}_gen"):
        values = [int(x) for x in seq.split() if x]
        if not is_graphic(values):
            st.warning("Ciąg nie jest graficzny.")
        else:
            graph = clean_adj(build_graph(values))
            st.session_state[f"graph_{set_key}_{task_key}"] = graph
            st.success("Ciąg jest graficzny.")
    graph = st.session_state[f"graph_{set_key}_{task_key}"]
    st.pyplot(render_graph(graph, title="Graf z ciągu graficznego"))
    st.code(f"Stopnie: {[len(graph[v]) for v in sorted(graph)]}")


def render_z2_2():
    set_key, task_key = "z2", "z2_2"
    graph = ensure_task_state(set_key, task_key)
    st.subheader("Zadanie 2: randomizacja grafu")
    st.write(SETS[set_key]["tasks"][task_key]["description"])
    swaps = st.number_input("Liczba swapów", min_value=1, max_value=200, value=50, key=f"{task_key}_swaps")
    seed = st.number_input("Seed", min_value=0, max_value=10000, value=7, key=f"{task_key}_seed")
    if st.button("Zrandomizuj", key=f"{task_key}_gen"):
        graph = clean_adj(randomize(graph, swaps, seed=seed))
        st.session_state[f"graph_{set_key}_{task_key}"] = graph
    graph = st.session_state[f"graph_{set_key}_{task_key}"]
    st.pyplot(render_graph(graph, title="Graf po randomizacji"))
    st.code(f"Stopnie: {[len(graph[v]) for v in sorted(graph)]}")


def render_z2_3():
    set_key, task_key = "z2", "z2_3"
    graph = ensure_task_state(set_key, task_key)
    st.subheader("Zadanie 3: największa spójna składowa")
    st.write(SETS[set_key]["tasks"][task_key]["description"])
    if st.button("Wczytaj przykładowy graf", key=f"{task_key}_gen"):
        graph = clean_adj({1: [2], 2: [1], 3: [4, 5], 4: [3], 5: [3], 6: []})
        st.session_state[f"graph_{set_key}_{task_key}"] = graph
    graph = st.session_state[f"graph_{set_key}_{task_key}"]
    comp = components(graph)
    groups = {}
    for v in sorted(comp):
        groups.setdefault(comp[v], []).append(v)
    st.write("Składowe:")
    st.code("\n".join(f"{k}: {v}" for k, v in groups.items()))
    st.write(f"Największa składowa: {largest_component(graph)}")
    st.pyplot(render_graph(graph, title="Składowe spójności", colors={v: c for v, c in comp.items()}))


def render_z2_4():
    set_key, task_key = "z2", "z2_4"
    graph = ensure_task_state(set_key, task_key)
    st.subheader("Zadanie 4: cykl Eulera")
    st.write(SETS[set_key]["tasks"][task_key]["description"])
    n = st.number_input("n", min_value=3, max_value=16, value=8, key=f"{task_key}_n")
    seed = st.number_input("Seed", min_value=0, max_value=10000, value=2, key=f"{task_key}_seed")
    if st.button("Generuj graf eulerowski", key=f"{task_key}_gen"):
        graph = random_eulerian_graph(n, seed=seed)
        st.session_state[f"graph_{set_key}_{task_key}"] = graph
    graph = st.session_state[f"graph_{set_key}_{task_key}"]
    try:
        cycle = euler_cycle(graph)
        st.success("Cykl Eulera znaleziony.")
        st.code(" -> ".join(map(str, cycle)))
    except ValueError:
        st.warning("Graf nie jest eulerowski.")
    st.pyplot(render_graph(graph, title="Graf eulerowski"))


def render_z2_5():
    set_key, task_key = "z2", "z2_5"
    graph = ensure_task_state(set_key, task_key)
    st.subheader("Zadanie 5: graf k-regularny")
    st.write(SETS[set_key]["tasks"][task_key]["description"])
    n = st.number_input("n", min_value=2, max_value=20, value=8, key=f"{task_key}_n")
    k = st.number_input("k", min_value=0, max_value=9, value=2, key=f"{task_key}_k")
    seed = st.number_input("Seed", min_value=0, max_value=10000, value=11, key=f"{task_key}_seed")
    if st.button("Generuj graf k-regularny", key=f"{task_key}_gen"):
        try:
            graph = clean_adj(random_k_regular(n, k, seed=seed))
            st.session_state[f"graph_{set_key}_{task_key}"] = graph
            st.success("Graf wygenerowany.")
        except ValueError as exc:
            st.error(str(exc))
    graph = st.session_state[f"graph_{set_key}_{task_key}"]
    st.pyplot(render_graph(graph, title=f"Graf {k}-regularny"))
    st.code(f"Stopnie: {[len(graph[v]) for v in sorted(graph)]}")


def render_z2_6():
    set_key, task_key = "z2", "z2_6"
    graph = ensure_task_state(set_key, task_key)
    st.subheader("Zadanie 6: graf hamiltonowski")
    st.write(SETS[set_key]["tasks"][task_key]["description"])
    if st.button("Wczytaj przykładowy graf", key=f"{task_key}_gen"):
        graph = {1: [2, 3], 2: [1, 3], 3: [1, 2]}
        st.session_state[f"graph_{set_key}_{task_key}"] = graph
    graph = st.session_state[f"graph_{set_key}_{task_key}"]
    cycle = hamilton_cycle(graph)
    if cycle:
        st.success("Graf jest hamiltonowski.")
        st.code(" -> ".join(map(str, cycle)))
    else:
        st.warning("Graf nie jest hamiltonowski.")
    st.pyplot(render_graph(graph, title="Graf do badania hamiltonowości"))


def render_z3_1():
    set_key, task_key = "z3", "z3_1"
    st.subheader("Zadanie 1: graf ważony")
    st.write(SETS[set_key]["tasks"][task_key]["description"])
    n = st.number_input("n", min_value=2, max_value=20, value=8, key=f"{task_key}_n")
    p = st.slider("p", min_value=0.0, max_value=1.0, value=0.25, step=0.01, key=f"{task_key}_p")
    seed = st.number_input("Seed", min_value=0, max_value=10000, value=3, key=f"{task_key}_seed")
    if st.button("Generuj graf ważony", key=f"{task_key}_gen"):
        edges, _ = random_connected_weighted_graph(n, p, seed=seed)
        st.session_state[f"weighted_edges_{task_key}"] = edges
        adj = {v: [] for v in range(1, n + 1)}
        for u, v, _ in edges:
            adj[u].append(v)
            adj[v].append(u)
        st.session_state[f"graph_{set_key}_{task_key}"] = {k: sorted(set(v)) for k, v in adj.items()}
    edges = st.session_state.get(f"weighted_edges_{task_key}", [])
    if edges:
        st.code("\n".join(f"{u}-{v}: {w}" for u, v, w in edges))
        graph = st.session_state.get(f"graph_{set_key}_{task_key}", {})
        st.pyplot(render_graph(graph, title="Graf ważony"))


def render_z3_2():
    set_key, task_key = "z3", "z3_2"
    st.subheader("Zadanie 2: Dijkstra")
    st.write(SETS[set_key]["tasks"][task_key]["description"])
    edges = st.session_state.get(f"weighted_edges_z3_1", [])
    if not edges:
        edges, _ = random_connected_weighted_graph(6, 0.45, seed=4)
        st.session_state[f"weighted_edges_z3_1"] = edges
    n = max(max(u, v) for u, v, _ in edges)
    w = [[0] * n for _ in range(n)]
    for u, v, weight in edges:
        w[u - 1][v - 1] = w[v - 1][u - 1] = weight
    graph = {v: [] for v in range(1, n + 1)}
    for u, v, _ in edges:
        graph[u].append(v)
        graph[v].append(u)
    start = st.selectbox("Wierzchołek startowy", list(range(1, n + 1)), key=f"{task_key}_start")
    if st.button("Uruchom Dijkstrę", key=f"{task_key}_gen"):
        ds, ps = dijkstra(w, start - 1)
        st.code("\n".join(
            f"d({v}) = {ds[v - 1]}  ścieżka: {' -> '.join(map(str, shortest_path(ps, start - 1, v - 1)))}"
            for v in range(1, n + 1)
        ))
    st.pyplot(render_graph({k: sorted(set(v)) for k, v in graph.items()}, title="Graf do Dijkstry"))


def render_z3_3():
    set_key, task_key = "z3", "z3_3"
    st.subheader("Zadanie 3: macierz odległości")
    st.write(SETS[set_key]["tasks"][task_key]["description"])
    edges = st.session_state.get(f"weighted_edges_z3_1", [])
    if not edges:
        edges, _ = random_connected_weighted_graph(6, 0.45, seed=4)
        st.session_state[f"weighted_edges_z3_1"] = edges
    n = max(max(u, v) for u, v, _ in edges)
    w = [[0] * n for _ in range(n)]
    for u, v, weight in edges:
        w[u - 1][v - 1] = w[v - 1][u - 1] = weight
    st.code(matrix_to_text(distance_matrix(w)))


def render_z3_4():
    set_key, task_key = "z3", "z3_4"
    st.subheader("Zadanie 4: centrum grafu")
    st.write(SETS[set_key]["tasks"][task_key]["description"])
    edges = st.session_state.get(f"weighted_edges_z3_1", [])
    if not edges:
        edges, _ = random_connected_weighted_graph(6, 0.45, seed=4)
        st.session_state[f"weighted_edges_z3_1"] = edges
    n = max(max(u, v) for u, v, _ in edges)
    w = [[0] * n for _ in range(n)]
    for u, v, weight in edges:
        w[u - 1][v - 1] = w[v - 1][u - 1] = weight
    dist = distance_matrix(w)
    c, cs = center(dist)
    m, md = minimax_center(dist)
    st.write(f"Centrum: {c + 1} (suma odległości = {cs})")
    st.write(f"Centrum minimax: {m + 1} (najdalsza odległość = {md})")
    st.code(matrix_to_text(dist))


def render_z3_5():
    set_key, task_key = "z3", "z3_5"
    st.subheader("Zadanie 5: minimalne drzewo rozpinające")
    st.write(SETS[set_key]["tasks"][task_key]["description"])
    edges = st.session_state.get(f"weighted_edges_z3_1", [])
    if not edges:
        edges, _ = random_connected_weighted_graph(6, 0.45, seed=4)
        st.session_state[f"weighted_edges_z3_1"] = edges
    n = max(max(u, v) for u, v, _ in edges)
    mst = minimum_spanning_tree(n, edges)
    st.write(f"Waga MST: {sum(w for *_, w in mst)}")
    st.code("\n".join(f"{u}-{v}: {w}" for u, v, w in mst))
    tree_edges = {(min(u, v), max(u, v)) for u, v, _ in mst}
    adj = {v: [] for v in range(1, n + 1)}
    for u, v, _ in edges:
        adj[u].append(v)
        adj[v].append(u)
    st.pyplot(render_graph({k: sorted(set(v)) for k, v in adj.items()}, title="MST", tree_edges=tree_edges))


TASK_RENDERERS = {
    "z1_1": render_z1_1,
    "z1_2": render_z1_2,
    "z1_3": render_z1_3,
    "z2_1": render_z2_1,
    "z2_2": render_z2_2,
    "z2_3": render_z2_3,
    "z2_4": render_z2_4,
    "z2_5": render_z2_5,
    "z2_6": render_z2_6,
    "z3_1": render_z3_1,
    "z3_2": render_z3_2,
    "z3_3": render_z3_3,
    "z3_4": render_z3_4,
    "z3_5": render_z3_5,
}


def main():
    st.set_page_config(page_title="Grafy Lab", page_icon="📈", layout="wide")
    if "current_set" not in st.session_state:
        st.session_state.current_set = None
    if "current_task" not in st.session_state:
        st.session_state.current_task = None

    if st.session_state.current_set is None:
        show_home()
        return

    set_key = st.session_state.current_set
    task_key = st.session_state.current_task

    st.sidebar.title("Nawigacja")
    if st.sidebar.button("← Wróć do zestawów"):
        st.session_state.current_set = None
        st.session_state.current_task = None
        st.rerun()

    st.sidebar.write(f"Zestaw: {SETS[set_key]['title']}")
    for key, task in SETS[set_key]["tasks"].items():
        if st.sidebar.button(task["title"], key=f"side_{set_key}_{key}"):
            st.session_state.current_task = key
            st.rerun()

    if task_key not in SETS[set_key]["tasks"]:
        st.session_state.current_task = next(iter(SETS[set_key]["tasks"]))
        st.rerun()

    TASK_RENDERERS[task_key]()


if __name__ == "__main__":
    main()

