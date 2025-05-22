import pygame
import copy
from game.constants import CellState
from game.board_generation import generate_nonogram_board


class Nonogram:
    """
    Class representing the Nonogram game board and logic.

    Attributes:
        width (int): Width of the board in tiles.
        height (int): Height of the board in tiles.
        density (int): Approximate density of tiles that should be filled
        solution (list[list[int]]): Randomly generated correct tiles (1 for filled, 0 for empty).
        user_board (list[list[CellState]]): Player's input (CellState.FILLED for filled, CellState.CROSSED for decoy, CellState.EMPTY for empty).
        correct_total (int): Total number of correct tiles in the solution.
        correct_count (int): Number of correct tiles marked by the user.
    """

    def __init__(self, width: int, height: int, density: int):
        self.width = width
        self.height = height
        self.density = density
        self.solution = generate_nonogram_board(
            width=width,
            height=height,
            density=density,
            symmetry_strength=0.8,
            symmetry_noise=0.05,
        )
        self.user_board = [
            [CellState.EMPTY for _ in range(width)] for _ in range(height)
        ]
        self.correct_total = sum(sum(row) for row in self.solution)
        self.correct_count = 0
        self.drag_history = []  # Stack to track drag history

    def restart(self):
        self.solution = generate_nonogram_board(
            width=self.width,
            height=self.height,
            density=self.density,
            symmetry_strength=0.8,
            symmetry_noise=0.05,
        )
        self.user_board = [
            [CellState.EMPTY for _ in range(self.width)] for _ in range(self.height)
        ]
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
        self.user_board = [
            [CellState.EMPTY for _ in range(self.width)] for _ in range(self.height)
        ]
        self.correct_count = 0
        pygame.display.set_caption("Nonogram")

    def check_correct(self):
        """Updates the number of filled tiles, auto-flags completed rows/columns, and checks win condition."""

        def extract_clues(line: list[CellState]):
            """Extract the clues that the users selections would match"""
            groups = "".join(
                ["1" if cell == CellState.FILLED else "0" for cell in line]
            ).split("0")
            clues = [len(group) for group in groups if group]
            return clues if clues else [0]

        def autofill_line(line_idx: int, is_row=True) -> bool:
            """Flag remaining tiles in column/row with completed clues"""
            # it's super lame to have the board autofill with x's for a 0 row/column, so ignore [0]
            if is_row:
                line = [self.user_board[line_idx][x] for x in range(self.width)]
                clues_match: bool = (
                    extract_clues(line) == self.get_row_clues()[line_idx]
                )
                if clues_match and extract_clues(line) != [0]:
                    for x in range(self.width):
                        if self.user_board[line_idx][x] == CellState.EMPTY:
                            self.user_board[line_idx][x] = CellState.CROSSED
                return clues_match
            else:
                line = [self.user_board[y][line_idx] for y in range(self.height)]
                clues_match: bool = (
                    extract_clues(line) == self.get_col_clues()[line_idx]
                )
                if clues_match and extract_clues(line) != [0]:
                    for y in range(self.height):
                        if self.user_board[y][line_idx] == CellState.EMPTY:
                            self.user_board[y][line_idx] = CellState.CROSSED
                return clues_match

        # Count correct selections
        selected = sum(
            cell == CellState.FILLED for row in self.user_board for cell in row
        )
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

    def get_row_clues(self) -> list[list[int]]:
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

    def get_col_clues(self) -> list[list[int]]:
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
