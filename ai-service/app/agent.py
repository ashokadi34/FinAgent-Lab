import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from app.tools.financial_tools import get_balance

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
    }
]


user_input = "What is the current balance of account ACC001?"

response = client.responses.create(
    model="gpt-5.6-luna",
    tools=tools,
    input=user_input
)


for item in response.output:

    if item.type == "function_call":

        print("LLM requested tool:", item.name)
        print("Arguments:", item.arguments)

        arguments = json.loads(item.arguments)

        if item.name == "get_balance":

            result = get_balance(
                arguments["account_id"]
            )

            print("Tool result:", result)

            # Continue the conversation from the previous response
            response = client.responses.create(
                model="gpt-5.6-luna",
                previous_response_id=response.id,
                tools=tools,
                input=[
                    {
                        "type": "function_call_output",
                        "call_id": item.call_id,
                        "output": json.dumps(result)
                    }
                ]
            )

            print("\nFinal answer:")
            print(response.output_text)