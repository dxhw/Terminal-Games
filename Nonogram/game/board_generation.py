import random


def generate_row(length: int, density: int) -> list[int]:
    row = []
    filled_prob = (density / 100) * (2 / 3)

    max_run = max(1, int(length * 0.5))
    one_run_weights = [i for i in range(1, max_run + 1)]
    zero_run_weights = [
        max(1, max_run - i + 1) for i in range(1, max(2, max_run // 2 + 1))
    ]

    # weight to have longer runs because having lots of 1s in a row is not fun
    while len(row) < length:
        is_one_run = random.random() < filled_prob
        if is_one_run:
            run_length = random.choices(range(1, max_run + 1), weights=one_run_weights)[
                0
            ]
        else:
            run_length = random.choices(
                range(1, max_run // 2 + 1), weights=zero_run_weights
            )[0]
        run_length = min(run_length, length - len(row))
        row.extend([1 if is_one_run else 0] * run_length)

    return row


def apply_symmetry_noise(row: list[int], noise_level: float):
    # Flip a percentage of bits in the row
    noisy_row = row.copy()
    for i in range(len(noisy_row)):
        if random.random() < noise_level:
            noisy_row[i] ^= 1  # Flip 0 <-> 1
    return noisy_row


def generate_nonogram_board(
    width: int, height: int, density: int, symmetry_strength=1.0, symmetry_noise=0.0
) -> list[list[int]]:
    board = [[0 for _ in range(width)] for _ in range(height)]

    symmetry_type = random.choices(
        ["none", "horizontal", "vertical", "rotational"], weights=[0.05, 0.3, 0.3, 0.35]
    )[0]

    for y in range(height):
        if symmetry_type in ["vertical", "rotational"]:
            sym_y = height - 1 - y
        else:
            sym_y = y

        if y > sym_y:
            continue  # already filled from symmetry

        row = generate_row(width, density)
        board[y] = row

        # Determine if we apply symmetry
        if symmetry_type == "none" or sym_y == y:
            continue

        if random.random() < symmetry_strength:
            mirrored = row.copy()
            if symmetry_type == "horizontal":
                mirrored = row[::-1]
            elif symmetry_type == "vertical":
                mirrored = row.copy()
            elif symmetry_type == "rotational":
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
