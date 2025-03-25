---
title: "web-commit-signoff-required-enabled (G001P)"
draft: false
type: docs
layout: "single"
params:
  tags: ["G001P"]
menu:
  lintr:
    parent: "rules"
---

✅  This rule is stable.

🛠️ This rule is automatically fixable by the `--fix` command-line option.

⚙️ This rule is configurable

↔️ This rule is mutually exclusive with [G001N](../web-commit-signoff-required-disabled/)
## What it does

Checks that the repository has _Require contributors to sign off on web-based commits_ enabled in the General settings.

## Configuration

Example:

```yaml
target: true
```

Schema:

```json
{
  "type": "object",
  "properties": {
    "target": {
      "type": "boolean",
      "title": "Target"
    }
  },
  "required": [
    "target"
  ],
  "title": "BinaryFlagRuleConfig",
  "additionalProperties": false
}
```
