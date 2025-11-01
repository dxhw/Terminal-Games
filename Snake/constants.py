# Colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (220, 0, 0)
WHITE = (255, 255, 255)
GREY = (40, 40, 40)
PURPLE = (138,43,226)
BLUE = (0,191,255)

# Directions
RIGHT = (1, 0)
LEFT = (-1, 0)
UP = (0, 1)
DOWN = (0, -1)

def opposite_dir(dir):
    if dir == RIGHT:
        return LEFT
    elif dir == LEFT:
        return RIGHT
    elif dir == UP:
        return DOWN
    elif dir == DOWN:
        return UP
