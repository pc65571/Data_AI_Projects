from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

result = client.responses.create(
    model = 'gpt-5.6-sol',input='''what's the weather in bellevue, wa tomorrow?''',
    tools=[{'type': 'web_search'}])

print(result.output_text)