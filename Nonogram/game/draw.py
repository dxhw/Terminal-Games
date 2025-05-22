import pygame
from game.board import Nonogram
from game.constants import * 
from game.util import get_mouse_cell

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BACKGROUND_COLOR = (200, 200, 200)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
IN_DARK_MODE = False


def draw_board(screen: pygame.Surface, game: Nonogram, drag_state: DragState = None):
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
        text = font.render(" ".join(map(str, clue)), True, BLACK)
        text_rect = text.get_rect(
            right=offset_x - 10, centery=offset_y + i * CELL_SIZE + CELL_SIZE // 2
        )
        screen.blit(text, text_rect)

    # Draw column clues
    for i, clue in enumerate(col_clues):
        for j, line in enumerate(clue):
            text = font.render(str(line), True, BLACK)
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
    prompt_font = font
    prompt_text = prompt_font.render("Press H for help", True, (255, 255, 255))
    prompt_bg = pygame.Rect(
        10, screen.get_height() - 30, prompt_text.get_width() + 20, 24
    )
    pygame.draw.rect(screen, (50, 50, 50), prompt_bg, border_radius=5)
    pygame.draw.rect(screen, (200, 200, 200), prompt_bg, 1, border_radius=5)
    screen.blit(prompt_text, (prompt_bg.x + 10, prompt_bg.y + 4))


def dark_mode(to_dark: bool = None):
    """Turn on/off dark mode"""
    global WHITE, BLACK, BACKGROUND_COLOR, BLUE, YELLOW, IN_DARK_MODE
    to_dark = not(IN_DARK_MODE) if to_dark == None else to_dark
    if to_dark:
        WHITE = D_WHITE
        BLACK = D_BLACK
        BACKGROUND_COLOR = D_BACKGROUND_COLOR
        BLUE = D_BLUE
        YELLOW = D_YELLOW
    else:
        WHITE = L_WHITE
        BLACK = L_BLACK
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
        "- SPACE: Fill tile",
        "- X: Mark tile as empty",
        "- U: Undo last drag",
        "- R: Restart game (new board)",
        "- C: Clear board",
        "- H: Toggle this help menu",
        "- D: Toggle dark mode",
        "Complete when all filled tiles match the hidden pattern!",
        "Press ESC or 'H' to exit this help screen!",
    ]
    help_bg = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
    help_bg.fill(WHITE)
    screen.blit(help_bg, (0, 0))
    font = pygame.font.SysFont(
        "Arial", int(min(screen.get_width(), screen.get_height()) * 0.03)
    )
    for i, line in enumerate(help_text):
        text = font.render(line, True, BLACK)
        screen.blit(text, (60, 20 + i * 30))
