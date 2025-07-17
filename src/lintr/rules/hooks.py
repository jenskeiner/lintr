from lintr.rules.base import (
    Rule,
    RuleCheckResult,
    RuleResult,
    BaseRuleConfig,
    RuleCategory,
)
from pydantic import BaseModel
from typing import Dict, Literal
from lintr.rules.context import RuleContext
from github.GithubException import GithubException
from difflib import unified_diff


class WebhookConfig(BaseModel):
    url: str
    content_type: Literal["json", "form"]
    has_secret: bool
    insecure_ssl: Literal["0", "1"]


class Webhook(BaseModel):
    active: bool
    type: str
    config: WebhookConfig


class WebhooksRuleConfig(BaseRuleConfig):
    webhooks: Dict[str, Webhook]


class WebhooksRule(Rule[WebhooksRuleConfig]):
    """Rule that checks the webhooks configuration for a repository."""

    _id = "W001"
    _category = RuleCategory.WEBHOOKS
    _description = "Checks the webhooks configuration for a repository"
    _config = WebhooksRuleConfig(webhooks={})

    def check(self, context: RuleContext) -> RuleCheckResult:
        try:
            # Get the repository object
            repo = context.repository

            hooks = {hook.name: hook for hook in repo.get_hooks()}

            violations = []

            # Check for required hooks.
            for name, expected in self.config.webhooks.items():
                if name not in hooks:
                    violations.append(f"Missing webhook: {name}")
                    continue

                hook = hooks[name]

                # Parse hook into Webhook pydantic model.
                hook = Webhook(
                    name=hook.name,
                    active=hook.active,
                    type=hook.type,
                    config=WebhookConfig(
                        url=hook.config.url,
                        content_type=hook.config.content_type,
                        has_secret=hook.config.secret is not None,
                        insecure_ssl=hook.config.insecure_ssl,
                    ),
                )

                if expected != hook:
                    diff_lines = unified_diff(
                        expected.model_dump_json(
                            exclude_keys={"config.has_secret"}, indent=2
                        ).splitlines(),
                        hook.model_dump_json(
                            exclude_keys={"config.has_secret"}, indent=2
                        ).splitlines(),
                        fromfile="expected",
                        tofile="actual",
                        n=500,
                    )
                    diff = []
                    for line in diff_lines:
                        if line.startswith("+"):
                            colored_line = f"[yellow]          {line}[/yellow]"
                        elif line.startswith("-"):
                            colored_line = f"[red]          {line}[/red]"
                        else:
                            colored_line = f"          {line}"
                        diff.append(colored_line)

                    if expected.config.has_secret != hook.config.has_secret:
                        diff.append(
                            f"[yellow]          Webhook has {"a" if hook.config.has_secret else "no"} secret configured, but expected {"a" if expected.config.has_secret else "no"} secret configured.[/yellow]"
                        )

                    violations.append("\n".join(diff))

            # Check for extra hooks.
            extra_hooks = set([name for name, _ in hooks.items()]) - set(
                self.config.webhooks.keys()
            )
            for name in extra_hooks:
                violations.append(f"Extra webhook: {name}")

            if violations:
                return RuleCheckResult(
                    result=RuleResult.FAILED,
                    message="\n".join(violations),
                    fix_available=False,
                )
            # for hook in hooks:
            #     print(hook.name)
            #     print(hook.active)
            #     print(hook.type)
            #     print(hook.config)
            #     print(hook.events)

            # All checks passed
            return RuleCheckResult(
                result=RuleResult.PASSED, message="Webhooks are correctly configured."
            )

        except GithubException as e:
            return RuleCheckResult(
                result=RuleResult.FAILED,
                message=f"Failed to check webhooks: {str(e)}",
                fix_available=False,
            )
