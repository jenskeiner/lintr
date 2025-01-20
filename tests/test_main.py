"""Tests for main entry point."""

from unittest.mock import patch


def test_main_entry_point():
    """Test the main entry point."""
    with patch('repolint.cli.main') as mock_main:
        mock_main.return_value = 0
        
        # Import __main__ after patching to ensure patch takes effect
        import repolint.__main__
        
        # Call the main function as if from command line
        with patch.object(repolint.__main__, '__name__', '__main__'):
            repolint.__main__.main()
            
        # Verify main was called
        mock_main.assert_called_once()
