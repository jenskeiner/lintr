---
title: "Contributing"
draft: false
type: docs
layout: "single"

menu:
  docs_lintr:
      weight: 4
---

Lintr is still under development. You can greatly help the project by
- suggesting improvements,
- reporting bugs,
- submitting PRs with improvements and/or fixes,
- adding new rules to check particular settings of interest,
- improving automated tests and test coverage,
- improving the documentation.

## Adding new rules

At this stage, the best way to see how you can add new rules is to check out the implementation of exisiting rules in the `src/lintr/rules` directory.
A good starting point are the rules in `src/lintr/rules/general.py`. Many of them are configurable, have a mutually exclusive counterpart, and perform
simple checks.

Once a new rule has been added, make sure that an entry point is added to `pyproject.toml` under `[project.entry-points."lintr.rules"]`. Otherwise,
the new rule will not be discovered at runtime.

Also, make sure you run `scripts/generate_rule_docs.py` to generate documentation for all rules, including your new one under `docs/rules`. If the script complains, 
you might have forgotten to set some required fields like `_id` on the new class.