"""Game loop, input, levels and scoring for Shadow Maze."""
import curses
import json
import os
import random
import time

from .constants import (
    TICK, LIVES, EXTRA_LIFE_EVERY, START, READY_SECS, DEATH_SECS, CLEAR_SECS,
    GEM_CYCLE, level_params,
)
from .entities import Player, Shadow, DIRS
from .render import Renderer
from .world import make_maze, place_gems, is_open

TITLE, READY, PLAY, DYING, CLEAR, GAMEOVER = range(6)

HIGH_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "highscore.json"
)

KEY_DIRS = {
    curses.KEY_UP: "up", curses.KEY_DOWN: "down",
    curses.KEY_LEFT: "left", curses.KEY_RIGHT: "right",
    ord("w"): "up", ord("s"): "down", ord("a"): "left", ord("d"): "right",
    ord("W"): "up", ord("S"): "down", ord("A"): "left", ord("D"): "right",
}
ESC = 27


def load_high():
    try:
        with open(HIGH_FILE) as f:
            return int(json.load(f).get("high", 0))
    except (OSError, ValueError, AttributeError):
        return 0


def save_high(high):
    try:
        with open(HIGH_FILE, "w") as f:
            json.dump({"high": high}, f)
    except OSError:
        pass


class Clock:
    """Game time that stands still while paused."""

    def __init__(self):
        self.t0 = time.monotonic()
        self.lost = 0.0
        self.paused_at = None

    def now(self):
        base = self.paused_at if self.paused_at is not None else time.monotonic()
        return base - self.t0 - self.lost

    def pause(self):
        if self.paused_at is None:
            self.paused_at = time.monotonic()

    def resume(self):
        if self.paused_at is not None:
            self.lost += time.monotonic() - self.paused_at
            self.paused_at = None


class Game:
    def __init__(self, stdscr, seed=None, ascii_mode=False):
        self.scr = stdscr
        try:
            curses.curs_set(0)
        except curses.error:
            pass
        stdscr.nodelay(True)
        stdscr.keypad(True)
        self.r = Renderer(stdscr, ascii_mode)
        self.rng = random.Random(seed)
        self.high = load_high()
        self.mode = 1            # Atari "game select": 1 run, 2 step
        self.hard = False        # difficulty switch: A (hard) / B
        self.state = TITLE
        self.frame = 0
        self.clock = Clock()
        self.paused = self.help = self.confirm_quit = False
        self.msg, self.msg_until = "", 0.0
        self.score, self.lives, self.level = 0, LIVES, 1
        self.next_extra = EXTRA_LIFE_EVERY
        self.grid, self.gems, self.params = None, set(), None
        self.player, self.shadow = None, None
        self.state_until = 0.0

    # ------------------------------------------------------------ main loop
    def run(self):
        while True:
            t = time.monotonic()
            if not self.step(self.read_keys()):
                break
            self.draw()
            dt = time.monotonic() - t
            if dt < TICK:
                time.sleep(TICK - dt)
            self.frame += 1

    def read_keys(self):
        keys = []
        while True:
            k = self.scr.getch()
            if k == -1:
                return keys
            keys.append(k)

    def say(self, text, secs=2.0):
        self.msg, self.msg_until = text, self.clock.now() + secs

    def sync_clock(self):
        if self.paused or self.help or self.confirm_quit:
            self.clock.pause()
        else:
            self.clock.resume()

    # ------------------------------------------------------------ game setup
    def new_game(self):
        self.score, self.lives, self.level = 0, LIVES, 1
        self.next_extra = EXTRA_LIFE_EVERY
        self.clock = Clock()
        self.paused = self.help = self.confirm_quit = False
        self.start_level()

    def start_level(self):
        self.params = level_params(self.level, self.hard)
        self.grid = make_maze(self.params["loops"], self.rng)
        self.gems = place_gems(self.grid, START, self.params["gems"], self.rng)
        self.player = Player(START)
        self.shadow = None
        self.state = READY
        self.state_until = self.clock.now() + READY_SECS
        self.say("LEVEL %d" % self.level, READY_SECS + 1.0)

    def begin_play(self, now):
        self.shadow = Shadow(START, now, self.params["delay"])
        self.player.next_step = now + self.params["step"]
        self.state = PLAY

    def respawn(self, now):
        self.player = Player(START)
        self.shadow = None
        self.state = READY
        self.state_until = now + READY_SECS

    def add_score(self, pts):
        self.score += pts
        if self.score >= self.next_extra:
            self.next_extra += EXTRA_LIFE_EVERY
            self.lives += 1
            self.say("EXTRA LIFE!")
        if self.score > self.high:
            self.high = self.score

    # ------------------------------------------------------------ input
    def step(self, keys):
        if self.state == TITLE:
            return self.step_title(keys)
        for k in keys:
            if self.confirm_quit:
                if k in (ord("y"), ord("Y")):
                    return False
                self.confirm_quit = False
                self.sync_clock()
                continue
            if k in (ord("q"), ord("Q"), ESC):
                if self.state == GAMEOVER:
                    self.state = TITLE
                    continue
                self.confirm_quit = True
                self.sync_clock()
                continue
            if self.help:
                self.help = False
                self.sync_clock()
                continue
            if k == ord("?"):
                self.help = True
                self.sync_clock()
                continue
            if k in (ord("p"), ord("P")):
                self.paused = not self.paused
                self.sync_clock()
                continue
            if self.state == GAMEOVER and k in (ord(" "), ord("\n"), curses.KEY_ENTER):
                self.state = TITLE
                continue
            if self.paused or self.state != PLAY:
                continue
            if k in KEY_DIRS:
                self.press(KEY_DIRS[k])

        if self.paused or self.help or self.confirm_quit:
            return True
        now = self.clock.now()
        if self.state == READY and now >= self.state_until:
            self.begin_play(now)
        elif self.state == PLAY:
            self.update_play(now)
        elif self.state == DYING and now >= self.state_until:
            if self.lives <= 0:
                save_high(self.high)
                self.state = GAMEOVER
            else:
                self.respawn(now)
        elif self.state == CLEAR and now >= self.state_until:
            self.level += 1
            self.start_level()
        return True

    def step_title(self, keys):
        for k in keys:
            if self.help:
                self.help = False
                continue
            if k in (ord("q"), ord("Q"), ESC):
                return False
            if k in (ord(" "), ord("\n"), curses.KEY_ENTER):
                self.new_game()
            elif k in (ord("g"), ord("G")):
                self.mode = 2 if self.mode == 1 else 1
            elif k in (ord("d"), ord("D")):
                self.hard = not self.hard
            elif k == ord("?"):
                self.help = True
        return True

    # ------------------------------------------------------------ movement
    def can_move(self, pos, d):
        dx, dy = DIRS[d]
        return is_open(self.grid, pos[0] + dx, pos[1] + dy)

    def press(self, d):
        p = self.player
        now = self.clock.now()
        if self.mode == 2:
            if self.can_move(p.pos, d):
                self.move(d, now)
            return
        if self.can_move(p.pos, d):
            was_stopped = p.facing is None
            p.facing, p.want = d, None
            if was_stopped:
                self.move(d, now)
                p.next_step = now + self.params["step"]
        else:
            p.want = d          # turn as soon as that way opens

    def move(self, d, now):
        dx, dy = DIRS[d]
        p = self.player
        new = (p.pos[0] + dx, p.pos[1] + dy)
        p.pos = new
        self.shadow.record(now, new)
        if new in self.gems:
            self.gems.discard(new)
            self.add_score(10 * self.level)
            if not self.gems:
                self.level_clear(now)
                return
        if self.shadow.pos == new:
            self.die(now)

    def update_play(self, now):
        p = self.player
        prev_player = p.pos
        if self.mode == 1:
            for _ in range(4):
                if now < p.next_step:
                    break
                if p.want and self.can_move(p.pos, p.want):
                    p.facing, p.want = p.want, None
                if p.facing and self.can_move(p.pos, p.facing):
                    self.move(p.facing, now)
                    p.next_step += self.params["step"]
                else:
                    p.facing = p.want = None
                    p.next_step = now + self.params["step"]
                    break
                if self.state != PLAY:
                    return
        prev_shadow = self.shadow.pos
        self.shadow.update(now)
        sp = self.shadow.pos
        if sp is None:
            return
        swapped = prev_shadow is not None and sp == prev_player and p.pos == prev_shadow
        if sp == p.pos or swapped:
            self.die(now)

    def die(self, now):
        self.lives -= 1
        self.state = DYING
        self.state_until = now + DEATH_SECS
        self.say("YOUR SHADOW CAUGHT YOU" if self.lives > 0 else "THE SHADOW WINS", DEATH_SECS + 1.5)
        curses.beep()

    def level_clear(self, now):
        bonus = 100 * self.level
        self.add_score(bonus)
        self.state = CLEAR
        self.state_until = now + CLEAR_SECS
        self.say("BONUS %d" % bonus, CLEAR_SECS)
        curses.beep()

    # ------------------------------------------------------------ drawing
    def draw(self):
        self.scr.erase()
        if not self.r.layout():
            self.r.too_small()
            self.scr.refresh()
            return
        if self.state == TITLE:
            self.r.draw_title(self.frame, self.mode, self.hard, self.high,
                              level_params(1, self.hard)["delay"])
            if self.help:
                self.r.draw_help()
            self.scr.refresh()
            return

        now = self.clock.now()
        self.r.draw_hud(self.score, self.lives, self.level)
        shadow_pos = self.shadow.pos if self.shadow else None
        hint = START if shadow_pos is None and self.state in (READY, PLAY) else None
        flash = None
        if self.state == DYING:
            flash = ("red", "white", "black")[(self.frame // 2) % 3]
        self.r.draw_field(self.grid, self.gems, self.player.pos, shadow_pos, hint, self.frame, flash)

        left = "GEMS %02d" % len(self.gems)
        right = "GAME %d  %s" % (self.mode, "A" if self.hard else "B")
        if self.state == PLAY and shadow_pos is None:
            center, fg = "SHADOW WAKES IN %.1f" % self.shadow.seconds_to_wake(now), "shadow_near"
        elif now < self.msg_until:
            center, fg = self.msg, "hud"
        else:
            center, fg = "HI %06d" % self.high, "dim"
        self.r.draw_msg(left, center, right, fg)

        if self.state == READY:
            self.r.banner(["READY"], "green")
        elif self.state == CLEAR:
            self.r.banner(["CLEAR"], GEM_CYCLE[(self.frame // 3) % len(GEM_CYCLE)])
        elif self.state == GAMEOVER:
            self.r.banner(["GAME", "OVER"], "red", footer="SPACE FOR TITLE")
        if self.paused:
            self.r.banner(["PAUSE"], "white")
        if self.help:
            self.r.draw_help()
        if self.confirm_quit:
            self.r.small_box("QUIT GAME?   Y / N")
        self.scr.refresh()

