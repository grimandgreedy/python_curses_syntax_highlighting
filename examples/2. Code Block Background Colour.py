#!/usr/bin/env python3
"""Demonstrates different background color options.

Press keys 1-6 to switch between background colors. Press q to quit.
"""

import curses
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from curses_syntax_highlighting import preview_text


def main(stdscr, filepath):
    curses.curs_set(0)
    stdscr.keypad(True)

    max_y, max_x = stdscr.getmaxyx()

    bg_options = {
        '1': (None,            "Terminal Default (None)"),
        '2': (-1,              "Terminal Default (-1)"),
        '3': (232,             "Dark Gray (232)"),
        '4': (17,              "Dark Blue (17)"),
        '5': (235,             "Almost Black (235)"),
        '6': (curses.COLOR_BLACK, "Pure Black"),
    }

    current_bg = None
    current_label = "Terminal Default (None)"

    while True:
        stdscr.erase()

        header = f"Background Color: {current_label}  |  1-6: change  q: quit"
        try:
            stdscr.addstr(0, 0, " " * max_x)
            stdscr.addstr(0, 0, header[:max_x], curses.A_REVERSE | curses.A_BOLD)
        except curses.error:
            pass

        preview_text(
            stdscr,
            filepath,
            code_x=0,
            code_y=1,
            code_w=max_x,
            code_h=max_y - 1,
            show_line_numbers=True,
            indent_guides=True,
            theme='dark',
            bg_color=current_bg,
        )

        key = stdscr.getch()
        if key in (ord('q'), ord('Q'), 27):
            break
        elif chr(key) in bg_options:
            current_bg, current_label = bg_options[chr(key)]


if __name__ == '__main__':
    default = os.path.join(os.path.dirname(__file__), 'test_file_for_features.py')
    filepath = sys.argv[1] if len(sys.argv) > 1 else default
    if not os.path.exists(filepath):
        print(f"Error: File '{filepath}' not found")
        sys.exit(1)
    try:
        curses.wrapper(lambda stdscr: main(stdscr, filepath))
    except KeyboardInterrupt:
        print("\nExited.")
