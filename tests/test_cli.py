"""Tests for the CLI interface."""

import pytest

from repolint.cli import main
from repolint.rules.base import Rule, RuleSet, RuleCheckResult, RuleResult
from tests.fixtures import TestRule, TestRuleSet
import tempfile
from pathlib import Path
import yaml


@pytest.fixture
def mock_config():
    """Create a temporary configuration file with given content."""

    def _create_config(content: dict) -> Path:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            yaml.dump(content, f)
            return Path(f.name)

    yield _create_config
    # Clean up any created files
    for file in Path(".").glob("*.yml"):
        if file.is_file() and "tmp" in str(file):
            file.unlink()


@pytest.fixture
def mock_github(monkeypatch):
    """Mock GitHub API responses."""

    class MockRepository:
        def __init__(self, name, private=False, archived=False):
            self.name = name
            self.private = private
            self.archived = archived

    class MockGitHubClient:
        def __init__(self, *args, **kwargs):
            pass

        def get_repositories(self):
            return [
                MockRepository("test-repo-1", private=False, archived=False),
                MockRepository("test-repo-2", private=True, archived=True),
            ]

    monkeypatch.setattr("repolint.github.GitHubClient", MockGitHubClient)
    return MockGitHubClient


@pytest.fixture
def mock_config_file(mock_config):
    """Create a default configuration file."""
    config = {
        "github_token": "test-token",
        "default_rule_set": "default",
        "repository_filter": {"include_patterns": [], "exclude_patterns": []},
        "rule_sets": {},
        "repository_rule_sets": {},
    }
    return mock_config(config)


def test_cli_version(capsys):
    """Test that the CLI version command works."""
    with pytest.raises(SystemExit) as exc_info:
        main(["--version"])
    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "repolint" in captured.out.lower()
    assert "0.1.0" in captured.out


def test_cli_no_args(capsys):
    """Test CLI with no arguments shows help."""
    assert main([]) == 1
    captured = capsys.readouterr()
    assert "usage:" in captured.out.lower()


def test_cli_lint_basic(capsys, test_env, mock_github, mock_config_file):
    """Test basic lint command."""
    result = main(["lint", "--config", str(mock_config_file)])
    assert result == 0
    captured = capsys.readouterr()
    assert str(mock_config_file) in captured.out
    assert "Found 2 repositories" in captured.out


def test_cli_lint_with_options(capsys, test_env, mock_github, mock_config_file):
    """Test lint command with options."""
    result = main(["lint", "--config", str(mock_config_file), "--fix", "--dry-run"])
    assert result == 0
    captured = capsys.readouterr()
    assert "auto-fix is enabled" in captured.out.lower()
    assert "dry-run mode is enabled" in captured.out.lower()


def test_cli_list_no_options(capsys, monkeypatch):
    """Test list command without options."""

    # Mock rule manager instance methods
    def mock_get_all_rules(self):
        return {}

    def mock_get_all_rule_sets(self):
        return {}

    monkeypatch.setattr(
        "repolint.rule_manager.RuleManager.get_all_rules", mock_get_all_rules
    )
    monkeypatch.setattr(
        "repolint.rule_manager.RuleManager.get_all_rule_sets", mock_get_all_rule_sets
    )

    assert main(["list"]) == 0
    captured = capsys.readouterr()
    assert "Please specify --rules and/or --rule-sets" in captured.out


def test_cli_list_rules(capsys, monkeypatch):
    """Test list command with --rules option comprehensively."""
    # Mock rule manager to return test rules
    test_rules = {
        "R001": TestRule("R001", "Check branch protection"),
        "R002": TestRule("R002", "Check repository visibility"),
    }

    def mock_get_all_rules(self):
        return test_rules

    monkeypatch.setattr(
        "repolint.rule_manager.RuleManager.get_all_rules", mock_get_all_rules
    )

    # Run command
    result = main(["list", "--rules"])

    # Verify exit code
    assert result == 0

    # Verify output format
    captured = capsys.readouterr()
    output_lines = captured.out.splitlines()

    # Check header
    assert output_lines[0] == "Available rules:"

    # Check each rule is listed with proper format
    for rule_id, rule in test_rules.items():
        rule_line = f"  {rule_id}: {rule.description}"
        assert rule_line in output_lines[1:]


def test_cli_list_rules_empty(capsys, monkeypatch):
    """Test list command with --rules option when no rules are available."""

    def mock_get_all_rules(self):
        return {}

    monkeypatch.setattr(
        "repolint.rule_manager.RuleManager.get_all_rules", mock_get_all_rules
    )

    assert main(["list", "--rules"]) == 0
    captured = capsys.readouterr()
    assert "Available rules:" in captured.out
    assert "No rules implemented yet" in captured.out


def test_cli_list_rule_sets(capsys, monkeypatch):
    """Test list command with --rule-sets option."""
    # Mock rule manager to return test rule sets
    test_rule_sets = {
        "RS001": TestRuleSet("RS001", "Basic repository checks"),
        "RS002": TestRuleSet("RS002", "Security checks"),
    }

    def mock_get_all_rule_sets(self):
        return test_rule_sets

    monkeypatch.setattr(
        "repolint.rule_manager.RuleManager.get_all_rule_sets", mock_get_all_rule_sets
    )

    # Run command
    result = main(["list", "--rule-sets"])

    # Verify exit code
    assert result == 0

    # Verify output format
    captured = capsys.readouterr()
    output_lines = captured.out.splitlines()

    # Check header
    assert output_lines[0] == "Available rule-sets:"

    # Check each rule set is listed with proper format
    for rule_set_id, rule_set in test_rule_sets.items():
        rule_set_line = f"  {rule_set_id}: {rule_set.description}"
        assert rule_set_line in output_lines[1:]


def test_cli_list_rule_sets_empty(capsys, monkeypatch):
    """Test list command with --rule-sets option when no rule sets are available."""

    def mock_get_all_rule_sets(self):
        return {}

    monkeypatch.setattr(
        "repolint.rule_manager.RuleManager.get_all_rule_sets", mock_get_all_rule_sets
    )

    assert main(["list", "--rule-sets"]) == 0
    captured = capsys.readouterr()
    assert "Available rule-sets:" in captured.out
    assert "No rule-sets implemented yet" in captured.out


def test_cli_init_basic(capsys):
    """Test basic init command."""
    output_file = Path(".repolint.test.yml")
    if output_file.exists():
        output_file.unlink()

    try:
        result = main(["init", "--output", str(output_file)])
        assert result == 0
        captured = capsys.readouterr()
        assert str(output_file) in captured.out
        assert output_file.exists()
    finally:
        if output_file.exists():
            output_file.unlink()


def test_cli_lint_with_config(capsys, mock_config, mock_github):
    """Test lint command with custom configuration."""
    config = {
        "github_token": "test-token",
        "default_rule_set": "test-ruleset",
        "repository_filter": {
            "include_patterns": ["test-repo-*"],
            "exclude_patterns": ["test-repo-excluded"],
        },
        "rule_sets": {"test-ruleset": {"name": "test-ruleset", "rules": ["R001"]}},
        "repository_rule_sets": {},
    }
    config_path = mock_config(config)

    result = main(["lint", "--config", str(config_path)])
    assert result == 0

    captured = capsys.readouterr()
    assert str(config_path) in captured.out
    assert "Found 2 repositories" in captured.out


def test_cli_lint_with_default_config(capsys, mock_config_file, mock_github):
    """Test lint command with default test configuration."""
    result = main(["lint", "--config", str(mock_config_file)])
    assert result == 0

    captured = capsys.readouterr()
    assert str(mock_config_file) in captured.out
    assert "Found 2 repositories" in captured.out


def test_cli_lint_with_mock_github(capsys, mock_config, test_env, mock_github):
    """Test lint command with mocked GitHub API responses."""
    # Define mock repository data

    # Define mock settings for each repository

    # Create test configuration
    config = {
        "github_token": "env-token",
        "default_rule_set": "default",
        "repository_filter": {
            "include_patterns": ["test-repo-*"],
            "exclude_patterns": [],
        },
        "rule_sets": {"test-ruleset": {"name": "test-ruleset", "rules": ["R001"]}},
        "repository_rule_sets": {},
    }
    config_path = mock_config(config)

    # Run lint command
    result = main(["lint", "--config", str(config_path)])
    assert result == 0

    # Verify output
    captured = capsys.readouterr()
    assert str(config_path) in captured.out
    assert "Found 2 repositories" in captured.out


def test_cli_lint_with_non_interactive(capsys, mock_config_file, mock_github, test_env):
    """Test lint command with --non-interactive option."""
    # Create a mock config file with a GitHub token
    mock_config_file.write_text(
        """
github_token: env-token
rule_sets:
  default:
    name: Default Rule Set
    rules:
      - test.rule
"""
    )

    # Run lint command with --fix and --non-interactive
    args = ["lint", "--fix", "--non-interactive", "--config", str(mock_config_file)]
    main(args)

    # Verify output messages
    captured = capsys.readouterr()
    output = captured.out
    assert "Auto-fix is enabled - will attempt to fix issues automatically" in output
    assert (
        "Non-interactive mode is enabled - fixes will be applied without prompting"
        in output
    )


def test_cli_lint_config_not_found(capsys):
    """Test lint command with non-existent config file."""
    # Use a non-existent config file path
    non_existent_config = "non_existent_config.yml"

    with pytest.raises(SystemExit) as exc_info:
        main(["lint", "--config", non_existent_config])

    assert exc_info.value.code == 1

    captured = capsys.readouterr()
    assert f"Error: Configuration file not found: {non_existent_config}" in captured.out
    assert "Run 'repolint init' to create a new configuration file" in captured.out


def test_cli_lint_no_github_token(capsys, mock_config, monkeypatch, test_env):
    """Test lint command with no GitHub token configured."""
    # Remove tokens from environment
    monkeypatch.delenv("REPOLINT_GITHUB_TOKEN", raising=False)

    # Create a temporary config without tokens
    config_path = mock_config(
        {
            "default_rule_set": "default",
            "repository_filter": {"include_patterns": [], "exclude_patterns": []},
            "rule_sets": {},
            "repository_rule_sets": {},
        }
    )

    with pytest.raises(SystemExit) as exc_info:
        main(["lint", "--config", str(config_path)])
    assert exc_info.value.code == 1

    captured = capsys.readouterr()
    assert (
        "Error loading configuration: 1 validation error for RepolintConfig\ngithub_token"
        in captured.out
    )


def test_cli_list_invalid_argument(capsys):
    """Test list command with an invalid argument."""
    # Test with an invalid argument that should be caught by argparse
    with pytest.raises(SystemExit) as exc_info:
        main(["list", "--invalid"])

    assert exc_info.value.code == 2
    captured = capsys.readouterr()
    assert "error: unrecognized arguments: --invalid" in captured.err


def test_cli_list_rules_error(capsys, monkeypatch):
    """Test list command with --rules when RuleManager.get_all_rules raises an exception."""

    def mock_get_all_rules_error(self):
        raise Exception("Failed to load rules")

    monkeypatch.setattr(
        "repolint.rule_manager.RuleManager.get_all_rules", mock_get_all_rules_error
    )

    with pytest.raises(SystemExit) as exc_info:
        main(["list", "--rules"])
    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "Error: Failed to load rules: Failed to load rules" in captured.err


def test_cli_list_rule_sets_error(capsys, monkeypatch):
    """Test list command with --rule-sets when RuleManager.get_all_rule_sets raises an exception."""

    def mock_get_all_rule_sets_error(self):
        raise Exception("Failed to load rule sets")

    monkeypatch.setattr(
        "repolint.rule_manager.RuleManager.get_all_rule_sets",
        mock_get_all_rule_sets_error,
    )

    with pytest.raises(SystemExit) as exc_info:
        main(["list", "--rule-sets"])
    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "Error: Failed to load rule sets: Failed to load rule sets" in captured.err


def test_cli_init_permission_error_mkdir(capsys, monkeypatch):
    """Test init command when mkdir fails due to permissions."""

    def mock_mkdir(*args, **kwargs):
        raise PermissionError("Permission denied")

    monkeypatch.setattr(Path, "mkdir", mock_mkdir)

    with pytest.raises(SystemExit) as exc_info:
        main(["init", "--output", "test/config.yml"])
    assert exc_info.value.code == 1

    captured = capsys.readouterr()
    assert "Error creating configuration file: Permission denied" in captured.out


def test_cli_init_permission_error_copy(capsys, monkeypatch):
    """Test init command when file copy fails due to permissions."""

    def mock_copy2(*args, **kwargs):
        raise PermissionError("Permission denied")

    # Allow mkdir to succeed but make copy2 fail
    monkeypatch.setattr("shutil.copy2", mock_copy2)

    with pytest.raises(SystemExit) as exc_info:
        main(["init", "--output", "test/config.yml"])
    assert exc_info.value.code == 1

    captured = capsys.readouterr()
    assert "Error creating configuration file: Permission denied" in captured.out


def test_cli_main_no_args(capsys, monkeypatch):
    """Test main function when no args are provided (using sys.argv)."""
    # Mock sys.argv to be empty
    monkeypatch.setattr("sys.argv", ["repolint"])

    # Call main without args to trigger sys.argv[1:] usage
    result = main()

    assert result == 1
    captured = capsys.readouterr()
    assert "usage:" in captured.out.lower()


def test_cli_main_unknown_command(capsys):
    """Test main function with an unknown command."""
    with pytest.raises(SystemExit) as exc_info:
        main(["unknown-command"])

    assert exc_info.value.code == 2
    captured = capsys.readouterr()
    assert "invalid choice: 'unknown-command'" in captured.err
    assert "choose from 'lint', 'list', 'init'" in captured.err


def test_cli_main_command_not_in_handlers(monkeypatch, capsys):
    """Test main function when command is not in handlers dict."""

    # Create a mock parser that returns a command not in handlers
    class MockParser:
        def parse_args(self, args):
            class MockArgs:
                command = "nonexistent"

            return MockArgs()

        def print_help(self):
            print("Mock help message")

    # Mock create_parser to return our mock parser
    monkeypatch.setattr("repolint.cli.create_parser", lambda: MockParser())

    result = main(["nonexistent"])

    assert result == 1
    captured = capsys.readouterr()
    assert (
        "Mock help message" not in captured.out
    )  # Help shouldn't be shown for unknown command


def test_cli_lint_interactive_fix(
    capsys, mock_config, mock_github, test_env, monkeypatch
):
    """Test lint command with interactive fix prompts."""
    # Create config with a test rule set
    config = {
        "github_token": "env-token",
        "default_rule_set": "test",
        "repository_filter": {"include_patterns": [], "exclude_patterns": []},
        "rule_sets": {
            "test": {
                "name": "Test Rule Set",
                "rules": ["TEST001"],
            }
        },
        "repository_rule_sets": {},
    }
    config_path = mock_config(config)

    # Mock a repository that needs fixing
    class MockRepo:
        def __init__(self):
            self.name = "test-repo"
            self.html_url = "https://github.com/test/test-repo"

    # Mock GitHub client with a repository that needs fixing
    class MockGitHubClientWithRepo(mock_github):
        def get_repositories(self):
            return [MockRepo()]

    monkeypatch.setattr("repolint.github.GitHubClient", MockGitHubClientWithRepo)

    # Mock a rule that always needs fixing
    class MockRule(Rule):
        def __init__(self):
            super().__init__("TEST001", "Test rule")

        def check(self, context):
            return RuleCheckResult(
                result=RuleResult.FAILED,
                message="Test failed",
                fix_available=True,
                fix_description="This can be fixed",
            )

        def fix(self, context):
            return True, "Fixed test issue"

    # Mock RuleManager to return our test rule
    class MockRuleManager:
        def __init__(self):
            self._rules = {"TEST001": MockRule}
            self._rule_sets = {}

        def load_rule_sets_from_config(self, config):
            for rule_set_id, rule_set_config in config.rule_sets.items():
                self._rule_sets[rule_set_id] = self.create_rule_set(
                    rule_set_id, rule_set_config.name, rule_set_config.rules
                )

        def create_rule_set(self, rule_set_id, description, rule_ids):
            rule_set = RuleSet(rule_set_id, description)
            for rule_id in rule_ids:
                rule = self._rules[rule_id]()
                rule_set.add_rule(rule)
            return rule_set

        def get_rule_set(self, rule_set_id):
            return self._rule_sets.get(rule_set_id)

    monkeypatch.setattr("repolint.linter.RuleManager", MockRuleManager)

    # First test: User accepts the fix
    def mock_input_yes(prompt):
        # Print the prompt to stdout to ensure it's captured
        print(prompt, end="")
        return "y"

    monkeypatch.setattr("builtins.input", mock_input_yes)

    result = main(["lint", "--fix", "--config", str(config_path)])
    assert result == 0

    captured = capsys.readouterr()
    assert "Apply this fix? [y/N]:" in captured.out
    assert "Fixed test issue" in captured.out

    # Second test: User rejects the fix
    def mock_input_no(prompt):
        print(prompt, end="")
        return "n"

    monkeypatch.setattr("builtins.input", mock_input_no)

    result = main(["lint", "--fix", "--config", str(config_path)])
    assert result == 0

    captured = capsys.readouterr()
    assert "Apply this fix? [y/N]:" in captured.out
    assert "Fix skipped" in captured.out


def test_cli_lint_fix_error(capsys, mock_config, mock_github, test_env, monkeypatch):
    """Test lint command when fix application raises an exception."""

    # Mock rule that raises an exception during fix
    class FailingFixRule(Rule):
        def __init__(self):
            super().__init__("R001", "Rule with failing fix")

        def check(self, context):
            return RuleCheckResult(
                result=RuleResult.FAILED,
                message="Test failed",
                fix_available=True,
                fix_description="Fix available",
            )

        def fix(self, context):
            raise RuntimeError("Fix failed with test error")

    # Create test rule set with failing fix rule
    class MockRuleManager:
        def __init__(self):
            self._rules = {"R001": FailingFixRule}
            self._rule_sets = {}

        def load_rule_sets_from_config(self, config):
            for rule_set_id, rule_set_config in config.rule_sets.items():
                self._rule_sets[rule_set_id] = self.create_rule_set(
                    rule_set_id, rule_set_config.name, rule_set_config.rules
                )

        def create_rule_set(self, rule_set_id, description, rule_ids):
            rule_set = RuleSet(rule_set_id, description)
            for rule_id in rule_ids:
                rule = self._rules[rule_id]()
                rule_set.add_rule(rule)
            return rule_set

        def get_rule_set(self, rule_set_id):
            return self._rule_sets.get(rule_set_id)

    monkeypatch.setattr("repolint.linter.RuleManager", MockRuleManager)

    # Create config with fix enabled
    config = {
        "github_token": "env-token",
        "default_rule_set": "default",
        "repository_filter": {"include_patterns": [], "exclude_patterns": []},
        "rule_sets": {
            "default": {
                "name": "Default Rule Set",
                "rules": ["R001"],
            }
        },
        "repository_rule_sets": {},
    }
    config_file = mock_config(config)

    # Run lint with fix
    result = main(["lint", "--fix", "--config", str(config_file), "--non-interactive"])
    assert result == 0

    # Verify output shows fix error
    captured = capsys.readouterr()
    assert "Fix error: Fix failed with test error" in captured.out


def test_cli_lint_fix_failure(capsys, mock_config, mock_github, test_env, monkeypatch):
    """Test lint command when fix returns failure status."""

    # Mock rule that returns failure from fix
    class FailingFixRule(Rule):
        def __init__(self):
            super().__init__("R001", "Rule with failing fix")

        def check(self, context):
            return RuleCheckResult(
                result=RuleResult.FAILED,
                message="Test failed",
                fix_available=True,
                fix_description="Fix available",
            )

        def fix(self, context):
            return False, "Fix could not be applied"

    # Create test rule set with failing fix rule
    class MockRuleManager:
        def __init__(self):
            self._rules = {"R001": FailingFixRule}
            self._rule_sets = {}

        def load_rule_sets_from_config(self, config):
            for rule_set_id, rule_set_config in config.rule_sets.items():
                self._rule_sets[rule_set_id] = self.create_rule_set(
                    rule_set_id, rule_set_config.name, rule_set_config.rules
                )

        def create_rule_set(self, rule_set_id, description, rule_ids):
            rule_set = RuleSet(rule_set_id, description)
            for rule_id in rule_ids:
                rule = self._rules[rule_id]()
                rule_set.add_rule(rule)
            return rule_set

        def get_rule_set(self, rule_set_id):
            return self._rule_sets.get(rule_set_id)

    monkeypatch.setattr("repolint.linter.RuleManager", MockRuleManager)

    # Create config with fix enabled
    config = {
        "github_token": "env-token",
        "default_rule_set": "default",
        "repository_filter": {"include_patterns": [], "exclude_patterns": []},
        "rule_sets": {
            "default": {
                "name": "Default Rule Set",
                "rules": ["R001"],
            }
        },
        "repository_rule_sets": {},
    }
    config_file = mock_config(config)

    # Run lint with fix
    result = main(["lint", "--config", str(config_file), "--fix", "--non-interactive"])
    assert result == 0

    # Verify output shows fix failure
    captured = capsys.readouterr()
    assert "Fix failed: Fix could not be applied" in captured.out


def test_cli_lint_github_access_error(capsys, mock_config, test_env, monkeypatch):
    """Test lint command when GitHub API access raises an exception."""
    # Create a test config file
    config_file = mock_config(
        {
            "repositories": ["test-org/test-repo"],
            "rules": ["test-rule"],
            "github_token": "env-token",
        }
    )

    # Mock GitHub client to raise an exception
    class MockGitHubError(Exception):
        pass

    class MockGitHubClient:
        def __init__(self, *args, **kwargs):
            pass

        def get_repositories(self):
            raise MockGitHubError("Failed to access GitHub API")

    monkeypatch.setattr("repolint.github.GitHubClient", MockGitHubClient)

    # Run lint command
    with pytest.raises(SystemExit) as exc_info:
        main(["lint", "--config", str(config_file)])

    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "Error accessing GitHub: Failed to access GitHub API" in captured.out


def test_cli_lint_config_load_error(capsys, mock_config):
    """Test lint command when configuration loading raises an exception."""
    # Create an invalid YAML config file
    config_file = mock_config(
        {
            "repositories": "not-a-list",  # This will cause a validation error
            "rules": ["test-rule"],
        }
    )

    # Run lint command
    with pytest.raises(SystemExit) as exc_info:
        main(["lint", "--config", str(config_file)])

    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "Error loading configuration:" in captured.out


def test_cli_init_existing_file(capsys, tmp_path):
    """Test init command when output file already exists."""
    # Create a file that already exists
    output_file = tmp_path / "config.yml"
    output_file.write_text("")  # Create an empty file

    # Run init command with existing file path
    with pytest.raises(SystemExit) as exc_info:
        main(["init", "--output", str(output_file)])

    # Verify exit code and error message
    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert f"Error: File {output_file} already exists" in captured.out


def test_cli_init_parent_dir_exists(capsys, tmp_path):
    """Test init command when parent directory exists."""
    # Create parent directory
    parent_dir = tmp_path / "config"
    parent_dir.mkdir()
    output_file = parent_dir / "config.yml"

    # Run init command
    result = main(["init", "--output", str(output_file)])

    # Verify success
    assert result == 0
    assert output_file.exists()
