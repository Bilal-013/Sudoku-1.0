""" Informed solver combining CSP concepts: AC-3, MRV, and Degree Heuristics. """
from solvers.base import SudokuSolver
from typing import Generator, Any, List, Dict, Tuple
from collections import deque
import copy

class InformedSolver(SudokuSolver):
    """ 
    Optimized Constraint Satisfaction Problem (CSP) solver utilizing:
    - Minimum Remaining Values (MRV) heuristic
    - Degree Heuristic
    - AC-3 (Arc Consistency 3) for inference
    """
    
    def __init__(self, board: List[List[int]]):
        super().__init__(board)
        self.domains = copy.deepcopy(self.csp.domains)
        
    def _ac3(self) -> bool:
        queue = deque()
        for cell in self.domains.keys():
            if self.csp.board[cell[0]][cell[1]] == 0:
                for neighbor in self.csp.get_neighbors(cell):
                    if self.csp.board[neighbor[0]][neighbor[1]] == 0:
                        queue.append((cell, neighbor))
                        
        while queue:
            xi, xj = queue.popleft()
            if self._revise(xi, xj):
                if len(self.domains[xi]) == 0:
                    return False
                for xk in self.csp.get_neighbors(xi):
                    if xk != xj and self.csp.board[xk[0]][xk[1]] == 0:
                        queue.append((xk, xi))
        return True
        
    def _revise(self, xi: Tuple[int, int], xj: Tuple[int, int]) -> bool:
        revised = False
        domain_xi = self.domains[xi][:]
        for x in domain_xi:
            if len(self.domains[xj]) == 1 and x in self.domains[xj]:
                self.domains[xi].remove(x)
                revised = True
        return revised

    def _select_unassigned_variable(self):
        best_cell = None
        min_domain = float('inf')
        max_degree = -1
        
        for r in range(9):
            for c in range(9):
                if self.csp.board[r][c] == 0:
                    cell = (r, c)
                    d_len = len(self.domains[cell])
                    
                    unassigned_neighbors = sum(1 for n in self.csp.get_neighbors(cell) 
                                               if self.csp.board[n[0]][n[1]] == 0)
                                               
                    if d_len < min_domain:
                        min_domain = d_len
                        max_degree = unassigned_neighbors
                        best_cell = cell
                    elif d_len == min_domain:
                        if unassigned_neighbors > max_degree:
                            max_degree = unassigned_neighbors
                            best_cell = cell
        return best_cell

    def solve(self) -> List[List[int]]:
        self.metrics.start()
        
        if not self._ac3():
            self.metrics.stop()
            return None
            
        def backtrack():
            self.metrics.record_state()
            if self.csp.is_complete():
                return True
                
            cell = self._select_unassigned_variable()
            if not cell:
                return True
                
            vals = self.domains[cell][:]
            for val in vals:
                if self.csp.is_consistent(cell, val):
                    self.csp.apply_assignment(cell, val)
                    self.metrics.assignments_made += 1
                    
                    saved_domains = copy.deepcopy(self.domains)
                    self.domains[cell] = [val]
                    
                    if backtrack():
                        return True
                        
                    self.domains = saved_domains
                    self.csp.remove_assignment(cell)
                    self.metrics.record_backtrack()
                    
            return False

        if backtrack():
            self.metrics.stop()
            return self.csp.board
        self.metrics.stop()
        return None

    def solve_steps(self) -> Generator[Dict[str, Any], None, None]:
        self.metrics.start()
        
        yield {
            "board": [row[:] for row in self.csp.board],
            "action": "start",
            "cell": [-1, -1],
            "value": -1,
            "metrics": self.metrics.snapshot()
        }
        
        queue = deque()
        for cell in self.domains.keys():
            if self.csp.board[cell[0]][cell[1]] == 0:
                for neighbor in self.csp.get_neighbors(cell):
                    if self.csp.board[neighbor[0]][neighbor[1]] == 0:
                        queue.append((cell, neighbor))
                        
        while queue:
            xi, xj = queue.popleft()
            if self._revise(xi, xj):
                yield {
                    "board": [row[:] for row in self.csp.board],
                    "action": "propagate",
                    "cell": list(xi),
                    "value": -1,
                    "metrics": self.metrics.snapshot()
                }
                if len(self.domains[xi]) == 0:
                    self.metrics.stop()
                    yield {
                        "board": [row[:] for row in self.csp.board],
                        "action": "complete",
                        "cell": [-1, -1],
                        "value": -1,
                        "metrics": self.metrics.snapshot()
                    }
                    return
                for xk in self.csp.get_neighbors(xi):
                    if xk != xj and self.csp.board[xk[0]][xk[1]] == 0:
                        queue.append((xk, xi))
                        
        def backtrack():
            self.metrics.record_state()
            if self.csp.is_complete():
                return True
                
            cell = self._select_unassigned_variable()
            if not cell:
                return True
                
            vals = self.domains[cell][:]
            for val in vals:
                if self.csp.is_consistent(cell, val):
                    self.csp.apply_assignment(cell, val)
                    self.metrics.assignments_made += 1
                    
                    yield {
                        "board": [row[:] for row in self.csp.board],
                        "action": "assign",
                        "cell": list(cell),
                        "value": val,
                        "metrics": self.metrics.snapshot()
                    }
                    
                    saved_domains = copy.deepcopy(self.domains)
                    self.domains[cell] = [val]
                    
                    found = yield from backtrack()
                    if found:
                        return True
                        
                    self.domains = saved_domains
                    self.csp.remove_assignment(cell)
                    self.metrics.record_backtrack()
                    
                    yield {
                        "board": [row[:] for row in self.csp.board],
                        "action": "backtrack",
                        "cell": list(cell),
                        "value": val,
                        "metrics": self.metrics.snapshot()
                    }
            return False
            
        yield from backtrack()
        self.metrics.stop()
        
        yield {
            "board": [row[:] for row in self.csp.board],
            "action": "complete",
            "cell": [-1, -1],
            "value": -1,
            "metrics": self.metrics.snapshot()
        }
