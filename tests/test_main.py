"""Tests for main entry point."""

from unittest.mock import patch
import runpy


def test_main_entry_point():
    """Test the main entry point."""
    with patch("repolint.cli.main") as mock_main:
        mock_main.return_value = (
            42  # arbitrary return value to verify it's passed to sys.exit
        )
        with patch("sys.exit") as mock_exit:
            # Run the module as if it was executed with python -m repolint
            runpy.run_module("repolint", run_name="__main__")

            # Verify cli.main was called
            mock_main.assert_called_once()

            # Verify sys.exit was called with cli.main's return value
            mock_exit.assert_called_once_with(42)
