import json, requests

def rpc_call(url: str, method: str, params: dict, id_: int = 1, timeout=5):
    payload = {"jsonrpc":"2.0","method":method,"params":params,"id":id_}
    r = requests.post(url, data=json.dumps(payload),
                      headers={"Content-Type":"application/json"}, timeout=timeout)
    r.raise_for_status()
    return r.json()