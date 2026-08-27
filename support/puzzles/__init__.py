"""Puzzle registry, keyed for the UI dropdown."""

from __future__ import annotations

from core.puzzles.eight_puzzle import EightPuzzle
from core.puzzles.maze import Maze
from core.puzzles.n_queens import NQueens

PUZZLES = {
    "eight_puzzle": {"label": "8-Puzzle", "cls": EightPuzzle},
    "maze": {"label": "Maze / Pathfinding", "cls": Maze},
    "n_queens": {"label": "N-Queens", "cls": NQueens},
}

__all__ = ["PUZZLES", "EightPuzzle", "Maze", "NQueens"]
