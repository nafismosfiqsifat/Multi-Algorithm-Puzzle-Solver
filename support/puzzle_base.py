"""Abstract puzzle interface.

Every puzzle in this project implements the same small interface so that the
search algorithms in ``core/search`` never need to know *which* puzzle they are
solving. This decoupling is the backbone of the "modular / multi-algorithm"
requirement: a new puzzle needs no new search code, and a new algorithm needs no
new puzzle code.

Design contract
---------------
* A **state** must be *hashable* and *immutable* (use tuples / frozensets), so it
  can live in ``set``/``dict`` visited structures without defensive copying.
* ``apply_action`` must return a **new** state and never mutate its input.
* Costs are non-negative numbers (``step_cost``).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Hashable, List

State = Hashable
Action = Any


class Puzzle(ABC):
    """Common interface implemented by every concrete puzzle.

    Subclasses expose their available heuristics through :meth:`heuristics`,
    which maps a human-readable name to a ``state -> float`` callable. The UI and
    the informed-search algorithms consume heuristics exclusively through that
    mapping, so puzzles stay self-describing.
    """

    #: Short human-readable name, e.g. "8-Puzzle".
    name: str = "Puzzle"

    @abstractmethod
    def get_initial_state(self) -> State:
        """Return the (hashable) start state."""

    @abstractmethod
    def get_actions(self, state: State) -> List[Action]:
        """Return the list of actions legal in ``state``."""

    @abstractmethod
    def apply_action(self, state: State, action: Action) -> State:
        """Return the successor state produced by ``action`` (no mutation)."""

    @abstractmethod
    def is_goal(self, state: State) -> bool:
        """Return ``True`` iff ``state`` satisfies the goal test."""

    def step_cost(self, state: State, action: Action) -> float:
        """Cost of taking ``action`` in ``state``. Defaults to unit cost."""
        return 1.0

    # --- optional, puzzle-supplied metadata ------------------------------

    def heuristics(self) -> Dict[str, Callable[[State], float]]:
        """Map heuristic name -> ``state -> estimated cost to goal``.

        Uninformed searches ignore this; informed searches (A*, Greedy) pick one
        by name. Default: no heuristics (only uninformed search applies).
        """
        return {}

    def heuristic_info(self) -> Dict[str, str]:
        """Map heuristic name -> one-line admissibility/consistency note.

        Used by the in-app "About" panel. Optional.
        """
        return {}

    def render_state(self, state: State) -> str:
        """Return a plain-text rendering of ``state`` for console/debug use."""
        return str(state)
