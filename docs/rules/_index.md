---
title: "Rules"
draft: false
type: docs
layout: "single"
menu:
  docs_lintr:
    identifier: "rules"
    weight: 2
---

Lintr currently supports 19 rules.

### Legend

✅ The rule is stable

🧪 The rule is unstable and is in preview.

⚠️ The rule has been deprecated and will be removed in a future release.

🛠️ The rule is automatically fixable by the `--fix` command-line option.

⚙️ The rule is configurable


### General (G)

General rules
| Code | Name | Message | Properties |
|-----|-----|-----|-----|
| R001 | [default-branch-exists](default-branch-exists/) | Repository must have a default branch | ✅ |
| R004 | [web-commit-signoff-required](web-commit-signoff-required/) | Repository must require signoff on web-based commits | ✅ 🛠️ |
| R011 | [preserve-repository](preserve-repository/) | Repository must have 'Preserve this repository' enabled | ✅ 🛠️ |
| R012 | [discussions-disabled](discussions-disabled/) | Repository must have Discussions disabled | ✅ 🛠️ |
| R013 | [projects-disabled](projects-disabled/) | Repository must have Projects disabled | ✅ 🛠️ |
| R017 | [delete-branch-on-merg](delete-branch-on-merg/) | Repository must have delete_branch_on_merge enabled | ✅ 🛠️ |
| R018 | [auto-merge-disabled](auto-merge-disabled/) | Repository must have auto merge disabled | ✅ 🛠️ |

### Miscellaneous (M)

Miscellaneous rules
| Code | Name | Message | Properties |
|-----|-----|-----|-----|
| GF001 | [git-flow-branch-naming](git-flow-branch-naming/) | Branch names must conform to GitFlow conventions | ✅ |
| GF002 | [git-flow-default-branch](git-flow-default-branch/) | Default branch must be 'develop' | ✅ 🛠️ ⚙️ |
| R005 | [single-own](single-own/) | Repository must have only one owner or admin (the user) | ✅ |
| R006 | [no-collaborators](no-collaborators/) | Repository must have no collaborators other than the user | ✅ 🛠️ |
| R007 | [wikis-disabled](wikis-disabled/) | Repository must have wikis disabled | ✅ 🛠️ |
| R008 | [issues-disabled](issues-disabled/) | Repository must have issues disabled | ✅ 🛠️ |
| R014 | [merge-commits-allowed](merge-commits-allowed/) | Repository must allow merge commits for pull requests | ✅ 🛠️ |
| R015 | [squash-merge-disabled](squash-merge-disabled/) | Repository must have squash merging disabled for pull requests | ✅ 🛠️ |
| R016 | [rebase-merge-disabled](rebase-merge-disabled/) | Repository must have rebase merging disabled for pull requests | ✅ 🛠️ |
| R019 | [no-classic-branch-protection](no-classic-branch-protection/) | Repository must not use classic branch protection rules | ✅ 🛠️ |

### Rules (R)

Rules
| Code | Name | Message | Properties |
|-----|-----|-----|-----|
| GF003 | [develop-branch-ruleset](develop-branch-ruleset/) | Develop branch must have a proper ruleset configured | ✅ 🛠️ ⚙️ |
| GF004 | [main-branch-ruleset](main-branch-ruleset/) | Main branch must have a proper ruleset configured | ✅ 🛠️ ⚙️ |