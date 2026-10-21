from grafy.common.types import Matrix
from grafy.zestaw3.dijkstra import dijkstra


def distance_matrix(w: Matrix) -> Matrix:
    return [dijkstra(w, s)[0] for s in range(len(w))]