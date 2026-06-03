""" FastAPI app and all routes for the Sudoku Solver backend """
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import json
import logging

from .models import (
    PuzzleRequest, PuzzleResponse, SolveRequest, SolveResponse,
    BenchmarkMetricsResponse, MetricsData
)
from .generator import PuzzleGenerator
from .solvers.backtracking import BacktrackingSolver
from .solvers.informed import InformedSolver
from .solvers.local_search import LocalSearchSolver
from .solvers.forward_checking import ForwardCheckingSolver

app = FastAPI(title="AI Sudoku Solver API")

# Configure CORS for localhost (frontend development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # requested: all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = logging.getLogger("sudoku_startup")

@app.on_event("startup")
def run_sanity_check():
    gen = PuzzleGenerator()
    for diff in ["easy", "medium", "hard", "expert"]:
        puzzle_data = gen.generate(diff)
        solver = BacktrackingSolver(puzzle_data["puzzle"])
        solution = solver.solve()
        if solution is not None:
            logger.info(f"Startup check ok: {diff} solved successfully.")
        else:
            logger.error(f"Startup check failed: {diff} could not be solved!")

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
def solve_puzzle(request: SolveRequest):
    """
    Solve the provided puzzle board using the specified AI algorithm.
    """
    SolverClass = get_solver_class(request.algorithm)
    solver = SolverClass(request.board)
    solution = solver.solve()
    
    return SolveResponse(
        solved=(solution is not None),
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
        
        # Send initial problem board as an event or metadata maybe?
        
        for step in steps:
            yield f"data: {json.dumps(step)}\n\n"
            
        metrics = solver.get_metrics()
        final_event = {
            "type": "done",
            "metrics": metrics
        }
        yield f"data: {json.dumps(final_event)}\n\n"
        
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
