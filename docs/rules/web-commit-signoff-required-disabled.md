---
title: "web-commit-signoff-required-disabled (G001N)"
draft: false
type: docs
layout: "single"
params:
  tags: ["G001N"]
menu:
  lintr:
    parent: "rules"
---

✅  This rule is stable.

🛠️ This rule is automatically fixable by the `--fix` command-line option.

⚙️ This rule is configurable

↔️ This rule is mutually exclusive with [G001P](../web-commit-signoff-required-enabled/)
## What it does

Checks that the repository has _Require contributors to sign off on web-based commits_ disabled in the General settings.

## Configuration

Example:

```yaml
target: false
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
