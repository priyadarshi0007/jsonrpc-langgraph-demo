# server_time.py
from flask import Flask, request, Response
import json, datetime
app = Flask(__name__)

@app.route("/", methods=["POST"])
def rpc():
    req = json.loads(request.data.decode())
    if req.get("method") == "now":
        iso = datetime.datetime.utcnow().isoformat()+"Z"
        resp = {"jsonrpc":"2.0","result":{"utc_iso": iso},"id":req.get("id")}
    else:
        resp = {"jsonrpc":"2.0","error":"Method not found","id":req.get("id")}
    return Response(json.dumps(resp), mimetype="application/json")

if __name__ == "__main__":
    app.run(port=5003)