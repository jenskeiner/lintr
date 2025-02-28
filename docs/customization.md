---
title: "Customization"
draft: false
type: docs
layout: "single"

menu:
  docs_lintr:
      weight: 1
---
## Custom rules

Sometimes, the pre-defined rules may not be enough. For example, the rule [GF002]() checks that the default branch is named `develop`. But what if in your repositories, it is typically named `dev` or something else? To make your life easier, Lintr allows you to define a new rule based on the existing one, but with a different branch name to check against. Consider the following configuration file
snippet:
```yaml
default_ruleset: standard

rules:
  myrule:  # The rule ID must be unique across rules and rulesets.
    base: GF002
    description: Check that the default branch is named `dev`.
    config:
      branch: dev

rulesets:
  standard:
    description: "Standard ruleset"
    rules:
      - G001
      - G002
      - G003
      - myrule
```

The new `rules` section allows you to define new rules. Many rules support customization through different parameters. For the above rule GF002, you can override
its branch name to check against (`main` by default). The new rule `myrule` is based on GF002 and uses `dev` as the branch name to check against. It's used
in the ruleset `standard` and thus checks in every repository that the default branch is named `dev`.

Many rules support customization through different parameters to generate new custom rules. See the [reference]() for more information.


## Repository-specific rule settings

Creating a new custom rule may be too much in some cases when you have a specific repository that needs slightly different settings.
In this scenario, you can just keep on using a regular ruleset for such a repository, but customize the settings for specific rules just for
that repository.

Here's an example:

```yaml
default_ruleset: standard

rulesets:
  standard:
    description: "Standard ruleset"
    rules:
      - G001
      - G002
      - G003
      - GF002

repositories:
  bar:
    ruleset: standard
    rules:
      GF002:
        branch: dev
```

Here, instead of defining a new custom rule based on [](GF002), the settings for this rule are overridden just for the repository `bar`. That is,
all repositories will use the same ruleset `standard`, but the rule `GF002` will check for the branch `dev` instead of `develop` for the 
repository `bar`only, and for `develop` on all remaining repositories.

## Abstract rules

Some pre-defined rules are abstract, indicated by 🔷, and therefore cannot be used directly. Usually, they implement a check that requires additional configuration
for which no sensible default exists. These rules provide a foundation for concrete rules that can be derived from them by providing a suitable configuration.

An example for such a rule is [branch-ruleset (M001)](../rules/branch-ruleset.md) which checks that a branch ruleset with given properties exists.
For a specific use case, you can derive a concrete rule from it and define specific properties you expect on the branch ruleset, like the target branches or
other restrictions. In fact, the pre-defined rule [develop-branch-ruleset (GF003)](../rules/develop-branch-ruleset.md) is derived from
[branch-ruleset (M001)](../rules/branch-ruleset.md) with a specific configuration.

## Mutually exclusive rules

Some rules, particularly those that check boolean properties, naturally come with a natural opposite. For example, the rule [web-commit-signoff-required-disabled (G001N)](../rules/web-commit-signoff-required-disabled.md) and [web-commit-signoff-required-enabled (G001P)](../rules/web-commit-signoff-required-enabled.md) are mutually exclusive.

This is not a problem unless these two rules are part of the same ruleset. In that case, regardless of the value of the property the rules check, one of them will always fail.
This problem can of course be solved by crafting rulesets so that conflicts like this do not occur.

However, in some cases, it may be convenient be able to flip a rule in an existing ruleset to create a new ruleset. And this is where the following special handling comes in:
Every ruleset defines a total ordering of all contained rules by a recursive depth-first traverse of the tree that contains all its rules and rulesets (remember that rulesets 
can contain other rulesets). Effectively, you can think of this as recursively replacing every child ruleset with its ordered list of rules.

Before a ruleset is applied, any conflicting rules are eliminated from the ordered list as follows: Starting from the last rule and moving to the first, any preceding rule that conflicts with the current rule is removed. This ensures that rules added "later" always override previous rules in case of a conflict.

Consider the following example:

```yaml
default_ruleset: standard

rulesets:
  rs1:
    description: "Ruleset 1"
    rules:
      - G002P
      - G001N
      - G003N
  rs2:
    description: "Ruleset 2"
    rules:
      - rs1
      - G001P
```

The ordered list of rules in the ruleset `rs2` is `G002P`, `G001N`, `G003N`, `G001P]`. The effective list, after elimination of conflicts, is `G002P`, `G003N`, `G001P`, since `G001P` and `G001N` are mutually exclusive and `G001P` comes after `G001N`, and thus has higher priority.

This behaviour may be convenient if `rs1` is a very large ruleset and an identical ruleset with `G001N` replaced by `G001P` is needed.

In the following example the situation is reversed:

```yaml
default_ruleset: standard

rulesets:
  rs1:
    description: "Ruleset 1"
    rules:
      - G002P
      - G001N
      - G003N
  rs2:
    description: "Ruleset 2"
    rules:
      - G001P
      - rs1
```

Here, the list of rules is `G001P`, `G002P`, `G001N`, `G003N` which gets resolved to `G002P`, `G001N`, `G003N`. So, `rs2` is effectively identical to `rs1`.
