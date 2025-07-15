import os
from dotenv import load_dotenv
import weaviate
from weaviate.classes.init import Auth


load_dotenv()

weaviate_url = os.environ["WEAVIATE_URL"]
weaviate_api_key = os.environ["WEAVIATE_API_KEY"]
client = weaviate.connect_to_weaviate_cloud(
    cluster_url=weaviate_url,
    auth_credentials=Auth.api_key(weaviate_api_key),
)

docs = [
    {
        "title": "Parking Spot 1",
        "content": "safe place to park your car between 8 AM and 6 PM",
        "source": "sf bay area parking guide",
    }
]

def create_schema():
    if client.schema.contains("Chunk"):
        client.schema.delete_class("Chunk")
    schema = {
        "classes": [{
            "class": "Chank",
            "description": "Documents parking spot",
            "properties": [
                {
                    "name": "title",
                    "dataType": ["text"],
                },
                {
                    "name": "content",
                    "dataType": ["text"],
                },
                {
                    "name": "source",
                    "dataType": ["text"],
                }
            ]
        }]
    }
    client.schema.create(schema)

def index_document():
    for doc in docs:
        client.data_object.create(
            data_object=doc,
            class_name="Chunk"
        )

if __name__ == "__main__":
    create_schema()
    index_document()
    print("Documents indexed to Weaviate successfully.")    