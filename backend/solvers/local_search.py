""" Local Search solver utilizing Simulated Annealing. """
from .base import SudokuSolver
from typing import Generator, Any, List, Dict
import random, math, copy

class LocalSearchSolver(SudokuSolver):
    """ 
    Metaheuristic optimization solver employing a Stochastic Local 
    Search technique—specifically Simulated Annealing.
    """
    def __init__(self, board: List[List[int]]):
        super().__init__(board)
        self.fixed = [[board[r][c] != 0 for c in range(9)] for r in range(9)]
    
    def _fill_board(self, board):
        for box_r in range(3):
            for box_c in range(3):
                nums = set(range(1, 10))
                for i in range(3):
                    for j in range(3):
                        if board[box_r*3 + i][box_c*3 + j] != 0:
                            nums.remove(board[box_r*3 + i][box_c*3 + j])
                
                nums = list(nums)
                random.shuffle(nums)
                for i in range(3):
                    for j in range(3):
                        if board[box_r*3 + i][box_c*3 + j] == 0:
                            board[box_r*3 + i][box_c*3 + j] = nums.pop()

    def _get_cost(self, board):
        cost = 0
        for i in range(9):
            row_set = set()
            col_set = set()
            for j in range(9):
                row_set.add(board[i][j])
                col_set.add(board[j][i])
            cost += (9 - len(row_set)) + (9 - len(col_set))
        return cost

    def _get_random_swap(self):
        box_r, box_c = random.randint(0, 2), random.randint(0, 2)
        candidates = []
        for i in range(3):
            for j in range(3):
                r, c = box_r*3 + i, box_c*3 + j
                if not self.fixed[r][c]:
                    candidates.append((r, c))
                    
        if len(candidates) < 2:
            return None, None
            
        c1, c2 = random.sample(candidates, 2)
        return c1, c2

    def solve(self) -> List[List[int]]:
        self.metrics.start()
        
        board = copy.deepcopy(self.csp.board)
        self._fill_board(board)
        
        current_cost = self._get_cost(board)
        if current_cost == 0:
            self.metrics.stop()
            return board
            
        T = 1.0
        cooling_rate = 0.9995
        max_iters = 100000
        
        for k in range(max_iters):
            self.metrics.record_state()
            
            c1, c2 = self._get_random_swap()
            if not c1:
                continue
                
            r1, c1_idx = c1
            r2, c2_idx = c2
            
            board[r1][c1_idx], board[r2][c2_idx] = board[r2][c2_idx], board[r1][c1_idx]
            self.metrics.assignments_made += 1
            
            new_cost = self._get_cost(board)
            delta = new_cost - current_cost
            
            if delta < 0 or random.random() < math.exp(-delta / T):
                current_cost = new_cost
                if current_cost == 0:
                    self.metrics.stop()
                    return board
            else:
                board[r1][c1_idx], board[r2][c2_idx] = board[r2][c2_idx], board[r1][c1_idx]
                self.metrics.record_backtrack()
                
            T *= cooling_rate
            
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
        
        board = copy.deepcopy(self.csp.board)
        self._fill_board(board)
        
        current_cost = self._get_cost(board)
        
        if current_cost == 0:
            self.metrics.stop()
            yield {
                "board": [row[:] for row in board],
                "action": "complete",
                "cell": [-1, -1],
                "value": -1,
                "metrics": self.metrics.snapshot()
            }
            return
            
        T = 1.0
        cooling_rate = 0.9995
        max_iters = 100000
        
        for k in range(1, max_iters + 1):
            self.metrics.record_state()
            
            c1, c2 = self._get_random_swap()
            if not c1:
                continue
                
            r1, c1_idx = c1
            r2, c2_idx = c2
            
            board[r1][c1_idx], board[r2][c2_idx] = board[r2][c2_idx], board[r1][c1_idx]
            self.metrics.assignments_made += 1
            
            new_cost = self._get_cost(board)
            delta = new_cost - current_cost
            
            accepted = False
            if delta < 0 or random.random() < math.exp(-delta / T):
                current_cost = new_cost
                accepted = True
            else:
                board[r1][c1_idx], board[r2][c2_idx] = board[r2][c2_idx], board[r1][c1_idx]
                self.metrics.record_backtrack()
                
            if k % 500 == 0 or current_cost == 0:
                yield {
                    "board": [row[:] for row in board],
                    "action": "assign" if accepted else "backtrack",
                    "cell": list(c1),
                    "value": board[r1][c1_idx],
                    "metrics": self.metrics.snapshot()
                }
                
            if current_cost == 0:
                self.metrics.stop()
                yield {
                    "board": [row[:] for row in board],
                    "action": "complete",
                    "cell": [-1, -1],
                    "value": -1,
                    "metrics": self.metrics.snapshot()
                }
                return
                
            T *= cooling_rate
            
        self.metrics.stop()
        yield {
            "board": [row[:] for row in board],
            "action": "complete",
            "cell": [-1, -1],
            "value": -1,
            "metrics": self.metrics.snapshot()
        }
