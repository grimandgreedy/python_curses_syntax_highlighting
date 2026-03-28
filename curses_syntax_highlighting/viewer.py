"""Lazy file viewer for efficient syntax-highlighted file display.

This module provides a LazyFileViewer class that loads and tokenizes
file content on-demand in blocks, optimizing memory usage for large files.
"""

from pygments import lex
from pygments.lexers import guess_lexer_for_filename, get_lexer_by_name, TextLexer
from pygments.token import Token


def _relabel_tokens(tokens):
    """Re-label tokens to improve highlighting beyond what Pygments provides.

    Handles three cases:
    - Function parameters in signatures → Token.Name.Variable.Parameter (orange)
    - Parameter names reused in the function body → Token.Name.Variable.Parameter (orange)
    - Name before '::' (namespace/type path) → Token.Name.Class (green)
    - Name after '::' (enum variant/associated item) → Token.Name.Tag (blue)
    """
    # Pass 1: collect all parameter names declared in function signatures.
    param_names = set()
    state = 'normal'
    paren_depth = 0
    for ttype, value in tokens:
        if state == 'normal':
            if ttype in Token.Name.Function:
                state = 'after_func'
        elif state == 'after_func':
            if value == '(':
                state = 'in_params'
                paren_depth = 1
            elif ttype not in Token.Text and ttype not in Token.Comment:
                state = 'normal'
        elif state == 'in_params':
            if value == '(':
                paren_depth += 1
            elif value == ')':
                paren_depth -= 1
                if paren_depth == 0:
                    state = 'normal'
            elif ttype is Token.Name and paren_depth == 1:
                param_names.add(value)

    # Pass 2: relabel tokens.
    result = []
    state = 'normal'
    paren_depth = 0
    last_name_idx = -1   # index into result of the most recent plain Token.Name
    after_coloncolon = False  # next Name token is an enum variant / associated item

    for ttype, value in tokens:
        # Path separator '::' — retroactively make the preceding name a type,
        # and flag the next name as an enum variant.
        if ttype is Token.Punctuation and value == '::':
            if last_name_idx >= 0:
                old_t, old_v = result[last_name_idx]
                if old_t is Token.Name:
                    result[last_name_idx] = (Token.Name.Class, old_v)
            after_coloncolon = True
            last_name_idx = -1
            result.append((ttype, value))
            continue

        # Maintain function-signature state for parameter detection.
        if state == 'normal':
            if ttype in Token.Name.Function:
                state = 'after_func'
        elif state == 'after_func':
            if value == '(':
                state = 'in_params'
                paren_depth = 1
            elif ttype not in Token.Text and ttype not in Token.Comment:
                state = 'normal'
        elif state == 'in_params':
            if value == '(':
                paren_depth += 1
            elif value == ')':
                paren_depth -= 1
                if paren_depth == 0:
                    state = 'normal'

        if ttype is Token.Name:
            if after_coloncolon:
                ttype = Token.Name.Tag          # enum variant / associated item → blue
                after_coloncolon = False
                last_name_idx = -1
            elif state == 'in_params' and paren_depth == 1:
                ttype = Token.Name.Variable.Parameter   # parameter in signature → orange
                last_name_idx = len(result)
            elif value in param_names:
                ttype = Token.Name.Variable.Parameter   # parameter used in body → orange
                last_name_idx = -1
            else:
                last_name_idx = len(result)
        elif ttype not in Token.Text and ttype not in Token.Comment:
            # Any significant non-name token resets the :: lookahead.
            if after_coloncolon:
                after_coloncolon = False

        result.append((ttype, value))

    return result


def get_lexer(filepath):
    """Guess the appropriate Pygments lexer for a file.

    Args:
        filepath: Path to the file to analyze

    Returns:
        Lexer: Pygments lexer instance for the file
    """
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            sample = f.read(2048)
        return guess_lexer_for_filename(filepath, sample)
    except Exception:
        return TextLexer()


class LazyFileViewer:
    """Efficiently view large files with syntax highlighting.

    This class loads and tokenizes file content in blocks, caching the results
    for efficient scrolling through large files.

    Attributes:
        filepath: Path to the file being viewed
        lexer: Pygments lexer for syntax highlighting
        block_size: Number of lines to load per block
        line_cache: Cache of tokenized lines
        total_lines: Total number of lines in the file
    """

    def __init__(self, filepath, lexer, block_size=50):
        """Initialize the file viewer.

        Args:
            filepath: Path to the file to view
            lexer: Pygments lexer for syntax highlighting
            block_size: Number of lines to load per block (default: 50)
        """
        self.filepath = filepath
        self.lexer = lexer
        self.block_size = block_size
        self.line_cache = {}  # line_number -> list[(char, token_type)]
        self.total_lines = self._count_lines()

    def _count_lines(self):
        """Count the total number of lines in the file.

        Returns:
            int: Total number of lines
        """
        with open(self.filepath, 'r', encoding='utf-8', errors='replace') as f:
            return sum(1 for _ in f)

    def get_lines(self, start_line, num_lines):
        """Get a range of tokenized lines.

        Lines are loaded and cached on-demand. If a line is not in the cache,
        the entire block containing it is loaded.

        Args:
            start_line: Starting line number (0-indexed)
            num_lines: Number of lines to retrieve

        Returns:
            list: List of tokenized lines, where each line is a list of
                  (char, token_type) tuples
        """
        lines = []
        needed_lines = range(start_line, start_line + num_lines)

        for line_num in needed_lines:
            if line_num >= self.total_lines:
                break
            if line_num not in self.line_cache:
                self._load_block_containing(line_num)
            lines.append(self.line_cache.get(line_num, []))

        return lines

    def _load_block_containing(self, line_number):
        """Load and tokenize a block of lines containing the specified line.

        Args:
            line_number: Line number that must be included in the block
        """
        block_start = (line_number // self.block_size) * self.block_size
        block_end = min(block_start + self.block_size, self.total_lines)

        # Read block of lines
        block_lines = []
        with open(self.filepath, 'r', encoding='utf-8', errors='replace') as f:
            for i, line in enumerate(f):
                if i < block_start:
                    continue
                if i >= block_end:
                    break
                block_lines.append(line)

        block_text = ''.join(block_lines)
        tokens = _relabel_tokens(list(lex(block_text, self.lexer)))

        # Split tokens into lines
        current_line = 0
        line_tokens = [[]]
        for ttype, value in tokens:
            for ch in value:
                if ch == '\n':
                    line_tokens.append([])
                    current_line += 1
                else:
                    if current_line >= len(line_tokens):
                        line_tokens.append([])
                    line_tokens[current_line].append((ch, ttype))

        # Store in cache
        for i, tok_line in enumerate(line_tokens):
            absolute_line = block_start + i
            if absolute_line < self.total_lines:
                self.line_cache[absolute_line] = tok_line


def get_lexer_for_language(language):
    """Get a Pygments lexer by language name or alias.

    Args:
        language: Language name or Pygments alias (e.g. 'python', 'rust', 'javascript').
                  Pass None for plain text with no highlighting.

    Returns:
        Lexer: Pygments lexer instance.
    """
    if not language:
        return TextLexer()
    try:
        return get_lexer_by_name(language)
    except Exception:
        return TextLexer()


class TextViewer:
    """View syntax-highlighted text from a string rather than a file.

    Tokenizes the entire text upfront and stores it in memory.
    Provides the same get_lines() interface as LazyFileViewer so it works
    transparently with display_code().

    Attributes:
        total_lines: Total number of lines in the text.
    """

    def __init__(self, text, lexer):
        """Initialize the viewer from a string.

        Args:
            text: The source text to highlight.
            lexer: Pygments lexer to use for tokenization.
        """
        self._lines = []
        self._tokenize(text, lexer)
        self.total_lines = len(self._lines)

    def _tokenize(self, text, lexer):
        tokens = _relabel_tokens(list(lex(text, lexer)))
        current = []
        for ttype, value in tokens:
            for ch in value:
                if ch == '\n':
                    self._lines.append(current)
                    current = []
                else:
                    current.append((ch, ttype))
        if current:
            self._lines.append(current)

    def get_lines(self, start_line, num_lines):
        """Get a range of tokenized lines.

        Args:
            start_line: Starting line number (0-indexed).
            num_lines: Number of lines to retrieve.

        Returns:
            list: List of tokenized lines, where each line is a list of
                  (char, token_type) tuples.
        """
        return self._lines[start_line:start_line + num_lines]
