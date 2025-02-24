---
title: "Lintr"
draft: false
type: docs
layout: "single"

menu:
  docs_lintr:
      name: "Introduction"
      weight: 0
---
A powerful and flexible GitHub repository settings linter, written in pure Python.

<center>
  <img src="./assets/demo.gif" style="max-width: 600px; width: 100%;" alt="Demo Animation">
</center>

## Highlights

- ✅ Enforces consistent GitHub repository settings.
- 🔒 Monitors key repository settings against [predefined rules](#rules) and [rule sets](#rule-sets).
- 🛡️ Helps mitigate security issues.
- ⚙️ Streamlines repository management.
- 🤖 Automates checks for repository hygiene.

## Installation

Lintr is available as `lintr` on [PyPI](https://pypi.org/project/lintr/).

Lintr can be invoked directly with [uvx](https://docs.astral.sh/uv/):

```bash
uvx lintr --help   # List command line reference.
uvx lintr lint     # Lint repository settings
```

Or installed with `uv` (recommended), `pip`, or `pipx`:

{{< tabs tabTotal="3" tabID1="pip" tabID2="pipx" tabID3="uv" tabName1="With pip" tabName2="With pipx" tabName3="With uv">}}

{{< tab tabID="pip" >}}
```bash
# Using pip.
pip install lintr
```
{{< /tab >}}
{{< tab tabID="pipx" >}}
```bash
# Using pipx.
pipx install lintr
```
{{< /tab >}}
{{< tab tabID="uv" >}}
```bash
# Using uv.
uv install lintr
```
{{< /tab >}}
{{< /tabs >}}

Once installed, you can run Lintr from the command line: 

```bash
lintr help   # List command line reference.
lintr lint   # Lint repository settings
```

Since Lintr is installed as the Python module `lintr`, you can also run Lintr through the Python interpreter:

```bash
python -m lintr help   # List command line reference.
python -m lintr lint   # Lint repository settings
```

Then, check out the [first steps]() or read on for a brief overview.

## Personal Access Token

Lintr needs a [personal access token](https://docs.github.com/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens) 
to access the GitHub API on your behalf.

It is recommended to generate a dedicated access token for use with Linter to ensure that it runs with the most restrictive privileges possible.

If you are using a [Fine-grained token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-fine-grained-personal-access-token),
make sure it has the following repository permissions:
- __Read access to metadata__, and either
- __Read access to administration__, or
- __Read and Write access to administration__.

Write access to administration is required if Lintr should make changes to repository settings to fix rule violations.

If you are using a [personal access token (classic)](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-fine-grained-personal-access-token), ensure `repo` and optionally `public_repo` are 
ticked.

Once you have retrieved the personal access token, make it available to Lintr by setting the environment variable `GITHUB_TOKEN`:
```bash
set GITHUB_TOKEN="your-token-here"
```

{{% warning %}}
You can also set the token in a [configuration file](#configuration-file), but it is recommended to use an environment variable instead, 
to ensure the token is not stored on disk in plain text, and/or mixed with other configuration that you might want to commit to 
version control or share with others.
{{% /warning %}}

Once you have configured the token, you can verify it:
```bash
lintr lint
```

This will enumerate all repositories that can be accessed with the token. By default, Lintr uses an empty rule set for each repository, so no actual linting will be performed.

## Configuration file

By default, Lintr will scan all repositories it has access to through the personal access token, but will not apply any checks.

To configure Linter, it is recommended to create a YAML-formatted configuration file, e.g. `lintr.yml`. Using a configuration file allows to configure the linting process, including the repositories to lint and the rule sets to use.

Check the [customization section](customization.md) for more detailed information.

Here is an example of a simple `lintr.yml` file:

```yaml
# GitHub personal access token.
# Not recommended to set here, use GITHUB_TOKEN environment variable.
#github_token: ...

# The default rule set to use.
default_ruleset: standard

rulesets:
  standard:  # Identifier must be unique across rules and rulesets.
    description: standard
    rules:  # List of rules and rulesets to include.
      - R001
      - R002
      - R003
```

This defines a new ruleset named `standard` and makes it the default for all repositories. It uses pre-defined rules that come with Lintr.

As already mentioned, it's not recommended to set the GitHub personal access token in a configuration file, but rather use the `GITHUB_TOKEN` environment variable.

Once created, you can use Lintr with the configuration file as follows:

```bash
lintr lint --config lintr.yml
```

This will lint all repositories using the `standard` ruleset defined in the configuration file and report any violations.

## Rules & Rulesets

Lintr checks repositories by applying a sequence of rules. Each rule has a relativly narrow focus, like checking if a certain repository setting is set to a certain value.
For example, there may be a rule to check if the default branch has a certain name, or whether sign off on web-based commits is required. The flexibility and power of Lintr
come from the combination of multiple rules.

Rules are combined into rulesets. A ruleset is a collection of rules that can be applied to a repository. A ruleset may also contain other rulesets. This is particularly
convenient to organise related rules into smaller sets from which larger rulesets can be composed. The larger rulesets can then be applied to repositories. This promotes
sharing of common rules across repositories, but still alows for fine-grained control over individual repositories.

Lintr comes with a range of pre-defined rules. Every rule has a unique identifier and a description. You can find a list of all available rules in the [rules section](rules/).

Lintr also provides a few pre-defined rulesets. The most basic one is the `empty` ruleset which contains no rules and is used by default absent any other configuration.
Like rules, each ruleset also has a unique identifier. You can find a list of all available rulesets in the [rulesets section](rulesets/).

{{% note %}}
To avoid confusion, rule and ruleset identifiers must be globally unique. Any rule or ruleset must have an ID distinct from that of any other rule or ruleset.
{{% /note %}}

### Custom rulesets

Since any GitHub account has specific needs and preferred settings, the pre-defined rulesets are probably not enough to work for you out of the box. Therefore,
Lintr allows you to define your own rulesets, so you can build up the exact set of checks you want to run on your repopsitories.

To create a custom ruleset, simply define it in the configuration file. Using the above example, this could look as follows:

```yaml
rulesets:
  standard:  # Identifier must be unique across rules and rulesets.
    description: "Standard ruleset"
    rules:  # List of rules and rulesets to include.
      - R001
      - R002
      - R003
```

Each ruleset must have a unique identifier (`standard`), an optional description, and a list of rules and rulesets to include.

A more complex example might look like this:

```yaml
rulesets:
  standard:
    description: "Standard ruleset"
    rules:
      - R001
      - R002
      - R003
  extended:
    description: "Extended ruleset"
    rules:
      - standard  # Include all rules from the standard ruleset as well.
      - R004
      - R005
      - R006
```

Here, the ruleset `extended` includes all rules from the `standard` ruleset as well as the rules `R004`, `R005` and `R006`.

### Applying rulesets

We already saw above that the configuration file may define a standard ruleset which by default applies to all repositories.
However, you may want to apply certain rulesets to specific repositories and just use the default ruleset for the rest. 
To that end, Lintr allows you to configure a ruleset for each repository in the configuration file as follows:

```yaml
default_ruleset: standard

rulesets:
  standard:
    description: "Standard ruleset"
    rules:
      - R001
      - R002
      - R003
  extended:
    description: "Extended ruleset"
    rules:
      - standard
      - R004
      - R005
      - R006

repositories:
  foo:
    ruleset: extended
  bar:
    ruleset: standard
```

Lintr will use the ruleset `standard` for repository `foo` and the ruleset `extended` for repository `bar`. It will also use the default ruleset `standard` for all other repositories.

Lintr can be customized further through custom rules and repository-specific rule settings. See the section on [customization](./customization) for more information.
