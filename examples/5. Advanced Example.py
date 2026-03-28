#!/usr/bin/env python3
"""Advanced example showing high-level API, low-level API, and split-screen viewing.

Usage:
    python "5. Advanced Example.py"              # Uses this file
    python "5. Advanced Example.py" myfile.py    # Views any file
"""

import curses
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from curses_syntax_highlighting import preview_text, LazyFileViewer, get_lexer, init_colors, display_code


def example_high_level(stdscr, filepath):
    """Example using the high-level preview_text function."""
    stdscr.clear()
    max_y, max_x = stdscr.getmaxyx()

    preview_text(
        stdscr,
        filepath,
        code_x=0,
        code_y=1,
        code_w=max_x,
        code_h=max_y - 2,
        show_line_numbers=True,
        indent_guides=True,
        theme='dark',
    )

    header = "Advanced Example - High Level API (press any key for next)"
    try:
        stdscr.addstr(0, 0, header[:max_x], curses.A_REVERSE | curses.A_BOLD)
    except curses.error:
        pass

    stdscr.refresh()
    stdscr.getch()


def example_low_level(stdscr, filepath):
    """Example using the low-level API for more control."""
    stdscr.clear()
    max_y, max_x = stdscr.getmaxyx()

    lexer = get_lexer(filepath)
    viewer = LazyFileViewer(filepath, lexer, block_size=100)
    token_to_color = init_colors('dark')

    display_code(
        stdscr=stdscr,
        viewer=viewer,
        token_to_color=token_to_color,
        code_x=0,
        code_y=1,
        code_w=max_x,
        code_h=max_y - 2,
        show_line_numbers=True,
        indent_guides=True,
        scroll_offset=0,
    )

    header = f"Advanced Example - Low Level API | {viewer.total_lines} lines (press any key for next)"
    try:
        stdscr.addstr(0, 0, header[:max_x], curses.A_REVERSE | curses.A_BOLD)
    except curses.error:
        pass

    stdscr.refresh()
    stdscr.getch()


def example_split_screen(stdscr, filepath):
    """Example showing two files side-by-side."""
    stdscr.clear()
    max_y, max_x = stdscr.getmaxyx()
    mid_x = max_x // 2

    test_file = os.path.join(os.path.dirname(__file__), 'test_file_for_features.py')

    preview_text(
        stdscr,
        test_file,
        code_x=0,
        code_y=1,
        code_w=mid_x - 1,
        code_h=max_y - 2,
        show_line_numbers=True,
        theme='dark',
    )

    for y in range(1, max_y - 1):
        try:
            stdscr.addstr(y, mid_x, '│', curses.A_DIM)
        except curses.error:
            pass

    preview_text(
        stdscr,
        filepath,
        code_x=mid_x + 1,
        code_y=1,
        code_w=max_x - mid_x - 1,
        code_h=max_y - 2,
        show_line_numbers=True,
        theme='dark',
    )

    header = "Split Screen - test_file_for_features.py (left) vs target file (right) | any key to exit"
    try:
        stdscr.addstr(0, 0, header[:max_x], curses.A_REVERSE | curses.A_BOLD)
    except curses.error:
        pass

    stdscr.refresh()
    stdscr.getch()


def main(stdscr, filepath):
    stdscr.keypad(True)
    example_high_level(stdscr, filepath)
    example_low_level(stdscr, filepath)
    example_split_screen(stdscr, filepath)


if __name__ == '__main__':
    filepath = sys.argv[1] if len(sys.argv) > 1 else __file__
    if not os.path.exists(filepath):
        print(f"Error: File '{filepath}' not found")
        sys.exit(1)
    try:
        curses.wrapper(lambda stdscr: main(stdscr, filepath))
    except KeyboardInterrupt:
        print("\nExited.")
