from app.data.transactions import transactions
from app.guardrails.evidence_guard import (
    requires_comparison,
    get_transaction_periods,
    check_comparison_evidence
)


account_transactions = transactions["ACC001"]


print("=== TEST 1: Current Data Only ===")

question = "Why did my spending increase for account ACC001?"

print(
    "Requires comparison:",
    requires_comparison(question)
)

print(
    "Transaction periods:",
    get_transaction_periods(account_transactions)
)

result = check_comparison_evidence(
    question,
    account_transactions
)

print("Evidence check:", result)


print("\n=== TEST 2: August + September Data ===")


august_transactions = [
    {
        "transaction_id": "TXN-AUG-001",
        "date": "2026-08-02",
        "description": "Grocery Store",
        "category": "Food",
        "amount": 2000.00,
        "currency": "INR",
        "type": "DEBIT"
    },
    {
        "transaction_id": "TXN-AUG-002",
        "date": "2026-08-05",
        "description": "Uber",
        "category": "Transport",
        "amount": 300.00,
        "currency": "INR",
        "type": "DEBIT"
    },
    {
        "transaction_id": "TXN-AUG-003",
        "date": "2026-08-08",
        "description": "Shopping",
        "category": "Shopping",
        "amount": 1500.00,
        "currency": "INR",
        "type": "DEBIT"
    }
]


comparison_transactions = (
        august_transactions
        + account_transactions
)


print(
    "Transaction periods:",
    get_transaction_periods(comparison_transactions)
)


result = check_comparison_evidence(
    question,
    comparison_transactions
)

print("Evidence check:", result)