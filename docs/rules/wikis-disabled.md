---
title: "wikis-disabled (G002N)"
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

Checks that _Wikis_ are disabled in the General settings.

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
