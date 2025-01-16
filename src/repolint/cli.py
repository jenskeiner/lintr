"""Command-line interface for Repolint."""

import argparse
import os
import shutil
import sys
from pathlib import Path
from typing import List, Optional

from repolint import __version__

# Path to the default configuration template
DEFAULT_CONFIG_TEMPLATE = Path(__file__).parent / "templates" / "default_config.yml"


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        description="Repolint - A tool to lint and enforce consistent settings across GitHub repositories.",
        prog="repolint"
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"repolint {__version__}"
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Lint command
    lint_parser = subparsers.add_parser(
        "lint",
        help="Lint repositories according to configured rules"
    )
    lint_parser.add_argument(
        "--config",
        help="Path to configuration file",
        default=".repolint.yml"
    )
    lint_parser.add_argument(
        "--fix",
        action="store_true",
        help="Attempt to fix issues automatically"
    )
    lint_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )

    # List command
    list_parser = subparsers.add_parser(
        "list",
        help="List available rules and rule-sets"
    )
    list_parser.add_argument(
        "--rules",
        action="store_true",
        help="List available rules"
    )
    list_parser.add_argument(
        "--rule-sets",
        action="store_true",
        help="List available rule-sets"
    )

    # Init command
    init_parser = subparsers.add_parser(
        "init",
        help="Initialize a new configuration file"
    )
    init_parser.add_argument(
        "--output",
        help="Path to write configuration file",
        default=".repolint.yml"
    )

    return parser


def handle_lint(args: argparse.Namespace) -> None:
    """Handle the lint command."""
    print(f"Would lint repositories using config from {args.config}")
    if args.fix:
        print("Auto-fix is enabled")
    if args.dry_run:
        print("Dry-run mode is enabled")


def handle_list(args: argparse.Namespace) -> None:
    """Handle the list command."""
    from repolint.rule_manager import RuleManager
    
    # Get singleton instance
    manager = RuleManager()
    
    if args.rules:
        print("Available rules:")
        rules = manager.get_all_rules()
        if not rules:
            print("  No rules implemented yet")
        else:
            for rule_id, rule in sorted(rules.items()):
                print(f"  {rule_id}: {rule.description}")
    
    if args.rule_sets:
        print("Available rule-sets:")
        rule_sets = manager.get_all_rule_sets()
        if not rule_sets:
            print("  No rule-sets implemented yet")
        else:
            for rule_set_id, rule_set in sorted(rule_sets.items()):
                print(f"  {rule_set_id}: {rule_set.description}")
    
    if not (args.rules or args.rule_sets):
        print("Please specify --rules and/or --rule-sets")


def handle_init(args: argparse.Namespace) -> None:
    """Handle the init command."""
    output_path = Path(args.output)
    
    if output_path.exists():
        print(f"Error: File {output_path} already exists. Use a different path or remove the existing file.")
        sys.exit(1)
    
    try:
        # Create parent directories if they don't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy the default configuration template
        shutil.copy2(DEFAULT_CONFIG_TEMPLATE, output_path)
        
        print(f"Created new configuration file at {output_path}")
        print("\nNext steps:")
        print("1. Edit the configuration file to set your GitHub token")
        print("2. Configure the repositories you want to check")
        print("3. Adjust rule sets and settings as needed")
        print("\nRun 'repolint list --rules' to see available rules")
    except Exception as e:
        print(f"Error creating configuration file: {e}")
        sys.exit(1)


def main(args: Optional[List[str]] = None) -> int:
    """Main entry point for the CLI.
    
    Args:
        args: Command line arguments. If None, sys.argv[1:] is used.
    
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    if args is None:
        args = sys.argv[1:]
    
    parser = create_parser()
    parsed_args = parser.parse_args(args)

    if not parsed_args.command:
        parser.print_help()
        return 1

    # Handle commands
    handlers = {
        "lint": handle_lint,
        "list": handle_list,
        "init": handle_init,
    }
    
    handler = handlers.get(parsed_args.command)
    if handler:
        handler(parsed_args)
        return 0
    
    return 1


if __name__ == "__main__":
    sys.exit(main())
