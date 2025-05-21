#!/Library/Frameworks/Python.framework/Versions/3.10/bin/python3

import pygame
import sys
import random
import argparse
import copy

# Constants
DEFAULT_WIDTH = 20  # Default board width
DEFAULT_HEIGHT = 20  # Default board height
DEFAULT_SCALE = 25  # Default cell size
DEFAULT_SIZE = DEFAULT_WIDTH
CELL_SIZE = DEFAULT_SCALE
MARGIN = 50        # Margin around the grid for clues
DENSITY = 40

# RGB Color definitions
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BACKGROUND_COLOR = (200, 200, 200)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
BORDER_COLOR = (50, 50, 50)
IN_DARK_MODE = False


def generate_row(length, density):
    row = []
    filled_prob = (density / 100) * (2/3)

    max_run = max(1, int(length * 0.5))
    one_run_weights = [i for i in range(1, max_run + 1)]
    zero_run_weights = [max(1, max_run - i + 1) for i in range(1, max(2, max_run // 2 + 1))]

    # weight to have longer runs because having lots of 1s in a row is not fun
    while len(row) < length:
        is_one_run = random.random() < filled_prob
        if is_one_run:
            run_length = random.choices(range(1, max_run + 1), weights=one_run_weights)[0]
        else:
            run_length = random.choices(range(1, max_run // 2 + 1), weights=zero_run_weights)[0]
        run_length = min(run_length, length - len(row))
        row.extend([1 if is_one_run else 0] * run_length)

    return row

def apply_symmetry_noise(row, noise_level):
    # Flip a percentage of bits in the row
    noisy_row = row.copy()
    for i in range(len(noisy_row)):
        if random.random() < noise_level:
            noisy_row[i] ^= 1  # Flip 0 <-> 1
    return noisy_row

def generate_nonogram_board(width, height, density, symmetry_strength=1.0, symmetry_noise=0.0):
    board = [[0 for _ in range(width)] for _ in range(height)]

    symmetry_type = random.choices(['none', 'horizontal', 'vertical', 'rotational'], weights=[0.1, 0.3, 0.3, 0.3])[0]
    
    for y in range(height):
        if symmetry_type in ['vertical', 'rotational']:
            sym_y = height - 1 - y
        else:
            sym_y = y

        if y > sym_y:
            continue  # already filled from symmetry

        row = generate_row(width, density)
        board[y] = row

        # Determine if we apply symmetry
        if symmetry_type == 'none' or sym_y == y:
            continue

        if random.random() < symmetry_strength:
            mirrored = row.copy()
            if symmetry_type == 'horizontal':
                mirrored = row[::-1]
            elif symmetry_type == 'vertical':
                mirrored = row.copy()
            elif symmetry_type == 'rotational':
                mirrored = row[::-1]
            
            # Apply noise
            mirrored = apply_symmetry_noise(mirrored, symmetry_noise)

            board[sym_y] = mirrored
        else:
            board[sym_y] = generate_row(width, density)

    if width == height:
        if random.randint(0, 1) == 1:
            # rotate board 90 degrees
            # there's no vertical run bias, so all of the long runs are always horizontal otherwise
            return [list(reversed(col)) for col in zip(*board)]
    return board


class Nonogram:
    """
    Class representing the Nonogram game board and logic.

    Attributes:
        width (int): Width of the board in tiles.
        height (int): Height of the board in tiles.
        solution (list[list[int]]): Randomly generated correct tiles (1 for filled, 0 for empty).
        user_board (list[list[str]]): Player's input ('F' for filled, 'X' for decoy, '' for empty).
        correct_total (int): Total number of correct tiles in the solution.
        correct_count (int): Number of correct tiles marked by the user.
    """
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.solution = generate_nonogram_board(width=width, height=height, density=DENSITY, symmetry_strength=0.8, symmetry_noise=0.05)
        self.user_board = [['' for _ in range(width)] for _ in range(height)]
        self.correct_total = sum(sum(row) for row in self.solution)
        self.correct_count = 0
        self.drag_history = []  # Stack to track drag history

    
    def save_drag_state(self):
        # Deep copy current state to allow undo
        self.drag_history.append(copy.deepcopy(self.user_board))

    def undo_drag(self):
        if self.drag_history:
            self.user_board = self.drag_history.pop()
        self.check_correct()
            
    def check_correct(self):
        """Updates the number of filled tiles by the user, autofills flags for columns/rows with completed hints, and evaluates win condition."""
        count = 0
        selected = 0
        for y in range(self.height):
            for x in range(self.width):
                if self.user_board[y][x] == 'F':
                    selected += 1
                if self.solution[y][x] == 1 and self.user_board[y][x] == 'F':
                    count += 1
        self.correct_count = selected

        # If all of the clues are fulfilled for a row/column, flag the rest of the line

        matches_clues = True
        # Flag remaining tiles in matched rows
        for y in range(self.height):
            # convert filled in tiles to set of clues
            user_row = ''.join(['1' if self.user_board[y][x] == 'F' else '0' for x in range(self.width)]).split('0')
            user_clues = [len(group) for group in user_row if group]
            if user_clues == []:
                user_clues = [0]
            # check if generated clues based on user inputs match true clues
            if user_clues == self.get_row_clues()[y]:
                if user_clues != [0]: # it's super lame to have the board autofill with x's for a 0 row
                    for x in range(self.width):
                        if self.user_board[y][x] == '':
                            self.user_board[y][x] = 'X'
            else:
                matches_clues = False

        # Flag remaining tiles in matched columns
        for x in range(self.width):
            # convert filled in tiles to set of clues
            user_col = ''.join(['1' if self.user_board[y][x] == 'F' else '0' for y in range(self.height)]).split('0')
            user_clues = [len(group) for group in user_col if group]
            if user_clues == []:
                user_clues = [0]
            # check if generated clues based on user inputs match true clues
            if user_clues == self.get_col_clues()[x]:
                if user_clues != [0]: # it's super lame to have the board autofill with x's for a 0 column
                    for y in range(self.height):
                        if self.user_board[y][x] == '':
                            self.user_board[y][x] = 'X'
            else: 
                matches_clues = False

        # Check win condition
        if selected == self.correct_total:
            if not(matches_clues):
                        pygame.display.set_caption("Error in solution. Try again!")
                        return
            pygame.display.set_caption("Success! Puzzle solved.")

    def get_row_clues(self):
        """Generates numerical clues for each row based on the solution.

        Returns:
            list[list[int]]: Clues for each row.
        """
        clues = []
        for row in self.solution:
            clue = []
            count = 0
            for val in row:
                if val == 1:
                    count += 1
                elif count > 0:
                    clue.append(count)
                    count = 0
            if count > 0:
                clue.append(count)
            clues.append(clue or [0])
        return clues

    def get_col_clues(self):
        """Generates numerical clues for each column based on the solution.

        Returns:
            list[list[int]]: Clues for each column.
        """
        clues = []
        for col in range(self.width):
            clue = []
            count = 0
            for row in range(self.height):
                if self.solution[row][col] == 1:
                    count += 1
                elif count > 0:
                    clue.append(count)
                    count = 0
            if count > 0:
                clue.append(count)
            clues.append(clue or [0])
        return clues

def draw_board(screen, game, drag_axis=None, drag_start=None, cell_x=None, cell_y=None):
    """
    Renders the game board, user input, clues, and the correct tile counter.

    Args:
        screen (pygame.Surface): The Pygame window surface.
        game (Nonogram): The game instance containing board and logic.
        drag_axis (str: either 'row' or 'col'): The direction that the current drag is moving in (for highlighting)
        drag_start ((int, int)): mouse x and y location at beginning of drag
        cell_x (int): current mouse x location by cell
        cell_y (int): current mouse y location by cell
    """
    screen.fill(BACKGROUND_COLOR)
    offset_x = MARGIN + 120
    offset_y = MARGIN + 100
    row_clues = game.get_row_clues()
    col_clues = game.get_col_clues()

    # Draw grid and user selections
    for y in range(game.height):
        for x in range(game.width):
            # Highlight drag path
            if drag_axis == 'row' and drag_start and y == drag_start[1] and min(drag_start[0], cell_x) <= x <= max(drag_start[0], cell_x):
                highlight = True
            elif drag_axis == 'col' and drag_start and x == drag_start[0] and min(drag_start[1], cell_y) <= y <= max(drag_start[1], cell_y):
                highlight = True
            else:
                highlight = False
            rect = pygame.Rect(offset_x + x * CELL_SIZE, offset_y + y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            # Draw cell border
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)
            # Draw thicker vertical lines every 5 columns
            if x % 5 == 0:
                pygame.draw.line(screen, BLACK, rect.topleft, rect.bottomleft, 5)
            # Draw thicker horizontal lines every 5 rows
            if y % 5 == 0:
                pygame.draw.line(screen, BLACK, rect.topleft, rect.topright, 5)
            # Draw right and bottom border (top and left already handled by thicker lines above)
            if x == game.width - 1:
                pygame.draw.line(screen, BLACK, rect.topright, rect.bottomright, 5)
            if y == game.height - 1:
                pygame.draw.line(screen, BLACK, rect.bottomleft, rect.bottomright, 5)
            if highlight:
                pygame.draw.rect(screen, YELLOW, rect, 2)
            if game.user_board[y][x] == 'F':
                pygame.draw.rect(screen, BLACK, rect.inflate(-4, -4))
            elif game.user_board[y][x] == 'X':
                pygame.draw.line(screen, RED, rect.topleft, rect.bottomright, 3)
                pygame.draw.line(screen, RED, rect.topright, rect.bottomleft, 3)

    font = pygame.font.SysFont('Arial', max(12, CELL_SIZE // 2), bold=True)

    # Draw row clues
    for i, clue in enumerate(row_clues):
        text = font.render(' '.join(map(str, clue)), True, BLACK)
        text_rect = text.get_rect(right=offset_x - 10, centery=offset_y + i * CELL_SIZE + CELL_SIZE // 2)
        screen.blit(text, text_rect)

    # Draw column clues
    for i, clue in enumerate(col_clues):
        for j, line in enumerate(clue):
            text = font.render(str(line), True, BLACK)
            text_rect = text.get_rect(center=(offset_x + i * CELL_SIZE + CELL_SIZE // 2, offset_y - (len(clue) - j) * 20))
            screen.blit(text, text_rect)

    # Draw correct count
    counter_text = font.render(f"Filled: {game.correct_count}/{game.correct_total}", True, BLUE)
    counter_bg = pygame.Rect(screen.get_width() // 2 - counter_text.get_width() // 2 - 10, 5, counter_text.get_width() + 20, counter_text.get_height() + 10)
    pygame.draw.rect(screen, WHITE, counter_bg, border_radius=5)
    pygame.draw.rect(screen, BLACK, counter_bg, 2, border_radius=5)
    screen.blit(counter_text, (counter_bg.x + 10, counter_bg.y + 5))

    # Draw "Press H for help" prompt
    prompt_font = font
    prompt_text = prompt_font.render("Press H for help", True, (255, 255, 255))
    prompt_bg = pygame.Rect(10, screen.get_height() - 30, prompt_text.get_width() + 20, 24)
    pygame.draw.rect(screen, (50, 50, 50), prompt_bg, border_radius=5)
    pygame.draw.rect(screen, (200, 200, 200), prompt_bg, 1, border_radius=5)
    screen.blit(prompt_text, (prompt_bg.x + 10, prompt_bg.y + 4))

def dark_mode(to_dark: bool):
    """Turn on/off dark mode"""
    global WHITE, BLACK, BACKGROUND_COLOR, BLUE, YELLOW, IN_DARK_MODE
    if to_dark:
        WHITE = (0, 0, 0)
        BLACK = (255, 255, 255)
        BACKGROUND_COLOR = (20, 20, 20)
        BLUE = (144,213,255)
        YELLOW = (245, 164, 0)
    else:
        WHITE = (255, 255, 255)
        BLACK = (0, 0, 0)
        BACKGROUND_COLOR = (255, 255, 255)
        BLUE = (0, 0, 255)
        YELLOW = (255, 255, 0)
    IN_DARK_MODE = to_dark

def help_screen(screen):
    help_text = [
    "Controls",
    "----------------------------------------------------------",
    "Mouse:",
    "- Left-click: Fill tile",
    "- Right-click: Mark tile as empty",
    "- Drag to fill/cross multiple tiles within one row/column",
    "Keyboard:",
    "- SPACE: Fill tile",
    "- X: Mark tile as empty",
    "- U: Undo last drag",
    "- R: Reset board",
    "- H: Toggle this help menu",
    "- D: Toggle dark mode",
    "Complete when all filled tiles match the hidden pattern!",
    "Press ESC or 'H' to exit this help screen!"
    ]
    help_bg = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
    help_bg.fill(WHITE)
    screen.blit(help_bg, (0, 0))
    font = pygame.font.SysFont('Arial', int(min(screen.get_width(), screen.get_height()) * 0.03))
    for i, line in enumerate(help_text):
        text = font.render(line, True, BLACK)
        screen.blit(text, (60, 20 + i * 30))


def main():
    """
    Main function to initialize and run the Nonogram game loop.
    Handles event processing and updates the game state accordingly.
    """
    global DENSITY

    parser = argparse.ArgumentParser(description="Run a Nonogram game with customizable grid, scale, and difficulty.")
    parser.add_argument("--scale", type=int, default=DEFAULT_SCALE, help=f"Cell size in pixels (default: {DEFAULT_SCALE})")
    parser.add_argument("--width", type=int, help="Grid width in tiles (default: based on difficulty)")
    parser.add_argument("--height", type=int, help="Grid height in tiles (default: based on difficulty)")
    parser.add_argument("--difficulty", choices=["easy", "medium", "hard"], default="hard", help="Difficulty level: easy (10x10), medium (15x15), hard (20x20) (default: hard)")
    parser.add_argument("--density", type=int, help=f"Approximate percentage of filled tiles in solution — lower to increase difficulty (default: {DENSITY})")
    parser.add_argument("--light", action='store_true', default=False, help="Include to default to light mode")

    args = parser.parse_args()

    # Apply difficulty if width/height not specified
    if args.difficulty == "easy":
        width, height = 10, 10
    elif args.difficulty == "medium":
        width, height = 15, 15
    else:
        width, height = 20, 20

    if args.width:
        width = args.width
    if args.height:
        height = args.height
    if args.light:
        global IN_DARK_MODE
        dark_mode(not(args.light))
    if args.density:
        DENSITY = args.density


    global CELL_SIZE
    CELL_SIZE = args.scale

    pygame.init()
    game = Nonogram(width, height)
    screen_width = width * CELL_SIZE + MARGIN * 2 + 150
    screen_height = height * CELL_SIZE + MARGIN * 2 + 120
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Nonogram")

    clock = pygame.time.Clock()

    running = True
    dragging = False
    drag_key = None
    drag_axis = None  # 'col' or 'row'
    drag_mode = None  # 'select' or 'deselect'
    drag_start = None
    help = False
    while running:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        cell_x = (mouse_x - (MARGIN + 120)) // CELL_SIZE
        cell_y = (mouse_y - (MARGIN + 100)) // CELL_SIZE

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if help:
                    break
                mouse_x, mouse_y = event.pos
                cell_x = (mouse_x - (MARGIN + 120)) // CELL_SIZE
                cell_y = (mouse_y - (MARGIN + 100)) // CELL_SIZE
                if 0 <= cell_x < game.width and 0 <= cell_y < game.height:
                    dragging = True
                    drag_key = pygame.K_SPACE if event.button == 1 else pygame.K_x
                    game.save_drag_state() # save state so that undo is possible
                    drag_start = (cell_x, cell_y)
                    drag_axis = None
                    if drag_key == pygame.K_SPACE:
                        drag_mode = 'deselect' if game.user_board[cell_y][cell_x] == 'F' else 'select'
                        game.user_board[cell_y][cell_x] = '' if game.user_board[cell_y][cell_x] == 'F' else 'F'
                    elif drag_key == pygame.K_x:
                        drag_mode = 'deselect' if game.user_board[cell_y][cell_x] == 'X' else 'select'
                        game.user_board[cell_y][cell_x] = '' if game.user_board[cell_y][cell_x] == 'X' else 'X'
                    game.check_correct()
                    

            elif event.type == pygame.KEYDOWN:
                if help:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_h:
                        help = False
                        break
                    elif event.key == pygame.K_d:
                        dark_mode(not(IN_DARK_MODE))
                        break
                    else:
                        break
                if event.key == pygame.K_r:
                    pygame.display.set_caption("Nonogram")
                    # restart
                    game = Nonogram(width, height) 
                elif event.key == pygame.K_u:
                    game.undo_drag()
                elif event.key == pygame.K_d:
                    dark_mode(not(IN_DARK_MODE))
                elif event.key == pygame.K_h:
                    help = True
                elif event.key in (pygame.K_SPACE, pygame.K_x):
                    if 0 <= cell_x < game.width and 0 <= cell_y < game.height:
                        dragging = True
                        drag_key = event.key
                        game.save_drag_state()
                        drag_start = (cell_x, cell_y)
                        drag_axis = None
                        if drag_key == pygame.K_SPACE:
                            drag_mode = 'deselect' if game.user_board[cell_y][cell_x] == 'F' else 'select'
                            game.user_board[cell_y][cell_x] = '' if game.user_board[cell_y][cell_x] == 'F' else 'F'
                        elif drag_key == pygame.K_x:
                            drag_mode = 'deselect' if game.user_board[cell_y][cell_x] == 'X' else 'select'
                            game.user_board[cell_y][cell_x] = '' if game.user_board[cell_y][cell_x] == 'X' else 'X'
                        game.check_correct()

        if help:
            help_screen(screen)
        else:   
            draw_board(screen, game, drag_axis, drag_start, cell_x, cell_y)
        pygame.display.flip()
        
        # Handle dragging
        if dragging and ((drag_key in (pygame.K_SPACE, pygame.K_x) and pygame.key.get_pressed()[drag_key]) or any(pygame.mouse.get_pressed())):
            if 0 <= cell_x < game.width and 0 <= cell_y < game.height and drag_start:
                drag_start_x, drag_start_y = drag_start
                # determine axis of drag based on first movement
                if drag_axis is None and (cell_x != drag_start_x or cell_y != drag_start_y):
                    if abs(cell_x - drag_start_x) >= abs(cell_y - drag_start_y):
                        drag_axis = 'row'
                    else:
                        drag_axis = 'col'
                
                if drag_axis == 'row' and cell_y == drag_start_y:
                    for x in range(min(drag_start_x, cell_x), max(drag_start_x, cell_x) + 1):
                        if drag_key == pygame.K_SPACE:
                            game.user_board[drag_start_y][x] = '' if drag_mode == 'deselect' else 'F'
                        elif drag_key == pygame.K_x:
                            game.user_board[drag_start_y][x] = '' if drag_mode == 'deselect' else 'X'
                    game.check_correct()
                elif drag_axis == 'col' and cell_x == drag_start_x:
                    for y in range(min(drag_start_y, cell_y), max(drag_start_y, cell_y) + 1):
                        if drag_key == pygame.K_SPACE:
                            game.user_board[y][drag_start_x] = '' if drag_mode == 'deselect' else 'F'
                        elif drag_key == pygame.K_x:
                            game.user_board[y][drag_start_x] = '' if drag_mode == 'deselect' else 'X'
                    game.check_correct()
        else:
            dragging = False
            drag_key = None
            drag_axis = None
            drag_start = None

        clock.tick(30)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
