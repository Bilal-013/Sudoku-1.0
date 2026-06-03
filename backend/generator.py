import random
import copy

class PuzzleGenerator:
    """ Generates playable Sudoku boards with varying difficulty levels. """
    
    def __init__(self):
        self.difficulties = {
            "easy": (36, 45),
            "medium": (27, 35),
            "hard": (19, 26),
            "expert": (17, 18)
        }

    def generate(self, difficulty: str) -> dict:
        """
        Generate and return a 9x9 Sudoku board based on difficulty constraints.
        Returns the puzzle, the solution, the difficulty, and the number of empty cells.
        """
        diff = difficulty.lower()
        if diff not in self.difficulties:
            diff = "medium"
            
        while True:
            solution = self._generate_full_board()
            puzzle = self._remove_cells(solution, diff)
            if puzzle:
                empty_cells = sum(row.count(0) for row in puzzle)
                return {
                    "puzzle": puzzle,
                    "solution": solution,
                    "difficulty": diff,
                    "empty_cells": empty_cells
                }

    def _generate_full_board(self) -> list[list[int]]:
        """ Creates a valid complete board """
        board = [[0]*9 for _ in range(9)]
        
        # Fill the diagonal 3x3 boxes first, as they are independent
        for i in range(0, 9, 3):
            nums = list(range(1, 10))
            random.shuffle(nums)
            for r in range(3):
                for c in range(3):
                    board[i+r][i+c] = nums.pop()
                    
        # Solve the rest to get a full board
        self._solve_board(board)
        return board

    def _remove_cells(self, board: list[list[int]], difficulty: str) -> list[list[int]]:
        """ Creates the puzzle by removing cells while maintaining unique solvability """
        min_filled, max_filled = self.difficulties[difficulty]
        target_filled = random.randint(min_filled, max_filled)
        
        puzzle = copy.deepcopy(board)
        cells = [(r, c) for r in range(9) for c in range(9)]
        random.shuffle(cells)
        
        filled = 81
        for r, c in cells:
            if filled <= target_filled:
                break
                
            temp = puzzle[r][c]
            puzzle[r][c] = 0
            
            if self._is_uniquely_solvable(puzzle):
                filled -= 1
            else:
                puzzle[r][c] = temp
                
        # If we couldn't remove enough (especially for expert), we might need to retry
        if filled > max_filled:
            return None # None signals it failed to generate within criteria, retry
            
        return puzzle

    def _is_uniquely_solvable(self, board: list[list[int]]) -> bool:
        """
        Ensures exactly one solution exists.
        
        Uniqueness Check Logic:
        1. A counter is initialized to track the number of valid solutions found.
        2. We use backtracking to systematically try filling empty cells.
        3. If a valid placement completes the board, we increment the solution count.
        4. If the count exceeds 1, we immediately stop and return False, as the puzzle is not unique.
        5. If the search finishes with exactly 1 solution, it returns True.
        """
        solutions = [0]
        
        def count_solutions(b):
            # If we found more than one solution, stop early
            if solutions[0] > 1:
                return
                
            empty = self._find_empty(b)
            if not empty:
                solutions[0] += 1
                return
                
            row, col = empty
            for num in range(1, 10):
                if self._is_valid(b, num, row, col):
                    b[row][col] = num
                    count_solutions(b)
                    b[row][col] = 0
                    
        # Work on a copy to avoid mutating the original puzzle
        b_copy = copy.deepcopy(board)
        count_solutions(b_copy)
        
        return solutions[0] == 1

    def _solve_board(self, board: list[list[int]]) -> bool:
        """ Helper method to solve the board """
        empty = self._find_empty(board)
        if not empty:
            return True
            
        row, col = empty
        nums = list(range(1, 10))
        random.shuffle(nums) # add randomness to board generation
        
        for num in nums:
            if self._is_valid(board, num, row, col):
                board[row][col] = num
                if self._solve_board(board):
                    return True
                board[row][col] = 0
                
        return False
        
    def _find_empty(self, board: list[list[int]]):
        for i in range(9):
            for j in range(9):
                if board[i][j] == 0:
                    return (i, j)
        return None
        
    def _is_valid(self, board: list[list[int]], num: int, row: int, col: int) -> bool:
        # Check row
        if num in board[row]:
            return False
            
        # Check col
        for i in range(9):
            if board[i][col] == num:
                return False
                
        # Check box
        box_x = col // 3
        box_y = row // 3
        
        for i in range(box_y * 3, box_y * 3 + 3):
            for j in range(box_x * 3, box_x * 3 + 3):
                if board[i][j] == num:
                    return False
                    
        return True
