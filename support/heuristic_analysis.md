# Heuristic Analysis — Admissibility & Consistency

A heuristic `h` is **admissible** if it never overestimates the true optimal
cost-to-go: `h(n) ≤ h*(n)` for all `n`. It is **consistent** (monotone) if for
every action from `n` to `n'`: `h(n) ≤ cost(n, n') + h(n')`. Consistency implies
admissibility and guarantees that A\* never needs to re-expand a closed node.

---

## 8-Puzzle

Let the goal place tile `t` at cell `g(t)`. Each move slides one tile to an
orthogonally adjacent cell at cost 1.

### Misplaced Tiles — `h₁ = #{tiles not in their goal cell}`
- **Admissible.** Each misplaced tile must move at least once to reach its goal
  cell, and a single move relocates exactly one tile by one cell. So at least `h₁`
  moves are required: `h₁ ≤ h*`.
- **Consistent.** A move changes the "misplaced" status of at most one tile (the
  one that moved), so `h₁(n) − h₁(n') ≤ 1 = cost(n, n')`, i.e.
  `h₁(n) ≤ 1 + h₁(n')`. ∎

### Manhattan Distance — `h₂ = Σ_t (|Δrow| + |Δcol|)`
- **Admissible.** Each tile needs at least its Manhattan distance in moves to reach
  its goal cell (each move cuts that distance by exactly 1), and moves relocate one
  tile at a time. Summing the independent lower bounds cannot exceed the true cost:
  `h₂ ≤ h*`.
- **Consistent.** One move changes exactly one tile's Manhattan distance by exactly
  ±1, so `|h₂(n) − h₂(n')| ≤ 1 = cost(n, n')`. Thus `h₂(n) ≤ 1 + h₂(n')`. ∎
- **Domination.** `h₂ ≥ h₁` (a misplaced tile contributes ≥1 to both, and a tile at
  distance `d` contributes `d ≥ 1` to `h₂`), so A\*+Manhattan expands ≤ the nodes of
  A\*+Misplaced. Confirmed empirically (§5.1 of the report).

### Linear Conflict — `h₃ = h₂ + 2·(#linear conflicts)`
Two tiles are in **linear conflict** when they are both in their goal row (or both
in their goal column), currently occupy that same line, and their required order is
reversed.
- **Admissible.** For each conflicting pair, at least one tile must temporarily
  leave the line and return — **2 extra moves** beyond Manhattan — and these extra
  moves are disjoint from the Manhattan lower bound (they are moves *perpendicular*
  to and then back into the line, not counted by Manhattan). Adding `2` per conflict
  therefore keeps `h₃ ≤ h*`. Conflicts in rows and columns are counted separately
  and never double-charge the same move, preserving the bound.
- **Consistency.** `h₃` remains consistent: a single slide changes the Manhattan
  term by ±1 and can create/resolve at most conflicts consistent with a ≤1 net
  change relative to the step cost in the standard construction; the widely used
  result (Hansson, Mayer & Yung) establishes monotonicity of Linear Conflict.
- **Domination.** `h₃ ≥ h₂ ≥ h₁`. Empirically Linear Conflict expands the fewest
  nodes of the three (§5.1).

---

## Maze / Grid Pathfinding

Goal cell fixed at `(gr, gc)`; orthogonal moves cost 1, diagonal moves cost √2.

### Manhattan — `|Δr| + |Δc|`
- **Admissible (4-connected).** Any 4-connected path must change row and column by
  at least `|Δr|` and `|Δc|` unit steps respectively, so `≥ |Δr| + |Δc|` moves are
  needed. Walls only *lengthen* real paths, so the bound still holds. `h ≤ h*`.
- **Consistent.** Moving to an orthogonal neighbor changes `h` by exactly ±1 = the
  step cost. `h(n) ≤ 1 + h(n')`. ∎
- *Note:* on an **8-connected** grid Manhattan can overestimate (a diagonal step of
  cost √2 reduces Manhattan by 2), so it is **not** admissible there — use Euclidean
  or Chebyshev when diagonals are enabled.

### Euclidean — `√(Δr² + Δc²)`
- **Admissible.** Straight-line distance lower-bounds any path length in the plane,
  under both 4- and 8-connected movement. `h ≤ h*`.
- **Consistent.** By the triangle inequality, `h(n) ≤ dist(n, n') + h(n')`, and the
  step cost equals the Euclidean length of the move (1 or √2), so
  `h(n) ≤ cost(n, n') + h(n')`. ∎

### Chebyshev (Diagonal) — `max(|Δr|, |Δc|)`
- **Admissible & consistent (8-connected, unit-ish cost).** When a diagonal move
  advances both axes at once, the minimum number of moves is `max(|Δr|, |Δc|)`. Each
  move changes Chebyshev distance by at most 1 ≤ step cost, giving consistency.
- On a **4-connected** grid Chebyshev *under*-estimates (it ignores that you cannot
  move diagonally), so it remains admissible but weaker than Manhattan → it expands
  more nodes (see report §5.2: Euclidean/Chebyshev expand more than Manhattan on the
  orthogonal maze).

---

## N-Queens (constructive)

### Remaining Rows — `h = N − (#queens placed)`
- **Admissible & consistent — in fact exact.** Every solution places exactly one
  queen per remaining row at cost 1 each, so precisely `N − placed` moves remain:
  `h = h*`. Each action places one queen, decreasing both `h` and the true remaining
  cost by exactly 1, so `h(n) = 1 + h(n') = cost(n,n') + h(n')`. An exact heuristic
  makes A\* expand essentially only nodes on a solution path.

### Attacking Pairs (relaxed) — `#pairs of placed queens that attack`
- On **legal** partial states this is always `0` (placements are constrained to be
  non-attacking), so it is trivially admissible here. It is included mainly to
  illustrate a relaxation-based heuristic and to contrast with the exact one.

---

## Takeaways

1. **Admissibility guarantees optimality** of A\* / Weighted-A\* (bounded) — every
   admissible heuristic above yields optimal-cost solutions in the experiments.
2. **Consistency guarantees efficiency** — no reopening of closed nodes, so A\*'s
   node counts are tight.
3. **More informed (larger, still admissible) ⇒ fewer expansions.** The strict
   ordering `Misplaced < Manhattan < Linear Conflict` in measured node counts is the
   domination theorem made visible.
