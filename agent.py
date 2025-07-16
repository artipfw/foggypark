import os
import weaviate
from weaviate.classes.init import Auth
from dotenv import load_dotenv
from langchain.vectorstores import Weaviate as WeaviateStore
from langchain.chains import RetrievalQA
from langchain.embeddings import OllamaEmbeddings 
from hypermode_llm import HypermodeLLM

load_dotenv()

def build_agent():
    weaviate_url = os.environ["WEAVIATE_URL"]
    weaviate_api_key = os.environ["WEAVIATE_API_KEY"]
    client = weaviate.connect_to_weaviate_cloud(
        cluster_url=weaviate_url,
        auth_credentials=Auth.api_key(weaviate_api_key),
        headers={"X-OpenAI-Api-Key": os.environ["OPENAI_API_KEY"]} if "OPENAI_API_KEY" in os.environ else None
    )

    embeddings = OllamaEmbeddings(model="mxbai-embed-large")
    vectorstore = WeaviateStore(client=client, index_name="Chain", embedding=embeddings)
    retriever = vectorstore.as_retriever()

    llm = HypermodeLLM()

    chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
    return chain