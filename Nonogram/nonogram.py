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

class DragState:
    def __init__(self):
        self.dragging = False     # True or False (is dragging on)
        self.key = None           # pygame.K_SPACE or pygame.K_x
        self.start = None         # (x, y)
        self.axis = None          # 'row' or 'col'
        self.mode = None          # 'select', 'deselect', 'overwrite'

    def reset(self):
        self.dragging = False
        self.key = None
        self.start = None
        self.axis = None
        self.mode = None

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

    symmetry_type = random.choices(['none', 'horizontal', 'vertical', 'rotational'], weights=[0.05, 0.3, 0.3, 0.35])[0]
    
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

    def restart(self):
        self.solution = generate_nonogram_board(width=self.width, height=self.height, density=DENSITY, symmetry_strength=0.8, symmetry_noise=0.05)
        self.user_board = [['' for _ in range(self.width)] for _ in range(self.height)]
        self.correct_total = sum(sum(row) for row in self.solution)
        self.correct_count = 0
        self.drag_history = []  # Stack to track drag history
        pygame.display.set_caption("Nonogram")

    def save_drag_state(self):
        # Deep copy current state to allow undo
        self.drag_history.append(copy.deepcopy(self.user_board))

    def undo_drag(self):
        if self.drag_history:
            self.user_board = self.drag_history.pop()
        self.check_correct()

    def clear_board(self):
        self.save_drag_state()
        self.user_board = [['' for _ in range(self.width)] for _ in range(self.height)]
        self.correct_count = 0
        pygame.display.set_caption("Nonogram")
            
    def check_correct(self):
        """Updates the number of filled tiles, auto-flags completed rows/columns, and checks win condition."""
        def extract_clues(line):
            """Extract the clues that the users selections would match"""
            groups = ''.join(['1' if cell == 'F' else '0' for cell in line]).split('0')
            clues = [len(group) for group in groups if group]
            return clues if clues else [0]

        def autofill_line(line_idx, is_row=True):
            """Flag remaining tiles in column/row with completed clues"""
            # it's super lame to have the board autofill with x's for a 0 row/column, so ignore [0]
            if is_row:
                line = [self.user_board[line_idx][x] for x in range(self.width)]
                clues_match = extract_clues(line) == self.get_row_clues()[line_idx]
                if clues_match and extract_clues(line) != [0]: 
                    for x in range(self.width):
                        if self.user_board[line_idx][x] == '':
                            self.user_board[line_idx][x] = 'X'
                return clues_match
            else:
                line = [self.user_board[y][line_idx] for y in range(self.height)]
                clues_match = extract_clues(line) == self.get_col_clues()[line_idx]
                if clues_match and extract_clues(line) != [0]:
                    for y in range(self.height):
                        if self.user_board[y][line_idx] == '':
                            self.user_board[y][line_idx] = 'X'
                return clues_match

        # Count correct selections
        selected = sum(cell == 'F' for row in self.user_board for cell in row)
        self.correct_count = selected

        # Auto-fill matched rows and columns
        rows_match = all([autofill_line(y, is_row=True) for y in range(self.height)])
        cols_match = all([autofill_line(x, is_row=False) for x in range(self.width)])

        # Check win condition
        if selected == self.correct_total:
            if not (rows_match and cols_match):
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

def draw_board(screen, game, drag_state: DragState = None):
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
            cell_x, cell_y = get_mouse_cell()
            if drag_state.axis == 'row' and drag_state.start and y == drag_state.start[1] and min(drag_state.start[0], cell_x) <= x <= max(drag_state.start[0], cell_x):
                highlight = True
            elif drag_state.axis == 'col' and drag_state.start and x == drag_state.start[0] and min(drag_state.start[1], cell_y) <= y <= max(drag_state.start[1], cell_y):
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
        BACKGROUND_COLOR = (40, 40, 40)
        BLUE = (144,213,255)
        YELLOW = (245, 164, 0)
    else:
        WHITE = (255, 255, 255)
        BLACK = (0, 0, 0)
        BACKGROUND_COLOR = (200, 200, 200)
        BLUE = (0, 0, 255)
        YELLOW = (255, 255, 0)
    IN_DARK_MODE = to_dark

def help_screen(screen):
    help_text = [
    "Controls",
    "Mouse:",
    "- Left-click: Fill tile",
    "- Right-click: Mark tile as empty",
    "- Drag to fill/cross multiple tiles within one row/column",
    "Keyboard:",
    "- SPACE: Fill tile",
    "- X: Mark tile as empty",
    "- U: Undo last drag",
    "- R: Restart game (new board)",
    "- C: Clear board",
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

def update_cell_value(current_value, key, mode):
    """Determines the new correct cell value for a given cell based on its current value, the 
    selected key, and the selected mode. 
    Returns a tuple of the new value and a boolean representing if the cell was changed"""
    if key == pygame.K_SPACE:
        target = 'F'
        other = 'X'
    elif key == pygame.K_x:
        target = 'X'
        other = 'F'
    else:
        return (current_value, False)  # Return unchanged if unsupported key

    if mode == 'overwrite':
        return (target, True) if current_value == other else (current_value, False)
    elif mode == 'deselect':
        return ('', True) if current_value == target else (current_value, False)
    elif mode == 'select':
        return (target, True) if current_value == '' else (current_value, False)
    return (current_value, False)

def parse_args():
    parser = argparse.ArgumentParser(description="Run a Nonogram game with customizable grid, scale, and difficulty.")
    parser.add_argument("--scale", type=int, default=DEFAULT_SCALE, help=f"Cell size in pixels (default: {DEFAULT_SCALE})")
    parser.add_argument("--width", type=int, help="Grid width in tiles (default: based on difficulty)")
    parser.add_argument("--height", type=int, help="Grid height in tiles (default: based on difficulty)")
    parser.add_argument("--difficulty", choices=["baby", "easy", "medium", "hard"], default="medium", help="Difficulty level: baby (5x5), easy (10x10), medium (15x15), hard (20x20) (default: medium)")
    parser.add_argument("--density", type=int, help=f"Approximate percentage of filled tiles in solution — lower to increase difficulty (default: {DENSITY})")
    parser.add_argument("--dark", action='store_true', default=False, help="Include to default to dark mode")

    return parser.parse_args()

def initialize_game(args):
    # Apply difficulty if width/height not specified
    if args.difficulty == "baby":
        width, height = 5, 5
        if args.scale == DEFAULT_SCALE: # change the scale so it's a bit less tiny
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
    global IN_DARK_MODE
    dark_mode(args.dark)
    if args.density:
        global DENSITY
        DENSITY = args.density


    global CELL_SIZE
    CELL_SIZE = args.scale

    pygame.init()
    game = Nonogram(width, height)
    screen_width = width * CELL_SIZE + MARGIN * 2 + 150
    screen_height = height * CELL_SIZE + MARGIN * 2 + 120
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Nonogram")

    return game, screen

def get_mouse_cell():
    mouse_x, mouse_y = pygame.mouse.get_pos()
    cell_x = (mouse_x - (MARGIN + 120)) // CELL_SIZE
    cell_y = (mouse_y - (MARGIN + 100)) // CELL_SIZE
    return cell_x, cell_y

def handle_event(event, game, drag_state, help_mode):
    if help_mode: return drag_state, handle_help_event(event)
    if event.type == pygame.MOUSEBUTTONDOWN:
        return handle_mouse_down(event, game, drag_state)
    elif event.type == pygame.KEYDOWN:
        return handle_key_down(event, game, drag_state)
    return drag_state, help_mode

def handle_help_event(event):
    if event.type != pygame.KEYDOWN: return True
    if event.key in (pygame.K_ESCAPE, pygame.K_h):
        return False
    elif event.key == pygame.K_d:
        dark_mode(not IN_DARK_MODE)
    return True

def determine_drag_mode(selected_cell, drag_key):
    if drag_key == pygame.K_SPACE:
        if selected_cell == 'F':
            return 'deselect'
        elif selected_cell == 'X':
            return 'overwrite'
        else:
            return 'select'
    elif drag_key == pygame.K_x:
        if selected_cell == 'X':
            return 'deselect'
        elif selected_cell == 'F':
            return 'overwrite'
        else:
            return 'select'
    else:
        return None

def handle_mouse_down(event, game, drag_state: DragState):
    cell_x, cell_y = get_mouse_cell()
    if not (0 <= cell_x < game.width and 0 <= cell_y < game.height):
        drag_state.reset()
        return False, drag_state, False
    
    drag_state.dragging = True
    drag_state.key = pygame.K_SPACE if event.button == 1 else pygame.K_x
    game.save_drag_state() # save state so that undo is possible
    drag_state.start = (cell_x, cell_y)
    drag_state.axis = None
    selected_cell = game.user_board[cell_y][cell_x]
    drag_state.mode = determine_drag_mode(selected_cell, drag_state.key)
    game.user_board[cell_y][cell_x], updated = update_cell_value(selected_cell, drag_state.key, drag_state.mode)
    if updated: game.check_correct()
    # last false means not in help mode
    return drag_state, False 

def handle_key_down(event, game, drag_state: DragState):
    if event.key == pygame.K_h:
        drag_state.reset()
        return drag_state, True
    
    elif event.key == pygame.K_r:
        game.restart()
    elif event.key == pygame.K_u:
        game.undo_drag()
    elif event.key == pygame.K_d:
        dark_mode(not(IN_DARK_MODE))
    elif event.key == pygame.K_c:
        game.clear_board()
    elif event.key in (pygame.K_SPACE, pygame.K_x):
        cell_x, cell_y = get_mouse_cell()
        if 0 <= cell_x < game.width and 0 <= cell_y < game.height:
            drag_state.dragging = True
            drag_state.key = event.key
            game.save_drag_state()
            drag_state.start = (cell_x, cell_y)
            drag_state.axis = None

            selected_cell = game.user_board[cell_y][cell_x]
            drag_state.mode = determine_drag_mode(selected_cell, drag_state.key)
            game.user_board[cell_y][cell_x], updated = update_cell_value(selected_cell, drag_state.key, drag_state.mode)
            if updated: game.check_correct()
    return drag_state, False

def handle_dragging(game, drag_state: DragState):    
    cell_x, cell_y = get_mouse_cell()
    if 0 <= cell_x < game.width and 0 <= cell_y < game.height and drag_state.start:
        drag_start_x, drag_start_y = drag_state.start
        # determine axis of drag based on first movement
        if drag_state.axis is None and (cell_x != drag_start_x or cell_y != drag_start_y):
            drag_state.axis = 'row' if abs(cell_x - drag_start_x) >= abs(cell_y - drag_start_y) else 'col'

        updated = False
        if drag_state.axis == 'row' and cell_y == drag_start_y:
            for x in range(min(drag_start_x, cell_x), max(drag_start_x, cell_x) + 1):
                current_val = game.user_board[drag_start_y][x]
                game.user_board[drag_start_y][x], updated = update_cell_value(current_val, drag_state.key, drag_state.mode)
        elif drag_state.axis == 'col' and cell_x == drag_start_x:
            for y in range(min(drag_start_y, cell_y), max(drag_start_y, cell_y) + 1):
                current_val = game.user_board[y][drag_start_x]
                game.user_board[y][drag_start_x], updated = update_cell_value(current_val, drag_state.key, drag_state.mode)
        
        if updated: game.check_correct()
        
    # Keep dragging if key or button is still pressed
    keys = pygame.key.get_pressed()
    mouse = pygame.mouse.get_pressed()
    key_or_mouse_held = (keys[drag_state.key] if drag_state.key else False) or any(mouse)
    if not(key_or_mouse_held): drag_state.reset()
    return drag_state

def game_loop(game, screen):
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
