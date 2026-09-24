"""5 - The same agent, with the loop written by a framework.

Compare with 04_agent_loop.py: the loop, the JSON parsing and the message
bookkeeping are gone. The tools and the question are the same.

Run:  python 05_agent_langgraph.py
"""

import os

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

MODEL = os.environ.get("MODEL", "qwen3.5:4b")

model = ChatOpenAI(
    model=MODEL,
    base_url="http://localhost:11434/v1",  # Ollama speaks the OpenAI API
    api_key="ollama",
    temperature=0,
)


# A plain function with a docstring is a tool. The docstring IS the description
# the model reads, and the type hints become the JSON schema.
TEMPERATURES = {"Vienna": 21, "Oslo": 8, "Cairo": 35}


def get_temperature(city: str) -> str:
    """Get the current temperature in a city, in Celsius."""
    return f"{TEMPERATURES.get(city, 15)} degrees Celsius"


def to_fahrenheit(celsius: float) -> str:
    """Convert a Celsius value to Fahrenheit."""
    return f"{celsius * 9 / 5 + 32} degrees Fahrenheit"


agent = create_agent(
    model,
    [get_temperature, to_fahrenheit],
    system_prompt="You are a concise weather assistant. Use the tools you have.",
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "How warm is it in Vienna, in Fahrenheit?"}]}
)

# Every message of the run, so the loop is still visible.
for message in result["messages"]:
    message.pretty_print()
