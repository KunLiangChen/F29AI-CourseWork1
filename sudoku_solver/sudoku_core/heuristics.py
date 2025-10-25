# sudoku_core/heuristics.py
from collections import defaultdict

def compute_neighbors():
    """
    Precompute neighbors for all 81 cells.
    Returns dict: (r,c) -> set of (r2,c2)
    """
    neighbors = {}
    for r in range(9):
        for c in range(9):
            s = set()
            # same row
            for cc in range(9):
                if cc != c:
                    s.add((r, cc))
            # same col
            for rr in range(9):
                if rr != r:
                    s.add((rr, c))
            # same box
            br = 3 * (r // 3)
            bc = 3 * (c // 3)
            for rr in range(br, br + 3):
                for cc in range(bc, bc + 3):
                    if (rr, cc) != (r, c):
                        s.add((rr, cc))
            neighbors[(r, c)] = s
    return neighbors

# cached neighbors to avoid recomputing
NEIGHBORS = compute_neighbors()

def select_unassigned_variable(domains, assigned, use_mrv=True, use_degree=True):
    """
    domains: dict (r,c) -> set(possible values)
    assigned: set of (r,c) that are already assigned
    Returns chosen variable (r,c)
    """
    unassigned = [v for v in domains.keys() if v not in assigned]
    if not unassigned:
        return None

    if not use_mrv:
        # fallback: first unassigned
        return unassigned[0]

    # MRV: choose var with smallest domain size (>0)
    min_size = min(len(domains[v]) for v in unassigned)
    candidates = [v for v in unassigned if len(domains[v]) == min_size]

    if len(candidates) == 1 or not use_degree:
        return candidates[0]

    # Degree heuristic tiebreaker: choose var with most unassigned neighbors
    best = None
    best_deg = -1
    for v in candidates:
        deg = sum(1 for n in NEIGHBORS[v] if n not in assigned)
        if deg > best_deg:
            best_deg = deg
            best = v
    return best

def order_domain_values(var, domains, neighbors=NEIGHBORS, use_lcv=True):
    """
    var: (r,c)
    domains: dict
    Returns list of values ordered. If use_lcv True, sort by least constraining first.
    """
    vals = list(domains[var])
    if not use_lcv:
        return vals

    # LCV: for each value, count how many choices it would eliminate from neighbors
    impact = {}
    for val in vals:
        count = 0
        for n in neighbors[var]:
            if val in domains.get(n, set()):
                count += 1
        impact[val] = count
    # sort by increasing impact (least constraining first)
    vals.sort(key=lambda v: impact[v])
    return vals
