from flask import Flask, request, Response
import json

app = Flask(__name__)

@app.route("/", methods=["POST"])
def rpc():
    # Parse raw JSON
    req = json.loads(request.data.decode())

    # Minimal "hello" implementation
    if req.get("method") == "hello":
        name = req.get("params", {}).get("name", "World")
        result = f"Hello, {name}!"
        resp = {"jsonrpc": "2.0", "result": result, "id": req.get("id")}
    else:
        resp = {"jsonrpc": "2.0", "error": "Method not found", "id": req.get("id")}

    # Return raw JSON response
    return Response(json.dumps(resp), mimetype="application/json")

if __name__ == "__main__":
    app.run(port=5000)