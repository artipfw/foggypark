import os
import weaviate
from dotenv import load_dotenv
from langchain.chains import RetrievalQA
from langchain_weaviate import WeaviateVectorStore
from langchain_ollama import OllamaEmbeddings
from hypermode_llm import HypermodeLLM

load_dotenv()

def build_agent():
    ollama_base_url = os.environ.get("OLLAMA_BASE_URL")
    ollama_model = os.environ.get("OLLAMA_MODEL")

    client = weaviate.connect_to_local(
        headers={"X-OpenAI-Api-Key": os.environ["HYPERMODE_API_KEY"]} if "HYPERMODE_API_KEY" in os.environ else None, 
    )

    embeddings = OllamaEmbeddings(base_url=ollama_base_url, model=ollama_model)
    vectorstore = WeaviateVectorStore(client=client, index_name="Chunk", embedding=embeddings, text_key="content")
    retriever = vectorstore.as_retriever()

    llm = HypermodeLLM()

    chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
    return chain