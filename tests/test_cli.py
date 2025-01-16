"""Tests for the CLI interface."""

import pytest

from repolint.cli import main
from repolint.rules.base import Rule, RuleSet, RuleCheckResult, RuleResult
from repolint.rules.context import RuleContext
import os
import tempfile
from pathlib import Path
import yaml


class TestRule(Rule):
    """Test rule implementation for testing."""
    
    def __init__(self, rule_id: str, description: str):
        super().__init__(rule_id, description)
    
    def check(self, context: RuleContext) -> RuleCheckResult:
        """Always returns PASSED."""
        return RuleCheckResult(RuleResult.PASSED, "Test passed")


class TestRuleSet(RuleSet):
    """Test rule set implementation for testing."""
    
    def __init__(self, rule_set_id: str, description: str):
        super().__init__(rule_set_id, description)
        self.add_rule(TestRule("R001", "Test rule 1"))
        self.add_rule(TestRule("R002", "Test rule 2"))


@pytest.fixture
def mock_config():
    """Create a temporary configuration file with given content."""
    def _create_config(content: dict) -> Path:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.dump(content, f)
            return Path(f.name)
    yield _create_config
    # Clean up any created files
    for file in Path('.').glob('*.yml'):
        if file.is_file() and 'tmp' in str(file):
            file.unlink()

@pytest.fixture
def mock_github_token():
    """Set up a mock GitHub token in environment."""
    token = "mock-github-token"
    os.environ["GITHUB_TOKEN"] = token
    yield token
    del os.environ["GITHUB_TOKEN"]

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
                MockRepository("test-repo-2", private=True, archived=True)
            ]

    monkeypatch.setattr("repolint.github.GitHubClient", MockGitHubClient)
    return MockGitHubClient

@pytest.fixture
def mock_config_file(mock_config):
    """Create a default configuration file."""
    config = {
        "github_token": "test-token",
        "default_rule_set": "default",
        "repository_filter": {
            "include_patterns": [],
            "exclude_patterns": []
        },
        "rule_sets": {},
        "repository_rule_sets": {}
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


def test_cli_lint_basic(capsys, mock_github_token, mock_github, mock_config_file):
    """Test basic lint command."""
    result = main(["lint", "--config", str(mock_config_file)])
    assert result == 0
    captured = capsys.readouterr()
    assert str(mock_config_file) in captured.out
    assert "Found 2 repositories" in captured.out


def test_cli_lint_with_options(capsys, mock_github_token, mock_github, mock_config_file):
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
    
    monkeypatch.setattr("repolint.rule_manager.RuleManager.get_all_rules", mock_get_all_rules)
    monkeypatch.setattr("repolint.rule_manager.RuleManager.get_all_rule_sets", mock_get_all_rule_sets)
    
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
    
    monkeypatch.setattr("repolint.rule_manager.RuleManager.get_all_rules", mock_get_all_rules)
    
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
    
    monkeypatch.setattr("repolint.rule_manager.RuleManager.get_all_rules", mock_get_all_rules)
    
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
    
    monkeypatch.setattr("repolint.rule_manager.RuleManager.get_all_rule_sets", mock_get_all_rule_sets)
    
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
    
    monkeypatch.setattr("repolint.rule_manager.RuleManager.get_all_rule_sets", mock_get_all_rule_sets)
    
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
            "exclude_patterns": ["test-repo-excluded"]
        },
        "rule_sets": {
            "test-ruleset": {
                "name": "test-ruleset",
                "rules": ["R001"]
            }
        },
        "repository_rule_sets": {}
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


def test_cli_lint_with_mock_github(capsys, mock_config, mock_github_token, mock_github):
    """Test lint command with mocked GitHub API responses."""
    # Define mock repository data
    mock_repos = [
        {
            "name": "test-repo-1",
            "private": False,
            "archived": False
        },
        {
            "name": "test-repo-2",
            "private": True,
            "archived": True
        }
    ]
    
    # Define mock settings for each repository
    mock_settings = {
        "test-repo-1": {
            "default_branch": "main",
            "has_issues": True,
            "allow_squash_merge": True
        },
        "test-repo-2": {
            "default_branch": "master",
            "has_issues": False,
            "allow_squash_merge": False
        }
    }
    
    # Create test configuration
    config = {
        "github_token": mock_github_token,
        "default_rule_set": "default",
        "repository_filter": {
            "include_patterns": ["test-repo-*"],
            "exclude_patterns": []
        },
        "rule_sets": {
            "test-ruleset": {
                "name": "test-ruleset",
                "rules": ["R001"]
            }
        },
        "repository_rule_sets": {}
    }
    config_path = mock_config(config)
    
    # Run lint command
    result = main(["lint", "--config", str(config_path)])
    assert result == 0
    
    # Verify output
    captured = capsys.readouterr()
    assert str(config_path) in captured.out
    assert "Found 2 repositories" in captured.out
