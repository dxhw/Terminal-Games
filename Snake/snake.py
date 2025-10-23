#!/Library/Frameworks/Python.framework/Versions/3.10/bin/python3

import pygame
import sys
import random

pygame.init()

# --- Game Constants ---
CELL_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 20
SCORE_AREA_HEIGHT = 40  # <--- extra space above play area
WINDOW_WIDTH = CELL_SIZE * GRID_WIDTH
WINDOW_HEIGHT = CELL_SIZE * GRID_HEIGHT + SCORE_AREA_HEIGHT
FPS = 10

# Colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (220, 0, 0)
WHITE = (255, 255, 255)
GREY = (40, 40, 40)

# Directions
RIGHT = (1, 0)
LEFT = (-1, 0)
UP = (0, 1)
DOWN = (0, -1)

# Game finish states
RESTART = "restart"
GAME_OVER = "game over"
EXIT = "exit"

# Set up display
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("🐍 Snake Game")

clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 24)

# --- Snake and Food Setup ---
def random_food_position(snake):
    while True:
        pos = (random.randint(1, GRID_WIDTH - 2), random.randint(1, GRID_HEIGHT - 2))
        if pos not in snake:
            return pos

def draw_cell(position, color):
    """Draw a square cell, offset by SCORE_AREA_HEIGHT."""
    rect = pygame.Rect(
        position[0] * CELL_SIZE,
        position[1] * CELL_SIZE + SCORE_AREA_HEIGHT,  # offset here
        CELL_SIZE,
        CELL_SIZE,
    )
    pygame.draw.rect(screen, color, rect)

def draw_snake(snake, green_color):
    for pos in snake:
        draw_cell(pos, green_color)

def draw_food(food_pos):
    draw_cell(food_pos, RED)

def draw_wall(wall_pos):
    draw_cell(wall_pos, GREY)

def draw_walls():
    for i in range(GRID_WIDTH):
        draw_wall((i, 0))
        draw_wall((i, GRID_HEIGHT - 1))
    for i in range(GRID_HEIGHT):
        draw_wall((0, i))
        draw_wall((GRID_WIDTH - 1, i))

def defaults():
    snake = [(5, 5), (4, 5), (3, 5)]
    direction = RIGHT
    food_pos = random_food_position(snake)
    score = 0
    return snake, direction, food_pos, score

def make_rainbow_color():
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    if r + g + b < 40:
        g = 255
    return (r, g, b)

def draw_game_over():
    """Show red 'Game Over' text but don't clear the screen."""
    text = font.render("GAME OVER - (R)estart", True, RED)
    screen.blit(text, (WINDOW_WIDTH // 2 - text.get_width() // 2, 10))

def game_loop(snake, direction, food_pos, score):
    moving = False
    game_over = False
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                moving = True
                if not game_over:
                    if (event.key == pygame.K_UP or event.key == pygame.K_w) and direction != UP:
                        direction = DOWN
                    elif (event.key == pygame.K_DOWN or event.key == pygame.K_s) and direction != DOWN:
                        direction = UP
                    elif (event.key == pygame.K_LEFT or event.key == pygame.K_a) and direction != RIGHT:
                        direction = LEFT
                    elif (event.key == pygame.K_RIGHT or event.key == pygame.K_d) and direction != LEFT:
                        direction = RIGHT
                if (event.key == pygame.K_r):
                    return True
                elif (event.key == pygame.K_ESCAPE):
                    return False

        if moving:
            new_head = (snake[0][0] + direction[0], snake[0][1] + direction[1])

            if (
                new_head[0] <= 0 or new_head[0] >= GRID_WIDTH - 1 or
                new_head[1] <= 0 or new_head[1] >= GRID_HEIGHT - 1 or
                new_head in snake
            ):
                game_over = True

            if not game_over:
                snake.insert(0, new_head)
                if new_head == food_pos:
                    score += 1
                    food_pos = random_food_position(snake)
                    rainbow_color = make_rainbow_color()
                else:
                    snake.pop()

        # Draw everything
        screen.fill(BLACK)

        # --- Draw score above the play area ---
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        # --- Draw play area below ---
        r = min(255, max(0, (score - 8) * 20))
        g = min(255, (score + 5) * 20)
        b = min(255, max(0, (score - 12) * 20))
        snake_color = (r, g, b)
        if r == g == b == 255:
            snake_color = rainbow_color

        draw_snake(snake, snake_color)
        draw_food(food_pos)
        draw_walls()
        if game_over:
            draw_game_over()

        pygame.display.flip()
        clock.tick(FPS)

def main():
    restart = True
    while restart == True:
        restart = game_loop(*defaults())
    draw_game_over()
    pygame.display.flip()
    pygame.time.wait(1000)

if __name__ == "__main__":
    main()
