"""Puzzle configuration widgets. Each ``configure_*`` renders Streamlit inputs in
the sidebar and returns a constructed puzzle instance (or ``None`` if the current
configuration is invalid, after showing an error).
"""

from __future__ import annotations

from typing import List, Optional

import streamlit as st

from core.puzzles import EightPuzzle, Maze, NQueens


def configure_eight_puzzle() -> Optional[EightPuzzle]:
    st.caption("Blank is 0. Goal is 1..8 then blank.")
    mode = st.radio("Configuration", ["Random shuffle", "Manual entry"], horizontal=True)

    if mode == "Random shuffle":
        seed = st.number_input("Random seed (reproducible)", value=42, step=1)
        moves = st.slider("Shuffle moves (difficulty)", 5, 120, 30)
        if st.button("🔀 Shuffle"):
            st.session_state.pop("eight_state", None)
        if "eight_state" not in st.session_state:
            st.session_state.eight_state = EightPuzzle.random(
                shuffle_moves=int(moves), seed=int(seed)).get_initial_state()
        state = st.session_state.eight_state
        return EightPuzzle(state)

    default = "1,2,3,4,0,6,7,5,8"
    raw = st.text_input("Tiles (row-major, comma-separated)", value=default)
    try:
        tiles = tuple(int(x) for x in raw.replace(" ", "").split(","))
    except ValueError:
        st.error("Could not parse tiles. Use 9 comma-separated integers 0-8.")
        return None
    if sorted(tiles) != list(range(9)):
        st.error("Tiles must be a permutation of 0..8.")
        return None
    if not EightPuzzle.is_solvable(tiles):
        st.error("⚠️ This configuration is **unsolvable** (inversion parity). Adjust the tiles.")
        return None
    st.success("Configuration is solvable.")
    return EightPuzzle(tiles)


def configure_maze() -> Optional[Maze]:
    col1, col2 = st.columns(2)
    rows = col1.slider("Rows", 5, 30, 15)
    cols = col2.slider("Cols", 5, 30, 15)
    wall_prob = st.slider("Wall density", 0.0, 0.5, 0.28, 0.02)
    allow_diag = st.checkbox("Allow diagonal moves (8-connected)", value=False)
    seed = st.number_input("Random seed", value=7, step=1)
    if st.button("🧱 Regenerate maze"):
        st.session_state.pop("maze_obj_key", None)

    key = (rows, cols, round(wall_prob, 2), allow_diag, int(seed))
    if st.session_state.get("maze_obj_key") != key:
        st.session_state.maze_obj_key = key
        st.session_state.maze_obj = Maze.random(
            rows=rows, cols=cols, wall_prob=wall_prob,
            allow_diagonal=allow_diag, seed=int(seed))
    return st.session_state.maze_obj


def configure_n_queens() -> Optional[NQueens]:
    n = st.slider("Board size N", 4, 20, 8)
    st.caption("Constructive formulation: place one non-attacking queen per row.")
    return NQueens(int(n))
