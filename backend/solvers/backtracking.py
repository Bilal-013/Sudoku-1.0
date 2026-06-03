""" Standard Backtracking Depth-First Search solver implementation. """
from .base import SudokuSolver
from typing import Generator, Any, List, Dict

class BacktrackingSolver(SudokuSolver):
    """ Basic brute-force Backtracking solving algorithm. """
    
    def solve(self) -> List[List[int]]:
        self.metrics.start()
        
        def backtrack():
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
                
            for val in range(1, 10):
                if self.csp.is_consistent(cell, val):
                    self.csp.apply_assignment(cell, val)
                    self.metrics.assignments_made += 1
                    
                    if backtrack():
                        return True
                        
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
        
        def backtrack():
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
                
            for val in range(1, 10):
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
                    
                    found = yield from backtrack()
                    if found:
                        return True
                        
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
