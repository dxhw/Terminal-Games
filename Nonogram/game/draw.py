import pygame
from game.board import Nonogram
from game.constants import * 

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (120, 120, 120)
BACKGROUND_COLOR = (200, 200, 200)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
IN_DARK_MODE = False
CELL_SIZE = DEFAULT_SCALE

def update_cell_size(scale=None, increase=False, decrease=False):
    global CELL_SIZE
    if scale:
        CELL_SIZE = scale
        return
    if increase:
        CELL_SIZE += 1
        return
    if decrease:
        CELL_SIZE -= 1
        return

def get_mouse_cell() -> tuple[int, int]:
    mouse_x, mouse_y = pygame.mouse.get_pos()
    cell_x = (mouse_x - (MARGIN + 120)) // CELL_SIZE
    cell_y = (mouse_y - (MARGIN + 100)) // CELL_SIZE
    return cell_x, cell_y

def draw_board(screen: pygame.Surface, game: Nonogram, drag_state: DragState):
    """
    Renders the game board, user input, clues, and the correct tile counter.

    Args:
        screen (pygame.Surface): The Pygame window surface.
        game (Nonogram): The game instance containing board and logic.
        drag_axis (DragAxis): The direction that the current drag is moving in (for highlighting)
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
            if (
                drag_state.axis == DragAxis.ROW
                and drag_state.start
                and y == drag_state.start[1]
                and min(drag_state.start[0], cell_x)
                <= x
                <= max(drag_state.start[0], cell_x)
            ):
                highlight = True
            elif (
                drag_state.axis == DragAxis.COL
                and drag_state.start
                and x == drag_state.start[0]
                and min(drag_state.start[1], cell_y)
                <= y
                <= max(drag_state.start[1], cell_y)
            ):
                highlight = True
            else:
                highlight = False
            rect = pygame.Rect(
                offset_x + x * CELL_SIZE, offset_y + y * CELL_SIZE, CELL_SIZE, CELL_SIZE
            )
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
            if game.user_board[y][x] == CellState.FILLED:
                pygame.draw.rect(screen, BLACK, rect.inflate(-4, -4))
            elif game.user_board[y][x] == CellState.CROSSED:
                pygame.draw.line(screen, RED, rect.topleft, rect.bottomright, 3)
                pygame.draw.line(screen, RED, rect.topright, rect.bottomleft, 3)

    font = pygame.font.SysFont("Arial", max(12, CELL_SIZE // 2), bold=True)

    # Draw row clues
    for i, clue in enumerate(row_clues):
        clue_color = GRAY if game.check_clues_match(i) else BLACK
        text = font.render(" ".join(map(str, clue)), True, clue_color)
        text_rect = text.get_rect(
            right=offset_x - 10, centery=offset_y + i * CELL_SIZE + CELL_SIZE // 2
        )
        screen.blit(text, text_rect)

    # Draw column clues
    for i, clue in enumerate(col_clues):
        clue_color = GRAY if game.check_clues_match(i, False) else BLACK
        for j, line in enumerate(clue):
            text = font.render(str(line), True, clue_color)
            text_rect = text.get_rect(
                center=(
                    offset_x + i * CELL_SIZE + CELL_SIZE // 2,
                    offset_y - (len(clue) - j) * 20,
                )
            )
            screen.blit(text, text_rect)

    # Draw correct count
    counter_text = font.render(
        f"Filled: {game.correct_count}/{game.correct_total}", True, BLUE
    )
    counter_bg = pygame.Rect(
        screen.get_width() // 2 - counter_text.get_width() // 2 - 10,
        5,
        counter_text.get_width() + 20,
        counter_text.get_height() + 10,
    )
    pygame.draw.rect(screen, WHITE, counter_bg, border_radius=5)
    pygame.draw.rect(screen, BLACK, counter_bg, 2, border_radius=5)
    screen.blit(counter_text, (counter_bg.x + 10, counter_bg.y + 5))

    # Draw "Press H for help" prompt
    help_prompt_font = font
    help_prompt_text = help_prompt_font.render("Press H for help", True, (255, 255, 255))
    help_prompt_bg = pygame.Rect(
        10, screen.get_height() - 30, help_prompt_text.get_width() + 20, help_prompt_text.get_height() + 10
    )
    pygame.draw.rect(screen, (50, 50, 50), help_prompt_bg, border_radius=5)
    pygame.draw.rect(screen, (200, 200, 200), help_prompt_bg, 1, border_radius=5)
    screen.blit(help_prompt_text, (help_prompt_bg.x + 10, help_prompt_bg.y + 4))

    # Draw auto flag on/off box
    autoflag_prompt_font = font
    autoflag_state = "on" if game.autoflag else "off"
    autoflag_prompt_text = autoflag_prompt_font.render("Auto flag " + autoflag_state, True, (255, 255, 255))
    autoflag_prompt_bg = pygame.Rect(
        help_prompt_text.get_width() * 1.4 , screen.get_height() - 30, help_prompt_text.get_width() - 3, help_prompt_text.get_height() + 10
    )
    pygame.draw.rect(screen, (50, 50, 50), autoflag_prompt_bg, border_radius=5)
    pygame.draw.rect(screen, (200, 200, 200), autoflag_prompt_bg, 1, border_radius=5)
    screen.blit(autoflag_prompt_text, (autoflag_prompt_bg.x + 10, autoflag_prompt_bg.y + 4))


def dark_mode(to_dark = None):
    """Turn on/off dark mode"""
    global WHITE, BLACK, BACKGROUND_COLOR, BLUE, YELLOW, IN_DARK_MODE, GRAY
    to_dark = not(IN_DARK_MODE) if to_dark == None else to_dark
    if to_dark:
        WHITE = D_WHITE
        BLACK = D_BLACK
        GRAY = D_GRAY
        BACKGROUND_COLOR = D_BACKGROUND_COLOR
        BLUE = D_BLUE
        YELLOW = D_YELLOW
    else:
        WHITE = L_WHITE
        BLACK = L_BLACK
        GRAY = L_GRAY
        BACKGROUND_COLOR = L_BACKGROUND_COLOR
        BLUE = L_BLUE
        YELLOW = L_YELLOW
    IN_DARK_MODE = to_dark


def help_screen(screen: pygame.Surface):
    help_text = [
        "Controls",
        "Mouse:",
        "- Left-click: Fill tile",
        "- Right-click: Mark tile as empty",
        "- Drag to fill/cross multiple tiles within one row/column",
        "Keyboard:",
        "- MINUS: Reduce cell/font size",
        "- EQUALS: Increase cell/font size",
        "- SPACE: Fill tile",
        "- X: Mark tile as empty",
        "- U: Undo last drag",
        "- R: Restart game (new board)",
        "- C: Clear board",
        "- H: Toggle this help menu",
        "- D: Toggle dark mode",
        "- A: Toggle auto flag when line matches hints",
        "Complete when all filled tiles match the hidden pattern!",
        "Press ESC or 'H' to exit this help screen!",
    ]
    help_bg = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
    help_bg.fill(WHITE)
    screen.blit(help_bg, (0, 0))
    font = pygame.font.SysFont(
        "Arial", int(CELL_SIZE * 3 / 4)
    )
    top_bottom_margin = 20
    help_text_length = len(help_text)
    space_between_lines = int((screen.get_height() - top_bottom_margin) / help_text_length)
    for i, line in enumerate(help_text):
        text = font.render(line, True, BLACK)
        screen.blit(text, (20, 10 + i * space_between_lines))
