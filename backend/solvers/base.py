""" Abstract base class SudokuSolver """
from abc import ABC, abstractmethod
from typing import List, Generator, Any, Tuple, Dict
import copy
from ..metrics import MetricsTracker

class SudokuCSP:
    """ CSP formulation of a Sudoku puzzle. """
    def __init__(self, board: List[List[int]]):
        self.board = [row[:] for row in board]
        # Variables are empty cells (r, c)
        self.variables = [(r, c) for r in range(9) for c in range(9) if self.board[r][c] == 0]
        self.domains = dict()
        self._initialize_domains()

    def _initialize_domains(self):
        """ Initialize domains for all variables based on initial board constraints. """
        for r, c in self.variables:
            valid_values = []
            for v in range(1, 10):
                if self.is_consistent((r, c), v):
                    valid_values.append(v)
            self.domains[(r, c)] = valid_values

    def get_neighbors(self, cell: Tuple[int, int]) -> List[Tuple[int, int]]:
        """ Returns a list of cells sharing a constraint (row, col, 3x3 box) with the given cell. """
        r, c = cell
        neighbors = set()
        
        # Row and col neighbors
        for i in range(9):
            if i != c:
                neighbors.add((r, i))
            if i != r:
                neighbors.add((i, c))
                
        # 3x3 box neighbors
        box_r, box_c = (r // 3) * 3, (c // 3) * 3
        for i in range(box_r, box_r + 3):
            for j in range(box_c, box_c + 3):
                if (i, j) != cell:
                    neighbors.add((i, j))
                    
        return list(neighbors)

    def is_consistent(self, cell: Tuple[int, int], value: int) -> bool:
        """ Check if assigning a value to a cell violates any constraints """
        r, c = cell
        
        # Check row
        for i in range(9):
            if self.board[r][i] == value:
                return False
                
        # Check column
        for i in range(9):
            if self.board[i][c] == value:
                return False
                
        # Check 3x3 block
        box_r, box_c = (r // 3) * 3, (c // 3) * 3
        for i in range(3):
            for j in range(3):
                if self.board[box_r + i][box_c + j] == value:
                    return False
                    
        return True

    def get_domain(self, cell: Tuple[int, int]) -> List[int]:
        """ Returns the current valid domain for the given cell """
        return self.domains.get(cell, [])

    def apply_assignment(self, cell: Tuple[int, int], value: int):
        """ Assigns a value to the board cell """
        self.board[cell[0]][cell[1]] = value

    def remove_assignment(self, cell: Tuple[int, int]):
        """ Removes an assignment, reverting the cell to 0 """
        self.board[cell[0]][cell[1]] = 0

    def is_complete(self) -> bool:
        """ Returns True if the board has no empty cells remaining """
        for r in range(9):
            for c in range(9):
                if self.board[r][c] == 0:
                    return False
        return True

class SudokuSolver(ABC):
    """ 
    Abstract base class enforcing a standard interface for all 
    Sudoku solving AI algorithms. 
    """
    
    def __init__(self, board: List[List[int]]):
        self.csp = SudokuCSP(board)
        self.metrics = MetricsTracker()

    @abstractmethod
    def solve(self) -> List[List[int]]:
        """ Execute the solving algorithm entirely. Return the solved board. """
        pass

    @abstractmethod
    def solve_steps(self) -> Generator[Dict[str, Any], None, None]:
        """ 
        Generator that yields intermediate board states and information 
        to visualize the AI decisions step-by-step. 
        Each yield must match the schema:
        {
            "board": [[int]],
            "action": str,
            "cell": [row, col],
            "value": int,
            "metrics": dict
        }
        """
        pass

    def get_metrics(self) -> dict:
        """ Retrieve the detailed performance metrics of the solve. """
        return self.metrics.snapshot()
