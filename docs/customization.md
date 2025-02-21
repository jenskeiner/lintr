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
      - R001
      - R002
      - R003
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
      - R001
      - R002
      - R003
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

tba


## Writing custom rules

tba