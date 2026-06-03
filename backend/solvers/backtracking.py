""" Standard Backtracking Depth-First Search solver implementation. """
from .base import SudokuSolver
from typing import Generator, Any

class BacktrackingSolver(SudokuSolver):
    """ Basic brute-force Backtracking solving algorithm. """
    
    def solve(self) -> bool:
        # TODO: Implement basic backtracking DFS
        return False

    def solve_steps(self) -> Generator[Any, None, None]:
        # TODO: Yield step events as backtracking attempts different paths
        yield None
    
    def get_metrics(self) -> dict:
        return self.metrics.get_metrics_dict()
