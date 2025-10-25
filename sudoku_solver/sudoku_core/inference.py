# sudoku_core/inference.py
from collections import deque
from .heuristics import NEIGHBORS

def forward_checking(domains, var, value):
    inferences = {}
    affected = []

    for n in NEIGHBORS[var]:
        if value in domains.get(n, set()):
            removed = inferences.setdefault(n, set())
            removed.add(value)
            domains[n] = domains[n] - {value}
            affected.append(n)

            if len(domains[n]) == 0:
                # restore before returning failure
                for cell in affected:
                    domains[cell] = domains[cell].union(inferences[cell])
                return None

    return inferences


def restore_inferences(domains, inferences):
    """
    Put back values removed by forward_checking.
    inferences: dict {cell: set_of_values_removed}
    """
    if not inferences:
        return
    for cell, removed in inferences.items():
        domains[cell] = domains[cell].union(removed)

def revise(domains, xi, xj):
    """
    Helper for AC-3: try to remove incompatible values from xi
    where xi and xj are neighboring cells.
    Return True if domain of xi changed.
    """
    removed_any = False
    to_remove = set()
    for x in domains[xi]:
        # if no value in domains[xj] can satisfy constraint (i.e., != x), then remove x
        if all(x == y for y in domains[xj]):
            to_remove.add(x)
    if to_remove:
        domains[xi] = domains[xi] - to_remove
        removed_any = True
    return removed_any

def ac3(domains, neighbors=NEIGHBORS):
    """
    AC-3 algorithm for arc consistency on binary inequality constraints.
    domains is modified in place. Returns True if success (no empty domains),
    False if any domain becomes empty.
    """
    queue = deque()
    for xi in domains:
        for xj in neighbors[xi]:
            queue.append((xi, xj))

    while queue:
        xi, xj = queue.popleft()
        if revise(domains, xi, xj):
            if len(domains[xi]) == 0:
                return False
            for xk in neighbors[xi]:
                if xk != xj:
                    queue.append((xk, xi))
    return True
