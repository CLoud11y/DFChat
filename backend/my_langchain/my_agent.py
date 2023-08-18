from langchain.chat_models import AzureChatOpenAI
from langchain.agents import load_tools, initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import PyPDFDirectoryLoader
from langchain.chains import ConversationalRetrievalChain
from langchain.vectorstores.base import VectorStoreRetriever
from typing import List
from models import Query
from database import DialogRecord
from config import (
    api_key,
    api_url,
    api_version,
    openweathermap_api_key,
    completion_engine_gpt35,
)
import os

os.environ["OPENAI_API_KEY"] = api_key
os.environ["OPENAI_API_BASE"] = api_url
os.environ["OPENAI_API_VERSION"] = api_version
os.environ["OPENWEATHERMAP_API_KEY"] = openweathermap_api_key

llm = AzureChatOpenAI(temperature=0, deployment_name=completion_engine_gpt35)
tools = load_tools(["llm-math","openweathermap-api"], llm=llm)


class MyAgent():
    def __init__(self, chat_history: List[Query], verbose=False, handle_parsing_errors=False) -> None:
        '''
        handle_parsing_errors:
        Defaults to False, which raises the error.
        If true, the error will be sent back to the LLM as an observation. 
        If a string, the string itself will be sent to the LLM as an observation. 
        If a callable function, the function will be called with the exception
        '''
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        for query in chat_history:
            if query.role == "assistant":
                self.memory.chat_memory.add_ai_message(query.content)
            else:
                self.memory.chat_memory.add_user_message(query.content)
        
        self.agent_chain = initialize_agent(
            tools, 
            llm, 
            agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION, 
            verbose=verbose, 
            memory=self.memory, 
            handle_parsing_errors=handle_parsing_errors
        )
    
    
    def run(self, input: str) -> str:
        return self.agent_chain.run(input=input)
    

class QAChain():
    def __init__(self, chat_history: List[Query], dialog_id : str) -> None:
        dialog = DialogRecord.get_record_by_id(int(dialog_id))
        path = dialog.file_path
        loader = PyPDFDirectoryLoader(path=path)
        texts = loader.load_and_split(text_splitter=CharacterTextSplitter(chunk_size=1000, chunk_overlap=0))
        embeddings = OpenAIEmbeddings(deployment="textembeddingada002")
        docsearch = Chroma.from_documents(texts, embeddings)
        retriever = VectorStoreRetriever(vectorstore=docsearch)

        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        for query in chat_history:
            if query.role == "assistant":
                self.memory.chat_memory.add_ai_message(query.content)
            else:
                self.memory.chat_memory.add_user_message(query.content)
        self.qa = ConversationalRetrievalChain.from_llm(llm=llm, retriever=retriever, chain_type="stuff", memory=self.memory)

    def run(self, input: str) -> str:
        return self.qa.run(input)