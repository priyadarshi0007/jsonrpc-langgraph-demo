# server_math.py
from flask import Flask, request, Response
import json
app = Flask(__name__)

def jsonrpc_result(result, id_):
    return Response(
        json.dumps({"jsonrpc": "2.0", "result": result, "id": id_}),
        mimetype="application/json"
    )

def jsonrpc_error(code, message, id_, data=None):
    err = {"code": code, "message": message}
    if data is not None:
        err["data"] = data
    return Response(
        json.dumps({"jsonrpc": "2.0", "error": err, "id": id_}),
        mimetype="application/json"
    )

@app.route("/", methods=["POST"])
def rpc():
    try:
        raw = request.data.decode()
        print(">> RAW:", raw)  # simple log
        req = json.loads(raw)
    except Exception as e:
        return jsonrpc_error(-32700, "Parse error", None, str(e))

    id_ = req.get("id")
    method = req.get("method")
    params = req.get("params", {}) or {}

    try:
        if method == "add":
            a = params.get("a")
            b = params.get("b")
            # Handle strings or missing numbers gracefully
            if a is None or b is None:
                return jsonrpc_error(-32602, "Invalid params: a and b required", id_)
            try:
                a = float(a)
                b = float(b)
            except Exception:
                return jsonrpc_error(-32602, "Invalid params: a and b must be numbers", id_)
            return jsonrpc_result(a + b, id_)

        if method == "mul":
            a = params.get("a")
            b = params.get("b")
            if a is None or b is None:
                return jsonrpc_error(-32602, "Invalid params: a and b required", id_)
            try:
                a = float(a)
                b = float(b)
            except Exception:
                return jsonrpc_error(-32602, "Invalid params: a and b must be numbers", id_)
            return jsonrpc_result(a * b, id_)

        # Method not found
        return jsonrpc_error(-32601, "Method not found", id_, {"method": method})

    except Exception as e:
        # Internal error
        return jsonrpc_error(-32603, "Internal error", id_, str(e))

if __name__ == "__main__":
    # Ensure you really are on 5002
    app.run(port=5002)