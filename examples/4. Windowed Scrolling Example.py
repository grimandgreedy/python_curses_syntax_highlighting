#!/usr/bin/env python3
"""Windowed scrolling example for curses_syntax.

This example demonstrates scrolling through a file in a centered window:
- Window is half the terminal width and 3/4 the terminal height
- Positioned at 1/4 width and 1/8 height
- Has a border around it
- Arrow keys (UP/DOWN) and j/k for vim-style navigation
- Toggle between wrap and truncate modes with 'w'
- q to quit
"""

import curses
import sys
import os

# Add parent directory to path so we can import curses_syntax_highlighting
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from curses_syntax_highlighting import LazyFileViewer, get_lexer, init_colors, display_code


def draw_border(stdscr, x, y, w, h, title=""):
    """Draw a border around a region with optional title.

    Args:
        stdscr: Curses window
        x: X position of border
        y: Y position of border
        w: Width of border
        h: Height of border
        title: Optional title to display in top border
    """
    try:
        # Draw corners
        stdscr.addch(y, x, curses.ACS_ULCORNER)
        stdscr.addch(y, x + w - 1, curses.ACS_URCORNER)
        stdscr.addch(y + h - 1, x, curses.ACS_LLCORNER)
        stdscr.addch(y + h - 1, x + w - 1, curses.ACS_LRCORNER)

        # Draw horizontal lines
        for i in range(1, w - 1):
            stdscr.addch(y, x + i, curses.ACS_HLINE)
            stdscr.addch(y + h - 1, x + i, curses.ACS_HLINE)

        # Draw vertical lines
        for i in range(1, h - 1):
            stdscr.addch(y + i, x, curses.ACS_VLINE)
            stdscr.addch(y + i, x + w - 1, curses.ACS_VLINE)

        # Add title if provided
        if title:
            title_text = f" {title} "
            title_x = x + (w - len(title_text)) // 2
            if title_x > x and title_x + len(title_text) < x + w:
                stdscr.addstr(y, title_x, title_text, curses.A_BOLD)
    except curses.error:
        pass


def main(stdscr, filepath):

    # Initialize curses settings
    curses.curs_set(0)  # Hide cursor
    stdscr.clear()
    stdscr.keypad(True)  # Enable keypad mode for arrow keys

    # Get screen dimensions
    max_y, max_x = stdscr.getmaxyx()

    # Calculate window dimensions and position
    # Window: 1/2 width, 3/4 height
    # Position: 1/4 width, 1/8 height
    window_w = max_x // 2
    window_h = (max_y * 3) // 4
    window_x = max_x // 4
    window_y = max_y // 8

    # Calculate code display area (inside the border)
    border_padding = 1
    code_x = window_x + border_padding
    code_y = window_y + border_padding + 1  # +1 for title bar
    code_w = window_w - (border_padding * 2)
    code_h = window_h - (border_padding * 2) - 2  # -2 for title and status bars

    # Initialize the lexer and viewer
    lexer = get_lexer(filepath)
    viewer = LazyFileViewer(filepath, lexer, block_size=code_h)

    # Initialize colors
    token_to_color = init_colors('dark')

    # Scrolling state
    scroll_offset = 0
    max_scroll = max(0, viewer.total_lines - code_h)
    wrap_mode = False  # Toggle between wrap and truncate

    def draw_ui():
        """Draw the UI including border, code, and status."""
        # Clear screen
        stdscr.clear()

        # Draw background instructions
        instructions = [
            "Windowed Scrolling Example",
            "",
            "The syntax-highlighted code is displayed in a window:",
            f"  • Size: {window_w} × {window_h} (1/2 width × 3/4 height)",
            f"  • Position: ({window_x}, {window_y}) (1/4 width, 1/8 height)",
            f"  • Mode: {'WRAP' if wrap_mode else 'TRUNCATE'}",
            "",
            "Controls:",
            "  ↑/↓ or j/k  - Scroll line by line",
            "  PgUp/PgDn   - Scroll by page",
            "  Home/End    - Jump to top/bottom",
            "  w           - Toggle wrap/truncate mode",
            "  q or ESC    - Quit",
        ]

        for i, line in enumerate(instructions):
            if i < max_y:
                try:
                    stdscr.addstr(i, 2, line[:max_x - 4])
                except curses.error:
                    pass

        # Draw window border with title
        filename = os.path.basename(filepath)
        draw_border(stdscr, window_x, window_y, window_w, window_h, filename)

        # Draw internal title bar
        title_bar_y = window_y + 1
        try:
            stdscr.addstr(title_bar_y, code_x, " " * code_w, curses.A_REVERSE)
            help_text = "↑/↓ j/k: scroll | w: toggle wrap | q: quit"
            stdscr.addstr(title_bar_y, code_x, help_text[:code_w], curses.A_REVERSE)
        except curses.error:
            pass

        # Display the code
        display_code(
            stdscr=stdscr,
            viewer=viewer,
            token_to_color=token_to_color,
            code_x=code_x,
            code_y=code_y,
            code_w=code_w,
            code_h=code_h,
            show_line_numbers=True,
            indent_guides=True,
            scroll_offset=scroll_offset,
            wrap=wrap_mode
        )

        # Draw status bar at bottom of window
        status_bar_y = window_y + window_h - 2
        position_pct = 0 if viewer.total_lines == 0 else int((scroll_offset / max(1, viewer.total_lines - 1)) * 100)
        mode_text = "WRAP" if wrap_mode else "TRUNC"
        status = f"Lines {scroll_offset + 1}-{min(scroll_offset + code_h, viewer.total_lines)} of {viewer.total_lines} ({position_pct}%) | Mode: {mode_text}"
        try:
            stdscr.addstr(status_bar_y, code_x, " " * code_w, curses.A_REVERSE)
            stdscr.addstr(status_bar_y, code_x, status[:code_w], curses.A_REVERSE)
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
        elif key in [ord('w'), ord('W')]:  # w - toggle wrap mode
            wrap_mode = not wrap_mode
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
    default = os.path.join(os.path.dirname(__file__), 'test_file_for_features.py')
    filepath = sys.argv[1] if len(sys.argv) > 1 else default
    if not os.path.exists(filepath):
        print(f"Error: File '{filepath}' not found")
        sys.exit(1)
    try:
        curses.wrapper(lambda stdscr: main(stdscr, filepath))
    except KeyboardInterrupt:
        print("\nExited.")
