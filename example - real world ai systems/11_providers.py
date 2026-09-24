"""11 - One code shape, many providers.

The OpenAI chat-completions format became the de facto standard. Local runtimes
and cloud vendors all speak it, so switching provider is a base_url and a key.

Run:  python 11_providers.py
Only the providers whose environment variable is set will be called.
"""

import os

from openai import OpenAI

QUESTION = "In one sentence: why do companies run language models on their own hardware?"

PROVIDERS = {
    # name:            (base_url,                                   api key,                     model)
    "Ollama (laptop)": ("http://localhost:11434/v1", "ollama", os.environ.get("MODEL", "qwen3.5:4b")),
    # The server started by 10_vllm_on_meltdown.sh, on this machine or forwarded to it.
    "vLLM (own GPU server)": ("http://localhost:8000/v1", "not-needed", "google/gemma-4-E2B-it"),
    "Amazon Bedrock": (
        f"https://bedrock-runtime.{os.environ.get('AWS_REGION', 'eu-central-1')}.amazonaws.com/openai/v1",
        os.environ.get("AWS_BEARER_TOKEN_BEDROCK"),
        "mistral.mistral-large-3",
    ),
    "Azure OpenAI": (
        f"{os.environ.get('AZURE_OPENAI_ENDPOINT', '')}/openai/v1",
        os.environ.get("AZURE_OPENAI_API_KEY"),
        "gpt-5-mini",
    ),
    "OpenAI": ("https://api.openai.com/v1", os.environ.get("OPENAI_API_KEY"), "gpt-5-mini"),
    "Mistral (EU)": (
        "https://api.mistral.ai/v1",
        os.environ.get("MISTRAL_API_KEY"),
        "mistral-small-latest",
    ),
}

for name, (base_url, api_key, model) in PROVIDERS.items():
    if not api_key:
        print(f"-- {name}: no credentials set, skipping")
        continue

    client = OpenAI(base_url=base_url, api_key=api_key)
    # The only error handling in these demos: one provider being unreachable
    # should not stop the comparison with the others.
    try:
        reply = client.chat.completions.create(
            model=model, messages=[{"role": "user", "content": QUESTION}]
        )
    except Exception as error:
        print(f"-- {name}: not reachable ({type(error).__name__})")
        continue

    print(f"\n=== {name} ({model}) ===")
    print(reply.choices[0].message.content)

# The code below the client is identical for a 4B model on a laptop and a
# frontier model in a hyperscaler. That is what makes a provider swappable -
# and what makes vendor lock-in a deployment decision rather than a code rewrite.
