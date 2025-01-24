"""Tests for CLI fix handling."""

import argparse
from unittest.mock import MagicMock, patch

import pytest

from repolint.cli import handle_lint


@pytest.fixture
def mock_config_file(tmp_path):
    """Create a mock config file."""
    config_file = tmp_path / ".repolint.yml"
    config_file.write_text("github_token: test-token")
    return config_file


@pytest.fixture
def mock_args():
    """Create mock CLI arguments."""
    args = argparse.Namespace()
    args.fix = False
    args.dry_run = False
    args.non_interactive = False
    args.include_organisations = False
    return args


def test_fix_option_is_passed_to_linter(mock_config_file, mock_args):
    """Test that the --fix option is correctly passed to the Linter."""
    # Set up args
    mock_args.config = str(mock_config_file)
    mock_args.fix = True  # Enable fix mode

    # Mock the GitHub client and Linter
    mock_client = MagicMock()
    mock_client.get_repositories.return_value = []

    mock_linter = MagicMock()

    with patch("repolint.github.GitHubClient", return_value=mock_client), patch(
        "repolint.linter.Linter", return_value=mock_linter
    ) as mock_linter_class:
        # Run the command
        handle_lint(mock_args)

        # Verify that Linter was created with fix=True
        mock_linter_class.assert_called_once()
        _, kwargs = mock_linter_class.call_args
        assert "fix" in kwargs, "fix parameter not passed to Linter"
        assert kwargs["fix"] is True, "fix parameter not set to True"
