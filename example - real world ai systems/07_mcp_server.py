"""7 - An MCP server: the same tools, but now anyone can use them.

MCP is a protocol, not a library. This server has no idea which model, which
agent framework or which company will connect to it.

Run it in its own terminal and leave it running:
    python 07_mcp_server.py
It then listens on http://127.0.0.1:8765/mcp
"""

from fastmcp import FastMCP

mcp = FastMCP("weather")

TEMPERATURES = {"Vienna": 21, "Oslo": 8, "Cairo": 35}


@mcp.tool
def get_temperature(city: str) -> str:
    """Get the current temperature in a city, in Celsius."""
    return f"{TEMPERATURES.get(city, 15)} degrees Celsius"


@mcp.tool
def to_fahrenheit(celsius: float) -> str:
    """Convert a Celsius value to Fahrenheit."""
    return f"{celsius * 9 / 5 + 32} degrees Fahrenheit"


if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=8765)

# The decorator does what we wrote by hand in 03: it reads the name, the type
# hints and the docstring, and publishes them as a machine-readable tool schema.
