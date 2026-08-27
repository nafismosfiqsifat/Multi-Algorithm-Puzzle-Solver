"""A* Search and its Weighted A* generalization.

A* orders the frontier by f(n) = g(n) + w * h(n).
* ``weight == 1``  -> classic A*: optimal when h is admissible.
* ``weight  > 1``  -> Weighted A*: greedier, faster, and bounded-suboptimal
  (solution cost <= w * optimal). Exposed for the speed/optimality tradeoff study.
"""

from __future__ import annotations

from time import perf_counter
from typing import Callable

from core.metrics import SearchResult
from core.puzzle_base import Puzzle
from core.search.search_utils import Node, PriorityQueue, reconstruct


def astar(puzzle: Puzzle, heuristic: Callable[[object], float],
          heuristic_name: str = "h", weight: float = 1.0, **_: object) -> SearchResult:
    if heuristic is None:
        raise ValueError("A* requires a heuristic.")

    label = "A*" if weight == 1.0 else f"Weighted A* (w={weight:g})"
    start = perf_counter()
    root = Node(puzzle.get_initial_state())

    frontier = PriorityQueue()
    frontier.push(root.state, weight * heuristic(root.state), root)
    best_g: dict = {root.state: 0.0}
    generated = 1
    expanded = 0
    max_frontier = 1

    while frontier:
        node = frontier.pop()
        if puzzle.is_goal(node.state):
            states, actions = reconstruct(node)
            return SearchResult(
                algorithm=label, solved=True, path=states, actions=actions,
                path_cost=node.path_cost, nodes_expanded=expanded,
                nodes_generated=generated, max_frontier=max_frontier,
                runtime_ms=(perf_counter() - start) * 1000, heuristic=heuristic_name,
            )
        # A node can be popped after a cheaper path to it was already found.
        if node.path_cost > best_g.get(node.state, float("inf")):
            continue
        expanded += 1
        for action in puzzle.get_actions(node.state):
            step = puzzle.step_cost(node.state, action)
            succ = puzzle.apply_action(node.state, action)
            g = node.path_cost + step
            if succ not in best_g or g < best_g[succ]:
                best_g[succ] = g
                child = node.child(succ, action, step)
                f = g + weight * heuristic(succ)
                frontier.push(succ, f, child)
                generated += 1
                max_frontier = max(max_frontier, len(frontier))

    return SearchResult(algorithm=label, solved=False, nodes_expanded=expanded,
                        nodes_generated=generated, max_frontier=max_frontier,
                        runtime_ms=(perf_counter() - start) * 1000,
                        heuristic=heuristic_name, note="no solution")
