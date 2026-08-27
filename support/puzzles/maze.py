"""Grid maze / pathfinding.

State  : (row, col) cell.
Actions: 4-connected ("N","S","E","W") or 8-connected (adds diagonals).
Goal   : reach the target cell.
Cost   : 1 for orthogonal moves; sqrt(2) for diagonal moves (8-connected), so UCS
         and A* stay meaningful and diagonal shortcuts are priced correctly.
"""

from __future__ import annotations

import random
from math import sqrt
from typing import Callable, Dict, List, Tuple

from core.heuristics import maze_heuristics as H
from core.puzzle_base import Puzzle

Cell = Tuple[int, int]

_ORTHO = {"N": (-1, 0), "S": (1, 0), "W": (0, -1), "E": (0, 1)}
_DIAG = {"NW": (-1, -1), "NE": (-1, 1), "SW": (1, -1), "SE": (1, 1)}
_DIAG_COST = sqrt(2)


class Maze(Puzzle):
    name = "Maze"

    def __init__(self, grid: List[List[int]], start: Cell, goal: Cell,
                 allow_diagonal: bool = False):
        """``grid[r][c] == 1`` marks a wall, ``0`` a free cell."""
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0]) if grid else 0
        self.start = start
        self.goal = goal
        self.allow_diagonal = allow_diagonal
        self._moves = dict(_ORTHO)
        if allow_diagonal:
            self._moves.update(_DIAG)
        self._validate()

    def _validate(self) -> None:
        for label, cell in (("start", self.start), ("goal", self.goal)):
            r, c = cell
            if not (0 <= r < self.rows and 0 <= c < self.cols):
                raise ValueError(f"{label} {cell} is outside the {self.rows}x{self.cols} grid.")
            if self.grid[r][c] == 1:
                raise ValueError(f"{label} {cell} is on a wall.")

    # --- interface -------------------------------------------------------

    def get_initial_state(self) -> Cell:
        return self.start

    def get_actions(self, state: Cell) -> List[str]:
        r, c = state
        actions = []
        for name, (dr, dc) in self._moves.items():
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.rows and 0 <= nc < self.cols and self.grid[nr][nc] == 0:
                # Block diagonal moves that cut through two wall corners.
                if name in _DIAG and (self.grid[r][nc] == 1 and self.grid[nr][c] == 1):
                    continue
                actions.append(name)
        return actions

    def apply_action(self, state: Cell, action: str) -> Cell:
        dr, dc = self._moves[action]
        return (state[0] + dr, state[1] + dc)

    def step_cost(self, state: Cell, action: str) -> float:
        return _DIAG_COST if action in _DIAG else 1.0

    def is_goal(self, state: Cell) -> bool:
        return state == self.goal

    def heuristics(self) -> Dict[str, Callable[[Cell], float]]:
        return H.for_goal(self.goal)

    def heuristic_info(self) -> Dict[str, str]:
        return H.info()

    def render_state(self, state: Cell) -> str:
        out = []
        for r in range(self.rows):
            row = []
            for c in range(self.cols):
                if (r, c) == state:
                    row.append("@")
                elif (r, c) == self.goal:
                    row.append("G")
                elif self.grid[r][c] == 1:
                    row.append("#")
                else:
                    row.append(".")
            out.append("".join(row))
        return "\n".join(out)

    # --- helpers ---------------------------------------------------------

    @classmethod
    def random(cls, rows: int = 15, cols: int = 15, wall_prob: float = 0.28,
               allow_diagonal: bool = False, seed: int | None = None) -> "Maze":
        """Random maze with start at top-left and goal at bottom-right.

        Retries wall placement until a path exists (checked with a quick BFS), so
        generated mazes are always solvable and ``seed`` keeps them reproducible.
        """
        rng = random.Random(seed)
        start, goal = (0, 0), (rows - 1, cols - 1)
        for _ in range(200):
            grid = [[1 if rng.random() < wall_prob else 0 for _ in range(cols)]
                    for _ in range(rows)]
            grid[start[0]][start[1]] = 0
            grid[goal[0]][goal[1]] = 0
            if cls._path_exists(grid, start, goal):
                return cls(grid, start, goal, allow_diagonal=allow_diagonal)
        # Fallback: empty grid (always solvable).
        grid = [[0] * cols for _ in range(rows)]
        return cls(grid, start, goal, allow_diagonal=allow_diagonal)

    @staticmethod
    def _path_exists(grid: List[List[int]], start: Cell, goal: Cell) -> bool:
        from collections import deque
        rows, cols = len(grid), len(grid[0])
        seen = {start}
        q = deque([start])
        while q:
            r, c = q.popleft()
            if (r, c) == goal:
                return True
            for dr, dc in _ORTHO.values():
                nr, nc = r + dr, c + dc
                if (0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 0
                        and (nr, nc) not in seen):
                    seen.add((nr, nc))
                    q.append((nr, nc))
        return False
