"""Plain-language explanations for the in-app About panel (functional req 6.5)."""

ALGORITHM_NOTES = {
    "Breadth-First Search": "Explores level by level. Complete; optimal when every move costs the same. Memory grows fast (whole frontier held).",
    "Depth-First Search": "Dives down one branch before backtracking. Low memory; not optimal and can wander. Depth limit tames infinite descent.",
    "Uniform Cost Search": "Dijkstra over states — always expands the cheapest-so-far node. Optimal for any non-negative costs; ignores the goal's location.",
    "Iterative Deepening": "Repeated depth-limited DFS with a growing bound. BFS-like optimality with DFS-like memory, at the price of re-expanding shallow nodes.",
    "Greedy Best-First": "Follows the heuristic straight toward the goal. Very fast, low memory, but neither complete nor optimal — it can be fooled.",
    "A* Search": "Orders by f = g + h. Optimal when h is admissible; the gold standard that balances cost-so-far against estimated cost-to-go.",
    "Weighted A*": "f = g + w·h with w>1. Trades a little optimality (bounded by w) for big speed/memory gains as puzzles grow.",
}

OVERVIEW = """
This tool solves several classic AI puzzles with a shared search engine. Every
puzzle implements one small interface (states, actions, goal test, cost), and
every algorithm runs against *only* that interface — so the same A* that solves
the 8-puzzle also solves the maze and N-Queens without changes.

**How to read the comparison:** *nodes expanded* measures search effort,
*max frontier* proxies memory, *path cost* measures solution quality, and
*runtime* is wall-clock. Informed search (A*/Greedy) should expand far fewer
nodes than uninformed search (BFS/UCS/IDS) when the heuristic is good — watch that
gap widen as you make the puzzle harder.
"""
