"""Heuristics for the (n^2 - 1)-puzzle (8-puzzle when n=3, 15-puzzle when n=4).

All three are **admissible** and **consistent** for the standard unit-cost slide
move. See ``docs/heuristic_analysis.md`` for the proof sketches.

A state is a flat tuple of length n*n; value 0 is the blank. The goal is the
identity ordering ``(1, 2, ..., n*n-1, 0)``.
"""

from __future__ import annotations

from typing import Callable, Dict, Tuple

State = Tuple[int, ...]


def _side(state: State) -> int:
    n = int(round(len(state) ** 0.5))
    return n


def goal_for(state: State) -> State:
    n2 = len(state)
    return tuple(list(range(1, n2)) + [0])


def misplaced_tiles(state: State) -> float:
    """Count of tiles not in their goal cell (the blank is not counted)."""
    goal = goal_for(state)
    return float(sum(1 for i, v in enumerate(state) if v != 0 and v != goal[i]))


def manhattan(state: State) -> float:
    """Sum over tiles of |dr| + |dc| between current and goal cell."""
    n = _side(state)
    total = 0
    for idx, v in enumerate(state):
        if v == 0:
            continue
        goal_idx = v - 1                      # tile v belongs at index v-1
        total += abs(idx // n - goal_idx // n) + abs(idx % n - goal_idx % n)
    return float(total)


def linear_conflict(state: State) -> float:
    """Manhattan distance + 2 per linear conflict.

    Two tiles are in linear conflict when they share their goal row (or column),
    are both currently in that row (or column), and their required order is
    reversed. Resolving each conflict forces >= 2 extra moves beyond Manhattan,
    so the bonus preserves admissibility. Dominates plain Manhattan.
    """
    n = _side(state)
    total = manhattan(state)

    # Row conflicts.
    for row in range(n):
        goal_cols = []  # (goal_col, current_col) for tiles whose goal row == row
        for col in range(n):
            v = state[row * n + col]
            if v == 0:
                continue
            gr, gc = (v - 1) // n, (v - 1) % n
            if gr == row:
                goal_cols.append((gc, col))
        total += 2 * _count_reversals(goal_cols)

    # Column conflicts.
    for col in range(n):
        goal_rows = []
        for row in range(n):
            v = state[row * n + col]
            if v == 0:
                continue
            gr, gc = (v - 1) // n, (v - 1) % n
            if gc == col:
                goal_rows.append((gr, row))
        total += 2 * _count_reversals(goal_rows)

    return float(total)


def _count_reversals(pairs) -> int:
    """Number of pairs whose goal order is reversed w.r.t. current order."""
    conflicts = 0
    for i in range(len(pairs)):
        for j in range(i + 1, len(pairs)):
            goal_i, cur_i = pairs[i]
            goal_j, cur_j = pairs[j]
            if (cur_i < cur_j and goal_i > goal_j) or (cur_i > cur_j and goal_i < goal_j):
                conflicts += 1
    return conflicts


def registry() -> Dict[str, Callable[[State], float]]:
    return {
        "Misplaced Tiles": misplaced_tiles,
        "Manhattan Distance": manhattan,
        "Linear Conflict": linear_conflict,
    }


def info() -> Dict[str, str]:
    return {
        "Misplaced Tiles": "Admissible & consistent. Each misplaced tile needs >=1 move; a slide changes h by at most 1.",
        "Manhattan Distance": "Admissible & consistent. Sum of tile distances; a single slide moves one tile one cell, so h drops by at most the step cost.",
        "Linear Conflict": "Admissible & consistent. Manhattan + 2 per in-line reversed pair; dominates Manhattan, expands fewer nodes.",
    }
