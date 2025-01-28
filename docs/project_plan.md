# Repolint: Project Plan

## Overview

*Repolint* is a Python-based command-line application to lint and enforce consistent settings across a user's GitHub repositories. The application is:
- *Convenient*: The CLI interface is very easy to use. The terminal output is richt and pleasant, but concise and very readable.
- *Comprehensive*: It supports personal and organizational repositories where the user has admin access.
- *Rule-based*: Pre-defined rules and rule-sets for common project types (e.g., standard Python library packages) are provided.
- *Powerful*: It supports both linting and autofix capabilities.
- *Extensible*: Users can define their own rules by implementing a Python class. Rule-sets can be defined through configuration.

This plan outlines the goals and phases for building Repolint.

## High-Level Architecture

### Core Functionality

- Lint repositories to check for specific conditions based on defined rules.
- Support a configuration file to specify:
  - Target repositories.
  - Custom rule-sets.
- Pre-defined rule-sets for common project types (e.g., standard Python library packages).

### User Interface

- CLI interface for specifying operations.
- Terminal output for presenting results and user feedback.

### Linter

- Represents the main entry point for the application.
- Loads the configuration.
- Discovers available rules and rule-sets.
- Discovers target repositories.
- Executes linting operations and gathers their results on all eligible repositories.
- Reports results to the user.
- Executes auto-fix operations if requested, after prompting the user for confirmation.
- Supports dry-run mode for previewing changes.

### Configuration

- `pydantic_settings` is used to implement a single main configuration class. Subclasses are used where appropriate to separate concerns.
- Valid configuration sources, from lowest to highest priority, are .env file, environment variables, command-line arguments. There must also be one command-line argument that just points to a configuration file that is then consumed.
- Configuration files use YAML format.
- The configuration controls which repositories are target for linting and which rule-sets are used.
- By default, all repositories to which the user has admin access are considered target repositories. a filter can be specified to only target a subset of these.
- A default rule set is used if none is specified in the configuration.
- For each repository, a different rule set can optionally be specified in the configuration.

### Rule Manager

- Discovers available rules and rule-sets.
- Manages and validates the relationship between rules and rule-sets.
- Auxilliary component for the Linter.

### Repo Context

- For each repository, provides the necessary context for each rule that is executed.
- Provides access to repository settings and contents.
- Caches frequently used data to improve performance.
- Acts as an abstraction layer towards the GitHub API.

### Rules

- Rules will check aspects such as:
  - Default branch naming conventions (e.g., `develop` and `main`).
  - Presence and quality of `README.md` files.
- There is an abstract base class for defining the common functionality for all rules.
- Rules have at least the following functionality:
    - Check a repository for a specific condition.
    - Report the result of the check (passed or not, if not why) back to the caller.
    - If available, pass back the suggested fix to the caller.
    - Execute the fix if requested.
- Concrete rules are subclasses of the abstract base class.
- Each rule has a short, unique identifier (similar to flake8, e.g. `R001`).
- Rules are discoverable at runtime. Adding a new rule class to the code base make sit available to the Rule Manager.
- Rules receive a context object when running checks, which encapsulates all information needed for the check.
  - Initially, the context only contains the GitHub repository object.
  - The context can be expanded in the future to provide more information.
- Mutually exclusive
  - Rules can be mutually exclusive with others. The relationship is bi-directional.
  - Mutually exclusive rules can be present in the same rule set.
  - Precedence rules determine which rules in a set are actually active:
    - Rules in sub-rule sets have lower precedence than rules in parent rule sets.
    - Tie-braker for rules at the same level is order in list (from lowest to highest).
    

### Rule Sets

- Rule sets collect several rules.
- Rule sets may be nested, i.e. they may reference individual rules as well as other rule sets.
- Rules have a short, unique identifier, similar to rules.
- Rules and rule sets are referenced by their names.
- At runtime, validation ensures that all references can be resolved.
- A single class defines the behaviour of a rule set.
- A concrete rule set is an instance of this class.
- Pre-defined rule sets are defined in a central YAML file.
- Like rules, rule sets are also discoverable at runtime. Adding a new definition to the central YAML file makes it available to the Rule Manager.


## Technical Constraints

### Programming Language
- Python 3.12+

### Build and Packaging
- Use `uv` as the build and packaging tool.

### Recommended Libraries and Dependencies
- `PyGithub` for interacting with the GitHub API.
- `pydantic` and `pydantic_settings` for configuration handling.
- `pytest` for unit testing.

### Forbidden Libraries
- `click` for the CLI interface.

### Repository Structure
```
project-root/
├── src/
│   ├── repolint/
│   │   ├── __init__.py
│   │   ├── ...
├── tests/
│   ├── __init__.py
│   ├── ...
├── docs/
│   ├── usage.md
│   ├── development.md
├── pyproject.toml
├── README.md
└── LICENSE
```

## Current project Status

We are at Phase 2 of the project.

### Phase 1: Initial Setup and Core Features
- [x] 1.1: Initialize Git repository.
- [x] 1.2: Set up `uv` for build and packaging.
  - [x] 1.2.1: Create `pyproject.toml`.
  - [x] 1.2.2: Add regular and dev dependencies to `pyproject.toml`.
  - [x] 1.2.3: Initialize Python virtual environment by running `uv sync --all-extras`.
- [] 1.3: Setup pre-commit framework.
  - [x] 1.3.1: Add pe-commit framework as dev dependency and sync it into the project's Python virtual environment.
  - [x] 1.3.2: Create ` .pre-commit-config.yaml` file. Add the following checks:
    - `pyupgrade` (for the used Python version): https://github.com/asottile/pyupgrade
    - `ruff` (linter and formatter): https://github.com/astral-sh/ruff
- [x] 1.4: Set up `pytest` for unit testing.
  - [x] 1.4.1: Create `tests/` directory.
  - [x] 1.4.2: Create dummy test file.
  - [x] 1.4.3: Ensure test dependencies are in `pyproject.toml`.
  - [x] 1.4.4: Run `pytest` to verify test setup.
- [x] 1.5: Implement basic CLI with placeholder commands.
  - [x] 1.5.1: Create a `__main__.py` file so the module can be run as a script.
  - [x] 1.5.2: Add an actual script named `repolint` to the package to run the CLI.
- [x] 1.6: Implement the `init` command properly to initialize a configuration file.
- [x] 1.7: Develop core functionality:
  - [x] 1.7.1: GitHub API integration.
  - [x] 1.7.2: Rules and rule-set base classes implementation. No concrete rules yet.
  - [x] 1.7.3: Rule Manager implementation. Singleton. Uses entry points to auto-discover rules and rule sets.
  - [x] 1.7.4: Configuration file parsing.
- [x] 1.8 Add true end-to-end tests for real CLI operations.
  - [x] 1.8.1: Add parameterizable fixture to mock configuration for e2e CLI tests.
  - [x] 1.8.2: Add parameterizable fixture to mock GitHub API responses for e2e CLI tests.
  - [x] 1.8.3: Improve test to verify listing of rules (`repolint --list rules`) to verify output comprehensively.
  - [x] 1.8.4: Improve test to verify listing of rule-sets (`repolint --list rule-sets`) to verify output comprehensively.
- [] 1.9: Create initial rules.
  - [x] 1.9.1: Create a rule that checks if a default branch exists.
  - [x] 1.9.2: Create a rule that checks if the setting "Whether to require contributors to sign off on web-based commits" is enabled (web_commit_signoff_required).
- [] 1.10: Create initial rule sets.
  - [x] 1.10.1: Review rule set discovery logic and ensure rule sets can be created programmatically as well as through configuration.
  - [x] 1.10.2: Create a minimalistic default rule set.
- [x] 1.11: Implement the `lint` command to run linting operations.
  - [x] 1.11.1: Parse and validate the configuration.
  - [x] 1.11.2: Connect to GitHub and enumerate repositories.
  - [x] 1.11.3: Apply inclusion and exclusion patterns to determine final list of repositories.
  - [x] 1.11.4: Iterate over repositories. In the loop body, set up the context to pass to linting rules, but don't actually call them yet.
  - [x] 1.11.5: Determine which rule set to use for each repository in the loop body.
  - [x] 1.11.6: Iterate over all rules in the rule set for each repository in the loop body. Consider using a generator pattern to recursively enumerate all rules in a rule set.
  - [x] 1.11.7: For each rule check on a repository, execute the fix step immediately after, if the --fix CLI option has been passed. Ensure proper terminal output to inform the user.
  - [x] 1.11.8: Add a --non-interactive CLI option. By default, when not given, applying fixes is interactive, i.e. the user should be prompted before executing each fix. When given, applying fixes should not be interactive.
  - [x] 1.11.9: Add CLI option --include-organisations. By default, when not given, linting only considers user repositories. When given, linting considers all repositories, including organisation repositories.
- [x] 1.12: Beautify the linting output.
  - [x] 1.12.1: For each repository, list the repository name followed by the rule set applied for the repo in parenthesis.
  - [x] 1.12.2: For each repository, start the line with a hyphen to indicate an itemized list.
  - [x] 1.12.3: For each repository, print out the result of each rule that gets applied as an itemized list. Indent accordingly.
  - [x] 1.12.4: Colorize the output where appropriate. E.g. printing a check mark should be green, a cross should be red, etc.
- [x] 1.13: Mutually exclusive rules and precedence.
  - [x] 1.13.1: Implement the concept of mutually exclusive rules. A rule may point to other rules that it is mutually exclusive with. The relationship is bi-directional.
  - [x] 1.13.2: Implement rule precedence in rule sets by adding new `effective_rules()` method. This method should:
    - Process rules in reverse order (last added first) to respect precedence
    - Build a dictionary of mutually exclusive relationships for efficient lookup
    - For each rule being processed, exclude any earlier rules that are mutually exclusive with it
    - Return an iterator of the effective rules in their original order
    - Handle the bi-directional nature of mutual exclusivity automatically
- [x] 1.14: Create a minimal default rule set.
- [x] 1.15: Output results of linting operations.

### Phase 2: Testing, Documentation, Rule Build-Out
- [] 2.1: Analyze and improve test coverage.
  - [x] 2.1.1: Identify test coverage gaps and note them down in a new file `docs/coverage.md`. Each gap must be uniquely identifiable so we can refer to it in tasks below.
- [] 2.2: Rules build-out.
  - [x] 2.2.1: Add a rule that checks that the user is the only owner or admin of the repository.
  - [x] 2.2.2: Add a rule that checks that a repo has no collaborators other than the user itself.
  - [x] 2.2.3: Add a rule that checks that Wikis are not enabled.
  - [x] 2.2.4: Add a rule that checks that Issues are not enabled.
  - [x] 2.2.5: Add a rule that checks that Sponsorships are not enabled.
  - [x] 2.2.6: Add a rule that checks that "Preserve this repository" is enabled.
  - [x] 2.2.7: Add a rule that checks that Discussions are not enabled.
  - [x] 2.2.8: Add a rule that checks that Projects are disabled.
- [] 2.3: Create usage and developer documentation.

### Phase 3: Predefined Rule-Sets and Enhancements
- [] 4.1: Add more pre-defined rule-sets for other project types.
- [] 4.2: Support for recursive rule-sets.
- [] 4.3: Optimize performance for large organizations.

### Phase 4: Release and Distribution
- [] 5.1: Finalize project documentation.
- [] 5.2: Publish the package to PyPI.
- [] 5.3: Promote and gather user feedback.

## Lessons Learned

This section collects lessons learned from implementing the project plan above. 
Each item represents a learning point to consider when working on tasks in the future.
For example, a first implementation of a feature may use a certain dependency that is not recommended. 
We can record here that this dependency should not be used in the future and list alternatives.

### Project Setup
1. Instead of creating custom .gitignore files, use GitHub's official language-specific templates from the [github/gitignore](https://github.com/github/gitignore) repository. These templates are comprehensive, well-maintained, and follow best practices for each language/framework.

### GitHub API Integration
1. When using PyGithub, prefer passing the token directly to the `Github` constructor rather than using `Auth.Token`. This simplifies testing and avoids potential compatibility issues.
2. When mocking GitHub API responses in tests, mock at the module level (e.g., `repolint.gh.Github`) rather than the package level (`github.Github`) to avoid issues with internal assertions.
3. For repository list operations, handle both user and organization repositories consistently, applying filtering after fetching the repositories.
4. When implementing repository enumeration:
   - Keep the GitHub-specific code in a dedicated module (`github.py`) to maintain separation of concerns
   - Use proper configuration classes (e.g., `GitHubConfig`) to handle GitHub-specific settings
   - Add clear error messages for common issues like invalid tokens or API rate limits
   - Consider making repository filtering options (private, archived) configurable through the main configuration
5. When handling GitHub organization repositories:
   - Maintain a clear separation between organization-specific mode (single org via `org_name`) and user mode with optional organization inclusion
   - Use `get_user().get_orgs()` to enumerate all organizations a user has access to
   - Consider performance implications when including organization repositories, as it requires additional API calls
   - Test both the positive case (organizations included) and negative case (organizations excluded) with proper mock resets
   - When fetching user repositories with `get_repos()`, always specify `affiliation="owner"` to get only user-owned repositories, as the default behavior includes all accessible repositories including organization ones

### Rule Implementation
1. Use Python's ABC (Abstract Base Class) to enforce a consistent interface for all rules. This ensures that all rules implement the required methods (`check`, `can_fix`, and `fix`).
2. Separate the rule result (passed/failed/skipped) from the result details (message, fix availability) using distinct classes (`RuleResult` enum and `RuleCheckResult` dataclass).
3. Design rule sets to support nesting (rule sets containing other rule sets) from the start, as this provides flexibility in organizing rules.
4. Use unique identifiers for both rules (e.g., 'R001') and rule sets (e.g., 'RS001') to prevent conflicts and enable easy referencing.
5. When implementing permission rules:
   - Always check both repository settings and related files (e.g., FUNDING.yml for sponsorships)
   - Provide clear error messages that indicate exactly what needs to be fixed
   - Consider implementing fix methods that handle both settings and file changes
   - Ensure tests cover all possible combinations of settings and file states

### Rule Manager Implementation
1. When implementing singletons in Python, include a way to reset the singleton state in tests. This can be done via a pytest fixture with `autouse=True` to ensure clean state between tests.
2. When mocking entry points in tests, use `unittest.mock.MagicMock` instead of dynamic type creation. MagicMock provides better control over method behavior and makes test failures more debuggable.
3. For plugin systems (like rules and rule sets), separate the discovery mechanism (Rule Manager) from the implementation (concrete rules). This allows for better extensibility and testing.

### Rule Discovery and Entry Points

1. When adding new rules, always add an entry point in `pyproject.toml` under `[project.entry-points."repolint.rules"]` so that the rule can be discovered at runtime.
2. The entry point key should be a snake_case identifier that describes the rule's purpose (e.g., `wikis_disabled`).
3. The entry point value should be the fully qualified path to the rule class (e.g., `repolint.rules.permission_rules:WikisDisabledRule`).
4. Remember to add entry points for all rules, even if they are only used in the default rule set.
5. Entry points allow for dynamic rule discovery and enable users to selectively enable/disable rules in their configuration.

### Rule Design
1. When designing rules:
   - Use a context object to pass information to rules instead of raw objects.
   - This makes it easier to add new information in the future without breaking the API.
   - The context object serves as a clear contract between the rule system and individual rules.

### Design
1. When designing rule execution:
   - Keep the rule iteration logic separate from rule set management
   - Rule sets should focus on organizing and providing access to rules
   - The linter class should handle rule execution and error handling
   - This separation makes the code more maintainable and testable
2. When working with collections of items:
   - Use generators (yield) instead of building lists when possible
   - This improves memory efficiency by avoiding intermediate lists
   - Makes the code more composable and easier to work with streams of data
   - Especially useful when dealing with potentially large collections
3. When dealing with hierarchical rule sets:
   - Ensure uniqueness by using rule IDs as keys
   - Keep the first occurrence of a rule when duplicates exist
   - Sort rules by ID for consistent ordering
   - This makes rule execution deterministic and easier to reason about

### Configuration
1. When using `pydantic_settings` with environment variables:
   - Use `json_schema_extra={"env": [...]}` instead of `env=...` to specify environment variable names (deprecated in Pydantic V2).
   - Set `env_vars_override_env_file=True` to ensure environment variables take precedence over `.env` file.
   - Use `env_nested_delimiter="__"` to support nested configuration via environment variables.

2. When implementing configuration file handling:
   - Provide a well-documented default configuration template with examples and comments
   - Include clear next steps for users after initialization
   - Handle file paths safely using pathlib
   - Give helpful error messages for common issues like existing files
3. When implementing configuration handling:
   - Use Pydantic's `BaseSettings` for configuration that can come from multiple sources (env vars, files)
   - Ensure configuration file templates exactly match the Pydantic model structure
   - Provide clear error messages that guide users to fix configuration issues
   - Support both file-based and environment variable configuration for sensitive values like tokens

### GitHub API Interaction
1. When writing rules that interact with the GitHub API:
   - Always handle `GithubException` to provide meaningful error messages.
   - Be careful with mock objects in tests, they may behave differently from real API responses.
   - Use type checks to ensure API responses match expected types.

### Development Environment
1. Always run pytest from within the project's virtual environment. Running it directly may fail even if pytest is installed globally.
2. When using `monkeypatch` in pytest, ensure that the path to the mocked attribute matches the actual import path in the code.
3. When mocking a class method, ensure the method exists in the class before attempting to mock it.
4. When mocking instance methods, remember to include `self` as the first parameter in the mock function.
5. When testing code that uses singletons:
   - Mock the singleton class itself, not its instance methods
   - Use pytest fixtures to ensure consistent mocking across test functions
   - Mock at the point where the singleton is imported, not where it's instantiated
   - Reset singleton state between tests if necessary
6. When testing rule execution:
   - Create mock rules that inherit from the base Rule class for testing
   - Test both successful and error cases for rule execution
   - Verify that rule results are correctly propagated through the system
   - Ensure error handling captures and reports rule execution failures appropriately
7. When implementing default rule sets:
   - Use an empty rule set as the default to provide a clean slate for repositories without specific rules configured.
   - This makes it easier for users to opt-in to rules rather than having to opt-out of unwanted rules.
   - The empty rule set should still be a proper rule set class to maintain consistent behavior with other rule sets.

### Implementation Patterns

#### Rule Execution and Fixes
- When implementing automated fixes, it's important to execute them immediately after each rule check rather than batching them. This provides better feedback to users and makes it easier to track the success/failure of each fix.
- Re-running rule checks after successful fixes helps verify that the fix actually resolved the issue and provides updated status to users.
- Consistent output formatting for both successful and failed checks/fixes improves user experience. Using distinct symbols (✓, ✗, ⚡) and colors helps users quickly understand results.
- Test fixtures for rules with fixes should properly implement both check() and fix() methods to ensure the fix functionality works as expected.
- In dry-run mode, use a different tone in output messages to clearly indicate what would happen (e.g., "Would attempt to fix...") rather than what is actually happening. This helps users understand the potential impact of running without --dry-run.
- The fix functionality should be explicitly enabled via a --fix command line option. This ensures that fixes are only attempted when the user explicitly requests them, preventing unintended modifications to repositories.
- Test cases involving fixes should explicitly pass fix=True to the Linter constructor to ensure consistent behavior between tests and actual usage.

### CLI Implementation
1. When implementing a Python CLI tool, create both a dedicated CLI module and a simple `__main__.py` entry point. The CLI module should contain all the actual implementation, while `__main__.py` just imports and calls the main function. This separation allows the tool to be run both as `python -m package` and as a direct script.

### Pattern Matching
1. Use Python's built-in `fnmatch` module for glob pattern matching instead of implementing custom pattern matching logic. It's well-tested, efficient, and supports all common glob patterns like `*`, `?`, and `[seq]`.
2. When implementing filtering with both inclusion and exclusion patterns, apply inclusion patterns first, then exclusion patterns. This is more efficient as it reduces the number of items that need to be checked against exclusion patterns.
3. Always write test cases that cover different pattern combinations:
   - Only inclusion patterns
   - Only exclusion patterns
   - Both inclusion and exclusion patterns
   - Edge cases like empty pattern lists

### Rule Set Discovery and Creation
1. When implementing rule set discovery and creation:
   - Handle rule sets in multiple passes to ensure dependencies are properly resolved
   - Create rule sets with direct rules first, then create empty rule sets for nested-only sets
   - Add nested rule sets last to ensure all dependencies exist
   - Clean up rule sets that have no rules and no valid nested sets
   - Provide clear error messages when rule sets cannot be created or nested sets are not found

### Output Formatting
- Keep output formatting simple and consistent. Instead of verbose labels like "rule set: default", just use the identifier in parentheses "(default)". This makes the output cleaner and easier to scan.
- Use Unicode symbols (✓, ✗, -, ⚡) to provide visual status indicators. These are more intuitive than text labels and make the output easier to scan quickly.
- Maintain a clear visual hierarchy through consistent indentation:
  - Repository names at the root level
  - Rule results indented with 2 spaces
  - Fix descriptions indented with 4 spaces
- When showing errors or problems, keep the error messages concise and prefix them with "Error:" for easy identification.

### Testing
1. When using `pydantic_settings` with environment variables:
   - Use `json_schema_extra={"env": [...]}` instead of `env=...` to specify environment variable names (deprecated in Pydantic V2).
   - Set `env_vars_override_env_file=True` to ensure environment variables take precedence over `.env` file.
   - Use `env_nested_delimiter="__"` to support nested configuration via environment variables.

2. When mocking properties in Python unit tests:
   - Use `PropertyMock` from `unittest.mock` to mock properties correctly.
   - Set the mock on the type of the object using `type(obj).property_name = PropertyMock(...)` instead of directly on the instance.
   - This ensures that property behavior (like raising exceptions) works correctly in tests.

3. When implementing default rule sets:
   - Use an empty rule set as the default to provide a clean slate for repositories without specific rules configured.
   - This makes it easier for users to opt-in to rules rather than having to opt-out of unwanted rules.
   - The empty rule set should still be a proper rule set class to maintain consistent behavior with other rule sets.

### Implementation Patterns

#### Rule Execution and Fixes
- When implementing automated fixes, it's important to execute them immediately after each rule check rather than batching them. This provides better feedback to users and makes it easier to track the success/failure of each fix.
- Re-running rule checks after successful fixes helps verify that the fix actually resolved the issue and provides updated status to users.
- Consistent output formatting for both successful and failed checks/fixes improves user experience. Using distinct symbols (✓, ✗, ⚡) and colors helps users quickly understand results.
- Test fixtures for rules with fixes should properly implement both check() and fix() methods to ensure the fix functionality works as expected.
- In dry-run mode, use a different tone in output messages to clearly indicate what would happen (e.g., "Would attempt to fix...") rather than what is actually happening. This helps users understand the potential impact of running without --dry-run.

4. Error Handling Tests
   - When using Python entry points for plugin discovery, it's important to test both successful and failed loading scenarios
   - Test cases should include:
     - Complete failure to load an entry point
     - Mixed scenarios with both successful and failed entry points
     - Rule creation failures:
       - Attempting to create non-existent rules
       - Rule initialization failures (e.g., invalid parameters)

5. When testing code that relies on environment variables:
   - Use pytest's `monkeypatch` fixture instead of directly modifying `os.environ`
   - This ensures automatic cleanup even if tests fail
   - Provides safer operations with `setenv()` and `delenv()`
   - Maintains test isolation by scoping changes to individual tests
   - Makes tests more maintainable by removing manual cleanup code

6. When implementing rule-based systems:
   - Keep track of rule state (e.g., whether a fix has been applied)
   - Re-check and display rule status after applying fixes
   - This provides better feedback to users about the effects of their actions

### Code Coverage and Exception Handling
- Python's coverage tool has limitations in recognizing coverage of exception handling blocks
- Solutions to improve coverage reporting:
  1. Configure coverage tool via `.coveragerc` to enable branch coverage and set appropriate exclusion rules
  2. Write explicit test cases for each branch condition and error path
- Sometimes remaining "uncovered" lines in exception blocks can be ignored if tests verify the behavior

## Future Scope (only for context, not a goal of current implementation)
- Support for organization-wide rules.
- Enhanced reporting with detailed analytics.
- Plugin system for third-party extensions.

5. When testing error handling in CLI applications:
   - Write test cases for each error condition separately
   - Use `pytest.raises()` to test for expected exceptions like `SystemExit`
   - Test all possible configuration sources (e.g., for GitHub tokens: config file, GITHUB_TOKEN, REPOLINT_GITHUB_TOKEN)
   - Clean up environment variables in tests to ensure test isolation

### Testing Coverage Gaps

When improving test coverage:
- Always measure coverage before and after adding tests to verify improvement
- Handle SystemExit exceptions in CLI tests using pytest.raises to properly test error paths
- Test both success and error paths for file operations (e.g., file exists vs doesn't exist)
- Use pytest's tmp_path fixture for file-based tests to ensure clean test environment

### Fix Handling
- When implementing automated fixes, it's important to execute them immediately after each rule check rather than batching them. This provides better feedback to users and makes it easier to track the success/failure of each fix.
- Re-running rule checks after successful fixes helps verify that the fix actually resolved the issue and provides updated status to users.
- Consistent output formatting for both successful and failed checks/fixes improves user experience. Using distinct symbols (✓, ✗, ⚡) and colors helps users quickly understand results.
- Test fixtures for rules with fixes should properly implement both check() and fix() methods to ensure the fix functionality works as expected.
- In dry-run mode, use a different tone in output messages to clearly indicate what would happen (e.g., "Would attempt to fix...") rather than what is actually happening. This helps users understand the potential impact of running without --dry-run.
- The fix functionality should be explicitly enabled via a --fix command line option. This ensures that fixes are only attempted when the user explicitly requests them, preventing unintended modifications to repositories.
- Test cases involving fixes should explicitly pass fix=True to the Linter constructor to ensure consistent behavior between tests and actual usage.

### Testing GitHub API Interactions

4. When mocking GitHub API properties:
   - Use `PropertyMock` from `unittest.mock` to mock properties that are accessed via the dot notation (e.g., `repository.has_wiki`)
   - Set up the mock using `type(mock_obj).property_name = PropertyMock(...)` instead of directly setting it on the mock object
   - This ensures that property access behavior matches the real GitHub API
   - Example:
     ```python
     # Incorrect:
     mock_repo.has_wiki = MagicMock(side_effect=GithubException(500, "API Error"))
     
     # Correct:
     type(mock_repo).has_wiki = PropertyMock(side_effect=GithubException(500, "API Error"))
     
