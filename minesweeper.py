#!/Library/Frameworks/Python.framework/Versions/3.10/bin/python3

import pygame
import sys
import random
from enum import Enum
import time
import argparse
import sys


class GameSize(Enum):
    LARGE = 1
    MEDIUM = 2
    SMALL = 3
    CUSTOM = 4

parser = argparse.ArgumentParser(description="This program runs the game minesweeper! Please put in additional parameters to customize your game")
parser.add_argument('-size', dest='gamesize', help="the gamesize, default is large", choices=["small", "medium", "large", "custom"], default="large")
parser.add_argument('-scale', dest='screen_scale', help="the scale of your screen, default is 30", default=30, type=int)
parser.add_argument("-height", dest="c_height", help="height to be used for a custom board", type=int)
parser.add_argument("-width", dest="c_width", help="width to be used for a custom board", type=int)
parser.add_argument("-mines", dest="c_mines", help="mine number to be used for a custom board", type=int)

args = parser.parse_args()
GAME_SIZE = None
match args.gamesize:
    case "small":
        GAME_SIZE = GameSize.SMALL
    case "medium":
        GAME_SIZE = GameSize.MEDIUM
    case "large":
        GAME_SIZE = GameSize.LARGE
    case "custom":
        GAME_SIZE = GameSize.CUSTOM

# Validation logic for custom game size
if args.gamesize == "custom":
    if args.c_height is None or args.c_width is None or args.c_mines is None:
        parser.error("When size is 'custom', -height, -width, and -mines must be specified.")
    if args.c_height <= 0 or args.c_width <= 0 or args.c_mines <= 0:
        parser.error("Height, width, and mines must be positive integers.")

# Custom game variables
CUSTOM_W = args.c_width # width
CUSTOM_H = args.c_height # height
CUSTOM_M = args.c_mines # number of mines

SCALE = args.screen_scale
INFO_BAR_HEIGHT = int(SCALE * 2)

# Initialize the game
pygame.init()

if GAME_SIZE == GameSize.LARGE:
    WIDTH, HEIGHT = SCALE * 30, SCALE * 16 + INFO_BAR_HEIGHT
    TILE_SIZE = SCALE
    GRID_WIDTH = WIDTH // TILE_SIZE #30
    GRID_HEIGHT = (HEIGHT - INFO_BAR_HEIGHT) // TILE_SIZE #16
    MINE_COUNT = 99
elif GAME_SIZE == GameSize.MEDIUM:
    WIDTH, HEIGHT = SCALE * 16, SCALE * 16 + INFO_BAR_HEIGHT
    TILE_SIZE = SCALE
    GRID_WIDTH = WIDTH // TILE_SIZE #16
    GRID_HEIGHT = (HEIGHT - INFO_BAR_HEIGHT) // TILE_SIZE #16
    MINE_COUNT = 40
elif GAME_SIZE == GameSize.SMALL:
    WIDTH, HEIGHT = SCALE * 9, SCALE * 9 + INFO_BAR_HEIGHT
    TILE_SIZE = SCALE
    GRID_WIDTH = WIDTH // TILE_SIZE #9
    GRID_HEIGHT = (HEIGHT - INFO_BAR_HEIGHT) // TILE_SIZE #9
    MINE_COUNT = 10
elif GAME_SIZE == GameSize.CUSTOM:
    WIDTH, HEIGHT = SCALE * CUSTOM_W, SCALE * CUSTOM_H + INFO_BAR_HEIGHT
    TILE_SIZE = SCALE
    GRID_WIDTH = WIDTH // TILE_SIZE #9
    GRID_HEIGHT = (HEIGHT - INFO_BAR_HEIGHT) // TILE_SIZE #9
    MINE_COUNT = CUSTOM_M

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (192, 192, 192)
BLUE = (0, 0, 255) #1
GREEN = (10,124,6) #2
RED = (249,26,24) #3
DARK_BLUE = (0, 0, 123) #4
MAROON = (130, 23, 22) #5
TURQOISE = (2,123,123) #6
PURPLE = (132, 0, 132) #7
GRAY_EIGHT = (114,114,114) #8

FPS = 20


# Create screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Minesweeper")

# Load assets
font = pygame.font.Font(None, SCALE)

# Place mines
def place_mines(grid):
    mines = set()
    while len(mines) < MINE_COUNT:
        x, y = random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1)
        if (x, y) not in mines:
            mines.add((x, y))
            grid[y][x] = -1  # Mine
    return grid

def calculate_nums(grid):
    # Calculate numbers
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if grid[y][x] == -1:
                continue
            count = 0
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT and grid[ny][nx] == -1:
                        count += 1
            grid[y][x] = count
    return grid

def num_revealed(revealed):
    num = 0
    for row in revealed:
        for cell in row:
            if cell == 1:
                num += 1
    return num

def reset_game():
    # Set game variables
    grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    revealed = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    grid = place_mines(grid)
    grid = calculate_nums(grid)
    return grid, revealed

def in_bounds(coord):
    ty, tx = coord
    if ty < 0 or ty > GRID_HEIGHT - 1 or tx < 0 or tx > GRID_WIDTH - 1:
        return False
    return True

def get_surrounding_coords(coord):
    ty, tx = coord
    coords = [(ty - 1, tx - 1), (ty - 1, tx), (ty - 1, tx + 1), 
              (ty, tx - 1),                   (ty, tx + 1), 
              (ty + 1, tx - 1), (ty + 1, tx), (ty + 1, tx + 1)]
    coords = [coord for coord in coords if in_bounds(coord)]
    return coords

def flood_fill(coord, grid, revealed, broken=False):
    ty, tx = coord 
    if not in_bounds(coord):
        return revealed, broken
    if broken:
        return revealed, broken
    num = grid[ty][tx]
    revealed[ty][tx] = 1
    if num == -1:
        return revealed, True
    if num != 0:
        return revealed, False
    coords = get_surrounding_coords(coord)
    while coords:
        next_coord = coords.pop()
        if revealed[next_coord[0]][next_coord[1]] == 0:
            revealed, broken = flood_fill(next_coord, grid, revealed, broken)
    return revealed, broken

def mandatory_flood(coord, grid, revealed, broken=False):
    surrounding_flags = 0
    count = grid[coord[0]][coord[1]]
    for count_coord in get_surrounding_coords(coord):
        if revealed[count_coord[0]][count_coord[1]] == 2:
            surrounding_flags += 1
    if surrounding_flags == count:
        for next_coord in get_surrounding_coords(coord):
            if revealed[next_coord[0]][next_coord[1]] == 0:
                revealed, broken = flood_fill(next_coord, grid, revealed, broken)
                if broken:
                    break
    return revealed, broken

#if the first click is a bomb, reset the board and try again
def first_click(ty, tx, grid, revealed):
    try_num = 0
    never_break = False
    # if the number of mines is reasonable, never give up on finding a good starting board
    if MINE_COUNT / (GRID_HEIGHT * GRID_WIDTH) < 0.25:
        never_break = True
    # if your mine number is outrageously high, your game might end quickly or you might not get a 0
    while grid[ty][tx] != 0 and (try_num < 300 or not never_break):
        grid, revealed = reset_game()
        try_num += 1 
    revealed, _ = flood_fill((ty, tx), grid, revealed)
    return grid, revealed
    
# Main game loop
def main():
    clock = pygame.time.Clock()  # Create a clock object
    start_time = time.time()
    grid, revealed = reset_game()
    first = True
    running = True
    broken = False
    flag_count = 0
    end_time = None
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                tx, ty = mx // TILE_SIZE, (my - INFO_BAR_HEIGHT) // TILE_SIZE
                
                if event.button == 1:  # Left click
                    #first click should be good
                    if first:
                        grid, revealed = first_click(ty, tx, grid, revealed)
                        start_time = time.time()
                        flag_count = 0
                        first = False
                    else:
                        revealed, broken = flood_fill((ty, tx), grid, revealed, broken)

                if event.button == 3: # Right click
                    if revealed[ty][tx] == 2:
                        revealed[ty][tx] = 0
                        flag_count -= 1
                    if revealed[ty][tx] == 0:
                        revealed[ty][tx] = 2
                        flag_count += 1

            elif event.type == pygame.KEYDOWN:
                #reset
                if event.key == pygame.K_r:
                    first = True
                    broken = False
                    start_time = time.time()
                    end_time = None
                    flag_count = 0
                    grid, revealed = reset_game()
                # space is flag if unrevealed, flood if revealed and matching number of flags surrounding
                if event.key == pygame.K_SPACE:
                    if not broken:
                        mx, my = pygame.mouse.get_pos()
                        tx, ty = mx // TILE_SIZE, (my - INFO_BAR_HEIGHT) // TILE_SIZE
                        #if unrevealed, flag
                        if revealed[ty][tx] == 0:
                            revealed[ty][tx] = 2
                            flag_count += 1
                        #if revealed, flood fill
                        elif revealed[ty][tx] == 1:
                            revealed, broken = mandatory_flood((ty, tx), grid, revealed, broken)
                        else:
                            revealed[ty][tx] = 0
                            flag_count -= 1

        # Drawing
        screen.fill(GRAY)
        if broken and not end_time:
            end_time = time.time()

        # Draw info bar
        pygame.draw.rect(screen, WHITE, (0, 0, WIDTH, INFO_BAR_HEIGHT))
        if end_time:
            time_text = font.render(f"Time: {round(end_time - start_time)}s", True, BLACK)
        elif first:
            time_text = font.render("Time: 0s", True, BLACK)
        else:
            time_text = font.render(f"Time: {round(time.time() - start_time)}s", True, BLACK)
        time_rect = time_text.get_rect(left = 10, centery=INFO_BAR_HEIGHT / 4)
        screen.blit(time_text, time_rect)
        flag_text_color = RED if flag_count > MINE_COUNT else BLACK
        flags_text = font.render(f"Flags: {flag_count}/{MINE_COUNT}", True, flag_text_color)
        flag_rect = flags_text.get_rect(right = WIDTH - 10, centery=INFO_BAR_HEIGHT / 4)
        screen.blit(flags_text, flag_rect)
        win_text = None
        if broken:
            win_text = font.render("YOU HIT A MINE!", True, RED)
        if not broken and num_revealed(revealed) == (GRID_WIDTH * GRID_HEIGHT) - MINE_COUNT:
            if not end_time:
                end_time = time.time()
            win_text = font.render("FIELD CLEARED!", True, GREEN)
        if win_text:
            win_rect = win_text.get_rect(center=(WIDTH//2, INFO_BAR_HEIGHT * 3 / 4))
            screen.blit(win_text, win_rect)

        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE + INFO_BAR_HEIGHT, TILE_SIZE, TILE_SIZE)
                if revealed[y][x] == 2:
                    pygame.draw.rect(screen, RED, rect)
                elif revealed[y][x] == 1:
                    if grid[y][x] == -1:
                        pygame.draw.rect(screen, BLACK, rect)
                    else:
                        pygame.draw.rect(screen, WHITE, rect)
                        num = grid[y][x]
                        color =  None
                        if num > 0:
                            match num:
                                case 1:
                                    color = BLUE
                                case 2:
                                    color = GREEN
                                case 3:
                                    color = RED
                                case 4:
                                    color = DARK_BLUE
                                case 5:
                                    color = MAROON
                                case 6:
                                    color = TURQOISE
                                case 7:
                                    color = PURPLE
                                case 8:
                                    color = BLACK
                            text = font.render(str(grid[y][x]), True, color)
                            num_rect = text.get_rect(center=rect.center)
                            screen.blit(text, num_rect)
                else:
                    pygame.draw.rect(screen, GRAY, rect)
                pygame.draw.rect(screen, BLACK, rect, 1)
                if broken and grid[y][x] == -1:
                    inner_rect = pygame.Rect(0, 0, TILE_SIZE // 2, TILE_SIZE // 2)
                    inner_rect.center = rect.center
                    pygame.draw.rect(screen, BLACK, inner_rect)
                if broken and grid[y][x] != -1 and revealed[y][x] == 2:
                    inner_rect = pygame.Rect(0, 0, TILE_SIZE // 2, TILE_SIZE // 2)
                    inner_rect.center = rect.center
                    pygame.draw.rect(screen, WHITE, inner_rect)
    
        if not end_time or not time.time() - end_time > 2:
            pygame.display.flip()
        clock.tick(FPS)  # Limit the frame rate to 20 FPS

main()
pygame.quit()
sys.exit()
