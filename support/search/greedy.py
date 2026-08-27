"""Greedy Best-First Search — expands the node with the lowest heuristic value
h(n), ignoring path cost g(n). Fast and memory-light, but neither complete (in
general) nor optimal. Great foil to A* in the comparison view.
"""

from __future__ import annotations

from time import perf_counter
from typing import Callable

from core.metrics import SearchResult
from core.puzzle_base import Puzzle
from core.search.search_utils import Node, PriorityQueue, reconstruct


def greedy(puzzle: Puzzle, heuristic: Callable[[object], float],
           heuristic_name: str = "h", **_: object) -> SearchResult:
    if heuristic is None:
        raise ValueError("Greedy Best-First Search requires a heuristic.")

    start = perf_counter()
    root = Node(puzzle.get_initial_state())

    frontier = PriorityQueue()
    frontier.push(root.state, heuristic(root.state), root)
    explored: set = set()
    generated = 1
    expanded = 0
    max_frontier = 1

    while frontier:
        node = frontier.pop()
        if puzzle.is_goal(node.state):
            states, actions = reconstruct(node)
            return SearchResult(
                algorithm="Greedy", solved=True, path=states, actions=actions,
                path_cost=node.path_cost, nodes_expanded=expanded,
                nodes_generated=generated, max_frontier=max_frontier,
                runtime_ms=(perf_counter() - start) * 1000, heuristic=heuristic_name,
            )
        if node.state in explored:
            continue
        explored.add(node.state)
        expanded += 1
        for action in puzzle.get_actions(node.state):
            succ = puzzle.apply_action(node.state, action)
            if succ in explored:
                continue
            child = node.child(succ, action, puzzle.step_cost(node.state, action))
            frontier.push(succ, heuristic(succ), child)
            generated += 1
            max_frontier = max(max_frontier, len(frontier))

    return SearchResult(algorithm="Greedy", solved=False, nodes_expanded=expanded,
                        nodes_generated=generated, max_frontier=max_frontier,
                        runtime_ms=(perf_counter() - start) * 1000,
                        heuristic=heuristic_name, note="no solution")
