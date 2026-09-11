// 게임 설정
const COLS = 10;
const ROWS = 20;
const BLOCK_SIZE = 30;

// 테트로미노 정의 (각 블록의 모양과 색상)
const TETROMINOS = {
    I: {
        shape: [[0, 0, 0, 0], [1, 1, 1, 1], [0, 0, 0, 0], [0, 0, 0, 0]],
        color: 'I'
    },
    O: {
        shape: [[1, 1], [1, 1]],
        color: 'O'
    },
    T: {
        shape: [[0, 1, 0], [1, 1, 1], [0, 0, 0]],
        color: 'T'
    },
    S: {
        shape: [[0, 1, 1], [1, 1, 0], [0, 0, 0]],
        color: 'S'
    },
    Z: {
        shape: [[1, 1, 0], [0, 1, 1], [0, 0, 0]],
        color: 'Z'
    },
    J: {
        shape: [[1, 0, 0], [1, 1, 1], [0, 0, 0]],
        color: 'J'
    },
    L: {
        shape: [[0, 0, 1], [1, 1, 1], [0, 0, 0]],
        color: 'L'
    }
};

// 게임 상태
class TetrisGame {
    constructor() {
        this.board = Array(ROWS).fill(null).map(() => Array(COLS).fill(null));
        this.currentPiece = null;
        this.nextPiece = null;
        this.score = 0;
        this.lines = 0;
        this.level = 1;
        this.gameActive = false;
        this.gamePaused = false;
        this.dropCounter = 0;
        this.gameSpeed = 800;
        
        this.initializeGame();
        this.setupEventListeners();
        this.render();
    }

    initializeGame() {
        this.currentPiece = this.createNewPiece();
        this.nextPiece = this.createNewPiece();
    }

    createNewPiece() {
        const pieces = Object.keys(TETROMINOS);
        const randomPiece = pieces[Math.floor(Math.random() * pieces.length)];
        const tetromino = TETROMINOS[randomPiece];
        
        return {
            shape: JSON.parse(JSON.stringify(tetromino.shape)),
            color: tetromino.color,
            row: 0,
            col: Math.floor(COLS / 2) - 2
        };
    }

    setupEventListeners() {
        document.getElementById('startBtn').addEventListener('click', () => this.start());
        document.getElementById('pauseBtn').addEventListener('click', () => this.togglePause());
        document.getElementById('resetBtn').addEventListener('click', () => this.reset());
        
        document.addEventListener('keydown', (e) => this.handleKeyPress(e));
    }

    handleKeyPress(e) {
        if (!this.gameActive) return;
        
        if (e.code === 'Space') {
            e.preventDefault();
            this.togglePause();
            return;
        }

        if (this.gamePaused) return;

        switch(e.code) {
            case 'ArrowLeft':
                e.preventDefault();
                this.moveLeft();
                this.render();
                break;
            case 'ArrowRight':
                e.preventDefault();
                this.moveRight();
                this.render();
                break;
            case 'ArrowDown':
                e.preventDefault();
                this.dropCounter = this.gameSpeed;
                break;
            case 'ArrowUp':
            case 'KeyZ':
            case 'KeyX':
                e.preventDefault();
                this.rotatePiece();
                this.render();
                break;
        }
    }

    start() {
        if (this.gameActive) return;
        
        this.gameActive = true;
        this.gamePaused = false;
        document.getElementById('startBtn').disabled = true;
        document.getElementById('pauseBtn').disabled = false;
        document.getElementById('status').textContent = '게임 중...';
        document.getElementById('status').classList.remove('game-over', 'paused');
        
        this.gameLoop();
    }

    togglePause() {
        if (!this.gameActive) return;
        
        this.gamePaused = !this.gamePaused;
        const pauseBtn = document.getElementById('pauseBtn');
        const status = document.getElementById('status');
        
        if (this.gamePaused) {
            pauseBtn.textContent = '계속';
            status.textContent = '일시 정지됨';
            status.classList.add('paused');
        } else {
            pauseBtn.textContent = '일시 정지';
            status.textContent = '게임 중...';
            status.classList.remove('paused');
            this.gameLoop();
        }
    }

    gameLoop() {
        if (!this.gameActive || this.gamePaused) return;

        this.dropCounter++;

        if (this.dropCounter >= this.gameSpeed / 50) {
            this.dropCounter = 0;
            this.dropPiece();
        }

        this.render();
        setTimeout(() => this.gameLoop(), 50);
    }

    dropPiece() {
        this.currentPiece.row++;

        if (this.isCollision()) {
            this.currentPiece.row--;
            this.placePiece();
            this.clearLines();
            this.currentPiece = this.nextPiece;
            this.nextPiece = this.createNewPiece();

            if (this.isCollision()) {
                this.gameOver();
            }
        }
    }

    moveLeft() {
        this.currentPiece.col--;
        if (this.isCollision()) {
            this.currentPiece.col++;
        }
    }

    moveRight() {
        this.currentPiece.col++;
        if (this.isCollision()) {
            this.currentPiece.col--;
        }
    }

    rotatePiece() {
        const original = JSON.parse(JSON.stringify(this.currentPiece.shape));
        this.currentPiece.shape = this.rotateMatrix(this.currentPiece.shape);

        if (this.isCollision()) {
            this.currentPiece.shape = original;
        }
    }

    rotateMatrix(matrix) {
        const n = matrix.length;
        const rotated = Array(n).fill(null).map(() => Array(n).fill(0));

        for (let i = 0; i < n; i++) {
            for (let j = 0; j < n; j++) {
                rotated[j][n - 1 - i] = matrix[i][j];
            }
        }

        return rotated;
    }

    isCollision() {
        for (let row = 0; row < this.currentPiece.shape.length; row++) {
            for (let col = 0; col < this.currentPiece.shape[row].length; col++) {
                if (this.currentPiece.shape[row][col]) {
                    const boardRow = this.currentPiece.row + row;
                    const boardCol = this.currentPiece.col + col;

                    if (boardRow >= ROWS || boardCol < 0 || boardCol >= COLS) {
                        return true;
                    }

                    if (boardRow >= 0 && this.board[boardRow][boardCol]) {
                        return true;
                    }
                }
            }
        }
        return false;
    }

    placePiece() {
        for (let row = 0; row < this.currentPiece.shape.length; row++) {
            for (let col = 0; col < this.currentPiece.shape[row].length; col++) {
                if (this.currentPiece.shape[row][col]) {
                    const boardRow = this.currentPiece.row + row;
                    const boardCol = this.currentPiece.col + col;

                    if (boardRow >= 0) {
                        this.board[boardRow][boardCol] = this.currentPiece.color;
                    }
                }
            }
        }
    }

    clearLines() {
        let clearedLines = 0;

        for (let row = ROWS - 1; row >= 0; row--) {
            if (this.board[row].every(cell => cell !== null)) {
                this.board.splice(row, 1);
                this.board.unshift(Array(COLS).fill(null));
                clearedLines++;
                row++;
            }
        }

        if (clearedLines > 0) {
            this.lines += clearedLines;
            const linePoints = [0, 40, 100, 300, 1200];
            this.score += linePoints[clearedLines] * this.level;
            
            this.level = Math.floor(this.lines / 10) + 1;
            this.gameSpeed = Math.max(200, 800 - (this.level - 1) * 50);

            this.updateUI();
        }
    }

    gameOver() {
        this.gameActive = false;
        document.getElementById('startBtn').disabled = false;
        document.getElementById('pauseBtn').disabled = true;
        document.getElementById('status').textContent = '게임 오버! 다시 시작하려면 시작 버튼을 누르세요.';
        document.getElementById('status').classList.add('game-over');
    }

    reset() {
        this.board = Array(ROWS).fill(null).map(() => Array(COLS).fill(null));
        this.score = 0;
        this.lines = 0;
        this.level = 1;
        this.gameActive = false;
        this.gamePaused = false;
        this.gameSpeed = 800;
        this.dropCounter = 0;
        
        document.getElementById('startBtn').disabled = false;
        document.getElementById('pauseBtn').disabled = true;
        document.getElementById('status').textContent = '준비 완료';
        document.getElementById('status').classList.remove('game-over', 'paused');
        
        this.initializeGame();
        this.updateUI();
        this.render();
    }

    updateUI() {
        document.getElementById('score').textContent = this.score;
        document.getElementById('level').textContent = this.level;
        document.getElementById('lines').textContent = this.lines;
    }

    render() {
        const gameBoard = document.getElementById('gameBoard');
        gameBoard.innerHTML = '';

        // 게임 보드 렌더링
        for (let row = 0; row < ROWS; row++) {
            for (let col = 0; col < COLS; col++) {
                const cell = document.createElement('div');
                cell.className = 'cell';

                if (this.board[row][col]) {
                    cell.classList.add('filled', this.board[row][col]);
                }

                gameBoard.appendChild(cell);
            }
        }

        // 현재 블록 렌더링
        if (this.currentPiece) {
            for (let row = 0; row < this.currentPiece.shape.length; row++) {
                for (let col = 0; col < this.currentPiece.shape[row].length; col++) {
                    if (this.currentPiece.shape[row][col]) {
                        const boardRow = this.currentPiece.row + row;
                        const boardCol = this.currentPiece.col + col;

                        if (boardRow >= 0 && boardRow < ROWS && boardCol >= 0 && boardCol < COLS) {
                            const index = boardRow * COLS + boardCol;
                            if (index < gameBoard.children.length) {
                                gameBoard.children[index].classList.add('filled', this.currentPiece.color);
                            }
                        }
                    }
                }
            }
        }

        // 다음 블록 렌더링
        this.renderNextPiece();
        this.updateUI();
    }

    renderNextPiece() {
        const nextPieceDiv = document.getElementById('nextPiece');
        nextPieceDiv.innerHTML = '';

        const shape = this.nextPiece.shape;
        for (let row = 0; row < 4; row++) {
            for (let col = 0; col < 4; col++) {
                const cell = document.createElement('div');
                cell.className = 'cell';

                if (row < shape.length && col < shape[row].length && shape[row][col]) {
                    cell.classList.add('filled', this.nextPiece.color);
                }

                nextPieceDiv.appendChild(cell);
            }
        }
    }
}

// 게임 초기화
let game;
document.addEventListener('DOMContentLoaded', () => {
    game = new TetrisGame();
});
