"""A single shape for every problem the runner reports."""
from dataclasses import dataclass

LEVELS = ("error", "warning", "info")


@dataclass(frozen=True)
class Issue:
    level: str      # "error" | "warning" | "info"
    where: str      # file or item the issue is about
    message: str


def has_errors(issues) -> bool:
    return any(i.level == "error" for i in issues)


def render(issues) -> str:
    if not issues:
        return "OK: no issues found"
    return "\n".join(f"{i.level.upper():7} {i.where}: {i.message}" for i in issues)
