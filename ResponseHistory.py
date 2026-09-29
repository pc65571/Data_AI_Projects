from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
client = OpenAI()

response_id = None
while True:
    user_input = input("Enter your prompt: ")
    if user_input.lower() == "exit":
        break
    result = client.responses.create(model="gpt-5.6-sol", 
                                     input=user_input, previous_response_id=response_id,
                                     tools=[{"type":"web_search"}])
    response_id = result.id    
    print(result.output_text)                                     