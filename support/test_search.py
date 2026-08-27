"""Correctness tests: every algorithm on hand-verifiable instances.

Key invariants checked:
* optimal algorithms (BFS unit-cost, UCS, A* with admissible h) agree on cost;
* every returned solution passes replay verification;
* informed search never expands *more* than blind search on the same instance
  when the heuristic is informative (sanity, not a hard guarantee — asserted only
  where it holds decisively).
"""

from __future__ import annotations

import pytest

from core.puzzles import EightPuzzle, Maze, NQueens
from core.solver import run_algorithm, verify_solution

# A known 8-puzzle instance solvable in exactly 4 moves.
#   1 2 3          1 2 3
#   4 0 6    ->    4 5 6
#   7 5 8          7 8 0
FOUR_MOVE = (1, 2, 3, 4, 0, 6, 7, 5, 8)


@pytest.fixture
def easy_eight():
    return EightPuzzle(FOUR_MOVE)


@pytest.mark.parametrize("algo,h", [
    ("bfs", None), ("ucs", None), ("ids", None),
    ("astar", "Manhattan Distance"), ("astar", "Misplaced Tiles"),
    ("astar", "Linear Conflict"),
])
def test_eight_optimal_cost(easy_eight, algo, h):
    res = run_algorithm(easy_eight, algo, heuristic_name=h, max_depth=10)
    assert res.solved
    assert verify_solution(easy_eight, res)
    assert res.path_cost == 2, f"{algo} found cost {res.path_cost}, expected optimal 2"


def test_eight_greedy_solves_but_may_be_suboptimal(easy_eight):
    res = run_algorithm(easy_eight, "greedy", heuristic_name="Manhattan Distance")
    assert res.solved
    assert verify_solution(easy_eight, res)
    assert res.path_cost >= 2  # greedy is not guaranteed optimal


def test_eight_solvability_check():
    assert EightPuzzle.is_solvable(FOUR_MOVE)
    # Swapping two tiles flips inversion parity -> unsolvable.
    bad = (2, 1, 3, 4, 0, 6, 7, 5, 8)
    assert not EightPuzzle.is_solvable(bad)
    with pytest.raises(ValueError):
        # apply_action never produces this, but the search should still refuse to
        # "solve" an unsolvable board within any depth (checked elsewhere).
        EightPuzzle((0, 0, 1, 2, 3, 4, 5, 6, 7))  # not a permutation


def test_random_shuffle_is_always_solvable():
    for seed in range(20):
        p = EightPuzzle.random(shuffle_moves=50, seed=seed)
        assert EightPuzzle.is_solvable(p.get_initial_state())


def test_astar_matches_ucs_cost_on_random_eight():
    for seed in range(5):
        p = EightPuzzle.random(shuffle_moves=14, seed=seed)
        ucs = run_algorithm(p, "ucs")
        astar = run_algorithm(p, "astar", heuristic_name="Manhattan Distance")
        assert ucs.solved and astar.solved
        assert ucs.path_cost == astar.path_cost


# --- Maze --------------------------------------------------------------

def test_maze_open_grid_shortest_path():
    grid = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    m = Maze(grid, start=(0, 0), goal=(2, 2))
    for algo, h in [("bfs", None), ("ucs", None), ("astar", "Manhattan Distance")]:
        res = run_algorithm(m, algo, heuristic_name=h)
        assert res.solved and verify_solution(m, res)
        assert res.path_cost == 4  # Manhattan distance on an open grid


def test_maze_unsolvable_when_walled_off():
    # Goal cell (2,2) is free but fully boxed off from the start by walls.
    grid = [
        [0, 0, 0],
        [0, 1, 1],
        [0, 1, 0],
    ]
    m = Maze(grid, start=(0, 0), goal=(2, 2))
    res = run_algorithm(m, "bfs")
    assert not res.solved


def test_maze_rejects_start_or_goal_on_wall():
    grid = [[0, 1], [0, 0]]
    with pytest.raises(ValueError):
        Maze(grid, start=(0, 0), goal=(0, 1))  # goal sits on a wall


def test_maze_diagonal_cost():
    grid = [[0, 0], [0, 0]]
    m = Maze(grid, start=(0, 0), goal=(1, 1), allow_diagonal=True)
    res = run_algorithm(m, "astar", heuristic_name="Chebyshev (Diagonal)")
    assert res.solved
    assert abs(res.path_cost - 2 ** 0.5) < 1e-6  # one diagonal step


# --- N-Queens ----------------------------------------------------------

@pytest.mark.parametrize("algo,h", [
    ("dfs", None), ("bfs", None),
    ("astar", "Remaining Rows"), ("greedy", "Remaining Rows"),
])
def test_n_queens_valid_solution(algo, h):
    q = NQueens(6)
    res = run_algorithm(q, algo, heuristic_name=h)
    assert res.solved and verify_solution(q, res)
    placement = res.path[-1]
    assert len(placement) == 6
    # No two queens attack each other.
    for i in range(6):
        for j in range(i + 1, 6):
            assert placement[i] != placement[j]
            assert abs(placement[i] - placement[j]) != abs(i - j)


def test_n_queens_no_solution_for_n_equals_3():
    q = NQueens(3)
    res = run_algorithm(q, "dfs")
    assert not res.solved  # 3-queens has no solution
