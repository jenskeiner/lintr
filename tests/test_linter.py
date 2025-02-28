"""Tests for core linting functionality."""
from abc import ABC
from unittest.mock import MagicMock, patch

import pytest
from colorama import Fore, Style

from lintr.config import RepositoryConfig
from lintr.linter import Linter
from lintr.rules import Rule, RuleCheckResult, RuleResult, RuleSet
from lintr.rules.base import RuleContext


def strip_color_codes(text: str) -> str:
    """Strip ANSI color codes from text."""
    for color in [
        Fore.GREEN,
        Fore.RED,
        Fore.YELLOW,
        Fore.BLUE,
        Fore.WHITE,
        Style.RESET_ALL,
    ]:
        text = text.replace(str(color), "")
    return text


class CustomException(Exception):
    """Custom exception for testing."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


@pytest.fixture
def ruleset(rule_cls):
    """Create a mock rule set."""
    ruleset = RuleSet("default", "Default rule set")
    ruleset.add(rule_cls("G001", "Test rule"))
    return ruleset


def test_rule_set_rules_ordering(rule_cls):
    """Test that rules are returned in order of addition."""
    # Create a rule set with rules in non-alphabetical order
    rule_set = RuleSet("test", "Test rule set")
    rule_set.add(rule_cls("G002", "Second rule"))
    rule_set.add(rule_cls("G001", "First rule"))
    rule_set.add(rule_cls("G003", "Third rule"))

    # Get rules and verify order
    rules = list(rule_set.rules())
    assert len(rules) == 3
    assert [r.rule_id for r in rules] == ["G002", "G001", "G003"]


def test_rule_set_rules_uniqueness(rule_cls):
    """Test that duplicate rules are handled correctly."""
    # Create nested rule sets with duplicate rules
    parent = RuleSet("parent", "Parent rule set")
    child = RuleSet("child", "Child rule set")
    grandchild = RuleSet("grandchild", "Grandchild rule set")

    # Add rules to each level
    parent.add(rule_cls("G001", "First rule - parent"))
    child.add(rule_cls("G001", "First rule - child"))  # Duplicate ID
    child.add(rule_cls("G002", "Second rule - child"))
    grandchild.add(rule_cls("G002", "Second rule - grandchild"))  # Duplicate ID
    grandchild.add(rule_cls("G003", "Third rule - grandchild"))

    # Link rule sets
    child.add(grandchild)
    parent.add(child)

    # Get rules and verify uniqueness and order
    rules = list(parent.rules())
    assert len(rules) == 3  # Should only have 3 unique rules
    assert [r.rule_id for r in rules] == ["G001", "G002", "G003"]
    # First occurrence of each rule should be kept
    assert rules[0].description == "First rule - child"
    assert rules[1].description == "Second rule - grandchild"
    assert rules[2].description == "Third rule - grandchild"


def test_create_context(repository, config):
    """Test creating a rule context."""
    linter = Linter(config)
    context = linter.create_context(repository)
    assert isinstance(context, RuleContext)
    assert context.repository == repository
    assert not context.dry_run


def test_get_rule_set_for_repository_default(repository, config, ruleset, rule_manager):
    """Test getting default rule set for repository."""
    # Setup mock rule manager
    rule_manager.get.return_value = ruleset

    # Create linter and get rule set
    linter = Linter(config)
    rule_set_info = linter.get_rule_set_for_repository(None)

    # Verify correct rule set is returned
    assert rule_set_info is not None
    rule_set_id, rule_set = rule_set_info
    assert rule_set_id == "empty"
    assert rule_set == ruleset
    rule_manager.get.assert_called_once_with("empty")


def test_get_rule_set_for_repository_specific(
    repository, config, ruleset, rule_manager
):
    """Test getting repository-specific rule set."""
    # Configure repository-specific rule set
    ruleset._id = "specific"

    # Setup mock rule manager
    rule_manager.get.return_value = ruleset

    # Create linter and get rule set
    linter = Linter(config)
    rule_set_info = linter.get_rule_set_for_repository(
        RepositoryConfig(ruleset="specific")
    )

    # Verify correct rule set is returned
    assert rule_set_info is not None
    rule_set_id, rule_set = rule_set_info
    assert rule_set_id == "specific"
    assert rule_set == ruleset
    rule_manager.get.assert_called_once_with("specific")


def test_get_rule_set_for_repository_not_found(repository, config, rule_manager):
    """Test handling of non-existent rule set."""
    # Setup mock rule manager to return no rule set
    rule_manager.get.return_value = None

    # Create linter and get rule set
    linter = Linter(config)
    rule_set_info = linter.get_rule_set_for_repository(None)

    # Verify no rule set is returned
    assert rule_set_info is None
    rule_manager.get.assert_called_once_with("empty")


def test_check_repository_success(repository, config, ruleset):
    """Test successful repository checking."""
    # Create linter and check repository
    linter = Linter(config)
    results = linter.check_repository(repository, ruleset)

    # Verify results
    assert "G001" in results
    assert results["G001"].result == RuleResult.PASSED
    assert results["G001"].message == "Test passed"
    assert not results["G001"].fix_available


def test_check_repository_rule_error(repository, config, rule_cls):
    """Test handling of rule execution errors."""
    # Create a rule set with a failing rule
    rule_set = RuleSet("test", "Test rule set")
    rule_set.add(rule_cls("G001", "Failing test rule", Exception("Rule failed")))

    # Create linter and check repository
    linter = Linter(config)
    results = linter.check_repository(repository, rule_set)

    # Verify error is reported in results
    assert "G001" in results
    assert results["G001"].result == RuleResult.FAILED
    assert "Rule execution failed" in results["G001"].message


def test_lint_repositories_with_missing_rule_set(repository, config, rule_manager):
    """Test linting repositories when rule set is not found."""
    # Setup mock rule manager to return no rule set
    rule_manager.get.return_value = None

    # Create linter and lint repositories
    linter = Linter(config)
    results = linter.lint_repositories([repository])

    # Verify error is reported in results
    assert "test-repo" in results
    assert "error" in results["test-repo"]
    assert "No rule set found" in results["test-repo"]["error"]
    rule_manager.get.assert_called_once_with("empty")


def test_lint_repositories_success(repository, config, ruleset, rule_manager):
    """Test successful repository linting."""
    # Setup mock rule manager
    rule_manager.get.return_value = ruleset

    # Create linter and lint repositories
    linter = Linter(config)
    results = linter.lint_repositories([repository])

    # Verify results
    assert "test-repo" in results
    repo_results = results["test-repo"]
    assert "G001" in repo_results
    assert repo_results["G001"].result == RuleResult.PASSED
    assert repo_results["G001"].message == "Test passed"
    assert not repo_results["G001"].fix_available


def test_lint_repositories_output_formatting(repository, config, capsys, rule_cls):
    """Test output formatting of lint results."""
    # Create rules with different results
    passing_rule = rule_cls("G001", "Passing rule")
    failing_rule = rule_cls(
        "G002",
        "Failing rule",
        RuleCheckResult(
            result=RuleResult.FAILED, message="Dummy rule result", fix_available=False
        ),
    )
    skipped_rule = rule_cls(
        "G003",
        "Skipped rule",
        RuleCheckResult(
            result=RuleResult.SKIPPED, message="Dummy rule result", fix_available=False
        ),
    )
    fixable_rule = rule_cls(
        "G004",
        "Fixable rule",
        RuleCheckResult(
            result=RuleResult.FAILED, message="Dummy rule result", fix_available=False
        ),
    )

    # Create a rule set with all types of rules
    rule_set = RuleSet("test", "Test rule set")
    rule_set.add(passing_rule)
    rule_set.add(failing_rule)
    rule_set.add(skipped_rule)
    rule_set.add(fixable_rule)

    # Configure mock config to use our test rule set
    config.default_ruleset = "test"

    # Setup mock rule manager to return our rule set
    rule_manager = MagicMock()
    rule_manager.get.return_value = rule_set

    # Create linter with mocked rule manager
    linter = Linter(config)
    linter._rule_manager = rule_manager

    # Run linting
    linter.lint_repositories([repository])

    # Capture output and strip color codes
    captured = capsys.readouterr()
    output_lines = [strip_color_codes(line) for line in captured.out.splitlines()]

    # Verify output format
    assert output_lines[0] == f"- {repository.name} (test)"
    assert "✓ G001:" in output_lines[1]  # Passing rule
    assert "✗ G002:" in output_lines[2]  # Failing rule
    assert "- G003:" in output_lines[3]  # Skipped rule
    assert "✗ G004:" in output_lines[4]  # Fixable rule


def test_lint_repositories_output_formatting_with_fix(
    repository, config, capsys, rule_cls
):
    """Test output formatting of lint results with a fixable rule."""
    # Create a rule set with a fixable rule
    rule_set = RuleSet("test", "Test rule set")
    rule_set.add(
        rule_cls(
            "G001",
            "Fixable rule",
            result=RuleCheckResult(
                result=RuleResult.FAILED,
                message="Rule failed but can be fixed",
                fix_available=True,
                fix_description="This can be fixed automatically",
            ),
        )
    )

    # Configure mock config to use our test rule set
    config.default_ruleset = "test"

    # Setup mock rule manager to return our rule set
    rule_manager = MagicMock()
    rule_manager.get.return_value = rule_set

    # Create linter with mocked rule manager
    linter = Linter(config)
    linter._rule_manager = rule_manager

    # Run linting
    linter.lint_repositories([repository])

    # Capture output and strip color codes
    captured = capsys.readouterr()
    output_lines = [strip_color_codes(line) for line in captured.out.splitlines()]

    # Verify output format
    assert output_lines[0] == f"- {repository.name} (test)"
    assert "✗ G001:" in output_lines[1]  # Failed rule
    assert "⚡" in output_lines[2]  # Fix available
    assert "This can be fixed automatically" in output_lines[2]  # Fix description


def test_lint_repositories_custom_error_message(repository, config, capsys, rule_cls):
    """Test output formatting of lint results with a custom error message."""
    error_message = "Custom error occurred while checking rule"

    # Create a rule set with an error-raising rule
    rule_set = RuleSet("test", "Test rule set")
    rule_set.add(rule_cls("G001", "Error rule", result=Exception(error_message)))

    # Configure mock config to use our test rule set
    config.default_ruleset = "test"

    # Setup mock rule manager to return our rule set
    rule_manager = MagicMock()
    rule_manager.get.return_value = rule_set

    # Create linter with mocked rule manager
    linter = Linter(config)
    linter._rule_manager = rule_manager

    # Run linting
    results = linter.lint_repositories([repository])

    # Verify error is correctly captured in results
    assert "G001" in results[repository.name]
    result = results[repository.name]["G001"]
    assert result.result == RuleResult.FAILED
    assert error_message in result.message
    assert not result.fix_available

    # Verify error output format
    captured = capsys.readouterr()
    output_lines = [strip_color_codes(line) for line in captured.out.splitlines()]
    assert output_lines[0] == f"- {repository.name} (test)"
    assert "Error executing rule G001" in output_lines[1]
    assert error_message in output_lines[1]
    assert "✗ G001:" in output_lines[2]
    assert "Rule execution failed" in output_lines[2]


def test_lint_repositories_no_rule_set_found(repository, config, capsys):
    """Test output formatting when no rule set is found."""
    # Configure mock config with non-existent rule set
    config.default_ruleset = "non-existent"
    config.repositories = {}

    # Setup mock rule manager to return no rule set
    rule_manager = MagicMock()
    rule_manager.get_rule_set.return_value = None

    # Create linter with mocked rule manager
    linter = Linter(config)
    linter._rule_manager = rule_manager

    # Run linting
    results = linter.lint_repositories([repository])

    # Verify error is correctly captured in results
    assert "error" in results[repository.name]
    assert "No rule set found" in results[repository.name]["error"]

    # Verify error output format
    captured = capsys.readouterr()
    output_lines = [strip_color_codes(line) for line in captured.out.splitlines()]
    assert output_lines[0] == f"- {repository.name} (no rule set)"


@pytest.mark.parametrize(
    "non_interactive,user_input,expected_fix",
    [
        (False, "y\n", True),  # Interactive mode, user confirms
        (False, "n\n", False),  # Interactive mode, user declines
        (True, "", True),  # Non-interactive mode, always fixes
    ],
)
def test_lint_repositories_fix_interaction(
    repository,
    config,
    capsys,
    monkeypatch,
    non_interactive,
    user_input,
    expected_fix,
    rule_cls,
):
    """Test interactive and non-interactive fix modes."""
    # Create a rule set with a fixable rule
    rule = rule_cls(
        "test.rule",
        "Test rule",
        result=RuleCheckResult(
            result=RuleResult.FAILED,
            message="Rule failed but can be fixed",
            fix_available=True,
            fix_description="This can be fixed automatically",
        ),
        fix=lambda context: (True, "Mock fix applied"),
    )
    rule_set = RuleSet("test", "Test rule set")
    rule_set.add(rule)

    # Mock rule manager
    rule_manager = MagicMock()
    rule_manager.get.return_value = rule_set

    # Mock user input
    mock_input = MagicMock(return_value=user_input.strip())
    monkeypatch.setattr("builtins.input", mock_input)

    # Mock repository name
    repository.description = "test-repo"

    # Create linter with mocked components
    linter = Linter(config, dry_run=False, non_interactive=non_interactive, fix=True)
    linter._rule_manager = rule_manager

    # Run linting
    linter.lint_repositories([repository])
    captured = capsys.readouterr()

    # Verify fix was applied or skipped based on interaction mode and user input
    if expected_fix:
        assert "⚡ Fixed: Mock fix applied" in strip_color_codes(captured.out)
    else:
        assert "Fix skipped" in strip_color_codes(captured.out)


def test_lint_repositories_fix_error(repository, config, capsys):
    """Test handling of errors during fix application."""

    class R(Rule):
        _id = "G001"
        _description = "Test rule"

        def __init__(self):
            super().__init__()
            self._check_count = 0

        def check(self, context: RuleContext) -> RuleCheckResult:
            return RuleCheckResult(
                result=RuleResult.FAILED,
                message="Rule failed but can be fixed",
                fix_available=True,
                fix_description="This can be fixed automatically",
            )

        def fix(self, context: RuleContext) -> tuple[bool, str]:
            raise CustomException("Error during fix")

    # Setup rule set with a rule that fails during fix
    rule_set = RuleSet("test", "Test rule set")
    rule_set.add(R)

    # Setup rule manager
    mock_manager = MagicMock()
    mock_manager.get.return_value = rule_set
    with patch("lintr.linter.RuleManager", return_value=mock_manager):
        # Run linter in non-interactive mode to trigger fix
        linter = Linter(config, non_interactive=True, fix=True)
        linter.lint_repositories([repository])

        # Check output
        captured = capsys.readouterr()
        output = strip_color_codes(captured.out)
        assert "✗ G001: Rule failed but can be fixed" in output
        assert "⚡ This can be fixed automatically" in output
        assert "⚡ Fix error: Error during fix" in output


def test_lint_repositories_recheck_error(repository, config, capsys):
    """Test handling of errors during recheck after fix."""

    class R(Rule):
        _id = "G001"
        _description = "Test rule"

        def __init__(self):
            super().__init__()
            self._check_count = 0

        def check(self, context: RuleContext) -> RuleCheckResult:
            self._check_count += 1

            # First check always returns failed with fix available
            if self._check_count == 1:
                return RuleCheckResult(
                    result=RuleResult.FAILED,
                    message="Rule failed but can be fixed",
                    fix_available=True,
                    fix_description="This can be fixed automatically",
                )

            raise CustomException("Error during recheck after fix")

        def fix(self, context: RuleContext) -> tuple[bool, str]:
            return True, "Mock fix applied"

    # Setup rule set with a rule that fails during recheck
    rule_set = RuleSet("test", "Test rule set")
    rule_set.add(R)

    # Setup rule manager
    mock_manager = MagicMock()
    mock_manager.get.return_value = rule_set
    with patch("lintr.linter.RuleManager", return_value=mock_manager):
        # Run linter in non-interactive mode to trigger fix
        linter = Linter(config, non_interactive=True, fix=True)
        linter.lint_repositories([repository])

        # Check output
        captured = capsys.readouterr()
        output = strip_color_codes(captured.out)
        assert "✗ G001: Rule failed but can be fixed" in output
        assert "⚡ This can be fixed automatically" in output
        assert "⚡ Fixed: Mock fix applied" in output
        assert "Fix error: Error during recheck after fix" in output


def test_lint_repositories_fix_error_with_failed_fix(repository, config, capsys):
    """Test handling of failed fixes (non-exception case)."""

    # Create a rule that returns success=False from fix
    class FailedFixRule(Rule):
        _id = "G001"
        _description = "Test rule"

        def check(self, context: RuleContext) -> RuleCheckResult:
            return RuleCheckResult(
                result=RuleResult.FAILED,
                message="Rule failed but can be fixed",
                fix_available=True,
                fix_description="This can be fixed automatically",
            )

        def fix(self, context: RuleContext) -> tuple[bool, str]:
            return False, "Fix failed for some reason"

    # Setup rule set with our test rule
    rule_set = RuleSet("test", "Test rule set")
    rule_set.add(FailedFixRule)

    # Setup rule manager
    mock_manager = MagicMock()
    mock_manager.get.return_value = rule_set
    with patch("lintr.linter.RuleManager", return_value=mock_manager):
        # Run linter in non-interactive mode to trigger fix
        linter = Linter(config, non_interactive=True, fix=True)
        linter.lint_repositories([repository])

        # Check output
        captured = capsys.readouterr()
        output = strip_color_codes(captured.out)
        assert "✗ G001: Rule failed but can be fixed" in output
        assert "⚡ This can be fixed automatically" in output
        assert "⚡ Fix failed: Fix failed for some reason" in output


def test_lint_repositories_fix_with_all_rule_results(
    repository, config, capsys, rule_cls
):
    """Test handling of all possible rule results after fix."""

    class MultiResultRule(Rule, ABC):
        _result = RuleResult.PASSED
        _fixed = False

        def check(self, context: RuleContext) -> RuleCheckResult:
            if not self._fixed:
                return RuleCheckResult(
                    result=RuleResult.FAILED,
                    message="Rule failed but can be fixed",
                    fix_available=True,
                    fix_description="This can be fixed automatically",
                )
            return RuleCheckResult(
                result=self._result,
                message=f"Rule returned {self._result} after fix",
                fix_available=False,
            )

        def fix(self, context: RuleContext) -> tuple[bool, str]:
            self._fixed = True
            return True, "Fix applied"

    # Test each possible result type
    for result in [RuleResult.PASSED, RuleResult.FAILED, RuleResult.SKIPPED]:
        # Setup rule set with a rule that returns our test result
        rule_set = RuleSet("test", "Test rule set")

        class MyRule(MultiResultRule):
            _id = "G001"
            _description = "Test rule"
            _result = result

        rule_set.add(MyRule)

        # Setup rule manager
        mock_manager = MagicMock()
        mock_manager.get.return_value = rule_set
        with patch("lintr.linter.RuleManager", return_value=mock_manager):
            # Run linter in non-interactive mode to trigger fix
            linter = Linter(config, non_interactive=True, fix=True)
            linter.lint_repositories([repository])

            # Check output
            captured = capsys.readouterr()
            output = strip_color_codes(captured.out)
            assert "Rule returned" in output
            if result == RuleResult.PASSED:
                assert "✓" in output
            elif result == RuleResult.FAILED:
                assert "✗" in output
            else:  # SKIPPED
                assert "-" in output


def test_lint_repositories_no_fix_prompt_without_fix_flag(
    repository, config, capsys, rule_cls
):
    """Test that fix prompts are not shown when --fix is not provided."""
    # Create a rule set with a fixable rule
    rule = rule_cls(
        "test.rule",
        "Test rule",
        result=RuleCheckResult(
            result=RuleResult.FAILED,
            message="Rule failed but can be fixed",
            fix_available=True,
            fix_description="This can be fixed automatically",
        ),
    )
    rule_set = RuleSet("test", "Test rule set")
    rule_set.add(rule)

    # Mock rule manager
    rule_manager = MagicMock()
    rule_manager.get.return_value = rule_set

    # Mock repository name and context
    repository.description = "test-repo"
    repository.empty = True

    # Create linter with mocked components (fix=False)
    linter = Linter(config, dry_run=False, non_interactive=False, fix=False)
    linter._rule_manager = rule_manager

    # Mock create_context to return a RuleContext
    context = RuleContext(repository, config)
    linter.create_context = MagicMock(return_value=context)

    # Run linting
    linter.lint_repositories([repository])
    captured = capsys.readouterr()
    output = strip_color_codes(captured.out)

    # Fix description should be shown but not fix prompt
    assert "⚡ This can be fixed automatically" in output
    assert "Apply this fix?" not in output
    assert "Fix skipped" not in output
    assert "Fixed: Mock fix applied" not in output
