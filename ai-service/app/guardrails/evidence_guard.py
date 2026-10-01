def requires_comparison(user_input: str) -> bool:
    """
    Determine whether the user's question requires
    historical or period-over-period comparison data.
    """

    comparison_phrases = [
        "spending increased",
        "spending decreased",
        "spending increase",
        "spending decrease",
        "increase in spending",
        "decrease in spending",
        "increased spending",
        "decreased spending",
        "over time",
        "compared with last",
        "compared to last",
        "compared with previous",
        "compared to previous",
        "previous month",
        "previous period",
        "last month",
        "last week",
        "change in spending"
    ]

    user_input = user_input.lower()

    return any(
        phrase in user_input
        for phrase in comparison_phrases
    )


def check_comparison_evidence(
        user_input: str,
        comparison_available: bool
) -> dict:
    """
    Validate whether sufficient evidence exists
    for a historical spending comparison.
    """

    if not requires_comparison(user_input):
        return {
            "allowed": True,
            "reason": "Historical comparison is not required."
        }

    if comparison_available:
        return {
            "allowed": True,
            "reason": "Comparison data is available."
        }

    return {
        "allowed": False,
        "reason": (
            "Historical comparison data is not available. "
            "A spending increase or decrease cannot be established."
        )
    }