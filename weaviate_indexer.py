import os
import json
from dotenv import load_dotenv
import weaviate
from weaviate.auth import AuthApiKey
import weaviate.classes.config as wc
from weaviate.classes.config import Configure

load_dotenv()

weaviate_url = os.environ["WEAVIATE_URL"]
weaviate_api_key = os.environ["WEAVIATE_API_KEY"]
openai_url = os.environ["TEXT2VEC_OPENAI_BASE_URL"]
openai_model = os.environ["OPENAI_MODEL"]
client = weaviate.connect_to_weaviate_cloud(
    cluster_url=weaviate_url,
    auth_credentials=AuthApiKey(weaviate_api_key),
    headers={"X-OpenAI-Api-Key": os.environ["OPENAI_API_KEY"]} if "OPENAI_API_KEY" in os.environ else None
)

with open("sample/datav3.json", "r") as f:
    data = json.load(f)
    docs = [
        {
            "title": garage.get("name", ""),
            "content": f"Address: {garage.get('address', '')}. "
                       f"Hourly Rate: {garage.get('hourlyRate', 'N/A')}. "
                       f"Features: {', '.join(garage.get('features', []))}.",
            "source": garage.get("website", ""),
        }
        for garage in data.get("garages", [])
        if garage.get("name")  # skip empty dicts
    ]

def create_schema():
    print(client.is_ready())
    if "Chunk" in client.collections.list_all():
        client.collections.delete("Chunk")
    collections = client.collections.list_all()
    print("Collections:", collections)
    if "Chunk" not in collections:
        client.collections.create(
            generative_config=Configure.Generative.openai(
                model=openai_model,
                base_url=openai_url
            ),
            name="Chunk",
            properties=[

                wc.Property(name="title", data_type=wc.DataType.TEXT),
                wc.Property(name="content", data_type=wc.DataType.TEXT),
                wc.Property(name="source", data_type=wc.DataType.TEXT),
            ],
            vector_config=wc.Configure.Vectors.text2vec_ollama(model="mxbai-embed-large"),
        )
    else:
        print("Collection 'Chunk' already exists. Skipping creation.")

def index_document():
    chunk = client.collections.get("Chunk")
    for doc in docs:
        chunk.data.insert(doc)

if __name__ == "__main__":
    try:
        create_schema()
        index_document()
        print("Documents indexed to Weaviate successfully.")
    finally:
        client.close()