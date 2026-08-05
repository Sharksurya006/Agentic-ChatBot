
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_tavily import TavilySearch
from langchain_core.tools import tool
from rag_tool import retrieval_rag_document

import requests
import math

import os
from dotenv import load_dotenv

load_dotenv()
# os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")

class WeatherTool:

    @staticmethod
    def get_weather(city: str):

        # Get latitude and longitude
        geo_url = (
            f"https://geocoding-api.open-meteo.com/v1/search"
            f"?name={city}&count=1"
        )

        geo = requests.get(geo_url).json()

        if "results" not in geo:
            return f"Couldn't find the city '{city}'."

        location = geo["results"][0]

        lat = location["latitude"]
        lon = location["longitude"]

        # Weather API
        weather_url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}"
            f"&longitude={lon}"
            "&current=temperature_2m,"
            "relative_humidity_2m,"
            "apparent_temperature,"
            "weather_code,"
            "wind_speed_10m"
        )

        weather = requests.get(weather_url).json()

        current = weather["current"]

        return {
            "city": city,
            "temperature": current["temperature_2m"],
            "feels_like": current["apparent_temperature"],
            "humidity": current["relative_humidity_2m"],
            "wind_speed": current["wind_speed_10m"],
            "weather_code": current["weather_code"]
        }



def calculator(expression: str)-> str:
      """
      Useful for simple math calculations.
      Input should be valid math expression.
      Example: 2 + 2, math.sqrt(16), 10 * 5
      
      """

      try:
            allowed = {
                   "math" : math,
                   "abs" : abs,
                   "round": round,
                   "min" : min,
                   "max" : max,
                   "sum" : sum
            }

            result = eval(expression, {"__builtins__":{}}, allowed)
            return str(result)
      except Exception as e:
            return f"Calculation error: {str(e)}"



def rag_tool(query: str) -> str:
    retriever =  retrieval_rag_document()
    documents = retriever.invoke(query)

    if not documents:
        return "No relevant information was found in the given PDF."

    formatted_documents = []

    for index, document in enumerate(documents, start=1):
        source = document.metadata.get("source", "Unknown source")
        page = document.metadata.get("page", "Unknown page")

        formatted_documents.append(
            f"Document {index}\n"
            f"Source: {source}\n"
            f"Page: {page}\n"
            f"Content:\n{document.page_content}\n"
        )

    return "\n\n".join(formatted_documents)



# wesearch api inbuild tool
search_tool = TavilySearch(
      max_results = 5,
      topic = "general",
      search_depth = "advanced"
)


def get_stock_price(symbol:str) -> dict:
      """
      Fetch latest stock price for a given symbol (e.g. 'APPI', 'TSLA')
      using Alpha vantage with API key in the URL

      """

      url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey=BQVREYO2VVQBPBFL"
      r = requests.get(url)
      return r.json()