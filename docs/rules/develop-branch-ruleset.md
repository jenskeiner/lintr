---
title: "develop-branch-ruleset (GF003)"
draft: false
type: docs
layout: "single"
menu:
  docs_lintr:
    parent: "rules"
---

✔️ This rule is stable

🛠️ This rule is automatically fixable by the `--fix` command-line option

🔧 This rule is configurable

## What it does

Develop branch must have a proper ruleset configured

## Configuration

Example:

```yaml
branch_name: develop
bypass_actors:
- actor_id: 5
  actor_type: RepositoryRole
  bypass_mode: always
ruleset_name: develop protection
```

Schema:

```json
{
  "type": "object",
  "properties": {
    "ruleset_name": {
      "type": "string",
      "title": "Ruleset Name"
    },
    "branch_name": {
      "type": "string",
      "title": "Branch Name"
    },
    "bypass_actors": {
      "type": "array",
      "items": {
        "type": "object"
      },
      "title": "Bypass Actors"
    }
  },
  "required": [
    "ruleset_name",
    "branch_name"
  ],
  "title": "BranchRulesetRuleConfig",
  "additionalProperties": false
}
```
