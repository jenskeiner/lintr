"""Tests for the CLI interface."""

import pytest

from repolint.cli import main


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


def test_cli_lint_basic(capsys):
    """Test basic lint command."""
    assert main(["lint"]) == 0
    captured = capsys.readouterr()
    assert ".repolint.yml" in captured.out


def test_cli_lint_with_options(capsys):
    """Test lint command with options."""
    assert main(["lint", "--fix", "--dry-run"]) == 0
    captured = capsys.readouterr()
    assert "auto-fix is enabled" in captured.out.lower()
    assert "dry-run mode is enabled" in captured.out.lower()


def test_cli_list_no_options(capsys):
    """Test list command without options."""
    assert main(["list"]) == 0
    captured = capsys.readouterr()
    assert "please specify" in captured.out.lower()


def test_cli_list_rules(capsys):
    """Test list command with --rules option."""
    assert main(["list", "--rules"]) == 0
    captured = capsys.readouterr()
    assert "available rules:" in captured.out.lower()


def test_cli_list_rule_sets(capsys):
    """Test list command with --rule-sets option."""
    assert main(["list", "--rule-sets"]) == 0
    captured = capsys.readouterr()
    assert "available rule-sets:" in captured.out.lower()


def test_cli_init_basic(capsys):
    """Test basic init command."""
    assert main(["init"]) == 0
    captured = capsys.readouterr()
    assert ".repolint.yml" in captured.out
