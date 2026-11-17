"""python -m yuris_joyfix [scan|install|restore GAME.exe]."""

import argparse
import pathlib
import sys
from .core import scan, install, restore


def main():
    if len(sys.argv) == 1:
        from .gui import gui

        gui()
        return 0
    parser = argparse.ArgumentParser(description="Whirlpool YU-RIS JoyFix")
    parser.add_argument("action", choices=["scan", "install", "restore"])
    parser.add_argument("exe", type=pathlib.Path)
    args = parser.parse_args()
    try:
        result = {"scan": scan, "install": install, "restore": restore}[args.action](
            args.exe
        )
        if sys.stdout:
            print(result)
        return 0
    except Exception as error:
        if sys.stderr:
            print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
