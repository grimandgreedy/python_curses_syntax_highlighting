#!/usr/bin/env python3
"""Split preview example — shows that the library is a pure renderer.

A main application scrolls a file list with j/k. Pressing o opens a
syntax-highlighted preview on the right half. The main application keeps
full control of key input; the library never reads from the keyboard.

Because preview_text accepts a scroll_offset parameter, the application
can route different keys to different scroll variables — j/k move the
file list, J/K scroll the preview independently.

Controls:
    j / ↓   Scroll file list down
    k / ↑   Scroll file list up
    J / K   Scroll code preview down / up
    o       Toggle code preview panel
    q       Quit
"""

import curses
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from curses_syntax_highlighting import preview_text


def find_files(directory):
    """Return a sorted list of files in directory, recursively up to depth 1."""
    entries = []
    try:
        for name in sorted(os.listdir(directory)):
            path = os.path.join(directory, name)
            if os.path.isfile(path) and not name.startswith('.'):
                entries.append(path)
    except PermissionError:
        pass
    return entries


def draw_file_list(stdscr, files, selected, scroll, panel_w, max_h):
    """Draw the left-side file list."""
    for row in range(max_h):
        idx = scroll + row
        if idx >= len(files):
            break
        name = os.path.basename(files[idx])
        prefix = '> ' if idx == selected else '  '
        line = (prefix + name)[:panel_w - 1]
        attr = curses.A_REVERSE if idx == selected else curses.A_NORMAL
        try:
            stdscr.addstr(row + 1, 0, line.ljust(panel_w - 1), attr)
        except curses.error:
            pass


def main(stdscr, start_dir):
    curses.curs_set(0)
    stdscr.keypad(True)

    files = find_files(start_dir)
    if not files:
        stdscr.addstr(0, 0, f"No files found in {start_dir}")
        stdscr.getch()
        return

    selected = 0
    last_selected = -1
    list_scroll = 0
    preview_open = False
    preview_scroll = 0
    preview_total_lines = 0

    while True:
        stdscr.erase()
        max_y, max_x = stdscr.getmaxyx()
        list_h = max_y - 2  # leave room for header and footer

        # Determine panel widths
        if preview_open:
            list_w = max_x // 2
            preview_x = list_w + 1
            preview_w = max_x - preview_x
        else:
            list_w = max_x
            preview_x = 0
            preview_w = 0

        # Header
        header = f" {start_dir}  |  j/k: scroll   o: {'close' if preview_open else 'open'} preview   q: quit"
        try:
            stdscr.addstr(0, 0, header[:max_x], curses.A_REVERSE | curses.A_BOLD)
        except curses.error:
            pass

        # Reset preview scroll when the selected file changes
        if selected != last_selected:
            preview_scroll = 0
            last_selected = selected

        # Keep selected item visible in the list
        if selected < list_scroll:
            list_scroll = selected
        elif selected >= list_scroll + list_h:
            list_scroll = selected - list_h + 1

        # Left panel: file list
        draw_file_list(stdscr, files, selected, list_scroll, list_w, list_h)

        # Divider
        if preview_open:
            for y in range(1, max_y - 1):
                try:
                    stdscr.addch(y, list_w, curses.ACS_VLINE)
                except curses.error:
                    pass

            # Right panel: syntax-highlighted preview.
            # preview_text is a pure render call — it never reads key input.
            # We pass preview_scroll so the application controls what's visible.
            viewer = preview_text(
                stdscr,
                files[selected],
                code_x=preview_x,
                code_y=1,
                code_w=preview_w,
                code_h=list_h,
                show_line_numbers=True,
                indent_guides=True,
                theme='dark',
                scroll_offset=preview_scroll,
            )
            if viewer:
                preview_total_lines = viewer.total_lines

        # Footer
        preview_info = f"  |  preview line {preview_scroll + 1}/{preview_total_lines}  J/K: scroll preview" if preview_open else ""
        footer = f" {selected + 1}/{len(files)}: {files[selected]}{preview_info}"
        try:
            stdscr.addstr(max_y - 1, 0, footer[:max_x], curses.A_REVERSE)
        except curses.error:
            pass

        stdscr.refresh()

        # ── All key handling is here in the application loop. ──
        # The library has already returned and is not waiting for input.
        key = stdscr.getch()

        if key in (ord('q'), ord('Q'), 27):
            break
        elif key in (ord('j'), curses.KEY_DOWN):
            selected = min(len(files) - 1, selected + 1)
        elif key in (ord('k'), curses.KEY_UP):
            selected = max(0, selected - 1)
        elif key == ord('J') and preview_open:
            # Scroll the preview independently — the app just increments its own variable
            max_preview_scroll = max(0, preview_total_lines - list_h)
            preview_scroll = min(max_preview_scroll, preview_scroll + 1)
        elif key == ord('K') and preview_open:
            preview_scroll = max(0, preview_scroll - 1)
        elif key in (ord('o'), ord('O')):
            preview_open = not preview_open


if __name__ == '__main__':
    start_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(__file__)
    if not os.path.isdir(start_dir):
        print(f"Error: '{start_dir}' is not a directory")
        sys.exit(1)
    try:
        curses.wrapper(lambda stdscr: main(stdscr, start_dir))
    except KeyboardInterrupt:
        print("\nExited.")
