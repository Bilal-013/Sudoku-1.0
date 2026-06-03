import asyncio
import time
from rich.console import Console
from rich.table import Table
from backend.generator import PuzzleGenerator
from backend.solvers.backtracking import BacktrackingSolver
from backend.solvers.forward_checking import ForwardCheckingSolver
from backend.solvers.informed import InformedSolver
from backend.solvers.local_search import LocalSearchSolver

console = Console()

def verify_solution(solution):
    if not solution:
        return False
    # Check rows, columns, and subgrids
    for i in range(9):
        row_set = set()
        col_set = set()
        for j in range(9):
            if solution[i][j] < 1 or solution[i][j] > 9:
                return False
            row_set.add(solution[i][j])
            col_set.add(solution[j][i])
        if len(row_set) != 9 or len(col_set) != 9:
            return False

    for box_r in range(3):
        for box_c in range(3):
            box_set = set()
            for i in range(3):
                for j in range(3):
                    val = solution[box_r*3 + i][box_c*3 + j]
                    box_set.add(val)
            if len(box_set) != 9:
                return False
    return True

async def run_tests():
    difficulties = ["easy", "medium", "hard", "expert"]
    algorithms = {
        "Backtracking": BacktrackingSolver,
        "ForwardChecking": ForwardCheckingSolver,
        "Informed (AC-3/MRV)": InformedSolver,
        "Simulated Annealing": LocalSearchSolver
    }

    console.print("[bold cyan]Generating Puzzles...[/bold cyan]")
    generator = PuzzleGenerator()
    puzzles = {}
    for diff in difficulties:
        console.print(f"Generating [yellow]{diff}[/yellow] puzzle...")
        puzzles[diff] = generator.generate(diff)

    table = Table(title="Sudoku AI Solver Benchmark Summary")
    table.add_column("Difficulty", justify="left", style="cyan", no_wrap=True)
    table.add_column("Algorithm", justify="left", style="magenta")
    table.add_column("Status", justify="center")
    table.add_column("Time (s)", justify="right", style="green")
    table.add_column("States Explored", justify="right")
    table.add_column("Assignments", justify="right")
    table.add_column("Backtracks", justify="right")

    for diff, board in puzzles.items():
        for algo_name, solver_class in algorithms.items():
            copied_board = [row[:] for row in board]
            solver = solver_class(copied_board)
            
            error_status = "N/A"
            solution = None
            try:
                # Basic wrapping logic to mimic asyncio timeout behavior within sync environment natively
                start_w = time.perf_counter()
                solution = solver.solve()
                end_w = time.perf_counter()
                # Overwrite metrics time due to test script overhead
                solver.metrics.time_elapsed = end_w - start_w
                status = "[green]OK[/green]" if verify_solution(solution) else "[red]FAIL[/red]"
                
            except Exception as e:
                status = f"[red]ERR: {str(e)}[/red]"

            if not solution and error_status == "N/A":
                status = "[red]NO SOLUTION[/red]"

            table.add_row(
                diff.capitalize(),
                algo_name,
                status,
                f"{solver.metrics.time_elapsed:.4f}",
                str(solver.metrics.states_explored),
                str(solver.metrics.assignments_made),
                str(solver.metrics.backtracks)
            )

    console.print(table)

if __name__ == "__main__":
    asyncio.run(run_tests())
