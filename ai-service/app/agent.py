import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from app.tools.financial_tools import (
    get_balance,
    get_transactions
)

from app.tools.payment_tools import create_payment_intent

from app.guardrails.evidence_guard import (
    check_comparison_evidence,
    requires_comparison
)

from app.guardrails.spending_comparator import (
    compare_latest_periods
)

from app.guardrails.spending_analyzer import (
    analyze_spending
)


# ---------------------------------------------------------
# Environment / OpenAI client
# ---------------------------------------------------------

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


# ---------------------------------------------------------
# Agent grounding instructions
# ---------------------------------------------------------

AGENT_INSTRUCTIONS = """
You are a financial assistant for FinAgent Lab.

Follow these rules carefully:

1. Use financial tools whenever account data is required.
2. Never invent financial information.
3. Only make conclusions supported by the data returned by financial tools.
4. Distinguish CREDIT transactions from DEBIT transactions.
5. Do not treat CREDIT transactions as spending.
6. If the available data does not support a conclusion, explicitly state that the conclusion cannot be determined.
7. Never claim that spending increased or decreased unless transactions from at least two comparable periods are available.
8. Never invent historical transaction data or previous-period values.
9. When analyzing transactions, base your answer only on the transactions returned by the tools.
10. For exact financial calculations or financial policy decisions, rely on deterministic application logic rather than assumptions.
11. If a user asks why spending increased or decreased and no comparison period exists, explicitly say that the change cannot be determined.
12. Do not use phrases such as "the increase", "the decrease", "increased because", "decreased because", "driven by the increase", or similar causal language when comparison data is unavailable.
13. When comparison data is unavailable, describe only the spending observed in the available transactions and clearly state that a trend cannot be established.
14. create_payment_intent only creates and validates a payment intent. It does not execute or transfer money.
15. Never claim that a payment has been executed or submitted unless a dedicated payment execution tool actually performs that action.
16. Financial policy decisions must be determined by the deterministic policy engine, not by the LLM.
"""


# ---------------------------------------------------------
# Financial tools available to the agent
# ---------------------------------------------------------

tools = [
    {
        "type": "function",
        "name": "get_balance",
        "description": "Get the current balance of a financial account.",
        "parameters": {
            "type": "object",
            "properties": {
                "account_id": {
                    "type": "string",
                    "description": "The financial account ID, for example ACC001."
                }
            },
            "required": ["account_id"],
            "additionalProperties": False
        },
        "strict": True
    },

    {
        "type": "function",
        "name": "get_transactions",
        "description": "Get recent transactions for a financial account.",
        "parameters": {
            "type": "object",
            "properties": {
                "account_id": {
                    "type": "string",
                    "description": "The financial account ID, for example ACC001."
                }
            },
            "required": ["account_id"],
            "additionalProperties": False
        },
        "strict": True
    },

    {
        "type": "function",
        "name": "create_payment_intent",
        "description": (
            "Create a financial payment intent after deterministic policy validation. "
            "This does not execute or transfer money."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "account_id": {
                    "type": "string",
                    "description": "Source account ID"
                },
                "amount": {
                    "type": "number",
                    "description": "Payment amount"
                },
                "currency": {
                    "type": "string",
                    "description": "Payment currency such as INR, USD or SGD"
                },
                "beneficiary_id": {
                    "type": "string",
                    "description": "Beneficiary ID"
                }
            },
            "required": [
                "account_id",
                "amount",
                "currency",
                "beneficiary_id"
            ],
            "additionalProperties": False
        },
        "strict": True
    }
]


# ---------------------------------------------------------
# Tool executor
# ---------------------------------------------------------

def execute_tool(tool_name, arguments):

    if tool_name == "get_balance":

        return get_balance(
            arguments["account_id"]
        )

    elif tool_name == "get_transactions":

        return get_transactions(
            arguments["account_id"]
        )

    elif tool_name == "create_payment_intent":

        return create_payment_intent(
            account_id=arguments["account_id"],
            amount=arguments["amount"],
            currency=arguments["currency"],
            beneficiary_id=arguments["beneficiary_id"]
        )

    return {
        "success": False,
        "message": f"Unknown tool: {tool_name}"
    }


# ---------------------------------------------------------
# Main reusable agent function
# ---------------------------------------------------------

def run_agent(user_input):

    # -----------------------------------------------------
    # Track agent execution for evaluation
    # -----------------------------------------------------

    tool_calls = []
    tool_results = []

    retrieved_transactions = []

    # -----------------------------------------------------
    # Step 1 — Initial LLM request
    # -----------------------------------------------------

    response = client.responses.create(
        model="gpt-5.6-luna",
        instructions=AGENT_INSTRUCTIONS,
        tools=tools,
        input=user_input
    )

    # -----------------------------------------------------
    # Step 2 — Process requested tools
    #
    # We intentionally handle the current agent as a single
    # tool-resolution cycle.
    #
    # This prevents accidental infinite tool loops while
    # building the core FinAgent Lab architecture.
    # -----------------------------------------------------

    tool_outputs = []

    for item in response.output:

        if item.type != "function_call":
            continue

        print("LLM requested tool:", item.name)
        print("Arguments:", item.arguments)

        arguments = json.loads(item.arguments)

        # ---------------------------------------------
        # Track tool call for evaluation
        # ---------------------------------------------

        tool_calls.append(
            {
                "name": item.name,
                "arguments": arguments
            }
        )

        # ---------------------------------------------
        # Execute tool
        # ---------------------------------------------

        result = execute_tool(
            item.name,
            arguments
        )

        print("Tool result:", result)

        # ---------------------------------------------
        # Track tool result for evaluation
        # ---------------------------------------------

        tool_results.append(
            {
                "name": item.name,
                "result": result
            }
        )

        # ---------------------------------------------
        # Capture transactions for deterministic analysis
        # ---------------------------------------------

        if (
                item.name == "get_transactions"
                and result.get("success") is True
        ):
            retrieved_transactions = result.get(
                "transactions",
                []
            )

        # ---------------------------------------------
        # Prepare function output for the LLM
        # ---------------------------------------------

        tool_outputs.append(
            {
                "type": "function_call_output",
                "call_id": item.call_id,
                "output": json.dumps(result)
            }
        )

    # -----------------------------------------------------
    # Step 3 — No tool call
    # -----------------------------------------------------

    if not tool_outputs:

        final_answer = response.output_text

        print("\nFinal answer:")
        print(final_answer)

        return {
            "user_input": user_input,
            "final_answer": final_answer,
            "tool_calls": tool_calls,
            "tool_results": tool_results
        }

    # -----------------------------------------------------
    # Step 4 — Evidence Guard
    # -----------------------------------------------------

    evidence_check = check_comparison_evidence(
        user_input,
        retrieved_transactions
    )

    if not evidence_check["allowed"]:

        print("\nEvidence Guard:")
        print("BLOCKED:", evidence_check["reason"])

        final_answer = (
            "I cannot determine whether spending increased or "
            "decreased because no historical comparison period "
            "is available."
        )

        print("\nFinal answer:")
        print(final_answer)

        return {
            "user_input": user_input,
            "final_answer": final_answer,
            "tool_calls": tool_calls,
            "tool_results": tool_results,
            "guardrail": {
                "status": "BLOCKED",
                "reason": evidence_check["reason"]
            }
        }

    # -----------------------------------------------------
    # Step 5 — Deterministic Spending Analysis
    # -----------------------------------------------------

    spending_analysis = None

    if retrieved_transactions:

        spending_analysis = analyze_spending(
            retrieved_transactions
        )

        print("\nDeterministic Spending Analysis:")
        print(spending_analysis)

    # -----------------------------------------------------
    # Step 6 — Deterministic Spending Comparison
    # -----------------------------------------------------

    comparison_result = None

    if (
            retrieved_transactions
            and requires_comparison(user_input)
    ):

        comparison_result = compare_latest_periods(
            retrieved_transactions
        )

        print("\nDeterministic Spending Comparison:")
        print(comparison_result)

    # -----------------------------------------------------
    # Step 7 — Prepare trusted information for final LLM
    # -----------------------------------------------------

    next_input = list(tool_outputs)

    # -----------------------------------------------------
    # Add trusted spending analysis
    # -----------------------------------------------------

    if (
            spending_analysis
            and spending_analysis.get("success") is True
            and spending_analysis.get("analysis")
    ):

        trusted_analysis = spending_analysis["analysis"]

        next_input.append(
            {
                "role": "developer",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "Trusted deterministic spending analysis:\n"
                            f"{json.dumps(trusted_analysis)}\n\n"
                            "Use this analysis as the authoritative "
                            "source for spending totals, category totals, "
                            "largest expense, and transaction count. "
                            "Do not recalculate or alter these financial "
                            "values."
                        )
                    }
                ]
            }
        )

    # -----------------------------------------------------
    # Add trusted spending comparison
    # -----------------------------------------------------

    if (
            comparison_result
            and comparison_result.get("success") is True
    ):

        trusted_comparison = comparison_result["comparison"]

        next_input.append(
            {
                "role": "developer",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "Trusted deterministic financial "
                            "comparison result:\n"
                            f"{json.dumps(trusted_comparison)}\n\n"
                            "Use this deterministic result when "
                            "answering the user's comparison "
                            "question. Do not recalculate, "
                            "modify, or contradict the financial "
                            "values."
                        )
                    }
                ]
            }
        )

    # -----------------------------------------------------
    # Add trusted payment-policy result
    # -----------------------------------------------------

    for tool_result in tool_results:

        if tool_result["name"] == "create_payment_intent":

            payment_result = tool_result["result"]

            next_input.append(
                {
                    "role": "developer",
                    "content": [
                        {
                            "type": "input_text",
                            "text": (
                                "Trusted deterministic payment "
                                "policy result:\n"
                                f"{json.dumps(payment_result)}\n\n"
                                "Use this policy result as the "
                                "authoritative source for the "
                                "payment status and reason. "
                                "Do not change, override, or "
                                "contradict the policy decision. "
                                "Remember that create_payment_intent "
                                "does not execute or transfer money."
                            )
                        }
                    ]
                }
            )

    # -----------------------------------------------------
    # Step 8 — Final LLM pass
    #
    # IMPORTANT:
    # tools=[] prevents the LLM from calling financial
    # tools again.
    #
    # LLM → understands the question
    # Tool → retrieves raw financial data
    # Python → performs deterministic analysis
    # Guardrail → validates evidence
    # LLM → explains trusted result
    # -----------------------------------------------------

    final_response = client.responses.create(
        model="gpt-5.6-luna",
        previous_response_id=response.id,
        tools=[],
        input=next_input
    )

    final_answer = final_response.output_text

    # -----------------------------------------------------
    # Step 9 — Final answer
    # -----------------------------------------------------

    print("\nFinal answer:")
    print(final_answer)

    # -----------------------------------------------------
    # Return structured result for evaluation
    # -----------------------------------------------------

    return {
        "user_input": user_input,
        "final_answer": final_answer,
        "tool_calls": tool_calls,
        "tool_results": tool_results
    }


# ---------------------------------------------------------
# Direct execution
# ---------------------------------------------------------

if __name__ == "__main__":

    user_input = (
        "Transfer ₹20,000 from ACC001 to beneficiary BEN001"
    )

    result = run_agent(user_input)