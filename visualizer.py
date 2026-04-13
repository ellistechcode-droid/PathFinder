import pygame
from grid import SAMPLE

CELL_SIZE = 30
SIDEBAR_WIDTH = 380

TOP_BANNER_HEIGHT = 70
TOP_MARGIN = 18
GRID_TOP_OFFSET = 110
BOTTOM_MARGIN = 20
BOTTOM_PANEL_HEIGHT = 190
BOTTOM_PANEL_GAP = 14

WINDOW_BG = (6, 8, 20)
GRID_BG = (8, 10, 24)
PANEL_BG = (10, 10, 28)

NEON_PINK = (255, 70, 200)
NEON_CYAN = (80, 220, 255)
TEXT_WHITE = (235, 240, 255)
TEXT_GRAY = (120, 128, 150)

EMPTY_COLOR = (16, 18, 30)
OBSTACLE_COLOR = (70, 70, 90)
START_COLOR = (0, 255, 120)
GOAL_COLOR = (255, 60, 60)
GOAL_REACHED_COLOR = (255, 130, 130)
SAMPLE_COLOR = (255, 150, 40)
COLLECTED_SAMPLE_COLOR = (0, 200, 255)

EXPLORED_COLOR = (50, 100, 255)
PATH_COLOR = (255, 220, 0)
ACTIVE_PATH_COLOR = (255, 255, 140)

GRID_LINE = (50, 60, 90)
BUTTON_BG = (22, 25, 44)
DISABLED_BUTTON_BG = (26, 28, 38)
INPUT_BG = (14, 18, 34)
INPUT_DISABLED_BG = (24, 26, 34)


def draw_glow_rect(surface, rect, color, border_radius=10, thickness=2):
    glow = pygame.Surface((rect.width + 16, rect.height + 16), pygame.SRCALPHA)
    pygame.draw.rect(
        glow,
        (*color, 55),
        (8, 8, rect.width, rect.height),
        border_radius=border_radius
    )
    surface.blit(glow, (rect.x - 8, rect.y - 8))
    pygame.draw.rect(surface, color, rect, thickness, border_radius=border_radius)


def draw_text(surface, text, font, color, x, y, center=False):
    rendered = font.render(text, True, color)
    rect = rendered.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    surface.blit(rendered, rect)


def get_window_size(rows, cols):
    grid_width = cols * CELL_SIZE
    grid_height = rows * CELL_SIZE
    width = grid_width + SIDEBAR_WIDTH
    min_height = GRID_TOP_OFFSET + grid_height + BOTTOM_PANEL_GAP + BOTTOM_PANEL_HEIGHT + BOTTOM_MARGIN
    height = max(min_height, 980)
    return width, height


def draw_bullseye(screen, row, col):
    cx = col * CELL_SIZE + CELL_SIZE // 2
    cy = GRID_TOP_OFFSET + row * CELL_SIZE + CELL_SIZE // 2

    pygame.draw.circle(screen, TEXT_WHITE, (cx, cy), CELL_SIZE // 2 - 2, 3)
    pygame.draw.circle(screen, TEXT_WHITE, (cx, cy), CELL_SIZE // 4, 3)
    pygame.draw.circle(screen, TEXT_WHITE, (cx, cy), CELL_SIZE // 10)

    pygame.draw.line(screen, TEXT_WHITE, (cx - 7, cy), (cx + 7, cy), 2)
    pygame.draw.line(screen, TEXT_WHITE, (cx, cy - 7), (cx, cy + 7), 2)


def heat_map_color(count):
    if count <= 0:
        return (45, 48, 85)
    elif count == 1:
        return (55, 45, 105)
    elif count == 2:
        return (75, 55, 130)
    elif count == 3:
        return (100, 68, 155)
    elif count == 4:
        return (130, 82, 180)
    elif count == 5:
        return (165, 98, 200)
    elif count == 6:
        return (205, 120, 218)
    else:
        return (245, 170, 230)


def draw_button(screen, rect, text, font, accent_color, active=False, enabled=True):
    if enabled:
        fill = BUTTON_BG if not active else (40, 48, 80)
        text_color = TEXT_WHITE
        border_color = accent_color
    else:
        fill = DISABLED_BUTTON_BG
        text_color = TEXT_GRAY
        border_color = (80, 84, 100)

    pygame.draw.rect(screen, fill, rect, border_radius=10)
    draw_glow_rect(screen, rect, border_color, border_radius=10, thickness=2)
    draw_text(screen, text, font, text_color, rect.centerx, rect.centery, center=True)


def draw_input_box(screen, rect, text, font, enabled=True, active=False):
    fill = INPUT_BG if enabled else INPUT_DISABLED_BG
    border = NEON_CYAN if active and enabled else (NEON_PINK if enabled else (80, 84, 100))
    text_color = TEXT_WHITE if enabled else TEXT_GRAY

    pygame.draw.rect(screen, fill, rect, border_radius=8)
    draw_glow_rect(screen, rect, border, border_radius=8, thickness=2)

    display_text = text if text else "0"
    draw_text(screen, display_text, font, text_color, rect.x + 10, rect.y + 8)


def draw_progress_meter(screen, rect, stage_text, percent, font):
    pygame.draw.rect(screen, BUTTON_BG, rect, border_radius=10)
    draw_glow_rect(screen, rect, NEON_CYAN, border_radius=10, thickness=2)

    label = f"STAGE: {stage_text}  |  {int(percent)}%"
    draw_text(screen, label, font, TEXT_WHITE, rect.x + 12, rect.y + 8)

    bar_bg = pygame.Rect(rect.x + 12, rect.y + 34, rect.width - 24, 12)
    pygame.draw.rect(screen, (25, 30, 46), bar_bg, border_radius=6)

    fill_width = int((bar_bg.width * max(0, min(100, percent))) / 100)
    bar_fill = pygame.Rect(bar_bg.x, bar_bg.y, fill_width, bar_bg.height)
    pygame.draw.rect(screen, NEON_CYAN, bar_fill, border_radius=6)


def make_ui_rects(rows, cols):
    grid_width = cols * CELL_SIZE
    grid_height = rows * CELL_SIZE
    panel_x = grid_width + 10
    panel_width = SIDEBAR_WIDTH - 20

    bottom_y = GRID_TOP_OFFSET + grid_height + BOTTOM_PANEL_GAP
    key_width = 400
    gap = 12
    viz_x = key_width + gap
    viz_width = grid_width + panel_width + 10 - viz_x

    right_x = panel_x + 190
    input_w = 90
    label_y0 = 180
    row_gap = 52

    return {
        "title_box": pygame.Rect(
            8,
            TOP_MARGIN,
            grid_width + SIDEBAR_WIDTH - 16,
            TOP_BANNER_HEIGHT - 10,
        ),

        "system_box": pygame.Rect(panel_x, 110, panel_width, 610),

        "key_box": pygame.Rect(8, bottom_y, key_width, BOTTOM_PANEL_HEIGHT),
        "viz_box": pygame.Rect(viz_x, bottom_y, viz_width, BOTTOM_PANEL_HEIGHT),

        "rows_input": pygame.Rect(right_x, label_y0 - 8, input_w, 34),
        "cols_input": pygame.Rect(right_x, label_y0 + row_gap - 8, input_w, 34),
        "obstacles_input": pygame.Rect(right_x, label_y0 + row_gap * 2 - 8, input_w, 34),
        "sample_input": pygame.Rect(right_x, label_y0 + row_gap * 3 - 8, input_w, 34),

        "algorithm_button": pygame.Rect(panel_x + 150, 420, 155, 34),

        "generate_button": pygame.Rect(panel_x + 20, 555, 130, 40),
        "run_button": pygame.Rect(panel_x + 175, 555, 130, 40),

        "meter_box": pygame.Rect(panel_x + 20, 615, 285, 58),

        "pause_button": pygame.Rect(panel_x + 20, 685, 82, 32),
        "slower_button": pygame.Rect(panel_x + 112, 685, 88, 32),
        "faster_button": pygame.Rect(panel_x + 210, 685, 95, 32),

        "standard_button": pygame.Rect(viz_x + 28, bottom_y + 58, 190, 36),
        "heatmap_button": pygame.Rect(viz_x + 248, bottom_y + 58, 190, 36),
        "visitcount_button": pygame.Rect(viz_x + 28, bottom_y + 108, 410, 36),
    }


def draw_grid(
    screen,
    grid,
    explored_set,
    path_set,
    goal_reached=False,
    active_path_cell=None,
    visual_mode="STANDARD",
    heat_count=None,
    show_visit_counts=False,
    small_font=None,
    collected_samples=None,
):
    rows = len(grid)
    cols = len(grid[0])
    collected_samples = collected_samples or set()

    grid_rect = pygame.Rect(0, GRID_TOP_OFFSET, cols * CELL_SIZE, rows * CELL_SIZE)
    pygame.draw.rect(screen, GRID_BG, grid_rect)
    draw_glow_rect(screen, grid_rect, NEON_CYAN, border_radius=0, thickness=2)

    for r in range(rows):
        for c in range(cols):
            tile = grid[r][c]
            pos = (r, c)

            rect = pygame.Rect(
                c * CELL_SIZE,
                GRID_TOP_OFFSET + r * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE,
            )

            color = EMPTY_COLOR

            if tile == "#":
                color = OBSTACLE_COLOR
            elif tile == "S":
                color = START_COLOR
            elif tile == "G":
                color = GOAL_REACHED_COLOR if goal_reached else GOAL_COLOR
            elif tile == SAMPLE:
                color = SAMPLE_COLOR

            if pos in explored_set and tile not in {"#", "S", "G"}:
                if visual_mode == "HEAT MAP" and heat_count:
                    color = heat_map_color(heat_count.get(pos, 0))
                else:
                    color = EXPLORED_COLOR

            if pos in path_set and tile not in {"#", "S", "G"}:
                color = PATH_COLOR

            if pos == active_path_cell and tile not in {"#", "S", "G"}:
                color = ACTIVE_PATH_COLOR

            if tile == SAMPLE and pos in collected_samples:
                color = COLLECTED_SAMPLE_COLOR

            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, GRID_LINE, rect, 1)

            if (
                visual_mode == "HEAT MAP"
                and show_visit_counts
                and heat_count
                and pos in explored_set
                and tile not in {"#", "S", "G"}
            ):
                count = heat_count.get(pos, 0)
                if count >= 2 and small_font is not None:
                    label = "9+" if count > 9 else str(count)
                    text_color = (0, 0, 0) if count >= 6 else TEXT_WHITE
                    draw_text(
                        screen,
                        label,
                        small_font,
                        text_color,
                        rect.centerx,
                        rect.centery,
                        center=True,
                    )

    if goal_reached:
        for r in range(rows):
            for c in range(cols):
                if grid[r][c] == "G":
                    draw_bullseye(screen, r, c)
                    return


def draw_sidebar(screen, rows, cols, app_state, fonts, rects):
    title_font, label_font, small_font = fonts
    grid_width = cols * CELL_SIZE

    panel_rect = pygame.Rect(grid_width, 0, SIDEBAR_WIDTH, screen.get_height())
    pygame.draw.rect(screen, PANEL_BG, panel_rect)

    draw_glow_rect(screen, rects["title_box"], NEON_PINK, border_radius=12, thickness=2)
    draw_text(
        screen,
        "PATHFINDER SYSTEM",
        title_font,
        NEON_CYAN,
        rects["title_box"].centerx,
        rects["title_box"].centery,
        center=True
    )

    draw_glow_rect(screen, rects["system_box"], NEON_PINK, border_radius=12, thickness=2)
    draw_glow_rect(screen, rects["viz_box"], NEON_PINK, border_radius=12, thickness=2)
    draw_glow_rect(screen, rects["key_box"], NEON_PINK, border_radius=12, thickness=2)

    # Right-side system panel
    x = rects["system_box"].x + 18
    y = rects["system_box"].y + 18

    draw_text(screen, "PATHFINDER SYSTEM", label_font, NEON_PINK, x, y)
    y += 42

    draw_text(screen, "ROWS:", small_font, TEXT_WHITE, x, y)
    draw_input_box(
        screen, rects["rows_input"], app_state["rows_input_text"], small_font,
        enabled=True, active=(app_state["active_input"] == "rows")
    )
    y += 52

    draw_text(screen, "COLUMNS:", small_font, TEXT_WHITE, x, y)
    draw_input_box(
        screen, rects["cols_input"], app_state["cols_input_text"], small_font,
        enabled=True, active=(app_state["active_input"] == "cols")
    )
    y += 52

    draw_text(screen, "OBSTACLES:", small_font, TEXT_WHITE, x, y)
    draw_input_box(
        screen, rects["obstacles_input"], app_state["obstacles_input_text"], small_font,
        enabled=True, active=(app_state["active_input"] == "obstacles")
    )
    y += 52

    draw_text(screen, "SAMPLE COUNT:", small_font, TEXT_WHITE, x, y)
    draw_input_box(
        screen,
        rects["sample_input"],
        app_state["sample_input_text"],
        small_font,
        enabled=app_state["sample_mode_enabled"],
        active=(app_state["active_input"] == "samples"),
    )
    y += 56

    draw_text(screen, f"SAMPLES ON MAP: {app_state['generated_samples']}", small_font, TEXT_WHITE, x, y)
    y += 38

    draw_text(screen, "ALGORITHM:", small_font, TEXT_WHITE, x, y)
    draw_button(
        screen,
        rects["algorithm_button"],
        app_state["algorithm_name"],
        small_font,
        NEON_PINK
    )
    y += 52

    draw_text(screen, f"EXPLORE SPEED: {app_state['explore_speed']}x", small_font, TEXT_WHITE, x, y)
    y += 24
    draw_text(screen, f"PATH SPEED: {app_state['path_speed']}x", small_font, TEXT_WHITE, x, y)

    draw_button(screen, rects["generate_button"], "GENERATE MAP", small_font, NEON_CYAN)
    draw_button(screen, rects["run_button"], "RUN ALGORITHM", small_font, NEON_PINK)

    draw_progress_meter(
        screen,
        rects["meter_box"],
        app_state["meter_stage_text"],
        app_state["meter_percent"],
        small_font,
    )

    draw_button(screen, rects["pause_button"], "PAUSE", small_font, NEON_PINK)
    draw_button(screen, rects["slower_button"], "SLOWER", small_font, NEON_CYAN)
    draw_button(screen, rects["faster_button"], "FASTER", small_font, NEON_CYAN)

    # Bottom-left key box
    draw_text(
        screen,
        "KEY",
        label_font,
        NEON_PINK,
        rects["key_box"].x + 18,
        rects["key_box"].y + 16
    )

    legend_left = [
        ("START", START_COLOR),
        ("GOAL", GOAL_COLOR),
        ("SAMPLE", SAMPLE_COLOR),
        ("COLLECTED", COLLECTED_SAMPLE_COLOR),
    ]
    legend_right = [
        ("OBSTACLE", OBSTACLE_COLOR),
        ("EXPLORED", EXPLORED_COLOR),
        ("PATH", PATH_COLOR),
    ]

    left_x = rects["key_box"].x + 20
    right_x = rects["key_box"].x + 190
    start_y = rects["key_box"].y + 52
    row_gap = 30

    for i, (label, color) in enumerate(legend_left):
        ly = start_y + i * row_gap
        swatch = pygame.Rect(left_x, ly, 18, 18)
        pygame.draw.rect(screen, color, swatch)
        pygame.draw.rect(screen, TEXT_WHITE, swatch, 1)
        draw_text(screen, label, small_font, TEXT_WHITE, swatch.right + 10, ly - 1)

    for i, (label, color) in enumerate(legend_right):
        ly = start_y + i * row_gap
        swatch = pygame.Rect(right_x, ly, 18, 18)
        pygame.draw.rect(screen, color, swatch)
        pygame.draw.rect(screen, TEXT_WHITE, swatch, 1)
        draw_text(screen, label, small_font, TEXT_WHITE, swatch.right + 10, ly - 1)

    # Bottom-right visualization box
    draw_text(
        screen,
        "VISUALIZATION",
        label_font,
        NEON_PINK,
        rects["viz_box"].x + 18,
        rects["viz_box"].y + 16
    )

    draw_text(
        screen,
        "MODE:",
        small_font,
        TEXT_WHITE,
        rects["viz_box"].x + 18,
        rects["viz_box"].y + 38
    )

    draw_button(
        screen,
        rects["standard_button"],
        "STANDARD",
        small_font,
        NEON_CYAN,
        active=(app_state["visual_mode"] == "STANDARD")
    )
    draw_button(
        screen,
        rects["heatmap_button"],
        "HEAT MAP",
        small_font,
        NEON_PINK,
        active=(app_state["visual_mode"] == "HEAT MAP")
    )

    visit_text = "VISIT COUNT: ON" if app_state["show_visit_counts"] else "VISIT COUNT: OFF"
    draw_button(
        screen,
        rects["visitcount_button"],
        visit_text,
        small_font,
        NEON_CYAN if app_state["show_visit_counts"] else NEON_PINK,
        active=app_state["show_visit_counts"]
    )