from app.tools.payment_tools import create_payment_intent


result = create_payment_intent(
    account_id="ACC001",
    amount=20000,
    currency="INR",
    beneficiary_id="BEN001"
)

print("\nPayment Intent:")
print(result)