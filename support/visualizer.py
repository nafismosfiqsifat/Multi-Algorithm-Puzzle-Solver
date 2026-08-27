"""Board / grid rendering for the Streamlit UI, built with matplotlib so a single
renderer handles the 8-puzzle board, the maze grid (with solution path), and the
N-Queens board.
"""

from __future__ import annotations

from typing import List, Optional, Sequence, Tuple

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from core.puzzles import EightPuzzle, Maze, NQueens


def render(puzzle, state, path: Optional[Sequence] = None) -> Figure:
    """Dispatch to the correct renderer for ``puzzle`` at ``state``.

    ``path`` (list of states) is used by the maze renderer to draw the route.
    """
    if isinstance(puzzle, EightPuzzle):
        return _render_eight(puzzle, state)
    if isinstance(puzzle, Maze):
        return _render_maze(puzzle, state, path)
    if isinstance(puzzle, NQueens):
        return _render_queens(puzzle, state)
    fig, ax = plt.subplots()
    ax.text(0.5, 0.5, puzzle.render_state(state), ha="center", va="center",
            family="monospace")
    ax.axis("off")
    return fig


def _render_eight(puzzle: EightPuzzle, state) -> Figure:
    n = puzzle.n
    fig, ax = plt.subplots(figsize=(3.2, 3.2))
    for idx, v in enumerate(state):
        r, c = divmod(idx, n)
        y = n - 1 - r
        if v == 0:
            ax.add_patch(plt.Rectangle((c, y), 1, 1, facecolor="#f0f0f0",
                                       edgecolor="#cccccc"))
            continue
        ax.add_patch(plt.Rectangle((c, y), 1, 1, facecolor="#4C78A8",
                                   edgecolor="white", linewidth=2))
        ax.text(c + 0.5, y + 0.5, str(v), ha="center", va="center",
                color="white", fontsize=20, fontweight="bold")
    ax.set_xlim(0, n)
    ax.set_ylim(0, n)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig


def _render_maze(puzzle: Maze, state, path: Optional[Sequence]) -> Figure:
    import numpy as np

    grid = np.array(puzzle.grid)
    fig, ax = plt.subplots(figsize=(4.5, 4.5))
    ax.imshow(grid, cmap="binary", origin="upper")

    if path:
        ys = [p[0] for p in path]
        xs = [p[1] for p in path]
        ax.plot(xs, ys, color="#F58518", linewidth=2.5, alpha=0.9, zorder=2)

    sr, sc = puzzle.start
    gr, gc = puzzle.goal
    ax.scatter([sc], [sr], c="#54A24B", s=140, marker="o", zorder=3, label="Start")
    ax.scatter([gc], [gr], c="#E45756", s=180, marker="*", zorder=3, label="Goal")
    if state is not None:
        ax.scatter([state[1]], [state[0]], c="#4C78A8", s=90, marker="s", zorder=4)

    ax.set_xticks([])
    ax.set_yticks([])
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.03), ncol=2, frameon=False)
    return fig


def _render_queens(puzzle: NQueens, state) -> Figure:
    n = puzzle.n
    fig, ax = plt.subplots(figsize=(4, 4))
    for r in range(n):
        for c in range(n):
            color = "#EEEEEE" if (r + c) % 2 == 0 else "#B7C7D9"
            ax.add_patch(plt.Rectangle((c, n - 1 - r), 1, 1, facecolor=color))
    for r, c in enumerate(state):
        ax.text(c + 0.5, n - 1 - r + 0.5, "♛", ha="center", va="center",
                fontsize=min(28, 220 // n), color="#22303C")
    ax.set_xlim(0, n)
    ax.set_ylim(0, n)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig
