"""Iterative Deepening Search — repeatedly runs depth-limited DFS with an
increasing bound. Combines DFS's linear memory with BFS's optimality (unit cost)
and completeness, at the cost of re-expanding shallow nodes each round.
"""

from __future__ import annotations

from time import perf_counter

from core.metrics import SearchResult
from core.puzzle_base import Puzzle
from core.search.dfs import dfs


def ids(puzzle: Puzzle, max_depth: int = 50, **_: object) -> SearchResult:
    start = perf_counter()
    total_expanded = 0
    total_generated = 0
    max_frontier = 0

    for depth in range(max_depth + 1):
        res = dfs(puzzle, depth_limit=depth)
        total_expanded += res.nodes_expanded
        total_generated += res.nodes_generated
        max_frontier = max(max_frontier, res.max_frontier)

        if res.solved:
            return SearchResult(
                algorithm="IDS", solved=True, path=res.path, actions=res.actions,
                path_cost=res.path_cost, nodes_expanded=total_expanded,
                nodes_generated=total_generated, max_frontier=max_frontier,
                runtime_ms=(perf_counter() - start) * 1000,
                note=f"solution depth {res.path_length}",
            )
        if res.note != "cutoff":
            # Whole space exhausted below this depth with no solution and no cutoff.
            break

    return SearchResult(algorithm="IDS", solved=False, nodes_expanded=total_expanded,
                        nodes_generated=total_generated, max_frontier=max_frontier,
                        runtime_ms=(perf_counter() - start) * 1000,
                        note=f"no solution within depth {max_depth}")
