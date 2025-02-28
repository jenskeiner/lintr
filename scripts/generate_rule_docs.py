#!/usr/bin/env python3
"""Script to generate documentation for all lintr rules."""

import json
import yaml
from io import StringIO
from collections import defaultdict
from typing import get_args, get_origin

from lintr.rule_manager import RuleManager
from lintr.rules.base import (
    Rule,
    BaseRuleConfig,
    RuleCategory,
    RuleCategoryValue,
    RuleStatus,
)
from pydantic.json_schema import GenerateJsonSchema, JsonSchemaValue


class MyGenerateJsonSchema(GenerateJsonSchema):
    def sort(
        self, value: JsonSchemaValue, parent_key: str | None = None
    ) -> JsonSchemaValue:
        """No-op, we don't want to sort schema values at all."""
        return value


def get_rule_parameter_class(rule_cls: type[Rule]) -> type[BaseRuleConfig]:
    """Extract the parameter class (ConfigT) from a Rule subclass.

    Args:
        rule_cls: The Rule subclass to analyze

    Returns:
        The parameter class used by this rule
    """
    # Look through the class's bases to find the Rule generic specialization
    for base in rule_cls.__orig_bases__:
        if (
            get_origin(base) is Rule
            and len(get_args(base)) == 1
            and issubclass(get_args(base)[0], BaseRuleConfig)
        ):
            return get_args(base)[0]

    # If we didn't find it in direct bases, check if the rule uses the default config
    if hasattr(rule_cls, "_config"):
        return type(rule_cls._config)

    return BaseRuleConfig


def collect_rules():
    """Collect all available rules and their parameter classes.

    Returns:
        A dictionary mapping RuleCategory values to lists of (rule_class, param_class) tuples
    """
    # Initialize the rule manager to discover all rules
    rule_manager = RuleManager()

    # Group rules by their category
    rules_by_category = defaultdict(list)

    for rule_id, rule in rule_manager.get_all_rules().items():
        # Skip RuleSets, we only want Rule classes
        if not isinstance(rule, type) or not issubclass(rule, Rule):
            continue

        # Get the rule's category, defaulting to MISC if not specified
        category = getattr(rule, "_category", RuleCategory.MISC)
        param_class = get_rule_parameter_class(rule)
        rules_by_category[category].append((rule, param_class))

    return rules_by_category


def generate_rule_doc(
    rule_cls: type[Rule],
    param_cls: type[BaseRuleConfig],
    output_dir: str = "docs/rules",
):
    """Generate markdown documentation for a single rule.

    Args:
        rule_cls: The Rule class to document
        param_cls: The parameter class for the rule
        output_dir: Directory where to output the rule documentation
    """
    output = []

    # Add frontmatter
    output.append("---")
    output.append(f'title: "{rule_cls._name} ({rule_cls._id})"')
    output.append("draft: false")
    output.append("type: docs")
    output.append('layout: "single"')
    output.append("menu:")
    output.append("  docs_lintr:")
    output.append('    parent: "rules"')
    output.append("---\n")

    # Add rule header
    # output.append(f"# {rule_cls._name} ({rule_cls._id})\n")

    # Add status indicators
    if rule_cls._status is RuleStatus.STABLE:
        output.append("✅  This rule is stable.\n")
    else:
        output.append("🧪 This rule is unstable and is in preview.\n")

    if rule_cls._abstract:
        output.append("🔷 This rule is abstract.\n")

    if rule_cls._deprecated:
        output.append(
            "⚠️ This rule has been deprecated and will be removed in a future release.\n"
        )

    if rule_cls._fixable:
        output.append(
            "🛠️ This rule is automatically fixable by the `--fix` command-line option.\n"
        )

    if rule_cls._configurable:
        output.append("⚙️ This rule is configurable\n")

    if len(rule_cls._mutually_exclusive_with_resolved) > 0:
        output.append(
            "↔️ This rule is mutually exclusive with "
            + ", ".join(
                [
                    f"[{r._id}](../{r._name}/)"
                    for r in rule_cls._mutually_exclusive_with_resolved
                ]
            )
        )

    # Add description and message
    output.append("## What it does")
    output.append(f"\n{rule_cls._description}\n")

    # Add parameter class info if it's not the default
    if param_cls is not BaseRuleConfig:
        output.append("## Configuration")
        output.append("\nExample:\n")
        output.append("```yaml")
        stream = StringIO()
        yaml.dump(rule_cls._example.model_dump(), stream)
        output.append(stream.getvalue().strip("\n"))
        output.append("```\n")
        stream.close()

        output.append("Schema:\n")
        output.append("```json")
        schema = param_cls.model_json_schema(schema_generator=MyGenerateJsonSchema)
        output.append(json.dumps(schema, indent=2))
        output.append("```\n")

    # Create output directory if it doesn't exist
    import os

    os.makedirs(output_dir, exist_ok=True)

    # Write the output file
    output_file = os.path.join(output_dir, f"{rule_cls._name}.md")
    with open(output_file, "w") as f:
        f.write("\n".join(output))


def generate_markdown(rules_by_category):
    """Generate markdown documentation for all rules.

    Args:
        rules_by_category: Dictionary mapping RuleCategory values to lists of
            (rule_class, param_class) tuples
    """
    # Clear target directory
    import os
    import shutil

    output_dir = "docs/rules"
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)

    output = []

    output.append(
        "---\n"
        'title: "Rules"\n'
        "draft: false\n"
        "type: docs\n"
        'layout: "single"\n'
        "menu:\n"
        "  docs_lintr:\n"
        '    identifier: "rules"\n'
        "    weight: 2\n"
        "---\n"
    )

    output.append(
        f"Lintr currently supports {sum(len(rules) for rules in rules_by_category.values())} rules.\n"
    )
    output.append("### Legend\n")
    output.append("✅ The rule is stable.\n")
    output.append("🧪 The rule is unstable and is in preview.\n")
    output.append("🔷 The rule is abstract.\n")
    output.append(
        "⚠️ The rule has been deprecated and will be removed in a future release.\n"
    )
    output.append(
        "🛠️ The rule is automatically fixable by the `--fix` command-line option.\n"
    )
    output.append("⚙️ The rule is configurable.\n")

    # Sort categories by their enum values to ensure consistent order
    for category in sorted(rules_by_category.keys(), key=lambda x: x.value.code):
        category_value: RuleCategoryValue = category.value

        output.append(f"\n### {category_value.name} ({category_value.code})\n")
        output.append(category_value.description)

        # Sort rules by their ID within each category
        rules = sorted(rules_by_category[category], key=lambda x: x[0]._id)

        output.append("| Code | Name | Message | Properties |")
        output.append("|-----|-----|-----|-----|")

        for rule_cls, param_cls in rules:
            # Generate individual rule documentation
            generate_rule_doc(rule_cls, param_cls)

            status = []
            if rule_cls._status is RuleStatus.STABLE:
                status.append("✅")
            else:
                status.append("🧪")

            if rule_cls._abstract:
                status.append("🔷")

            if rule_cls._deprecated:
                status.append("⚠️")

            if rule_cls._fixable:
                status.append("🛠️")

            if rule_cls._configurable:
                status.append("⚙️")

            rule_link = f"[{rule_cls._name}]({rule_cls._name}/)"
            output.append(
                f"| {rule_cls._id} | {rule_link} | {rule_cls._message} | {' '.join(status)} |"
            )

    # Write the output file
    with open("docs/rules/_index.md", "w") as f:
        f.write("\n".join(output))


def main():
    """Main entry point."""
    rules = collect_rules()

    # For now, just print what we found
    for category, rule_list in rules.items():
        print(f"\nCategory: {category}")
        for rule_cls, param_cls in rule_list:
            print(f"  Rule: {rule_cls._id} ({rule_cls.__name__})")
            print(f"    Description: {rule_cls._description}")
            print(f"    Parameters: {param_cls.__name__}")

            # Only show schema for non-default parameter classes
            if param_cls is not BaseRuleConfig:
                schema = param_cls.model_json_schema(
                    schema_generator=MyGenerateJsonSchema
                )
                # Format the schema nicely
                schema_str = json.dumps(schema, indent=2)
                # Indent each line to align with our output structure
                schema_str = "\n".join(
                    "      " + line for line in schema_str.split("\n")
                )
                print(f"    Schema:\n{schema_str}")
    generate_markdown(rules)
    print("Generated rules documentation in rules_reference.md")


if __name__ == "__main__":
    main()
