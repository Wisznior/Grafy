import streamlit as st
import matplotlib.pyplot as plt

from grafy.zestaw1.random_graphs import gnl, gnp
from grafy.zestaw1.representations import list_to_incidence, list_to_matrix
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
                "title": "1. Kodowanie grafów i konwersja",
                "description": "Napisz program kodujący graf prosty za pomocą macierzy sąsiedztwa, macierzy incydencji i listy sąsiedztwa. Stwórz moduł do konwersji między reprezentacjami.",
            },
            "z1_2": {
                "title": "2. Wizualizacja na okręgu",
                "description": "Narysuj graf prosty z wierzchołkami rozłożonymi równomiernie na okręgu.",
            },
            "z1_3": {
                "title": "3. Generowanie grafów losowych G(n, l) i G(n, p)",
                "description": "Zaimplementuj generację losowych grafów G(n, l) oraz G(n, p).",
            },
        },
    },
    "z2": {
        "title": "Zestaw 2",
        "tasks": {
            "z2_1": {
                "title": "1. Ciąg graficzny i konstrukcja grafu",
                "description": "Sprawdź, czy ciąg jest graficzny, i zbuduj prosty graf o stopniach podanych przez ten ciąg.",
            },
            "z2_2": {
                "title": "2. Randomizacja grafu o zadanych stopniach",
                "description": "Wykonuj wielokrotnie zamianę ab i cd na ad i bc, zachowując stopnie wierzchołków.",
            },
            "z2_3": {
                "title": "3. Największa spójna składowa",
                "description": "Znajdź największą spójną składową w grafie.",
            },
            "z2_4": {
                "title": "4. Graf eulerowski i cykl Eulera",
                "description": "Wygeneruj losowy graf eulerowski i znajdź na nim cykl Eulera.",
            },
            "z2_5": {
                "title": "5. Graf k-regularny",
                "description": "Generuj losowy graf k-regularny.",
            },
            "z2_6": {
                "title": "6. Graf hamiltonowski",
                "description": "Sprawdź, czy graf jest hamiltonowski.",
            },
        },
    },
    "z3": {
        "title": "Zestaw 3",
        "tasks": {
            "z3_1": {
                "title": "1. Graf spójny z losowymi wagami",
                "description": "Wygeneruj spójny graf losowy z wagami na krawędziach z zakresu 1..10.",
            },
            "z3_2": {
                "title": "2. Dijkstra",
                "description": "Zastosuj algorytm Dijkstry do znalezienia najkrótszych ścieżek od zadanego wierzchołka.",
            },
            "z3_3": {
                "title": "3. Macierz odległości",
                "description": "Wyznacz macierz odległości między wszystkimi parami wierzchołków.",
            },
            "z3_4": {
                "title": "4. Centrum i centrum minimax",
                "description": "Wyznacz centrum grafu oraz centrum minimax.",
            },
            "z3_5": {
                "title": "5. Minimalne drzewo rozpinające",
                "description": "Znajdź minimalne drzewo rozpinające.",
            },
        },
    },
}


def clean_adj(adj):
    return {v: sorted(set(nb)) for v, nb in adj.items()}


def adj_to_text(adj):
    return "\n".join(
        f"{v}: {', '.join(map(str, adj.get(v, []))) if adj.get(v) else '-'}"
        for v in sorted(adj)
    )


def matrix_to_text(matrix):
    return "\n".join(" ".join(map(str, row)) for row in matrix)


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
    params_key = f"params_{set_key}_{task_key}"
    if graph_key not in st.session_state:
        st.session_state[graph_key] = default_graph_for_task(set_key, task_key)
    if params_key not in st.session_state:
        st.session_state[params_key] = {}
    return st.session_state[graph_key], st.session_state[params_key]


def show_home():
    st.title("Grafy i ich zastosowania")
    st.caption("Wybierz zestaw, a następnie konkretne zadanie. Każde zadanie ma własne parametry i własny graf.")

    for set_key, set_data in SETS.items():
        with st.container():
            st.subheader(set_data["title"])
            cols = st.columns(3)
            items = list(set_data["tasks"].items())
            for idx, (task_key, task) in enumerate(items):
                with cols[idx % 3]:
                    st.markdown(f"**{task['title']}**")
                    st.write(task["description"])
                    if st.button(f"Otwórz {task_key}", key=f"btn_{set_key}_{task_key}"):
                        st.session_state.current_set = set_key
                        st.session_state.current_task = task_key
                        st.rerun()
            st.markdown("---")


def render_z1_1():
    set_key, task_key = "z1", "z1_1"
    graph, params = ensure_task_state(set_key, task_key)
    st.subheader("1. Kodowanie grafów i konwersja")
    st.write(SETS[set_key]["tasks"][task_key]["description"])

    n = st.number_input("Liczba wierzchołków", 2, 12, value=max(graph.keys()) if graph else 7, key=f"{task_key}_n")
    p = st.slider("Prawdopodobieństwo połączenia p", 0.0, 1.0, 0.45, 0.01, key=f"{task_key}_p")
    seed = st.number_input("Seed", 0, 1000, 4, key=f"{task_key}_seed")
    if st.button("Generuj graf", key=f"{task_key}_gen"):
        st.session_state[f"graph_{set_key}_{task_key}"] = clean_adj(gnp(n, p, seed=seed))
        graph = st.session_state[f"graph_{set_key}_{task_key}"]

    st.pyplot(render_graph(graph, title="Graf prosty"))
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Lista sąsiedztwa")
        st.code(adj_to_text(graph))
    with col2:
        st.subheader("Macierz sąsiedztwa")
        st.code(matrix_to_text(list_to_matrix({v: graph.get(v, []) for v in sorted(graph)})))

    st.subheader("Macierz incydencji")
    st.code(matrix_to_text(list_to_incidence({v: graph.get(v, []) for v in sorted(graph)})))


def render_z1_2():
    set_key, task_key = "z1", "z1_2"
    graph, _ = ensure_task_state(set_key, task_key)
    st.subheader("2. Wizualizacja na okręgu")
    st.write(SETS[set_key]["tasks"][task_key]["description"])

    n = st.number_input("Liczba wierzchołków", 3, 12, value=max(graph.keys()) if graph else 7, key=f"{task_key}_n")
    p = st.slider("Prawdopodobieństwo połączenia p", 0.0, 1.0, 0.45, 0.01, key=f"{task_key}_p")
    seed = st.number_input("Seed", 0, 1000, 3, key=f"{task_key}_seed")
    if st.button("Generuj graf", key=f"{task_key}_gen"):
        st.session_state[f"graph_{set_key}_{task_key}"] = clean_adj(gnp(n, p, seed=seed))

    graph = st.session_state[f"graph_{set_key}_{task_key}"]
    st.pyplot(render_graph(graph, title="Graf na okręgu"))
    st.code(adj_to_text(graph))


def render_z1_3():
    set_key, task_key = "z1", "z1_3"
    graph, _ = ensure_task_state(set_key, task_key)
    st.subheader("3. Grafy losowe G(n, l) i G(n, p)")
    st.write(SETS[set_key]["tasks"][task_key]["description"])

    model = st.radio("Model losowego grafu", ["G(n, p)", "G(n, l)"], key=f"{task_key}_model")
    n = st.number_input("n", 2, 20, value=7, key=f"{task_key}_n")
    p = st.slider("p", 0.0, 1.0, 0.45, 0.01, key=f"{task_key}_p")
    l = st.number_input("l", 0, 60, 10, key=f"{task_key}_l")
    seed = st.number_input("Seed", 0, 1000, 2, key=f"{task_key}_seed")
    if st.button("Generuj graf", key=f"{task_key}_gen"):
        if model == "G(n, p)":
            graph = clean_adj(gnp(n, p, seed=seed))
        else:
            graph = clean_adj(gnl(n, l, seed=seed))
        st.session_state[f"graph_{set_key}_{task_key}"] = graph

    graph = st.session_state[f"graph_{set_key}_{task_key}"]
    st.pyplot(render_graph(graph, title=f"{model}: n={n}"))
    st.code(f"Liczba krawędzi: {sum(len(v) for v in graph.values()) // 2}")
    st.code(adj_to_text(graph))


def render_z2_1():
    set_key, task_key = "z2", "z2_1"
    graph, params = ensure_task_state(set_key, task_key)
    st.subheader("1. Ciąg graficzny i konstrukcja grafu")
    st.write(SETS[set_key]["tasks"][task_key]["description"])

    seq_text = st.text_input("Ciąg stopni", value="4 2 2 3 2 1 4 2 2 2 2", key=f"{task_key}_seq")
    if st.button("Sprawdź i zbuduj graf", key=f"{task_key}_gen"):
        seq = [int(x) for x in seq_text.split() if x]
        if not is_graphic(seq):
            st.error("Ciąg nie jest graficzny.")
        else:
            graph = clean_adj(build_graph(seq))
            st.session_state[f"graph_{set_key}_{task_key}"] = graph
            st.success("Ciąg jest graficzny.")

    graph = st.session_state[f"graph_{set_key}_{task_key}"]
    st.pyplot(render_graph(graph, title="Graf z ciągu graficznego"))
    st.code(f"Stopnie: {[len(graph[v]) for v in sorted(graph)]}")
    st.code(adj_to_text(graph))


def render_z2_2():
    set_key, task_key = "z2", "z2_2"
    graph, _ = ensure_task_state(set_key, task_key)
    st.subheader("2. Randomizacja grafu o zadanych stopniach")
    st.write(SETS[set_key]["tasks"][task_key]["description"])

    swaps = st.number_input("Liczba swapów", 1, 500, 50, key=f"{task_key}_swaps")
    seed = st.number_input("Seed", 0, 10000, 7, key=f"{task_key}_seed")
    if st.button("Randomizuj graf", key=f"{task_key}_gen"):
        graph = clean_adj(randomize(graph, swaps, seed=seed))
        st.session_state[f"graph_{set_key}_{task_key}"] = graph

    graph = st.session_state[f"graph_{set_key}_{task_key}"]
    st.pyplot(render_graph(graph, title="Graf po randomizacji"))
    st.code(f"Stopnie: {[len(graph[v]) for v in sorted(graph)]}")
    st.code(adj_to_text(graph))


def render_z2_3():
    set_key, task_key = "z2", "z2_3"
    graph, _ = ensure_task_state(set_key, task_key)
    st.subheader("3. Największa spójna składowa")
    st.write(SETS[set_key]["tasks"][task_key]["description"])

    if st.button("Generuj przykładowy graf", key=f"{task_key}_gen"):
        graph = clean_adj({1: [2], 2: [1], 3: [4, 5], 4: [3], 5: [3], 6: []})
        st.session_state[f"graph_{set_key}_{task_key}"] = graph

    graph = st.session_state[f"graph_{set_key}_{task_key}"]
    comp = components(graph)
    groups = {}
    for v in sorted(comp):
        groups.setdefault(comp[v], []).append(v)
    st.write("Komponenty:")
    st.code("\n".join(f"{k}: {v}" for k, v in groups.items()))
    st.write(f"Największa składowa: {largest_component(graph)}")
    colors = {v: c for v, c in comp.items()}
    st.pyplot(render_graph(graph, title="Największa spójna składowa", colors=colors))


def render_z2_4():
    set_key, task_key = "z2", "z2_4"
    graph, _ = ensure_task_state(set_key, task_key)
    st.subheader("4. Graf eulerowski i cykl Eulera")
    st.write(SETS[set_key]["tasks"][task_key]["description"])

    n = st.number_input("n", 3, 16, value=8, key=f"{task_key}_n")
    seed = st.number_input("Seed", 0, 10000, 2, key=f"{task_key}_seed")
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
    graph, _ = ensure_task_state(set_key, task_key)
    st.subheader("5. Grafy k-regularne")
    st.write(SETS[set_key]["tasks"][task_key]["description"])

    n = st.number_input("n", 2, 20, value=8, key=f"{task_key}_n")
    k = st.number_input("k", 0, 9, value=2, key=f"{task_key}_k")
    seed = st.number_input("Seed", 0, 10000, 11, key=f"{task_key}_seed")
    if st.button("Generuj graf k-regularny", key=f"{task_key}_gen"):
        try:
            graph = clean_adj(random_k_regular(n, k, seed=seed))
            st.session_state[f"graph_{set_key}_{task_key}"] = graph
        except ValueError as exc:
            st.error(str(exc))

    graph = st.session_state[f"graph_{set_key}_{task_key}"]
    st.pyplot(render_graph(graph, title=f"Graf {k}-regularny"))
    st.code(f"Stopnie: {[len(graph[v]) for v in sorted(graph)]}")


def render_z2_6():
    set_key, task_key = "z2", "z2_6"
    graph, _ = ensure_task_state(set_key, task_key)
    st.subheader("6. Graf hamiltonowski")
    st.write(SETS[set_key]["tasks"][task_key]["description"])

    if st.button("Ustaw przykładowy graf", key=f"{task_key}_gen"):
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
    graph, _ = ensure_task_state(set_key, task_key)
    st.subheader("1. Graf spójny z losowymi wagami")
    st.write(SETS[set_key]["tasks"][task_key]["description"])

    n = st.number_input("n", 2, 20, value=8, key=f"{task_key}_n")
    p = st.slider("p", 0.0, 1.0, 0.25, 0.01, key=f"{task_key}_p")
    seed = st.number_input("Seed", 0, 10000, 3, key=f"{task_key}_seed")
    if st.button("Generuj graf ważony", key=f"{task_key}_gen"):
        edges, _ = random_connected_weighted_graph(n, p, seed=seed)
        st.session_state[f"weighted_edges_{set_key}_{task_key}"] = edges
        adj = {v: [] for v in range(1, n + 1)}
        for u, v, _ in edges:
            adj[u].append(v)
            adj[v].append(u)
        st.session_state[f"graph_{set_key}_{task_key}"] = {k: sorted(set(v)) for k, v in adj.items()}

    edges = st.session_state.get(f"weighted_edges_{set_key}_{task_key}", [])
    if edges:
        st.code("\n".join(f"{u}-{v}: {w}" for u, v, w in edges))
        graph = st.session_state[f"graph_{set_key}_{task_key}"]
        st.pyplot(render_graph(graph, title="Graf ważony"))


def render_z3_2():
    set_key, task_key = "z3", "z3_2"
    st.subheader("2. Algorytm Dijkstry")
    st.write(SETS[set_key]["tasks"][task_key]["description"])

    edges = st.session_state.get(f"weighted_edges_{set_key}_{task_key}", [])
    if not edges:
        edges, _ = random_connected_weighted_graph(6, 0.45, seed=4)
        st.session_state[f"weighted_edges_{set_key}_{task_key}"] = edges
    n = max(max(u, v) for u, v, _ in edges)
    w = [[0] * n for _ in range(n)]
    for u, v, weight in edges:
        w[u - 1][v - 1] = w[v - 1][u - 1] = weight
    graph = {v: [] for v in range(1, n + 1)}
    for u, v, _ in edges:
        graph[u].append(v)
        graph[v].append(u)
    start = st.selectbox("Wierzchołek startowy", list(range(1, n + 1)), key=f"{task_key}_start")
    if st.button("Uruchom Dijkstra", key=f"{task_key}_gen"):
        ds, ps = dijkstra(w, start - 1)
        st.code("\n".join(
            f"d({v}) = {ds[v - 1]}  ścieżka: {' -> '.join(map(str, shortest_path(ps, start - 1, v - 1)))}"
            for v in range(1, n + 1)
        ))
    st.pyplot(render_graph({k: sorted(set(v)) for k, v in graph.items()}, title="Graf do Dijkstry"))


def render_z3_3():
    set_key, task_key = "z3", "z3_3"
    st.subheader("3. Macierz odległości")
    st.write(SETS[set_key]["tasks"][task_key]["description"])
    edges = st.session_state.get(f"weighted_edges_z3_z3_1", [])
    if not edges:
        edges, _ = random_connected_weighted_graph(6, 0.45, seed=4)
        st.session_state[f"weighted_edges_z3_z3_1"] = edges
    n = max(max(u, v) for u, v, _ in edges)
    w = [[0] * n for _ in range(n)]
    for u, v, weight in edges:
        w[u - 1][v - 1] = w[v - 1][u - 1] = weight
    st.code(matrix_to_text(distance_matrix(w)))


def render_z3_4():
    set_key, task_key = "z3", "z3_4"
    st.subheader("4. Centrum i centrum minimax")
    st.write(SETS[set_key]["tasks"][task_key]["description"])
    edges = st.session_state.get(f"weighted_edges_z3_z3_1", [])
    if not edges:
        edges, _ = random_connected_weighted_graph(6, 0.45, seed=4)
        st.session_state[f"weighted_edges_z3_z3_1"] = edges
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
    st.subheader("5. Minimalne drzewo rozpinające")
    st.write(SETS[set_key]["tasks"][task_key]["description"])
    edges = st.session_state.get(f"weighted_edges_z3_z3_1", [])
    if not edges:
        edges, _ = random_connected_weighted_graph(6, 0.45, seed=4)
        st.session_state[f"weighted_edges_z3_z3_1"] = edges
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

    if st.session_state.current_set is None or st.session_state.current_task is None:
        show_home()
        return

    set_key = st.session_state.current_set
    task_key = st.session_state.current_task

    st.sidebar.title("Nawigacja")
    if st.sidebar.button("← Powrót do zestawów"):
        st.session_state.current_set = None
        st.session_state.current_task = None
        st.rerun()

    st.sidebar.write(f"Wybrany zestaw: {SETS[set_key]['title']}")
    for key, task in SETS[set_key]["tasks"].items():
        if st.sidebar.button(task["title"], key=f"sidebar_{set_key}_{key}"):
            st.session_state.current_task = key
            st.rerun()

    TASK_RENDERERS[task_key]()


if __name__ == "__main__":
    main()

