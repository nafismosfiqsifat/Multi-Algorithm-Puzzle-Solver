"""Heuristics for grid pathfinding. A state is a ``(row, col)`` cell; the goal is
a fixed target cell captured via a closure in :func:`for_goal`.

* **Manhattan** — admissible & consistent for 4-connected grids (unit cost).
* **Euclidean** — admissible & consistent; a lower bound on any grid path.
* **Chebyshev (Diagonal)** — admissible & consistent when diagonal moves are
  allowed (also unit cost); on a 4-connected grid it is still admissible but
  weaker than Manhattan.
"""

from __future__ import annotations

from math import sqrt
from typing import Callable, Dict, Tuple

Cell = Tuple[int, int]


def for_goal(goal: Cell) -> Dict[str, Callable[[Cell], float]]:
    gr, gc = goal

    def manhattan(cell: Cell) -> float:
        return float(abs(cell[0] - gr) + abs(cell[1] - gc))

    def euclidean(cell: Cell) -> float:
        return sqrt((cell[0] - gr) ** 2 + (cell[1] - gc) ** 2)

    def chebyshev(cell: Cell) -> float:
        return float(max(abs(cell[0] - gr), abs(cell[1] - gc)))

    return {
        "Manhattan Distance": manhattan,
        "Euclidean Distance": euclidean,
        "Chebyshev (Diagonal)": chebyshev,
    }


def info() -> Dict[str, str]:
    return {
        "Manhattan Distance": "Admissible & consistent on 4-connected grids; exact when no walls block the direct L-path.",
        "Euclidean Distance": "Admissible & consistent; straight-line lower bound, mildly under-estimates on grid moves.",
        "Chebyshev (Diagonal)": "Admissible & consistent when 8-connected; on 4-connected grids it under-estimates more, so it expands more nodes.",
    }
