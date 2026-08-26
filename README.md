# 🧩 Multi-Algorithm Puzzle Solver

**CSE 440 — Artificial Intelligence**

A modular puzzle-solving application that solves several classic AI puzzles with a
shared search engine, then compares how uninformed and informed search algorithms
perform against each other — side by side, with charts and exportable metrics.

Pick a puzzle → pick one or more algorithms → solve → watch the solution animate
and see the performance comparison.

---

## ✨ Features

- **3 puzzles** behind one interface: **8-Puzzle**, **Maze / Pathfinding**, **N-Queens**
- **7 search algorithms**: BFS, DFS (with depth limit), UCS, Iterative Deepening,
  Greedy Best-First, A*, and Weighted A*
- **8 heuristics** across puzzles, each analyzed for admissibility & consistency
  (Misplaced Tiles, Manhattan, Linear Conflict, Euclidean, Chebyshev, …)
- **Solvability checking** for the 8-puzzle (inversion-count parity) and always-
  solvable random maze generation (seeded / reproducible)
- **Verified correctness**: every solution is replayed from the start state and
  confirmed to reach the goal before it is displayed
- **Performance comparison**: metrics table + bar charts for nodes expanded,
  runtime, path cost, and frontier size, with **CSV export**
- **Step-through visualization** of the solution path
- **In-app About panel** explaining each algorithm and heuristic in plain language

---

## 🚀 Setup & Run

Requires **Python 3.10+**.

```bash
# 1. (recommended) create a virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 2. install dependencies
pip install -r requirements.txt

# 3. launch the app
streamlit run app.py
```

The app opens in your browser (default: http://localhost:8501).

### Run the tests

```bash
pytest -q
```

### Use the solver from Python (no UI)

```python
from core.puzzles import EightPuzzle
from core.solver import run_algorithm

puzzle = EightPuzzle.random(shuffle_moves=25, seed=1)
result = run_algorithm(puzzle, "astar", heuristic_name="Manhattan Distance")
print(result.as_row())
```

---

## 🗂️ Project structure

```
puzzle-solver/
├── app.py                     # Streamlit entry point
├── core/
│   ├── puzzle_base.py         # Abstract Puzzle interface
│   ├── solver.py              # Runs an algorithm + verifies the solution
│   ├── metrics.py             # SearchResult (path + performance metrics)
│   ├── puzzles/               # eight_puzzle, maze, n_queens (+ registry)
│   ├── search/                # bfs, dfs, ucs, ids, greedy, astar (+ registry, utils)
│   └── heuristics/            # eight_puzzle_heuristics, maze_heuristics
├── ui/
│   ├── input_forms.py         # Per-puzzle configuration widgets
│   ├── visualizer.py          # Board / grid / queens rendering
│   ├── comparison_view.py     # Comparison table, charts, CSV export
│   └── about.py               # Plain-language algorithm notes
├── tests/test_search.py       # Correctness tests per puzzle/algorithm
├── docs/report.md             # Written analysis & experiments
├── docs/heuristic_analysis.md # Admissibility / consistency proofs
├── requirements.txt
└── README.md
```

**Design principle.** Every puzzle implements
`get_initial_state`, `get_actions`, `apply_action`, `is_goal`, `step_cost`, and
exposes its heuristics via `heuristics()`. Every algorithm operates *only* against
that interface, so adding a puzzle needs no new search code and adding an algorithm
needs no new puzzle code.

---

## 🧭 How to read the comparison

| Metric | Meaning |
|---|---|
| **Nodes expanded** | Search effort — how many states were popped and expanded |
| **Max frontier** | Memory proxy — peak size of the open list |
| **Path cost** | Solution quality — lower is better; optimal algorithms tie |
| **Runtime (ms)** | Wall-clock time |

Informed search (A*/Greedy) with a good heuristic expands **far fewer nodes** than
uninformed search (BFS/UCS/IDS). Make the puzzle harder and watch that gap grow —
that is exactly where uninformed search breaks down.

See [`docs/report.md`](docs/report.md) for the full analysis and experiments, and
[`docs/heuristic_analysis.md`](docs/heuristic_analysis.md) for the heuristic proofs.
