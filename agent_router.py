# agent_router.py
import os
import json
from typing import TypedDict, Any, Dict

from langgraph.graph import StateGraph, END
from rpc_client import rpc_call

# --- Load .env if present (pip install python-dotenv) ---
try:
    from dotenv import load_dotenv
    load_dotenv(override=True) 
except Exception:
    pass

# --- JSON-RPC service endpoints ---
HELLO_URL = "http://127.0.0.1:5001/"
MATH_URL  = "http://127.0.0.1:5002/"
TIME_URL  = "http://127.0.0.1:5003/"

# --- OpenAI (optional). If not set, we use a tiny rule-based fallback. ---
OPENAI_API_KEY = (os.getenv("OPENAI_API_KEY") or "").strip()
use_llm = bool(OPENAI_API_KEY)

if use_llm:
    # pip install openai
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)
    # Uncomment for a one-time sanity print:
    # print("OpenAI key detected (len):", len(OPENAI_API_KEY))


# ---------------- Graph State ----------------
class S(TypedDict, total=False):
    user_input: str
    plan: Dict[str, Any]   # {"tool": "hello"|"add"|"now", "params": {...}}
    result: Any


# ---------------- LLM Router Prompt ----------------
SYSTEM = """You are a strict router. Map the user's request to exactly one tool:
- hello: requires {"name": <string>}
- add:   requires {"a": <number>, "b": <number>}
- now:   requires {}

Return STRICT JSON ONLY with keys: tool, params.
Examples:
User: "Say hello to Pri"        -> {"tool":"hello","params":{"name":"Pri"}}
User: "Add 21 and 21"           -> {"tool":"add","params":{"a":21,"b":21}}
User: "What time is it now?"    -> {"tool":"now","params":{}}
No extra text.
"""


# ---------------- Nodes ----------------
def route_with_llm(state: S) -> S:
    """
    If OPENAI_API_KEY is present, ask the LLM to produce a JSON plan.
    Otherwise, fall back to a simple rule-based router so demos still run.
    """
    text = state["user_input"]

    if not use_llm:
        lower = text.lower()
        if "hello" in lower or "greet" in lower or "hi" in lower:
            plan = {"tool": "hello", "params": {"name": "Pri"}}
        elif "add" in lower:
            # naive parse: find first two integers
            import re
            nums = [int(n) for n in re.findall(r"-?\d+", lower)]
            a, b = (nums + [21, 21])[:2]   # default 21+21 if none
            plan = {"tool": "add", "params": {"a": a, "b": b}}
        else:
            plan = {"tool": "now", "params": {}}
        return {"plan": plan}

    # LLM path
    prompt = f'User request: {text}\nReturn only JSON.'
    resp = client.responses.create(
        model="gpt-4o-mini",
        input=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": prompt},
        ],
    )
    raw = resp.output_text.strip()

    # Try to parse; if it fails, retry once with a harder constraint.
    try:
        plan = json.loads(raw)
    except json.JSONDecodeError:
        resp2 = client.responses.create(
            model="gpt-4o-mini",
            input=[
                {"role": "system", "content": SYSTEM},
                {
                    "role": "user",
                    "content": prompt + "\nReturn strict JSON only. No prose."
                },
            ],
        )
        plan = json.loads(resp2.output_text.strip())

    # Basic normalization
    if not isinstance(plan, dict):
        plan = {"tool": "now", "params": {}}
    plan.setdefault("tool", "now")
    plan.setdefault("params", {})

    return {"plan": plan}


def act(state: S) -> S:
    plan = state["plan"]
    tool = plan.get("tool")
    params = plan.get("params", {})

    try:
        if tool == "hello":
            out = rpc_call(HELLO_URL, "hello", params)
        elif tool == "add":
            out = rpc_call(MATH_URL, "add", params)
        elif tool == "now":
            out = rpc_call(TIME_URL, "now", params)
        else:
            out = {"error": f"Unknown tool: {tool}", "plan": plan}
    except Exception as e:
        out = {"error": f"Execution failed: {e}", "plan": plan}

    return {"result": out}


# ---------------- Build Graph ----------------
def build():
    g = StateGraph(S)
    g.add_node("route_with_llm", route_with_llm)
    g.add_node("act", act)
    g.set_entry_point("route_with_llm")
    g.add_edge("route_with_llm", "act")
    g.add_edge("act", END)
    return g.compile()


# ---------------- CLI Demo ----------------
if __name__ == "__main__":
    # Ensure your Flask services are running on :5001, :5002, :5003
    app = build()

    # print("Demo 1:", app.invoke({"user_input": "Say hello to PSK"}))
    print("Demo 2:", app.invoke({"user_input": "do a summation of 11 and one"}))
    # print("Demo 3:", app.invoke({"user_input": "What time is it now?"}))