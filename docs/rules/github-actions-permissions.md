---
title: "github-actions-permissions (A001)"
draft: false
type: docs
layout: "single"
params:
  tags: ["A001"]
menu:
  lintr:
    parent: "rules"
---

✅     This rule is stable.<br>
🔷     This rule is abstract.<br>
🛠️     This rule is automatically fixable by the `--fix` command-line option.<br>
⚙️     This rule is configurable.

## What it does

Checks GitHub Actions permissions for a repository

## Configuration

Example:

```yaml
github_owned_allowed: true
verified_allowed: true
patterns_allowed:
- owner/repo
```

Schema:

```json
{
  "oneOf": [
    {
      "$ref": "#/$defs/ActionsDisabledRuleConfig"
    },
    {
      "oneOf": [
        {
          "$ref": "#/$defs/ActionsEnabledAllRuleConfig"
        },
        {
          "$ref": "#/$defs/ActionsEnabledLocalOnlyRuleConfig"
        },
        {
          "$ref": "#/$defs/ActionsEnabledSelectedRuleConfig"
        }
      ],
      "discriminator": {
        "propertyName": "allowed_actions",
        "mapping": {
          "all": "#/$defs/ActionsEnabledAllRuleConfig",
          "local_only": "#/$defs/ActionsEnabledLocalOnlyRuleConfig",
          "selected": "#/$defs/ActionsEnabledSelectedRuleConfig"
        }
      }
    }
  ],
  "discriminator": {
    "propertyName": "enabled",
    "mapping": {
      "False": "#/$defs/ActionsDisabledRuleConfig",
      "True": {
        "oneOf": [
          {
            "$ref": "#/$defs/ActionsEnabledAllRuleConfig"
          },
          {
            "$ref": "#/$defs/ActionsEnabledLocalOnlyRuleConfig"
          },
          {
            "$ref": "#/$defs/ActionsEnabledSelectedRuleConfig"
          }
        ],
        "discriminator": {
          "propertyName": "allowed_actions",
          "mapping": {
            "all": "#/$defs/ActionsEnabledAllRuleConfig",
            "local_only": "#/$defs/ActionsEnabledLocalOnlyRuleConfig",
            "selected": "#/$defs/ActionsEnabledSelectedRuleConfig"
          }
        }
      }
    }
  },
  "$defs": {
    "ActionsDisabledRuleConfig": {
      "type": "object",
      "properties": {
        "enabled": {
          "const": false,
          "type": "boolean",
          "default": false,
          "description": "Whether GitHub Actions should be enabled for the repository",
          "title": "Enabled"
        }
      },
      "title": "ActionsDisabledRuleConfig",
      "description": "Configuration when GitHub Actions are disabled.",
      "additionalProperties": false
    },
    "ActionsEnabledAllRuleConfig": {
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
          "const": "all",
          "type": "string",
          "default": "all",
          "description": "Which actions are allowed to run",
          "title": "Allowed Actions"
        }
      },
      "title": "ActionsEnabledAllRuleConfig",
      "description": "Configuration when GitHub Actions are enabled with ALL policy.",
      "additionalProperties": false
    },
    "ActionsEnabledLocalOnlyRuleConfig": {
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
          "const": "local_only",
          "type": "string",
          "default": "local_only",
          "description": "Which actions are allowed to run",
          "title": "Allowed Actions"
        }
      },
      "title": "ActionsEnabledLocalOnlyRuleConfig",
      "description": "Configuration when GitHub Actions are enabled with LOCAL_ONLY policy.",
      "additionalProperties": false
    },
    "ActionsEnabledSelectedRuleConfig": {
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
  }
}
```
