import os
import random
from datetime import datetime
from collections import deque

EMPTY = "."
OBSTACLE = "#"
START = "S"
GOAL = "G"
SAMPLE = "P"
VISITED_SPECIAL = "X"


def in_bounds(rows, cols, r, c):
    return 0 <= r < rows and 0 <= c < cols


def get_neighbors(rows, cols, r, c):
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    neighbors = []

    for dr, dc in directions:
        nr, nc = r + dr, c + dc
        if in_bounds(rows, cols, nr, nc):
            neighbors.append((nr, nc))

    return neighbors


def reachable_from(grid, start):
    rows = len(grid)
    cols = len(grid[0])

    queue = deque([start])
    visited = {start}

    while queue:
        current = queue.popleft()

        for nr, nc in get_neighbors(rows, cols, current[0], current[1]):
            if (nr, nc) not in visited and grid[nr][nc] != OBSTACLE:
                visited.add((nr, nc))
                queue.append((nr, nc))

    return visited


def basic_reachable(grid, start, goal):
    return goal in reachable_from(grid, start)


def samples_safely_reachable(grid, start, goal, sample_positions):
    reachable_from_start = reachable_from(grid, start)
    reachable_from_goal = reachable_from(grid, goal)

    if goal not in reachable_from_start:
        return False

    for sample in sample_positions:
        if sample not in reachable_from_start:
            return False
        if sample not in reachable_from_goal:
            return False

    return True


def generate_random_positions(rows, cols):
    start = (random.randint(0, rows - 1), random.randint(0, cols - 1))
    goal = start

    while goal == start:
        goal = (random.randint(0, rows - 1), random.randint(0, cols - 1))

    return start, goal


def generate_solvable_grid(rows, cols, obstacle_count, sample_count=0):
    while True:
        grid = [[EMPTY for _ in range(cols)] for _ in range(rows)]
        start, goal = generate_random_positions(rows, cols)

        grid[start[0]][start[1]] = START
        grid[goal[0]][goal[1]] = GOAL

        available_cells = [
            (r, c)
            for r in range(rows)
            for c in range(cols)
            if (r, c) != start and (r, c) != goal
        ]

        max_obstacles = len(available_cells)
        if obstacle_count > max_obstacles:
            raise ValueError(f"Too many obstacles. Maximum is {max_obstacles}.")

        obstacle_positions = random.sample(available_cells, obstacle_count)
        for r, c in obstacle_positions:
            grid[r][c] = OBSTACLE

        remaining_cells = [
            (r, c)
            for r in range(rows)
            for c in range(cols)
            if grid[r][c] == EMPTY
        ]

        if sample_count > len(remaining_cells):
            raise ValueError(
                f"Too many samples. Maximum after obstacle placement is {len(remaining_cells)}."
            )

        sample_positions = random.sample(remaining_cells, sample_count)
        for r, c in sample_positions:
            grid[r][c] = SAMPLE

        if sample_count == 0:
            if basic_reachable(grid, start, goal):
                return grid, start, goal
        else:
            if samples_safely_reachable(grid, start, goal, sample_positions):
                return grid, start, goal


def generate_filename(rows, cols, obstacles, samples=0, algo="bfs"):
    os.makedirs("maps", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"maps/map_{rows}x{cols}_obs{obstacles}_samp{samples}_{algo}_{timestamp}.txt"


def save_grid(grid, filename):
    os.makedirs("maps", exist_ok=True)

    with open(filename, "w", encoding="utf-8") as file:
        rows = len(grid)
        cols = len(grid[0])
        file.write(f"{rows} {cols}\n")
        for row in grid:
            file.write(" ".join(row) + "\n")


def print_grid(grid):
    for row in grid:
        print(" ".join(row))