"""GitHub API integration for Lintr."""

from fnmatch import fnmatch

from github import Github
from github.Repository import Repository
from pydantic import BaseModel
from lintr.config import RepositoryFilter


class GitHubConfig(BaseModel):
    """Configuration for GitHub API access."""

    token: str
    org_name: str | None = None
    include_private: bool = True
    include_archived: bool = False
    include_organisations: bool = False
    repository_filter: RepositoryFilter = RepositoryFilter()


class GitHubClient:
    """Client for interacting with GitHub API."""

    def __init__(self, config: GitHubConfig):
        """Initialize GitHub client.

        Args:
            config: GitHub configuration.
        """
        self._config = config
        self._client = Github(config.token)

    def get_repositories(self) -> list[Repository]:
        """Get list of repositories based on configuration.

        Returns:
            List of GitHub repositories.
        """
        repositories = []

        if self._config.org_name:
            # If org_name is specified, only get that organization's repositories
            org = self._client.get_organization(self._config.org_name)
            repositories.extend(org.get_repos())
        else:
            # Get authenticated user's repositories
            user = self._client.get_user()

            # Get user's own repositories (affiliation="owner")
            repositories.extend(user.get_repos(affiliation="owner"))

            # If requested, also include organization repositories
            if self._config.include_organisations:
                for org in user.get_orgs():
                    repositories.extend(org.get_repos())

        # Filter repositories based on configuration
        filtered_repos = [
            repo
            for repo in repositories
            if (self._config.include_private or not repo.private)
            and (self._config.include_archived or not repo.archived)
        ]

        # Apply repository filters if configured
        if self._config.repository_filter.include_patterns:
            filtered_repos = [
                repo
                for repo in filtered_repos
                if not self._config.repository_filter.include_patterns
                or any(
                    fnmatch(repo.name, pattern)
                    for pattern in self._config.repository_filter.include_patterns
                )
            ]

        # Apply exclusion patterns if specified
        if self._config.repository_filter.exclude_patterns:
            filtered_repos = [
                repo
                for repo in filtered_repos
                if not self._config.repository_filter.exclude_patterns
                or not any(
                    fnmatch(repo.name, pattern)
                    for pattern in self._config.repository_filter.exclude_patterns
                )
            ]

        return filtered_repos

    def get_repository_settings(self, repo: Repository) -> dict:
        """Get settings for a repository.

        Args:
            repo: GitHub repository.

        Returns:
            Dictionary containing repository settings.
        """
        return {
            "name": repo.name,
            "default_branch": repo.default_branch,
            "description": repo.description,
            "homepage": repo.homepage,
            "private": repo.private,
            "archived": repo.archived,
            "has_issues": repo.has_issues,
            "has_projects": repo.has_projects,
            "has_wiki": repo.has_wiki,
            "allow_squash_merge": repo.allow_squash_merge,
            "allow_merge_commit": repo.allow_merge_commit,
            "allow_rebase_merge": repo.allow_rebase_merge,
            "delete_branch_on_merge": repo.delete_branch_on_merge,
        }
