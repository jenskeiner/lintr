"""Tests for CLI fix handling."""

import argparse
from unittest.mock import MagicMock, patch

from lintr.cli import handle_lint


def test_fix_option_is_passed_to_linter(config_file):
    """Test that the --fix option is correctly passed to the Linter."""
    # Set up args
    args = argparse.Namespace()
    args.fix = True
    args.dry_run = False
    args.non_interactive = False
    args.include_organisations = False
    args.config = str(config_file.path)

    # Mock the GitHub client and Linter
    mock_client = MagicMock()
    mock_client.get_repositories.return_value = []

    mock_linter = MagicMock()

    with patch("lintr.gh.GitHubClient", return_value=mock_client), patch(
        "lintr.linter.Linter", return_value=mock_linter
    ) as mock_linter_class:
        # Run the command
        handle_lint(args)

        # Verify that Linter was created with fix=True
        mock_linter_class.assert_called_once()
        _, kwargs = mock_linter_class.call_args
        assert "fix" in kwargs, "fix parameter not passed to Linter"
        assert kwargs["fix"] is True, "fix parameter not set to True"
