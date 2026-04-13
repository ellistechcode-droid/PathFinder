import pygame

from grid import generate_solvable_grid, SAMPLE
from algorithms import (
    bfs,
    greedy,
    weighted_astar,
    dfs_samples,
    ucs_samples,
    ids_samples,
    astar_samples,
)
from visualizer import draw_grid, draw_sidebar, make_ui_rects, get_window_size


DEFAULT_ROWS = 20
DEFAULT_COLS = 20
DEFAULT_OBSTACLES = 30
DEFAULT_SAMPLE_COUNT = 3
MAX_SPEED = 20

ALGORITHMS = [
    ("DFS", dfs_samples),
    ("UCS", ucs_samples),
    ("IDS", ids_samples),
    ("A*", astar_samples),
    ("BFS", bfs),
    ("GREEDY", greedy),
    ("WEIGHTED A*", weighted_astar),
]

SAMPLE_ENABLED_ALGOS = {"DFS", "UCS", "IDS", "A*"}


def supports_samples(algorithm_name):
    return algorithm_name in SAMPLE_ENABLED_ALGOS


def clamp_int(value, low, high):
    return max(low, min(high, value))


def parse_rows(text):
    if not text.strip():
        return DEFAULT_ROWS
    return clamp_int(int(text), 2, 20)


def parse_cols(text):
    if not text.strip():
        return DEFAULT_COLS
    return clamp_int(int(text), 2, 20)


def parse_obstacles(text, rows, cols):
    max_obstacles = max(0, rows * cols - 2)
    if not text.strip():
        return min(DEFAULT_OBSTACLES, max_obstacles)
    return clamp_int(int(text), 0, max_obstacles)


def parse_samples(text, rows, cols, obstacles):
    max_samples = max(0, rows * cols - obstacles - 2)
    if not text.strip():
        return 0
    return clamp_int(int(text), 0, max_samples)


def count_samples_in_grid(grid):
    total = 0
    for row in grid:
        for tile in row:
            if tile == SAMPLE:
                total += 1
    return total


def run_selected_algorithm(grid, start, goal, algorithm_name):
    for name, func in ALGORITHMS:
        if name == algorithm_name:
            if name == "WEIGHTED A*":
                return func(grid, start, goal, weight=1.5)
            return func(grid, start, goal)
    return bfs(grid, start, goal)


def build_new_run(algorithm_name, rows_text, cols_text, obstacles_text, sample_input_text):
    rows = parse_rows(rows_text)
    cols = parse_cols(cols_text)
    obstacles = parse_obstacles(obstacles_text, rows, cols)

    requested_samples = parse_samples(sample_input_text, rows, cols, obstacles)
    actual_samples = requested_samples if supports_samples(algorithm_name) else 0

    grid, start, goal = generate_solvable_grid(rows, cols, obstacles, sample_count=actual_samples)
    path, explored, _, visit_count, heat_count = run_selected_algorithm(grid, start, goal, algorithm_name)

    return {
        "rows": rows,
        "cols": cols,
        "grid": grid,
        "start": start,
        "goal": goal,
        "path": path if path else [],
        "explored": explored if explored else [],
        "visit_count": visit_count if visit_count else {},
        "heat_count": heat_count if heat_count else {},
        "explored_set": set(),
        "path_set": set(),
        "collected_samples": set(),
        "active_path_cell": None,
        "step": 0,
        "phase": "explore",
        "goal_reached": False,
        "algorithm_name": algorithm_name,
        "visual_mode": "STANDARD",
        "show_visit_counts": False,
        "paused": False,
        "explore_speed": 10,
        "path_speed": 6,
        "obstacles": obstacles,
        "rows_input_text": str(rows),
        "cols_input_text": str(cols),
        "obstacles_input_text": str(obstacles),
        "sample_input_text": sample_input_text,
        "active_input": None,
        "sample_mode_enabled": supports_samples(algorithm_name),
        "generated_samples": count_samples_in_grid(grid),
        "meter_stage_text": "READY",
        "meter_percent": 0,
    }


def reset_animation(state):
    state["explored_set"].clear()
    state["path_set"].clear()
    state["collected_samples"].clear()
    state["active_path_cell"] = None
    state["step"] = 0
    state["phase"] = "explore"
    state["goal_reached"] = False
    state["paused"] = False


def cycle_algorithm(current):
    names = [name for name, _ in ALGORITHMS]
    idx = names.index(current)
    return names[(idx + 1) % len(names)]


def rerun_current_map(state):
    path, explored, _, visit_count, heat_count = run_selected_algorithm(
        state["grid"],
        state["start"],
        state["goal"],
        state["algorithm_name"]
    )
    state["path"] = path if path else []
    state["explored"] = explored if explored else []
    state["visit_count"] = visit_count if visit_count else {}
    state["heat_count"] = heat_count if heat_count else {}
    reset_animation(state)


def rebuild_window(state):
    width, height = get_window_size(state["rows"], state["cols"])
    return pygame.display.set_mode((width, height))


def get_steps_this_frame(current_speed, frame_counter):
    if current_speed <= 10:
        return 1 if frame_counter % max(1, 11 - current_speed) == 0 else 0
    return current_speed - 9


def update_meter(state):
    explored_len = max(1, len(state["explored"]))
    path_len = max(1, len(state["path"]))

    if state["goal_reached"]:
        state["meter_stage_text"] = "COMPLETE"
        state["meter_percent"] = 100
        return

    if state["paused"]:
        base_stage = "EXPLORE" if state["phase"] == "explore" else "PATH"
        state["meter_stage_text"] = f"PAUSED {base_stage}"
    else:
        state["meter_stage_text"] = "EXPLORING" if state["phase"] == "explore" else "FINAL PATH"

    if state["phase"] == "explore":
        state["meter_percent"] = (state["step"] / explored_len) * 100
    else:
        state["meter_percent"] = (state["step"] / path_len) * 100


def advance_animation(state, steps_this_frame):
    for _ in range(steps_this_frame):
        if state["phase"] == "explore":
            if state["step"] < len(state["explored"]):
                cell = state["explored"][state["step"]]
                state["explored_set"].add(cell)
                state["step"] += 1
            else:
                state["phase"] = "path"
                state["step"] = 0
                state["active_path_cell"] = None

        elif state["phase"] == "path":
            if state["step"] < len(state["path"]):
                cell = state["path"][state["step"]]
                is_final_path_cell = (state["step"] == len(state["path"]) - 1)

                state["active_path_cell"] = cell
                state["path_set"].add(cell)

                if state["grid"][cell[0]][cell[1]] == SAMPLE:
                    state["collected_samples"].add(cell)

                if cell == state["goal"] and is_final_path_cell:
                    state["goal_reached"] = True

                state["step"] += 1
            else:
                state["active_path_cell"] = None
                break


def main():
    pygame.init()

    state = build_new_run(
        "DFS",
        str(DEFAULT_ROWS),
        str(DEFAULT_COLS),
        str(DEFAULT_OBSTACLES),
        str(DEFAULT_SAMPLE_COUNT),
    )

    screen = rebuild_window(state)
    pygame.display.set_caption("Pathfinder")

    title_font = pygame.font.SysFont("arial", 22, bold=True)
    label_font = pygame.font.SysFont("arial", 18, bold=True)
    small_font = pygame.font.SysFont("arial", 16, bold=True)
    fonts = (title_font, label_font, small_font)

    clock = pygame.time.Clock()
    rects = make_ui_rects(state["rows"], state["cols"])

    frame_counter = 0
    running = True

    while running:
        clock.tick(60)
        frame_counter += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                state["active_input"] = None

                if rects["rows_input"].collidepoint(pos):
                    state["active_input"] = "rows"
                elif rects["cols_input"].collidepoint(pos):
                    state["active_input"] = "cols"
                elif rects["obstacles_input"].collidepoint(pos):
                    state["active_input"] = "obstacles"
                elif rects["sample_input"].collidepoint(pos) and state["sample_mode_enabled"]:
                    state["active_input"] = "samples"

                if rects["pause_button"].collidepoint(pos):
                    state["paused"] = not state["paused"]

                elif rects["faster_button"].collidepoint(pos):
                    if state["phase"] == "explore":
                        state["explore_speed"] = min(MAX_SPEED, state["explore_speed"] + 1)
                    else:
                        state["path_speed"] = min(MAX_SPEED, state["path_speed"] + 1)

                elif rects["slower_button"].collidepoint(pos):
                    if state["phase"] == "explore":
                        state["explore_speed"] = max(1, state["explore_speed"] - 1)
                    else:
                        state["path_speed"] = max(1, state["path_speed"] - 1)

                elif rects["algorithm_button"].collidepoint(pos):
                    next_algorithm = cycle_algorithm(state["algorithm_name"])
                    state = build_new_run(
                        next_algorithm,
                        state["rows_input_text"],
                        state["cols_input_text"],
                        state["obstacles_input_text"],
                        state["sample_input_text"],
                    )
                    screen = rebuild_window(state)
                    rects = make_ui_rects(state["rows"], state["cols"])

                elif rects["standard_button"].collidepoint(pos):
                    state["visual_mode"] = "STANDARD"

                elif rects["heatmap_button"].collidepoint(pos):
                    state["visual_mode"] = "HEAT MAP"

                elif rects["visitcount_button"].collidepoint(pos):
                    state["show_visit_counts"] = not state["show_visit_counts"]

                elif rects["generate_button"].collidepoint(pos):
                    state = build_new_run(
                        state["algorithm_name"],
                        state["rows_input_text"],
                        state["cols_input_text"],
                        state["obstacles_input_text"],
                        state["sample_input_text"],
                    )
                    screen = rebuild_window(state)
                    rects = make_ui_rects(state["rows"], state["cols"])

                elif rects["run_button"].collidepoint(pos):
                    rerun_current_map(state)

            elif event.type == pygame.KEYDOWN and state["active_input"] is not None:
                key_to_field = {
                    "rows": "rows_input_text",
                    "cols": "cols_input_text",
                    "obstacles": "obstacles_input_text",
                    "samples": "sample_input_text",
                }
                field = key_to_field[state["active_input"]]

                if event.key == pygame.K_BACKSPACE:
                    state[field] = state[field][:-1]
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    if not state[field]:
                        state[field] = "0"
                else:
                    if event.unicode.isdigit() and len(state[field]) < 3:
                        state[field] += event.unicode

        if not state["paused"]:
            current_speed = state["explore_speed"] if state["phase"] == "explore" else state["path_speed"]
            steps_this_frame = get_steps_this_frame(current_speed, frame_counter)
            advance_animation(state, steps_this_frame)

        update_meter(state)

        screen.fill((6, 8, 20))

        draw_grid(
            screen,
            state["grid"],
            state["explored_set"],
            state["path_set"],
            goal_reached=state["goal_reached"],
            active_path_cell=state["active_path_cell"],
            visual_mode=state["visual_mode"],
            heat_count=state["heat_count"],
            show_visit_counts=state["show_visit_counts"],
            small_font=small_font,
            collected_samples=state["collected_samples"],
        )

        draw_sidebar(screen, state["rows"], state["cols"], state, fonts, rects)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()