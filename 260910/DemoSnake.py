import pygame
import random
import sys
from enum import Enum
from collections import deque

# pygame 초기화
pygame.init()

# 게임 설정
COLS = 10
ROWS = 20
BLOCK_SIZE = 30
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 700

# 색상 정의
COLORS = {
    'I': (0, 240, 241),      # 시안
    'O': (240, 224, 0),      # 노란색
    'T': (160, 0, 240),      # 보라색
    'S': (0, 240, 80),       # 초록색
    'Z': (240, 0, 0),        # 빨간색
    'J': (0, 0, 240),        # 파란색
    'L': (240, 160, 0),      # 주황색
    'BLACK': (26, 26, 46),
    'DARK_BLUE': (15, 52, 96),
    'LIGHT_BLUE': (79, 172, 254),
    'WHITE': (255, 255, 255),
    'PURPLE': (102, 126, 234),
    'GRAY': (100, 100, 100)
}

# 테트로미노 정의
TETROMINOS = {
    'I': {
        'shape': [[0, 0, 0, 0], [1, 1, 1, 1], [0, 0, 0, 0], [0, 0, 0, 0]],
        'color': 'I'
    },
    'O': {
        'shape': [[1, 1], [1, 1]],
        'color': 'O'
    },
    'T': {
        'shape': [[0, 1, 0], [1, 1, 1], [0, 0, 0]],
        'color': 'T'
    },
    'S': {
        'shape': [[0, 1, 1], [1, 1, 0], [0, 0, 0]],
        'color': 'S'
    },
    'Z': {
        'shape': [[1, 1, 0], [0, 1, 1], [0, 0, 0]],
        'color': 'Z'
    },
    'J': {
        'shape': [[1, 0, 0], [1, 1, 1], [0, 0, 0]],
        'color': 'J'
    },
    'L': {
        'shape': [[0, 0, 1], [1, 1, 1], [0, 0, 0]],
        'color': 'L'
    }
}


class GameState(Enum):
    """게임 상태"""
    READY = 1
    PLAYING = 2
    PAUSED = 3
    GAME_OVER = 4


class Piece:
    """테트로미노 블록 클래스"""
    def __init__(self, piece_type):
        self.type = piece_type
        tetromino = TETROMINOS[piece_type]
        self.shape = [row[:] for row in tetromino['shape']]
        self.color = tetromino['color']
        self.row = 0
        self.col = COLS // 2 - 2
    
    def rotate(self):
        """블록 회전"""
        n = len(self.shape)
        rotated = [[0] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                rotated[j][n - 1 - i] = self.shape[i][j]
        self.shape = rotated
    
    def get_blocks(self):
        """블록의 모든 채워진 칸 반환"""
        blocks = []
        for row in range(len(self.shape)):
            for col in range(len(self.shape[row])):
                if self.shape[row][col]:
                    blocks.append((self.row + row, self.col + col))
        return blocks


class TetrisGame:
    """테트리스 게임 메인 클래스"""
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("테트리스 게임 - Python Edition")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 20)
        
        # 게임 상태 초기화
        self.reset()
    
    def reset(self):
        """게임 리셋"""
        self.board = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.current_piece = None
        self.next_piece = None
        self.score = 0
        self.lines = 0
        self.level = 1
        self.game_state = GameState.READY
        self.drop_counter = 0
        self.game_speed = 800
        
        self.create_new_piece()
    
    def create_new_piece(self):
        """새로운 블록 생성"""
        if self.current_piece is None:
            piece_types = list(TETROMINOS.keys())
            self.current_piece = Piece(random.choice(piece_types))
        else:
            self.current_piece = self.next_piece
        
        piece_types = list(TETROMINOS.keys())
        self.next_piece = Piece(random.choice(piece_types))
        
        if self.is_collision():
            self.game_state = GameState.GAME_OVER
    
    def is_collision(self):
        """충돌 감지"""
        blocks = self.current_piece.get_blocks()
        
        for block_row, block_col in blocks:
            if (block_row >= ROWS or 
                block_col < 0 or 
                block_col >= COLS or
                (block_row >= 0 and self.board[block_row][block_col] is not None)):
                return True
        
        return False
    
    def place_piece(self):
        """블록을 보드에 배치"""
        blocks = self.current_piece.get_blocks()
        for block_row, block_col in blocks:
            if block_row >= 0:
                self.board[block_row][block_col] = self.current_piece.color
    
    def clear_lines(self):
        """완성된 라인 제거"""
        cleared_lines = 0
        row = ROWS - 1
        
        while row >= 0:
            if all(cell is not None for cell in self.board[row]):
                self.board.pop(row)
                self.board.insert(0, [None] * COLS)
                cleared_lines += 1
            else:
                row -= 1
        
        if cleared_lines > 0:
            self.lines += cleared_lines
            line_points = [0, 40, 100, 300, 1200]
            self.score += line_points[min(cleared_lines, 4)] * self.level
            self.level = self.lines // 10 + 1
            self.game_speed = max(200, 800 - (self.level - 1) * 50)
    
    def move_left(self):
        """블록 좌측 이동"""
        if self.game_state != GameState.PLAYING:
            return
        
        self.current_piece.col -= 1
        if self.is_collision():
            self.current_piece.col += 1
    
    def move_right(self):
        """블록 우측 이동"""
        if self.game_state != GameState.PLAYING:
            return
        
        self.current_piece.col += 1
        if self.is_collision():
            self.current_piece.col -= 1
    
    def rotate_piece(self):
        """블록 회전"""
        if self.game_state != GameState.PLAYING:
            return
        
        original_shape = [row[:] for row in self.current_piece.shape]
        self.current_piece.rotate()
        
        if self.is_collision():
            self.current_piece.shape = original_shape
    
    def drop_piece(self):
        """블록 하강"""
        if self.game_state != GameState.PLAYING:
            return
        
        self.current_piece.row += 1
        
        if self.is_collision():
            self.current_piece.row -= 1
            self.place_piece()
            self.clear_lines()
            self.create_new_piece()
    
    def handle_events(self):
        """이벤트 처리"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.toggle_pause()
                
                elif self.game_state == GameState.PLAYING:
                    if event.key == pygame.K_LEFT:
                        self.move_left()
                    elif event.key == pygame.K_RIGHT:
                        self.move_right()
                    elif event.key == pygame.K_DOWN:
                        self.drop_counter = self.game_speed
                    elif event.key in [pygame.K_UP, pygame.K_z, pygame.K_x]:
                        self.rotate_piece()
                
                elif self.game_state == GameState.READY:
                    if event.key == pygame.K_RETURN:
                        self.start_game()
                
                elif self.game_state == GameState.GAME_OVER:
                    if event.key == pygame.K_r:
                        self.reset()
        
        return True
    
    def start_game(self):
        """게임 시작"""
        self.game_state = GameState.PLAYING
    
    def toggle_pause(self):
        """일시 정지 토글"""
        if self.game_state == GameState.PLAYING:
            self.game_state = GameState.PAUSED
        elif self.game_state == GameState.PAUSED:
            self.game_state = GameState.PLAYING
    
    def update(self):
        """게임 상태 업데이트"""
        if self.game_state == GameState.PLAYING:
            self.drop_counter += self.clock.get_time()
            
            if self.drop_counter >= self.game_speed:
                self.drop_counter = 0
                self.drop_piece()
    
    def draw_board(self):
        """게임 보드 그리기"""
        board_x = 20
        board_y = 20
        
        # 보드 배경
        pygame.draw.rect(self.screen, COLORS['DARK_BLUE'], 
                        (board_x - 5, board_y - 5, 
                         COLS * BLOCK_SIZE + 10, ROWS * BLOCK_SIZE + 10))
        pygame.draw.rect(self.screen, COLORS['BLACK'], 
                        (board_x, board_y, 
                         COLS * BLOCK_SIZE, ROWS * BLOCK_SIZE))
        
        # 게임 보드 셀 그리기
        for row in range(ROWS):
            for col in range(COLS):
                cell_x = board_x + col * BLOCK_SIZE
                cell_y = board_y + row * BLOCK_SIZE
                
                pygame.draw.rect(self.screen, COLORS['GRAY'], 
                               (cell_x, cell_y, BLOCK_SIZE, BLOCK_SIZE), 1)
                
                if self.board[row][col] is not None:
                    color = COLORS[self.board[row][col]]
                    pygame.draw.rect(self.screen, color, 
                                   (cell_x + 1, cell_y + 1, 
                                    BLOCK_SIZE - 2, BLOCK_SIZE - 2))
        
        # 현재 블록 그리기
        if self.current_piece:
            blocks = self.current_piece.get_blocks()
            color = COLORS[self.current_piece.color]
            
            for block_row, block_col in blocks:
                if block_row >= 0:
                    cell_x = board_x + block_col * BLOCK_SIZE
                    cell_y = board_y + block_row * BLOCK_SIZE
                    pygame.draw.rect(self.screen, color, 
                                   (cell_x + 1, cell_y + 1, 
                                    BLOCK_SIZE - 2, BLOCK_SIZE - 2))
    
    def draw_info_panel(self):
        """정보 패널 그리기"""
        info_x = 350
        info_y = 20
        
        # 점수
        score_text = self.font_small.render("점수", True, COLORS['WHITE'])
        self.screen.blit(score_text, (info_x, info_y))
        score_value = self.font_large.render(str(self.score), True, (0, 240, 241))
        self.screen.blit(score_value, (info_x, info_y + 25))
        
        # 레벨
        level_text = self.font_small.render("레벨", True, COLORS['WHITE'])
        self.screen.blit(level_text, (info_x, info_y + 80))
        level_value = self.font_large.render(str(self.level), True, (0, 240, 241))
        self.screen.blit(level_value, (info_x, info_y + 105))
        
        # 라인
        lines_text = self.font_small.render("라인", True, COLORS['WHITE'])
        self.screen.blit(lines_text, (info_x, info_y + 160))
        lines_value = self.font_large.render(str(self.lines), True, (0, 240, 241))
        self.screen.blit(lines_value, (info_x, info_y + 185))
        
        # 다음 블록
        next_text = self.font_small.render("다음 블록", True, COLORS['WHITE'])
        self.screen.blit(next_text, (info_x, info_y + 240))
        
        self.draw_next_piece(info_x, info_y + 265)
    
    def draw_next_piece(self, x, y):
        """다음 블록 그리기"""
        piece_size = 20
        pygame.draw.rect(self.screen, COLORS['BLACK'], (x, y, 100, 100))
        pygame.draw.rect(self.screen, (50, 50, 70), (x, y, 100, 100), 2)
        
        if self.next_piece:
            color = COLORS[self.next_piece.color]
            for row in range(len(self.next_piece.shape)):
                for col in range(len(self.next_piece.shape[row])):
                    if self.next_piece.shape[row][col]:
                        cell_x = x + col * piece_size + 10
                        cell_y = y + row * piece_size + 10
                        pygame.draw.rect(self.screen, color, 
                                       (cell_x, cell_y, piece_size - 2, piece_size - 2))
    
    def draw_status(self):
        """상태 메시지 그리기"""
        status_y = 480
        
        if self.game_state == GameState.READY:
            status_text = self.font_medium.render("ENTER를 눌러서 시작하세요", True, (255, 200, 100))
        elif self.game_state == GameState.PLAYING:
            status_text = self.font_medium.render("게임 중...", True, (100, 255, 100))
        elif self.game_state == GameState.PAUSED:
            status_text = self.font_medium.render("일시 정지됨 (SPACE to resume)", True, (255, 165, 0))
        elif self.game_state == GameState.GAME_OVER:
            status_text = self.font_medium.render("게임 오버! R을 눌러서 다시 시작", True, (255, 100, 100))
        
        text_rect = status_text.get_rect(center=(WINDOW_WIDTH // 2, status_y))
        self.screen.blit(status_text, text_rect)
    
    def draw_controls(self):
        """조작 방법 그리기"""
        controls_y = 550
        controls = [
            "← → : 이동",
            "↓ : 빠르게 내리기",
            "↑/Z/X : 회전",
            "SPACE : 일시 정지"
        ]
        
        for i, control in enumerate(controls):
            control_text = self.font_small.render(control, True, (200, 200, 200))
            self.screen.blit(control_text, (20, controls_y + i * 25))
    
    def draw(self):
        """화면 그리기"""
        # 배경 그리기
        self.screen.fill(COLORS['BLACK'])
        
        # 그라디언트 효과 (근사)
        for i in range(WINDOW_HEIGHT):
            color_ratio = i / WINDOW_HEIGHT
            r = int(102 * (1 - color_ratio) + 15 * color_ratio)
            g = int(126 * (1 - color_ratio) + 52 * color_ratio)
            b = int(234 * (1 - color_ratio) + 96 * color_ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, i), (WINDOW_WIDTH, i))
        
        # 게임 요소 그리기
        self.draw_board()
        self.draw_info_panel()
        self.draw_status()
        self.draw_controls()
        
        pygame.display.flip()
    
    def run(self):
        """게임 메인 루프"""
        running = True
        
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)  # 60 FPS
        
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = TetrisGame()
    game.run()
