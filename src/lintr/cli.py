"""Command-line interface for Lintr."""

import argparse
import shutil
import sys
from pathlib import Path

from lintr import __version__
from lintr.config import create_config_class

# Path to the default configuration template
DEFAULT_CONFIG_TEMPLATE = Path(__file__).parent / "templates" / "default_config.yml"


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        description="Lintr - A tool to lint and enforce consistent settings across GitHub repositories.",
        prog="lintr",
    )
    parser.add_argument("--version", action="version", version=f"lintr {__version__}")

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Lint command
    lint_parser = subparsers.add_parser(
        "lint", help="Lint repositories according to configured rules"
    )
    lint_parser.add_argument(
        "--config", help="Path to configuration file", default="lintr.yml"
    )
    lint_parser.add_argument(
        "--fix", action="store_true", help="Attempt to fix issues automatically"
    )
    lint_parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Apply fixes without prompting for confirmation",
    )
    lint_parser.add_argument(
        "--include-organisations",
        action="store_true",
        help="Include organisation repositories in addition to user repositories",
    )
    lint_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )

    # List command
    list_parser = subparsers.add_parser(
        "list", help="List available rules and rule-sets"
    )
    list_parser.add_argument(
        "--rules", action="store_true", help="List available rules"
    )
    list_parser.add_argument(
        "--rule-sets", action="store_true", help="List available rule-sets"
    )

    # Init command
    init_parser = subparsers.add_parser(
        "init", help="Initialize a new configuration file"
    )
    init_parser.add_argument(
        "--output", help="Path to write configuration file", default="lintr.yml"
    )

    # Help command
    _ = subparsers.add_parser("help", help="Show this help message and exit")

    return parser


def handle_lint(args: argparse.Namespace) -> None:
    """Handle the lint command."""
    try:
        # # Check if config file exists
        config_path = Path(args.config)
        # if not config_path.exists():
        #     print(f"Error: Configuration file not found: {args.config}")
        #     print("Run 'lintr init' to create a new configuration file")
        #     sys.exit(1)

        # Load and validate configuration from all sources
        LintrConfig = create_config_class(config_path)
        config = LintrConfig()

        # Validate GitHub token
        if not config.github_token:
            print("Error: GitHub token not configured.")
            print("Either:")
            print("  1. Set it in your configuration file")
            print("  2. Set the GITHUB_TOKEN environment variable")
            print("  3. Set the LINTR_GITHUB_TOKEN environment variable")
            sys.exit(1)

        # Show what we're about to do
        print(f"Using configuration from {args.config}")
        if args.fix:
            print("Auto-fix is enabled - will attempt to fix issues automatically")
            if args.non_interactive:
                print(
                    "Non-interactive mode is enabled - fixes will be applied without prompting"
                )
        if args.dry_run:
            print("Dry-run mode is enabled - no changes will be made")

        # Create GitHub client with configuration
        from lintr.gh import GitHubClient, GitHubConfig
        from lintr.linter import Linter

        github_config = GitHubConfig(
            token=config.github_token,
            include_private=True,  # TODO: Make configurable
            include_organisations=getattr(args, "include_organisations", False),
            repository_filter=config.repository_filter,
        )
        client = GitHubClient(github_config)

        # Get repositories
        print("\nEnumerating repositories...")
        try:
            repos = client.get_repositories()
            print(f"Found {len(repos)} repositories")

            # Create linter and process repositories
            linter = Linter(
                config,
                dry_run=args.dry_run,
                non_interactive=args.non_interactive,
                fix=args.fix,
            )
            linter.lint_repositories(repos)

            # TODO: Display results

        except Exception as e:
            print(f"Error accessing GitHub: {e}")
            sys.exit(1)

    except Exception as e:
        print(f"Error loading configuration: {e}")
        sys.exit(1)


def handle_list(args: argparse.Namespace) -> None:
    """Handle the list command."""
    from lintr.rule_manager import RuleManager

    try:
        # Get singleton instance
        manager = RuleManager()

        if args.rules:
            print("Available rules:")
            try:
                rules = manager.get_all_rules()
                if not rules:
                    print("  No rules implemented yet")
                else:
                    for rule_id, rule in sorted(rules.items()):
                        print(f"  {rule_id}: {rule.description}")
            except Exception as e:
                print(f"Error: Failed to load rules: {e}", file=sys.stderr)
                sys.exit(1)

        if args.rule_sets:
            print("Available rule-sets:")
            try:
                rule_sets = manager.get_all_rule_sets()
                if not rule_sets:
                    print("  No rule-sets implemented yet")
                else:
                    for rule_set_id, rule_set in sorted(rule_sets.items()):
                        print(f"  {rule_set_id}: {rule_set.description}")
            except Exception as e:
                print(f"Error: Failed to load rule sets: {e}", file=sys.stderr)
                sys.exit(1)

        if not (args.rules or args.rule_sets):
            print("Please specify --rules and/or --rule-sets")
    except Exception as e:
        print(f"Error: Failed to initialize RuleManager: {e}", file=sys.stderr)
        sys.exit(1)


def handle_init(args: argparse.Namespace) -> None:
    """Handle the init command."""
    output_path = Path(args.output)

    if output_path.exists():
        print(
            f"Error: File {output_path} already exists. Use a different path or remove the existing file."
        )
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
        print("\nRun 'lintr list --rules' to see available rules")
    except Exception as e:
        print(f"Error creating configuration file: {e}")
        sys.exit(1)


def handle_help(args: argparse.Namespace) -> None:
    """Handle the help command."""
    parser = create_parser()
    parser.print_help()


def main(args: list[str] | None = None) -> int:
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
        "help": handle_help,
    }

    handler = handlers.get(parsed_args.command)
    if handler:
        handler(parsed_args)
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
