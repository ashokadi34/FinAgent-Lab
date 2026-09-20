from app.tools.financial_tools import get_balance, get_transactions


print("=== Balance ===")

balance_result = get_balance("ACC001")
print(balance_result)


print("\n=== Transactions ===")

transaction_result = get_transactions("ACC001")
print(transaction_result)