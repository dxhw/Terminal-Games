#!/Library/Frameworks/Python.framework/Versions/3.10/bin/python3

import pygame
import sys
import random
import argparse
from constants import *
from snake_ai import simple_ai_direction_chooser

parser = argparse.ArgumentParser(description="This program runs the game Snake! Please put in additional parameters to customize your game")
parser.add_argument('-scale', dest='cell_size', help="the scale of your screen, default is 20", default=20, type=int)
parser.add_argument("-height", dest="g_height", help="height to be used for the board, default 20", default=20, type=int)
parser.add_argument("-width", dest="g_width", help="width to be used for the board, default 30", default=30, type=int)
parser.add_argument("-speed", dest="speed", help="the speed of the game (in FPS), default is 10", default=10, type=int)
parser.add_argument("-portals", action="store_true", help="include this flag to play with portals!")
parser.add_argument("-ai", action="store_true", help="include this flag to play with an AI snake!")

args = parser.parse_args()

# --- Game Constants ---
CELL_SIZE = args.cell_size
GRID_WIDTH = args.g_width
GRID_HEIGHT = args.g_height
SCORE_AREA_HEIGHT = CELL_SIZE * 2
WINDOW_WIDTH = CELL_SIZE * GRID_WIDTH
WINDOW_HEIGHT = CELL_SIZE * GRID_HEIGHT + SCORE_AREA_HEIGHT
PORTALS_ON = args.portals
AI_ON = args.ai
FPS = args.speed

# Validation logic for custom game size
if CELL_SIZE <= 0 or GRID_WIDTH <= 0 or GRID_HEIGHT <= 0 or FPS <= 0:
    parser.error("scale, height, width, and speed must be positive integers.")

pygame.init()

# Set up display
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("🐍 Snake Game")

clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 24)

# --- Snake and Food Setup ---
def random_food_position(snake, other_unallowed=[]):
    while True:
        pos = (random.randint(1, GRID_WIDTH - 2), random.randint(1, GRID_HEIGHT - 2))
        if pos not in snake and pos not in other_unallowed:
            return pos

def random_empty_position(snake, food_pos, other_unallowed = []):
    found_pos = False
    while not found_pos:
        pos = (random.randint(2, GRID_WIDTH - 3), random.randint(2, GRID_HEIGHT - 3))
        found_pos = pos not in snake and pos != food_pos and pos not in other_unallowed
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

def draw_portal(portal_pos):
    draw_cell(portal_pos, PURPLE)

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
    portal_entry = None
    portal_exit = None
    ai_snake = []
    ai_direction = None
    if PORTALS_ON:
        portal_entry = random_empty_position(snake, food_pos)
        portal_exit = random_empty_position(snake, food_pos, [portal_entry])
    if AI_ON:
        ai_snake = [random_empty_position(snake, food_pos, [portal_entry, portal_exit])]
        ai_direction = RIGHT
    return snake, direction, food_pos, score, portal_entry, portal_exit, ai_snake, ai_direction

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

def move_snake(direction, snake, food_pos, portal_entry=None, portal_exit=None, other_snake=[]):
    game_over = False
    new_head = (snake[0][0] + direction[0], snake[0][1] + direction[1])
    if PORTALS_ON:
        assert portal_exit != None and portal_entry != None
        if new_head == portal_entry:
            new_head = portal_exit[0] + direction[0], portal_exit[1] + direction[1]
            snake.insert(0, portal_entry)
        if new_head == portal_exit:
            new_head = portal_entry[0] + direction[0], portal_entry[1] + direction[1]
            snake.insert(0, portal_exit)

    if (
        new_head[0] <= 0 or new_head[0] >= GRID_WIDTH - 1 or
        new_head[1] <= 0 or new_head[1] >= GRID_HEIGHT - 1 or
        ((new_head in snake or new_head in other_snake) and 
        (new_head != portal_entry) and (new_head != portal_exit))
    ):
        game_over = True

    if game_over:
        if new_head == snake[-1] or (len(other_snake) > 0 and new_head == other_snake[-1]):
            game_over = False # snake can move into the spot that the snake is moving away from

    got_food = False
    new_portal = False
    if not game_over:
        snake.insert(0, new_head)
        if new_head == food_pos:
            got_food = True
        else:
            popped = snake.pop()
            if PORTALS_ON:
                exited_portal = popped == portal_exit or popped == portal_entry
                portal_entry_in_use = portal_entry in snake or portal_entry in other_snake
                portal_exit_in_use = portal_exit in snake or portal_exit in other_snake
                if exited_portal and not portal_entry_in_use and not portal_exit_in_use:
                    new_portal = True
    return got_food, game_over, new_portal


def game_loop(snake, direction, food_pos, score, portal_entry=None, portal_exit=None, ai_snake=[], ai_direction=None):
    moving = False
    move_by_key = False
    game_over = False
    got_food = False
    ai_score = 0
    new_portal = False
    ai_new_portal = False
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
                    got_food, game_over, new_portal = move_snake(direction, snake, food_pos, portal_entry, portal_exit, ai_snake)
                    move_by_key = True
                if (event.key == pygame.K_r):
                    return True
                elif (event.key == pygame.K_ESCAPE):
                    return False

        if moving and not game_over:
            if not move_by_key:
                got_food, game_over, new_portal = move_snake(direction, snake, food_pos, portal_entry, portal_exit, ai_snake)
            else:
                move_by_key = False
            if got_food:
                score += 1
                unallowed_spots = [portal_entry, portal_exit]
                unallowed_spots.extend(ai_snake)
                food_pos = random_food_position(snake, unallowed_spots)
                rainbow_color = make_rainbow_color()
            if ai_snake:
                ai_direction = simple_ai_direction_chooser(ai_direction, ai_snake, snake, food_pos, GRID_WIDTH, GRID_HEIGHT)
                ai_got_food, ai_game_over, ai_new_portal = move_snake(ai_direction, ai_snake, food_pos, portal_entry, portal_exit, snake)
                if ai_got_food:
                    unallowed_spots = [portal_entry, portal_exit]
                    unallowed_spots.extend(ai_snake)
                    food_pos = random_food_position(snake, unallowed_spots)
                    ai_score += 1
                if ai_game_over:
                    ai_snake = [random_empty_position(snake, food_pos, [portal_entry, portal_exit])]
                    ai_score = 0
            if new_portal or ai_new_portal:
                portal_entry = random_empty_position(snake, food_pos)
                portal_exit = random_empty_position(snake, food_pos, [portal_entry])

        # Draw everything
        screen.fill(BLACK)

        # --- Draw score above the play area ---
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        if AI_ON:
            ai_score_text = font.render(f"AI Score: {ai_score}", True, WHITE)
            text_width = ai_score_text.get_width()
            screen.blit(ai_score_text, (WINDOW_WIDTH - 10 - text_width, 10))

        # --- Draw play area below ---
        r = min(255, max(0, (score - 8) * 20))
        g = min(255, (score + 5) * 20)
        b = min(255, max(0, (score - 12) * 20))
        snake_color = (r, g, b)
        if snake_color == WHITE:
            snake_color = rainbow_color


        draw_walls()
        if game_over:
            draw_game_over()
        if AI_ON:
            draw_snake(ai_snake, BLUE)
        draw_snake(snake, snake_color)
        if PORTALS_ON:
            draw_portal(portal_entry)
            draw_portal(portal_exit)
        draw_food(food_pos)

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
