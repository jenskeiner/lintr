---
title: "branch-ruleset (M001)"
draft: false
type: docs
layout: "single"
params:
  tags: ["M001"]
menu:
  lintr:
    parent: "rules"
---

✅     This rule is stable.<br>
🔷     This rule is abstract.<br>
🛠️     This rule is automatically fixable by the `--fix` command-line option.<br>
⚙️     This rule is configurable.

## What it does

Checks that a ruleset with given properties exists.

## Configuration

Example:

```yaml
name: ruleset
enabled: true
included_refs:
- refs/heads/master
excluded_refs:
- refs/heads/develop
bypass_actors:
- actor_id: 5
  actor_type: RepositoryRole
  bypass_mode: always
rules:
  creation: null
  update: null
  deletion: null
  required_signatures: null
  pull_request:
    required_approving_review_count: 1
    dismiss_stale_reviews_on_push: true
    require_code_owner_review: true
    require_last_push_approval: true
    required_review_thread_resolution: true
    automatic_copilot_code_review_enabled: false
    allowed_merge_methods:
    - merge
  non_fast_forward: null
```

Schema:

```json
{
  "type": "object",
  "properties": {
    "name": {
      "type": "string",
      "description": "The name of the branch ruleset to check.",
      "title": "Name"
    },
    "enabled": {
      "type": "boolean",
      "default": true,
      "description": "Whether the branch ruleset should be enabled.",
      "title": "Enabled"
    },
    "included_refs": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "List of refs to include in the branch ruleset.",
      "title": "Included Refs"
    },
    "excluded_refs": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "List of refs to exclude from the branch ruleset.",
      "title": "Excluded Refs"
    },
    "bypass_actors": {
      "type": "array",
      "items": {
        "type": "object"
      },
      "description": "List of actors that should bypass the branch ruleset.",
      "title": "Bypass Actors"
    },
    "rules": {
      "type": "object",
      "additionalProperties": {
        "anyOf": [
          {
            "type": "object"
          },
          {
            "type": "null"
          }
        ]
      },
      "description": "List of required rules for the branch ruleset.",
      "title": "Rules"
    }
  },
  "required": [
    "name"
  ],
  "title": "BranchRulesetRuleConfig",
  "additionalProperties": false
}
```
