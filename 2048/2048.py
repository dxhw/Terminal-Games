#!/Library/Frameworks/Python.framework/Versions/3.10/bin/python3

import pygame
import sys
import random
import argparse
import copy
import time

parser = argparse.ArgumentParser(description="This program runs the game 2048! Please put in additional parameters to customize your game")
parser.add_argument('-scale', dest='screen_scale', help="the scale of your screen, default is 20", default=20, type=int)

args = parser.parse_args()
SCALE = args.screen_scale

# Initialize pygame
pygame.init()

# Constants
GRID_SIZE = 4
TILE_SIZE = 5 * SCALE
TILE_MARGIN = SCALE
FONT_SIZE = 3 * SCALE
WIDTH = GRID_SIZE * TILE_SIZE + (GRID_SIZE + 1) * TILE_MARGIN + SCALE * 2
HEIGHT = WIDTH + FONT_SIZE
FPS = 60

# Colors
BACKGROUND_COLOR = (187, 173, 160)
EMPTY_TILE_COLOR = (205, 193, 180)
TILE_COLORS = {
    2: (238, 228, 218),
    4: (237, 224, 200),
    8: (242, 177, 121),
    16: (245, 149, 99),
    32: (246, 124, 95),
    64: (246, 94, 59),
    128: (237, 207, 114),
    256: (237, 204, 97),
    512: (237, 200, 80),
    1024: (237, 197, 63),
    2048: (237, 194, 46),
    4096: (237, 194, 46),
    8192: (237, 194, 46),
    16384: (237, 194, 46)
}
TEXT_COLOR = (119, 110, 101)
RED = (249,26,24)

# Initialize screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2048")
font = pygame.font.Font(None, FONT_SIZE)

# Game grid
grid = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
previous_grids = {}
grid_rotated = {}
move_number = 1

def add_new_tile():
    empty_tiles = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE) if grid[r][c] == 0]
    if empty_tiles:
        r, c = random.choice(empty_tiles)
        grid[r][c] = 2 if random.random() < 0.9 else 4

def draw_grid(start_time, display_game_over=False):
    screen.fill(BACKGROUND_COLOR)

    # Display the move number
    time_text = f"Time: {int(time.time() - start_time)}s"
    time_text_surface = font.render(time_text, True, TEXT_COLOR)
    time_text_rect = time_text_surface.get_rect(left=SCALE, centery=(TILE_MARGIN + FONT_SIZE // 2))
    screen.blit(time_text_surface, time_text_rect)

    move_text = f"Move: {move_number - 1}"
    move_text_color = TEXT_COLOR
    if display_game_over:
        move_text = f"GAME OVER!"
        move_text_color = RED
    move_text_surface = font.render(move_text, True, move_text_color)
    move_text_rect = move_text_surface.get_rect(right=WIDTH - (SCALE), centery=(TILE_MARGIN + FONT_SIZE // 2))
    screen.blit(move_text_surface, move_text_rect)

    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            value = grid[r][c]
            rect = pygame.Rect(
                c * (TILE_SIZE + TILE_MARGIN) + TILE_MARGIN + SCALE,
                r * (TILE_SIZE + TILE_MARGIN) + TILE_MARGIN + FONT_SIZE + SCALE,
                TILE_SIZE,
                TILE_SIZE,
            )
            pygame.draw.rect(screen, TILE_COLORS.get(value, EMPTY_TILE_COLOR), rect)
            if value != 0:
                text_surface = font.render(str(value), True, TEXT_COLOR)
                text_rect = text_surface.get_rect(center=rect.center)
                screen.blit(text_surface, text_rect)

def slide_row_left(row):
    new_row = [value for value in row if value != 0]
    while len(new_row) < GRID_SIZE:
        new_row.append(0)
    return new_row

def merge_row(row):
    for i in range(len(row) - 1):
        if row[i] == row[i + 1] and row[i] != 0:
            row[i] *= 2
            row[i + 1] = 0
    return row

def move_left():
    global move_number
    global previous_grids
    global grid
    previous_grids[move_number] = copy.deepcopy(grid)
    for r in range(GRID_SIZE):
        grid[r] = slide_row_left(grid[r])
        grid[r] = merge_row(grid[r])
        grid[r] = slide_row_left(grid[r])
    if grid != previous_grids[move_number]:
        move_number += 1
        return True
    return False
    

def rotate_grid():
    global grid
    grid = [list(row) for row in zip(*grid[::-1])]

def move_right():
    rotate_grid()
    rotate_grid()
    changed = move_left()
    rotate_grid()
    rotate_grid()
    return changed

def move_up():
    rotate_grid()
    rotate_grid()
    rotate_grid()
    changed = move_left()
    rotate_grid()
    return changed

def move_down():
    rotate_grid()
    changed = move_left()
    rotate_grid()
    rotate_grid()
    rotate_grid()
    return changed

def undo():
    global move_number
    global grid
    global previous_grids
    if move_number != 1:
        move_number -= 1
    grid = previous_grids[move_number]
    while grid_rotated[move_number] > 0:
        rotate_grid()
        grid_rotated[move_number] -= 1

def restart():
    global grid
    global previous_grids
    global move_number
    global grid_rotated
    grid = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
    previous_grids = {}
    grid_rotated = {}
    move_number = 1
    add_new_tile()
    add_new_tile()
    previous_grids[0] = copy.deepcopy(grid)
    grid_rotated[0] = 0

def is_game_over():
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            if grid[r][c] == 0:
                return False
            if c < GRID_SIZE - 1 and grid[r][c] == grid[r][c + 1]:
                return False
            if r < GRID_SIZE - 1 and grid[r][c] == grid[r + 1][c]:
                return False
    return True

# Initialize the grid with two tiles
add_new_tile()
add_new_tile()

previous_grids[0] = copy.deepcopy(grid)
grid_rotated[0] = 0

# Main game loop
clock = pygame.time.Clock()
pygame.key.set_repeat(500, 50)
running = True
display_game_over = False
start_time = time.time()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                if not display_game_over:
                    grid_rotated[move_number] = 0
                    if move_left():
                        add_new_tile()
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                if not display_game_over:
                    grid_rotated[move_number] = 2
                    if move_right():
                        add_new_tile()
            elif event.key == pygame.K_UP or event.key == pygame.K_w:
                if not display_game_over:
                    grid_rotated[move_number] = 1
                    if move_up():
                        add_new_tile()
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                if not display_game_over:
                    grid_rotated[move_number] = 3
                    if move_down():
                        add_new_tile()
            elif event.key == pygame.K_u:
                display_game_over = False
                undo()
            elif event.key == pygame.K_r:
                start_time = time.time()
                display_game_over = False
                restart()
    
    draw_grid(start_time, display_game_over)
    pygame.display.flip()
    clock.tick(FPS)

    if is_game_over():
        display_game_over = True

pygame.quit()
sys.exit()