---
title: "auto-merge-disabled (G010N)"
draft: false
type: docs
layout: "single"
params:
  tags: ["G010N"]
menu:
  lintr:
    parent: "rules"
---

✅     This rule is stable.<br>
🛠️     This rule is automatically fixable by the `--fix` command-line option.<br>
⚙️     This rule is configurable.

## What it does

Checks that 'Allow auto-merge' is disabled for a repository.

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
