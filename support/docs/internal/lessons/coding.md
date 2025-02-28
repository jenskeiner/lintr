### General

- When working with collections of items, use generators (yield) instead of building lists when possible.
- Handle file paths safely using pathlib.
- When implementing singletons in Python, include a way to reset the singleton state in tests. This can e.g. be done via a pytest fixture with `autouse=True` to ensure clean state between tests.

### CLI Implementation
- When implementing a Python CLI tool, create both a dedicated CLI module and a simple `__main__.py` entry point.
- The CLI module should contain all the actual implementation, while `__main__.py` just imports and calls the main function.

### Pattern Matching
- Use Python's built-in `fnmatch` module for glob pattern matching instead of implementing custom pattern matching logic.
- When implementing filtering with both inclusion and exclusion patterns, apply inclusion patterns first, then exclusion patterns.
- Always write test cases that cover different pattern combinations:
   - Only inclusion patterns.
   - Only exclusion patterns.
   - Both inclusion and exclusion patterns.
   - Edge cases like empty pattern lists.

### Output Formatting
- Keep output formatting simple and consistent. E.g. instead of verbose labels like "rule set: default", just use the identifier in parentheses "(default)".
- Use Unicode symbols (✓, ✗, -, ⚡) to provide visual status indicators.
- Maintain a clear visual hierarchy through consistent indentation.
- When showing errors or problems, keep the error messages concise and prefix them with "Error:" for easy identification.
