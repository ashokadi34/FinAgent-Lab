from app.data.accounts import accounts
from app.data.beneficiaries import beneficiaries
from app.guardrails.policy_engine import evaluate_payment_policy


def create_payment_intent(
        account_id: str,
        amount: float,
        currency: str,
        beneficiary_id: str
):
    """
    Creates a payment intent after deterministic policy validation.

    This function does NOT execute a real payment.
    """

    account = accounts.get(account_id)

    if account is None:
        return {
            "success": False,
            "status": "BLOCKED",
            "message": "Account not found"
        }

    beneficiary = beneficiaries.get(beneficiary_id)

    if beneficiary is None:
        return {
            "success": False,
            "status": "BLOCKED",
            "message": "Beneficiary not found"
        }

    policy_result = evaluate_payment_policy(
        account_id=account_id,
        amount=amount,
        currency=currency,
        beneficiary_id=beneficiary_id
    )

    return {
        "success": True,
        "payment_intent": {
            "account_id": account_id,
            "amount": amount,
            "currency": currency,
            "beneficiary_id": beneficiary_id,
            "beneficiary_name": beneficiary["name"],
            "destination_country": beneficiary["country"],
            "status": policy_result["status"],
            "reason": policy_result["reason"]
        }
    }