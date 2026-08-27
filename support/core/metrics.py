"""Search result + performance metrics container.

Every search algorithm returns a :class:`SearchResult`. It bundles the solution
(so the UI can animate it) with the empirical measurements the report needs:
nodes expanded / generated, peak frontier size, runtime, and path cost.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class SearchResult:
    """Outcome of running one algorithm on one puzzle instance."""

    algorithm: str
    solved: bool
    path: List[Any] = field(default_factory=list)        # sequence of states, start..goal
    actions: List[Any] = field(default_factory=list)     # actions taken between states
    path_cost: float = 0.0
    nodes_expanded: int = 0                               # states popped & goal-tested/expanded
    nodes_generated: int = 0                              # successor states created
    max_frontier: int = 0                                 # peak size of the frontier
    runtime_ms: float = 0.0
    heuristic: Optional[str] = None
    note: str = ""                                        # e.g. "depth limit reached"

    @property
    def path_length(self) -> int:
        """Number of moves in the solution (edges, not nodes)."""
        return max(len(self.path) - 1, 0)

    def as_row(self) -> Dict[str, Any]:
        """Flatten to a dict suitable for a pandas DataFrame / CSV export."""
        return {
            "Algorithm": self.algorithm,
            "Heuristic": self.heuristic or "—",
            "Solved": self.solved,
            "Path Length": self.path_length,
            "Path Cost": self.path_cost,
            "Nodes Expanded": self.nodes_expanded,
            "Nodes Generated": self.nodes_generated,
            "Max Frontier": self.max_frontier,
            "Runtime (ms)": round(self.runtime_ms, 3),
            "Note": self.note,
        }
