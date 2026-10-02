from app.data.transactions import transactions
from app.guardrails.spending_comparator import (
    calculate_period_spending,
    compare_period_spending,
    compare_latest_periods
)


account_transactions = transactions["ACC001"]


august_spending = calculate_period_spending(
    account_transactions,
    2026,
    8
)

september_spending = calculate_period_spending(
    account_transactions,
    2026,
    9
)

print("August spending:", august_spending)
print("September spending:", september_spending)


comparison = compare_period_spending(
    account_transactions,
    previous_year=2026,
    previous_month=8,
    current_year=2026,
    current_month=9
)

print("\nComparison:")
print(comparison)

print("\nLatest period comparison:")

latest_comparison = compare_latest_periods(
    account_transactions
)

print(latest_comparison)