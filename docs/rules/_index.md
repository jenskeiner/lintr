---
title: "Rules"
draft: false
type: docs
layout: "single"
menu:
  lintr:
    identifier: "rules"
    weight: 2
---

Lintr currently supports 30 rules.

### Legend

✅     The rule is stable.
<br>
🧪     The rule is unstable and is in preview.
<br>
🔷     The rule is abstract.
<br>
⚠️     The rule has been deprecated and will be removed in a future release.
<br>
🛠     The rule is automatically fixable by the `--fix` command-line option.
<br>
⚙️     The rule is configurable.



### General (G)

General rules
| Code | Name | Message | Properties |
|-----|-----|-----|-----|
| G001N | [web-commit-signoff-required-disabled](web-commit-signoff-required-disabled.md) | Checks that the repository has _Require contributors to sign off on web-based commits_ disabled in the General settings. | ✅ 🛠️ ⚙️ |
| G001P | [web-commit-signoff-required-enabled](web-commit-signoff-required-enabled.md) | Checks that the repository has _Require contributors to sign off on web-based commits_ enabled in the General settings. | ✅ 🛠️ ⚙️ |
| G002N | [wikis-disabled](wikis-disabled.md) | Checks that _Wikis_ are disabled in the General settings. | ✅ 🛠️ ⚙️ |
| G002P | [wikis-enabled](wikis-enabled.md) | Checks that _Wikis_ are enabled in the General settings. | ✅ 🛠️ ⚙️ |
| G003N | [issues-disabled](issues-disabled.md) | Checks that _Issues_ are disabled in the General settings. | ✅ 🛠️ ⚙️ |
| G003P | [issues-enabled](issues-enabled.md) | Checks that _Issues_ are enabled in the General settings. | ✅ 🛠️ ⚙️ |
| G004N | [preserve-repository-disabled](preserve-repository-disabled.md) | Checks that the repository has 'Preserve this repository' disabled in the General settings. | ✅ 🛠️ ⚙️ |
| G004P | [preserve-repository-enabled](preserve-repository-enabled.md) | Checks that the repository has 'Preserve this repository' enabled in the General settings. | ✅ 🛠️ ⚙️ |
| G005N | [discussions-disabled](discussions-disabled.md) | Checks that Discussions are disabled in the General settings. | ✅ 🛠️ ⚙️ |
| G005P | [discussions-enabled](discussions-enabled.md) | Checks that Discussions are enabled in the General settings. | ✅ 🛠️ ⚙️ |
| G006N | [projects-disabled](projects-disabled.md) | Checks that Projects are disabled in the General settings. | ✅ 🛠️ ⚙️ |
| G006P | [projects-enabled](projects-enabled.md) | Checks that Projects are enabled in the General settings. | ✅ 🛠️ ⚙️ |
| G007N | [merge-commits-disabled](merge-commits-disabled.md) | Checks that merge commits are disabled for pull requests. | ✅ 🛠️ ⚙️ |
| G007P | [merge-commits-enabled](merge-commits-enabled.md) | Checks that merge commits are enabled for pull requests. | ✅ 🛠️ ⚙️ |
| G008N | [squash-merge-disabled](squash-merge-disabled.md) | Checks that squash merging is disabled for pull requests. | ✅ 🛠️ ⚙️ |
| G008P | [squash-merge-enabled](squash-merge-enabled.md) | Checks that squash merging is enabled for pull requests. | ✅ 🛠️ ⚙️ |
| G009N | [rebase-merge-disabled](rebase-merge-disabled.md) | Checks that rebase merging is disabled for pull requests. | ✅ 🛠️ ⚙️ |
| G009P | [rebase-merge-enabled](rebase-merge-enabled.md) | Checks that rebase merging is enabled for pull requests. | ✅ 🛠️ ⚙️ |
| G010N | [auto-merge-disabled](auto-merge-disabled.md) | Checks that 'Allow auto-merge' is disabled for a repository. | ✅ 🛠️ ⚙️ |
| G010P | [auto-merge-enabled](auto-merge-enabled.md) | Checks that 'Allow auto-merge' is enabled for a repository. | ✅ 🛠️ ⚙️ |
| G011N | [delete-branch-on-merge-disabled](delete-branch-on-merge-disabled.md) | Checks that automatically delete head branches is disabled for a repository. | ✅ 🛠️ ⚙️ |
| G011P | [delete-branch-on-merge-enabled](delete-branch-on-merge-enabled.md) | Checks that automatically delete head branches is enabled for a repository. | ✅ 🛠️ ⚙️ |

### GitFlow (GF)

GitFlow rules
| Code | Name | Message | Properties |
|-----|-----|-----|-----|
| GF001 | [git-flow-branch-naming](git-flow-branch-naming.md) | Branch names must conform to GitFlow conventions | ✅ |
| GF002 | [git-flow-default-branch](git-flow-default-branch.md) | Default branch must be 'develop' | ✅ 🛠️ ⚙️ |
| GF003 | [git-flow-develop-branch-ruleset](git-flow-develop-branch-ruleset.md) | Develop branch must have a proper ruleset configured | ✅ 🛠️ ⚙️ |
| GF004 | [git-flow-main-branch-ruleset](git-flow-main-branch-ruleset.md) | Main branch must have a proper ruleset configured | ✅ 🛠️ ⚙️ |

### Miscellaneous (M)

Miscellaneous rules
| Code | Name | Message | Properties |
|-----|-----|-----|-----|
| M001 | [branch-ruleset](branch-ruleset.md) | Checks that a ruleset with given properties exists. | ✅ 🔷 🛠️ ⚙️ |
| R012 | [single-own](single-own.md) | Repository must have only one owner or admin (the user) | ✅ |
| R013 | [no-collaborators](no-collaborators.md) | Repository must have no collaborators other than the user | ✅ 🛠️ |
| R019 | [no-classic-branch-protection](no-classic-branch-protection.md) | Repository must not use classic branch protection rules | ✅ 🛠️ |