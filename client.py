# client.py
import requests, json

url = "http://127.0.0.1:5000/"
payload = {"jsonrpc":"2.0","method":"hello","params":{"name":"World"},"id":1}
headers = {"Content-Type":"application/json"}

print("Sending request...")
try:
    r = requests.post(url, data=json.dumps(payload), headers=headers, timeout=5)
    print("Status:", r.status_code)
    print("Body:", r.text)
except Exception as e:
    print("Error:", repr(e))