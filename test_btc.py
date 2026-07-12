import requests
r = requests.get("https://blockchain.info/rawaddr/1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa")
data = r.json()
print("Total txs:", len(data.get("txs")))
for tx in data.get("txs", [])[:1]:
    print(tx)
