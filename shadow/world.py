"""Maze generation, loops and gem placement."""
import random
from collections import deque

from .constants import MAZE_W, MAZE_H, GRID_W, GRID_H

WALL, OPEN = 1, 0
STEPS = ((1, 0), (-1, 0), (0, 1), (0, -1))


def make_maze(loop_fraction, rng):
    """Perfect maze by depth-first carving, then extra openings for loops.

    Returns a GRID_H x GRID_W list of lists of WALL / OPEN. Rooms sit at
    odd (x, y) coordinates; the pixels between them are the walls.
    """
    g = [[WALL] * GRID_W for _ in range(GRID_H)]
    start = (0, 0)
    g[1][1] = OPEN
    seen = {start}
    stack = [start]
    while stack:
        x, y = stack[-1]
        options = [
            (x + dx, y + dy, dx, dy)
            for dx, dy in STEPS
            if 0 <= x + dx < MAZE_W and 0 <= y + dy < MAZE_H and (x + dx, y + dy) not in seen
        ]
        if not options:
            stack.pop()
            continue
        nx, ny, dx, dy = rng.choice(options)
        g[2 * y + 1 + dy][2 * x + 1 + dx] = OPEN     # the wall between
        g[2 * ny + 1][2 * nx + 1] = OPEN             # the new room
        seen.add((nx, ny))
        stack.append((nx, ny))

    # Knock out interior walls that separate two rooms. Every interior pixel
    # with odd x+y lies between two rooms, so opening it always makes a loop.
    between = [
        (x, y)
        for y in range(1, GRID_H - 1)
        for x in range(1, GRID_W - 1)
        if g[y][x] == WALL and (x + y) % 2 == 1
    ]
    rng.shuffle(between)
    for x, y in between[: int(MAZE_W * MAZE_H * loop_fraction)]:
        g[y][x] = OPEN
    return g


def is_open(g, x, y):
    return 0 <= x < GRID_W and 0 <= y < GRID_H and g[y][x] == OPEN


def distances(g, start):
    """BFS walking distance (in grid pixels) from start to every open pixel."""
    dist = {start: 0}
    q = deque([start])
    while q:
        x, y = q.popleft()
        for dx, dy in STEPS:
            n = (x + dx, y + dy)
            if n not in dist and is_open(g, n[0], n[1]):
                dist[n] = dist[(x, y)] + 1
                q.append(n)
    return dist


def dead_ends(g):
    """Rooms with exactly one way out."""
    out = set()
    for y in range(1, GRID_H, 2):
        for x in range(1, GRID_W, 2):
            exits = sum(1 for dx, dy in STEPS if is_open(g, x + dx, y + dy))
            if exits == 1:
                out.add((x, y))
    return out


def place_gems(g, start, count, rng):
    """Spread gems over rooms that are a fair walk from the start."""
    dist = distances(g, start)
    rooms = [p for p, d in dist.items() if p[0] % 2 and p[1] % 2 and d >= 8]
    rng.shuffle(rooms)
    picked = []
    for p in rooms:                          # first pass: keep them spread out
        if all(abs(p[0] - q[0]) + abs(p[1] - q[1]) >= 5 for q in picked):
            picked.append(p)
        if len(picked) == count:
            break
    for p in rooms:                          # fill in if the maze was cramped
        if len(picked) == count:
            break
        if p not in picked:
            picked.append(p)
    return set(picked)
