// 게임 객체
const game = {
    canvas: null,
    ctx: null,
    width: 400,
    height: 600,
    gameRunning: false,
    gameOver: false,
    score: 0,
    lives: 3,
    
    // 플레이어
    player: {
        x: 175,
        y: 550,
        width: 50,
        height: 40,
        speed: 5,
        vx: 0
    },
    
    // 총알 배열
    bullets: [],
    
    // 적 배열
    enemies: [],
    
    // 적 생성 관련
    enemySpawnRate: 0.02,
    waveCounter: 0,
    
    // 초기화
    init() {
        this.canvas = document.getElementById('gameCanvas');
        this.ctx = this.canvas.getContext('2d');
        
        this.setupEventListeners();
        this.drawInitialScreen();
    },
    
    setupEventListeners() {
        // 시작 버튼
        document.getElementById('startBtn').addEventListener('click', () => {
            this.start();
        });
        
        // 재시작 버튼
        document.getElementById('resetBtn').addEventListener('click', () => {
            this.reset();
        });
        
        // 마우스 이동
        this.canvas.addEventListener('mousemove', (e) => {
            if (!this.gameRunning) return;
            
            const rect = this.canvas.getBoundingClientRect();
            const x = e.clientX - rect.left;
            this.player.x = Math.max(0, Math.min(x - this.player.width / 2, this.width - this.player.width));
        });
        
        // 마우스 클릭 (총알 발사)
        this.canvas.addEventListener('click', () => {
            if (this.gameRunning) {
                this.shoot();
            }
        });
        
        // 키보드 이벤트
        window.addEventListener('keydown', (e) => {
            if (!this.gameRunning) return;
            
            if (e.key === 'ArrowLeft' || e.key === 'a') {
                this.player.vx = -this.player.speed;
            } else if (e.key === 'ArrowRight' || e.key === 'd') {
                this.player.vx = this.player.speed;
            } else if (e.key === ' ') {
                e.preventDefault();
                this.shoot();
            }
        });
        
        window.addEventListener('keyup', (e) => {
            if (e.key === 'ArrowLeft' || e.key === 'a' || e.key === 'ArrowRight' || e.key === 'd') {
                this.player.vx = 0;
            }
        });
    },
    
    drawInitialScreen() {
        this.ctx.fillStyle = '#1a1a2e';
        this.ctx.fillRect(0, 0, this.width, this.height);
        
        this.ctx.fillStyle = '#00ff00';
        this.ctx.font = 'bold 24px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.fillText('우주 슈팅 게임', this.width / 2, 100);
        
        this.ctx.font = '14px Arial';
        this.ctx.fillText('시작 버튼을 눌러 게임을 시작하세요', this.width / 2, 200);
        this.ctx.fillText('마우스로 이동하고 클릭해서 발사하세요', this.width / 2, 230);
    },
    
    start() {
        if (this.gameRunning) return;
        
        this.gameRunning = true;
        this.gameOver = false;
        document.getElementById('startBtn').style.display = 'none';
        document.getElementById('resetBtn').style.display = 'none';
        document.getElementById('gameStatus').textContent = '';
        
        this.gameLoop();
    },
    
    reset() {
        this.score = 0;
        this.lives = 3;
        this.gameRunning = false;
        this.gameOver = false;
        this.bullets = [];
        this.enemies = [];
        this.player.x = 175;
        this.player.y = 550;
        this.player.vx = 0;
        
        document.getElementById('score').textContent = this.score;
        document.getElementById('lives').textContent = this.lives;
        document.getElementById('startBtn').style.display = 'inline-block';
        document.getElementById('resetBtn').style.display = 'none';
        document.getElementById('gameStatus').textContent = '게임이 초기화되었습니다. 시작 버튼을 눌러주세요.';
        
        this.drawInitialScreen();
    },
    
    shoot() {
        this.bullets.push({
            x: this.player.x + this.player.width / 2 - 3,
            y: this.player.y,
            width: 6,
            height: 15,
            speed: 7
        });
    },
    
    spawnEnemy() {
        const enemyWidth = 35;
        const x = Math.random() * (this.width - enemyWidth);
        
        this.enemies.push({
            x: x,
            y: -40,
            width: 35,
            height: 30,
            speed: 2 + Math.random() * 2,
            health: 1
        });
    },
    
    update() {
        if (!this.gameRunning) return;
        
        // 플레이어 이동
        this.player.x += this.player.vx;
        this.player.x = Math.max(0, Math.min(this.player.x, this.width - this.player.width));
        
        // 총알 업데이트
        this.bullets.forEach((bullet, index) => {
            bullet.y -= bullet.speed;
            if (bullet.y < -bullet.height) {
                this.bullets.splice(index, 1);
            }
        });
        
        // 적 생성
        if (Math.random() < this.enemySpawnRate) {
            this.spawnEnemy();
        }
        
        // 적 업데이트
        this.enemies.forEach((enemy, index) => {
            enemy.y += enemy.speed;
            
            // 화면을 벗어난 적 제거
            if (enemy.y > this.height) {
                this.enemies.splice(index, 1);
                this.lives--;
                document.getElementById('lives').textContent = this.lives;
                
                if (this.lives <= 0) {
                    this.endGame();
                }
            }
        });
        
        // 충돌 감지
        this.checkCollisions();
        
        // 난이도 증가
        this.waveCounter++;
        if (this.waveCounter > 500) {
            this.enemySpawnRate = Math.min(0.08, this.enemySpawnRate + 0.005);
            this.waveCounter = 0;
        }
    },
    
    checkCollisions() {
        // 총알과 적의 충돌
        this.bullets.forEach((bullet, bulletIndex) => {
            this.enemies.forEach((enemy, enemyIndex) => {
                if (this.isColliding(bullet, enemy)) {
                    this.bullets.splice(bulletIndex, 1);
                    this.enemies.splice(enemyIndex, 1);
                    this.score += 10;
                    document.getElementById('score').textContent = this.score;
                }
            });
        });
        
        // 플레이어와 적의 충돌
        this.enemies.forEach((enemy, index) => {
            if (this.isColliding(this.player, enemy)) {
                this.enemies.splice(index, 1);
                this.lives--;
                document.getElementById('lives').textContent = this.lives;
                
                if (this.lives <= 0) {
                    this.endGame();
                }
            }
        });
    },
    
    isColliding(rect1, rect2) {
        return rect1.x < rect2.x + rect2.width &&
               rect1.x + rect1.width > rect2.x &&
               rect1.y < rect2.y + rect2.height &&
               rect1.y + rect1.height > rect2.y;
    },
    
    draw() {
        // 배경
        this.ctx.fillStyle = 'rgba(10, 14, 39, 0.2)';
        this.ctx.fillRect(0, 0, this.width, this.height);
        
        // 플레이어 그리기
        this.drawPlayer();
        
        // 총알 그리기
        this.drawBullets();
        
        // 적 그리기
        this.drawEnemies();
    },
    
    drawPlayer() {
        // 플레이어 본체 (녹색)
        this.ctx.fillStyle = '#00ff00';
        this.ctx.fillRect(this.player.x, this.player.y, this.player.width, this.player.height);
        
        // 플레이어 윤곽
        this.ctx.strokeStyle = '#00cc00';
        this.ctx.lineWidth = 2;
        this.ctx.strokeRect(this.player.x, this.player.y, this.player.width, this.player.height);
        
        // 플레이어 앞 부분 (삼각형)
        this.ctx.fillStyle = '#00ff00';
        this.ctx.beginPath();
        this.ctx.moveTo(this.player.x + this.player.width / 2, this.player.y - 10);
        this.ctx.lineTo(this.player.x, this.player.y);
        this.ctx.lineTo(this.player.x + this.player.width, this.player.y);
        this.ctx.fill();
    },
    
    drawBullets() {
        this.ctx.fillStyle = '#ffff00';
        this.bullets.forEach(bullet => {
            this.ctx.fillRect(bullet.x, bullet.y, bullet.width, bullet.height);
            this.ctx.shadowColor = 'rgba(255, 255, 0, 0.8)';
            this.ctx.shadowBlur = 5;
        });
        this.ctx.shadowBlur = 0;
    },
    
    drawEnemies() {
        this.ctx.fillStyle = '#ff4444';
        this.enemies.forEach(enemy => {
            this.ctx.fillRect(enemy.x, enemy.y, enemy.width, enemy.height);
            
            // 적 윤곽
            this.ctx.strokeStyle = '#ff0000';
            this.ctx.lineWidth = 2;
            this.ctx.strokeRect(enemy.x, enemy.y, enemy.width, enemy.height);
            
            // 적의 목 부분
            this.ctx.fillStyle = '#00ffff';
            this.ctx.fillRect(enemy.x + 8, enemy.y + enemy.height, 3, 8);
            this.ctx.fillRect(enemy.x + enemy.width - 11, enemy.y + enemy.height, 3, 8);
        });
    },
    
    endGame() {
        this.gameRunning = false;
        this.gameOver = true;
        
        document.getElementById('gameStatus').textContent = 
            `게임 오버! 최종 점수: ${this.score}`;
        document.getElementById('resetBtn').style.display = 'inline-block';
        
        // 게임 오버 화면
        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
        this.ctx.fillRect(0, 0, this.width, this.height);
        
        this.ctx.fillStyle = '#ff4444';
        this.ctx.font = 'bold 32px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.fillText('GAME OVER', this.width / 2, this.height / 2 - 30);
        
        this.ctx.fillStyle = '#ffff00';
        this.ctx.font = '20px Arial';
        this.ctx.fillText(`최종 점수: ${this.score}`, this.width / 2, this.height / 2 + 30);
    },
    
    gameLoop() {
        this.update();
        this.draw();
        
        if (this.gameRunning) {
            requestAnimationFrame(() => this.gameLoop());
        }
    }
};

// 게임 초기화
window.addEventListener('DOMContentLoaded', () => {
    game.init();
});
