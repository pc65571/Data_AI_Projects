from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Literal, List, Optional

load_dotenv()

client = OpenAI()

class sqlrequest(BaseModel):
      query: str = Field(description = "SQL query to be executed")
      explanation: str = Field(description = "This should be a brief explanation of the query")
      filters: List[str] = Field(description = "This should be a list of the filters used in the query")
      operations: Literal['select', 'insert', 'update', 'delete'] = Field(description = "This should be the type of operation being performed in the query")
      tables_used: List[str] = Field(description = "This should be a list of tables used in the query")

response = client.responses.parse(model = 'gpt-5.6-sol', 
                                   input='gibe me a sql query for top 5 products in USA based on sales amount',
                                      text_format=sqlrequest)

print(response.output_parsed)
print(response.output_parsed.query)
print(response.output_parsed.explanation)
print(response.output_parsed.filters)
print(response.output_parsed.operations)
print(response.output_parsed.tables_used)






