"""Side-by-side performance comparison: a metrics table, bar charts, and CSV
export. Consumes a list of :class:`SearchResult` (one per algorithm run on the
same puzzle instance).
"""

from __future__ import annotations

from typing import List

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from core.metrics import SearchResult


def results_dataframe(results: List[SearchResult]) -> pd.DataFrame:
    return pd.DataFrame([r.as_row() for r in results])


def render_comparison(results: List[SearchResult]) -> None:
    if not results:
        st.info("Run one or more algorithms to see a comparison.")
        return

    df = results_dataframe(results)
    st.subheader("📊 Metrics table")
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.download_button(
        "⬇️ Export results as CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="puzzle_solver_results.csv",
        mime="text/csv",
    )

    solved = [r for r in results if r.solved]
    if not solved:
        st.warning("No algorithm found a solution on this instance.")
        return

    labels = [f"{r.algorithm}\n{r.heuristic}" if r.heuristic else r.algorithm for r in solved]
    st.subheader("📈 Charts")
    c1, c2 = st.columns(2)
    with c1:
        _bar(labels, [r.nodes_expanded for r in solved], "Nodes expanded", "#4C78A8")
        _bar(labels, [r.runtime_ms for r in solved], "Runtime (ms)", "#F58518")
    with c2:
        _bar(labels, [r.path_cost for r in solved], "Path cost (optimality)", "#54A24B")
        _bar(labels, [r.max_frontier for r in solved], "Max frontier (memory)", "#E45756")

    _highlight_best(solved)


def _bar(labels: List[str], values: List[float], title: str, color: str) -> None:
    fig, ax = plt.subplots(figsize=(5, 3))
    ax.bar(labels, values, color=color)
    ax.set_title(title, fontsize=11)
    ax.tick_params(axis="x", labelrotation=30, labelsize=8)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


def _highlight_best(solved: List[SearchResult]) -> None:
    fastest = min(solved, key=lambda r: r.runtime_ms)
    leanest = min(solved, key=lambda r: r.nodes_expanded)
    optimal = min(solved, key=lambda r: r.path_cost)
    st.markdown(
        f"""
**Takeaways for this instance**
- ⚡ Fastest runtime: **{fastest.algorithm}** ({fastest.runtime_ms:.2f} ms)
- 🧠 Fewest nodes expanded: **{leanest.algorithm}** ({leanest.nodes_expanded})
- 🎯 Lowest path cost: **{optimal.algorithm}** ({optimal.path_cost:g})
"""
    )
