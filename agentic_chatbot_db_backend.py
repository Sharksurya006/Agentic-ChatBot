from langgraph.graph import StateGraph, START, END
from typing import TypedDict,Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langgraph.graph.message import add_messages
import os
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

load_dotenv()

os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.3)


import sys
import os

print("Backend")
print(sys.executable)
print(os.getcwd())
print(os.path.abspath("chatbot.db"))

# def weather(city:str)->str:
# 	"""This tool gives the live weather update"""
# 	return f"The weather in the {city} is too sunny" 

# llm = llm.bind_tools(tools = [weather])

class ChatState(TypedDict):
	messages: Annotated[list[BaseMessage], add_messages]


def chat_node(state: ChatState):

	messages = state['messages']

	response = llm.invoke(messages)

	return {'messages' : [response]}


conn = sqlite3.connect(database="chatbot.db", check_same_thread=False)
checkpoint = SqliteSaver(conn)
# checkpoint = SqliteSaver.from_conn_string("chatbot.db")

# print(type(checkpoint))
# print(checkpoint)

graph = StateGraph(ChatState)

# adding the node to the graph
graph.add_node("chat_node", chat_node)

#adding the edges to the graph
graph.add_edge(START, 'chat_node')
graph.add_edge('chat_node', END)

chatbot = graph.compile(checkpointer=checkpoint)


def get_all_threads():
    all_threads = set()

    for ckpt in checkpoint.list(None):
        all_threads.add(
            ckpt.config["configurable"]["thread_id"]
        )

    return list(all_threads)



# thread_id = 'surya'

# config = {'configurable' : {'thread_id' : thread_id}}

# initial_state = {
# 	'messages' : [HumanMessage(content = 'my name is Surya?')]
# }

# response = chatbot.invoke(initial_state, config= config)

# print(response['messages'][-1].content)



# get_all_threads()