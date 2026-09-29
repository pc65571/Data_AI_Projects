from openai import OpenAI
from dotenv import load_dotenv
from tools import get_expenses, add_expense, update_expense, delete_expense
import json

load_dotenv()
client = OpenAI()

mytools = [
    {
        "type": "function",
        "name": "get_expenses",
        "description": "Get all expenses.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "type": "function",
        "name": "add_expense",
        "description": "Add a new expense.",
        "parameters": {
            "type": "object",
            "properties": {
                "expense_date": {
                    "type": "string",
                    "description": "Expense date in YYYY-MM-DD format."
                },
                "category": {
                    "type": "string",
                    "description": "Expense category."
                },
                "description": {
                    "type": "string",
                    "description": "Expense description."
                },
                "amount": {
                    "type": "number",
                    "description": "Expense amount."
                },
                "payment_method": {
                    "type": "string",
                    "description": "Payment method."
                }
            },
            "required": [
                "expense_date",
                "category",
                "description",
                "amount",
                "payment_method"
            ]
        }
    },
    {
        "type": "function",
        "name": "update_expense",
        "description": "Update an existing expense.",
        "parameters": {
            "type": "object",
            "properties": {
                "expense_id": {
                    "type": "integer",
                    "description": "Expense ID to update."
                },
                "expense_date": {
                    "type": "string",
                    "description": "Expense date in YYYY-MM-DD format."
                },
                "category": {
                    "type": "string",
                    "description": "Expense category."
                },
                "description": {
                    "type": "string",
                    "description": "Expense description."
                },
                "amount": {
                    "type": "number",
                    "description": "Expense amount."
                },
                "payment_method": {
                    "type": "string",
                    "description": "Payment method."
                }
            },
            "required": [
                "expense_id",
                "expense_date",
                "category",
                "description",
                "amount",
                "payment_method"
            ]
        }
    },
    {
        "type": "function",
        "name": "delete_expense",
        "description": "Delete an expense.",
        "parameters": {
            "type": "object",
            "properties": {
                "expense_id": {
                    "type": "integer",
                    "description": "Expense ID to delete."
                }
            },
            "required": [
                "expense_id"
            ]
        }
    }
]

tool_mapping = {'get_expenses': get_expenses, 'add_expense': add_expense, 'update_expense': update_expense, 'delete_expense': delete_expense}

response_id = None

while True:
    user_input = input("Please Ask Your Question: ")
    if user_input.lower() == 'exit':
        break
    response = client.responses.create(model='gpt-5.6-sol', input=user_input,
                                        previous_response_id=response_id, tools=mytools)
    response_id = response.id
    
    while True:
        tool_outputs = []
        for item in response.output:
            if item.type == 'function_call':
                tool_name = item.name
                tool_args = json.loads(item.arguments)
                callingfunction = tool_mapping.get(tool_name)
                tool_result = callingfunction(**tool_args)
                callid = item.call_id
                tool_outputs.append({'type': 'function_call_output', 'call_id': callid, 'output': str(tool_result)})
        if not tool_outputs:
            break
        response = client.responses.create(model='gpt-5.6-sol', input=tool_outputs,
                                            previous_response_id=response_id, tools=mytools)
        response_id = response.id
    print(response.output_text)

