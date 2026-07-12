import requests

api_key = "5HVRJGR3D1FGAG1VQXEIPN5HE7WU399CDY"
chain_id_map = {
    "ETHEREUM": 1, "BSC": 56, "POLYGON": 137, 
    "BASE": 8453, "ARBITRUM": 42161, "AVALANCHE": 43114,
    "OPTIMISM": 10, "CELO": 42220, "LINEA": 59144
}

for chain, cid in chain_id_map.items():
    url = f"https://api.etherscan.io/v2/api?chainid={cid}&module=account&action=txlist&address=0x3b5D17e2236f4D773DA87EE10B71D80C5e5b5772&startblock=0&endblock=99999999&page=1&offset=100&sort=desc&apikey={api_key}"
    r = requests.get(url).json()
    print(f"{chain}: {r.get('message')} - {r.get('result')}")
