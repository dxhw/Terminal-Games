from enum import Enum, auto


class DragState:
    def __init__(self):
        self.dragging: bool = False  # True or False (is dragging on)
        self.key = None  # pygame.K_SPACE or pygame.K_x
        self.start: tuple[int, int] = None  # (x, y)
        self.axis: DragAxis = None
        self.mode: DragMode = None

    def reset(self):
        self.dragging = False
        self.key = None
        self.start = None
        self.axis = None
        self.mode = None


class CellState(Enum):
    EMPTY = auto()
    FILLED = auto()
    CROSSED = auto()


class DragMode(Enum):
    SELECT = auto()
    DESELECT = auto()
    OVERWRITE = auto()


class DragAxis(Enum):
    ROW = auto()
    COL = auto()


# Constants
DEFAULT_WIDTH = 20  # Default board width
DEFAULT_HEIGHT = 20  # Default board height
DEFAULT_SCALE = 25  # Default cell size
DEFAULT_SIZE = DEFAULT_WIDTH
MARGIN = 50  # Margin around the grid for clues
DEFAULT_DENSITY = 40

# RGB Color definitions
BORDER_COLOR = (50, 50, 50)
RED = (255, 0, 0)

# Light mode colors
L_WHITE = (255, 255, 255)
L_BLACK = (0, 0, 0)
L_BACKGROUND_COLOR = (200, 200, 200)
L_BLUE = (0, 0, 255)
L_YELLOW = (255, 255, 0)

# Dark mode colors
D_WHITE = (0, 0, 0)
D_BLACK = (255, 255, 255)
D_BACKGROUND_COLOR = (40, 40, 40)
D_BLUE = (144, 213, 255)
D_YELLOW = (245, 164, 0)
