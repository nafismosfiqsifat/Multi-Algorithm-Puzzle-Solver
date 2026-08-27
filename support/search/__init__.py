"""Search-algorithm registry.

Each entry describes an algorithm so the UI can render it generically:
``key -> {func, label, informed, params}``. ``informed`` algorithms require a
heuristic; ``params`` lists extra options the UI should expose.
"""

from __future__ import annotations

from core.search.astar import astar
from core.search.bfs import bfs
from core.search.dfs import dfs
from core.search.greedy import greedy
from core.search.ids import ids
from core.search.ucs import ucs

# Registry: stable key -> metadata. ``params`` values are (label, kind, default).
ALGORITHMS = {
    "bfs":    {"func": bfs,    "label": "Breadth-First Search", "informed": False, "params": {}},
    "dfs":    {"func": dfs,    "label": "Depth-First Search",   "informed": False,
               "params": {"depth_limit": ("Depth limit (blank = none)", "int_opt", None)}},
    "ucs":    {"func": ucs,    "label": "Uniform Cost Search",  "informed": False, "params": {}},
    "ids":    {"func": ids,    "label": "Iterative Deepening",  "informed": False,
               "params": {"max_depth": ("Max depth", "int", 50)}},
    "greedy": {"func": greedy, "label": "Greedy Best-First",    "informed": True,  "params": {}},
    "astar":  {"func": astar,  "label": "A* Search",            "informed": True,  "params": {}},
    "wastar": {"func": astar,  "label": "Weighted A*",          "informed": True,
               "params": {"weight": ("Weight (w >= 1)", "float", 2.0)}},
}

__all__ = ["ALGORITHMS", "bfs", "dfs", "ucs", "ids", "greedy", "astar"]
