### Core Functionality

- Lint repositories to check for specific conditions based on defined rules.
- Support a configuration file to specify:
  - Target repositories.
  - Custom rule-sets.
- Pre-defined rule-sets for common project types (e.g., standard Python library packages).

### User Interface

- CLI interface for specifying operations.
- Terminal output for presenting results and user feedback.

### Linter

- Represents the main entry point for the application.
- Loads the configuration.
- Discovers available rules and rule-sets.
- Discovers target repositories.
- Executes linting operations and gathers their results on all eligible repositories.
- Reports results to the user.
- Executes auto-fix operations if requested, after prompting the user for confirmation.
- Supports dry-run mode for previewing changes.

### Configuration

- `pydantic_settings` is used to implement a single main configuration class. Subclasses are used where appropriate to separate concerns.
- Valid configuration sources, from lowest to highest priority, are .env file, environment variables, command-line arguments. There must also be one command-line argument that just points to a configuration file that is then consumed.
- Configuration files use YAML format.
- The configuration controls which repositories are target for linting and which rule-sets are used.
- By default, all repositories to which the user has admin access are considered target repositories. a filter can be specified to only target a subset of these.
- A default rule set is used if none is specified in the configuration.
- For each repository, a different rule set can optionally be specified in the configuration.

### Rule Manager

- Discovers available rules and rule-sets.
- Manages and validates the relationship between rules and rule-sets.
- Auxilliary component for the Linter.

### Repo Context

- For each repository, provides the necessary context for each rule that is executed.
- Provides access to repository settings and contents.
- Caches frequently used data to improve performance.
- Acts as an abstraction layer towards the GitHub API.

### Rules

- Rules will check aspects such as:
  - Default branch naming conventions (e.g., `develop` and `main`).
  - Presence and quality of `README.md` files.
- There is an abstract base class for defining the common functionality for all rules.
- Rules have at least the following functionality:
    - Check a repository for a specific condition.
    - Report the result of the check (passed or not, if not why) back to the caller.
    - If available, pass back the suggested fix to the caller.
    - Execute the fix if requested.
- Concrete rules are subclasses of the abstract base class.
- Each rule has a short, unique identifier (similar to flake8, e.g. `G001`).
- Rules are discoverable at runtime. Adding a new rule class to the code base make sit available to the Rule Manager.
- Rules receive a context object when running checks, which encapsulates all information needed for the check.
  - Initially, the context only contains the GitHub repository object.
  - The context can be expanded in the future to provide more information.
- Mutually exclusive
  - Rules can be mutually exclusive with others. The relationship is bi-directional.
  - Mutually exclusive rules can be present in the same rule set.
  - Precedence rules determine which rules in a set are actually active:
    - Rules in sub-rule sets have lower precedence than rules in parent rule sets.
    - Tie-braker for rules at the same level is order in list (from lowest to highest).
    

### Rule Sets

- Rule sets collect several rules.
- Rule sets may be nested, i.e. they may reference individual rules as well as other rule sets.
- Rules have a short, unique identifier, similar to rules.
- Rules and rule sets are referenced by their names.
- At runtime, validation ensures that all references can be resolved.
- A single class defines the behaviour of a rule set.
- A concrete rule set is an instance of this class.
- Pre-defined rule sets are defined in a central YAML file.
- Like rules, rule sets are also discoverable at runtime. Adding a new definition to the central YAML file makes it available to the Rule Manager.
