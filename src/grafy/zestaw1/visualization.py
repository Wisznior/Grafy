"""Z1.2 - wizualizacja grafu na okregu (2 pkt).

alpha = 2*pi/n;  x_i = x0 + r*cos(i*alpha);  y_i = y0 + r*sin(i*alpha)
Zalezy od: Z1.1 (reprezentacje).
"""
from __future__ import annotations

from grafy.common.types import AdjList


def circle_layout(n: int, r: float = 1.0, x0: float = 0.0, y0: float = 0.0) -> list[tuple[float, float]]:
    raise NotImplementedError


def draw_graph_on_circle(adj: AdjList, out_path: str | None = None) -> None:
    raise NotImplementedError
