"""curses drawing: block-digit HUD, the maze, sprites, banners and overlays."""
import curses

from .constants import (
    PALETTE, GEM_CYCLE, GLYPHS, ASCII_GLYPHS, FONT, FONT_ADVANCE,
    GRID_W, GRID_H, FIELD_COLS, HUD_ROWS, GAP_ROWS, MIN_ROWS, MIN_COLS, HELP_LINES,
)
from .world import OPEN


class Renderer:
    def __init__(self, stdscr, ascii_mode=False):
        self.scr = stdscr
        self.g = ASCII_GLYPHS if ascii_mode else GLYPHS
        self.pairs = {}
        self.colors_ok = curses.has_colors()
        if self.colors_ok:
            curses.start_color()
            try:
                curses.use_default_colors()
            except curses.error:
                pass
        self.many = self.colors_ok and curses.COLORS >= 256
        self.max_pairs = curses.COLOR_PAIRS if self.colors_ok else 0
        self.ox = self.oy = 0

    # ------------------------------------------------------------ colours
    def cidx(self, name):
        full, basic = PALETTE[name]
        return full if self.many else basic

    def attr(self, fg, bg="bg", bold=False):
        a = curses.A_BOLD if bold else 0
        if not self.colors_ok:
            return a
        key = (self.cidx(fg), self.cidx(bg))
        if key not in self.pairs:
            n = len(self.pairs) + 1
            if n >= self.max_pairs:
                return a
            try:
                curses.init_pair(n, key[0], key[1])
            except curses.error:
                return a
            self.pairs[key] = n
        return curses.color_pair(self.pairs[key]) | a

    # ------------------------------------------------------------ primitives
    def put(self, y, x, s, a=0):
        if y < 0 or x < 0:
            return
        try:
            self.scr.addstr(y, x, s, a)
        except curses.error:
            pass

    def size(self):
        return self.scr.getmaxyx()

    def layout(self):
        rows, cols = self.size()
        self.ox = max(0, (cols - FIELD_COLS) // 2)
        self.oy = max(0, (rows - MIN_ROWS) // 2)
        return rows >= MIN_ROWS and cols >= MIN_COLS

    @property
    def field_y(self):
        return self.oy + HUD_ROWS + GAP_ROWS

    def too_small(self):
        rows, cols = self.size()
        msg = "NEED %dx%d, HAVE %dx%d" % (MIN_COLS, MIN_ROWS, cols, rows)
        self.put(rows // 2, max(0, (cols - len(msg)) // 2), msg, self.attr("red", bold=True))

    def center_text(self, y, text, fg="text", bg="bg", bold=False):
        rows, cols = self.size()
        self.put(y, max(0, (cols - len(text)) // 2), text, self.attr(fg, bg, bold))

    def field_text(self, y, text, fg="text", bg="bg", bold=False):
        """Text centred on the playfield rather than the screen."""
        self.put(y, self.ox + max(0, (FIELD_COLS - len(text)) // 2), text, self.attr(fg, bg, bold))

    # ------------------------------------------------------------ block font
    @staticmethod
    def big_width(text):
        return len(text) * FONT_ADVANCE - 2

    def big_text(self, y, x, text, fg, bg="bg"):
        a = self.attr(fg, bg)
        px = self.g["px"]
        for ci, ch in enumerate(text.upper()):
            rows = FONT.get(ch, FONT[" "])
            for r in range(5):
                for i, bit in enumerate(rows[r]):
                    if bit != " ":
                        self.put(y + r, x + ci * FONT_ADVANCE + i * 2, px, a)

    def big_center(self, y, text, fg, bg="bg"):
        rows, cols = self.size()
        w = self.big_width(text)
        if w <= cols:
            self.big_text(y, (cols - w) // 2, text, fg, bg)
        else:
            self.center_text(y + 2, text, fg, bg, bold=True)

    # ------------------------------------------------------------ HUD
    def draw_hud(self, score, lives, level):
        y, x = self.oy, self.ox
        self.big_text(y, x, "%06d" % min(score, 999999), "hud")
        rx = x + FIELD_COLS - 15
        self.put(y, rx, "LIVES", self.attr("dim"))
        for i in range(min(lives, 5)):
            self.put(y + 1, rx + i * 3, self.g["player"], self.attr("player"))
        self.put(y + 3, rx, "LEVEL", self.attr("dim"))
        self.put(y + 4, rx, "%02d" % level, self.attr("text", bold=True))

    def draw_msg(self, left, center, right, center_fg="text"):
        y = self.field_y + GRID_H
        self.put(y, self.ox, left, self.attr("text"))
        self.put(y, self.ox + FIELD_COLS - len(right), right, self.attr("dim"))
        self.field_text(y, center, center_fg, bold=True)

    # ------------------------------------------------------------ playfield
    def draw_field(self, grid, gems, player, shadow, hint, frame, flash=None):
        fy, fx = self.field_y, self.ox
        if flash:
            a = self.attr("black", flash)
            for gy in range(GRID_H):
                self.put(fy + gy, fx, "  " * GRID_W, a)
            return
        wall_a = self.attr("wall", "floor")
        floor_a = self.attr("floor", "floor")
        wall, floor = self.g["wall"], self.g["floor"]
        for gy in range(GRID_H):
            row = grid[gy]
            for gx in range(GRID_W):
                if row[gx] == OPEN:
                    self.put(fy + gy, fx + gx * 2, floor, floor_a)
                else:
                    self.put(fy + gy, fx + gx * 2, wall, wall_a)
        gem_a = self.attr(GEM_CYCLE[(frame // 5) % len(GEM_CYCLE)], "floor", bold=True)
        gem = self.g["gem"]
        for (x, y) in gems:
            self.put(fy + y, fx + x * 2, gem, gem_a)
        if hint is not None and hint != player:
            self.put(fy + hint[1], fx + hint[0] * 2, self.g["hint"], self.attr("hint", "floor"))
        if shadow is not None:
            near = abs(shadow[0] - player[0]) + abs(shadow[1] - player[1]) <= 3
            if near:
                col = "shadow_near" if frame % 2 else "shadow"
            else:
                col = "shadow" if frame % 2 else "shadow2"
            glyph = self.g["shadow"][(frame // 4) % 2]
            self.put(fy + shadow[1], fx + shadow[0] * 2, glyph, self.attr(col, "floor", bold=True))
        self.put(fy + player[1], fx + player[0] * 2, self.g["player"], self.attr("player", "floor", bold=True))

    # ------------------------------------------------------------ overlays
    def band(self, y, height, bg="black"):
        a = self.attr("black", bg)
        for r in range(height):
            self.put(y + r, self.ox, " " * FIELD_COLS, a)

    def banner(self, lines, fg, bg="black", footer=None):
        """One or two words in the block font, boxed over the middle of the field."""
        rows, cols = self.size()
        h = len(lines) * 6 - 1
        y = self.field_y + (GRID_H - h) // 2
        self.band(y - 1, h + (3 if footer else 2), bg)
        if footer:
            self.field_text(y + h, footer, "text", bg)
        for i, text in enumerate(lines):
            w = self.big_width(text)
            if w <= cols:
                self.big_text(y + i * 6, (cols - w) // 2, text, fg, bg)
            else:
                self.center_text(y + i * 6 + 2, text, fg, bg, bold=True)

    def small_box(self, text, fg="white", bg="red"):
        y = self.field_y + GRID_H // 2
        self.band(y - 1, 3, bg)
        self.field_text(y, text, fg, bg, bold=True)

    def draw_help(self):
        y = self.field_y
        self.band(y, GRID_H, "black")
        self.field_text(y + 1, "HOW TO PLAY", "hud", "black", bold=True)
        for i, line in enumerate(HELP_LINES):
            self.field_text(y + 3 + i, line, "text", "black")

    # ------------------------------------------------------------ title
    def draw_title(self, frame, mode, hard, high, delay):
        y = self.oy
        cyc = GEM_CYCLE[(frame // 4) % len(GEM_CYCLE)]
        self.big_center(y, "SHADOW", cyc)
        self.big_center(y + 6, "MAZE", "shadow" if frame % 2 else "shadow2")

        # attract strip: a runner and its shadow loop under the title
        lane = FIELD_COLS // 2 + 14
        px = (frame // 2) % lane - 2
        sx = px - 9
        if 0 <= px < FIELD_COLS // 2:
            self.put(y + 12, self.ox + px * 2, self.g["player"], self.attr("player", bold=True))
        if 0 <= sx < FIELD_COLS // 2:
            col = "shadow" if frame % 2 else "shadow2"
            self.put(y + 12, self.ox + sx * 2, self.g["shadow"][(frame // 4) % 2], self.attr(col, bold=True))

        self.field_text(y + 14, "YOUR SHADOW REPLAYS EVERY MOVE YOU MAKE, A FEW SECONDS LATE.")
        self.field_text(y + 15, "COLLECT EVERY GEM. DON'T LET IT TOUCH YOU.")
        mode_txt = "RUN" if mode == 1 else "STEP"
        self.field_text(
            y + 17,
            "GAME %d  %s MODE      DIFFICULTY %s  SHADOW %.1f SEC"
            % (mode, mode_txt, "A" if hard else "B", delay),
            "hud", bold=True,
        )
        self.field_text(y + 18, "G  GAME SELECT          D  DIFFICULTY SWITCH", "dim")
        if (frame // 10) % 2:
            self.field_text(y + 20, "PRESS SPACE TO START", "white", bold=True)
        self.field_text(y + 21, "ARROWS / WASD MOVE    P PAUSE    ? HELP    Q QUIT", "dim")
        self.field_text(y + 22, "HIGH SCORE %06d" % high, "text")
