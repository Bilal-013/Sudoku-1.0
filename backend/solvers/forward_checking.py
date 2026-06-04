""" Backtracking augmented with Forward Checking for early failure detection. """
from solvers.base import SudokuSolver
from typing import Generator, Any, List, Dict
import copy

class ForwardCheckingSolver(SudokuSolver):
    """ 
    CSP Solver emphasizing Forward Checking inferences upon each variable assignment 
    to aggressively prune invalid search spaces early.
    """
    
    def __init__(self, board: List[List[int]]):
        super().__init__(board)
        self.current_domains = copy.deepcopy(self.csp.domains)
    
    def solve(self) -> List[List[int]]:
        self.metrics.start()
        
        def forward_check(cell, value, domains):
            removed = {}
            for neighbor in self.csp.get_neighbors(cell):
                if self.csp.board[neighbor[0]][neighbor[1]] == 0:
                    if neighbor in domains and value in domains[neighbor]:
                        domains[neighbor].remove(value)
                        if neighbor not in removed:
                            removed[neighbor] = []
                        removed[neighbor].append(value)
                        if len(domains[neighbor]) == 0:
                            return False, removed
            return True, removed
            
        def backtrack(domains):
            self.metrics.record_state()
            if self.csp.is_complete():
                return True
                
            cell = None
            for r in range(9):
                for c in range(9):
                    if self.csp.board[r][c] == 0:
                        cell = (r, c)
                        break
                if cell:
                    break
            if not cell:
                return True
                
            for val in list(domains.get(cell, [])):
                if self.csp.is_consistent(cell, val):
                    self.csp.apply_assignment(cell, val)
                    self.metrics.assignments_made += 1
                    
                    is_valid, removed = forward_check(cell, val, domains)
                    
                    if is_valid:
                        if backtrack(domains):
                            return True
                            
                    for n, vals in removed.items():
                        domains[n].extend(vals)
                        
                    self.csp.remove_assignment(cell)
                    self.metrics.record_backtrack()
                    
            return False

        if backtrack(self.current_domains):
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
        
        def forward_check(cell, value, domains):
            removed = {}
            for neighbor in self.csp.get_neighbors(cell):
                if self.csp.board[neighbor[0]][neighbor[1]] == 0:
                    if neighbor in domains and value in domains[neighbor]:
                        domains[neighbor].remove(value)
                        if neighbor not in removed:
                            removed[neighbor] = []
                        removed[neighbor].append(value)
                        if len(domains[neighbor]) == 0:
                            return False, removed
            return True, removed
            
        def backtrack(domains):
            self.metrics.record_state()
            if self.csp.is_complete():
                return True
                
            cell = None
            for r in range(9):
                for c in range(9):
                    if self.csp.board[r][c] == 0:
                        cell = (r, c)
                        break
                if cell:
                    break
            if not cell:
                return True
                
            for val in list(domains.get(cell, [])):
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
                    
                    is_valid, removed = forward_check(cell, val, domains)
                    
                    if removed:
                        yield {
                            "board": [row[:] for row in self.csp.board],
                            "action": "propagate",
                            "cell": list(cell),
                            "value": val,
                            "metrics": self.metrics.snapshot()
                        }
                        
                    if is_valid:
                        found = yield from backtrack(domains)
                        if found:
                            return True
                            
                    for n, vals in removed.items():
                        domains[n].extend(vals)
                        
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

        yield from backtrack(self.current_domains)
        self.metrics.stop()
        
        yield {
            "board": [row[:] for row in self.csp.board],
            "action": "complete",
            "cell": [-1, -1],
            "value": -1,
            "metrics": self.metrics.snapshot()
        }
