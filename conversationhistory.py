from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

conversation_history = []
while True:
    user_input = input("Enter your prompt: ")
    if user_input.lower() == "exit":
        break
    conversation_history.append({"role":"user","content":user_input})
    result = client.responses.create(model="gpt-5.6-sol", 
                                     input=conversation_history, 
                                     tools=[{"type":"web_search"}])
    conversation_history.append({"role":"assistant","content":result.output_text})
    print(result.output_text)                                     