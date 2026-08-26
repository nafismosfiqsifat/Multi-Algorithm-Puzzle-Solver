# Multi-Algorithm Puzzle Solver
### CSE 440 — Artificial Intelligence | Project Instructions

---

## 1. Project Overview

Build a puzzle-solver application that tackles diverse puzzle types using multiple
search algorithms, with custom heuristics for informed search. The system should
provide user-friendly input, algorithm selection, and side-by-side performance
comparison, backed by clear documentation and analysis.

**Core deliverable:** A working, documented, modular codebase (Streamlit UI +
Python backend) that lets a user pick a puzzle, pick an algorithm, solve it, and
see how different algorithms perform against each other.

---

## 2. Learning Objectives Addressed

- Problem formulation (states, actions, transition model, goal test, path cost)
- Uninformed search: BFS, DFS, Uniform Cost Search, Iterative Deepening
- Informed search: Greedy Best-First, A*, Weighted A*
- Heuristic design and admissibility/consistency analysis
- Local search (optional extension): Hill Climbing, Simulated Annealing
- Empirical performance evaluation of search algorithms

---

## 3. Suggested Puzzles to Support

Pick at least **2–3** for a solid submission; more puzzles = stronger project.

| Puzzle | State Space | Good For |
|---|---|---|
| 8-Puzzle / 15-Puzzle | Tile permutations | A*, BFS, IDA*, heuristic design (Manhattan distance, misplaced tiles) |
| N-Queens | Queen placements | Backtracking, local search, CSP framing |
| Rubik's Cube (2x2 optional) | Cube orientations | IDA*, pattern database heuristics (stretch goal) |
| Maze / Pathfinding Grid | Grid cells | BFS, DFS, UCS, A* with Euclidean/Manhattan heuristic |
| Sudoku | Grid with constraints | Backtracking + constraint propagation (CSP framing) |
| Water Jug Problem | Jug volume states | Classic BFS/DFS demo, good for simple state-space intro |

**Recommendation:** 8-Puzzle (or 15-Puzzle) + Maze Pathfinding as the two anchor
puzzles — they map cleanly onto the same generic search framework and make
heuristic comparison intuitive to visualize.

---

## 4. Algorithms to Implement

### Uninformed
- Breadth-First Search (BFS)
- Depth-First Search (DFS)
- Uniform Cost Search (UCS)
- Iterative Deepening Search (IDS)

### Informed
- Greedy Best-First Search
- A* Search
- (Optional) IDA* — memory-efficient A* variant, good for 15-puzzle
- (Optional) Weighted A* — for speed/optimality tradeoff analysis

### Heuristics (design at least 2 per puzzle, compare them)
- **8/15-Puzzle:** Misplaced Tiles, Manhattan Distance, Linear Conflict (bonus)
- **Maze:** Manhattan Distance, Euclidean Distance, Diagonal (Chebyshev)
- **N-Queens (if using local search):** Number of attacking pairs

State clearly whether each heuristic is **admissible** and **consistent**, with a
short proof sketch or counterexample in the documentation.

---

## 5. System Architecture

```
puzzle-solver/
├── app.py                     # Streamlit entry point (UI)
├── core/
│   ├── puzzle_base.py         # Abstract Puzzle interface (state, actions, goal_test, cost)
│   ├── puzzles/
│   │   ├── eight_puzzle.py
│   │   ├── maze.py
│   │   └── n_queens.py
│   ├── search/
│   │   ├── bfs.py
│   │   ├── dfs.py
│   │   ├── ucs.py
│   │   ├── ids.py
│   │   ├── greedy.py
│   │   ├── astar.py
│   │   └── search_utils.py    # Node class, PriorityQueue wrapper, path reconstruction
│   ├── heuristics/
│   │   ├── eight_puzzle_heuristics.py
│   │   └── maze_heuristics.py
│   └── metrics.py             # Tracks nodes expanded, time, memory, path length
├── ui/
│   ├── input_forms.py         # Puzzle configuration widgets
│   ├── visualizer.py          # Board/grid/tree rendering
│   └── comparison_view.py     # Side-by-side algorithm comparison charts
├── tests/
│   └── test_*.py              # Unit tests per puzzle/algorithm
├── docs/
│   ├── report.md              # Written analysis (see Section 8)
│   └── heuristic_analysis.md
├── requirements.txt
└── README.md
```

**Design principle:** Every puzzle implements a common interface
(`get_initial_state`, `get_actions(state)`, `apply_action(state, action)`,
`is_goal(state)`, `step_cost(state, action)`), and every algorithm operates only
against that interface. This decoupling is what makes the "modular" and
"multiple search algorithms" requirements clean to satisfy — a new puzzle
doesn't require new search code, and a new algorithm doesn't require new puzzle
code.

---

## 6. Functional Requirements

### 6.1 Input
- Puzzle type selector (dropdown)
- Puzzle-specific configuration:
  - 8-puzzle: random shuffle button, or manual tile entry, with a solvability check
  - Maze: grid size, click-to-place walls/start/goal, or random maze generator
  - N-Queens: board size (N)
- Validation: reject unsolvable/invalid configurations with a clear message

### 6.2 Algorithm Selection
- Multi-select or dropdown to choose one or more algorithms to run
- Optional parameters exposed (e.g., heuristic choice for A*/Greedy, weight for
  Weighted A*, depth limit for IDS)

### 6.3 Solving & Visualization
- Run button triggers solve; show a spinner/progress indicator
- Animate or step through the solution path
- Display: solution path, path length/cost, nodes expanded, nodes generated,
  max frontier size, runtime (ms), peak memory (optional)

### 6.4 Performance Comparison
- Run multiple algorithms on the same puzzle instance
- Show a comparison table and bar/line charts for: runtime, nodes expanded,
  path optimality, memory usage
- Allow export of results (CSV) for the written report

### 6.5 Documentation in-app
- Short "About" panel explaining each algorithm and heuristic in plain language

---

## 7. Non-Functional Requirements

- **Modularity:** puzzle logic, search logic, and UI must be separable (see
  architecture above)
- **Correctness:** every returned solution must be verified (replay actions
  from initial state and confirm goal reached) before being shown
- **Performance:** avoid recomputation; use efficient data structures
  (`heapq` for priority queues, sets/frozensets for visited-state tracking)
- **Reproducibility:** allow fixed random seeds for shuffles/mazes
- **Testing:** unit tests for each search algorithm on a small known instance
  with a hand-verified optimal solution

---

## 8. Documentation & Report Requirements

Your `docs/report.md` should include:

1. **Problem formulations** for each puzzle (state, initial state, actions,
   transition model, goal test, path cost)
2. **Algorithm descriptions** — brief pseudocode or explanation per algorithm
3. **Heuristic design & analysis** — definition, admissibility/consistency
   justification, and intuition for why it guides search well
4. **Experimental setup** — puzzle instances used, hardware, how trials were run
5. **Results tables/charts** — nodes expanded, runtime, path cost per
   algorithm per puzzle instance (use multiple instances of varying difficulty)
6. **Discussion** — which algorithm/heuristic combo performed best and why;
   tradeoffs (optimality vs. speed vs. memory); where uninformed search breaks
   down as puzzle size grows
7. **Limitations & future work** — e.g., pattern database heuristics, IDA* for
   15-puzzle, parallel search

---

## 9. Suggested Milestones

| Milestone | Deliverable |
|---|---|
| 1 | Puzzle interface + one puzzle (8-puzzle) + BFS/DFS working in console |
| 2 | Add UCS, A*, Greedy + at least 2 heuristics for 8-puzzle |
| 3 | Add second puzzle (Maze) reusing the same search modules |
| 4 | Build Streamlit UI: input forms + visualization |
| 5 | Add performance metrics tracking + comparison view (charts/table) |
| 6 | Testing pass + write `docs/report.md` with experiments and analysis |
| 7 | Polish, README, final run-through, optional LLM chatbot layer |

---

## 10. Optional Extensions (stretch goals)

- **LLM chatbot component:** a sidebar assistant that explains the chosen
  algorithm's behavior on the current run, or lets the user ask "why did A*
  expand more nodes here?" — keep this decoupled from the core solver so the
  project still stands on its own without it
- IDA* and pattern-database heuristics for 15-puzzle
- Simulated Annealing / Hill Climbing for N-Queens with restarts
- Interactive step-by-step frontier/tree visualization
- Solvability checker with explanation (e.g., inversion count parity for
  8-puzzle)

---

## 11. Tech Stack

- **Language:** Python 3.10+
- **UI:** Streamlit
- **Core libs:** `heapq`, `collections` (deque), `dataclasses`, `numpy` (grid
  ops), `matplotlib` or `plotly` (charts), `pandas` (metrics tables)
- **Testing:** `pytest`
- **Environment:** `requirements.txt` + optional `conda`/`venv` setup notes in
  README

---

## 12. Grading-Alignment Checklist

- [ ] At least 3 search algorithms implemented and correct
- [ ] At least 2 custom heuristics implemented and analyzed for admissibility
- [ ] At least 2 distinct puzzle types supported via a shared interface
- [ ] Streamlit UI: input, algorithm selection, visualization, comparison
- [ ] Performance metrics captured and compared (table/chart)
- [ ] Unit tests for search correctness
- [ ] Written report with formulations, results, and discussion
- [ ] Clean, modular, commented code with a README covering setup and usage
