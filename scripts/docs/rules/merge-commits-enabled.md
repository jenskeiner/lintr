---
title: "merge-commits-enabled (G007P)"
draft: false
type: docs
layout: "single"
params:
  tags: ["G007P"]
menu:
  lintr:
    parent: "rules"
---

✅     This rule is stable.<br>
🛠️     This rule is automatically fixable by the `--fix` command-line option.<br>
⚙️     This rule is configurable.

## What it does

Checks that merge commits are enabled for pull requests.

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
