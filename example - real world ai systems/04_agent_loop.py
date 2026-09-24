"""4 - An agent is a while loop around tool calling.

This is the entire idea of agentic AI. Everything else is safety and comfort.

Run:  python 04_agent_loop.py
"""

import json
import os

from openai import OpenAI

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
MODEL = os.environ.get("MODEL", "qwen3.5:4b")


TEMPERATURES = {"Vienna": 21, "Oslo": 8, "Cairo": 35}


def get_temperature(city: str) -> str:
    return f"{TEMPERATURES.get(city, 15)} degrees Celsius"


def to_fahrenheit(celsius: float) -> str:
    return f"{float(celsius) * 9 / 5 + 32} degrees Fahrenheit"


AVAILABLE = {"get_temperature": get_temperature, "to_fahrenheit": to_fahrenheit}

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_temperature",
            "description": "Get the current temperature in a city, in Celsius.",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string"}},
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "to_fahrenheit",
            "description": "Convert a Celsius value to Fahrenheit.",
            "parameters": {
                "type": "object",
                "properties": {"celsius": {"type": "number"}},
                "required": ["celsius"],
            },
        },
    },
]

messages = [{"role": "user", "content": "How warm is it in Vienna, in Fahrenheit?"}]

# THE AGENT LOOP
for step in range(1, 6):  # the limit is what makes it terminate
    reply = client.chat.completions.create(model=MODEL, messages=messages, tools=TOOLS)
    message = reply.choices[0].message
    messages.append(message)

    if not message.tool_calls:
        print(f"\n=== Final answer (after {step} model calls) ===")
        print(message.content)
        break

    for call in message.tool_calls:
        arguments = json.loads(call.function.arguments)
        result = AVAILABLE[call.function.name](**arguments)
        print(f"step {step}: {call.function.name}({arguments}) -> {result}")

        # The result goes back into the conversation. That is the feedback.
        messages.append(
            {"role": "tool", "tool_call_id": call.id, "content": result}
        )

# Reason -> act -> observe -> reason again, until the model stops asking for tools.
