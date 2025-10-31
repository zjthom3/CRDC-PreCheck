from enum import Enum
from typing import Any, Callable

from pydantic import BaseModel, Field


class RuleSeverity(str, Enum):
    error = "error"
    warning = "warning"
    info = "info"


class RuleDefinition(BaseModel):
    """Minimal rule definition used for Sprint 0 scaffolding."""

    code: str = Field(..., description="Unique rule code identifier.")
    description: str = Field(..., description="Human-readable rule summary.")
    severity: RuleSeverity = Field(RuleSeverity.error, description="Rule severity.")
    predicate: Callable[[dict[str, Any]], bool] | None = Field(
        default=None,
        description="Callable predicate returning True when the record passes.",
    )
