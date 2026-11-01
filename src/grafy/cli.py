"""python -m grafy <komenda> ...  (wierzcholki od 1)."""
import argparse
from pathlib import Path

from grafy.common import io
from grafy.common.graph import edges_to_adj
from grafy.zestaw1 import representations as rep
from grafy.zestaw1.random_graphs import gnl, gnp
from grafy.zestaw1.visualization import draw_graph_on_circle
from grafy.zestaw2.components import components
from grafy.zestaw2.degree_sequence import build_graph, is_graphic
from grafy.zestaw2.euler import euler_cycle, random_eulerian_graph
from grafy.zestaw2.hamilton import hamilton_cycle
from grafy.zestaw2.randomization import randomize
from grafy.zestaw2.regular import random_k_regular
from grafy.zestaw3.centers import center, minimax_center
from grafy.zestaw3.dijkstra import dijkstra, shortest_path
from grafy.zestaw3.distances import distance_matrix
from grafy.zestaw3.mst import minimum_spanning_tree
from grafy.zestaw3.weighted_graph import (edges_to_matrix, random_connected_weighted_graph,
                                          read_weighted_edges)
from grafy.zestaw4.bellman_ford import bellman_ford
from grafy.zestaw4.directed_graph import (adjacency_matrix, gnp_digraph, incidence_matrix,
                                          random_strongly_connected_weighted_digraph)
from grafy.zestaw4.johnson import johnson
from grafy.zestaw4.scc import strongly_connected_components
from grafy.zestaw5.flow_network import draw_flow_network, random_flow_network
from grafy.zestaw5.max_flow import ford_fulkerson
from grafy.zestaw6.pagerank import (pagerank_power_iteration, pagerank_random_walk,
                                    ranking, read_digraph)
from grafy.zestaw6.tsp import draw_tour, read_points, simulated_annealing, tour_length

READ = {"matrix": io.read_adjacency_matrix, "list": io.read_adjacency_list,
        "incidence": io.read_incidence_matrix}
NAMES = {"matrix": "Macierz sasiedztwa", "list": "Lista sasiedztwa", "incidence": "Macierz incydencji"}


def show(adj, draw=None, **kw):
    print(io.format_adjacency_list(adj))
    if draw:
        draw_graph_on_circle(adj, draw, **kw)
        print("Rysunek:", draw)


def load(a):
    if a.seq:
        return build_graph(a.seq)
    if not a.file:
        raise SystemExit("podaj --file PLIK [--from matrix|list|incidence] albo --seq 4 2 2 ...")
    return rep.convert(READ[a.fmt](a.file), a.fmt, "list")


def cmd_convert(a):
    data = READ[a.fmt](a.file)
    for k in NAMES:
        if k != a.fmt:
            out = rep.convert(data, a.fmt, k)
            print(f"{NAMES[k]}:\n" + (io.format_adjacency_list(out) if k == "list" else io.format_matrix(out)))
    if a.draw:
        draw_graph_on_circle(rep.convert(data, a.fmt, "list"), a.draw)
        print("Rysunek:", a.draw)


def cmd_graphic(a):
    ok = is_graphic(a.seq)
    print("Ciag graficzny:", "TAK" if ok else "NIE")
    if ok:
        show(build_graph(a.seq), a.draw)


def cmd_components(a):
    adj = load(a)
    comp = components(adj)
    groups = {}
    for v in sorted(comp):
        groups.setdefault(comp[v], []).append(v)
    for nr, vs in groups.items():
        print(f"{nr}) " + " ".join(map(str, vs)))
    print(f"Najwieksza skladowa ma numer {max(groups, key=lambda k: len(groups[k]))}.")
    if a.draw:
        draw_graph_on_circle(adj, a.draw, colors=comp)


def cmd_euler(a):
    adj = random_eulerian_graph(a.n, a.seed)
    print("Stopnie:", " ".join(str(len(adj[v])) for v in sorted(adj)))
    show(adj, a.draw)
    print("Cykl Eulera: [" + " - ".join(map(str, euler_cycle(adj))) + "]")


def cmd_hamilton(a):
    adj = load(a)
    cyc = hamilton_cycle(adj)
    print("Cykl Hamiltona: [" + " - ".join(map(str, cyc)) + "]" if cyc else "Graf NIE jest hamiltonowski")
    if a.draw:
        draw_graph_on_circle(adj, a.draw)


def cmd_set3(a):
    if a.edges:
        n, edges = read_weighted_edges(a.edges)
    else:
        n = a.n
        edges, _ = random_connected_weighted_graph(n, a.p, seed=a.seed)
    w = edges_to_matrix(n, edges)
    print("Krawedzie (u v waga):")
    for u, v, x in edges:
        print(u, v, x)
    s = a.s - 1
    ds, ps = dijkstra(w, s)
    print(f"START: s = {a.s}")
    for v in range(n):
        print(f"d({v + 1}) = {ds[v]} ==> [" + " - ".join(str(x + 1) for x in shortest_path(ps, s, v)) + "]")
    d = distance_matrix(w)
    print("Macierz odleglosci:\n" + io.format_matrix(d))
    c, cs = center(d)
    m, mf = minimax_center(d)
    print(f"Centrum = {c} (suma odleglosci: {cs})")
    print(f"Centrum minimax = {m} (odleglosc od najdalszego: {mf})")
    tree = minimum_spanning_tree(n, edges)
    print("MST: " + " ".join(f"{u}-{v}" for u, v, _ in tree) + f", suma wag = {sum(x for *_, x in tree)}")
    if a.draw:
        key = lambda u, v: (min(u, v), max(u, v))
        draw_graph_on_circle(edges_to_adj(n, [(u, v) for u, v, _ in edges]), a.draw,
                             weights={key(u, v): x for u, v, x in edges},
                             tree={key(u, v) for u, v, _ in tree})
        print("Rysunek:", a.draw)


def cmd_digraph(a):
    graph = gnp_digraph(a.n, a.p, a.seed)
    print("Lista sasiedztwa:")
    for u, neighbors in graph.items():
        print(f"{u}: " + (" ".join(map(str, neighbors)) if neighbors else "-"))
    print("Macierz sasiedztwa:\n" + io.format_matrix(adjacency_matrix(graph)))
    print("Macierz incydencji (-1 zrodlo, +1 cel):\n" +
          io.format_matrix(incidence_matrix(graph)))
    print("Silnie spojne skladowe:")
    for number, component in enumerate(strongly_connected_components(graph), 1):
        print(f"{number}) " + " ".join(map(str, component)))


def cmd_set4(a):
    graph, arcs = random_strongly_connected_weighted_digraph(a.n, a.p, a.seed)
    print("Losowy silnie spojny digraf (luki u v waga):")
    for u, v, weight in arcs:
        print(u, v, weight)
    print("Silnie spojne skladowe:")
    for number, component in enumerate(strongly_connected_components(graph), 1):
        print(f"{number}) " + " ".join(map(str, component)))
    distances, _ = bellman_ford(a.n, arcs, a.source)
    print(f"Bellman-Ford od wierzcholka {a.source}:")
    for vertex in range(1, a.n + 1):
        print(f"d({vertex}) = {distances[vertex]}")
    print("Macierz odleglosci Johnsona:\n" + io.format_matrix(johnson(a.n, arcs)))


def _project_file(*parts):
    return Path(__file__).resolve().parents[2].joinpath(*parts)


def cmd_set5(a):
    network = random_flow_network(a.layers, a.seed)
    result = ford_fulkerson(network)
    label = lambda vertex: "s" if vertex == network.source else (
        "t" if vertex == network.sink else str(vertex))
    print("Zrodlo: s, ujscie: t")
    print("Luki (u v przeplyw/przepustowosc):")
    for (u, v), capacity in sorted(network.capacities.items()):
        print(f"{label(u)} {label(v)} {result.flows[(u, v)]}/{capacity}")
    print("Sciezki powiekszajace (w kolejnosci znalezienia):")
    for path, amount in result.augmentations:
        print(" ".join(map(label, path)), f"(+{amount})")
    print(f"Maksymalny przeplyw: {result.value}")
    draw_flow_network(network, a.draw, result.flows)
    print("Rysunek:", a.draw)


def cmd_set6(a):
    graph_path = Path(a.graph_file) if a.graph_file else _project_file(
        "data", "examples", "zestaw6", "pagerank_graph.txt")
    points_path = Path(a.points_file) if a.points_file else _project_file(
        "data", "examples", "zestaw6", "tsp_points.txt")
    graph = read_digraph(graph_path)
    walk_scores = pagerank_random_walk(graph, a.damping, a.walk_steps, a.seed)
    power_scores, iterations = pagerank_power_iteration(graph, a.damping)
    print(f"PageRank: bledzenie losowe, krokow = {a.walk_steps}")
    for node, score in ranking(walk_scores):
        print(f"{node} -> PageRank = {score:.6f}")
    print(f"PageRank: iteracja potegowa, iteracji = {iterations}")
    for node, score in ranking(power_scores):
        print(f"{node} -> PageRank = {score:.6f}")

    points = read_points(points_path)
    initial = list(range(len(points)))
    initial_length = tour_length(points, initial)
    tour, length = simulated_annealing(points, a.iterations,
                                       None if a.seed is None else a.seed + 1,
                                       initial_tour=initial)
    print(f"TSP: {len(points)} punktow, dlugosc poczatkowa = {initial_length:.3f}")
    print(f"Dlugosc znalezionej trasy = {length:.3f}")
    print("Kolejnosc wierzcholkow (indeksy od 1): " +
          " ".join([*(str(vertex + 1) for vertex in tour), str(tour[0] + 1)]))
    draw_tour(points, tour, a.draw)
    print("Rysunek:", a.draw)


def build_parser():
    p = argparse.ArgumentParser(prog="grafy")
    sub = p.add_subparsers(dest="cmd", required=True)

    def add(name, fn, draw=True, seed=False, source=False):
        sp = sub.add_parser(name)
        sp.set_defaults(run=fn)
        if draw:
            sp.add_argument("--draw", metavar="PLIK.png")
        if seed:
            sp.add_argument("--seed", type=int)
        if source:
            sp.add_argument("--file")
            sp.add_argument("--from", dest="fmt", choices=READ, default="matrix")
            sp.add_argument("--seq", type=int, nargs="+", help="ciag graficzny zamiast pliku")
        return sp

    sp = add("convert", cmd_convert)
    sp.add_argument("file")
    sp.add_argument("--from", dest="fmt", choices=READ, required=True)

    sp = add("gnl", lambda a: show(gnl(a.n, a.l, a.seed), a.draw), seed=True)
    sp.add_argument("n", type=int)
    sp.add_argument("l", type=int)
    sp = add("gnp", lambda a: show(gnp(a.n, a.p, a.seed), a.draw), seed=True)
    sp.add_argument("n", type=int)
    sp.add_argument("p", type=float)

    sp = add("graphic", cmd_graphic)
    sp.add_argument("seq", type=int, nargs="+")
    sp = add("randomize", lambda a: show(randomize(load(a), a.k, a.seed), a.draw), seed=True, source=True)
    sp.add_argument("k", type=int, help="liczba randomizacji")
    add("components", cmd_components, source=True)
    sp = add("euler", cmd_euler, seed=True)
    sp.add_argument("--n", type=int)
    sp = add("kregular", lambda a: show(random_k_regular(a.n, a.k, a.seed), a.draw), seed=True)
    sp.add_argument("n", type=int)
    sp.add_argument("k", type=int)
    add("hamilton", cmd_hamilton, source=True)

    sp = add("set3", cmd_set3, seed=True)
    sp.add_argument("--n", type=int, default=12)
    sp.add_argument("--p", type=float, default=0.3)
    sp.add_argument("--s", type=int, default=1, help="wierzcholek startowy Dijkstry")
    sp.add_argument("--edges", help="plik 'u v waga' zamiast grafu losowego")

    sp = add("digraph", cmd_digraph, seed=True)
    sp.add_argument("n", type=int)
    sp.add_argument("p", type=float)

    sp = add("set4", cmd_set4, draw=False, seed=True)
    sp.add_argument("--n", type=int, default=12)
    sp.add_argument("--p", type=float, default=0.25)
    sp.add_argument("--source", type=int, default=1)

    sp = add("set5", cmd_set5, draw=False, seed=True)
    sp.add_argument("--layers", type=int, default=3, help="liczba warstw posrednich N (N >= 2)")
    sp.add_argument("--draw", default="output/zestaw5_flow.png", metavar="PLIK.png")

    sp = add("set6", cmd_set6, draw=False, seed=True)
    sp.add_argument("--graph-file", help="lista sasiedztwa w formacie 'wierzcholek: sasiedzi'")
    sp.add_argument("--points-file", help="plik z dwiema wspolrzednymi na wiersz")
    sp.add_argument("--damping", type=float, default=0.15)
    sp.add_argument("--walk-steps", type=int, default=1_000_000)
    sp.add_argument("--iterations", type=int, default=200_000, help="liczba prob 2-opt")
    sp.add_argument("--draw", default="output/zestaw6_tsp.png", metavar="PLIK.png")
    return p


def main(argv=None):
    a = build_parser().parse_args(argv)
    a.run(a)
    return 0
