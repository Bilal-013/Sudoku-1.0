""" Pydantic schemas for request and response validation """
from pydantic import BaseModel
from typing import List

class PuzzleRequest(BaseModel):
    """ Request structure to generate a new puzzle. """
    difficulty: str = "medium"

class SolveRequest(BaseModel):
    """ Request structure containing the initial board and chosen AI algorithm to solve. """
    board: List[List[int]]
    algorithm: str = "backtracking"

class MetricsResponse(BaseModel):
    """ Schema for returning algorithm performance metrics. """
    time_taken_ms: float
    nodes_expanded: int
    steps_taken: int

class SolveResponse(BaseModel):
    """ Complete response containing the solved board and performance metrics. """
    solved: bool
    solution: List[List[int]]
    metrics: MetricsResponse

class StepEvent(BaseModel):
    """ Schema for emitting a single step in a Server-Sent Events (SSE) stream or Websocket. """
    board_state: List[List[int]]
    step_description: str
