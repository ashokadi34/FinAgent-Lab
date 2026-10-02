from app.guardrails.policy_engine import evaluate_payment_policy


def test_payment(amount, beneficiary_id):
    result = evaluate_payment_policy(
        account_id="ACC001",
        amount=amount,
        currency="INR",
        beneficiary_id=beneficiary_id
    )

    print("\nPayment Test")
    print(f"Amount: ₹{amount:,.2f}")
    print(f"Beneficiary: {beneficiary_id}")
    print(f"Result: {result}")


# Test 1: Domestic small payment
test_payment(
    amount=10000,
    beneficiary_id="BEN003"
)

# Test 2: Large payment
test_payment(
    amount=30000,
    beneficiary_id="BEN003"
)

# Test 3: International payment
test_payment(
    amount=20000,
    beneficiary_id="BEN001"
)

# Test 4: New beneficiary
test_payment(
    amount=10000,
    beneficiary_id="BEN002"
)

# Test 5: Exceeds maximum limit
test_payment(
    amount=60000,
    beneficiary_id="BEN003"
)