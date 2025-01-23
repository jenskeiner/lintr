# Code Coverage Gaps

This document lists the identified coverage gaps in the codebase. Each gap has a unique identifier for easy reference.

## Main Package (MAIN)

- **MAIN-001**: Missing coverage in `__main__.py` line 7 (75% coverage)
  - Description: Entry point execution path not covered

## CLI Module (CLI)

- **CLI-001**: Missing coverage in `cli.py` lines 148-150, 153-154 (92% coverage)
  - Description: Error handling paths in CLI processing

- **CLI-002**: Missing coverage in `cli.py` lines 194-195, 203-204
  - Description: Branch conditions in command processing

- **CLI-003**: Missing coverage in `cli.py` line 259
  - Description: Exception handling path

## Linter Module (LINT)

- **LINT-001**: Missing coverage in `linter.py` lines 116-117, 140 (97% coverage)
  - Description: Error handling paths in linting process

## Rule Manager Module (RULE)

- **RULE-001**: Missing coverage in `rule_manager.py` lines 103-105, 114 (88% coverage)
  - Description: Rule initialization error paths

- **RULE-002**: Missing coverage in `rule_manager.py` lines 125-126, 141
  - Description: Rule validation and processing paths

- **RULE-003**: Missing coverage in `rule_manager.py` line 160
  - Description: Rule execution path

- **RULE-004**: Missing coverage in `rule_manager.py` lines 227-230, 238
  - Description: Rule manager error handling paths

## Base Rules Module (BASE)

- **BASE-001**: Missing coverage in `rules/base.py` lines 55, 71 (97% coverage)
  - Description: Base rule error handling paths

## Overall Statistics

- Total statements: 549
- Missed statements: 29
- Overall coverage: 95%

## Priority Areas

Based on coverage percentages, the following modules should be prioritized for coverage improvements:

1. Rule Manager Module (88% coverage)
2. CLI Module (92% coverage)
3. Other modules with >95% coverage need minimal attention

Each gap can be referenced by its unique identifier (e.g., "RULE-001") when discussing or working on coverage improvements.
