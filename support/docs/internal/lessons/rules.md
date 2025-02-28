### Rule Implementation

- Use Python's ABC (Abstract Base Class) to enforce a consistent interface for all rules. This ensures that all rules implement the required methods (`check`, `can_fix`, and `fix`).
- Separate the rule result (passed/failed/skipped) from the result details (message, fix availability) using distinct classes (`RuleResult` enum and `RuleCheckResult` dataclass).
- Design rule sets to support nesting (rule sets containing other rule sets) from the start.
- Use unique identifiers for rules (e.g., 'G001'). Rule identifiers are class attributes on concrete sub-classes of the rule base clasds.
- In case a rule fails, provide a clear error message that indicate exactly what needs to be fixed.
- The linter class in `src/lintr/linter.py`should handle rule execution and error handling.
- Use a context object to pass information to rules instead of raw objects.
- Re-running rule checks after successful fixes helps verify that the fix actually resolved the issue.
- Consistent output formatting for both successful and failed checks/fixes improves user experience. Using distinct symbols (✓, ✗, ⚡) and colors helps users quickly understand results.
- Test fixtures for rules with fixes should properly implement both check() and fix() methods to ensure the fix functionality works as expected.
- In dry-run mode, use a different tone in output messages to clearly indicate what would happen (e.g., "Would attempt to fix...") rather than what is actually happening.
- Ensure that tests cover any rule-relatedd changes such as addition of a new rule or modification of an existing one.
- When adding new rules, always add an entry point in `pyproject.toml` under `[project.entry-points."lintr.rules"]` so that the rule can be discovered at runtime.
- The fix functionality should be explicitly enabled via a --fix command line option. This prevents unintended modifications to repositories.
- Test cases involving fixes should explicitly pass fix=True to the Linter constructor to ensure consistent behavior between tests and actual usage.
- When implementing automated fixes, execute them immediately after each rule check rather than batching them.

### Rule Sets
- Rule sets should focus on organizing and providing access to rules.
- Use unique identifiers for rule sets (e.g., 'RS001') to prevent conflicts and enable easy referencing. Identifiers are instance members passed to the constructor.
- When dealing with hierarchical rule sets:
  - Filter out multiple occurrences of the same rule.
  - Keep the first occurrence of a rule when duplicates exist.

### Rule Discovery and Entry Points
- When adding new rules, always add an entry point in `pyproject.toml` under `[project.entry-points."lintr.rules"]` so that the rule can be discovered at runtime.
- The entry point key should be a snake_case identifier that describes the rule's purpose (e.g., `wikis_disabled`).
- The entry point value should be the fully qualified path to the rule class (e.g., `lintr.rules.permission_rules:WikisDisabledRule`).
- Provide clear error messages when rule sets cannot be created or nested sets are not found.
