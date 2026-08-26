"""Multi-Algorithm Puzzle Solver — Streamlit entry point.

Run with:  streamlit run app.py
"""

from __future__ import annotations

import streamlit as st

from core.search import ALGORITHMS
from core.solver import run_algorithm
from ui import about
from ui.comparison_view import render_comparison
from ui.input_forms import (configure_eight_puzzle, configure_maze,
                            configure_n_queens)
from ui.visualizer import render

st.set_page_config(page_title="Puzzle Solver", page_icon="🧩", layout="wide")

PUZZLE_CONFIGURERS = {
    "8-Puzzle": configure_eight_puzzle,
    "Maze / Pathfinding": configure_maze,
    "N-Queens": configure_n_queens,
}


def sidebar():
    """Render all inputs; return (puzzle, run_specs, do_run)."""
    st.sidebar.title("🧩 Puzzle Solver")
    st.sidebar.markdown("CSE 440 — Multi-Algorithm Search")

    puzzle_label = st.sidebar.selectbox("Puzzle", list(PUZZLE_CONFIGURERS))
    st.sidebar.markdown("### 1 · Configure puzzle")
    with st.sidebar:
        puzzle = PUZZLE_CONFIGURERS[puzzle_label]()

    st.sidebar.markdown("### 2 · Choose algorithms")
    chosen = st.sidebar.multiselect(
        "Algorithms to run",
        options=list(ALGORITHMS),
        default=["bfs", "astar"],
        format_func=lambda k: ALGORITHMS[k]["label"],
    )

    # Heuristic selector (shared by all informed algorithms) + per-algo params.
    heuristic_name = None
    params: dict[str, dict] = {}
    if puzzle is not None:
        needs_h = any(ALGORITHMS[k]["informed"] for k in chosen)
        heuristics = list(puzzle.heuristics().keys())
        if needs_h and heuristics:
            heuristic_name = st.sidebar.selectbox("Heuristic (for A*/Greedy)", heuristics)
        for k in chosen:
            for pname, (plabel, kind, default) in ALGORITHMS[k]["params"].items():
                widget_key = f"{k}_{pname}"
                if kind == "int":
                    val = st.sidebar.number_input(f"{ALGORITHMS[k]['label']} · {plabel}",
                                                  value=int(default), step=1, key=widget_key)
                    params.setdefault(k, {})[pname] = int(val)
                elif kind == "int_opt":
                    txt = st.sidebar.text_input(f"{ALGORITHMS[k]['label']} · {plabel}",
                                                value="", key=widget_key)
                    params.setdefault(k, {})[pname] = int(txt) if txt.strip() else None
                elif kind == "float":
                    val = st.sidebar.number_input(f"{ALGORITHMS[k]['label']} · {plabel}",
                                                  value=float(default), step=0.5,
                                                  min_value=1.0, key=widget_key)
                    params.setdefault(k, {})[pname] = float(val)

    do_run = st.sidebar.button("▶️ Solve", type="primary", use_container_width=True,
                               disabled=(puzzle is None or not chosen))
    return puzzle, puzzle_label, chosen, heuristic_name, params, do_run


def solve_all(puzzle, chosen, heuristic_name, params):
    results = []
    progress = st.progress(0.0, text="Solving…")
    for i, key in enumerate(chosen, 1):
        label = ALGORITHMS[key]["label"]
        progress.progress(i / len(chosen), text=f"Running {label}…")
        try:
            res = run_algorithm(puzzle, key, heuristic_name=heuristic_name,
                                **params.get(key, {}))
        except Exception as exc:  # surface bad configs without crashing the app
            st.error(f"{label} failed: {exc}")
            continue
        results.append(res)
    progress.empty()
    return results


def show_solution(puzzle, result):
    st.markdown(f"#### {result.algorithm}"
                + (f" · heuristic: *{result.heuristic}*" if result.heuristic else ""))
    if not result.solved:
        st.warning(f"No solution found. {result.note}")
        st.pyplot(render(puzzle, puzzle.get_initial_state()))
        return

    st.caption(f"Path length {result.path_length} · cost {result.path_cost:g} · "
               f"{result.nodes_expanded} nodes expanded · {result.runtime_ms:.2f} ms")
    step = st.slider("Step through solution", 0, result.path_length, 0,
                     key=f"step_{result.algorithm}")
    state = result.path[step]
    st.pyplot(render(puzzle, state, path=result.path))
    if step < len(result.actions):
        st.caption(f"Next move: **{result.actions[step]}**")


def main():
    puzzle, puzzle_label, chosen, heuristic_name, params, do_run = sidebar()

    st.title("Multi-Algorithm Puzzle Solver")

    if puzzle is None:
        st.info("Fix the puzzle configuration in the sidebar to continue.")
        return

    # Preview the current instance.
    left, right = st.columns([1, 1])
    with left:
        st.markdown("### Current instance")
        st.pyplot(render(puzzle, puzzle.get_initial_state()))

    if do_run:
        st.session_state.results = solve_all(puzzle, chosen, heuristic_name, params)
        st.session_state.results_puzzle = puzzle

    results = st.session_state.get("results", [])
    if results and st.session_state.get("results_puzzle") is not None:
        rp = st.session_state.results_puzzle
        with right:
            st.markdown("### Solution viewer")
            labels = [f"{r.algorithm}" for r in results]
            pick = st.selectbox("Show solution for", range(len(results)),
                                format_func=lambda i: labels[i])
            show_solution(rp, results[pick])

        st.divider()
        render_comparison(results)

    # About panel.
    st.divider()
    with st.expander("ℹ️ About the algorithms & heuristics"):
        st.markdown(about.OVERVIEW)
        st.markdown("#### Algorithms")
        for k in chosen:
            label = ALGORITHMS[k]["label"]
            st.markdown(f"- **{label}** — {about.ALGORITHM_NOTES.get(label, '')}")
        info = puzzle.heuristic_info()
        if info:
            st.markdown("#### Heuristics for this puzzle")
            for name, note in info.items():
                st.markdown(f"- **{name}** — {note}")


if __name__ == "__main__":
    main()
