""" FastAPI app and all routes for the Sudoku Solver backend """
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .models import PuzzleRequest, SolveRequest, SolveResponse

app = FastAPI(title="AI Sudoku Solver API")

# Configure CORS for localhost (frontend development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:5500", "http://localhost:5500", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    """ Root endpoint verifying API is running. """
    return {"message": "Sudoku Solver API is online"}

@app.post("/generate")
def generate_puzzle(request: PuzzleRequest):
    """
    Generate a new Sudoku puzzle based on requested difficulty.
    """
    # TODO: Connect pattern to generator module
    pass

@app.post("/solve", response_model=SolveResponse)
def solve_puzzle(request: SolveRequest):
    """
    Solve the provided puzzle board using the specified AI algorithm.
    """
    # TODO: Implement dynamic algorithm selection and solver execution
    pass
