/**
 * Frontend execution logic for the AI Sudoku Solver.
 */

const API_BASE_URL = 'http://localhost:8000';

let initialBoard = [];
let currentBoard = [];
let selectedDifficulty = 'medium';
let selectedAlgorithm = 'backtracking';
let eventSource = null;
let chartInstance = null;

document.addEventListener('DOMContentLoaded', () => {
    initGridDom();
    initEventListeners();
    generatePuzzle();
});

function initGridDom() {
    const boardEl = document.getElementById('sudoku-board');
    boardEl.innerHTML = '';
    
    for (let i = 0; i < 81; i++) {
        const cell = document.createElement('div');
        cell.classList.add('sudoku-cell');
        cell.dataset.index = i;
        
        const row = Math.floor(i / 9);
        const col = i % 9;
        cell.dataset.row = row;
        cell.dataset.col = col;
        
        if (col === 2 || col === 5) cell.classList.add('col-group-end');
        if (row === 2 || row === 5) cell.classList.add('row-group-end');
        
        boardEl.appendChild(cell);
    }
}

function initEventListeners() {
    // Difficulty
    document.querySelectorAll('.diff-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.diff-btn').forEach(b => {
                b.classList.remove('bg-blue-600', 'text-white');
                b.classList.add('bg-white', 'text-gray-600');
            });
            e.target.classList.remove('bg-white', 'text-gray-600');
            e.target.classList.add('bg-blue-600', 'text-white');
            selectedDifficulty = e.target.dataset.diff;
        });
    });

    // Strategy
    document.querySelectorAll('.algo-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.algo-btn').forEach(b => {
                b.classList.remove('bg-blue-50', 'border-blue-400', 'text-blue-800');
                b.classList.add('bg-white', 'text-gray-700');
            });
            e.target.classList.remove('bg-white', 'text-gray-700');
            e.target.classList.add('bg-blue-50', 'border-blue-400', 'text-blue-800');
            selectedAlgorithm = e.target.dataset.algo;
        });
    });

    document.getElementById('btn-generate').addEventListener('click', () => {
        stopVisualization();
        generatePuzzle();
    });
    
    document.getElementById('btn-solve').addEventListener('click', () => {
        stopVisualization();
        solveInstantly();
    });

    document.getElementById('btn-visualize').addEventListener('click', startVisualization);
    document.getElementById('btn-stop').addEventListener('click', stopVisualization);
    
    document.getElementById('btn-benchmark').addEventListener('click', () => {
        stopVisualization();
        runBenchmark();
    });
}

function showToast(message, isError=false) {
    const toast = document.createElement('div');
    toast.className = `fixed bottom-4 right-4 px-6 py-3 rounded-lg shadow-lg font-bold text-white transition-opacity z-50 ${isError ? 'bg-red-600' : 'bg-green-600'}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ============== RENDERERS ==============

function renderGrid(board, actionCell = null, actionType = null) {
    const cells = document.querySelectorAll('.sudoku-cell');
    
    for (let r = 0; r < 9; r++) {
        for (let c = 0; c < 9; c++) {
            const idx = r * 9 + c;
            const node = cells[idx];
            const val = board[r][c];
            const initialVal = initialBoard[r] ? initialBoard[r][c] : 0;
            
            node.textContent = val !== 0 ? val : '';
            
            node.classList.remove('cell-fixed', 'cell-user', 'highlight-process', 'flash-red');
            
            if (initialVal !== 0) {
                node.classList.add('cell-fixed');
            } else if (val !== 0) {
                node.classList.add('cell-user');
            }
            
            if (actionCell && actionCell[0] === r && actionCell[1] === c) {
                if (actionType === 'backtrack') {
                    // Trigger reflow to restart animation
                    void node.offsetWidth; 
                    node.classList.add('flash-red');
                } else if (actionType !== 'start' && actionType !== 'complete') {
                    node.classList.add('highlight-process');
                }
            }
        }
    }
}

function updateMetrics(metrics) {
    if(!metrics) return;
    document.getElementById('metric-time').textContent = metrics.time_elapsed ? metrics.time_elapsed.toFixed(3) + 's' : '0.0s';
    document.getElementById('metric-states').textContent = metrics.states_explored || 0;
    document.getElementById('metric-assigns').textContent = metrics.assignments_made || 0;
    document.getElementById('metric-backtracks').textContent = metrics.backtracks || 0;
}

function updateStatus(status, pulse = false, isReconnect = false) {
    const statBadge = document.getElementById('status-badge');
    const progCont = document.getElementById('prog-container');
    const bVis = document.getElementById('btn-visualize');
    const bStop = document.getElementById('btn-stop');
    
    statBadge.textContent = status;
    
    if (pulse) {
        progCont.classList.remove('hidden');
        bVis.classList.add('hidden');
        bStop.classList.remove('hidden');
        bStop.textContent = "Stop";
    } else {
        progCont.classList.add('hidden');
        
        if (isReconnect) {
            bVis.classList.add('hidden');
            bStop.classList.remove('hidden');
            bStop.textContent = "Reconnect";
            bStop.onclick = () => {
                bStop.onclick = stopVisualization;
                bStop.textContent = "Stop";
                startVisualization();
            };
        } else {
            bVis.classList.remove('hidden');
            bStop.classList.add('hidden');
        }
        
        document.querySelectorAll('.sudoku-cell').forEach(c => c.classList.remove('highlight-process'));
    }
}

// ============== API CALLS ==============

async function generatePuzzle() {
    try {
        updateStatus('Generating...', true);
        const res = await fetch(`${API_BASE_URL}/generate`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ difficulty: selectedDifficulty })
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        initialBoard = data.puzzle.map(row => [...row]);
        currentBoard = data.puzzle.map(row => [...row]);
        renderGrid(currentBoard);
        updateMetrics({ time_elapsed: 0, states_explored: 0, assignments_made: 0, backtracks: 0 });
        updateStatus('Ready');
        document.getElementById('chart-container').classList.add('hidden');
    } catch (e) {
        console.error(e);
        updateStatus('Error');
        showToast('Failed to generate puzzle. API Error.', true);
    }
}

async function solveInstantly() {
    if (!initialBoard.length) return;
    try {
        updateStatus('Solving...', true);
        const res = await fetch(`${API_BASE_URL}/solve`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                board: initialBoard.map(row => [...row]),
                algorithm: selectedAlgorithm
            })
        });
        const data = await res.json();
        if (!res.ok) {
            if (res.status === 422) throw new Error("Puzzle has no valid solution.");
            if (res.status === 504) throw new Error("Solving timeout exceeded 30s.");
            throw new Error(`HTTP ${res.status}`);
        }
        if (data.solved) {
            currentBoard = data.solution;
            renderGrid(currentBoard);
        }
        updateMetrics(data.metrics);
        updateStatus('Solved');
    } catch (e) {
        console.error(e);
        updateStatus('Error');
        showToast(e.message || 'API Error occurred while solving.', true);
    }
}

// ============== SSE VISUALIZATION ==============

let expectingClose = false;

function startVisualization() {
    stopVisualization();
    expectingClose = false;
    updateStatus('Streaming...', true);
    
    // We pass the diff param, so backend generates a fresh one & streams
    const url = new URL(`${API_BASE_URL}/solve/stream`);
    url.searchParams.append('algorithm', selectedAlgorithm);
    url.searchParams.append('difficulty', selectedDifficulty);
    
    eventSource = new EventSource(url);
    
    eventSource.onmessage = (e) => {
        const data = JSON.parse(e.data);
        
        if (data.type === 'done') {
            expectingClose = true;
            stopVisualization();
            updateMetrics(data.metrics);
            updateStatus('Solved');
            return;
        }
        
        if (data.action === 'start') {
            initialBoard = data.board.map(r=>[...r]); 
        }

        currentBoard = data.board;
        renderGrid(currentBoard, data.cell, data.action);
        updateMetrics(data.metrics);
    };
    
    eventSource.onerror = (e) => {
        eventSource.close();
        if (!expectingClose) {
            updateStatus('Stream Connection Lost', false, true);
            showToast('SSE Connection interrupted.', true);
        } else {
            updateStatus('Canceled', false);
        }
    };
}

function stopVisualization() {
    if (eventSource) {
        expectingClose = true;
        eventSource.close();
        eventSource = null;
        updateStatus('Canceled', false);
    }
}

// ============== CHARTS ==============

async function runBenchmark() {
    try {
        updateStatus('Benchmarking...', true);
        const res = await fetch(`${API_BASE_URL}/benchmark`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ difficulty: selectedDifficulty })
        });
        const data = await res.json();
        renderChart(data);
        updateStatus('Benchmark Complete');
    } catch (e) {
        console.error(e);
        updateStatus('Error');
    }
}

function renderChart(benchmarkData) {
    document.getElementById('chart-container').classList.remove('hidden');
    
    const labels = benchmarkData.map(d => d.algorithm.replace('_', ' ').toUpperCase());
    const times = benchmarkData.map(d => d.metrics.time_elapsed);
    const states = benchmarkData.map(d => d.metrics.states_explored);

    const ctx = document.getElementById('benchmarkChart').getContext('2d');
    
    if (chartInstance) {
        chartInstance.destroy();
    }
    
    chartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Time Elapsed (s)',
                    data: times,
                    backgroundColor: 'rgba(59, 130, 246, 0.7)',
                    borderColor: 'rgba(59, 130, 246, 1)',
                    borderWidth: 1,
                    yAxisID: 'y'
                },
                {
                    label: 'States Explored',
                    data: states,
                    backgroundColor: 'rgba(249, 115, 22, 0.7)',
                    borderColor: 'rgba(249, 115, 22, 1)',
                    borderWidth: 1,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: { display: true, text: 'Time (s)' }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: { display: true, text: 'States' },
                    grid: { drawOnChartArea: false }
                }
            }
        }
    });
}
{
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
