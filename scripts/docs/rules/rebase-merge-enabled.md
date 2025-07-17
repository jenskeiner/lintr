---
title: "rebase-merge-enabled (G009P)"
draft: false
type: docs
layout: "single"
params:
  tags: ["G009P"]
menu:
  lintr:
    parent: "rules"
---

✅     This rule is stable.<br>
🛠️     This rule is automatically fixable by the `--fix` command-line option.<br>
⚙️     This rule is configurable.

## What it does

Checks that rebase merging is enabled for pull requests.

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
