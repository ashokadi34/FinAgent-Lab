from app.data.accounts import accounts


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