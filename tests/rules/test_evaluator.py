from packages.rules.rules.evaluator import evaluate_rule
from packages.rules.rules.models import RuleDefinition, RuleSeverity


def test_evaluate_rule_returns_records_that_fail_predicate() -> None:
    rule = RuleDefinition(
        code="TEST",
        description="Record must have flag set",
        severity=RuleSeverity.error,
        predicate=lambda record: record.get("flag") is True,
    )

    violations = evaluate_rule(rule, [{"flag": True}, {"flag": False}])

    assert violations == [{"flag": False}]


def test_evaluate_rule_returns_empty_when_no_predicate() -> None:
    rule = RuleDefinition(code="TEST", description="No predicate", severity=RuleSeverity.info)

    violations = evaluate_rule(rule, [{"flag": False}])

    assert violations == []
