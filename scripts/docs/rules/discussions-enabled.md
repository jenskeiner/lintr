---
title: "discussions-enabled (G005P)"
draft: false
type: docs
layout: "single"
params:
  tags: ["G005P"]
menu:
  lintr:
    parent: "rules"
---

✅     This rule is stable.<br>
🛠️     This rule is automatically fixable by the `--fix` command-line option.<br>
⚙️     This rule is configurable.

## What it does

Checks that Discussions are enabled in the General settings.

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
