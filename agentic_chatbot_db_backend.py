from langgraph.graph import StateGraph, START, END
from typing import TypedDict,Annotated,List,Optional
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langgraph.graph.message import add_messages

from langgraph.prebuilt import ToolNode, tools_condition
from langchain_tavily import TavilySearch
from langchain_core.tools import tool

from email_tool import Send_email

import requests
from urllib.parse import quote
import uuid
from prompt import system_prompt

import os
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain.chat_models import init_chat_model
import sqlite3

from tools import WeatherTool,calculator,get_stock_price,search_tool, rag_tool

load_dotenv()

os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")
os.environ["DEEPSEEK_API_KEY"] = os.getenv("DEEPSEEK_API_KEY")

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.3)

llm_google = init_chat_model("google_genai:gemini-3.5-flash")

# llm_deepseek = init_chat_model(
#     "openrouter:deepseek/deepseek-r1"
# )

@tool
def get_weather_update(city:str):
      """This method returns the live weather update in a specific city"""
      weather = WeatherTool()
      return weather.get_weather(city)


@tool
def generate_image(prompt: str) -> str:
    """
    Generates an image from the given prompt using Pollinations AI.
    Returns the path to the generated image.
    """

    filename = f"generated_{uuid.uuid4().hex[:8]}.png"
    url = f"https://image.pollinations.ai/prompt/{quote(prompt)}"

    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()

        with open(filename, "wb") as f:
            f.write(response.content)

        return {
          "type": "image",
          "path": os.path.abspath(filename)
        }

    except requests.RequestException as e:
        return f"Image generation failed: {e}"



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


@tool
def RAG_tool(query:str) -> str:
       """
    Search the uploaded PDF knowledge base.

    ALWAYS use this tool whenever the user asks about:

    - uploaded PDFs
    - resumes
    - CVs
    - documents
    - research papers
    - contracts
    - reports
    - "this file"
    - "the uploaded document"

    Never answer from your own knowledge if the answer may exist in the uploaded document.

    Args:
        query: User question.

    Returns:
        Relevant extracted text from the uploaded PDF.
    """
       return rag_tool(query)


@tool
def send_email(
    recipients: List[str],
    subject: str,
    body: str,
    cc: Optional[List[str]] = None,
    bcc: Optional[List[str]] = None,
    attachments: Optional[List[str]] = None,
    html: bool = False,
    reply_to: Optional[str] = None,
    priority: str = "normal"
) -> str:
    """
    Sends an email using Gmail.

    Parameters
    ----------
    recipients : List[str]
        Recipient email addresses.

    subject : str
        Email subject.

    body : str
        Email content.

    cc : List[str], optional
        CC recipients.

    bcc : List[str], optional
        BCC recipients.

    attachments : List[str], optional
        List of file paths.

    html : bool
        Whether body contains HTML.

    reply_to : str
        Reply-To address.

    priority : str
        low, normal, high
    """

    return Send_email(
    recipients,
    subject,
    body,
    cc,
    bcc,
    attachments,
    html,
    reply_to,
    priority
    ) 

class ChatState(TypedDict):
	messages: Annotated[list[BaseMessage], add_messages]



tools = [get_weather_update,calculator_tool,stock_update,web_search_tool,RAG_tool,send_email,generate_image]

llm_with_tools = llm_google.bind_tools(tools)

def chat_node(state: ChatState):

    system_message = SystemMessage(content = system_prompt)

    messages = [system_message,*state["messages"]]

    try:
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    except Exception as e:
        print(f"LLM Error: {e}")

        return {
            "messages": [
                AIMessage(
                    content="Sorry can't resolve the Query, LLM model is experiencing issues as of now. Please try again later."
                )
            ]
        }


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