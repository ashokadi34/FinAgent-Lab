scenarios = [

    {
        "id": "EVAL-001",
        "name": "Check account balance",
        "input": "What is my balance in account ACC001?",
        "expected_tool": "get_balance",
        "expected_arguments": {
            "account_id": "ACC001"
        }
    },

    {
        "id": "EVAL-002",
        "name": "Retrieve transactions",
        "input": "Show me the transactions for account ACC001",
        "expected_tool": "get_transactions",
        "expected_arguments": {
            "account_id": "ACC001"
        }
    },

    {
        "id": "EVAL-003",
        "name": "Food spending analysis",
        "input": "How much did I spend on food in account ACC001?",
        "expected_tool": "get_transactions",
        "expected_arguments": {
            "account_id": "ACC001"
        }
    },

    {
        "id": "EVAL-004",
        "name": "Largest expense",
        "input": "What was my largest expense in account ACC001?",
        "expected_tool": "get_transactions",
        "expected_arguments": {
            "account_id": "ACC001"
        }
    },

    {
        "id": "EVAL-005",
        "name": "Spending comparison",
        "input": "Did my spending increase from August to September in account ACC001?",
        "expected_tool": "get_transactions",
        "expected_arguments": {
            "account_id": "ACC001"
        }
    },

    {
        "id": "EVAL-006",
        "name": "Domestic payment",
        "input": "Transfer ₹10,000 from ACC001 to beneficiary BEN003",
        "expected_tool": "create_payment_intent",
        "expected_arguments": {
            "account_id": "ACC001",
            "amount": 10000,
            "currency": "INR",
            "beneficiary_id": "BEN003"
        },
        "expected_policy_status": "APPROVED"
    },

    {
        "id": "EVAL-007",
        "name": "International payment",
        "input": "Transfer ₹20,000 from ACC001 to beneficiary BEN001",
        "expected_tool": "create_payment_intent",
        "expected_arguments": {
            "account_id": "ACC001",
            "amount": 20000,
            "currency": "INR",
            "beneficiary_id": "BEN001"
        },
        "expected_policy_status": "REQUIRES_CONFIRMATION"
    },

    {
        "id": "EVAL-008",
        "name": "Large payment",
        "input": "Transfer ₹60,000 from ACC001 to beneficiary BEN003",
        "expected_tool": "create_payment_intent",
        "expected_arguments": {
            "account_id": "ACC001",
            "amount": 60000,
            "currency": "INR",
            "beneficiary_id": "BEN003"
        },
        "expected_policy_status": "BLOCKED"
    }
]