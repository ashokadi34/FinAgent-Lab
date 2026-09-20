from fastapi import FastAPI, HTTPException

from app.data.accounts import accounts

app = FastAPI()

@app.get("/")
def home():
    return {
        "message": "Welcome to FinAgent Lab"
    }


@app.get("/api/accounts/{account_id}/balance")
def get_balance(account_id: str):

    account = accounts.get(account_id)

    if account is None:
        raise HTTPException(
            status_code=404,
            detail="Account not found"
        )

    return {
        "account_id": account_id,
        "customer_name": account["customer_name"],
        "currency": account["currency"],
        "balance": account["balance"]
    }