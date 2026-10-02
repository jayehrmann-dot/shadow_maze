"""Player and Shadow."""
from collections import deque

DIRS = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}


class Player:
    def __init__(self, pos):
        self.pos = pos
        self.facing = None      # direction currently gliding in (Game 1)
        self.want = None        # buffered turn, taken as soon as it opens
        self.next_step = 0.0    # game-clock time of the next glide step


class Shadow:
    """Replays the player's trail `delay` seconds late.

    The trail is a queue of (time, position). The shadow stands wherever the
    player stood `delay` seconds ago, so standing still lets it arrive.
    """

    def __init__(self, start, t0, delay):
        self.trail = deque([(t0, start)])
        self.delay = delay
        self.wake_at = t0 + delay
        self.pos = None          # None while still asleep

    def record(self, t, pos):
        self.trail.append((t, pos))

    def update(self, now):
        target = now - self.delay
        if target < self.trail[0][0]:
            self.pos = None
            return
        while len(self.trail) > 1 and self.trail[1][0] <= target:
            self.trail.popleft()
        self.pos = self.trail[0][1]

    def seconds_to_wake(self, now):
        return max(0.0, self.wake_at - now)
