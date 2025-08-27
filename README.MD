# JSON-RPC + LangGraph Demo

This repo shows how to build simple JSON-RPC microservices in Python (no extra RPC libs),
and orchestrate them with [LangGraph](https://github.com/langchain-ai/langgraph).

## Services
- `server_hello.py` → greets a user
- `server_math.py` → basic math (`add`, `mul`)
- `server_time.py` → returns UTC time
- `rpc_client.py` → helper for JSON-RPC calls

## Clients
- `client_demo.py` → sequential demo calling all services
- `graph_runner.py` → LangGraph orchestrator (manual server start)
- `graph_runner_auto_start_servers.py` → LangGraph orchestrator that auto-starts servers

## Usage

### Install
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt