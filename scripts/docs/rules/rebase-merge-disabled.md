---
title: "rebase-merge-disabled (G009N)"
draft: false
type: docs
layout: "single"
menu:
  docs_lintr:
    parent: "rules"
---

✅  This rule is stable.

🛠️ This rule is automatically fixable by the `--fix` command-line option.

⚙️ This rule is configurable

## What it does

Checks that rebase merging is disabled for pull requests.

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
