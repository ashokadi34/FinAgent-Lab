from datetime import datetime

from app.guardrails.evidence_guard import get_transaction_periods


def calculate_period_spending(
        transactions: list,
        year: int,
        month: int
) -> float:
    """
    Calculate total DEBIT spending for a specific
    calendar month.
    """

    total = 0.0

    for transaction in transactions:

        if transaction.get("type") != "DEBIT":
            continue

        transaction_date = transaction.get("date")

        if not transaction_date:
            continue

        try:
            date = datetime.strptime(
                transaction_date,
                "%Y-%m-%d"
            )

        except ValueError:
            continue

        if date.year == year and date.month == month:
            total += transaction.get("amount", 0.0)

    return round(total, 2)


def compare_period_spending(
        transactions: list,
        previous_year: int,
        previous_month: int,
        current_year: int,
        current_month: int
) -> dict:
    """
    Compare DEBIT spending between two calendar months.
    """

    previous_spending = calculate_period_spending(
        transactions,
        previous_year,
        previous_month
    )

    current_spending = calculate_period_spending(
        transactions,
        current_year,
        current_month
    )

    difference = round(
        current_spending - previous_spending,
        2
    )

    if previous_spending == 0:
        percentage_change = None
    else:
        percentage_change = round(
            (difference / previous_spending) * 100,
            2
        )

    if difference > 0:
        direction = "INCREASE"
    elif difference < 0:
        direction = "DECREASE"
    else:
        direction = "NO_CHANGE"

    return {
        "previous_period": {
            "year": previous_year,
            "month": previous_month,
            "spending": previous_spending
        },
        "current_period": {
            "year": current_year,
            "month": current_month,
            "spending": current_spending
        },
        "difference": abs(difference),
        "percentage_change": percentage_change,
        "direction": direction
    }

def compare_latest_periods(transactions: list) -> dict:
    """
    Compare spending between the two latest transaction periods.
    """

    periods = sorted(
        get_transaction_periods(transactions)
    )

    if len(periods) < 2:
        return {
            "success": False,
            "message": (
                "At least two transaction periods are required "
                "for comparison."
            )
        }

    previous_year, previous_month = periods[-2]
    current_year, current_month = periods[-1]

    comparison = compare_period_spending(
        transactions,
        previous_year,
        previous_month,
        current_year,
        current_month
    )

    return {
        "success": True,
        "comparison": comparison
    }