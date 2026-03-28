import curses
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from curses_syntax_highlighting import preview_text


def main(stdscr, filepath):
    
    ## Simply use the preview text function to preview text
    preview_text(stdscr, filepath)
    stdscr.getch()


if __name__ == '__main__':
    filepath = sys.argv[1] if len(sys.argv) > 1 else __file__
    if not os.path.exists(filepath):
        print(f"Error: File '{filepath}' not found")
        sys.exit(1)



    curses.wrapper(lambda stdscr: main(stdscr, filepath))
