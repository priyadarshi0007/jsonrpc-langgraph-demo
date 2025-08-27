# graph_runner.py
import subprocess, sys, time, atexit
from rpc_client import rpc_call
from langgraph.graph import StateGraph, END
from typing import TypedDict, Dict, Any

HELLO_URL = "http://127.0.0.1:5001/"
MATH_URL  = "http://127.0.0.1:5002/"
TIME_URL  = "http://127.0.0.1:5003/"

# --- Step 1: start servers ---
processes = []

def start_server(script, port):
    p = subprocess.Popen([sys.executable, script], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    processes.append(p)
    print(f"Started {script} on port {port} (pid {p.pid})")

# cleanup on exit
def cleanup():
    for p in processes:
        p.terminate()
        try:
            p.wait(timeout=3)
        except subprocess.TimeoutExpired:
            p.kill()
    print("Cleaned up servers")

atexit.register(cleanup)

# Start all 3 servers
start_server("server_hello.py", 5001)
start_server("server_math.py", 5002)
start_server("server_time.py", 5003)

# Give them time to boot
time.sleep(2)

# --- Step 2: define graph state ---
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
    result = app.invoke({"name": "PSK"})
    print("FINAL RESULT:", result)