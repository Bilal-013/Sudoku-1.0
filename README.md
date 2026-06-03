# AI Sudoku Solver

A full-stack, end-to-end web application that visualizes how different Artificial Intelligence search algorithms and Constraint Satisfaction Problem (CSP) heuristics solve Sudoku puzzles.

## Project Structure Overview

```
backend/
  main.py               # FastAPI application, routing, error handling, endpoints
  generator.py          # Backtracking puzzle generator yielding unique solutions
  metrics.py            # Tracks elapsed time, assignments, states explored, and backtracks
  models.py             # Pydantic schemas for request/response validation
  solvers/              # AI Algorithm implementations
    base.py             # CSP definition, domain init, constraint checking
    backtracking.py     # Pure Depth-First Search with backtracking
    forward_checking.py # DFS + early failure detection reducing domains
    informed.py         # DFS + AC-3 + MRV (Minimum Remaining Values) + Degree Heuristic
    local_search.py     # Simulated Annealing optimization

frontend/
  index.html            # Main UI structure
  app.js                # Vanilla JS driving the API calls, SSE rendering, and Chart.js
  style.css             # Custom utility classes and animations over Tailwind CSS
```

## How to run the application

### Backend
1. Ensure you have Python 3.8+ installed.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the FastAPI server:
   ```bash
   uvicorn backend.main:app --reload
   ```
   The backend will be available at `http://localhost:8000`.

### Frontend
1. The frontend operates independently. You can serve the folder using any HTTP server:
   ```bash
   cd frontend
   python -m http.server 8080
   ```
   Or open `index.html` directly in a modern web browser.

## API Endpoint Reference

- `GET /health`: Returns `{ "status": "ok" }`.
- `POST /generate`: Given a `{ difficulty: "easy|medium|hard|expert" }` payload, returns a 9x9 uniquely solvable `puzzle`.
- `POST /solve`: Given a `board` and `algorithm`, attempts to solve the puzzle instantly (max 30s timeout). Returns `solution` and `metrics`.
- `GET /solve/stream`: Initiates an SSE (Server-Sent Events) stream. Parameters: `algorithm`, `difficulty`. Streams `{"action": "...", "board": [...], "cell": [r,c], "metrics": {...}}` at simulated intervals for visualization. Returns `{ "type": "done" }` at conclusion.
- `GET /benchmark/all`: Generates puzzles across all 4 difficulty levels, runs to completion on all 4 algorithms, and returns aggregated JSON metrics. Max timeout 120s.

## Screenshot Section

*(Place screenshots of the UI, streaming solving process, and benchmarking charts here)*
