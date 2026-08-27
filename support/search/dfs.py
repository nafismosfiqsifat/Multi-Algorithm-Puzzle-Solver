"""Depth-First Search (graph search, iterative) and a depth-limited variant used
by Iterative Deepening. DFS is complete on finite graphs but **not** optimal.
"""

from __future__ import annotations

from time import perf_counter
from typing import Optional

from core.metrics import SearchResult
from core.puzzle_base import Puzzle
from core.search.search_utils import Node, reconstruct


def dfs(puzzle: Puzzle, depth_limit: Optional[int] = None, **_: object) -> SearchResult:
    """Iterative DFS with a visited set. ``depth_limit=None`` means unbounded."""
    start = perf_counter()
    root = Node(puzzle.get_initial_state())

    stack = [root]
    # Visited maps state -> shallowest depth seen, so we can re-open a state if we
    # reach it via a shorter path (matters under a depth limit).
    visited: dict = {root.state: 0}
    generated = 1
    expanded = 0
    max_frontier = 1
    cutoff = False

    while stack:
        node = stack.pop()
        if puzzle.is_goal(node.state):
            return _result(node, expanded, generated, max_frontier, start, cutoff)
        expanded += 1

        if depth_limit is not None and node.depth >= depth_limit:
            cutoff = True
            continue

        for action in puzzle.get_actions(node.state):
            succ = puzzle.apply_action(node.state, action)
            child = node.child(succ, action, puzzle.step_cost(node.state, action))
            prev = visited.get(succ)
            if prev is not None and prev <= child.depth:
                continue
            visited[succ] = child.depth
            generated += 1
            stack.append(child)
            max_frontier = max(max_frontier, len(stack))

    note = "cutoff" if cutoff else "no solution"
    return SearchResult(algorithm="DFS", solved=False, nodes_expanded=expanded,
                        nodes_generated=generated, max_frontier=max_frontier,
                        runtime_ms=(perf_counter() - start) * 1000, note=note)


def _result(node, expanded, generated, max_frontier, start, cutoff) -> SearchResult:
    states, actions = reconstruct(node)
    return SearchResult(
        algorithm="DFS", solved=True, path=states, actions=actions,
        path_cost=node.path_cost, nodes_expanded=expanded, nodes_generated=generated,
        max_frontier=max_frontier, runtime_ms=(perf_counter() - start) * 1000,
    )
