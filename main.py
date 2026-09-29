from openai import OpenAI
from dotenv import load_dotenv
from sqldb import execute_query, get_table_schema

load_dotenv()

client = OpenAI()

schema = get_table_schema('Sales.SalesOrderDetail')

def is_safe_query(query):
    query = query.strip().lower()
    return query.startswith("select")

chat_history = [
    {
        "role": "developer",
        "content": f"""
You are a SQL assistant.

Generate MSSQL queries using only the schema below:

{schema}

Rules:
- Return SQL only
- Do not explain
- Use valid MSSQL syntax
- Generate SELECT queries only
"""
    }
]

while True:
    
    user_input = input("Please Ask Your Question: ")
    
    if user_input.lower() == 'exit':
        break
    
    chat_history.append({"role": "user", "content": user_input})

    response = client.responses.create(model = 'gpt-5.6-sol',
                            input = chat_history)

    chat_history.append({"role": "assistant", "content": response.output_text})                            

    print(response.output_text)

    sql_query = response.output_text

    if is_safe_query(sql_query):
        print(execute_query(sql_query))
    else:
        print("Blocked: Only SELECT queries are allowed.")