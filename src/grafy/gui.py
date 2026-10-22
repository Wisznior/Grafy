import streamlit as st
import matplotlib.pyplot as plt

from grafy.common.graph import adj_to_edges, edges_to_adj
from grafy.zestaw1.random_graphs import gnl, gnp
from grafy.zestaw1.representations import (
    convert,
    list_to_incidence,
    list_to_matrix,
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


ZESTAWY = {
    "zestaw1": {
        "title": "Zestaw 1 — Grafy i ich zastosowania",
        "tasks": {
            "1": {
                "title": "1. Kodowanie grafów i konwersja reprezentacji",
                "description": "Program kodujący grafy proste za pomocą macierzy sąsiedztwa, macierzy incydencji i list sąsiedztwa. Moduł zamiany pomiędzy reprezentacjami.",
                "controls": ["liczba wierzchołków", "gęstość połączeń", "wybór reprezentacji wejściowej", "zapis rysunku"],
                "actions": ["generuj graf", "konwertuj między reprezentacjami", "wyświetl listę sąsiedztwa i macierz incydencji"],
            },
            "2": {
                "title": "2. Wizualizacja grafu na okręgu",
                "description": "Graf prosty z wierzchołkami rozłożonymi równomiernie na okręgu.",
                "controls": ["liczba wierzchołków", "prawdopodobieństwo połączeń", "kolorowanie komponentów", "opcjonalnie wagi"],
                "actions": ["narysuj graf na okręgu", "zobacz numery wierzchołków", "przełącz widok między grafami"],
            },
            "3": {
                "title": "3. Generowanie grafów losowych G(n, l) oraz G(n, p)",
                "description": "Losowe grafy ze stałą liczbą krawędzi G(n, l) oraz z prawdopodobieństwem G(n, p).",
                "controls": ["n", "l lub p", "seed", "typ modelu losowego"],
                "actions": ["wygeneruj graf", "zobacz liczbę krawędzi", "porównaj parametry"],
            },
        },
    },
    "zestaw2": {
        "title": "Zestaw 2 — Grafy i ich zastosowania",
        "tasks": {
            "1": {
                "title": "1. Ciąg graficzny i konstrukcja grafu",
                "description": "Sprawdzenie, czy sekwencja jest ciągiem graficznym i zbudowanie prostego grafu o zadanych stopniach.",
                "controls": ["ciąg liczb", "walidacja", "automatyczne tworzenie grafu"],
                "actions": ["sprawdź ciąg", "zbuduj graf", "wypisz stopnie wierzchołków"],
            },
            "2": {
                "title": "2. Randomizacja grafu o zadanych stopniach",
                "description": "Powtarzanie operacji zamieniającej ab i cd na ad i bc, zachowującej stopnie wierzchołków.",
                "controls": ["liczba swapów", "seed", "graf wejściowy"],
                "actions": ["uruchom randomizację", "porównaj stopnie przed i po", "sprawdź liczbę krawędzi"],
            },
            "3": {
                "title": "3. Największa spójna składowa",
                "description": "Znajdowanie największej składowej spójności na grafie.",
                "controls": ["graf wejściowy", "kolorowanie komponentów"],
                "actions": ["wyznacz komponenty", "podświetl największą składową", "zobacz numerację komponentów"],
            },
            "4": {
                "title": "4. Graf eulerowski i cykl Eulera",
                "description": "Generowanie losowego grafu eulerowskiego i znajdowanie cyklu Eulera.",
                "controls": ["n", "seed", "automatyczna generacja"],
                "actions": ["wygeneruj graf eulerowski", "znajdź cykl Eulera", "zobacz poprawność przejścia po każdej krawędzi"],
            },
            "5": {
                "title": "5. Grafy k-regularne",
                "description": "Generowanie losowych grafów k-regularnych.",
                "controls": ["n", "k", "seed"],
                "actions": ["wygeneruj graf k-regularny", "sprawdź stopnie wierzchołków", "zobacz wizualizację"],
            },
            "6": {
                "title": "6. Graf hamiltonowski",
                "description": "Sprawdzanie (dla małych grafów), czy graf jest hamiltonowski.",
                "controls": ["graf wejściowy", "opcja automatycznego generowania"],
                "actions": ["sprawdź hamiltonowość", "znajdź cykl Hamiltona", "zobacz rezultat dla grafu pełnego lub gwiaździstego"],
            },
        },
    },
    "zestaw3": {
        "title": "Zestaw 3 — Grafy i ich zastosowania",
        "tasks": {
            "1": {
                "title": "1. Losowy graf spójny z wagami na krawędziach",
                "description": "Generowanie spójnego grafu losowego z losowymi wagami od 1 do 10 na każdej krawędzi.",
                "controls": ["n", "p", "seed", "wagi"],
                "actions": ["wygeneruj graf ważony", "pokaż wagi krawędzi", "zaznacz graf na okręgu"],
            },
            "2": {
                "title": "2. Algorytm Dijkstry",
                "description": "Znajdowanie najkrótszych ścieżek od zadanego wierzchołka do pozostałych wierzchołków.",
                "controls": ["wybór wierzchołka startowego", "graf ważony"],
                "actions": ["uruchom Dijkstrę", "pokaż odległości", "wyświetl najkrótsze ścieżki"],
            },
            "3": {
                "title": "3. Macierz odległości",
                "description": "Obliczanie odległości między wszystkimi parami wierzchołków.",
                "controls": ["graf ważony"],
                "actions": ["wyznacz macierz odległości", "zobacz odległości w tabeli"],
            },
            "4": {
                "title": "4. Centrum i centrum minimax",
                "description": "Wyznaczanie centrum grafu oraz centrum minimax.",
                "controls": ["graf ważony"],
                "actions": ["policz sumę odległości", "wyznacz centrum", "wyznacz centrum minimax"],
            },
            "5": {
                "title": "5. Minimalne drzewo rozpinające",
                "description": "Wyznaczanie MST algorytmem Prima lub Kruskala.",
                "controls": ["graf ważony"],
                "actions": ["policz MST", "podświetl krawędzie drzewa", "zobacz łączną wagę"],
            },
        },
    },
}


def _clean_adj(adj):
    return {v: sorted(set(nb)) for v, nb in adj.items()}


def _adj_to_text(adj):
    return "\n".join(f"{v}: {', '.join(map(str, adj.get(v, []))) if adj.get(v) else '-'}" for v in sorted(adj))


def _matrix_to_text(mat):
    return "\n".join(" ".join(str(x) for x in row) for row in mat)


def _make_default_adj(n=7, p=0.45, seed=4):
    return _clean_adj(gnp(n, p, seed=seed))


def _render_graph(adj, title="Graf", weights=None, tree_edges=None, colors=None):
    fig, ax = plt.subplots(figsize=(7, 7))
    pos = circle_layout(len(adj))
    for u in sorted(adj):
        for v in sorted(adj[u]):
            if u < v:
                (x1, y1), (x2, y2) = pos[u - 1], pos[v - 1]
                is_tree = bool(tree_edges and (min(u, v), max(u, v)) in tree_edges)
                color = "#2c7be5" if is_tree else "#4a5568"
                lw = 3.0 if is_tree else 1.8
                ax.plot([x1, x2], [y1, y2], color=color, lw=lw)
                if weights and (min(u, v), max(u, v)) in weights:
                    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
                    ax.text(mx, my, str(weights[(min(u, v), max(u, v))]), fontsize=9, ha="center", va="center",
                            bbox={"boxstyle": "round,pad=0.25", "fc": "white", "ec": "none"})
    for idx, (x, y) in enumerate(pos, start=1):
        clr = plt.cm.tab10(colors[idx] % 10) if colors else "#dfe8ff"
        ax.text(x, y, str(idx), ha="center", va="center", fontsize=11,
                bbox={"boxstyle": "circle,pad=0.35", "fc": clr, "ec": "#2c7be5"})
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, pad=18)
    return fig


def _build_graph_from_sequence(seq_text):
    seq = [int(x) for x in seq_text.split() if x]
    if not seq:
        st.warning("Wprowadź ciąg liczb dla zadania o ciągu graficznym.")
        return None
    if not is_graphic(seq):
        st.warning("Podany ciąg nie jest graficzny.")
        return None
    return _clean_adj(build_graph(seq))


def _graph_from_random_model(model, n, p, l, k, seed):
    if model == "G(n, p)":
        return _clean_adj(gnp(n, p, seed=seed))
    if model == "G(n, l)":
        return _clean_adj(gnl(n, l, seed=seed))
    if model == "k-regular":
        return _clean_adj(random_k_regular(n, k, seed=seed))
    return _make_default_adj(n=n, p=p, seed=seed)


def _show_home_page():
    st.title("Grafy i ich zastosowania")
    st.caption("Wybierz zestaw i konkretne zadanie, aby uruchomić odpowiednią analizę i wizualizację.")
    for key, value in ZESTAWY.items():
        st.markdown(f"### {value['title']}")
        cols = st.columns(3)
        tasks = list(value["tasks"].items())
        for i, (task_key, task) in enumerate(tasks):
            with cols[i % 3]:
                st.markdown(f"**{task['title']}**")
                st.write(task["description"])
                st.markdown("Co można zmieniać:")
                st.write("• " + "\n• ".join(task["controls"]))
                st.markdown("Co można uruchomić:")
                st.write("• " + "\n• ".join(task["actions"]))
                if st.button(f"Otwórz {key} / {task_key}", key=f"open_{key}_{task_key}"):
                    st.session_state.current_set = key
                    st.session_state.current_task = task_key
                    st.rerun()
        st.markdown("---")


def _show_zestaw_page(key):
    set_data = ZESTAWY[key]
    st.title(set_data["title"])
    tasks = list(set_data["tasks"].items())
    selected = st.selectbox("Wybierz zadanie", [f"{task_key}: {task['title']}" for task_key, task in tasks], index=0)
    current_key = selected.split(":", 1)[0]
    task = set_data["tasks"][current_key]

    st.subheader(task["title"])
    st.write(task["description"])
    st.markdown("**Co można zmieniać:**")
    st.write("• " + "\n• ".join(task["controls"]))
    st.markdown("**Co można uruchomić:**")
    st.write("• " + "\n• ".join(task["actions"]))

    if key == "zestaw1":
        _show_zestaw1_task(current_key)
    elif key == "zestaw2":
        _show_zestaw2_task(current_key)
    elif key == "zestaw3":
        _show_zestaw3_task(current_key)


def _show_zestaw1_task(task_key):
    if "graph" not in st.session_state:
        st.session_state.graph = _make_default_adj()

    st.markdown("---")
    n = st.number_input("Liczba wierzchołków", min_value=2, max_value=12, value=len(st.session_state.graph), key="z1_n")
    p = st.slider("Prawdopodobieństwo połączenia p", 0.0, 1.0, 0.45, 0.01, key="z1_p")
    seed = st.number_input("Seed", min_value=0, max_value=1000, value=4, key="z1_seed")
    model = st.radio("Typ modelu losowego", ["G(n, p)", "G(n, l)"], key="z1_model")
    l = st.number_input("Liczba krawędzi l", min_value=0, max_value=50, value=10, key="z1_l")

    if st.button("Wygeneruj graf", key="z1_generate"):
        if model == "G(n, p)":
            st.session_state.graph = _clean_adj(gnp(n, p, seed=seed))
        else:
            st.session_state.graph = _clean_adj(gnl(n, l, seed=seed))

    graph = st.session_state.graph
    fig = _render_graph(graph, title="Graf prosty")
    st.pyplot(fig)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Lista sąsiedztwa")
        st.code(_adj_to_text(graph))
    with col2:
        st.subheader("Macierz sąsiedztwa")
        st.code(_matrix_to_text(list_to_matrix({v: graph.get(v, []) for v in sorted(graph)})))

    st.subheader("Macierz incydencji")
    st.code(_matrix_to_text(list_to_incidence({v: graph.get(v, []) for v in sorted(graph)})))

    if task_key == "1":
        st.info("Tutaj możesz zmieniać liczbę wierzchołków, gęstość połączeń oraz typ modelu, a następnie szybko sprawdzić konwersję między reprezentacjami.")
    elif task_key == "2":
        st.info("Wizualizacja na okręgu: wierzchołki są rozłożone równomiernie, dzięki czemu łatwo analizować strukturę grafu.")
    elif task_key == "3":
        st.info("Przełączaj się między G(n, p) i G(n, l), zmieniając parametry i obserwując różnicę w strukturze losowego grafu.")


def _show_zestaw2_task(task_key):
    if task_key == "1":
        seq_text = st.text_input("Ciąg stopni wierzchołków", value="4 2 2 3 2 1 4 2 2 2 2", key="z2_seq")
        if st.button("Sprawdź ciąg i zbuduj graf", key="z2_check_seq"):
            seq = [int(x) for x in seq_text.split() if x]
            if is_graphic(seq):
                graph = _clean_adj(build_graph(seq))
                st.session_state.graph = graph
                st.success(f"Ciąg jest graficzny. Liczba wierzchołków: {len(graph)}")
            else:
                st.error("Ciąg nie jest graficzny.")
        graph = st.session_state.get("graph", _make_default_adj())
        st.pyplot(_render_graph(graph, title="Graf z ciągu graficznego"))
        st.code(_adj_to_text(graph))

    elif task_key == "2":
        base = st.session_state.get("graph", _make_default_adj())
        swaps = st.number_input("Liczba randomizacji", min_value=1, max_value=500, value=50, key="z2_swaps")
        seed = st.number_input("Seed", min_value=0, max_value=10000, value=5, key="z2_seed")
        if st.button("Zrandomizuj graf", key="z2_randomize"):
            graph = _clean_adj(randomize(base, swaps, seed=seed))
            st.session_state.graph = graph
            st.success("Graf zrandomizowany.")
        graph = st.session_state.get("graph", base)
        st.pyplot(_render_graph(graph, title="Graf po randomizacji"))
        st.code(f"Stopnie: {[len(graph[v]) for v in sorted(graph)]}")

    elif task_key == "3":
        graph = st.session_state.get("graph", _make_default_adj())
        comp = components(graph)
        groups = {}
        for v in sorted(comp):
            groups.setdefault(comp[v], []).append(v)
        st.write("Komponenty spójności:")
        st.code("\n".join(f"{k}: {v}" for k, v in groups.items()))
        st.write(f"Największa składowa: {largest_component(graph)}")
        colors = {v: idx for v, idx in comp.items()}
        st.pyplot(_render_graph(graph, title="Składowe spójności", colors=colors))

    elif task_key == "4":
        n = st.number_input("n", min_value=3, max_value=20, value=8, key="z2_euler_n")
        seed = st.number_input("Seed", min_value=0, max_value=10000, value=1, key="z2_euler_seed")
        if st.button("Generuj graf eulerowski", key="z2_euler_generate"):
            graph = random_eulerian_graph(n, seed=seed)
            st.session_state.graph = graph
        graph = st.session_state.get("graph", random_eulerian_graph(8, seed=1))
        try:
            cycle = euler_cycle(graph)
            st.success("Cykl Eulera znaleziony.")
            st.code(" -> ".join(map(str, cycle)))
        except ValueError:
            st.warning("Graf nie jest eulerowski.")
        st.pyplot(_render_graph(graph, title="Graf eulerowski"))

    elif task_key == "5":
        n = st.number_input("n", min_value=2, max_value=20, value=8, key="z2_kreg_n")
        k = st.number_input("k", min_value=0, max_value=10, value=2, key="z2_kreg_k")
        if st.button("Generuj graf k-regularny", key="z2_kreg_generate"):
            try:
                graph = _clean_adj(random_k_regular(n, k, seed=7))
                st.session_state.graph = graph
                st.success("Graf k-regularny wygenerowany.")
            except ValueError as exc:
                st.error(str(exc))
        graph = st.session_state.get("graph", _clean_adj(random_k_regular(8, 2, seed=7)))
        st.pyplot(_render_graph(graph, title="Graf k-regularny"))
        st.code(f"Stopnie: {[len(graph[v]) for v in sorted(graph)]}")

    elif task_key == "6":
        graph = st.session_state.get("graph", {1: [2, 3], 2: [1, 3], 3: [1, 2]})
        if st.button("Sprawdź Hamiltonowość", key="z2_ham_check"):
            cycle = hamilton_cycle(graph)
            if cycle:
                st.success("Graf jest hamiltonowski.")
                st.code(" -> ".join(map(str, cycle)))
            else:
                st.warning("Graf nie jest hamiltonowski.")
        st.pyplot(_render_graph(graph, title="Graf do sprawdzenia Hamiltonowości"))



def _show_zestaw3_task(task_key):
    if task_key == "1":
        n = st.number_input("n", min_value=2, max_value=20, value=8, key="z3_gen_n")
        p = st.slider("p", 0.0, 1.0, 0.25, 0.01, key="z3_gen_p")
        seed = st.number_input("Seed", min_value=0, max_value=10000, value=3, key="z3_gen_seed")
        if st.button("Wygeneruj graf ważony", key="z3_gen_button"):
            edges, _ = random_connected_weighted_graph(n, p, seed=seed)
            st.session_state.weighted_edges = edges
            st.session_state.graph = {v: [] for v in range(1, n + 1)}
            for u, v, _ in edges:
                st.session_state.graph.setdefault(u, []).append(v)
                st.session_state.graph.setdefault(v, []).append(u)
        edges = st.session_state.get("weighted_edges", [])
        if edges:
            st.code("\n".join(f"{u}-{v}: {w}" for u, v, w in edges))
            adj = {v: [] for v in range(1, max(max(u, v) for u, v, _ in edges) + 1)}
            for u, v, _ in edges:
                adj[u].append(v)
                adj[v].append(u)
            st.pyplot(_render_graph(adj, title="Graf ważony"))

    elif task_key == "2":
        edges = st.session_state.get("weighted_edges", [])
        if not edges:
            edges, _ = random_connected_weighted_graph(6, 0.45, seed=4)
        n = max(max(u, v) for u, v, _ in edges)
        w = [[0] * n for _ in range(n)]
        for u, v, weight in edges:
            w[u - 1][v - 1] = w[v - 1][u - 1] = weight
        start = st.selectbox("Wierzchołek startowy", list(range(1, n + 1)), key="z3_dijkstra_start")
        if st.button("Uruchom Dijkstrę", key="z3_dijkstra_run"):
            ds, ps = dijkstra(w, start - 1)
            st.code("\n".join(f"d({v}) = {ds[v-1]}  ścieżka: {' -> '.join(map(str, shortest_path(ps, start - 1, v - 1)))}" for v in range(1, n + 1)))
        adj = {v: [] for v in range(1, n + 1)}
        for u, v, _ in edges:
            adj[u].append(v)
            adj[v].append(u)
        st.pyplot(_render_graph(adj, title="Graf do Dijkstry"))

    elif task_key == "3":
        edges = st.session_state.get("weighted_edges", [])
        if not edges:
            edges, _ = random_connected_weighted_graph(6, 0.45, seed=4)
        n = max(max(u, v) for u, v, _ in edges)
        w = [[0] * n for _ in range(n)]
        for u, v, weight in edges:
            w[u - 1][v - 1] = w[v - 1][u - 1] = weight
        mat = distance_matrix(w)
        st.code(_matrix_to_text(mat))

    elif task_key == "4":
        edges = st.session_state.get("weighted_edges", [])
        if not edges:
            edges, _ = random_connected_weighted_graph(6, 0.45, seed=4)
        n = max(max(u, v) for u, v, _ in edges)
        w = [[0] * n for _ in range(n)]
        for u, v, weight in edges:
            w[u - 1][v - 1] = w[v - 1][u - 1] = weight
        dist = distance_matrix(w)
        center_id, center_sum = center(dist)
        minimax_id, minimax_dist = minimax_center(dist)
        st.write(f"Centrum: {center_id + 1} (suma odległości = {center_sum})")
        st.write(f"Centrum minimax: {minimax_id + 1} (najdalsza odległość = {minimax_dist})")
        st.code(_matrix_to_text(dist))

    elif task_key == "5":
        edges = st.session_state.get("weighted_edges", [])
        if not edges:
            edges, _ = random_connected_weighted_graph(6, 0.45, seed=4)
        n = max(max(u, v) for u, v, _ in edges)
        mst = minimum_spanning_tree(n, edges)
        st.write(f"Waga MST = {sum(weight for *_, weight in mst)}")
        st.code("\n".join(f"{u}-{v}: {w}" for u, v, w in mst))
        tree_edges = {(min(u, v), max(u, v)) for u, v, _ in mst}
        adj = {v: [] for v in range(1, n + 1)}
        for u, v, _ in edges:
            adj[u].append(v)
            adj[v].append(u)
        st.pyplot(_render_graph(adj, title="Minimalne drzewo rozpinające", tree_edges=tree_edges))


def main():
    st.set_page_config(page_title="Grafy Lab", page_icon="📈", layout="wide")

    if "current_set" not in st.session_state:
        st.session_state.current_set = "home"
    if "current_task" not in st.session_state:
        st.session_state.current_task = "1"
    if "graph" not in st.session_state:
        st.session_state.graph = _make_default_adj()

    with st.sidebar:
        st.title("Menu")
        choice = st.radio("Wybierz sekcję", ["Strona główna", *[f"Zestaw {idx}" for idx in range(1, 4)]])
        if choice == "Strona główna":
            st.session_state.current_set = "home"
        else:
            st.session_state.current_set = f"zestaw{choice.split()[-1]}"

    if st.session_state.current_set == "home":
        _show_home_page()
    else:
        _show_zestaw_page(st.session_state.current_set)


if __name__ == "__main__":
    main()
