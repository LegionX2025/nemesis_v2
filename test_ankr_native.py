import os
import requests
from dotenv import load_dotenv
load_dotenv()
key = os.environ.get('ANKR_API_KEY')
addr = '0x3b5D17e2236f4D773DA87EE10B71D80C5e5b5772'
url = f"https://rpc.ankr.com/multichain/{key}"
payload = {
    "jsonrpc": "2.0",
    "method": "ankr_getTransactionsByAddress",
    "params": {
        "address": addr,
        "blockchain": ["eth", "bsc", "polygon", "arbitrum", "optimism", "base"],
        "descOrder": True
    },
    "id": 1
}
r = requests.post(url, json=payload)
data = r.json()
if 'result' in data:
    transactions = data['result'].get('transactions', [])
    print(f"Ankr success! Found {len(transactions)} native transactions.")
    if transactions:
        print("First native tx:", transactions[0])
else:
    print("Ankr error:", data)
