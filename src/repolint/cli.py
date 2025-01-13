"""Command-line interface for Repolint."""

import argparse
import sys
from typing import List, Optional

from repolint import __version__


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
    if args.rules:
        print("Available rules:")
        print("  - No rules implemented yet")
    if args.rule_sets:
        print("Available rule-sets:")
        print("  - No rule-sets implemented yet")
    if not (args.rules or args.rule_sets):
        print("Please specify --rules and/or --rule-sets")


def handle_init(args: argparse.Namespace) -> None:
    """Handle the init command."""
    print(f"Would create new configuration file at {args.output}")


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
