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