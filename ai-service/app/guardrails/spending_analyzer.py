from collections import defaultdict
from datetime import datetime


def analyze_spending(transactions):

    if not transactions:
        return {
            "success": False,
            "message": "No transactions available."
        }

    # ---------------------------------------------------------
    # Consider only DEBIT transactions as spending.
    # ---------------------------------------------------------

    spending_transactions = [
        transaction
        for transaction in transactions
        if transaction.get("type") == "DEBIT"
    ]

    if not spending_transactions:
        return {
            "success": True,
            "message": "No spending transactions available.",
            "analysis": None
        }

    # ---------------------------------------------------------
    # Determine the latest available transaction period.
    # ---------------------------------------------------------

    latest_date = max(
        datetime.strptime(
            transaction["date"],
            "%Y-%m-%d"
        )
        for transaction in spending_transactions
    )

    latest_year = latest_date.year
    latest_month = latest_date.month

    latest_period_transactions = [
        transaction
        for transaction in spending_transactions
        if (
                datetime.strptime(
                    transaction["date"],
                    "%Y-%m-%d"
                ).year == latest_year
                and
                datetime.strptime(
                    transaction["date"],
                    "%Y-%m-%d"
                ).month == latest_month
        )
    ]

    # ---------------------------------------------------------
    # Total spending for latest period.
    # ---------------------------------------------------------

    total_spending = sum(
        transaction["amount"]
        for transaction in latest_period_transactions
    )

    # ---------------------------------------------------------
    # Category totals.
    # ---------------------------------------------------------

    category_totals = defaultdict(float)

    for transaction in latest_period_transactions:

        category = transaction.get(
            "category",
            "Unknown"
        )

        category_totals[category] += transaction["amount"]

    # ---------------------------------------------------------
    # Largest expense.
    # ---------------------------------------------------------

    largest_expense = max(
        latest_period_transactions,
        key=lambda transaction: transaction["amount"]
    )

    # ---------------------------------------------------------
    # Return deterministic analysis.
    # ---------------------------------------------------------

    return {
        "success": True,
        "analysis": {
            "period": {
                "year": latest_year,
                "month": latest_month
            },
            "total_spending": round(
                total_spending,
                2
            ),
            "category_totals": dict(
                category_totals
            ),
            "largest_expense": {
                "transaction_id": largest_expense["transaction_id"],
                "date": largest_expense["date"],
                "description": largest_expense["description"],
                "category": largest_expense["category"],
                "amount": largest_expense["amount"]
            },
            "transaction_count": len(
                latest_period_transactions
            )
        }
    }