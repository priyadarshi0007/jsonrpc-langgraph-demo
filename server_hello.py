# server_hello.py
from flask import Flask, request, Response
import json
app = Flask(__name__)

@app.route("/", methods=["POST"])
def rpc():
    req = json.loads(request.data.decode())
    if req.get("method") == "hello":
        name = req.get("params", {}).get("name", "World")
        resp = {"jsonrpc":"2.0","result":f"Hello, {name}!","id":req.get("id")}
    else:
        resp = {"jsonrpc":"2.0","error":"Method not found","id":req.get("id")}
    return Response(json.dumps(resp), mimetype="application/json")

if __name__ == "__main__":
    app.run(port=5001)