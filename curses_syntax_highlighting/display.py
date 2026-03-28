"""Display functions for rendering syntax-highlighted code in curses.

This module provides high-level functions for displaying syntax-highlighted
code in a curses window, with optional features like line numbers and indent guides.
"""

import curses
import os
from wcwidth import wcwidth

from .highlighter import init_colors, get_color_for_token
from .viewer import LazyFileViewer, TextViewer, get_lexer, get_lexer_for_language
from pygments.token import Comment, Literal

_BRACKETS = frozenset('()[]{}')


def _get_char_color(ch, ttype, token_to_color):
    if ch in _BRACKETS and not (ttype is Comment or ttype in Comment or ttype in Literal.String):
        bracket_color = token_to_color.get("bracket")
        if bracket_color is not None:
            return bracket_color
    return get_color_for_token(ttype, token_to_color)


def display_code(
    stdscr,
    viewer,
    token_to_color,
    code_x,
    code_y,
    code_w,
    code_h,
    show_line_numbers,
    indent_guides,
    scroll_offset=0,
    wrap=False
):
    """Display syntax-highlighted code in a curses window.

    Args:
        stdscr: Curses window object
        viewer: LazyFileViewer instance
        token_to_color: Token-to-color mapping from init_colors()
        code_x: X coordinate of display area
        code_y: Y coordinate of display area
        code_w: Width of display area
        code_h: Height of display area
        show_line_numbers: Whether to show line numbers
        indent_guides: Whether to show indent guides
        scroll_offset: Line number to start displaying from (default: 0)
        wrap: Whether to wrap long lines (default: False, truncate instead)
    """
    curses.curs_set(0)
    max_y, max_x = stdscr.getmaxyx()

    # Get background color for clearing display area
    bg_color_attr = token_to_color.get("background", curses.color_pair(0))

    # Clear the display area with the background color
    for i in range(code_h):
        try:
            stdscr.addstr(code_y + i, code_x, ' ' * min(code_w, max_x - code_x), bg_color_attr)
        except curses.error:
            pass

    # Calculate line number width
    num_lines = viewer.total_lines
    line_num_width = (len(str(num_lines)) + 2) if show_line_numbers else 0

    # Calculate available width for code content
    content_width = code_w - line_num_width

    # Get visible lines
    visible = viewer.get_lines(scroll_offset, code_h)

    display_row = 0  # Track which display row we're on

    for idx, line in enumerate(visible):
        if display_row >= code_h:
            break

        y = code_y + display_row
        if y >= max_y or y >= code_y + code_h:
            break

        x = code_x

        # Draw line numbers (only on first row of wrapped line)
        if show_line_numbers:
            ln = str(scroll_offset + idx + 1).rjust(line_num_width - 1) + " "
            ln_color = token_to_color.get("line_number", curses.color_pair(0))
            try:
                stdscr.addstr(y, x, ln[:min(line_num_width, max_x - x)], ln_color)
            except curses.error:
                pass
            x += line_num_width

        # Draw code with syntax highlighting
        if wrap:
            # Wrapping mode: continue on next lines if content exceeds width
            col = 0
            char_idx = 0
            in_leading_whitespace = True  # Track if we're still in leading whitespace

            while char_idx < len(line):
                if display_row >= code_h:
                    break

                y = code_y + display_row
                if y >= max_y or y >= code_y + code_h:
                    break

                # For continuation lines, fill line number area with spaces
                if col >= content_width and char_idx < len(line):
                    display_row += 1
                    col = 0
                    in_leading_whitespace = False  # Wrapped lines are not leading whitespace
                    if display_row >= code_h:
                        break
                    y = code_y + display_row
                    if y >= max_y or y >= code_y + code_h:
                        break
                    x = code_x

                    # Draw empty line number area for wrapped continuation
                    if show_line_numbers:
                        try:
                            stdscr.addstr(y, x, " " * line_num_width, bg_color_attr)
                        except curses.error:
                            pass
                        x += line_num_width

                if char_idx >= len(line):
                    break

                ch, ttype = line[char_idx]
                width = wcwidth(ch)
                if width < 0:
                    width = 0  # unprintable

                # Check if character fits in current line
                if col + width > content_width:
                    # Move to next line
                    display_row += 1
                    col = 0
                    in_leading_whitespace = False  # Wrapped content is not leading whitespace
                    continue

                # Track leading whitespace - once we see a non-space, we're done
                if ch != ' ' and ch != '\t':
                    in_leading_whitespace = False

                try:
                    # Only draw indent guides in leading whitespace
                    if indent_guides and in_leading_whitespace and ch == ' ' and (col % 4 == 0) and col + width <= content_width:
                        guide = token_to_color.get("indent_guide", curses.color_pair(0))
                        stdscr.addstr(y, x + col, '│', guide)
                    else:
                        color = _get_char_color(ch, ttype, token_to_color)
                        stdscr.addstr(y, x + col, ch, color)
                except curses.error:
                    pass

                col += width
                char_idx += 1

            display_row += 1

        else:
            # Truncate mode: stop at width boundary
            col = 0
            in_leading_whitespace = True  # Track if we're still in leading whitespace

            for ch, ttype in line:
                width = wcwidth(ch)
                if width < 0:
                    width = 0  # unprintable

                # Check boundary: respect code_w, not max_x
                if col + width > content_width:
                    break

                # Track leading whitespace - once we see a non-space, we're done
                if ch != ' ' and ch != '\t':
                    in_leading_whitespace = False

                try:
                    # Only draw indent guides in leading whitespace
                    if indent_guides and in_leading_whitespace and ch == ' ' and (col % 4 == 0):
                        guide = token_to_color.get("indent_guide", curses.color_pair(0))
                        stdscr.addstr(y, x + col, '│', guide)
                    else:
                        color = _get_char_color(ch, ttype, token_to_color)
                        stdscr.addstr(y, x + col, ch, color)
                except curses.error:
                    pass

                col += width

            display_row += 1

    stdscr.refresh()


def preview_text(
    stdscr,
    filepath,
    code_x=0,
    code_y=0,
    code_w=None,
    code_h=None,
    show_line_numbers=False,
    indent_guides=False,
    theme="dark",
    wrap=False,
    bg_color=None,
    scroll_offset=0
):
    """Display a syntax-highlighted preview of a text file.

    This is the main high-level function for displaying a file with
    syntax highlighting.

    Args:
        stdscr: Curses window object
        filepath: Path to the file to preview
        code_x: X coordinate of display area (default: 0)
        code_y: Y coordinate of display area (default: 0)
        code_w: Width of display area (default: remaining width)
        code_h: Height of display area (default: remaining height)
        show_line_numbers: Whether to show line numbers (default: False)
        indent_guides: Whether to show indent guides (default: False)
        theme: Color theme to use ('dark' or 'light', default: 'dark')
        wrap: Whether to wrap long lines (default: False, truncate instead)
        bg_color: Optional background color override. Use -1 for terminal
                  default (recommended), or a curses color number (0-255).
                  If None, uses theme default (-1 for terminal background).
        scroll_offset: Line number to start displaying from (default: 0)

    Returns:
        LazyFileViewer: The viewer instance (access viewer.total_lines for line count)
                        Returns None on error (file not found, etc.)
    """
    try:
        if not os.path.isfile(filepath):
            return None

        lexer = get_lexer(filepath)

        max_y, max_x = stdscr.getmaxyx()

        if code_w is None:
            code_w = max_x - code_x
        if code_h is None:
            code_h = max_y - code_y

        viewer = LazyFileViewer(filepath, lexer, block_size=code_h)
        token_to_color = init_colors(theme, bg_color=bg_color)

        display_code(
            stdscr=stdscr,
            viewer=viewer,
            token_to_color=token_to_color,
            code_x=code_x,
            code_y=code_y,
            code_w=code_w,
            code_h=code_h,
            show_line_numbers=show_line_numbers,
            indent_guides=indent_guides,
            scroll_offset=scroll_offset,
            wrap=wrap,
        )

        return viewer
    except Exception:
        return None


def preview_string(
    stdscr,
    text,
    language=None,
    code_x=0,
    code_y=0,
    code_w=None,
    code_h=None,
    show_line_numbers=False,
    indent_guides=False,
    theme="dark",
    wrap=False,
    bg_color=None,
    scroll_offset=0,
):
    """Display a syntax-highlighted preview of a plain-text string.

    Args:
        stdscr: Curses window object.
        text: The source text to display.
        language: Pygments language alias for syntax highlighting, e.g. 'python',
                  'rust', 'javascript'. Pass None for plain text with no highlighting.
        code_x: X coordinate of display area (default: 0).
        code_y: Y coordinate of display area (default: 0).
        code_w: Width of display area (default: remaining width).
        code_h: Height of display area (default: remaining height).
        show_line_numbers: Whether to show line numbers (default: False).
        indent_guides: Whether to show indent guides (default: False).
        theme: Color theme ('dark' or 'light', default: 'dark').
        wrap: Whether to wrap long lines (default: False).
        bg_color: Background color override. Use -1 or None for terminal default.
        scroll_offset: Line number to start displaying from (default: 0).

    Returns:
        TextViewer: The viewer instance (access viewer.total_lines for line count).
    """
    lexer = get_lexer_for_language(language)

    max_y, max_x = stdscr.getmaxyx()
    if code_w is None:
        code_w = max_x - code_x
    if code_h is None:
        code_h = max_y - code_y

    viewer = TextViewer(text, lexer)
    token_to_color = init_colors(theme, bg_color=bg_color)

    display_code(
        stdscr=stdscr,
        viewer=viewer,
        token_to_color=token_to_color,
        code_x=code_x,
        code_y=code_y,
        code_w=code_w,
        code_h=code_h,
        show_line_numbers=show_line_numbers,
        indent_guides=indent_guides,
        scroll_offset=scroll_offset,
        wrap=wrap,
    )

    return viewer
