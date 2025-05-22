import pygame
from game.draw import dark_mode
from game.constants import DragState, CellState, DragMode, DragAxis
from game.board import Nonogram
from game.util import get_mouse_cell


def update_cell_value(
    current_value: CellState, key: int, mode: DragMode
) -> tuple[CellState, bool]:
    """Determines the new correct cell value for a given cell based on its current value, the
    selected key, and the selected mode.
    Returns a tuple of the new value and a boolean representing if the cell was changed
    """
    if key == pygame.K_SPACE:
        target = CellState.FILLED
        other = CellState.CROSSED
    elif key == pygame.K_x:
        target = CellState.CROSSED
        other = CellState.FILLED
    else:
        return (current_value, False)  # Return unchanged if unsupported key

    if mode == DragMode.OVERWRITE:
        return (target, True) if current_value == other else (current_value, False)
    elif mode == DragMode.DESELECT:
        return (
            (CellState.EMPTY, True)
            if current_value == target
            else (current_value, False)
        )
    elif mode == DragMode.SELECT:
        return (
            (target, True)
            if current_value == CellState.EMPTY
            else (current_value, False)
        )
    return (current_value, False)


def handle_event(
    event: pygame.event, game: Nonogram, drag_state: DragState, help_mode: bool
) -> tuple[DragState, bool]:
    if help_mode:
        return drag_state, handle_help_event(event)
    if event.type == pygame.MOUSEBUTTONDOWN:
        return handle_mouse_down(event, game, drag_state)
    elif event.type == pygame.KEYDOWN:
        return handle_key_down(event, game, drag_state)
    return drag_state, help_mode


def handle_help_event(event: pygame.event) -> bool:
    if event.type != pygame.KEYDOWN:
        return True
    if event.key in (pygame.K_ESCAPE, pygame.K_h):
        return False
    elif event.key == pygame.K_d:
        dark_mode()
    return True


def determine_drag_mode(selected_cell: CellState, drag_key: int) -> DragMode:
    if drag_key == pygame.K_SPACE:
        if selected_cell == CellState.FILLED:
            return DragMode.DESELECT
        elif selected_cell == CellState.CROSSED:
            return DragMode.OVERWRITE
        else:
            return DragMode.SELECT
    elif drag_key == pygame.K_x:
        if selected_cell == CellState.CROSSED:
            return DragMode.DESELECT
        elif selected_cell == CellState.FILLED:
            return DragMode.OVERWRITE
        else:
            return DragMode.SELECT
    else:
        return None


def handle_mouse_down(
    event: pygame.event, game: Nonogram, drag_state: DragState
) -> tuple[DragState, bool]:
    cell_x, cell_y = get_mouse_cell()
    if not (0 <= cell_x < game.width and 0 <= cell_y < game.height):
        drag_state.reset()
        return drag_state, False

    drag_state.dragging = True
    drag_state.key = pygame.K_SPACE if event.button == 1 else pygame.K_x
    game.save_drag_state()  # save state so that undo is possible
    drag_state.start = (cell_x, cell_y)
    drag_state.axis = None
    selected_cell = game.user_board[cell_y][cell_x]
    drag_state.mode = determine_drag_mode(selected_cell, drag_state.key)
    game.user_board[cell_y][cell_x], updated = update_cell_value(
        selected_cell, drag_state.key, drag_state.mode
    )
    if updated:
        game.check_correct()
    # last false means not in help mode
    return drag_state, False


def handle_key_down(
    event: pygame.event, game: Nonogram, drag_state: DragState
) -> tuple[DragState, bool]:
    if event.key == pygame.K_h:
        drag_state.reset()
        return drag_state, True

    elif event.key == pygame.K_r:
        game.restart()
    elif event.key == pygame.K_u:
        game.undo_drag()
    elif event.key == pygame.K_d:
        dark_mode()
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
            game.user_board[cell_y][cell_x], updated = update_cell_value(
                selected_cell, drag_state.key, drag_state.mode
            )
            if updated:
                game.check_correct()
    return drag_state, False


def handle_dragging(game, drag_state: DragState) -> DragState:
    cell_x, cell_y = get_mouse_cell()
    if 0 <= cell_x < game.width and 0 <= cell_y < game.height and drag_state.start:
        drag_start_x, drag_start_y = drag_state.start
        # determine axis of drag based on first movement
        if drag_state.axis is None and (
            cell_x != drag_start_x or cell_y != drag_start_y
        ):
            drag_state.axis = (
                DragAxis.ROW
                if abs(cell_x - drag_start_x) >= abs(cell_y - drag_start_y)
                else DragAxis.COL
            )

        updated = False
        if drag_state.axis == DragAxis.ROW and cell_y == drag_start_y:
            for x in range(min(drag_start_x, cell_x), max(drag_start_x, cell_x) + 1):
                current_val = game.user_board[drag_start_y][x]
                game.user_board[drag_start_y][x], updated = update_cell_value(
                    current_val, drag_state.key, drag_state.mode
                )
        elif drag_state.axis == DragAxis.COL and cell_x == drag_start_x:
            for y in range(min(drag_start_y, cell_y), max(drag_start_y, cell_y) + 1):
                current_val = game.user_board[y][drag_start_x]
                game.user_board[y][drag_start_x], updated = update_cell_value(
                    current_val, drag_state.key, drag_state.mode
                )

        if updated:
            game.check_correct()

    # Keep dragging if key or button is still pressed
    keys = pygame.key.get_pressed()
    mouse = pygame.mouse.get_pressed()
    key_or_mouse_held = (keys[drag_state.key] if drag_state.key else False) or any(
        mouse
    )
    if not (key_or_mouse_held):
        drag_state.reset()
    return drag_state
