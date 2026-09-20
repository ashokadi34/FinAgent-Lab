from app.data.accounts import accounts
from app.data.transactions import transactions


def get_balance(account_id: str):
    account = accounts.get(account_id)

    if account is None:
        return {
            "success": False,
            "message": "Account not found"
        }

    return {
        "success": True,
        "account_id": account_id,
        "customer_name": account["customer_name"],
        "currency": account["currency"],
        "balance": account["balance"]
    }


def get_transactions(account_id: str):
    account_transactions = transactions.get(account_id)

    if account_transactions is None:
        return {
            "success": False,
            "message": "Account not found"
        }

    return {
        "success": True,
        "account_id": account_id,
        "transactions": account_transactions
    }