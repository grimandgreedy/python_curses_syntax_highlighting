"""Python Curses Syntax Highlighting

A library for displaying syntax-highlighted code in terminal applications
using Python's curses library and Pygments for lexing.

Basic usage:
    import curses
    from curses_syntax_highlighting import preview_text

    def main(stdscr):
        preview_text(stdscr, 'myfile.py', show_line_numbers=True)

    curses.wrapper(main)
"""

__version__ = '0.1.0'
__author__ = 'Grim'

# Public API
from .themes import THEMES, get_theme
from .highlighter import init_colors, get_color_for_token
from .viewer import LazyFileViewer, TextViewer, get_lexer, get_lexer_for_language
from .display import display_code, preview_text, preview_string

__all__ = [
    'THEMES',
    'get_theme',
    'init_colors',
    'get_color_for_token',
    'LazyFileViewer',
    'TextViewer',
    'get_lexer',
    'get_lexer_for_language',
    'display_code',
    'preview_text',
    'preview_string',
]
