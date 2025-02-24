# Lintr Rules Reference


## General


### R001: DefaultBranchExistsRule

Repository must have a default branch


### R004: WebCommitSignoffRequiredRule

Repository must require signoff on web-based commits


### R011: PreserveRepositoryRule

Repository must have 'Preserve this repository' enabled


### R012: DiscussionsDisabledRule

Repository must have Discussions disabled


### R013: ProjectsDisabledRule

Repository must have Projects disabled


### R017: DeleteBranchOnMergeRule

Repository must have delete_branch_on_merge enabled


### R018: AutoMergeDisabledRule

Repository must have auto merge disabled


## Miscellaneous


### GF001: GitFlowBranchNamingRule

Branch names must conform to GitFlow conventions


### GF002: GitFlowDefaultBranchRule

Default branch must be 'develop'

{{% note title=\"Parameters\" collapsible=\"true\" %}}
Example:

```json
{
  "branch": "develop"
}
```

Example:

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

{{% /note %}}

### R005: SingleOwnerRule

Repository must have only one owner or admin (the user)


### R006: NoCollaboratorsRule

Repository must have no collaborators other than the user


### R007: WikisDisabledRule

Repository must have wikis disabled


### R008: IssuesDisabledRule

Repository must have issues disabled


### R014: MergeCommitsAllowedRule

Repository must allow merge commits for pull requests


### R015: SquashMergeDisabledRule

Repository must have squash merging disabled for pull requests


### R016: RebaseMergeDisabledRule

Repository must have rebase merging disabled for pull requests


### R019: NoClassicBranchProtectionRule

Repository must not use classic branch protection rules


## Rules


### GF003: DevelopBranchRulesetRule

Develop branch must have a proper ruleset configured

{{% note title=\"Parameters\" collapsible=\"true\" %}}
Example:

```json
{
  "ruleset_name": "develop protection",
  "branch_name": "develop",
  "bypass_actors": [
    {
      "actor_id": 5,
      "actor_type": "RepositoryRole",
      "bypass_mode": "always"
    }
  ]
}
```

Example:

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

{{% /note %}}

### GF004: MainBranchRulesetRule

Main branch must have a proper ruleset configured

{{% note title=\"Parameters\" collapsible=\"true\" %}}
Example:

```json
{
  "ruleset_name": "main protection",
  "branch_name": "main",
  "bypass_actors": [
    {
      "actor_id": 5,
      "actor_type": "RepositoryRole",
      "bypass_mode": "always"
    }
  ]
}
```

Example:

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

{{% /note %}}