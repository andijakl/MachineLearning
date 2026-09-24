"""2 - RAG in 30 lines, with no vector database at all.

Retrieve -> Augment -> Generate. The database is a Python list.

Run:  python 02_rag_minimal.py
"""

import os

import numpy as np
from openai import OpenAI

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
MODEL = os.environ.get("MODEL", "qwen3.5:4b")
EMBED_MODEL = "nomic-embed-text"

# A tiny knowledge base. "Meltdown" is the name of a GPU server (an NVIDIA H100)
# that serves as the running example in these demos; the rest is unrelated noise.
DOCS = [
    "The Meltdown server is an NVIDIA H100 with 80 GB of VRAM.",
    "Meltdown is shared between projects, so a job must release the GPU when idle.",
    "The campus cafeteria serves warm food until 14:00 on weekdays.",
    "Student projects must be submitted through the university Git server.",
    "An H100 can be split into MIG slices, for example four slices of 20 GB.",
]

QUESTION = "How much memory does Meltdown have, and can it be shared?"


def embed(texts: list[str]) -> np.ndarray:
    reply = client.embeddings.create(model=EMBED_MODEL, input=texts)
    return np.array([item.embedding for item in reply.data])


# 1. RETRIEVE - turn text into vectors and find the closest ones.
doc_vectors = embed(DOCS)
question_vector = embed([QUESTION])[0]

similarity = doc_vectors @ question_vector / (
    np.linalg.norm(doc_vectors, axis=1) * np.linalg.norm(question_vector)
)
best = np.argsort(similarity)[::-1][:2]
context = "\n".join(DOCS[i] for i in best)

print("=== Retrieved context ===")
for i in best:
    print(f"  [{similarity[i]:.2f}] {DOCS[i]}")

# 2. AUGMENT - paste the found text into the prompt.
prompt = f"Answer using only the context.\n\nContext:\n{context}\n\nQuestion: {QUESTION}"

# 3. GENERATE
answer = client.chat.completions.create(
    model=MODEL, messages=[{"role": "user", "content": prompt}]
)
print("\n=== Answer ===")
print(answer.choices[0].message.content)

# Note what the model never saw: the cafeteria and the Git server.
# Retrieval decided that, not the model.
