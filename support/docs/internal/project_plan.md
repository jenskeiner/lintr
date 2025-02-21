# Lintr: Project Plan

## Overview

*Lintr* is a Python-based command-line application to lint and enforce consistent settings across a user's GitHub repositories. The application is:
- *Convenient*: The CLI interface is very easy to use. The terminal output is richt and pleasant, but concise and very readable.
- *Comprehensive*: It supports personal and organizational repositories where the user has admin access.
- *Rule-based*: Pre-defined rules and rule-sets for common project types (e.g., standard Python library packages) are provided.
- *Powerful*: It supports both linting and autofix capabilities.
- *Extensible*: Users can define their own rules by implementing a Python class. Rule-sets can be defined through configuration.

This plan outlines the goals and phases for building Lintr.

## High-level architecture

The high-level architecture is described [here](./high_level_architecture.md).

## Technical Constraints

Technical constraints, i.e. technologies to use and those to avoid, as well as general information around the tech stack are described [here](./technical_constraints.md).

### Repository Structure

The repository structure is described [here](./repository_structure.md).

## Current project Status

We are at Phase 2 of the project.

The individual phases of the project are described in the following files.
- [Phase 1](./phase_1.md)
- [Phase 2](./phase_2.md)
- [Phase 3](./phase_3.md)
- [Phase 4](./phase_4.md)

## Lessons Learned

This section collects lessons learned from implementing the project plan above. 
Each item represents a learning point to consider when working on tasks in the future.
For example, a first implementation of a feature may use a certain dependency that is not recommended. 
We can record here that this dependency should not be used in the future and list alternatives.

- Project Setup: ./lessons/project_setup.md
- GitHub API Integration: ./lessons/github_api_integration.md
- Rule Implementation: ./lessons/rules.md
- Rule Manager Implementation: ./lessons/rules.md
- Rule Discovery and Entry Points: ./lessons/rules.md
- Configuration: ./lessons/configuration.md
- Coding: ./lessons/coding.md
- Development Environment: ./lessons/development_environment.md
- Testing: ./lessons/testing.md

## Future Scope (only for context, not a goal of current implementation)
- Support for organization-wide rules.
- Enhanced reporting with detailed analytics.
- Plugin system for third-party extensions.
