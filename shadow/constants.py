"""Layout, tuning, palette, glyphs and block font for Shadow Maze."""

FPS = 30
TICK = 1.0 / FPS

# ---------------------------------------------------------------- layout
# The maze is MAZE_W x MAZE_H rooms. Walls live between rooms, so the drawn
# grid is (2w+1) x (2h+1) fat pixels, each two terminal columns wide.
MAZE_W, MAZE_H = 15, 8
GRID_W, GRID_H = MAZE_W * 2 + 1, MAZE_H * 2 + 1      # 31 x 17
FIELD_COLS = GRID_W * 2                             # 62
HUD_ROWS = 5                                        # block-digit score
GAP_ROWS = 1
MSG_ROWS = 1
MIN_ROWS = HUD_ROWS + GAP_ROWS + GRID_H + MSG_ROWS  # 24
MIN_COLS = FIELD_COLS + 2                           # 64

START = (1, 1)
LIVES = 3
EXTRA_LIFE_EVERY = 3000
READY_SECS = 1.2
DEATH_SECS = 1.0
CLEAR_SECS = 1.8


def level_params(level, hard):
    """Per-level tuning. hard=True is the Atari 'A' difficulty switch."""
    base = 2.0 if hard else 3.0
    floor = 0.8 if hard else 1.0
    return {
        # seconds the shadow lags behind you
        "delay": max(floor, base - 0.2 * (level - 1)),
        # seconds per cell when gliding in Game 1 (run mode)
        "step": max(0.10, 0.14 - 0.006 * (level - 1)),
        # fraction of rooms that get an extra opening (loops). Fewer = harder.
        "loops": max(0.10, 0.22 - 0.02 * (level - 1)),
        "gems": min(12, 5 + level),
    }


# ---------------------------------------------------------------- palette
# name: (256-colour index, 8-colour fallback). -1 is the terminal default.
PALETTE = {
    "bg": (-1, -1),
    "black": (16, 0),
    "floor": (17, -1),
    "wall": (172, 3),
    "player": (226, 3),
    "shadow": (93, 5),
    "shadow2": (55, 5),
    "shadow_near": (196, 1),
    "hint": (60, 5),
    "hud": (226, 3),
    "text": (250, 7),
    "dim": (244, 7),
    "red": (196, 1),
    "white": (231, 7),
    "green": (46, 2),
    "cyan": (51, 6),
    # the gems colour-cycle, 2600 style
    "gem0": (51, 6),
    "gem1": (118, 2),
    "gem2": (213, 5),
    "gem3": (208, 3),
    "gem4": (45, 6),
    "gem5": (201, 5),
}
GEM_CYCLE = ("gem0", "gem1", "gem2", "gem3", "gem4", "gem5")

# ---------------------------------------------------------------- glyphs
# Every grid pixel is two terminal characters.
GLYPHS = {
    "wall": "██",
    "floor": "  ",
    "player": "██",
    "shadow": ("▓▓", "▒▒"),
    "hint": "░░",
    "gem": "▐▌",
    "px": "██",
}
ASCII_GLYPHS = {
    "wall": "##",
    "floor": "  ",
    "player": "@@",
    "shadow": ("%%", "%%"),
    "hint": "::",
    "gem": "<>",
    "px": "##",
}

# ---------------------------------------------------------------- 3x5 block font
FONT = {
    "A": (" █ ", "█ █", "███", "█ █", "█ █"),
    "B": ("██ ", "█ █", "██ ", "█ █", "██ "),
    "C": (" ██", "█  ", "█  ", "█  ", " ██"),
    "D": ("██ ", "█ █", "█ █", "█ █", "██ "),
    "E": ("███", "█  ", "██ ", "█  ", "███"),
    "F": ("███", "█  ", "██ ", "█  ", "█  "),
    "G": (" ██", "█  ", "█ █", "█ █", " ██"),
    "H": ("█ █", "█ █", "███", "█ █", "█ █"),
    "I": ("███", " █ ", " █ ", " █ ", "███"),
    "J": ("  █", "  █", "  █", "█ █", " █ "),
    "K": ("█ █", "█ █", "██ ", "█ █", "█ █"),
    "L": ("█  ", "█  ", "█  ", "█  ", "███"),
    "M": ("█ █", "███", "███", "█ █", "█ █"),
    "N": ("██ ", "█ █", "█ █", "█ █", "█ █"),
    "O": ("███", "█ █", "█ █", "█ █", "███"),
    "P": ("██ ", "█ █", "██ ", "█  ", "█  "),
    "Q": (" █ ", "█ █", "█ █", "██ ", " ██"),
    "R": ("██ ", "█ █", "██ ", "█ █", "█ █"),
    "S": ("███", "█  ", "███", "  █", "███"),
    "T": ("███", " █ ", " █ ", " █ ", " █ "),
    "U": ("█ █", "█ █", "█ █", "█ █", "███"),
    "V": ("█ █", "█ █", "█ █", "█ █", " █ "),
    "W": ("█ █", "█ █", "███", "███", "█ █"),
    "X": ("█ █", "█ █", " █ ", "█ █", "█ █"),
    "Y": ("█ █", "█ █", " █ ", " █ ", " █ "),
    "Z": ("███", "  █", " █ ", "█  ", "███"),
    "0": ("███", "█ █", "█ █", "█ █", "███"),
    "1": (" █ ", "██ ", " █ ", " █ ", "███"),
    "2": ("███", "  █", "███", "█  ", "███"),
    "3": ("███", "  █", "███", "  █", "███"),
    "4": ("█ █", "█ █", "███", "  █", "  █"),
    "5": ("███", "█  ", "███", "  █", "███"),
    "6": ("███", "█  ", "███", "█ █", "███"),
    "7": ("███", "  █", "  █", "  █", "  █"),
    "8": ("███", "█ █", "███", "█ █", "███"),
    "9": ("███", "█ █", "███", "  █", "███"),
    "!": (" █ ", " █ ", " █ ", "   ", " █ "),
    "?": ("███", "  █", " ██", "   ", " █ "),
    " ": ("   ", "   ", "   ", "   ", "   "),
}
FONT_ADVANCE = 8   # columns per character: 3 pixels x 2 cols + 2 col gap

HELP_LINES = (
    "YOUR SHADOW REPLAYS YOUR EXACT PATH, A FEW SECONDS LATE.",
    "STAND STILL AND IT CATCHES UP. BACKTRACK AND YOU WALK INTO IT.",
    "",
    "COLLECT EVERY GEM TO CLEAR THE MAZE.",
    "LOOPS LET YOU CIRCLE WITHOUT RETRACING A STEP.",
    "DEAD ENDS ARE TRAPS: THE ONLY WAY OUT IS THROUGH YOUR SHADOW.",
    "GRAB A DEAD-END GEM ONLY WHEN THE SHADOW IS FAR BEHIND.",
    "",
    "GAME 1  RUN MODE:  YOU KEEP MOVING UNTIL A WALL OR A TURN.",
    "GAME 2  STEP MODE: ONE CELL PER KEY PRESS.",
    "DIFFICULTY A: THE SHADOW FOLLOWS ONE SECOND CLOSER.",
    "",
    "EXTRA LIFE EVERY 3000 POINTS.   PRESS ANY KEY.",
)
