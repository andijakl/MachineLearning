"""6 - The harness: the same agent, made safe to put in front of users.

The agent from 05 works. It is also unbounded: a confused model can loop for
ever, and nobody watching sees what it did. A harness fixes both.

Run:  python 06_agent_harness.py
"""

import os

from langchain.agents import create_agent
from langchain.agents.middleware import ModelCallLimitMiddleware, ToolCallLimitMiddleware
from langchain_openai import ChatOpenAI

MODEL = os.environ.get("MODEL", "qwen3.5:4b")

model = ChatOpenAI(
    model=MODEL, base_url="http://localhost:11434/v1", api_key="ollama", temperature=0
)

TEMPERATURES = {"Vienna": 21, "Oslo": 8, "Cairo": 35, "Berlin": 18, "Rome": 25, "Lisbon": 22}


def get_temperature(city: str) -> str:
    """Get the current temperature in a city, in Celsius."""
    return f"{TEMPERATURES.get(city, 15)} degrees Celsius"


agent = create_agent(
    model,
    [get_temperature],
    system_prompt="You are a weather assistant.",
    middleware=[
        # A run that reaches a limit ENDS with what it has. It does not crash,
        # and it does not run for ever on someone else's budget.
        ModelCallLimitMiddleware(run_limit=4, exit_behavior="end"),
        ToolCallLimitMiddleware(run_limit=5, exit_behavior="end"),
    ],
)

# Deliberately more work than the limits allow, to show the bound taking effect.
question = (
    "Compare the temperature in Vienna, Oslo, Cairo, Berlin, Rome and Lisbon, "
    "then rank them."
)

print("=== Watching the agent work, step by step ===")
for chunk in agent.stream(
    {"messages": [{"role": "user", "content": question}]}, stream_mode="values"
):
    chunk["messages"][-1].pretty_print()

# Streaming the steps is not a nicety. It is how an operator sees which tool
# produced an answer - and how a user sees that something is happening at all.
