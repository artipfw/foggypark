import os
import weaviate
from dotenv import load_dotenv
from langchain.vectorstores import Weaviate as WeaviateStore
from langchain.chains import RetrievalQA
from langchain.embeddings import OpenAIEmbeddings 
from hypermode_llm import HypermodeLLM

load_dotenv()

def build_agent():
    client = weaviate.WeaviateClient(os.getenv("WEAVIATE_URL"))

    embeddings = OpenAIEmbeddings()
    vectorstore = WeaviateStore(client=client, index_name="Chain", embedding=embeddings)
    retriever = vectorstore.as_retriever()

    llm = HypermodeLLM()

    chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
    return chain