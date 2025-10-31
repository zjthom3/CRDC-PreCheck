from typing import Any, Iterable

from .models import RuleDefinition


def evaluate_rule(rule: RuleDefinition, records: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return records that violate the provided rule.

    Sprint 0 implementation treats a missing predicate as a no-op.
    """
    if rule.predicate is None:
        return []

    violations: list[dict[str, Any]] = []
    for record in records:
        if not rule.predicate(record):
            violations.append(record)
    return violations
