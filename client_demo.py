# client_demo.py
from rpc_client import rpc_call

HELLO_URL = "http://127.0.0.1:5001/"
MATH_URL  = "http://127.0.0.1:5002/"
TIME_URL  = "http://127.0.0.1:5003/"

print(rpc_call(HELLO_URL, "hello", {"name":"Pri"}))
print(rpc_call(MATH_URL, "add", {"a": 7, "b": 5}))
print(rpc_call(MATH_URL, "mul", {"a": 6, "b": 7}))
print(rpc_call(TIME_URL, "now", {}))
