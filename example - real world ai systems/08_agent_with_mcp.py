"""8 - An agent that discovers its tools over MCP instead of importing them.

Start 07_mcp_server.py in another terminal first, then run:
    python 08_agent_with_mcp.py

Expect a LangChainBetaWarning: `langchain.mcp` is still marked beta. MCP support
moved into LangChain itself in 2026, replacing the separate adapter package. The
protocol is settled; the libraries around it are still moving.
"""

import asyncio
import os

from langchain.agents import create_agent
from langchain.mcp import MCPAdapter
from langchain_openai import ChatOpenAI

MODEL = os.environ.get("MODEL", "qwen3.5:4b")

model = ChatOpenAI(
    model=MODEL, base_url="http://localhost:11434/v1", api_key="ollama", temperature=0
)

adapter = MCPAdapter("http://127.0.0.1:8765/mcp")


async def main() -> None:
    # The tools are not in this file. They are fetched from the server at runtime.
    tools = await adapter.list_tools()
    print("Discovered over MCP:", [tool.name for tool in tools])

    agent = create_agent(model, tools, system_prompt="You are a weather assistant.")
    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "How warm is it in Vienna, in Fahrenheit?"}]}
    )
    print("\n" + result["messages"][-1].content)


asyncio.run(main())

# Swap the URL for someone else's MCP server and this agent gains their tools
# without a single line changing here. That is the entire point of the protocol.
