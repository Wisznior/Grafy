import re

import matplotlib.pyplot as plt
import streamlit as st

from grafy.common.types import AdjList, Matrix
from grafy.zestaw1.representations import (
    incidence_to_list,
    list_to_incidence,
    list_to_matrix,
    matrix_to_list,
)
from grafy.zestaw1.visualization import circle_layout


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
    fig = render_graph(st.session_state.graph, title="Graf prosty")
    st.pyplot(fig)

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

    converted = data
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

    if target == "lista":
        st.code(adj_to_text(converted))
    elif target == "matrix":
        st.code(matrix_to_text(converted))
    else:
        st.code(matrix_to_text(converted))


def task2_section() -> None:
    st.markdown("### 2. Wizualizacja grafów prostych na okręgu")
    st.write("Program do wizualizacji grafów prostych z wierzchołkami równomiernie rozmieszczonymi na okręgu.")
    fig = render_graph(DEFAULT_GRAPH, title="Wizualizacja na okręgu")
    st.pyplot(fig)


def task3_section() -> None:
    st.markdown("### 3. Generowanie grafów losowych G(n, l) oraz G(n, p)")
    st.write("Tutaj można wygenerować grafy losowe z parametrami n, l lub n, p i zobaczyć ich reprezentacje.")
    st.info("To miejsce jest gotowe do dalszego rozwinięcia o generator losowy i predefiniowane eksperymenty.")


def main() -> None:
    st.set_page_config(page_title="Grafy Lab", page_icon="📈", layout="wide")

    with st.sidebar:
        st.title("Nawigacja")
        st.caption("Zestaw 1 – Grafy i ich zastosowania")
        task = st.radio(
            "Wybierz zadanie",
            [
                "1. Kodowanie grafów i konwersja",
                "2. Wizualizacja na okręgu",
                "3. Generowanie grafów losowych",
            ],
        )

    if task == "1. Kodowanie grafów i konwersja":
        task1_section()
    elif task == "2. Wizualizacja na okręgu":
        task2_section()
    else:
        task3_section()


if __name__ == "__main__":
    main()
