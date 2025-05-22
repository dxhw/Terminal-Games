#!/Library/Frameworks/Python.framework/Versions/3.10/bin/python3

from game.constants import MARGIN, DEFAULT_SCALE, DEFAULT_DENSITY, DragState
from game.events import handle_event, handle_dragging
from game.draw import draw_board, help_screen, dark_mode
from game.board import Nonogram

import pygame
import sys
import argparse

CELL_SIZE = DEFAULT_SCALE


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run a Nonogram game with customizable grid, scale, and difficulty."
    )
    parser.add_argument(
        "--scale",
        type=int,
        default=DEFAULT_SCALE,
        help=f"Cell size in pixels (default: {DEFAULT_SCALE})",
    )
    parser.add_argument(
        "--width", type=int, help="Grid width in tiles (default: based on difficulty)"
    )
    parser.add_argument(
        "--height", type=int, help="Grid height in tiles (default: based on difficulty)"
    )
    parser.add_argument(
        "--difficulty",
        choices=["baby", "easy", "medium", "hard"],
        default="medium",
        help="Difficulty level: baby (5x5), easy (10x10), medium (15x15), hard (20x20) (default: medium)",
    )
    parser.add_argument(
        "--density",
        type=int,
        default=DEFAULT_DENSITY,
        help=f"Approximate percentage of filled tiles in solution — lower to increase difficulty (default: {DEFAULT_DENSITY})",
    )
    parser.add_argument(
        "--dark",
        action="store_true",
        default=False,
        help="Include to default to dark mode",
    )

    return parser.parse_args()


def initialize_game(args):
    # Apply difficulty if width/height not specified
    if args.difficulty == "baby":
        width, height = 5, 5
        if args.scale == DEFAULT_SCALE:  # change the scale so it's a bit less tiny
            args.scale = 60
    elif args.difficulty == "easy":
        width, height = 10, 10
    elif args.difficulty == "medium":
        width, height = 15, 15
    else:
        width, height = 20, 20

    if args.width:
        width = args.width
    if args.height:
        height = args.height
    dark_mode(args.dark)
    density = args.density

    global CELL_SIZE
    CELL_SIZE = args.scale

    pygame.init()
    game = Nonogram(width, height, density)
    screen_width = width * CELL_SIZE + MARGIN * 2 + 150
    screen_height = height * CELL_SIZE + MARGIN * 2 + 120
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Nonogram")

    return game, screen


def game_loop(game: Nonogram, screen: pygame.Surface):
    clock = pygame.time.Clock()

    running = True
    drag_state = DragState()
    help_mode = False
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                drag_state, help_mode = handle_event(event, game, drag_state, help_mode)

        if help_mode:
            help_screen(screen)
        else:
            draw_board(screen, game, drag_state)
        pygame.display.flip()

        if drag_state.dragging:
            drag_state = handle_dragging(game, drag_state)

        clock.tick(30)

    pygame.quit()
    sys.exit()


def main():
    """
    Main function to initialize and run the Nonogram game loop.
    Handles event processing and updates the game state accordingly.
    """
    args = parse_args()
    game, screen = initialize_game(args)
    game_loop(game, screen)


if __name__ == "__main__":
    main()
