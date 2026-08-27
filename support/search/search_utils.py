"""Shared search primitives: the search Node, a heapq-backed priority queue, and
path reconstruction. Kept separate so every algorithm reuses identical plumbing.
"""

from __future__ import annotations

import heapq
import itertools
from dataclasses import dataclass, field
from typing import Any, List, Optional, Tuple


@dataclass
class Node:
    """A node in the search tree.

    ``parent``/``action`` let us reconstruct the solution path once the goal is
    reached, without storing full paths on the frontier.
    """

    state: Any
    parent: Optional["Node"] = None
    action: Any = None
    path_cost: float = 0.0          # g(n): accumulated cost from the start
    depth: int = 0

    def child(self, state: Any, action: Any, step_cost: float) -> "Node":
        return Node(
            state=state,
            parent=self,
            action=action,
            path_cost=self.path_cost + step_cost,
            depth=self.depth + 1,
        )


def reconstruct(node: Node) -> Tuple[List[Any], List[Any]]:
    """Walk parent pointers from ``node`` back to the root.

    Returns ``(states, actions)`` ordered start -> goal.
    """
    states: List[Any] = []
    actions: List[Any] = []
    cur: Optional[Node] = node
    while cur is not None:
        states.append(cur.state)
        if cur.action is not None:
            actions.append(cur.action)
        cur = cur.parent
    states.reverse()
    actions.reverse()
    return states, actions


class PriorityQueue:
    """Min-priority queue over items with tie-breaking and lazy deletion.

    ``heapq`` has no decrease-key, so we push duplicates and skip stale entries
    on pop (tracked via a per-item removal marker). A monotonic counter breaks
    ties deterministically (FIFO among equal priorities) and prevents Python
    from ever comparing the payload objects.
    """

    _REMOVED = object()

    def __init__(self) -> None:
        self._heap: List[Tuple[float, int, Any]] = []
        self._entry: dict[Any, list] = {}       # key -> [priority, count, item]
        self._counter = itertools.count()
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def __bool__(self) -> bool:
        return self._size > 0

    def push(self, key: Any, priority: float, item: Any) -> None:
        """Insert/oust ``item`` under ``key``. A cheaper priority replaces the old."""
        if key in self._entry:
            existing = self._entry[key]
            if existing[0] <= priority:
                return  # keep the better (or equal) existing entry
            existing[2] = PriorityQueue._REMOVED  # invalidate the stale entry
            self._size -= 1
        entry = [priority, next(self._counter), item]
        self._entry[key] = entry
        heapq.heappush(self._heap, entry)
        self._size += 1

    def pop(self) -> Any:
        """Remove and return the lowest-priority live item."""
        while self._heap:
            priority, _, item = heapq.heappop(self._heap)
            if item is not PriorityQueue._REMOVED:
                # Find the key by identity of the entry list is overkill; the
                # entry's item is unique, so drop its key mapping if it matches.
                self._size -= 1
                # Remove key bookkeeping (item carries its own key via .state).
                key = getattr(item, "state", None)
                if key in self._entry and self._entry[key][2] is item:
                    del self._entry[key]
                return item
        raise KeyError("pop from an empty priority queue")

    def contains(self, key: Any) -> bool:
        entry = self._entry.get(key)
        return entry is not None and entry[2] is not PriorityQueue._REMOVED

    def priority_of(self, key: Any) -> Optional[float]:
        entry = self._entry.get(key)
        if entry is None or entry[2] is PriorityQueue._REMOVED:
            return None
        return entry[0]
