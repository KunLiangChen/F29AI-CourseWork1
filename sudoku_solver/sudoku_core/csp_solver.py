# sudoku_core/csp_solver.py
from .heuristics import select_unassigned_variable, order_domain_values, NEIGHBORS
from .inference import forward_checking, restore_inferences, ac3
import time

# Try to import a project Metrics, else provide a simple fallback
try:
    from .metrics import Metrics
except Exception:
    class Metrics:
        def __init__(self):
            self.assignments = 0
            self.backtracks = 0
            self.start_time = None
            self.end_time = None
        def start(self):
            self.start_time = time.time()
        def stop(self):
            self.end_time = time.time()
        def record_assignment(self):
            self.assignments += 1
        def record_backtrack(self):
            self.backtracks += 1
        def summary(self):
            return {
                "assignments": self.assignments,
                "backtracks": self.backtracks,
                "time": (self.end_time - self.start_time) if self.start_time and self.end_time else None
            }

class CSPSolver:
    def __init__(self, board, use_mrv=True, use_lcv=True, use_fc=True, use_ac3=False):
        """
        board: SudokuBoard instance
        Options:
            use_mrv, use_lcv: heuristics
            use_fc: forward checking (during search)
            use_ac3: run AC-3 once at initialization
        """
        self.board = board
        self.use_mrv = use_mrv
        self.use_lcv = use_lcv
        self.use_fc = use_fc
        self.use_ac3 = use_ac3

        self.metrics = Metrics()
        self.domains = {}   # (r,c) -> set of possible values
        self.assigned = set()
        self.step_log = []  
        self._step_counter = 0  
        self._init_domains()

        if self.use_ac3:
            ac3(self.domains)

    def _is_initial_board_valid(self):
        """Check whether current board violates Sudoku constraints."""
        grid = self.board.grid
        for r in range(9):
            for c in range(9):
                val = grid[r, c]
                if val != 0:
                    grid[r, c] = 0
                    if not self.board.is_valid(r, c, val):
                        grid[r, c] = val  
                        return False
                    grid[r, c] = val  
        return True

    def _init_domains(self):
        """Initialize domains from board state."""
        for r in range(9):
            for c in range(9):
                if self.board.grid[r, c] != 0:
                    # assigned cell has singleton domain
                    self.domains[(r, c)] = {int(self.board.grid[r, c])}
                    self.assigned.add((r, c))
                else:
                    # start with 1..9 then remove inconsistent
                    possible = set(range(1, 10))
                    # remove values in same row/col/box
                    for rr, cc in NEIGHBORS[(r, c)]:
                        val = self.board.grid[rr, cc]
                        if val != 0 and val in possible:
                            possible.discard(int(val))
                    self.domains[(r, c)] = possible

    def _assign(self, var, value):
        """Assign value to var on board and mark as assigned."""
        r, c = var
        self.board.set_value(r, c, value)
        self.assigned.add(var)

    def _unassign(self, var):
        r, c = var
        self.board.clear_value(r, c)
        if var in self.assigned:
            self.assigned.remove(var)

    def _log_step(self, message: str):
        self._step_counter += 1
        log_entry = f"Step {self._step_counter}: {message}"
        self.step_log.append(log_entry)

    def solve(self):
        """Public entry point. Returns True if solved."""
        self.metrics.start()
        if not self._is_initial_board_valid():
            return False
        success = self._backtrack()
        self.metrics.stop()
        return success

    def _backtrack(self):
        # goal test
        if len(self.assigned) == 81:
            return True
        
        var = select_unassigned_variable(self.domains, self.assigned,
                                         use_mrv=self.use_mrv, use_degree=True)
        
        r, c = var
        domain = list(self.domains[var])
        self._log_step(f"Select cell ({r},{c}), domain={domain}")

        for value in order_domain_values(var, self.domains, use_lcv=self.use_lcv):
            # check consistency quickly using board.is_valid
            if not self.board.is_valid(r, c, value):
                self._log_step(f"  Try ({r},{c})={value}: INVALID (constraint violation)")
                continue

            self._log_step(f"  Try ({r},{c})={value}: VALID")
            
            # tentatively assign
            self._assign(var, value)
            self.metrics.record_assignment()
            self._log_step(f"    Assigned ({r},{c})={value}")

            # maintain domains: remove value from var domain (store old)
            old_domain_var = self.domains[var]
            self.domains[var] = {value}

            inferences = None
            failure = False
            if self.use_fc:
                inferences = forward_checking(self.domains, var, value)
                if inferences is None:
                    failure = True
                    self._log_step(f"    Forward checking failed for ({r},{c})={value}")
                else:
                    self._log_step(f"    Forward checking passed, eliminated some values")

            if not failure:
                result = self._backtrack()
                if result:
                    return True

            # undo
            self.metrics.record_backtrack()
            self._log_step(f"  Backtrack from ({r},{c})={value}")
            
            # restore domains
            self.domains[var] = old_domain_var
            if inferences:
                restore_inferences(self.domains, inferences)
            self._unassign(var)

        return False
