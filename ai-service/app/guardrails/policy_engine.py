from app.data.accounts import accounts
from app.data.beneficiaries import beneficiaries


MAX_TRANSACTION_AMOUNT = 50000.00
DAILY_TRANSACTION_LIMIT = 100000.00
SUPPORTED_CURRENCIES = {"INR", "USD", "SGD"}
CONFIRMATION_THRESHOLD = 25000.00


def evaluate_payment_policy(
        account_id: str,
        amount: float,
        currency: str,
        beneficiary_id: str
):
    """
    Deterministic policy engine for payment intent validation.
    """

    # 1. Validate account
    account = accounts.get(account_id)

    if account is None:
        return {
            "status": "BLOCKED",
            "reason": "Source account not found"
        }

    # 2. Validate amount
    if amount <= 0:
        return {
            "status": "BLOCKED",
            "reason": "Payment amount must be greater than zero"
        }

    # 3. Maximum transaction limit
    if amount > MAX_TRANSACTION_AMOUNT:
        return {
            "status": "BLOCKED",
            "reason": (
                f"Payment exceeds maximum transaction limit of "
                f"₹{MAX_TRANSACTION_AMOUNT:,.2f}"
            )
        }

    # 4. Validate currency
    if currency not in SUPPORTED_CURRENCIES:
        return {
            "status": "BLOCKED",
            "reason": f"Currency {currency} is not supported"
        }

    # 5. Validate balance
    if currency == account["currency"] and amount > account["balance"]:
        return {
            "status": "BLOCKED",
            "reason": "Insufficient account balance"
        }

    # 6. Validate beneficiary
    beneficiary = beneficiaries.get(beneficiary_id)

    if beneficiary is None:
        return {
            "status": "BLOCKED",
            "reason": "Beneficiary not found"
        }

    # 7. New beneficiary requires confirmation
    if beneficiary["is_new"] or not beneficiary["verified"]:
        return {
            "status": "REQUIRES_CONFIRMATION",
            "reason": "New or unverified beneficiary requires confirmation",
            "beneficiary": beneficiary["name"]
        }

    # 8. International transfer requires confirmation
    if beneficiary["country"] != "IN":
        return {
            "status": "REQUIRES_CONFIRMATION",
            "reason": "International transfer requires confirmation",
            "destination_country": beneficiary["country"]
        }

    # 9. Large transaction requires confirmation
    if amount > CONFIRMATION_THRESHOLD:
        return {
            "status": "REQUIRES_CONFIRMATION",
            "reason": (
                f"Payment exceeds confirmation threshold of "
                f"₹{CONFIRMATION_THRESHOLD:,.2f}"
            )
        }

    # 10. Payment approved
    return {
        "status": "APPROVED",
        "reason": "Payment satisfies configured policy rules"
    }