#!/usr/bin/env python3
"""Basic scrolling example using only preview_text.

This example demonstrates how to use ONLY the high-level preview_text function
to create an interactive file viewer with:
- Scrolling (↑/↓, j/k, Page Up/Down, Home/End)
- Line number toggling (n)
- Indent guide toggling (i) - best viewed with test_file_for_features.py
- Word wrap toggling (w) - best viewed with test_file_for_features.py
- Theme toggling (t)

By default, displays test_file_for_features.py which has long lines and deep
indentation to demonstrate wrap and indent features clearly.

Usage:
    python basic_scrolling_example.py              # Uses test_file_for_features.py
    python basic_scrolling_example.py myfile.py    # Views any file
"""

import curses
import sys
import os

# Add parent directory to path so we can import curses_syntax_highlighting
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from curses_syntax_highlighting import preview_text


def main(stdscr, custom_file=None):
    """Interactive file viewer using only preview_text."""
    # Use custom file if provided, otherwise default to test file, then this file
    if custom_file:
        filepath = custom_file
    else:
        test_file = os.path.join(os.path.dirname(__file__), 'test_file_for_features.py')
        filepath = test_file if os.path.exists(test_file) else __file__

    # Initialize curses settings
    curses.curs_set(0)  # Hide cursor
    stdscr.clear()
    stdscr.keypad(True)  # Enable keypad mode for arrow keys

    # Get screen dimensions
    max_y, max_x = stdscr.getmaxyx()

    # State variables
    scroll_offset = 0
    show_line_numbers = True
    indent_guides = True
    wrap = False
    theme = 'dark'

    # Get file info without rendering
    from curses_syntax_highlighting import LazyFileViewer, get_lexer
    lexer = get_lexer(filepath)
    temp_viewer = LazyFileViewer(filepath, lexer)
    total_lines = temp_viewer.total_lines

    # Calculate display area (leave room for header and footer)
    header_height = 2
    footer_height = 1
    code_y = header_height
    code_h = max_y - header_height - footer_height
    max_scroll = max(0, total_lines - code_h)

    def draw_ui():
        """Draw the UI with current settings."""
        # Clear screen completely
        stdscr.erase()

        # Draw header with filename
        filename = os.path.basename(filepath)
        header = f"File: {filename} | Lines: {total_lines}"
        try:
            stdscr.addstr(0, 0, " " * max_x)
            stdscr.addstr(0, 0, header[:max_x], curses.A_REVERSE | curses.A_BOLD)
        except curses.error:
            pass

        # Draw controls help
        controls = "n:LineNum  i:Indent  w:Wrap  t:Theme  ↑↓/jk:Scroll  PgUp/Dn  Home/End  q:Quit"
        try:
            stdscr.addstr(1, 0, " " * max_x)
            stdscr.addstr(1, 0, controls[:max_x], curses.A_DIM)
        except curses.error:
            pass

        # Display the code using preview_text
        # Note: preview_text returns a viewer, but we ignore it here since we already have total_lines
        preview_text(
            stdscr,
            filepath,
            code_x=0,
            code_y=code_y,
            code_w=max_x,
            code_h=code_h,
            show_line_numbers=show_line_numbers,
            indent_guides=indent_guides,
            theme=theme,
            wrap=wrap,
            scroll_offset=scroll_offset
        )

        # Draw footer with status
        position_pct = 0 if total_lines == 0 else int((scroll_offset / max(1, total_lines - 1)) * 100)
        status = f"Lines {scroll_offset + 1}-{min(scroll_offset + code_h, total_lines)} ({position_pct}%) | "
        status += f"LineNum:{'ON' if show_line_numbers else 'OFF'} "
        status += f"Indent:{'ON' if indent_guides else 'OFF'} "
        status += f"Wrap:{'ON' if wrap else 'OFF'} "
        status += f"Theme:{theme.upper()}"

        try:
            stdscr.addstr(max_y - 1, 0, " " * max_x)
            stdscr.addstr(max_y - 1, 0, status[:max_x], curses.A_REVERSE)
        except curses.error:
            pass

        stdscr.refresh()

    # Main loop
    while True:
        draw_ui()

        # Get user input
        key = stdscr.getch()

        # Handle key presses
        if key in [ord('q'), ord('Q'), 27]:  # q or ESC to quit
            break
        elif key in [ord('n'), ord('N')]:  # Toggle line numbers
            show_line_numbers = not show_line_numbers
        elif key in [ord('i'), ord('I')]:  # Toggle indent guides
            indent_guides = not indent_guides
        elif key in [ord('w'), ord('W')]:  # Toggle word wrap
            wrap = not wrap
        elif key in [ord('t'), ord('T')]:  # Toggle theme
            theme = 'light' if theme == 'dark' else 'dark'
        elif key in [curses.KEY_UP, ord('k'), ord('K')]:  # Up arrow or k
            scroll_offset = max(0, scroll_offset - 1)
        elif key in [curses.KEY_DOWN, ord('j'), ord('J')]:  # Down arrow or j
            scroll_offset = min(max_scroll, scroll_offset + 1)
        elif key == curses.KEY_PPAGE:  # Page Up
            scroll_offset = max(0, scroll_offset - code_h)
        elif key == curses.KEY_NPAGE:  # Page Down
            scroll_offset = min(max_scroll, scroll_offset + code_h)
        elif key == curses.KEY_HOME:  # Home - go to top
            scroll_offset = 0
        elif key == curses.KEY_END:  # End - go to bottom
            scroll_offset = max_scroll
        elif key in [ord('g')]:  # g - go to top (vim style)
            scroll_offset = 0
        elif key in [ord('G')]:  # Shift+G - go to bottom (vim style)
            scroll_offset = max_scroll


if __name__ == '__main__':
    # Allow specifying a file as command line argument
    custom_file = None
    if len(sys.argv) > 1:
        custom_file = sys.argv[1]
        if not os.path.exists(custom_file):
            print(f"Error: File '{custom_file}' not found")
            print(f"Usage: {sys.argv[0]} [filepath]")
            sys.exit(1)

    try:
        curses.wrapper(lambda stdscr: main(stdscr, custom_file))
    except KeyboardInterrupt:
        print("\nExited.")
