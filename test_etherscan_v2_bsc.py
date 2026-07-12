import os
import requests
from dotenv import load_dotenv
load_dotenv()
key = os.environ.get('VITE_ETHERSCAN_API_KEY')
addr = '0x3b5D17e2236f4D773DA87EE10B71D80C5e5b5772'
url = f'https://api.etherscan.io/v2/api?chainid=56&module=account&action=txlist&address={addr}&startblock=0&endblock=99999999&page=1&offset=5&sort=desc&apikey={key}'
r = requests.get(url)
data = r.json()
print("Etherscan V2 (Chain 56) status:", data.get('status'), "msg:", data.get('message'), "result:", data.get('result'))
