#!/usr/bin/env python3
"""String input example — highlight a code string directly without a file.

Demonstrates preview_string(), which accepts a plain string and a language
name instead of a file path. Useful when the code lives in a variable,
comes from an API, a database, or is generated at runtime.

Controls:
    j / ↓   Scroll down
    k / ↑   Scroll up
    1-5     Switch language example
    q       Quit
"""

import curses
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from curses_syntax_highlighting import preview_string

EXAMPLES = [
    ("python", """\
def greet(name: str) -> str:
    \"\"\"Return a personalised greeting.\"\"\"
    return f"Hello, {name}!"

class Counter:
    def __init__(self, start: int = 0):
        self.value = start

    def increment(self):
        self.value += 1
        return self

    def reset(self):
        self.value = 0

counter = Counter(start=10)
counter.increment().increment()
print(counter.value)  # 12
"""),

    ("rust", """\
use std::collections::HashMap;

struct Cache {
    store: HashMap<String, Vec<f64>>,
}

impl Cache {
    fn new() -> Self {
        Cache { store: HashMap::new() }
    }

    fn insert(&mut self, key: &str, values: Vec<f64>) {
        self.store.insert(key.to_string(), values);
    }

    fn mean(&self, key: &str) -> Option<f64> {
        self.store.get(key).map(|v| {
            v.iter().sum::<f64>() / v.len() as f64
        })
    }
}

fn main() {
    let mut cache = Cache::new();
    cache.insert("temps", vec![36.6, 37.1, 36.9]);
    if let Some(avg) = cache.mean("temps") {
        println!("Average temperature: {:.2}", avg);
    }
}
"""),

    ("javascript", """\
async function fetchUser(id) {
  const response = await fetch(`/api/users/${id}`);
  if (!response.ok) {
    throw new Error(`HTTP error: ${response.status}`);
  }
  return response.json();
}

class EventBus {
  constructor() {
    this.listeners = new Map();
  }

  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event).push(callback);
  }

  emit(event, data) {
    this.listeners.get(event)?.forEach(cb => cb(data));
  }
}

const bus = new EventBus();
bus.on('login', user => console.log(`Welcome, ${user.name}`));
"""),

    ("sql", """\
-- Monthly revenue report with running total
WITH monthly AS (
    SELECT
        DATE_TRUNC('month', created_at)  AS month,
        SUM(amount_cents) / 100.0        AS revenue,
        COUNT(DISTINCT customer_id)      AS customers
    FROM orders
    WHERE status = 'completed'
      AND created_at >= NOW() - INTERVAL '1 year'
    GROUP BY 1
)
SELECT
    month,
    revenue,
    customers,
    SUM(revenue) OVER (ORDER BY month) AS running_total
FROM monthly
ORDER BY month;
"""),

    ("json", """\
{
  "name": "curses-syntax-highlighting",
  "version": "0.1.0",
  "description": "Syntax highlighting for curses TUI applications",
  "dependencies": {
    "pygments": ">=2.0.0",
    "wcwidth": ">=0.2.0"
  },
  "themes": ["dark", "light"],
  "features": [
    "file input",
    "string input",
    "line numbers",
    "indent guides",
    "word wrap"
  ]
}
"""),
]


def main(stdscr):
    curses.curs_set(0)
    stdscr.keypad(True)

    example_idx = 0
    scroll = 0

    while True:
        stdscr.erase()
        max_y, max_x = stdscr.getmaxyx()
        code_h = max_y - 2

        language, code = EXAMPLES[example_idx]

        # Header
        tabs = "  ".join(
            f"[{i+1}:{lang}]" if i == example_idx else f" {i+1}:{lang} "
            for i, (lang, _) in enumerate(EXAMPLES)
        )
        try:
            stdscr.addstr(0, 0, (" " * max_x), curses.A_REVERSE)
            stdscr.addstr(0, 0, tabs[:max_x], curses.A_REVERSE | curses.A_BOLD)
        except curses.error:
            pass

        # Render the string directly — no file involved
        viewer = preview_string(
            stdscr,
            code,
            language=language,
            code_x=0,
            code_y=1,
            code_w=max_x,
            code_h=code_h,
            show_line_numbers=True,
            indent_guides=True,
            theme='dark',
            scroll_offset=scroll,
        )

        max_scroll = max(0, (viewer.total_lines if viewer else 0) - code_h)

        # Footer
        footer = f" j/k: scroll   1-{len(EXAMPLES)}: switch language   q: quit"
        try:
            stdscr.addstr(max_y - 1, 0, " " * max_x, curses.A_REVERSE)
            stdscr.addstr(max_y - 1, 0, footer[:max_x], curses.A_REVERSE)
        except curses.error:
            pass

        key = stdscr.getch()

        if key in (ord('q'), ord('Q'), 27):
            break
        elif key in (ord('j'), curses.KEY_DOWN):
            scroll = min(max_scroll, scroll + 1)
        elif key in (ord('k'), curses.KEY_UP):
            scroll = max(0, scroll - 1)
        elif ord('1') <= key <= ord('0') + len(EXAMPLES):
            new_idx = key - ord('1')
            if new_idx != example_idx:
                example_idx = new_idx
                scroll = 0


if __name__ == '__main__':
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        print("\nExited.")
