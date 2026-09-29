from openai import OpenAI
from dotenv import load_dotenv
from ingestion import create_embeddings
import chromadb

load_dotenv()
client = OpenAI()

dbclient = chromadb.PersistentClient("./chroma_db")
collection = dbclient.get_or_create_collection("CompanyPolicies", configuration={ "hnsw": {"space": "cosine"}})
responseid = None

while True:

    userquery = input("Please ask your question: ")
    if userquery.lower() == "exit":
        break
    queryembedding = create_embeddings(userquery)

    relateddocs = collection.query(query_embeddings=queryembedding, n_results=3)

    context = relateddocs["documents"]

    prompt = f'''consider user query {userquery} and context {context} and respond. Give direct and natural answers. If you don't have any answer to 
            user query, pls don't hallucinate. simply say, i don't have any context regarding the query.'''

    response = client.responses.create(model = 'gpt-5.6-sol',
                                   input=prompt, previous_response_id= responseid
                                   )

    responseid = response.id
    print(response.output_text)

