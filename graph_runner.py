# here we need to start all three servers in 3 different terminals.
# graph_runner.py
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
    # seed inputs
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
    # just pass through; in real life you could format or validate
    return state

def build():
    g = StateGraph(GraphState)
    g.add_node("start", start)
    g.add_node("hello", call_hello)
    g.add_node("math_add", call_math_add)
    g.add_node("time_now", call_time_now)
    g.add_node("aggregate", aggregate)

    # entry
    g.set_entry_point("start")

    # sequence: start -> hello
    g.add_edge("start", "hello")

    # fan-out after hello (parallel branches)
    g.add_edge("hello", "math_add")
    g.add_edge("hello", "time_now")

    # join: when both finish, go to aggregate then END
    g.add_edge("math_add", "aggregate")
    g.add_edge("time_now", "aggregate")
    g.add_edge("aggregate", END)

    return g.compile()

if __name__ == "__main__":
    app = build()
    final = app.invoke({"name":"PSK"})
    print(final)