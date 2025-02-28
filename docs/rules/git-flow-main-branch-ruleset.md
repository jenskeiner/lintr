---
title: "git-flow-main-branch-ruleset (GF004)"
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

Main branch must have a proper ruleset configured

## Configuration

Example:

```yaml
bypass_actors:
- actor_id: 5
  actor_type: RepositoryRole
  bypass_mode: always
enabled: true
excluded_refs: []
included_refs:
- refs/heads/main
name: main protection
rules:
  creation: null
  deletion: null
  non_fast_forward: null
  pull_request:
    allowed_merge_methods:
    - merge
    automatic_copilot_code_review_enabled: false
    dismiss_stale_reviews_on_push: true
    require_code_owner_review: true
    require_last_push_approval: true
    required_approving_review_count: 1
    required_review_thread_resolution: true
  required_signatures: null
  update: null
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
