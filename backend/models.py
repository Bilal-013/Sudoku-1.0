""" Pydantic schemas for request and response validation """
from pydantic import BaseModel
from typing import List, Optional

class PuzzleRequest(BaseModel):
    """ Request structure to generate a new puzzle. """
    difficulty: str = "medium"

class PuzzleResponse(BaseModel):
    puzzle: List[List[int]]
    solution: List[List[int]]
    difficulty: str
    empty_cells: int

class SolveRequest(BaseModel):
    """ Request structure containing the initial board and chosen AI algorithm to solve. """
    board: List[List[int]]
    algorithm: str = "backtracking"

class MetricsData(BaseModel):
    time_elapsed: float
    states_explored: int
    backtracks: int
    assignments_made: int

class BenchmarkMetricsResponse(BaseModel):
    algorithm: str
    metrics: MetricsData

class SolveResponse(BaseModel):
    """ Complete response containing the solved board and performance metrics. """
    solved: bool
    solution: Optional[List[List[int]]] = None
    metrics: MetricsData

class StepEvent(BaseModel):
    board: List[List[int]]
    action: str
    cell: List[int]
    value: int
    metrics: MetricsData
