from constants import *

def signof(x):
    if x >= 0: # need to also go on equal so that the direction is not (0, 0)
        return 1
    else:
        return -1

def ai_headed_towards_food(current_dir, x_from_food, y_from_food):
    dx, dy = current_dir
    return dx * x_from_food + dy * y_from_food > 0

# returns the order of directions that would be most beneficial for the snake to move in
# prioritizes keeping the same direction
def naive_direction_chooser(current_dir, head_pos, food_pos):
    x_from_food = food_pos[0] - head_pos[0]
    y_from_food = food_pos[1] - head_pos[1]
    if ai_headed_towards_food(current_dir, x_from_food, y_from_food):
        if current_dir[0] != 0:
            return [current_dir, (0, signof(y_from_food)), (0, -signof(y_from_food))]
        return [current_dir, (signof(x_from_food), 0), (-signof(x_from_food), 0)]
    if abs(x_from_food) > abs(y_from_food):
        return [(signof(x_from_food), 0), (0, signof(y_from_food)), (0, -signof(y_from_food)), (-signof(x_from_food), 0)]
    return [(0, signof(y_from_food)), (signof(x_from_food), 0), (-signof(x_from_food), 0), (0, -signof(y_from_food))]

def check_if_will_kill(move_dir, ai_snake, snake, grid_width, grid_height):
    x, y = ai_snake[0]
    x, y = x + move_dir[0], y + move_dir[1]
    return (
        x <= 0 or x >= grid_width - 1 or
        y <= 0 or y >= grid_height - 1 or
        (x, y) in ai_snake or (x, y) in snake 
    )

def has_future_escape(move_dir, ai_snake, snake, grid_width, grid_height):
    """Simulate moving one step and check if any future move will be safe."""
    new_head = (ai_snake[0][0] + move_dir[0], ai_snake[0][1] + move_dir[1])
    new_snake = [new_head] + ai_snake[:-1]  # simulate move without growing
    possible_dirs = [(1,0), (-1,0), (0,1), (0,-1)]
    for nd in possible_dirs:
        x, y = new_head[0] + nd[0], new_head[1] + nd[1]
        if not (
            x <= 0 or x >= grid_width - 1 or
            y <= 0 or y >= grid_height - 1 or
            (x, y) in new_snake or (x, y) in snake
        ):
            return True
    return False

def simple_ai_direction_chooser(current_dir, ai_snake, snake, food_pos, grid_width, grid_height):
    dirs = naive_direction_chooser(current_dir, ai_snake[0], food_pos)
    # Prefer a direction that is immediately safe and has a future escape
    for d in dirs:
        if not check_if_will_kill(d, ai_snake, snake, grid_width, grid_height) and has_future_escape(d, ai_snake, snake, grid_width, grid_height):
            return d

    # If none have a guaranteed escape, pick any immediately safe one
    for d in dirs:
        if not check_if_will_kill(d, ai_snake, snake, grid_width, grid_height):
            return d

    # If no move is safe, accept fate
    return dirs[0]