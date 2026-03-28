"""Color themes for syntax highlighting in curses.

This module defines color themes that map Pygments token types to curses color pairs.
Each theme specifies foreground and background colors for different token types.

The background color -1 means "use the terminal's default background color".
"""

import curses
from pygments.token import Token


THEMES = {
    'dark': {
        # Special UI elements (must be first to ensure they're within color pair limit)
        "background": (-1, -1),  # For clearing display area
        "line_number": (curses.COLOR_CYAN, -1),  # Use terminal background
        "indent_guide": (curses.COLOR_BLACK, -1),
        "bracket": (curses.COLOR_YELLOW, -1),  # (), [], {}

        # Base tokens
        Token: (curses.COLOR_WHITE, -1),  # Base token (fallback for all)
        Token.Error: (curses.COLOR_RED, -1),  # Errors

        # Comments
        Token.Comment: (curses.COLOR_GREEN, -1),
        Token.Comment.Preproc: (curses.COLOR_CYAN, -1),  # Preprocessor comments

        # Keywords
        Token.Keyword: (curses.COLOR_MAGENTA, -1),
        Token.Keyword.Constant: (curses.COLOR_MAGENTA, -1),   # True, False, None
        Token.Keyword.Declaration: (curses.COLOR_MAGENTA, -1), # let, fn, pub, class, def
        Token.Keyword.Type: (curses.COLOR_GREEN, -1),          # f64, i32, str, bool
        Token.Keyword.Namespace: (curses.COLOR_MAGENTA, -1),   # import, use, mod

        # Operators and Punctuation
        Token.Operator: (curses.COLOR_CYAN, -1),
        Token.Operator.Word: (curses.COLOR_MAGENTA, -1),  # and, or, not, in
        Token.Punctuation: (curses.COLOR_WHITE, -1),

        # Names (variables, functions, classes, etc.)
        Token.Name: (curses.COLOR_WHITE, -1),  # Generic names
        Token.Name.Attribute: (curses.COLOR_CYAN, -1),  # object.attribute
        Token.Name.Builtin: (curses.COLOR_MAGENTA, -1),  # len, range, etc.
        Token.Name.Builtin.Pseudo: (curses.COLOR_MAGENTA, -1),  # self, cls
        Token.Name.Class: (curses.COLOR_GREEN, -1),   # Class/type names
        Token.Name.Constant: (curses.COLOR_MAGENTA, -1),  # CONSTANTS
        Token.Name.Decorator: (curses.COLOR_CYAN, -1),  # @decorator
        Token.Name.Exception: (curses.COLOR_RED, -1),  # Exception names
        Token.Name.Function: (curses.COLOR_CYAN, -1),  # Function names
        Token.Name.Function.Magic: (curses.COLOR_MAGENTA, -1),  # __init__, __str__
        Token.Name.Namespace: (curses.COLOR_CYAN, -1),  # Module names
        Token.Name.Tag: (curses.COLOR_BLUE, -1),  # HTML/XML tags
        Token.Name.Variable.Parameter: (208, -1),  # Function parameters (orange; falls back to yellow)

        # Numbers
        Token.Literal.Number: (curses.COLOR_MAGENTA, -1),

        # Strings
        Token.Literal.String: (curses.COLOR_YELLOW, -1),
        Token.Literal.String.Doc: (curses.COLOR_GREEN, -1),  # Docstrings
        Token.Literal.String.Escape: (curses.COLOR_CYAN, -1),  # \n, \t, etc.
        Token.Literal.String.Interpol: (curses.COLOR_CYAN, -1),  # f-string interpolation

        # Generic (used in diffs, markdown, etc.)
        Token.Generic.Deleted: (curses.COLOR_RED, -1),
        Token.Generic.Heading: (curses.COLOR_CYAN, -1),
        Token.Generic.Inserted: (curses.COLOR_GREEN, -1),
        Token.Generic.Subheading: (curses.COLOR_BLUE, -1),
    },
    'light': {
        # Special UI elements (must be first to ensure they're within color pair limit)
        "background": (-1, -1),  # For clearing display area
        "line_number": (curses.COLOR_BLUE, -1),  # Use terminal background
        "indent_guide": (curses.COLOR_WHITE, -1),
        "bracket": (curses.COLOR_BLUE, -1),  # (), [], {}

        # Base tokens
        Token: (curses.COLOR_BLACK, -1),  # Base token (fallback for all)
        Token.Error: (curses.COLOR_RED, -1),  # Errors

        # Comments
        Token.Comment: (curses.COLOR_GREEN, -1),
        Token.Comment.Preproc: (curses.COLOR_CYAN, -1),  # Preprocessor comments

        # Keywords
        Token.Keyword: (curses.COLOR_BLUE, -1),
        Token.Keyword.Constant: (curses.COLOR_MAGENTA, -1),   # True, False, None
        Token.Keyword.Declaration: (curses.COLOR_BLUE, -1),   # let, fn, pub, class, def
        Token.Keyword.Type: (curses.COLOR_GREEN, -1),         # f64, i32, str, bool
        Token.Keyword.Namespace: (curses.COLOR_BLUE, -1),     # import, use, mod

        # Operators and Punctuation
        Token.Operator: (curses.COLOR_CYAN, -1),
        Token.Operator.Word: (curses.COLOR_BLUE, -1),  # and, or, not, in
        Token.Punctuation: (curses.COLOR_BLACK, -1),

        # Names (variables, functions, classes, etc.)
        Token.Name: (curses.COLOR_BLACK, -1),  # Generic names
        Token.Name.Attribute: (curses.COLOR_CYAN, -1),  # object.attribute
        Token.Name.Builtin: (curses.COLOR_MAGENTA, -1),  # len, range, etc.
        Token.Name.Builtin.Pseudo: (curses.COLOR_MAGENTA, -1),  # self, cls
        Token.Name.Class: (curses.COLOR_GREEN, -1),  # Class/type names
        Token.Name.Constant: (curses.COLOR_MAGENTA, -1),  # CONSTANTS
        Token.Name.Decorator: (curses.COLOR_CYAN, -1),  # @decorator
        Token.Name.Exception: (curses.COLOR_RED, -1),  # Exception names
        Token.Name.Function: (curses.COLOR_CYAN, -1),  # Function names
        Token.Name.Function.Magic: (curses.COLOR_MAGENTA, -1),  # __init__, __str__
        Token.Name.Namespace: (curses.COLOR_CYAN, -1),  # Module names
        Token.Name.Tag: (curses.COLOR_BLUE, -1),  # HTML/XML tags
        Token.Name.Variable.Parameter: (208, -1),  # Function parameters (orange; falls back to yellow)

        # Numbers
        Token.Literal.Number: (curses.COLOR_MAGENTA, -1),

        # Strings
        Token.Literal.String: (curses.COLOR_RED, -1),
        Token.Literal.String.Doc: (curses.COLOR_GREEN, -1),  # Docstrings
        Token.Literal.String.Escape: (curses.COLOR_CYAN, -1),  # \n, \t, etc.
        Token.Literal.String.Interpol: (curses.COLOR_CYAN, -1),  # f-string interpolation

        # Generic (used in diffs, markdown, etc.)
        Token.Generic.Deleted: (curses.COLOR_RED, -1),
        Token.Generic.Heading: (curses.COLOR_CYAN, -1),
        Token.Generic.Inserted: (curses.COLOR_GREEN, -1),
        Token.Generic.Subheading: (curses.COLOR_BLUE, -1),
    }
}


def get_theme(theme_name, bg_color=None):
    """Get a theme by name with optional background color override.

    Args:
        theme_name: Name of the theme ('dark' or 'light')
        bg_color: Optional background color to override theme default.
                  Use -1 for terminal default, or a curses color number.

    Returns:
        dict: Theme dictionary mapping tokens to (fg, bg) color pairs
    """
    theme = THEMES.get(theme_name, THEMES['dark']).copy()

    # Override background color if specified
    if bg_color is not None:
        theme = {}
        base_theme = THEMES.get(theme_name, THEMES['dark'])
        for token, (fg, bg) in base_theme.items():
            # Don't override line_number background
            if token == "line_number":
                theme[token] = (fg, bg)
            else:
                theme[token] = (fg, bg_color)

    return theme
