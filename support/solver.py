"""Thin orchestration layer between the UI and the algorithms.

Responsibilities:
* resolve an algorithm key + optional heuristic name into a concrete run,
* enforce the correctness requirement by *replaying* every returned solution from
  the initial state and confirming it reaches the goal before it is trusted.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from core.metrics import SearchResult
from core.puzzle_base import Puzzle
from core.search import ALGORITHMS


def run_algorithm(puzzle: Puzzle, algo_key: str, heuristic_name: Optional[str] = None,
                  **params: Any) -> SearchResult:
    """Run ``algo_key`` on ``puzzle`` and return a verified :class:`SearchResult`.

    ``params`` are algorithm-specific options (depth_limit, max_depth, weight).
    Informed algorithms require ``heuristic_name`` to name a heuristic the puzzle
    exposes.
    """
    if algo_key not in ALGORITHMS:
        raise KeyError(f"Unknown algorithm '{algo_key}'. Choices: {list(ALGORITHMS)}")

    spec = ALGORITHMS[algo_key]
    func = spec["func"]
    kwargs: Dict[str, Any] = dict(params)

    if spec["informed"]:
        heuristics = puzzle.heuristics()
        if not heuristics:
            raise ValueError(f"{puzzle.name} exposes no heuristics for informed search.")
        if heuristic_name is None:
            heuristic_name = next(iter(heuristics))
        if heuristic_name not in heuristics:
            raise KeyError(f"Unknown heuristic '{heuristic_name}' for {puzzle.name}.")
        kwargs["heuristic"] = heuristics[heuristic_name]
        kwargs["heuristic_name"] = heuristic_name

    result = func(puzzle, **kwargs)

    if result.solved and not verify_solution(puzzle, result):
        result.solved = False
        result.note = (result.note + "; " if result.note else "") + "FAILED verification"
    return result


def verify_solution(puzzle: Puzzle, result: SearchResult) -> bool:
    """Replay ``result.actions`` from the initial state; confirm the goal is hit
    and the reported path/cost are internally consistent.
    """
    if not result.path:
        return False
    state = puzzle.get_initial_state()
    if result.path[0] != state:
        return False
    cost = 0.0
    for action in result.actions:
        legal = puzzle.get_actions(state)
        if action not in legal:
            return False
        cost += puzzle.step_cost(state, action)
        state = puzzle.apply_action(state, action)
    if not puzzle.is_goal(state):
        return False
    # Path cost should match the sum of step costs (allow tiny float slack).
    return abs(cost - result.path_cost) < 1e-6
