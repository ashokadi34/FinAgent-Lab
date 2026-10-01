from datetime import datetime


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


def get_transaction_periods(transactions: list) -> set:
    """
    Extract unique year-month periods from transaction dates.
    """

    periods = set()

    for transaction in transactions:

        transaction_date = transaction.get("date")

        if not transaction_date:
            continue

        try:
            date = datetime.strptime(
                transaction_date,
                "%Y-%m-%d"
            )

            periods.add(
                (date.year, date.month)
            )

        except ValueError:
            continue

    return periods


def check_comparison_evidence(
        user_input: str,
        transactions: list
) -> dict:
    """
    Determine whether the available transaction data
    contains enough evidence for a historical comparison.

    Current implementation considers two or more distinct
    calendar months as comparison evidence.
    """

    if not requires_comparison(user_input):

        return {
            "allowed": True,
            "reason": "Historical comparison is not required."
        }

    periods = get_transaction_periods(transactions)

    if len(periods) >= 2:

        return {
            "allowed": True,
            "reason": "Multiple transaction periods are available.",
            "periods": sorted(periods)
        }

    return {
        "allowed": False,
        "reason": (
            "Historical comparison data is not available. "
            "A spending increase or decrease cannot be established."
        ),
        "periods": sorted(periods)
    }