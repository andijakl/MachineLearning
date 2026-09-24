#!/usr/bin/env bash
# 10 - Serving an open-weight model in production, on a GPU server.
#
# "Meltdown" is the NVIDIA H100 server these examples were written for. Nothing
# here depends on it: the script runs on any machine with an NVIDIA GPU.
#
# Ollama is built for one developer on one machine. vLLM is built for many
# concurrent users: continuous batching, paged KV cache, tensor parallelism.
# Same model, very different throughput.
#
# Run this on a machine with an NVIDIA GPU and vLLM installed (pip install vllm).
# To use it from another machine, forward the port, for example:
#     ssh -L 8000:localhost:8000 <your-gpu-server>

set -euo pipefail

MODEL="${MODEL:-google/gemma-4-E2B-it}"

# 1. What is on the GPU right now?
nvidia-smi --query-gpu=name,memory.total,memory.used --format=csv

# 2. Serve the model. --enable-auto-tool-choice is what makes agents possible;
#    without it the model can chat, but it cannot request a tool.
vllm serve "$MODEL" \
  --host 0.0.0.0 --port 8000 \
  --max-model-len 8192 \
  --gpu-memory-utilization 0.90 \
  --enable-auto-tool-choice \
  --tool-call-parser gemma4

# The parser belongs to the MODEL, not to the server:
#   Gemma 4 -> gemma4      Qwen -> hermes       Llama 3 -> llama3_json
#   Gemma 3 -> pythonic    Mistral -> mistral   Llama 4 -> pythonic
# The wrong parser looks like a model that "answers in prose instead of calling
# the tool" - a confusing failure that appears only at the first agent request.

# 3. From any machine that reaches port 8000, it is the same OpenAI client as
#    everything else:
#    curl http://localhost:8000/v1/models
#    python 11_providers.py     (the vLLM entry)
