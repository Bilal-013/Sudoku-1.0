""" Abstract base class SudokuSolver """
from abc import ABC, abstractmethod
from typing import List, Generator, Any
from ..metrics import MetricsTracker

class SudokuSolver(ABC):
    """ 
    Abstract base class enforcing a standard interface for all 
    Sudoku solving AI algorithms. 
    """
    
    def __init__(self, board: List[List[int]]):
        self.board = board
        self.metrics = MetricsTracker()

    @abstractmethod
    def solve(self) -> bool:
        """ Execute the solving algorithm entirely. Return True if solved. """
        pass

    @abstractmethod
    def solve_steps(self) -> Generator[Any, None, None]:
        """ 
        Generator that yields intermediate board states and information 
        to visualize the AI decisions step-by-step. 
        """
        pass

    @abstractmethod
    def get_metrics(self) -> dict:
        """ Retrieve the detailed performance metrics of the solve. """
        pass
