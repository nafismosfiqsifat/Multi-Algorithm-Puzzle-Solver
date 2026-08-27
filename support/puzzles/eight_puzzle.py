"""The 8-puzzle (generalizes to the 15-puzzle for n=4).

State  : flat tuple of length n*n; 0 is the blank.
Actions: slide a neighboring tile into the blank -> "Up"/"Down"/"Left"/"Right"
         (naming the direction the *blank* moves).
Goal   : (1, 2, ..., n*n-1, 0).
Cost   : 1 per slide.

Solvability is decided by inversion-count parity, so we can validate manual input
and generate guaranteed-solvable shuffles.
"""

from __future__ import annotations

import random
from typing import Callable, Dict, List, Tuple

from core.heuristics import eight_puzzle_heuristics as H
from core.puzzle_base import Puzzle

State = Tuple[int, ...]

# Direction the blank moves -> (row delta, col delta).
_MOVES = {"Up": (-1, 0), "Down": (1, 0), "Left": (0, -1), "Right": (0, 1)}


class EightPuzzle(Puzzle):
    name = "8-Puzzle"

    def __init__(self, initial: State, n: int = 3):
        if len(initial) != n * n:
            raise ValueError(f"State length {len(initial)} does not match n={n} (n*n={n*n}).")
        if sorted(initial) != list(range(n * n)):
            raise ValueError("State must be a permutation of 0..n*n-1.")
        self.n = n
        self._initial = tuple(initial)
        self._goal = tuple(list(range(1, n * n)) + [0])

    # --- interface -------------------------------------------------------

    def get_initial_state(self) -> State:
        return self._initial

    def get_actions(self, state: State) -> List[str]:
        blank = state.index(0)
        r, c = divmod(blank, self.n)
        actions = []
        for name, (dr, dc) in _MOVES.items():
            if 0 <= r + dr < self.n and 0 <= c + dc < self.n:
                actions.append(name)
        return actions

    def apply_action(self, state: State, action: str) -> State:
        blank = state.index(0)
        r, c = divmod(blank, self.n)
        dr, dc = _MOVES[action]
        swap = (r + dr) * self.n + (c + dc)
        lst = list(state)
        lst[blank], lst[swap] = lst[swap], lst[blank]
        return tuple(lst)

    def is_goal(self, state: State) -> bool:
        return state == self._goal

    def heuristics(self) -> Dict[str, Callable[[State], float]]:
        return H.registry()

    def heuristic_info(self) -> Dict[str, str]:
        return H.info()

    def render_state(self, state: State) -> str:
        rows = []
        for r in range(self.n):
            cells = state[r * self.n:(r + 1) * self.n]
            rows.append(" ".join("_" if v == 0 else str(v) for v in cells))
        return "\n".join(rows)

    # --- helpers ---------------------------------------------------------

    @staticmethod
    def is_solvable(state: State, n: int = 3) -> bool:
        """Solvable iff inversion parity matches the goal's.

        For odd n: solvable iff the inversion count is even.
        For even n: solvable iff (inversions + row-of-blank-from-bottom) is odd.
        """
        tiles = [v for v in state if v != 0]
        inversions = sum(
            1 for i in range(len(tiles)) for j in range(i + 1, len(tiles))
            if tiles[i] > tiles[j]
        )
        if n % 2 == 1:
            return inversions % 2 == 0
        blank_row_from_bottom = n - (state.index(0) // n)
        return (inversions + blank_row_from_bottom) % 2 == 1

    @classmethod
    def random(cls, n: int = 3, shuffle_moves: int = 60, seed: int | None = None) -> "EightPuzzle":
        """Build a guaranteed-solvable instance by random-walking from the goal.

        Walking backwards from the solved board keeps the result solvable and
        lets ``seed`` make instances reproducible (non-functional requirement).
        """
        rng = random.Random(seed)
        goal = tuple(list(range(1, n * n)) + [0])
        puzzle = cls(goal, n=n)
        state = goal
        last = None
        for _ in range(shuffle_moves):
            actions = puzzle.get_actions(state)
            # Avoid immediately undoing the previous move for a better shuffle.
            if last is not None:
                opposite = {"Up": "Down", "Down": "Up", "Left": "Right", "Right": "Left"}[last]
                actions = [a for a in actions if a != opposite] or actions
            action = rng.choice(actions)
            state = puzzle.apply_action(state, action)
            last = action
        return cls(state, n=n)
