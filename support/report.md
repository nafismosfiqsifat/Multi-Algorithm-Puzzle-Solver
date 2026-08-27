# Multi-Algorithm Puzzle Solver — Report

**Course:** CSE 440 — Artificial Intelligence
**Deliverable:** A modular Streamlit + Python application that solves multiple
puzzle types with multiple search algorithms and compares their performance.

---

## 1. Problem formulations

Every puzzle is expressed as a search problem `⟨S, s₀, Actions, Result, GoalTest, StepCost⟩`
and implements the shared `Puzzle` interface, so all algorithms run unchanged
across all puzzles.

### 1.1 8-Puzzle (generalizes to the 15-puzzle)
- **State:** a permutation of `0..8` (0 = blank), stored as a length-9 tuple.
- **Initial state:** any solvable permutation (validated by inversion parity).
- **Actions:** slide the blank `Up / Down / Left / Right` (only in-bounds moves).
- **Transition model:** swap the blank with the neighboring tile in that direction.
- **Goal test:** state equals `(1,2,3,4,5,6,7,8,0)`.
- **Step cost:** 1 per slide.
- **State space:** `9!/2 = 181,440` reachable states (even permutations only).

### 1.2 Maze / Pathfinding
- **State:** a grid cell `(row, col)`.
- **Initial state:** the start cell.
- **Actions:** 4-connected `N/S/E/W`, optionally 8-connected (adds diagonals).
- **Transition model:** move to the adjacent free cell (walls and out-of-bounds
  blocked; diagonals may not cut between two wall corners).
- **Goal test:** state equals the goal cell.
- **Step cost:** 1 orthogonal, √2 diagonal.

### 1.3 N-Queens (constructive formulation)
- **State:** a tuple of column indices, one per already-placed row (top-down).
- **Initial state:** `()` (empty board).
- **Actions:** a safe column for a queen in the next empty row.
- **Transition model:** append the chosen column.
- **Goal test:** all `N` rows filled (a complete non-attacking placement).
- **Step cost:** 1 per queen; every solution lies at depth `N`.

---

## 2. Algorithm descriptions

| Algorithm | Frontier | Complete | Optimal | Notes |
|---|---|---|---|---|
| **BFS** | FIFO queue | Yes | Yes (unit cost) | Goal-tested on generation |
| **DFS** | LIFO stack | Yes (finite) | No | Optional depth limit |
| **UCS** | min-priority by `g` | Yes | Yes (any ≥0 cost) | Dijkstra; goal-tested on pop |
| **IDS** | iterative DFS | Yes | Yes (unit cost) | Linear memory, re-expands shallow nodes |
| **Greedy** | min-priority by `h` | No | No | Fast, easily misled |
| **A\*** | min-priority by `g+h` | Yes | Yes (admissible `h`) | Balances cost-so-far vs. cost-to-go |
| **Weighted A\*** | min-priority by `g+w·h` | Yes | Bounded (`≤ w·opt`) | Speed/optimality knob |

All priority-queue searches share one `heapq`-backed `PriorityQueue` with lazy
deletion and deterministic tie-breaking (`core/search/search_utils.py`). Visited
tracking uses sets / dicts of hashable states.

Pseudocode (A\*, representative of the priority-queue family):

```
frontier ← priority queue ordered by f(n) = g(n) + w·h(n)
best_g[s₀] ← 0;  push s₀
while frontier not empty:
    n ← pop lowest f
    if GoalTest(n): return reconstruct(n)
    for a in Actions(n.state):
        s' ← Result(n.state, a);  g ← n.g + StepCost(n.state, a)
        if s' unseen or g < best_g[s']:
            best_g[s'] ← g;  push child with f = g + w·h(s')
```

---

## 3. Heuristic design & analysis

Full proofs are in [`heuristic_analysis.md`](heuristic_analysis.md). Summary:

| Puzzle | Heuristic | Admissible | Consistent | Intuition |
|---|---|---|---|---|
| 8-Puzzle | Misplaced Tiles | ✅ | ✅ | Each wrong tile needs ≥1 move |
| 8-Puzzle | Manhattan Distance | ✅ | ✅ | Sum of per-tile grid distances; dominates Misplaced |
| 8-Puzzle | Linear Conflict | ✅ | ✅ | Manhattan + 2 per in-line reversed pair; dominates Manhattan |
| Maze | Manhattan | ✅ | ✅ | Exact when the direct L-path is unobstructed |
| Maze | Euclidean | ✅ | ✅ | Straight-line lower bound |
| Maze | Chebyshev | ✅ | ✅ (8-conn) | Diagonal-aware distance |
| N-Queens | Remaining Rows | ✅ | ✅ | `N − placed` = exact moves left |

**Domination:** `Misplaced ≤ Manhattan ≤ Linear Conflict ≤ h*`. A more informed
(larger, still admissible) heuristic expands no more nodes than a weaker one — the
experiments below confirm this exactly.

---

## 4. Experimental setup

- **Instances:** seeded, reproducible puzzle instances of increasing difficulty.
  8-puzzle difficulty is controlled by the number of random shuffle moves from the
  goal (which also bounds the optimal solution length); maze difficulty by grid
  size. Each data point averages **5 seeds** (`seed = 0..4`).
- **Metrics:** nodes expanded (primary effort measure), optimal path length/cost,
  runtime, peak frontier. Captured by `core/metrics.py`; every solution is replayed
  and verified before it is counted (`core/solver.verify_solution`).
- **Hardware/software:** Python 3.14, standard-library data structures (`heapq`,
  `deque`, `set`). Reproduce with the benchmark snippet in §7.

---

## 5. Results

### 5.1 8-Puzzle — nodes expanded vs. difficulty (avg of 5 seeds)

| Shuffle (≈opt len) | BFS | UCS | IDS | A\* Misplaced | A\* Manhattan | A\* Lin.Conflict | Greedy (Manh.) |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 6  (~6)  | 40    | 70    | 183    | 6    | 6   | 6   | 6   |
| 10 (~10) | 343   | 556   | 1,665  | 35   | 16  | 12  | 30  |
| 14 (~14) | 2,640 | 4,291 | 11,262 | 221  | 59  | 45  | 33  |
| 18 (~17) | 12,489| 19,203| 61,900 | 1,104| 198 | 135 | 112 |

*All uninformed searches and all A\* variants return the **optimal** cost; Greedy
does not (it trades optimality for speed).*

### 5.2 Maze — 20×20 grid, nodes expanded (avg of 5 seeds, ~38-step optimal path)

| BFS | UCS | A\* Manhattan | A\* Euclidean | Greedy (Manh.) | DFS (path len) |
|---:|---:|---:|---:|---:|---:|
| 284 | 284 | 184 | 243 | 48 | 67 (vs 38 optimal) |

---

## 6. Discussion

**Informed vs. uninformed.** On the 8-puzzle the gap explodes with difficulty. At
~17 moves, BFS expands **12,489** nodes and IDS **61,900**, while A\*+Manhattan
expands **198** and A\*+Linear-Conflict just **135** — a **60–90×** reduction for
the *same optimal answer*. This is exactly where uninformed search breaks down: its
effort grows with the branching factor raised to the solution depth, whereas a good
heuristic prunes the exponential.

**Heuristic domination is visible in the numbers.** `Misplaced (1,104) > Manhattan
(198) > Linear Conflict (135)` at shuffle 18 — the strict node-count ordering
predicted by the domination relation. Linear Conflict's +2-per-conflict bonus keeps
it admissible while expanding ~30% fewer nodes than plain Manhattan.

**UCS vs. BFS.** UCS expands *more* nodes than BFS here (e.g. 19,203 vs 12,489)
because with unit costs BFS can goal-test on generation and stop earlier, while UCS
must pop a goal node with minimal `g`. Both are optimal; BFS is the better choice
when all steps cost the same, UCS when they don't (e.g. the diagonal maze).

**Greedy — fast but fallible.** Greedy expands the fewest nodes on the maze (48) and
is competitive on the 8-puzzle, but its solutions are **not optimal** (52-move
solutions on 20-move-optimal boards were observed). It is the right tool only when
*any* solution quickly beats the *best* solution slowly.

**DFS.** On the maze DFS returns a 67-step path where the optimum is 38 — completing
quickly but wandering. Useful for low memory / "just find a path" settings.

**Tradeoffs summary.**
- *Optimal + simple, equal costs* → **BFS**
- *Optimal, weighted costs* → **UCS** or **A\*** (prefer A\* with a heuristic)
- *Optimal + memory-bound* → **IDS** (time cost) or **IDA\*** (future work)
- *Fastest good-enough* → **Greedy** or **Weighted A\*** (bounded suboptimality)

---

## 7. Reproducing the experiments

```python
from core.puzzles import EightPuzzle, Maze
from core.solver import run_algorithm

p = EightPuzzle.random(shuffle_moves=18, seed=0)
for algo, h in [("bfs", None), ("astar", "Manhattan Distance"),
                ("astar", "Linear Conflict"), ("greedy", "Manhattan Distance")]:
    r = run_algorithm(p, algo, heuristic_name=h)
    print(algo, h, r.path_cost, r.nodes_expanded)
```

The Streamlit app (`streamlit run app.py`) runs the same comparison interactively
and exports the results table as CSV.

---

## 8. Limitations & future work

- **IDA\*** and **pattern-database heuristics** for the 15-puzzle — the current A\*
  holds the full frontier in memory, which limits scaling; IDA\* removes that limit.
- **Linear Conflict for columns and rows** is implemented; additive PDBs would push
  the 15-puzzle further.
- **Local search** (Hill Climbing / Simulated Annealing with restarts) for N-Queens
  at large `N`, where constructive search's frontier grows.
- **Bidirectional search** for the maze.
- **Parallel / batched** experiments and a built-in benchmark harness in the UI.
- **Optional LLM assistant** (Section 10 of the brief) to explain a given run —
  intentionally decoupled so the solver stands alone.
