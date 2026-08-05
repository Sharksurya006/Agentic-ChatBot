from langgraph.graph import StateGraph, START, END
from typing import TypedDict,Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langgraph.graph.message import add_messages

from langgraph.prebuilt import ToolNode, tools_condition
from langchain_tavily import TavilySearch
from langchain_core.tools import tool

import requests
import math

import os
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain.chat_models import init_chat_model
import sqlite3


from tools import WeatherTool,calculator,get_stock_price,search_tool

load_dotenv()

os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")

llm = ChatGroq(model="qwen/qwen3-32b", temperature=0.3)

llm_google = init_chat_model("google_genai:gemini-2.0-flash")

@tool
def get_weather_update(city:str):
      """This method returns the live weather update in a specific city"""
      weather = WeatherTool()
      return weather.get_weather(city)


@tool
def calculator_tool(expression:str) -> str:
      """This method calculates the simple mathematical expressions"""

      return calculator(expression)


@tool
def stock_update(symbol:str) -> dict:
      """This method gives the live update of a specific company stock"""
      return get_stock_price(symbol)


@tool
def web_search_tool(query:str) -> str:
      """This method gives the live update of a specific company stock"""
      return search_tool.invoke(query)


class ChatState(TypedDict):
	messages: Annotated[list[BaseMessage], add_messages]



tools = [get_weather_update,calculator_tool,stock_update,web_search_tool]

llm_with_tools = llm.bind_tools(tools)

def chat_node(state: ChatState):

	messages = state['messages']

	response = llm_with_tools.invoke(messages)

	return {'messages' : [response]}



tool_node = ToolNode(tools)

conn = sqlite3.connect(database="chatbot.db", check_same_thread=False)
checkpoint = SqliteSaver(conn)
# checkpoint = SqliteSaver.from_conn_string("chatbot.db")

# print(type(checkpoint))
# print(checkpoint)

graph = StateGraph(ChatState)

# adding the node to the graph
graph.add_node("chat_node", chat_node)
graph.add_node("tools",tool_node)

#adding the edges to the graph
graph.add_edge(START, 'chat_node')

# if the llm asked for a tool, go to ToolNode; else finish

graph.add_conditional_edges("chat_node",tools_condition)

graph.add_edge("tools","chat_node")

# graph.add_edge('chat_node', END)

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