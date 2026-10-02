"""Entry point: python3 -m shadow"""
import argparse
import curses
import locale
import os
import sys


def main():
    ap = argparse.ArgumentParser(prog="shadow", description="Shadow Maze")
    ap.add_argument("--seed", type=int, default=None, help="fixed maze seed")
    ap.add_argument("--ascii", action="store_true", help="plain ASCII glyphs")
    args = ap.parse_args()

    locale.setlocale(locale.LC_ALL, "")
    os.environ.setdefault("ESCDELAY", "25")
    if not os.environ.get("TERM"):
        os.environ["TERM"] = "xterm-256color"
    from .engine import Game

    def run(stdscr):
        Game(stdscr, seed=args.seed, ascii_mode=args.ascii).run()

    try:
        curses.wrapper(run)
    except KeyboardInterrupt:
        pass
    print("The shadow stops when you do.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
