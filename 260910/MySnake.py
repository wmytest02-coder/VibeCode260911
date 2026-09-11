import pygame
import random
from enum import Enum
from collections import deque

# Pygame 초기화
pygame.init()

# 게임 상수 설정
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# 색상 정의
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 200, 0)
YELLOW = (255, 255, 0)

# 방향 정의
class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

class SnakeGame:
    def __init__(self):
        """게임 초기화"""
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Snake Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.game_over_font = pygame.font.Font(None, 72)
        
        # 게임 상태 초기화
        self.reset_game()
        
    def reset_game(self):
        """게임 리셋"""
        # 뱀을 화면 중앙에서 시작
        start_x = GRID_WIDTH // 2
        start_y = GRID_HEIGHT // 2
        self.snake = deque([
            (start_x, start_y),
            (start_x - 1, start_y),
            (start_x - 2, start_y)
        ])
        
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT
        self.food = self.spawn_food()
        self.score = 0
        self.game_over = False
        
    def spawn_food(self):
        """음식 위치 생성"""
        while True:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            if (x, y) not in self.snake:
                return (x, y)
    
    def handle_events(self):
        """이벤트 처리"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and self.direction != Direction.DOWN:
                    self.next_direction = Direction.UP
                elif event.key == pygame.K_DOWN and self.direction != Direction.UP:
                    self.next_direction = Direction.DOWN
                elif event.key == pygame.K_LEFT and self.direction != Direction.RIGHT:
                    self.next_direction = Direction.LEFT
                elif event.key == pygame.K_RIGHT and self.direction != Direction.LEFT:
                    self.next_direction = Direction.RIGHT
                elif event.key == pygame.K_SPACE and self.game_over:
                    self.reset_game()
        
        return True
    
    def update(self):
        """게임 상태 업데이트"""
        if self.game_over:
            return
        
        self.direction = self.next_direction
        
        # 새로운 뱀의 머리 위치 계산
        head_x, head_y = self.snake[0]
        dx, dy = self.direction.value
        new_head_x = (head_x + dx) % GRID_WIDTH
        new_head_y = (head_y + dy) % GRID_HEIGHT
        new_head = (new_head_x, new_head_y)
        
        # 뱀이 자기 자신과 충돌했는지 확인
        if new_head in self.snake:
            self.game_over = True
            return
        
        # 뱀의 머리를 앞에 추가
        self.snake.appendleft(new_head)
        
        # 음식을 먹었는지 확인
        if new_head == self.food:
            self.score += 10
            self.food = self.spawn_food()
        else:
            # 음식을 먹지 않았으면 꼬리를 제거
            self.snake.pop()
    
    def draw(self):
        """게임 화면 그리기"""
        self.screen.fill(BLACK)
        
        # 뱀 그리기
        for i, (x, y) in enumerate(self.snake):
            rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE - 2, GRID_SIZE - 2)
            if i == 0:  # 머리
                pygame.draw.rect(self.screen, DARK_GREEN, rect)
            else:  # 몸
                pygame.draw.rect(self.screen, GREEN, rect)
        
        # 음식 그리기
        food_rect = pygame.Rect(
            self.food[0] * GRID_SIZE,
            self.food[1] * GRID_SIZE,
            GRID_SIZE - 2,
            GRID_SIZE - 2
        )
        pygame.draw.rect(self.screen, RED, food_rect)
        
        # 점수 그리기
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # 게임 오버 메시지
        if self.game_over:
            game_over_text = self.game_over_font.render("GAME OVER", True, RED)
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            self.screen.blit(game_over_text, text_rect)
            
            restart_text = self.font.render("Press SPACE to restart", True, WHITE)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            self.screen.blit(restart_text, restart_rect)
        
        pygame.display.flip()
    
    def run(self):
        """게임 메인 루프"""
        running = True
        
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(10)  # 10 FPS로 게임 속도 조정
        
        pygame.quit()

if __name__ == "__main__":
    game = SnakeGame()
    game.run()
