from langgraph.graph import StateGraph, START, END
from typing import TypedDict,Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langgraph.graph.message import add_messages
import os
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.3)

class ChatState(TypedDict):
	messages: Annotated[list[BaseMessage], add_messages]


def chat_node(state: ChatState):

	messages = state['messages']

	response = llm.invoke(messages)

	return {'messages' : [response]}


checkpoint = MemorySaver()

graph = StateGraph(ChatState)

# adding the node to the graph
graph.add_node("chat_node", chat_node)

#adding the edges to the graph
graph.add_edge(START, 'chat_node')
graph.add_edge('chat_node', END)

chatbot = graph.compile(checkpointer=checkpoint)

thread_id = '1'

config = {'configurable' : {'thread_id' : thread_id}}

initial_state = {
	'messages' : [HumanMessage(content = 'my name is Surya?')]
}

response = chatbot.invoke(initial_state, config= config)

print(response['messages'][-1].content)