import pygame
from game.constants import MARGIN, CELL_SIZE


def get_mouse_cell() -> tuple[int, int]:
    mouse_x, mouse_y = pygame.mouse.get_pos()
    cell_x = (mouse_x - (MARGIN + 120)) // CELL_SIZE
    cell_y = (mouse_y - (MARGIN + 100)) // CELL_SIZE
    return cell_x, cell_y
