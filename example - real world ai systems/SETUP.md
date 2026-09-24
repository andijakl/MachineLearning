# Setup

Short, runnable examples of real-world AI system concepts: reasoning, RAG, tool
calling, agents and agent harnesses, MCP and A2A, serving models, provider
APIs, and speech. They are kept as small as possible on purpose: no error
handling and few best practices, so the idea stays visible in a few lines.

Almost everything runs locally on a laptop, without a GPU, through
[Ollama](https://ollama.com). Only example 10 needs a machine with an NVIDIA GPU.

## The examples

| File | What it shows |
|---|---|
| `01_reasoning.py` | Prompted reasoning vs a model's own thinking mode |
| `02_rag_minimal.py` | Retrieve, augment, generate – with a Python list as the database |
| `03_tool_calling.py` | The model asks for a function call; your code decides to run it |
| `04_agent_loop.py` | An agent written by hand: a loop around tool calling |
| `05_agent_langgraph.py` | The same agent, with the loop written by LangGraph |
| `06_agent_harness.py` | Limits and streaming around the agent – the harness |
| `07_mcp_server.py` | The same tools, published as an MCP server |
| `08_agent_with_mcp.py` | An agent that discovers its tools over MCP |
| `09_a2a_agent_card.py` | An A2A agent card: how one agent learns what another can do |
| `10_vllm_on_meltdown.sh` | Serving an open-weight model with vLLM on a GPU server |
| `11_providers.py` | One OpenAI-style client, many providers: local, own server, cloud |
| `12_tts.py` | Text to speech on a CPU |
| `13_stt.py` | Speech to text on a CPU, with timestamps |

*Meltdown*, which appears in a file name and in some example data, is the name
of the NVIDIA H100 GPU server these examples were written for. Nothing depends
on it; any NVIDIA GPU works for example 10, and everything else runs without one.

## 1. Python environment

Python 3.12 or newer.

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Ollama and the models

Install [Ollama](https://ollama.com), then:

```bash
ollama pull qwen3.5:4b             # chat, reasoning and tool calling
ollama pull nomic-embed-text       # embeddings, for the RAG example
ollama list                        # check what you have
```

To use a different model, set it once per terminal:

```bash
export MODEL=qwen3.5:4b            # Windows: set MODEL=qwen3.5:4b
```

> Part 3 of `01_reasoning.py` needs a model with a **thinking mode** (`qwen3.5`
> has one). Without it, `reasoning_effort` is ignored and part 3 prints the
> same as part 1.
>
> Examples 3 to 8 need a model that **supports tool calling**. `qwen3`,
> `granite4`, `llama3.3` and `gemma3`/`gemma4` do. Most 1B models do not.

A 4B model at 4-bit quantisation needs about 3 GB of memory and runs at a
readable speed on a laptop CPU.

## 3. Speech models

Both download on first use; fetching them up front avoids a wait later.

```bash
python -m piper.download_voices en_US-lessac-medium                        # ~60 MB voice
python -c "from faster_whisper import WhisperModel; WhisperModel('tiny')"  # ~75 MB
```

Run `12_tts.py` first: it writes the `sample.wav` that `13_stt.py` transcribes.

## 4. MCP – two processes

`07_mcp_server.py` is a server, so it needs its own terminal:

```bash
python 07_mcp_server.py        # terminal A – leave it running, listens on 127.0.0.1:8765
python 08_agent_with_mcp.py    # terminal B
```

The agent prints `Discovered over MCP: ['get_temperature', 'to_fahrenheit']`
before it answers – the tool names come from the server, not from its own code.
Stop the server with `Ctrl+C` when you are done.

## 5. Cloud providers (optional)

`11_providers.py` calls only the providers whose credentials are set, so it
runs with none, some or all of these:

```bash
export AWS_BEARER_TOKEN_BEDROCK=...   # Amazon Bedrock
export AWS_REGION=eu-central-1
export AZURE_OPENAI_ENDPOINT=https://<resource>.openai.azure.com
export AZURE_OPENAI_API_KEY=...
export OPENAI_API_KEY=...
export MISTRAL_API_KEY=...
```

Never commit these values. Model names differ per account and region – adjust
them in `11_providers.py` if a provider reports an unknown model.

## 6. Serving a model on a GPU (optional)

`10_vllm_on_meltdown.sh` runs on a machine with an NVIDIA GPU:

```bash
pip install vllm
./10_vllm_on_meltdown.sh
```

To call it from another machine, forward its port and then use the vLLM entry
in `11_providers.py`:

```bash
ssh -L 8000:localhost:8000 <your-gpu-server>
```

The first start downloads the model and loads it onto the GPU, which can take
several minutes.

## Ports

| Port | Used by |
|---|---|
| `11434` | Ollama |
| `8765` | the MCP server (examples 7 and 8) |
| `8000` | vLLM (examples 10 and 11) |

## Troubleshooting

**`cannot import name 'RequestContext' from 'mcp.shared.context'`** – the
package `langchain-mcp-adapters` is installed. Remove it with
`pip uninstall langchain-mcp-adapters`. MCP support is now part of LangChain
itself as `langchain.mcp`, and the old package pins an older MCP SDK that breaks
the examples.

**`LangChainBetaWarning` when running example 8** – expected. `langchain.mcp`
is still marked beta; the example works regardless.

**An example answers in prose instead of calling a tool** – the model does not
support tool calling. Pick one of the models listed in step 2.
