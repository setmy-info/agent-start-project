# agent-start-project

FastAPI playground API with MCP metadata and a CLI AI agent that uses MCP and RAG to interact with it.

## Installation

```shell
source .venv/bin/activate
```

```shell
pip install -r requirements.txt
```

## Execution REST service

```shell
uvicorn api.main:app --reload --host 127.0.0.1 --port 5000
```

## Execution CLI Agent

Illustrating multiple rag folders and multiple MCP servers endpoints

```shell
export OPENAI_API_KEY=your_api_key_here
python agent/main.py --rag ./rag ./rag --mcp http://127.0.0.1:5000/mcp http://127.0.0.1:5000/mcp -t ./tasks/example.md ./tasks/example.md
```
