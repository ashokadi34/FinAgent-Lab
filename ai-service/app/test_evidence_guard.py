from app.guardrails.evidence_guard import (
    requires_comparison,
    check_comparison_evidence
)


question = "How much did I spend on food in account ACC001?"

print(
    "Requires comparison:",
    requires_comparison(question)
)

result = check_comparison_evidence(
    question,
    comparison_available=False
)

print("Evidence check:", result)