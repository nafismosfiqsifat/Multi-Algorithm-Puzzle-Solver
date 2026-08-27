"""Breadth-First Search — uninformed, complete, optimal for *unit* step costs."""

from __future__ import annotations

from collections import deque
from time import perf_counter

from core.metrics import SearchResult
from core.puzzle_base import Puzzle
from core.search.search_utils import Node, reconstruct


def bfs(puzzle: Puzzle, **_: object) -> SearchResult:
    start = perf_counter()
    root = Node(puzzle.get_initial_state())

    if puzzle.is_goal(root.state):
        return _result(root, expanded=0, generated=1, max_frontier=1, start=start)

    frontier: deque[Node] = deque([root])
    explored: set = {root.state}
    generated = 1
    expanded = 0
    max_frontier = 1

    while frontier:
        node = frontier.popleft()
        expanded += 1
        for action in puzzle.get_actions(node.state):
            succ = puzzle.apply_action(node.state, action)
            if succ in explored:
                continue
            generated += 1
            child = node.child(succ, action, puzzle.step_cost(node.state, action))
            if puzzle.is_goal(succ):  # goal test on generation -> optimal for unit cost
                return _result(child, expanded, generated, max_frontier, start)
            explored.add(succ)
            frontier.append(child)
            max_frontier = max(max_frontier, len(frontier))

    return SearchResult(algorithm="BFS", solved=False, nodes_expanded=expanded,
                        nodes_generated=generated, max_frontier=max_frontier,
                        runtime_ms=(perf_counter() - start) * 1000, note="no solution")


def _result(node: Node, expanded: int, generated: int, max_frontier: int, start: float) -> SearchResult:
    states, actions = reconstruct(node)
    return SearchResult(
        algorithm="BFS", solved=True, path=states, actions=actions,
        path_cost=node.path_cost, nodes_expanded=expanded, nodes_generated=generated,
        max_frontier=max_frontier, runtime_ms=(perf_counter() - start) * 1000,
    )
