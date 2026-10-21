from grafy.common.types import Matrix


def center(d: Matrix) -> tuple[int, int]:
    """(wierzcholek od 1, suma odleglosci do pozostalych)."""
    sums = [sum(r) for r in d]
    return sums.index(min(sums)) + 1, min(sums)


def minimax_center(d: Matrix) -> tuple[int, int]:
    """(wierzcholek od 1, odleglosc do najdalszego)."""
    far = [max(r) for r in d]
    return far.index(min(far)) + 1, min(far)