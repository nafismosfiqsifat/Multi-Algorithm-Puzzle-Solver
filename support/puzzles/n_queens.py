"""N-Queens, framed as a constructive search problem so it plugs into the same
generic search algorithms as the other puzzles.

State  : tuple of column indices, one per already-placed row (top-down). Length =
         number of rows filled so far. e.g. (1, 3) means row0->col1, row1->col3.
Actions: a column to place a queen in the next empty row, if it attacks none of
         the queens already placed.
Goal   : all N rows filled (a complete non-attacking placement).
Cost   : 1 per queen placed (every solution sits at depth N).

Heuristic ``Remaining Rows`` = N - (rows placed) is the *exact* number of moves
left, hence admissible and consistent — it makes A*/Greedy drive straight to a
solution with almost no wasted expansion, a nice contrast against blind DFS.
"""

from __future__ import annotations

from typing import Callable, Dict, List, Tuple

from core.puzzle_base import Puzzle

State = Tuple[int, ...]


class NQueens(Puzzle):
    name = "N-Queens"

    def __init__(self, n: int = 8):
        if n < 1:
            raise ValueError("N must be >= 1.")
        self.n = n

    # --- interface -------------------------------------------------------

    def get_initial_state(self) -> State:
        return ()

    def get_actions(self, state: State) -> List[int]:
        row = len(state)
        if row >= self.n:
            return []
        return [col for col in range(self.n) if self._safe(state, col)]

    def apply_action(self, state: State, action: int) -> State:
        return state + (action,)

    def is_goal(self, state: State) -> bool:
        return len(state) == self.n

    def heuristics(self) -> Dict[str, Callable[[State], float]]:
        return {
            "Remaining Rows": lambda s: float(self.n - len(s)),
            "Attacking Pairs (relaxed)": self._attacking_pairs,
        }

    def heuristic_info(self) -> Dict[str, str]:
        return {
            "Remaining Rows": "Admissible & consistent: exactly N - placed queens remain, each costing one move.",
            "Attacking Pairs (relaxed)": "Admissible here (always 0 on legal partial states, since placements never attack); shown for comparison.",
        }

    def render_state(self, state: State) -> str:
        rows = []
        for r in range(self.n):
            row = ["."] * self.n
            if r < len(state):
                row[state[r]] = "Q"
            rows.append(" ".join(row))
        return "\n".join(rows)

    # --- helpers ---------------------------------------------------------

    def _safe(self, state: State, col: int) -> bool:
        row = len(state)
        for r, c in enumerate(state):
            if c == col or abs(c - col) == abs(r - row):
                return False
        return True

    def _attacking_pairs(self, state: State) -> float:
        pairs = 0
        for i in range(len(state)):
            for j in range(i + 1, len(state)):
                if state[i] == state[j] or abs(state[i] - state[j]) == abs(i - j):
                    pairs += 1
        return float(pairs)
