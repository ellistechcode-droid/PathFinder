import heapq
from collections import deque
from grid import OBSTACLE, SAMPLE


def get_neighbors(grid, position):
    rows = len(grid)
    cols = len(grid[0])
    r, c = position

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    neighbors = []

    for dr, dc in directions:
        nr, nc = r + dr, c + dc
        if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != OBSTACLE:
            neighbors.append((nr, nc))

    return neighbors


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def reconstruct_path(parent, start_state, goal_state):
    if goal_state not in parent and goal_state != start_state:
        return None

    path = []
    current = goal_state

    while current != start_state:
        path.append(current)
        current = parent[current]

    path.append(start_state)
    path.reverse()
    return path


def extract_positions(state_path):
    if not state_path:
        return None
    return [(state[0], state[1]) for state in state_path]


def get_sample_positions(grid):
    samples = set()
    for r, row in enumerate(grid):
        for c, tile in enumerate(row):
            if tile == SAMPLE:
                samples.add((r, c))
    return samples


def sample_successors(grid, state):
    r, c, remaining = state
    successors = []

    # Sample action: stay in place, remove sample from remaining
    if (r, c) in remaining:
        new_remaining = frozenset(pos for pos in remaining if pos != (r, c))
        successors.append((r, c, new_remaining))

    # Movement actions
    for nr, nc in get_neighbors(grid, (r, c)):
        successors.append((nr, nc, remaining))

    return successors


def sample_goal_test(state, goal):
    r, c, remaining = state
    return (r, c) == goal and len(remaining) == 0


def sample_heuristic(state, goal):
    r, c, remaining = state
    current = (r, c)

    if not remaining:
        return manhattan(current, goal)

    nearest_sample = min(manhattan(current, sample) for sample in remaining)
    nearest_sample_to_goal = min(manhattan(sample, goal) for sample in remaining)

    # Admissible lower bound:
    # must at least reach some remaining sample, sample all remaining locations,
    # and eventually head toward the goal.
    return nearest_sample + len(remaining) + nearest_sample_to_goal


def bfs(grid, start, goal):
    queue = deque([start])
    visited = {start}
    parent = {}
    explored_order = []
    nodes_expanded = 0

    visit_count = {}
    heat_count = {start: 1}

    while queue:
        current = queue.popleft()
        explored_order.append(current)
        nodes_expanded += 1
        visit_count[current] = visit_count.get(current, 0) + 1

        if current == goal:
            path = reconstruct_path(parent, start, goal)
            return path, explored_order, nodes_expanded, visit_count, heat_count

        for neighbor in get_neighbors(grid, current):
            heat_count[neighbor] = heat_count.get(neighbor, 0) + 1

            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = current
                queue.append(neighbor)

    return None, explored_order, nodes_expanded, visit_count, heat_count


def greedy(grid, start, goal):
    frontier = []
    heapq.heappush(frontier, (manhattan(start, goal), start))

    parent = {}
    visited = set()
    explored_order = []
    nodes_expanded = 0
    visit_count = {}
    heat_count = {start: 1}

    while frontier:
        _, current = heapq.heappop(frontier)

        if current in visited:
            continue

        visited.add(current)
        explored_order.append(current)
        nodes_expanded += 1
        visit_count[current] = visit_count.get(current, 0) + 1

        if current == goal:
            path = reconstruct_path(parent, start, goal)
            return path, explored_order, nodes_expanded, visit_count, heat_count

        for neighbor in get_neighbors(grid, current):
            heat_count[neighbor] = heat_count.get(neighbor, 0) + 1

            if neighbor not in visited:
                if neighbor not in parent:
                    parent[neighbor] = current
                priority = manhattan(neighbor, goal)
                heapq.heappush(frontier, (priority, neighbor))

    return None, explored_order, nodes_expanded, visit_count, heat_count


def weighted_astar(grid, start, goal, weight=1.5):
    frontier = []
    heapq.heappush(frontier, (weight * manhattan(start, goal), 0, start))

    parent = {}
    cost_so_far = {start: 0}
    explored_order = []
    nodes_expanded = 0
    visit_count = {}
    heat_count = {start: 1}
    closed = set()

    while frontier:
        _, current_cost, current = heapq.heappop(frontier)

        if current in closed:
            continue

        closed.add(current)
        explored_order.append(current)
        nodes_expanded += 1
        visit_count[current] = visit_count.get(current, 0) + 1

        if current == goal:
            path = reconstruct_path(parent, start, goal)
            return path, explored_order, nodes_expanded, visit_count, heat_count

        for neighbor in get_neighbors(grid, current):
            new_cost = current_cost + 1
            heat_count[neighbor] = heat_count.get(neighbor, 0) + 1

            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                parent[neighbor] = current
                priority = new_cost + weight * manhattan(neighbor, goal)
                heapq.heappush(frontier, (priority, new_cost, neighbor))

    return None, explored_order, nodes_expanded, visit_count, heat_count


def dfs_samples(grid, start, goal):
    remaining_samples = frozenset(get_sample_positions(grid))
    start_state = (start[0], start[1], remaining_samples)

    stack = [start_state]
    visited = {start_state}
    parent = {}
    explored_order = []
    nodes_expanded = 0
    visit_count = {}
    heat_count = {start: 1}

    while stack:
        current = stack.pop()
        pos = (current[0], current[1])

        explored_order.append(pos)
        nodes_expanded += 1
        visit_count[pos] = visit_count.get(pos, 0) + 1

        if sample_goal_test(current, goal):
            state_path = reconstruct_path(parent, start_state, current)
            return extract_positions(state_path), explored_order, nodes_expanded, visit_count, heat_count

        successors = sample_successors(grid, current)

        for nxt in reversed(successors):
            next_pos = (nxt[0], nxt[1])
            heat_count[next_pos] = heat_count.get(next_pos, 0) + 1

            if nxt not in visited:
                visited.add(nxt)
                parent[nxt] = current
                stack.append(nxt)

    return None, explored_order, nodes_expanded, visit_count, heat_count


def ucs_samples(grid, start, goal):
    remaining_samples = frozenset(get_sample_positions(grid))
    start_state = (start[0], start[1], remaining_samples)

    frontier = []
    counter = 0
    heapq.heappush(frontier, (0, counter, start_state))

    parent = {}
    cost_so_far = {start_state: 0}
    explored_order = []
    nodes_expanded = 0
    visit_count = {}
    heat_count = {start: 1}
    closed = set()

    while frontier:
        current_cost, _, current = heapq.heappop(frontier)

        if current in closed:
            continue

        closed.add(current)
        pos = (current[0], current[1])

        explored_order.append(pos)
        nodes_expanded += 1
        visit_count[pos] = visit_count.get(pos, 0) + 1

        if sample_goal_test(current, goal):
            state_path = reconstruct_path(parent, start_state, current)
            return extract_positions(state_path), explored_order, nodes_expanded, visit_count, heat_count

        for nxt in sample_successors(grid, current):
            next_pos = (nxt[0], nxt[1])
            heat_count[next_pos] = heat_count.get(next_pos, 0) + 1

            new_cost = current_cost + 1
            if nxt not in cost_so_far or new_cost < cost_so_far[nxt]:
                cost_so_far[nxt] = new_cost
                parent[nxt] = current
                counter += 1
                heapq.heappush(frontier, (new_cost, counter, nxt))

    return None, explored_order, nodes_expanded, visit_count, heat_count


def depth_limited_search(grid, start_state, goal, limit, parent, visit_count, heat_count):
    stack = [(start_state, 0)]
    seen_depth = {start_state: 0}
    explored_order = []
    nodes_expanded = 0

    while stack:
        current, depth = stack.pop()
        pos = (current[0], current[1])

        explored_order.append(pos)
        nodes_expanded += 1
        visit_count[pos] = visit_count.get(pos, 0) + 1

        if sample_goal_test(current, goal):
            return current, explored_order, nodes_expanded, True

        if depth == limit:
            continue

        successors = sample_successors(grid, current)

        for nxt in reversed(successors):
            next_pos = (nxt[0], nxt[1])
            heat_count[next_pos] = heat_count.get(next_pos, 0) + 1

            next_depth = depth + 1
            if nxt not in seen_depth or next_depth < seen_depth[nxt]:
                seen_depth[nxt] = next_depth
                parent.setdefault(nxt, current)
                stack.append((nxt, next_depth))

    return None, explored_order, nodes_expanded, False


def ids_samples(grid, start, goal):
    remaining_samples = frozenset(get_sample_positions(grid))
    start_state = (start[0], start[1], remaining_samples)

    total_explored = []
    total_nodes_expanded = 0
    visit_count = {}
    heat_count = {start: 1}

    for limit in range(0, 200):
        parent = {}
        goal_state, explored_order, expanded, found = depth_limited_search(
            grid, start_state, goal, limit, parent, visit_count, heat_count
        )

        total_explored.extend(explored_order)
        total_nodes_expanded += expanded

        if found:
            state_path = reconstruct_path(parent, start_state, goal_state)
            return extract_positions(state_path), total_explored, total_nodes_expanded, visit_count, heat_count

    return None, total_explored, total_nodes_expanded, visit_count, heat_count


def astar_samples(grid, start, goal):
    remaining_samples = frozenset(get_sample_positions(grid))
    start_state = (start[0], start[1], remaining_samples)

    frontier = []
    counter = 0
    heapq.heappush(frontier, (sample_heuristic(start_state, goal), 0, counter, start_state))

    parent = {}
    cost_so_far = {start_state: 0}
    explored_order = []
    nodes_expanded = 0
    visit_count = {}
    heat_count = {start: 1}
    closed = set()

    while frontier:
        _, current_cost, _, current = heapq.heappop(frontier)

        if current in closed:
            continue

        closed.add(current)
        pos = (current[0], current[1])

        explored_order.append(pos)
        nodes_expanded += 1
        visit_count[pos] = visit_count.get(pos, 0) + 1

        if sample_goal_test(current, goal):
            state_path = reconstruct_path(parent, start_state, current)
            return extract_positions(state_path), explored_order, nodes_expanded, visit_count, heat_count

        for nxt in sample_successors(grid, current):
            next_pos = (nxt[0], nxt[1])
            heat_count[next_pos] = heat_count.get(next_pos, 0) + 1

            new_cost = current_cost + 1
            if nxt not in cost_so_far or new_cost < cost_so_far[nxt]:
                cost_so_far[nxt] = new_cost
                parent[nxt] = current
                counter += 1
                priority = new_cost + sample_heuristic(nxt, goal)
                heapq.heappush(frontier, (priority, new_cost, counter, nxt))

    return None, explored_order, nodes_expanded, visit_count, heat_count