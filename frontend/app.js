/**
 * Frontend execution logic for the AI Sudoku Solver.
 * Handles board drawing, selections, constraints, and API hooks.
 */

const API_BASE_URL = 'http://localhost:8000';

document.addEventListener('DOMContentLoaded', () => {
    initBoard();
    initNumpad();
    
    // Initial mockup state based on screenshot provided
    mockInitialDemoState();
});

function initBoard() {
    const boardEl = document.getElementById('sudoku-board');
    
    for (let i = 0; i < 81; i++) {
        const cell = document.createElement('div');
        cell.classList.add('sudoku-cell');
        cell.dataset.index = i;
        
        const row = Math.floor(i / 9);
        const col = i % 9;
        
        // Emphasize right borders for columns 2 and 5 (0-indexed)
        if (col === 2 || col === 5) {
            cell.classList.add('col-group-end');
        }
        
        // Emphasize bottom borders for rows 2 and 5
        if (row === 2 || row === 5) {
            cell.classList.add('row-group-end');
        }
        
        // Click listener for highlighting mechanism
        cell.addEventListener('click', () => handleCellClick(i));
        
        boardEl.appendChild(cell);
    }
}

function initNumpad() {
    const numpadEl = document.getElementById('numpad');
    // Generates keys 1-9
    for (let i = 1; i <= 9; i++) {
        const btn = document.createElement('div');
        btn.classList.add('numpad-btn');
        btn.textContent = i;
        btn.addEventListener('click', () => handleNumberInput(i));
        numpadEl.appendChild(btn);
    }
}

function handleCellClick(index) {
    const cells = document.querySelectorAll('.sudoku-cell');
    
    // Clear previous selections
    cells.forEach(c => {
        c.classList.remove('cell-selected-bg');
        c.classList.remove('cell-peer-bg');
    });

    // Highlighting logic (demo version)
    // Real implementation will calculate row, col and subgrid peers
    cells[index].classList.add('cell-selected-bg');
}

function handleNumberInput(num) {
    // Write logic here for inputting numbers from user interactions
    console.log(`Input Number ${num} pressed`);
}

/** 
 * Matches to the given target screenshot to establish baseline look 
 */
function mockInitialDemoState() {
    const cells = document.querySelectorAll('.sudoku-cell');
    
    const puzzle = [
        [0, 0, 0, 2, 4, 7, 0, 0, 3],
        [0, 0, 0, 0, 0, 0, 6, 0, 0],
        [0, 7, 9, 8, 6, 3, 2, 5, 0],
        [0, 9, 0, 6, 0, 0, 0, 0, 0],
        [0, 0, 8, 3, 1, 0, 0, 0, 0],
        [7, 4, 0, 0, 0, 0, 1, 0, 0],
        [9, 0, 2, 0, 0, 0, 3, 0, 0],
        [0, 0, 0, 4, 0, 0, 0, 0, 6],
        [0, 0, 7, 5, 2, 6, 0, 0, 1]
    ];
    
    for (let r = 0; r < 9; r++) {
        for (let c = 0; c < 9; c++) {
            let val = puzzle[r][c];
            if (val !== 0) {
                let node = cells[r * 9 + c];
                node.textContent = val;
                node.classList.add('cell-prefilled');
            }
        }
    }
    
    // Replicate top corner selection aesthetic
    cells[0].classList.add('cell-selected-bg');
    cells[1].classList.add('cell-peer-bg');
    cells[2].classList.add('cell-peer-bg');
    cells[9].classList.add('cell-peer-bg');
    cells[10].classList.add('cell-peer-bg');
    cells[11].classList.add('cell-peer-bg');
    cells[18].classList.add('cell-peer-bg');
    cells[19].classList.add('cell-peer-bg');
    cells[20].classList.add('cell-peer-bg');
}

// TODO: Connect fetch APIs pointing to the FastAPI backend endpoints
