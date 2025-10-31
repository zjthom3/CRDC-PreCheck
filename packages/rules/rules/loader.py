from pathlib import Path
from typing import Iterable

import yaml

from .models import RuleDefinition, RuleSeverity


def load_rules_from_yaml(paths: Iterable[Path]) -> list[RuleDefinition]:
    """Load rule definitions from one or more YAML files."""
    rules: list[RuleDefinition] = []
    for path in paths:
        data = yaml.safe_load(path.read_text())
        for item in data or []:
            rules.append(
                RuleDefinition(
                    code=item["code"],
                    description=item["description"],
                    severity=RuleSeverity(item.get("severity", "error")),
                    predicate=None,
                )
            )
    return rules
