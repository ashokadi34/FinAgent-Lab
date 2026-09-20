import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from app.tools.financial_tools import (
    get_balance,
    get_transactions
)

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# Grounding instructions improve model behavior but are not
# a deterministic enforcement mechanism.
# Deterministic evidence and policy validation will be added
# in a later stage of FinAgent Lab.

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
""" 

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
    }
]


def execute_tool(name, arguments):

    if name == "get_balance":
        return get_balance(
            arguments["account_id"]
        )

    if name == "get_transactions":
        return get_transactions(
            arguments["account_id"]
        )

    return {
        "success": False,
        "message": f"Unknown tool: {name}"
    }


user_input = (
    "Why did my spending increase for account ACC001?"
)


response = client.responses.create(
    model="gpt-5.6-luna",
    instructions=AGENT_INSTRUCTIONS,
    tools=tools,
    input=user_input
)


while True:

    tool_outputs = []

    for item in response.output:

        if item.type != "function_call":
            continue

        print("LLM requested tool:", item.name)
        print("Arguments:", item.arguments)

        arguments = json.loads(item.arguments)

        result = execute_tool(
            item.name,
            arguments
        )

        print("Tool result:", result)

        tool_outputs.append(
            {
                "type": "function_call_output",
                "call_id": item.call_id,
                "output": json.dumps(result)
            }
        )

    if not tool_outputs:
        break

    response = client.responses.create(
        model="gpt-5.6-luna",
        previous_response_id=response.id,
        tools=tools,
        input=tool_outputs
    )


print("\nFinal answer:")
print(response.output_text)