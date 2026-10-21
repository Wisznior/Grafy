import math

from grafy.common.types import AdjList


def circle_layout(n: int, r: float = 1.0, x0: float = 0.0, y0: float = 0.0):
    alpha = 2 * math.pi / n
    return [(x0 + r * math.cos(i * alpha), y0 + r * math.sin(i * alpha)) for i in range(n)]


def draw_graph_on_circle(adj: AdjList, out_path=None, weights=None, tree=None, colors=None):
    """weights: {(u,v): w} (u<v); tree: zbior (u,v) (u<v) do pogrubienia; colors: {v: nr}."""
    import matplotlib
    if out_path:
        matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    pos = circle_layout(len(adj))
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.add_patch(plt.Circle((0, 0), 1, fill=False, ls=":", color="red"))
    for u in adj:
        for v in adj[u]:
            if u < v:
                (x1, y1), (x2, y2) = pos[u - 1], pos[v - 1]
                bold = tree is not None and (u, v) in tree
                color = "blue" if bold else ("lightgray" if tree is not None else "black")
                ax.plot([x1, x2], [y1, y2], color=color, lw=2.5 if bold else 1.2, zorder=1)
                if weights:
                    ax.text((x1 + x2) / 2, (y1 + y2) / 2, str(weights[(u, v)]), fontsize=8,
                            ha="center", va="center", color=color if bold else "dimgray",
                            bbox=dict(fc="white", ec="none", pad=0.5), zorder=2)
    for i, (x, y) in enumerate(pos):
        fc = plt.cm.tab10(colors[i + 1] % 10) if colors else "#ddddff"
        ax.text(x, y, str(i + 1), ha="center", va="center", zorder=3,
                bbox=dict(boxstyle="circle", fc=fc, ec="blue"))
    ax.set_aspect("equal")
    ax.axis("off")
    if out_path:
        fig.savefig(out_path, dpi=150, bbox_inches="tight")
        plt.close(fig)
    else:
        plt.show()