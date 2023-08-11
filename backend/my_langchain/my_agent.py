from langchain.chat_models import AzureChatOpenAI
from langchain.agents import load_tools, initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from typing import List
from models import Query
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
    def __init__(self, chat_history: List[Query], verbose=False) -> None:
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        for query in chat_history:
            if query.role == "assistant":
                self.memory.chat_memory.add_ai_message(query.content)
            else:
                self.memory.chat_memory.add_user_message(query.content)
        self.agent_chain = initialize_agent(tools, llm, agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION, verbose=verbose, memory=self.memory)
    
    def run(self, input: str) -> str:
        return self.agent_chain.run(input=input)