# Shadow Maze

Something is following you through the maze, and it is you. Your shadow
replays every move you make, a few seconds late, step for step. Collect every
gem without ever touching it. Atari 2600 looks, single-screen maze play,
running entirely inside your terminal.

<p align="center">
<img width="563" height="425" alt="shadow_maze" src="https://github.com/user-attachments/assets/06b842cb-3280-46a6-90cc-016fb7254397" />
<p>

```bash
./play.sh
```

or `python3 -m shadow` from this folder. Needs Python 3 (ships with macOS)
and a terminal at least 64 columns by 24 rows. A 256-colour terminal gives the
full palette; 8-colour terminals still work. `--ascii` swaps the block glyphs
for plain characters and `--seed N` repeats a maze layout.

## The game

A 15x8-room maze drawn in fat orange pixels on a navy floor. You are the
yellow block in the top-left corner. The flickering purple block is your
shadow. The colour-cycling gems are what you came for.

- **The shadow is your past.** It stands exactly where you stood N seconds
  ago. It cannot cut corners, cannot hunt you, and cannot go anywhere you have
  not already been. It also never slows down and never stops unless you did.
- **Standing still is how you die.** Stop, and N seconds later the shadow
  arrives on your square.
- **Backtracking is the other way to die.** Turn around and you walk straight
  into it. Dead ends are the trap: go in for a gem and the only way out is
  back through your own trail. Take them when the shadow is far behind, or
  when it has not woken up yet.
- **Loops keep you alive.** Every maze has extra openings. Circle a block and
  you never retrace a step, so the shadow stays behind you forever. Plan a
  route that threads the gems through loops.
- **Shadow wakes.** At the start of each level (and after each life) the
  shadow sleeps at your starting square for N seconds. A faint ghost marks the
  spot and the message line counts down. Be gone by then.
- **Flicker warning.** When the shadow is within three squares it flashes red.
- **Levels.** Clear every gem and the next maze is generated: fewer loops,
  more gems, and the shadow follows a little closer each time. Bonus 100 x
  level. Gems are worth 10 x level.
- **Game over** when you run out of lives. Extra life every 3000 points.

The high score is saved to `highscore.json` in this folder.

## Switches

Like a real 2600 cartridge, the title screen has a game-select and a
difficulty switch.

| Switch | Options |
| --- | --- |
| **Game 1, Run** | Tap a direction and you keep gliding until you hit a wall or turn. Taps ahead of a junction are buffered, Pac-Man style. |
| **Game 2, Step** | One square per key press. Hold the key to use your OS key-repeat. Harder: a hesitant thumb is a stationary player. |
| **Difficulty B** | Shadow starts 3.0 seconds behind. |
| **Difficulty A** | Shadow starts 2.0 seconds behind. |

## Controls

| Key | Action |
| --- | --- |
| Arrows / WASD | Move (in Game 1: set your direction) |
| Space | Start |
| G / D | Game select / difficulty switch (title screen) |
| P | Pause |
| ? | How to play |
| Q / Esc | Quit (asks first) |

## Layout

```
shadow/
  constants.py   layout, per-level tuning, palette, glyphs, block font, help text
  world.py       maze carving, loop openings, BFS distances, gem placement
  entities.py    Player, Shadow (the time-delayed trail)
  render.py      curses drawing: block-digit HUD, maze, sprites, banners, title
  engine.py      game loop, input, switches, levels, scoring, high score
  __main__.py    entry point and flags
highscore.json   created after your first game
```

Difficulty lives in `level_params()` at the top of `constants.py`: the shadow
delay, glide speed, loop fraction and gem count per level. Maze size is
`MAZE_W` x `MAZE_H` in the same file (bigger needs a taller terminal).
