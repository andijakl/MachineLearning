"""3 - Tool calling: the model does not run anything. It asks.

Run:  python 03_tool_calling.py
"""

import json
import os

from openai import OpenAI

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
MODEL = os.environ.get("MODEL", "qwen3.5:4b")

# A tool is a normal Python function...
def get_temperature(city: str) -> str:
    fake = {"Vienna": 21, "Oslo": 8, "Cairo": 35}
    return f"{fake.get(city, 15)} degrees Celsius"


# ...plus a description the model can read. This is the whole contract.
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_temperature",
            "description": "Get the current temperature in a city.",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string"}},
                "required": ["city"],
            },
        },
    }
]

reply = client.chat.completions.create(
    model=MODEL,
    messages=[{"role": "user", "content": "How warm is it in Vienna right now?"}],
    tools=TOOLS,
)

message = reply.choices[0].message
print("=== What the model sent back ===")
print("content:   ", message.content)
print("tool_calls:", message.tool_calls)

# The model produced *text describing a function call*. Nothing has run yet.
call = message.tool_calls[0]
arguments = json.loads(call.function.arguments)

print("\n=== Our code decides to run it ===")
print(f"calling {call.function.name}({arguments})")
result = get_temperature(**arguments)
print("result:", result)

# The security boundary lives here, not in the model:
# we chose which functions exist, and we chose to run this one.
