---
title: "github-actions-enabled-selected (A001S)"
draft: false
type: docs
layout: "single"
params:
  tags: ["A001S"]
menu:
  lintr:
    parent: "rules"
---

✅     This rule is stable.<br>
🛠️     This rule is automatically fixable by the `--fix` command-line option.<br>
⚙️     This rule is configurable.

## What it does

Checks that only selected GitHub Actions are enabled for the repository

## Configuration

Example:

```yaml
github_owned_allowed: true
verified_allowed: true
patterns_allowed: []
```

Schema:

```json
{
  "type": "object",
  "properties": {
    "enabled": {
      "const": true,
      "type": "boolean",
      "default": true,
      "description": "Whether GitHub Actions should be enabled for the repository",
      "title": "Enabled"
    },
    "allowed_actions": {
      "const": "selected",
      "type": "string",
      "default": "selected",
      "description": "Which actions are allowed to run",
      "title": "Allowed Actions"
    },
    "github_owned_allowed": {
      "type": "boolean",
      "default": false,
      "description": "Whether GitHub-owned actions are allowed",
      "title": "Github Owned Allowed"
    },
    "verified_allowed": {
      "type": "boolean",
      "default": false,
      "description": "Whether verified actions are allowed",
      "title": "Verified Allowed"
    },
    "patterns_allowed": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "Specific patterns of actions that are allowed",
      "title": "Patterns Allowed"
    }
  },
  "title": "ActionsEnabledSelectedRuleConfig",
  "description": "Configuration when GitHub Actions are enabled with SELECTED policy.",
  "additionalProperties": false
}
```
