"""Uniform Cost Search — Dijkstra's algorithm over the state space. Complete and
optimal for any non-negative step costs. Goal test happens on *pop*.
"""

from __future__ import annotations

from time import perf_counter

from core.metrics import SearchResult
from core.puzzle_base import Puzzle
from core.search.search_utils import Node, PriorityQueue, reconstruct


def ucs(puzzle: Puzzle, **_: object) -> SearchResult:
    start = perf_counter()
    root = Node(puzzle.get_initial_state())

    frontier = PriorityQueue()
    frontier.push(root.state, root.path_cost, root)
    best_g: dict = {root.state: 0.0}
    generated = 1
    expanded = 0
    max_frontier = 1

    while frontier:
        node = frontier.pop()
        if puzzle.is_goal(node.state):
            states, actions = reconstruct(node)
            return SearchResult(
                algorithm="UCS", solved=True, path=states, actions=actions,
                path_cost=node.path_cost, nodes_expanded=expanded,
                nodes_generated=generated, max_frontier=max_frontier,
                runtime_ms=(perf_counter() - start) * 1000,
            )
        expanded += 1
        for action in puzzle.get_actions(node.state):
            succ = puzzle.apply_action(node.state, action)
            g = node.path_cost + puzzle.step_cost(node.state, action)
            if succ not in best_g or g < best_g[succ]:
                best_g[succ] = g
                child = node.child(succ, action, puzzle.step_cost(node.state, action))
                frontier.push(succ, g, child)
                generated += 1
                max_frontier = max(max_frontier, len(frontier))

    return SearchResult(algorithm="UCS", solved=False, nodes_expanded=expanded,
                        nodes_generated=generated, max_frontier=max_frontier,
                        runtime_ms=(perf_counter() - start) * 1000, note="no solution")
