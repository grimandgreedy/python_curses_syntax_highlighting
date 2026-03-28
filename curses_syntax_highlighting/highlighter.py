"""Core syntax highlighting functions for curses.

This module provides functions to initialize color pairs and map
Pygments tokens to curses color attributes.
"""

import curses
from .themes import get_theme


def init_colors(theme_name='dark', start_color_id=200, bg_color=None):
    """Initialize color pairs for syntax highlighting.

    This function must be called after curses.initscr() and before
    displaying any syntax-highlighted text.

    Args:
        theme_name: Name of the theme to use ('dark' or 'light')
        start_color_id: Starting color pair ID (default: 200)
        bg_color: Optional background color override. Use -1 for terminal
                  default (recommended), or a curses color number (0-255).
                  If None, uses theme default (-1 for terminal background).

    Returns:
        dict: Mapping from token types to curses color pair attributes
    """
    curses.start_color()
    curses.use_default_colors()
    theme = get_theme(theme_name, bg_color)

    color_id = start_color_id
    token_to_color = {}

    for token, (fg, bg) in theme.items():
        # Clamp extended 256-color values to what the terminal supports.
        # -1 means terminal default and is always valid.
        if fg != -1 and fg >= curses.COLORS:
            fg = curses.COLOR_YELLOW  # fallback for orange (208) on 8-color terminals
        if bg != -1 and bg >= curses.COLORS:
            bg = -1
        curses.init_pair(color_id, fg, bg)
        token_to_color[token] = curses.color_pair(color_id)
        color_id += 1

    return token_to_color


def get_color_for_token(token_type, token_to_color):
    """Get the curses color attribute for a Pygments token type.

    This function traverses the token type hierarchy to find the most
    specific color mapping available.

    Args:
        token_type: Pygments token type
        token_to_color: Mapping from token types to color attributes

    Returns:
        int: Curses color pair attribute for the token
    """
    while token_type not in token_to_color and token_type.parent:
        token_type = token_type.parent
    # Fallback to "background" color if token not found, then curses.color_pair(0)
    return token_to_color.get(token_type, token_to_color.get("background", curses.color_pair(0)))
