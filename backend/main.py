""" FastAPI app and all routes for the Sudoku Solver backend """
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import json
import logging
import asyncio
from contextlib import asynccontextmanager

from models import (
    PuzzleRequest, PuzzleResponse, SolveRequest, SolveResponse,
    BenchmarkMetricsResponse, MetricsData
)
from generator import PuzzleGenerator
from solvers.backtracking import BacktrackingSolver
from solvers.informed import InformedSolver
from solvers.local_search import LocalSearchSolver
from solvers.forward_checking import ForwardCheckingSolver

logger = logging.getLogger("sudoku_startup")

@asynccontextmanager
async def lifespan(app: FastAPI):
    gen = PuzzleGenerator()
    for diff in ["easy", "medium", "hard", "expert"]:
        puzzle_data = gen.generate(diff)
        solver = BacktrackingSolver(puzzle_data["puzzle"])
        solution = solver.solve()
        if solution is not None:
            logger.info(f"Startup check ok: {diff} solved successfully.")
        else:
            logger.error(f"Startup check failed: {diff} could not be solved!")
    yield

app = FastAPI(title="AI Sudoku Solver API", lifespan=lifespan)

# Configure CORS for localhost (frontend development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # requested: all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_solver_class(algorithm: str):
    mapping = {
        "backtracking": BacktrackingSolver,
        "informed": InformedSolver,
        "local_search": LocalSearchSolver,
        "forward_checking": ForwardCheckingSolver
    }
    alg = algorithm.lower()
    if alg not in mapping:
        raise HTTPException(status_code=400, detail=f"Unknown algorithm: {algorithm}")
    return mapping[alg]

def validate_board(board: List[List[int]]):
    if len(board) != 9 or any(len(row) != 9 for row in board):
        raise HTTPException(status_code=400, detail="Board must be exactly 9x9.")
    for r in board:
        for val in r:
            if not (0 <= val <= 9):
                raise HTTPException(status_code=400, detail="Board values must be between 0 and 9.")

@app.get("/health")
def health_check():
    """ Returns server status and loaded algorithms """
    return {
        "status": "ok",
        "algorithms": ["backtracking", "informed", "local_search", "forward_checking"]
    }

@app.get("/")
def read_root():
    """ Root endpoint verifying API is running. """
    return {"message": "Sudoku Solver API is online"}

@app.post("/generate", response_model=PuzzleResponse)
def generate_puzzle(request: PuzzleRequest):
    """
    Generate a new Sudoku puzzle based on requested difficulty.
    """
    gen = PuzzleGenerator()
    data = gen.generate(request.difficulty)
    return PuzzleResponse(**data)

@app.post("/solve", response_model=SolveResponse)
async def solve_puzzle(request: SolveRequest):
    """
    Solve the provided puzzle board using the specified AI algorithm.
    """
    validate_board(request.board)
    SolverClass = get_solver_class(request.algorithm)
    solver = SolverClass(request.board)
    
    try:
        solution = await asyncio.wait_for(asyncio.to_thread(solver.solve), timeout=30.0)
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Solving exceeded 30 seconds.")
        
    if solution is None:
        raise HTTPException(status_code=422, detail="Puzzle has no valid solution.")
    
    return SolveResponse(
        solved=True,
        solution=solution,
        metrics=MetricsData(**solver.get_metrics())
    )

@app.get("/solve/stream")
def solve_stream(algorithm: str = "backtracking", difficulty: str = "medium"):
    gen = PuzzleGenerator()
    data = gen.generate(difficulty)
    board = data["puzzle"]
    
    SolverClass = get_solver_class(algorithm)
    
    def event_generator():
        solver = SolverClass(board)
        steps = solver.solve_steps()
        
        for step in steps:
            yield f"data: {json.dumps(step)}\n\n"
            
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post("/benchmark", response_model=List[BenchmarkMetricsResponse])
def benchmark(request: PuzzleRequest):
    gen = PuzzleGenerator()
    data = gen.generate(request.difficulty)
    board = data["puzzle"]
    
    algorithms = ["backtracking", "informed", "local_search", "forward_checking"]
    results = []
    
    for alg in algorithms:
        SolverClass = get_solver_class(alg)
        solver = SolverClass(board)
        solver.solve()
        results.append(BenchmarkMetricsResponse(
            algorithm=alg,
            metrics=MetricsData(**solver.get_metrics())
        ))
        
    return results
