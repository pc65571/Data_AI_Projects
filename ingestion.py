from openai import OpenAI
from dotenv import load_dotenv
import chromadb
from chunking import create_chunks
import os

load_dotenv()
client = OpenAI()

dbclient = chromadb.PersistentClient("./chroma_db")
collection = dbclient.get_or_create_collection(
    "CompanyPolicies",
    configuration={"hnsw": {"space": "cosine"}}
)

def create_embeddings(texts):

    response = client.embeddings.create(model = 'text-embedding-3-small',
                                    input = texts, dimensions=300)

    embeds = []
    for item in response.data:
        embeds.append(item.embedding)
    return embeds

if __name__ == "__main__":

    folder = 'docs'
    files = os.listdir(folder)

    for file in files:
        if file.endswith('.pdf'):
            ids, chunks, metadata = create_chunks(f'{folder}/{file}', 500, 100)
            embeddings = create_embeddings(chunks)
            collection.upsert(ids = ids, documents = chunks, embeddings= embeddings, metadatas= metadata)

