"""9 - A2A: how one agent finds out what another agent can do.

MCP connects an agent to TOOLS. A2A connects an agent to OTHER AGENTS.
An A2A server publishes a signed "agent card" at a well-known URL; this is
what a peer reads before it delegates anything.

Run:  python 09_a2a_agent_card.py
"""

import json

# This is what a remote agent serves at /.well-known/agent-card.json
AGENT_CARD = {
    "protocolVersion": "1.0",
    "name": "Facility Documents Agent",
    "description": "Answers questions about building documentation.",
    "url": "https://agents.example.at/a2a",
    "skills": [
        {
            "id": "document_question",
            "name": "Answer a question about a building",
            "description": "Searches approved facility documents and cites sources.",
            "inputModes": ["text/plain"],
            "outputModes": ["text/plain"],
        }
    ],
    "capabilities": {"streaming": True, "pushNotifications": False},
    "securitySchemes": {"bearer": {"type": "http", "scheme": "bearer"}},
}

print(json.dumps(AGENT_CARD, indent=2))

print("\nWhat a peer agent learns from this, without any shared code:")
for skill in AGENT_CARD["skills"]:
    print(f"  - it can '{skill['name']}' (id: {skill['id']})")
print(f"  - reach it at {AGENT_CARD['url']}, authenticate with a bearer token")
print(f"  - streaming supported: {AGENT_CARD['capabilities']['streaming']}")

# Compare with MCP's tool list: the unit here is a SKILL owned by someone else's
# agent, which keeps its own model, its own data and its own permissions.
# You delegate a task. You do not call a function.
