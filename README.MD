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

Here’s the same blog, rewritten cleanly in GitHub-flavored Markdown (GFM) so you can drop it straight into a README.md or publish it as a post in your repo.

⸻

Building JSON-RPC Microservices and Orchestrating Them with LangGraph

Introduction

When designing microservices for data engineering or agentic AI systems, communication between components often becomes a bottleneck. REST is widely adopted, but sometimes a simpler, more lightweight protocol is useful. JSON-RPC is one such option. It is a stateless, lightweight remote procedure call (RPC) protocol encoded in JSON. Unlike REST, it does not impose resource semantics but instead focuses on invoking methods on a server with parameters and receiving structured responses.

In this post, we will build three JSON-RPC microservices in Python without any external JSON-RPC libraries. Then we will write a simple client to interact with them, and finally orchestrate them using LangGraph to demonstrate fan-out, parallel execution, and aggregation of results.

⸻

Why JSON-RPC?

JSON-RPC has a few clear benefits:
	•	Minimal overhead compared to REST.
	•	Standardized request and response formats.
	•	Easy to implement manually with just Flask and json.
	•	Native support for batch calls.

Typical JSON-RPC request:

{
  "jsonrpc": "2.0",
  "method": "hello",
  "params": {"name": "World"},
  "id": 1
}

Typical response:

{
  "jsonrpc": "2.0",
  "result": "Hello, World!",
  "id": 1
}


⸻

Designing the Microservices

We will implement three independent services:
	1.	Hello Service – greets the user.
	2.	Math Service – provides basic arithmetic (add and mul).
	3.	Time Service – returns the current UTC timestamp.

All services are Flask applications that parse JSON requests and return JSON-RPC compliant responses.

Hello Service (server_hello.py)

from flask import Flask, request, Response
import json

app = Flask(__name__)

@app.route("/", methods=["POST"])
def rpc():
    req = json.loads(request.data.decode())
    if req.get("method") == "hello":
        name = req.get("params", {}).get("name", "World")
        result = f"Hello, {name}!"
        resp = {"jsonrpc": "2.0", "result": result, "id": req.get("id")}
    else:
        resp = {"jsonrpc": "2.0", "error": "Method not found", "id": req.get("id")}
    return Response(json.dumps(resp), mimetype="application/json")

if __name__ == "__main__":
    app.run(port=5001)

Math Service (server_math.py)

from flask import Flask, request, Response
import json

app = Flask(__name__)

@app.route("/", methods=["POST"])
def rpc():
    req = json.loads(request.data.decode())
    method = req.get("method")
    params = req.get("params", {})

    if method == "add":
        result = params.get("a", 0) + params.get("b", 0)
    elif method == "mul":
        result = params.get("a", 1) * params.get("b", 1)
    else:
        return Response(json.dumps({"jsonrpc": "2.0", "error": "Method not found", "id": req.get("id")}), mimetype="application/json")

    return Response(json.dumps({"jsonrpc": "2.0", "result": result, "id": req.get("id")}), mimetype="application/json")

if __name__ == "__main__":
    app.run(port=5002)

Time Service (server_time.py)

from flask import Flask, request, Response
import json, datetime

app = Flask(__name__)

@app.route("/", methods=["POST"])
def rpc():
    req = json.loads(request.data.decode())
    if req.get("method") == "now":
        iso = datetime.datetime.utcnow().isoformat() + "Z"
        resp = {"jsonrpc": "2.0", "result": {"utc_iso": iso}, "id": req.get("id")}
    else:
        resp = {"jsonrpc": "2.0", "error": "Method not found", "id": req.get("id")}
    return Response(json.dumps(resp), mimetype="application/json")

if __name__ == "__main__":
    app.run(port=5003)


⸻

Writing a Simple Client

The client just sends JSON payloads to each service and prints responses.

# rpc_client.py
import requests, json

def rpc_call(url, method, params, id_=1):
    payload = {"jsonrpc": "2.0", "method": method, "params": params, "id": id_}
    r = requests.post(url, data=json.dumps(payload), headers={"Content-Type": "application/json"})
    return r.json()

# client_demo.py
from rpc_client import rpc_call

HELLO_URL = "http://127.0.0.1:5001/"
MATH_URL  = "http://127.0.0.1:5002/"
TIME_URL  = "http://127.0.0.1:5003/"

print(rpc_call(HELLO_URL, "hello", {"name": "Pri"}))
print(rpc_call(MATH_URL, "add", {"a": 7, "b": 5}))
print(rpc_call(MATH_URL, "mul", {"a": 6, "b": 7}))
print(rpc_call(TIME_URL, "now", {}))

Running this produces:

{"jsonrpc":"2.0","result":"Hello, Pri!","id":1}
{"jsonrpc":"2.0","result":12,"id":1}
{"jsonrpc":"2.0","result":42,"id":1}
{"jsonrpc":"2.0","result":{"utc_iso":"2025-08-26T05:10:12Z"},"id":1}


⸻

Orchestrating with LangGraph

LangGraph provides a stateful DAG execution engine for AI agents and workflows. We can map our JSON-RPC services as nodes in a graph:
	•	start → hello
	•	hello → math_add
	•	hello → time_now
	•	math_add, time_now → aggregate → END

This demonstrates fan-out parallelism and aggregation of results.

Graph Runner (graph_runner.py)

from typing import TypedDict, Any, Dict
from langgraph.graph import StateGraph, END
from rpc_client import rpc_call

HELLO_URL = "http://127.0.0.1:5001/"
MATH_URL  = "http://127.0.0.1:5002/"
TIME_URL  = "http://127.0.0.1:5003/"

class GraphState(TypedDict, total=False):
    name: str
    hello: str
    add_result: int
    now: Dict[str, Any]

def start(state: GraphState) -> GraphState:
    return {"name": state.get("name", "World")}

def call_hello(state: GraphState) -> GraphState:
    res = rpc_call(HELLO_URL, "hello", {"name": state["name"]})
    return {"hello": res["result"]}

def call_math_add(state: GraphState) -> GraphState:
    res = rpc_call(MATH_URL, "add", {"a": 21, "b": 21})
    return {"add_result": res["result"]}

def call_time_now(state: GraphState) -> GraphState:
    res = rpc_call(TIME_URL, "now", {})
    return {"now": res["result"]}

def aggregate(state: GraphState) -> GraphState:
    return state

def build():
    g = StateGraph(GraphState)
    g.add_node("start", start)
    g.add_node("hello", call_hello)
    g.add_node("math_add", call_math_add)
    g.add_node("time_now", call_time_now)
    g.add_node("aggregate", aggregate)

    g.set_entry_point("start")
    g.add_edge("start", "hello")
    g.add_edge("hello", "math_add")
    g.add_edge("hello", "time_now")
    g.add_edge("math_add", "aggregate")
    g.add_edge("time_now", "aggregate")
    g.add_edge("aggregate", END)

    return g.compile()

if __name__ == "__main__":
    app = build()
    result = app.invoke({"name": "Pri"})
    print(result)

Expected output:

{
  'name': 'Pri',
  'hello': 'Hello, Pri!',
  'add_result': 42,
  'now': {'utc_iso': '2025-08-26T05:10:12Z'}
}


⸻

Lessons Learned
	1.	JSON-RPC is lightweight and easy to implement manually, making it suitable for fast prototyping.
	2.	Error handling is essential. JSON-RPC defines standard error codes for parse errors, invalid parameters, and method not found.
	3.	LangGraph enables orchestration of independent services, allowing parallel execution and aggregation in a clean DAG representation.
	4.	This approach can scale into larger agentic AI or data engineering workflows where services are small and composable.

⸻

Next Steps
	•	Extend the Math service to include subtraction, division, and batch processing.
	•	Add error handling with JSON-RPC error objects (codes -32600 to -32603).
	•	Replace Flask with FastAPI for async support and better performance.
	•	Use LangGraph conditions and routers to dynamically select which service to call.

⸻

Conclusion

This project demonstrates how to combine the simplicity of JSON-RPC with the orchestration capabilities of LangGraph. By building independent microservices and wiring them into a graph-based execution model, we get a flexible, testable, and composable system that is directly applicable to real-world data engineering and AI workflows.

⸻

