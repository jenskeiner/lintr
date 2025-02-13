### General
- pytest is used for unit testing.
- When implementing tests, always consider which existing and new fixtures are needed.
- Always analyse exisiting fixtures to understand the capabilities of the fixtures and how they help with your task.
- Always try to re-use or extend an existing fixture before considering adding a new one.
- Avoid creating fixtures with a lot of functional overlap.
- When writing tests for a functionality target 100% branch coverage.
- When mocking properties in Python unit tests:
  - Use `PropertyMock` from `unittest.mock` to mock properties correctly.
  - Set the mock on the type of the object using `type(obj).property_name = PropertyMock(...)` instead of directly on the instance.
  - This ensures that property behavior (like raising exceptions) works correctly in tests.
- When testing code that relies on environment variablesuse pytest's `monkeypatch` fixture instead of directly modifying `os.environ`.
- Python's coverage tool has limitations in recognizing coverage of exception handling blocks
- Configure coverage tool via `.coveragerc` to enable branch coverage and set appropriate exclusion rules.
- Write explicit test cases for each branch condition and error path.
- Sometimes remaining "uncovered" lines in exception blocks can be ignored if tests verify the behavior.
- Use `pytest.raises()` to test for expected exceptions like `SystemExit`
- When trying to improve test coverage always measure coverage before and after adding tests to verify improvement.
- When using `monkeypatch` in pytest, ensure that the path to the mocked attribute matches the actual import path in the code.
- When mocking a class method, ensure the method exists in the class before attempting to mock it.
- When mocking instance methods, remember to include `self` as the first parameter in the mock function.
- When testing code that uses singletons:
   - Mock the singleton class itself, not its instance methods.
   - Use pytest fixtures to ensure consistent mocking across test functions.
   - Mock at the point where the singleton is imported, not where it's instantiated.
   - Reset singleton state between tests if necessary.
- When testing rule execution:
   - CUse the existing `rule_cls` fixture to create mock rule classes with the desired behaviour.
   - Test both successful and error cases for rule execution.
- When mocking entry points in tests, use `unittest.mock.MagicMock` instead of dynamic type creation. MagicMock provides better control over method behavior and makes test failures more debuggable.

### GitHub API Interactions
When mocking GitHub API properties, use `PropertyMock` from `unittest.mock` to mock properties that are accessed via the dot notation (e.g., `repository.has_wiki`); see also above.
Example:
```python
# Incorrect:
mock_repo.has_wiki = MagicMock(side_effect=GithubException(500, "API Error"))

# Correct:
type(mock_repo).has_wiki = PropertyMock(side_effect=GithubException(500, "API Error"))
```
