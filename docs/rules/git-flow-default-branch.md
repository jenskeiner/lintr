---
title: "git-flow-default-branch (GF002)"
draft: false
type: docs
layout: "single"
params:
  tags: ["GF002"]
menu:
  lintr:
    parent: "rules"
---

✅  This rule is stable.

🛠️ This rule is automatically fixable by the `--fix` command-line option.

⚙️ This rule is configurable

## What it does

Default branch must be 'develop'

## Configuration

Example:

```yaml
branch: develop
```

Schema:

```json
{
  "type": "object",
  "properties": {
    "branch": {
      "type": "string",
      "title": "Branch"
    }
  },
  "required": [
    "branch"
  ],
  "title": "DefaultBranchNameRuleConfig",
  "additionalProperties": false
}
```
