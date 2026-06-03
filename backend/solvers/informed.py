""" Informed solver combining CSP concepts: AC-3, MRV, and Degree Heuristics. """
from .base import SudokuSolver
from typing import Generator, Any

class InformedSolver(SudokuSolver):
    """ 
    Optimized Constraint Satisfaction Problem (CSP) solver utilizing:
    - Minimum Remaining Values (MRV) heuristic
    - Degree Heuristic
    - AC-3 (Arc Consistency 3) for inference
    """
    
    def solve(self) -> bool:
        # TODO: Implement CSP solver with smart heuristics
        return False

    def solve_steps(self) -> Generator[Any, None, None]:
        # TODO: Yield state changes reflecting inference steps 
        yield None
    
    def get_metrics(self) -> dict:
        return self.metrics.get_metrics_dict()
