import json
import urllib.request

req = urllib.request.Request("https://rpc.ankr.com/eth", data=json.dumps({"jsonrpc":"2.0","method":"eth_getBalance","params":["0x3b5D17e2236f4D773DA87EE10B71D80C5e5b5772", "latest"],"id":1}).encode('utf-8'), headers={'Content-Type': 'application/json'})
response = urllib.request.urlopen(req)
print("0x3b5D ETH Balance:", json.loads(response.read().decode('utf-8')))

req = urllib.request.Request("https://rpc.ankr.com/polygon", data=json.dumps({"jsonrpc":"2.0","method":"eth_getBalance","params":["0x030c0c65DBb914e423992F35b4Fe956F5E90b045", "latest"],"id":1}).encode('utf-8'), headers={'Content-Type': 'application/json'})
response = urllib.request.urlopen(req)
print("0x030c POLYGON Balance:", json.loads(response.read().decode('utf-8')))
